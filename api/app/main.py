from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import cli, dashboard, dna, health, models, quota, sequences

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "HTTP snapshot API for Grok Imagine Cinematic Studio — "
        "shared backend for Streamlit, TUI, and React web_dashboard."
    ),
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(cli.router)
app.include_router(dna.router)
app.include_router(sequences.router)
app.include_router(quota.router)
app.include_router(models.router)


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "snapshot": f"{settings.api_prefix}/dashboard/snapshot",
    }
