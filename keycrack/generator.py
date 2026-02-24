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

SUFFIXES = [
    "", "1", "2", "12", "123", "1234", "12345",
    "!", "!!", "!1", "!@", "!123", "@", "#", "$", "*",
    "69", "420", "007", "01", "11", "22", "99",
]

SEPARATORS = ["", "_", "-", ".", "@"]

MIN_LENGTH = 8


@dataclass
class PersonalInfo:
    first_name: str
    last_name: str
    dob: str  # MMDDYYYY
    pet_name: Optional[str] = None


def leet_speak(word: str) -> str:
    return "".join(LEET_MAP.get(c.lower(), c) for c in word)


def case_variations(word: str) -> list[str]:
    if not word:
        return []
    return [
        word.lower(),
        word.upper(),
        word.capitalize(),
        word[0].lower() + word[1:].upper() if len(word) > 1 else word.lower(),
    ]


def dob_patterns(dob: str) -> list[str]:
    mm = dob[0:2]
    dd = dob[2:4]
    yyyy = dob[4:8]
    yy = yyyy[2:4]
    return [
        yyyy, yy, mm + dd, dd + mm,
        mm + dd + yyyy, dd + mm + yyyy,
        mm + dd + yy, dd + mm + yy,
        yyyy + mm + dd,
        mm + yyyy, dd + yyyy,
        mm + yy, dd + yy,
        mm, dd,
    ]


def build_base_words(info: PersonalInfo) -> list[str]:
    first = info.first_name
    last = info.last_name
    pet = info.pet_name or ""

    bases = [first, last]
    if pet:
        bases.append(pet)

    bases.append(first + last)
    bases.append(first[0] + last if first else last)
    bases.append(first + last[0] if last else first)

    if pet:
        bases.append(first + pet)
        bases.append(pet + first)
        bases.append(last + pet)

    return [b for b in bases if b]


def expand_bases(bases: list[str]) -> list[str]:
    expanded = []
    for base in bases:
        expanded.append(base)
        expanded.append(leet_speak(base))
        expanded.append(base[::-1])
    return expanded


def generate_passwords(info: PersonalInfo) -> set[str]:
    passwords = set()

    raw_bases = build_base_words(info)
    expanded = expand_bases(raw_bases)

    all_words = []
    for word in expanded:
        all_words.extend(case_variations(word))

    dob_pats = dob_patterns(info.dob)

    # A) Word + suffix
    for word in all_words:
        for suffix in SUFFIXES:
            passwords.add(word + suffix)

    # B) Word + separator + DOB pattern
    for word in all_words:
        for sep in SEPARATORS:
            for pat in dob_pats:
                passwords.add(word + sep + pat)

    # C) DOB pattern + separator + word
    for pat in dob_pats:
        for sep in SEPARATORS:
            for word in all_words:
                passwords.add(pat + sep + word)

    # D) DOB pattern + suffix
    for pat in dob_pats:
        for suffix in SUFFIXES:
            passwords.add(pat + suffix)

    passwords.discard("")
    return {pw for pw in passwords if len(pw) >= MIN_LENGTH}
