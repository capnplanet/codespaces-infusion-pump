#include "safety_controller.h"
#include "pump_hal.h"

#include <math.h>
#include <stddef.h>

#define MIN_CONFIDENCE_THRESHOLD 0.5f

static dosing_limits_t active_limits;

void safety_controller_init(const dosing_limits_t *limits) {
    if (limits == NULL) {
        return;
    }
    safety_controller_set_limits(limits);
}

void safety_controller_set_limits(const dosing_limits_t *limits) {
    if (limits == NULL) {
        return;
    }
    active_limits = *limits;
}

static float clamp_rate(float rate) {
    if (rate < active_limits.min_rate_mcg_per_kg_min) {
        return active_limits.min_rate_mcg_per_kg_min;
    }
    if (rate > active_limits.max_rate_mcg_per_kg_min) {
        return active_limits.max_rate_mcg_per_kg_min;
    }
    return rate;
}

control_output_t safety_controller_step(const control_inputs_t *inputs) {
    control_output_t output = {
        .commanded_rate_mcg_per_kg_min = active_limits.current_rate_mcg_per_kg_min,
        .use_fallback_profile = false,
        .trigger_alarm = false
    };

    if (inputs == NULL) {
        output.use_fallback_profile = true;
        output.commanded_rate_mcg_per_kg_min = active_limits.fallback_rate_mcg_per_kg_min;
        output.trigger_alarm = true;
        return output;
    }

    if (!isfinite(inputs->confidence) ||
        inputs->confidence < MIN_CONFIDENCE_THRESHOLD ||
        inputs->confidence > 1.0f ||
        !isfinite(inputs->predicted_map_mmHg) ||
        !isfinite(inputs->clinician_target_map_mmHg)) {
        output.use_fallback_profile = true;
        output.commanded_rate_mcg_per_kg_min = active_limits.fallback_rate_mcg_per_kg_min;
        output.trigger_alarm = true;
        return output;
    }

    float target_rate = active_limits.current_rate_mcg_per_kg_min;

    if (inputs->predicted_map_mmHg < inputs->clinician_target_map_mmHg) {
        target_rate += active_limits.max_delta_mcg_per_kg_min;
    } else {
        target_rate -= active_limits.max_delta_mcg_per_kg_min;
    }

    target_rate = clamp_rate(target_rate);
    active_limits.current_rate_mcg_per_kg_min = target_rate;
    output.commanded_rate_mcg_per_kg_min = target_rate;

    if (output.use_fallback_profile) {
        pump_hal_trigger_alarm();
    }

    pump_hal_set_infusion_rate(output.commanded_rate_mcg_per_kg_min);
    return output;
}
