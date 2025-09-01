from __future__ import annotations
import os
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.staticfiles import StaticFiles
from src.aggregator.routes.jobs import router as jobs_router
from src.aggregator.routes.upload import router as upload_router
from src.infra.db import ensure_engine

log = logging.getLogger("he-api")

def create_app() -> FastAPI:
    API_KEY = os.environ.get("API_KEY", "devkey")
    CORS_ALLOW_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOW_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    COOKIE_NAME = os.environ.get("API_COOKIE_NAME", "he_api_token")
    RESULTS_DIR = os.environ.get("RESULTS_DIR", "../results")
    AUTH_HEADER = os.environ.get("API_HEADER_NAME", "X-API-Key")

    log.info("RESULTS_DIR=%s DB_URL=%s CORS=%s", RESULTS_DIR, os.environ.get("DB_URL"), CORS_ALLOW_ORIGINS)

    app = FastAPI(title="HE API", version="0.1.0")
    ensure_engine(os.environ.get("DB_URL"))
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ALLOW_ORIGINS, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])

    @app.middleware("http")
    async def auth_guard(request: Request, call_next):
        if request.url.path.startswith(("/healthz","/api/login","/metrics","/files/")):
            return await call_next(request)
        header_token = request.headers.get(AUTH_HEADER) or (
            request.headers.get("Authorization","").removeprefix("Bearer ").strip()
        )
        cookie_token = request.cookies.get(COOKIE_NAME)
        token = header_token or cookie_token
        if not API_KEY or token == API_KEY:
            return await call_next(request)
        raise HTTPException(status_code=401, detail="unauthorized")

    @app.post("/api/login")
    async def login(req: Request, resp: Response):
        data = await req.json()
        token = (data.get("token") or "").strip()
        if API_KEY and token != API_KEY:
            raise HTTPException(status_code=401, detail="invalid token")
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, samesite="lax",
                        secure=False, max_age=7*24*3600)
        return {"ok": True}

    @app.get("/healthz")
    async def healthz(): return {"ok": True}

    app.include_router(jobs_router)
    app.include_router(upload_router)
    app.mount("/metrics", make_asgi_app())
    app.mount("/files", StaticFiles(directory=RESULTS_DIR), name="files")
    return app

app = create_app()
