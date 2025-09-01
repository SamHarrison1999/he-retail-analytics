from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import shutil

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "results/uploads/catalogs")

@router.post("/catalog")
async def upload_catalog(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="only .csv allowed")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}")
    with open(dest, "wb") as out:
      shutil.copyfileobj(file.file, out)
    return JSONResponse({"server_path": dest})
