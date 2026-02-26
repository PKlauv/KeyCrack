import re
from dataclasses import dataclass
from datetime import datetime
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


def case_variations(word: str) -> list[str]:
    if not word:
        return []
    return list(dict.fromkeys([
        word.lower(),
        word.upper(),
        word.capitalize(),
    ]))


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


def _build_high_priority_passwords(info: PersonalInfo) -> list[str]:
    """Generate the most common/realistic password patterns people actually use."""
    first = info.first_name.lower()
    first_cap = info.first_name.capitalize()
    last = info.last_name.lower()
    last_cap = info.last_name.capitalize()
    pet = (info.pet_name or "").lower()
    pet_cap = (info.pet_name or "").capitalize()

    yyyy = info.dob[4:8]
    yy = yyyy[2:4]
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    mmdd = mm + dd

    current_year = str(datetime.now().year)
    next_year = str(datetime.now().year + 1)

    initials_lower = (first[0] + last[0]) if first and last else ""
    initials_upper = initials_lower.upper()

    passwords = []

    # Tier 1: The most common patterns people actually use
    # name123 is the single most common pattern
    for name, name_cap in [(first, first_cap), (last, last_cap)]:
        passwords.extend([
            name + "123",
            name_cap + "123",
            name + "1234",
            name_cap + "1234",
            name + "12345",
            name_cap + "12345",
            name + "1",
            name_cap + "1",
            name + "!",
            name_cap + "!",
            name + "!!",
            name_cap + "!!",
            name + yyyy,
            name_cap + yyyy,
            name + yy,
            name_cap + yy,
            name + "123!",
            name_cap + "123!",
        ])

    # Pet name combos (people love pet names)
    if pet:
        for p, p_cap in [(pet, pet_cap)]:
            passwords.extend([
                p + "123",
                p_cap + "123",
                p + "1",
                p_cap + "1",
                p + "!",
                p_cap + "!",
                p + yyyy,
                p_cap + yyyy,
                p + yy,
                p_cap + yy,
                p + "1234",
                p_cap + "1234",
                p + mmdd,
                p_cap + mmdd,
                p + mm + dd + yy,
                p_cap + mm + dd + yy,
            ])

    # Tier 2: Name + DOB patterns, Name + current year
    for name, name_cap in [(first, first_cap), (last, last_cap)]:
        passwords.extend([
            name + mmdd,
            name_cap + mmdd,
            name + mm + dd + yy,
            name_cap + mm + dd + yy,
            name + mm + dd + yyyy,
            name_cap + mm + dd + yyyy,
            mmdd + name,
            mmdd + name_cap,
            name + current_year,
            name_cap + current_year,
            name + next_year,
            name_cap + next_year,
        ])

    # Tier 3: Emotional/phrase patterns
    passwords.extend([
        "ilove" + first,
        "iLove" + first_cap,
        "ilove" + last,
        first + "4ever",
        first_cap + "4ever",
        first + first,
        first_cap + first_cap,
    ])

    if pet:
        passwords.extend([
            "ilove" + pet,
            "iLove" + pet_cap,
            pet + pet,
        ])

    # Tier 4: Initials + DOB
    if initials_lower:
        passwords.extend([
            initials_lower + yyyy,
            initials_upper + yyyy,
            initials_lower + mmdd,
            initials_upper + mmdd,
            initials_lower + mm + dd + yyyy,
            initials_upper + mm + dd + yyyy,
            initials_lower + "123",
            initials_upper + "123",
        ])

    # Tier 5: Name + separator + DOB (common but less frequent)
    for name, name_cap in [(first, first_cap)]:
        passwords.extend([
            name + "_" + yyyy,
            name_cap + "_" + yyyy,
            name + "." + yyyy,
            name + "_" + mmdd,
        ])

    # Deduplicate while preserving order, filter empty strings
    seen = set()
    unique = []
    for pw in passwords:
        if pw and pw not in seen:
            seen.add(pw)
            unique.append(pw)
    return unique


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

    # E) High-priority realistic passwords
    for pw in _build_high_priority_passwords(info):
        passwords.add(pw)

    passwords.discard("")
    return {pw for pw in passwords if len(pw) >= MIN_LENGTH}


