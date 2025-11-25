cmake_minimum_required(VERSION 3.20)
project(vaso_pump_firmware C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    -Werror
)

include_directories(include)

add_executable(pump_firmware
    src/main.c
    src/safety_controller.c
    src/communication.c
)

target_include_directories(pump_firmware PRIVATE include)

enable_testing()

add_executable(test_safety_controller
    tests/test_safety_controller.c
    src/safety_controller.c
)

target_include_directories(test_safety_controller PRIVATE include)

add_test(NAME safety_controller COMMAND test_safety_controller)
