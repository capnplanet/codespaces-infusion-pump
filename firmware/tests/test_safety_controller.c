#include "safety_controller.h"

#include <assert.h>
#include <stdio.h>

int main(void) {
    dosing_limits_t limits = {
        .current_rate_mcg_per_kg_min = 0.05f,
        .min_rate_mcg_per_kg_min = 0.02f,
        .max_rate_mcg_per_kg_min = 0.90f,
        .max_delta_mcg_per_kg_min = 0.10f,
        .fallback_rate_mcg_per_kg_min = 0.05f
    };

    safety_controller_init(&limits);

    control_inputs_t inputs = {
        .predicted_map_mmHg = 60.0f,
        .hypotension_risk = 0.8f,
        .confidence = 0.9f,
        .clinician_target_map_mmHg = 65.0f
    };

    control_output_t output = safety_controller_step(&inputs);
    assert(output.commanded_rate_mcg_per_kg_min >= limits.min_rate_mcg_per_kg_min);
    assert(output.commanded_rate_mcg_per_kg_min <= limits.max_rate_mcg_per_kg_min);
    assert(!output.use_fallback_profile);

    inputs.confidence = 0.2f;
    output = safety_controller_step(&inputs);
    assert(output.use_fallback_profile);

    printf("safety_controller tests passed.\n");
    return 0;
}
