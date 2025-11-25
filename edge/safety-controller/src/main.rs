fn main() {
    let mut limits = gateway_safety_controller::DosingLimits {
        current_rate_mcg_per_kg_min: 0.05,
        min_rate_mcg_per_kg_min: 0.02,
        max_rate_mcg_per_kg_min: 0.9,
        max_delta_mcg_per_kg_min: 0.1,
        fallback_rate_mcg_per_kg_min: 0.05,
    };

    let inputs = gateway_safety_controller::ControlInputs {
        predicted_map_mmhg: 60.0,
        hypotension_risk: 0.8,
        confidence: 0.9,
        clinician_target_map_mmhg: 65.0,
    };

    let output = gateway_safety_controller::safety_step(&mut limits, Some(&inputs));
    println!("Commanded rate: {:.3}", output.commanded_rate_mcg_per_kg_min);
}
