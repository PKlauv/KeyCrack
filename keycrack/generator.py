import re
from dataclasses import dataclass
from typing import Optional

LEET_MAP = {
    "a": "@",
    "e": "3",
    "i": "1",
    "o": "0",
    "s": "$",
    "t": "7",
    "l": "1",
}

MIN_LENGTH = 6


def validate_dob(dob: str) -> str:
    if not re.fullmatch(r"\d{8}", dob):
        raise ValueError("DOB must be exactly 8 digits (MMDDYYYY).")
    mm = int(dob[0:2])
    dd = int(dob[2:4])
    if mm < 1 or mm > 12:
        raise ValueError(f"Invalid month: {mm:02d}. Must be 01-12.")
    if dd < 1 or dd > 31:
        raise ValueError(f"Invalid day: {dd:02d}. Must be 01-31.")
    return dob


def strip_to_alpha(name: str) -> str:
    return re.sub(r"[^a-zA-Z]", "", name)


@dataclass
class PersonalInfo:
    first_name: str
    last_name: str
    dob: str  # MMDDYYYY
    pet_name: Optional[str] = None


def leet_speak(word: str) -> str:
    return "".join(LEET_MAP.get(c.lower(), c) for c in word)


@dataclass
class CategorizedPasswords:
    name_based: set[str]
    leet_speak: set[str]
    name_dob: set[str]
    dob_name: set[str]
    dob_only: set[str]
    top_passwords: list[tuple[str, float]]