def _score_password(pw: str, info: PersonalInfo) -> float:
    score = 0.0
    pw_lower = pw.lower()
    first = info.first_name.lower()
    last = info.last_name.lower()
    pet = (info.pet_name or "").lower()
    yyyy = info.dob[4:8]
    yy = yyyy[2:4]
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    current_year = str(datetime.now().year)

    length = len(pw)
    has_first = bool(first and first in pw_lower)
    has_last = bool(last and last in pw_lower)
    has_pet = bool(pet and pet in pw_lower)
    name_count = sum([has_first, has_last, has_pet])

    # Capitalization tiebreaker: lowercase/capitalize > ALL CAPS
    if pw == pw.lower() or pw == pw.capitalize():
        score += 2.0
    elif pw == pw.upper():
        score -= 5.0

    # Exact pattern matching for the most realistic passwords
    name_bases = []
    if first:
        name_bases.append(first)
    if last:
        name_bases.append(last)
    if pet:
        name_bases.append(pet)

    mmdd = mm + dd

    for i, name in enumerate(name_bases):
        # Rank offset: first=0, last=-2, pet=-4
        rank_offset = -2.0 * i
        name_cap = name.capitalize()

        # name123 / Name123 - THE most common pattern
        if pw_lower == name + "123" or pw == name_cap + "123":
            score += 50.0 + rank_offset
        # name + birth year (Name1983)
        elif pw_lower == name + yyyy or pw == name_cap + yyyy:
            score += 44.0 + rank_offset
        # name + mmdd (james0314)
        elif pw_lower == name + mmdd or pw == name_cap + mmdd:
            score += 42.0 + rank_offset
        # name + 2-digit year
        elif pw_lower == name + yy or pw == name_cap + yy:
            score += 38.0 + rank_offset
        # name + current year
        elif pw_lower == name + current_year or pw == name_cap + current_year:
            score += 37.0 + rank_offset
        # name + mmddyy (james031483)
        elif pw_lower == name + mm + dd + yy or pw == name_cap + mm + dd + yy:
            score += 36.0 + rank_offset
        # name1234
        elif pw_lower == name + "1234" or pw == name_cap + "1234":
            score += 36.0 + rank_offset
        # name + "1"
        elif pw in (name_cap + "1", name + "1"):
            score += 35.0 + rank_offset
        # name!
        elif pw in (name_cap + "!", name + "!"):
            score += 34.0 + rank_offset
        # name + mmddyyyy (james03141983)
        elif pw_lower == name + mm + dd + yyyy or pw == name_cap + mm + dd + yyyy:
            score += 33.0 + rank_offset
        # name12345
        elif pw_lower == name + "12345" or pw == name_cap + "12345":
            score += 32.0 + rank_offset
        # mmdd + name (0314james)
        elif pw_lower == mmdd + name or pw == mmdd + name_cap:
            score += 30.0 + rank_offset
        # name!!
        elif pw in (name_cap + "!!", name + "!!"):
            score += 26.0 + rank_offset
        # name123!
        elif pw_lower == name + "123!" or pw == name_cap + "123!":
            score += 26.0 + rank_offset

    # "ilove" patterns
    if first and pw_lower == "ilove" + first:
        score += 35.0
    elif first and pw == "iLove" + first.capitalize():
        score += 34.0
    elif pet and pw_lower == "ilove" + pet:
        score += 33.0

    # Repeated name
    if first and pw_lower == first + first:
        score += 30.0

    # Name + 4ever
    if first and (pw_lower == first + "4ever" or pw == first.capitalize() + "4ever"):
        score += 29.0

    # Initials-based patterns
    initials = (first[0] + last[0]) if first and last else ""
    if initials:
        initials_upper = initials.upper()
        if pw_lower == initials + yyyy or pw == initials_upper + yyyy:
            score += 40.0
        elif pw_lower == initials + mmdd or pw == initials_upper + mmdd:
            score += 39.0
        elif pw_lower == initials + mm + dd + yyyy or pw == initials_upper + mm + dd + yyyy:
            score += 38.0
        elif pw_lower == initials + "123" or pw == initials_upper + "123":
            score += 37.0

    # Compound name patterns (no suffix)
    if first and last and pw_lower == first + last:
        score += 35.0
    elif first and last and pw_lower == first[0] + last:
        score += 34.0
    elif first and pet and pw_lower == first + pet:
        score += 33.0

    # Separator patterns (name_year, name.mmdd, etc.)
    for name in name_bases:
        name_cap = name.capitalize()
        matched_sep = False
        for sep in ("_", ".", "-"):
            if pw in (name + sep + yyyy, name_cap + sep + yyyy):
                score += 28.0
                matched_sep = True
                break
            elif pw in (name + sep + mmdd, name_cap + sep + mmdd):
                score += 27.0
                matched_sep = True
                break
        if matched_sep:
            break

    # If we already matched an exact pattern, return early
    if score > 0:
        return score

    # General scoring for everything else
    # Short passwords
    if length <= 8:
        score += 6.0
    elif length <= 10:
        score += 4.0
    elif length <= 12:
        score += 2.0

    # Simple capitalization
    if pw == pw.lower() or pw == pw.capitalize():
        score += 3.0

    # Contains a single personal name
    if has_first:
        score += 4.0
    if has_pet:
        score += 4.0
    if has_last:
        score += 1.0

    # Penalize compound names
    if name_count >= 2:
        score -= 6.0

    # Common suffix endings
    for suf in ("123", "1234", "12345"):
        if pw.endswith(suf):
            score += 3.0
            break
    for suf in ("!", "!!"):
        if pw.endswith(suf):
            score += 1.0
            break

    # Year in password
    if yyyy in pw:
        score += 3.0
    elif current_year in pw:
        score += 2.0
    elif yy in pw:
        score += 1.0

    # Penalize separators (people don't usually type john_1990)
    if any(sep in pw for sep in ("_", "-", ".")):
        score -= 3.0

    # Penalize leet speak
    leet_chars = sum(1 for c in pw if c in "@$037")
    if leet_chars >= 2:
        score -= 10.0

    # Penalize reversed names
    if first and first[::-1] in pw_lower:
        score -= 6.0
    if last and last[::-1] in pw_lower:
        score -= 6.0

    # Penalize long passwords
    if length > 16:
        score -= 4.0

    return score


