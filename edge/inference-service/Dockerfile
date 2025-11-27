# Edge Inference service Dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install .
COPY src ./src
ENV PYTHONPATH=/app/src
EXPOSE 8080
CMD ["uvicorn", "edge_inference.service:app", "--host", "0.0.0.0", "--port", "8080"]
