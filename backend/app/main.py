"""FastAPI entry point for Document AI Platform."""

from fastapi import FastAPI

app = FastAPI(
    title="Document AI Thesis Platform API",
    version="0.1.0",
    description="Export Document Management Platform with Document AI",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok", "service": "document-ai-backend"}
