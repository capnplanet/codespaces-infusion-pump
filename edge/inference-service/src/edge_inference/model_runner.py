"""ONNX runtime wrapper for MAP prediction."""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Tuple

import numpy as np
import onnxruntime as ort


class ModelRunner:
    """Executes MAP prediction ONNX models with safety envelopes."""

    def __init__(self, model_path: str, inference_timeout_ms: int) -> None:
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        self._session = ort.InferenceSession(model_path, so, providers=["CPUExecutionProvider"])
        self._timeout = inference_timeout_ms

    def run(self, features: Dict[str, Iterable[float]]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Run inference and return predictions plus metadata."""
        start = time.monotonic()
        inputs = {k: np.asarray(v, dtype=np.float32) for k, v in features.items()}
        outputs = self._session.run(None, inputs)
        duration_ms = (time.monotonic() - start) * 1000
        if duration_ms > self._timeout:
            raise RuntimeError("Inference exceeded timeout budget")
        metadata = {"inference_ms": duration_ms}
        if len(outputs) > 1:
            confidence_output = np.asarray(outputs[1])
            if confidence_output.size == 1:
                metadata["confidence"] = float(confidence_output.reshape(-1)[0])
        return outputs[0], metadata
