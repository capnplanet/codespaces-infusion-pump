# Pump Firmware Module

Safety-critical firmware for the infusion pump controller. Implements deterministic dosing enforcement, secure communications with bedside gateway, and hardware monitoring. Code adheres to IEC 62304 Class C expectations and MISRA C guidelines.

## Structure

- `src/` — Core application logic (scheduler, communications, diagnostics).
- `include/` — Public interfaces and hardware abstraction layer definitions.
- `tests/` — Unit and integration tests (Ceedling or Unity based).

## Build

1. Install cross-compilation toolchain and CMake.
2. Configure build: `cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake`.
3. Compile: `cmake --build build`.
4. Run tests: `ctest --test-dir build`.

All changes require requirements traceability updates and verification evidence before merging.
