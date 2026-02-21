use gateway_safety_controller::{safety_step, ControlInputs, DosingLimits};

#[test]
fn fallback_when_low_confidence() {
    let mut limits = DosingLimits {
        current_rate_mcg_per_kg_min: 0.05,
        min_rate_mcg_per_kg_min: 0.02,
        max_rate_mcg_per_kg_min: 0.8,
        max_delta_mcg_per_kg_min: 0.1,
        fallback_rate_mcg_per_kg_min: 0.05,
    };

    let inputs = ControlInputs {
        predicted_map_mmhg: 55.0,
        hypotension_risk: 0.8,
        confidence: 0.1,
        clinician_target_map_mmhg: 65.0,
    };

    let output = safety_step(&mut limits, Some(&inputs));
    assert!(output.use_fallback_profile);
}

#[test]
fn fallback_when_confidence_out_of_range() {
    let mut limits = DosingLimits {
        current_rate_mcg_per_kg_min: 0.05,
        min_rate_mcg_per_kg_min: 0.02,
        max_rate_mcg_per_kg_min: 0.8,
        max_delta_mcg_per_kg_min: 0.1,
        fallback_rate_mcg_per_kg_min: 0.05,
    };

    let inputs = ControlInputs {
        predicted_map_mmhg: 55.0,
        hypotension_risk: 0.8,
        confidence: 1.2,
        clinician_target_map_mmhg: 65.0,
    };

    let output = safety_step(&mut limits, Some(&inputs));
    assert!(output.use_fallback_profile);
    assert!(output.trigger_alarm);
}

#[test]
fn fallback_when_map_not_finite() {
    let mut limits = DosingLimits {
        current_rate_mcg_per_kg_min: 0.05,
        min_rate_mcg_per_kg_min: 0.02,
        max_rate_mcg_per_kg_min: 0.8,
        max_delta_mcg_per_kg_min: 0.1,
        fallback_rate_mcg_per_kg_min: 0.05,
    };

    let inputs = ControlInputs {
        predicted_map_mmhg: f32::INFINITY,
        hypotension_risk: 0.8,
        confidence: 0.9,
        clinician_target_map_mmhg: 65.0,
    };

    let output = safety_step(&mut limits, Some(&inputs));
    assert!(output.use_fallback_profile);
    assert!(output.trigger_alarm);
}
