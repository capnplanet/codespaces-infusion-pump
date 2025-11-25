#include "safety_controller.h"
#include "communication.h"
#include "pump_hal.h"

#include <stdio.h>

static dosing_limits_t g_limits = {
    .current_rate_mcg_per_kg_min = 0.0f,
    .min_rate_mcg_per_kg_min = 0.02f,
    .max_rate_mcg_per_kg_min = 1.00f,
    .max_delta_mcg_per_kg_min = 0.10f,
    .fallback_rate_mcg_per_kg_min = 0.05f
};

int main(void) {
    pump_hal_init();
    comms_init();
    safety_controller_init(&g_limits);

    // Integration loops implemented in platform-specific scheduler.
    printf("Pump firmware bootstrap complete.\n");
    return 0;
}
