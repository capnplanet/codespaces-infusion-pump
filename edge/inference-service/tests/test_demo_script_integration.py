from __future__ import annotations

import os
import subprocess
from concurrent import futures
from pathlib import Path

import grpc

from edge_inference.ingestion_proto import telemetry_pb2, telemetry_pb2_grpc


class CaptureIngestionService(telemetry_pb2_grpc.TelemetryIngestionServicer):
    def __init__(self) -> None:
        self.event_count = 0
        self.api_key = None
        self.device_id = None

    def StreamTelemetry(self, request_iterator, context):
        metadata = dict(context.invocation_metadata())
        self.api_key = metadata.get("x-api-key")
        self.device_id = metadata.get("x-device-id")

        for _ in request_iterator:
            self.event_count += 1

        return telemetry_pb2.TelemetryAck(accepted=True)


def test_run_synthetic_demo_script_replays_fixture(tmp_path: Path) -> None:
    service = CaptureIngestionService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    telemetry_pb2_grpc.add_TelemetryIngestionServicer_to_server(service, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()

    try:
        repo_root = Path(__file__).resolve().parents[3]
        script_path = repo_root / "scripts" / "run_synthetic_demo.sh"
        output_dir = tmp_path / "demo-output"

        env = os.environ.copy()
        env["INGEST_TARGET"] = f"127.0.0.1:{port}"
        env["DEVICE_API_KEY"] = "demo-key"
        env["DEMO_SESSIONS"] = "2"
        env["DEMO_STEPS"] = "3"

        subprocess.run([str(script_path), str(output_dir)], cwd=repo_root, env=env, check=True)

        assert service.event_count == 6
        assert service.api_key == "demo-key"
        assert service.device_id is None
        assert (output_dir / "fixtures" / "telemetry_stream.jsonl").exists()
    finally:
        server.stop(grace=0)
