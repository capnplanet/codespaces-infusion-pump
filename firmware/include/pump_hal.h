#ifndef PUMP_HAL_H
#define PUMP_HAL_H

#include <stdbool.h>

void pump_hal_init(void);
bool pump_hal_set_infusion_rate(float rate_mcg_per_kg_min);
float pump_hal_get_current_rate(void);
void pump_hal_trigger_alarm(void);

#endif
