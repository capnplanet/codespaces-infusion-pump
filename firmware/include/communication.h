#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <stddef.h>
#include <stdint.h>

void comms_init(void);
int comms_send_signed_command(const uint8_t *payload, size_t length);
int comms_receive_gateway_message(uint8_t *buffer, size_t length);

#endif
