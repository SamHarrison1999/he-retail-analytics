from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, Response

from src.infra.db import ensure_engine


def _api_key() -> str | None:
    return os.environ.get("API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure DB exists
    ensure_engine()
    # Ensure static root exists
    static_root = Path(os.environ.get("RESULTS_DIR") or (Path.cwd() / "results"))
    static_root.mkdir(parents=True, exist_ok=True)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="HE Retail Analytics", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Public static files at /files/**
    static_root = Path(os.environ.get("RESULTS_DIR") or (Path.cwd() / "results"))
    app.mount("/files", StaticFiles(directory=static_root, html=False), name="files")

    @app.middleware("http")
    async def auth_guard(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Allow health and static files without auth
        if request.url.path == "/healthz" or request.url.path.startswith("/files/"):
            return await call_next(request)

        api_key = _api_key()
        if api_key:
            presented = request.headers.get("X-API-Key")
            if presented != api_key:
                return JSONResponse({"detail": "Forbidden"}, status_code=403)

        return await call_next(request)

    @app.get("/healthz")
    async def healthz() -> dict[str, bool]:
        return {"ok": True}

    # Mount routers
    from src.aggregator.routes.jobs import router as jobs_router

    app.include_router(jobs_router)

    return app


app = create_app()