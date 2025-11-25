#include "communication.h"

#include <stdio.h>

void comms_init(void) {
    // Placeholder: initialize authenticated field bus stack.
    printf("Communications initialized.\n");
}

int comms_send_signed_command(const uint8_t *payload, size_t length) {
    (void)payload;
    (void)length;
    // Placeholder: sign payload and dispatch to gateway.
    return 0;
}

int comms_receive_gateway_message(uint8_t *buffer, size_t length) {
    (void)buffer;
    (void)length;
    // Placeholder: receive message with sequence counter and verify signature.
    return 0;
}
