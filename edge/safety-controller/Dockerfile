# Gateway Safety Controller Dockerfile
# Build stage
FROM rust:1.75 as builder
WORKDIR /src
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

# Runtime stage
FROM gcr.io/distroless/cc-debian12
COPY --from=builder /src/target/release/gateway_safety_controller /usr/local/bin/gateway_safety_controller
ENTRYPOINT ["/usr/local/bin/gateway_safety_controller"]