def _classify_password(pw: str, info: PersonalInfo) -> str:
    """Classify a password into a fine-grained structural template for diversity.

    Each template represents a visually distinct password pattern so the top-20
    list never shows two entries that look like the same idea.
    """
    pw_lower = pw.lower()
    first = info.first_name.lower()
    last = info.last_name.lower()
    pet = (info.pet_name or "").lower()
    yyyy = info.dob[4:8]
    yy = yyyy[2:4]
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    mmdd = mm + dd
    current_year = str(datetime.now().year)
    next_year = str(datetime.now().year + 1)
    initials = (first[0] + last[0]) if first and last else ""

    names = [n for n in [first, last, pet] if n]

    # 1. ilove -- starts with "ilove"
    if pw_lower.startswith("ilove"):
        return "ilove"

    # 2. name_4ever -- ends with "4ever"
    for name in names:
        if pw_lower == name + "4ever" or pw_lower == name.capitalize() + "4ever":
            return "name_4ever"

    # 3. name_repeat -- name+name pattern
    for name in names:
        if pw_lower == name + name:
            return "name_repeat"

    # 4. initials -- starts with 2-char initials, rest is digits/dob
    if initials and len(pw) > 2:
        prefix = pw_lower[:2]
        if prefix == initials:
            rest = pw[2:]
            if rest.isdigit() or rest in (yyyy, yy, mmdd, mm + dd + yy, mm + dd + yyyy):
                return "initials"

    # 5. compound -- first+last, first+pet, initial+last (no trailing digits)
    if first and last and pw_lower in (first + last, last + first):
        return "compound"
    if first and last and pw_lower in (first[0] + last, last[0] + first):
        return "compound"
    if first and pet and pw_lower in (first + pet, pet + first):
        return "compound"
    if last and pet and pw_lower in (last + pet, pet + last):
        return "compound"

    # 6. seq_123_bang -- ends with "123!"
    if pw_lower.endswith("123!"):
        return "seq_123_bang"

    # 7. seq_12345 -- ends with "12345" (checked before 1234)
    if pw_lower.endswith("12345"):
        return "seq_12345"

    # 8. seq_1234 -- ends with "1234" (checked after 12345)
    if pw_lower.endswith("1234"):
        return "seq_1234"

    # 9. seq_123 -- ends with "123" (checked after 1234)
    if pw_lower.endswith("123"):
        return "seq_123"

    # 10. bang_double -- ends with "!!" (no digits before)
    if pw.endswith("!!"):
        before = pw[:-2]
        if before and not before[-1].isdigit():
            return "bang_double"

    # 11. bang_single -- ends with "!" (no digits before)
    if pw.endswith("!"):
        before = pw[:-1]
        if before and not before[-1].isdigit():
            return "bang_single"

    # 12. full_dob -- contains mmddyyyy or mmddyy
    for name in names:
        if pw_lower in (name + mm + dd + yyyy, name.capitalize() + mm + dd + yyyy,
                        mm + dd + yyyy + name):
            return "full_dob"
        if pw_lower in (name + mm + dd + yy, name.capitalize() + mm + dd + yy,
                        mm + dd + yy + name):
            return "full_dob"

    # 13. birthday_prefix -- starts with mmdd + name
    for name in names:
        if pw_lower in (mmdd + name, mmdd + name.capitalize()):
            return "birthday_prefix"

    # 14. birthday -- name + mmdd
    for name in names:
        if pw_lower in (name + mmdd, name.capitalize() + mmdd):
            return "birthday"

    # 15. current_year -- ends with current or next year
    if pw_lower.endswith(current_year) or pw_lower.endswith(next_year):
        return "current_year"

    # 16. birth_year -- ends with yyyy or yy
    for name in names:
        if pw_lower in (name + yyyy, name.capitalize() + yyyy,
                        name + yy, name.capitalize() + yy):
            return "birth_year"

    # 17. separator -- contains _, -, or . between name and digits
    if any(sep in pw for sep in ("_", "-", ".")):
        return "separator"

    # 18. name_one -- ends with single digit
    if len(pw) > 1 and pw[-1].isdigit() and not pw[-2].isdigit():
        return "name_one"

    # 19. other -- fallback
    return "other"


