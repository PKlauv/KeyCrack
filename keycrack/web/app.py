import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import aiosqlite
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from keycrack.generator import PersonalInfo, strip_to_alpha, validate_dob
from keycrack.pcfg import generate_passwords_pcfg

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DATA_DIR / "bugs.db"
db: aiosqlite.Connection | None = None

CREATE_BUGS_TABLE = """
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    email TEXT,
    category TEXT NOT NULL DEFAULT 'Other',
    created_at TEXT NOT NULL
);
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute(CREATE_BUGS_TABLE)
    await db.commit()
    yield
    await db.close()


app = FastAPI(title="KeyCrack", description="Password awareness tool", lifespan=lifespan)

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


# --- Bug Reports ---


class BugCategory(str, Enum):
    UI_ISSUE = "UI issue"
    WRONG_PASSWORDS = "Wrong passwords"
    CRASH = "Crash"
    OTHER = "Other"


class BugReportRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    email: Optional[str] = None
    category: BugCategory = BugCategory.OTHER


class BugReportResponse(BaseModel):
    id: int
    message: str


class BugReportDetail(BaseModel):
    id: int
    description: str
    email: Optional[str]
    category: str
    created_at: str


@app.get("/report-bug")
async def report_bug_page():
    return FileResponse(STATIC_DIR / "report-bug.html")


@app.post("/api/bugs", response_model=BugReportResponse, status_code=201)
async def submit_bug(report: BugReportRequest):
    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        "INSERT INTO bugs (description, email, category, created_at) VALUES (?, ?, ?, ?)",
        (report.description, report.email, report.category.value, now),
    )
    await db.commit()
    return BugReportResponse(id=cursor.lastrowid, message="Bug report submitted.")


@app.get("/admin/bugs")
async def admin_bugs_page():
    return FileResponse(STATIC_DIR / "admin-bugs.html")


@app.get("/api/bugs", response_model=list[BugReportDetail])
async def list_bugs():
    cursor = await db.execute("SELECT * FROM bugs ORDER BY id DESC")
    rows = await cursor.fetchall()
    return [
        BugReportDetail(
            id=row["id"],
            description=row["description"],
            email=row["email"],
            category=row["category"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
