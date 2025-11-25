#ifndef SAFETY_CONTROLLER_H
#define SAFETY_CONTROLLER_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float current_rate_mcg_per_kg_min;
    float min_rate_mcg_per_kg_min;
    float max_rate_mcg_per_kg_min;
    float max_delta_mcg_per_kg_min;
    float fallback_rate_mcg_per_kg_min;
} dosing_limits_t;

typedef struct {
    float predicted_map_mmHg;
    float hypotension_risk;
    float confidence;
    float clinician_target_map_mmHg;
} control_inputs_t;

typedef struct {
    float commanded_rate_mcg_per_kg_min;
    bool use_fallback_profile;
    bool trigger_alarm;
} control_output_t;

void safety_controller_init(const dosing_limits_t *limits);
control_output_t safety_controller_step(const control_inputs_t *inputs);
void safety_controller_set_limits(const dosing_limits_t *limits);

#endif
