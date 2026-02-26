import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from keycrack.generator import PersonalInfo, strip_to_alpha, validate_dob
from keycrack.pcfg import generate_passwords_pcfg

app = FastAPI(title="KeyCrack", description="Password awareness tool")

STATIC_DIR = Path(__file__).parent / "static"


class PasswordRequest(BaseModel):
    first_name: str
    last_name: str
    dob: str
    pet_name: Optional[str] = None


class TopPassword(BaseModel):
    password: str
    probability: float


class CategoryDetail(BaseModel):
    label: str
    description: str
    passwords: list[str]
    count: int


class CategorizedPasswordResponse(BaseModel):
    categories: dict[str, CategoryDetail]
    top_passwords: list[TopPassword]
    total_count: int
    elapsed_seconds: float


CATEGORY_META = {
    "name_based": {
        "label": "Name-Based",
        "description": "Name combinations with common suffixes",
    },
    "leet_speak": {
        "label": "Leet Speak",
        "description": "Letter substitutions (a=@, e=3, s=$, etc.) with suffixes",
    },
    "name_dob": {
        "label": "Name + DOB",
        "description": "Name followed by date-of-birth patterns",
    },
    "dob_name": {
        "label": "DOB + Name",
        "description": "Date-of-birth patterns followed by name",
    },
    "dob_only": {
        "label": "DOB Only",
        "description": "Date-of-birth patterns with common suffixes",
    },
}


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/generate", response_model=CategorizedPasswordResponse)
async def generate(req: PasswordRequest):
    dob = validate_dob(req.dob.strip())

    clean_first = strip_to_alpha(req.first_name.strip())
    clean_last = strip_to_alpha(req.last_name.strip())
    clean_pet = strip_to_alpha(req.pet_name.strip()) if req.pet_name else ""

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
    result = generate_passwords_pcfg(info)
    elapsed = time.perf_counter() - start

    categories = {}
    total = 0
    for key, meta in CATEGORY_META.items():
        pws = sorted(getattr(result, key))
        categories[key] = CategoryDetail(
            label=meta["label"],
            description=meta["description"],
            passwords=pws,
            count=len(pws),
        )
        total += len(pws)

    top_passwords = [
        TopPassword(password=pw, probability=prob)
        for pw, prob in result.top_passwords
    ]

    return CategorizedPasswordResponse(
        categories=categories,
        top_passwords=top_passwords,
        total_count=total,
        elapsed_seconds=round(elapsed, 4),
    )
