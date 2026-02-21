use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DosingLimits {
    pub current_rate_mcg_per_kg_min: f32,
    pub min_rate_mcg_per_kg_min: f32,
    pub max_rate_mcg_per_kg_min: f32,
    pub max_delta_mcg_per_kg_min: f32,
    pub fallback_rate_mcg_per_kg_min: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlInputs {
    pub predicted_map_mmhg: f32,
    pub hypotension_risk: f32,
    pub confidence: f32,
    pub clinician_target_map_mmhg: f32,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct ControlOutput {
    pub commanded_rate_mcg_per_kg_min: f32,
    pub use_fallback_profile: bool,
    pub trigger_alarm: bool,
}

const MIN_CONFIDENCE: f32 = 0.5;

fn clamp(value: f32, min: f32, max: f32) -> f32 {
    value.min(max).max(min)
}

pub fn safety_step(limits: &mut DosingLimits, inputs: Option<&ControlInputs>) -> ControlOutput {
    let mut output = ControlOutput {
        commanded_rate_mcg_per_kg_min: limits.current_rate_mcg_per_kg_min,
        use_fallback_profile: false,
        trigger_alarm: false,
    };

    let inputs = match inputs {
        Some(data) => data,
        None => {
            output.use_fallback_profile = true;
            output.commanded_rate_mcg_per_kg_min = limits.fallback_rate_mcg_per_kg_min;
            output.trigger_alarm = true;
            return output;
        }
    };

    if !inputs.confidence.is_finite()
        || inputs.confidence < MIN_CONFIDENCE
        || inputs.confidence > 1.0
        || !inputs.predicted_map_mmhg.is_finite()
        || !inputs.clinician_target_map_mmhg.is_finite()
    {
        output.use_fallback_profile = true;
        output.commanded_rate_mcg_per_kg_min = limits.fallback_rate_mcg_per_kg_min;
        output.trigger_alarm = true;
        return output;
    }

    let mut target = limits.current_rate_mcg_per_kg_min;

    if inputs.predicted_map_mmhg < inputs.clinician_target_map_mmhg {
        target += limits.max_delta_mcg_per_kg_min;
    } else {
        target -= limits.max_delta_mcg_per_kg_min;
    }

    target = clamp(target, limits.min_rate_mcg_per_kg_min, limits.max_rate_mcg_per_kg_min);
    limits.current_rate_mcg_per_kg_min = target;
    output.commanded_rate_mcg_per_kg_min = target;

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn step_increases_rate_when_below_target() {
        let mut limits = DosingLimits {
            current_rate_mcg_per_kg_min: 0.05,
            min_rate_mcg_per_kg_min: 0.02,
            max_rate_mcg_per_kg_min: 0.8,
            max_delta_mcg_per_kg_min: 0.1,
            fallback_rate_mcg_per_kg_min: 0.05,
        };

        let inputs = ControlInputs {
            predicted_map_mmhg: 55.0,
            hypotension_risk: 0.7,
            confidence: 0.8,
            clinician_target_map_mmhg: 65.0,
        };

        let output = safety_step(&mut limits, Some(&inputs));
        assert!(output.commanded_rate_mcg_per_kg_min > 0.05);
    }
}
