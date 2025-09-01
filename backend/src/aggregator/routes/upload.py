from __future__ import annotations

import os
import shutil
import uuid
from typing import Final

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["upload"])

RESULTS_DIR: Final[str] = os.environ.get("RESULTS_DIR", "results")
UPLOAD_DIR: Final[str] = os.path.join(RESULTS_DIR, "uploads", "catalogs")


@router.post("/upload/catalog")
async def upload_catalog(file: UploadFile = File(...)) -> JSONResponse:
    # Resolve a safe filename even if client didn't send one (mypy-safe)
    original_name: str = file.filename or "catalog.csv"
    safe_name: str = os.path.basename(original_name)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{safe_name}")

    # Copy the stream to disk (separate lines for ruff E70x)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)

    return JSONResponse({"server_path": dest})