@dataclass
class CategorizedPasswords:
    name_based: set[str]
    leet_speak: set[str]
    name_dob: set[str]
    dob_name: set[str]
    dob_only: set[str]
    top_passwords: list[str]


def generate_passwords_categorized(info: PersonalInfo) -> CategorizedPasswords:
    raw_bases = build_base_words(info)
    dob_pats = dob_patterns(info.dob)

    # Build plain and leet word lists separately for categorization
    plain_words = []
    leet_words = []
    for base in raw_bases:
        plain_words.extend(case_variations(base))
        plain_words.extend(case_variations(base[::-1]))
        leet_words.extend(case_variations(leet_speak(base)))
        leet_words.extend(case_variations(leet_speak(base[::-1])))

    raw_name_based: set[str] = set()
    raw_leet: set[str] = set()
    raw_name_dob: set[str] = set()
    raw_dob_name: set[str] = set()
    raw_dob_only: set[str] = set()

    # Name-based: plain words + suffixes
    for word in plain_words:
        for suffix in SUFFIXES:
            pw = word + suffix
            if pw and len(pw) >= MIN_LENGTH:
                raw_name_based.add(pw)

    # Add high-priority passwords to name-based
    for pw in _build_high_priority_passwords(info):
        if len(pw) >= MIN_LENGTH:
            raw_name_based.add(pw)

    # Leet speak: leet words + suffixes
    for word in leet_words:
        for suffix in SUFFIXES:
            pw = word + suffix
            if pw and len(pw) >= MIN_LENGTH:
                raw_leet.add(pw)

    # Name + DOB
    for word in plain_words + leet_words:
        for sep in SEPARATORS:
            for pat in dob_pats:
                pw = word + sep + pat
                if pw and len(pw) >= MIN_LENGTH:
                    raw_name_dob.add(pw)

    # DOB + Name
    for pat in dob_pats:
        for sep in SEPARATORS:
            for word in plain_words + leet_words:
                pw = pat + sep + word
                if pw and len(pw) >= MIN_LENGTH:
                    raw_dob_name.add(pw)

    # DOB only
    for pat in dob_pats:
        for suffix in SUFFIXES:
            pw = pat + suffix
            if pw and len(pw) >= MIN_LENGTH:
                raw_dob_only.add(pw)

    # Deduplicate across categories by priority
    seen: set[str] = set()

    leet_speak_cat = raw_leet - seen
    seen |= leet_speak_cat

    name_dob_cat = raw_name_dob - seen
    seen |= name_dob_cat

    dob_name_cat = raw_dob_name - seen
    seen |= dob_name_cat

    name_based_cat = raw_name_based - seen
    seen |= name_based_cat

    dob_only_cat = raw_dob_only - seen

    # Score all passwords for top 30
    all_passwords = leet_speak_cat | name_dob_cat | dob_name_cat | name_based_cat | dob_only_cat
    scored = [(pw, _score_password(pw, info)) for pw in all_passwords]
    scored.sort(key=lambda x: (-x[1], x[0]))

    # Strategy-bucket-capped selection for structural diversity
    seen_lower: set[str] = set()
    strategy_counts: dict[str, int] = {}
    MAX_PER_STRATEGY = 2
    top_30: list[str] = []

    for pw, _ in scored:
        key = pw.lower()
        if key in seen_lower:
            continue
        strategy = _classify_password(pw, info)
        if strategy_counts.get(strategy, 0) >= MAX_PER_STRATEGY:
            continue
        seen_lower.add(key)
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        top_30.append(pw)
        if len(top_30) == 30:
            break

    return CategorizedPasswords(
        name_based=name_based_cat,
        leet_speak=leet_speak_cat,
        name_dob=name_dob_cat,
        dob_name=dob_name_cat,
        dob_only=dob_only_cat,
        top_passwords=top_30,
    )
