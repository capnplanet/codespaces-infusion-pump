#include "pump_hal.h"

#include <stdio.h>

static float g_rate = 0.0f;

void pump_hal_init(void) {
    // Placeholder: configure motor drivers and sensors.
    g_rate = 0.0f;
}

bool pump_hal_set_infusion_rate(float rate_mcg_per_kg_min) {
    g_rate = rate_mcg_per_kg_min;
    // Placeholder: apply rate to hardware with dual watchdog verification.
    return true;
}

float pump_hal_get_current_rate(void) {
    return g_rate;
}

void pump_hal_trigger_alarm(void) {
    // Placeholder: actuate audible/visual alarm and notify gateway.
    printf("Alarm triggered.\n");
}
