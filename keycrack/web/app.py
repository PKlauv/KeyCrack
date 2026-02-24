import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from keycrack.cli import strip_to_alpha, validate_dob
from keycrack.generator import PersonalInfo, generate_passwords

app = FastAPI(title="KeyCrack", description="Password awareness tool")

STATIC_DIR = Path(__file__).parent / "static"


class PasswordRequest(BaseModel):
    first_name: str
    last_name: str
    dob: str
    pet_name: Optional[str] = None


class PasswordResponse(BaseModel):
    passwords: list[str]
    count: int
    elapsed_seconds: float


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/generate", response_model=PasswordResponse)
async def generate(req: PasswordRequest):
    dob = validate_dob(req.dob)

    clean_first = strip_to_alpha(req.first_name)
    clean_last = strip_to_alpha(req.last_name)
    clean_pet = strip_to_alpha(req.pet_name) if req.pet_name else ""

    if not clean_first:
        raise HTTPException(status_code=422, detail="First name must contain at least one letter.")
    if not clean_last:
        raise HTTPException(status_code=422, detail="Last name must contain at least one letter.")

    info = PersonalInfo(
        first_name=clean_first,
        last_name=clean_last,
        dob=dob,
        pet_name=clean_pet if clean_pet else None,
    )

    start = time.perf_counter()
    passwords = generate_passwords(info)
    elapsed = time.perf_counter() - start

    sorted_passwords = sorted(passwords)
    return PasswordResponse(
        passwords=sorted_passwords,
        count=len(sorted_passwords),
        elapsed_seconds=round(elapsed, 4),
    )
