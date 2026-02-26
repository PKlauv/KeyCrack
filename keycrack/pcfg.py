# Probabilistic Context-Free Grammar (PCFG) password generator. Defines a
# grammar of 30 templates (name+digits, name+DOB, leet variants, etc.), expands
# every combination via Cartesian product, scores them by probability, and
# returns a diverse top-30 list plus full categorized results.

from dataclasses import dataclass
from datetime import datetime

from keycrack.generator import (
    MIN_LENGTH,
    CategorizedPasswords,
    PersonalInfo,
    leet_speak,
)

# Grammar model: a Template is a sequence of Slots, each Slot holds possible
# SlotValues with probabilities. Expanding a Template produces every combination
# of slot values with their joint probability.

@dataclass(frozen=True)
class SlotValue:
    value: str
    prob: float


@dataclass(frozen=True)
class Slot:
    name: str
    values: list[SlotValue]
    apply_case: bool = False


@dataclass(frozen=True)
class Template:
    name: str
    slots: list[Slot]
    base_prob: float
    category: str


# Split a name into three casing variants weighted by real-world frequency:
# lowercase (50%), capitalized (40%), and uppercase (10%).
def case_expand(value: str) -> list[tuple[str, float]]:
    results = [(value.lower(), 0.50), (value.capitalize(), 0.40)]
    if value.lower() != value.upper():
        results.append((value.upper(), 0.10))
    return results


# -- Slot factory functions --


# When no pet name is provided, its probability share is redistributed
# to first and last name so slot probabilities still sum to 1.0.
def make_name_slot(info: PersonalInfo) -> Slot:
    values = [
        SlotValue(info.first_name, 0.50),
        SlotValue(info.last_name, 0.20),
    ]
    if info.pet_name:
        values.append(SlotValue(info.pet_name, 0.30))
    else:
        # Redistribute pet probability to first/last
        values = [
            SlotValue(info.first_name, 0.70),
            SlotValue(info.last_name, 0.30),
        ]
    return Slot(name="name", values=values, apply_case=True)


def make_compound_slot(info: PersonalInfo) -> Slot:
    first = info.first_name
    last = info.last_name
    pet = info.pet_name

    values = [
        SlotValue(first + last, 0.30),
        SlotValue(first[0] + last, 0.25),
        SlotValue(first + last[0], 0.15),
    ]
    if pet:
        values.append(SlotValue(first + pet, 0.20))
        values.append(SlotValue(pet + first, 0.10))
    else:
        # Redistribute: bump existing probs
        values = [
            SlotValue(first + last, 0.45),
            SlotValue(first[0] + last, 0.35),
            SlotValue(first + last[0], 0.20),
        ]
    return Slot(name="compound", values=values, apply_case=True)


def make_initials_slot(info: PersonalInfo) -> Slot:
    initials = info.first_name[0] + info.last_name[0]
    return Slot(
        name="initials",
        values=[SlotValue(initials, 1.0)],
        apply_case=True,
    )


def make_leet_name_slot(info: PersonalInfo) -> Slot:
    values = [
        SlotValue(leet_speak(info.first_name), 0.50),
        SlotValue(leet_speak(info.last_name), 0.20),
    ]
    if info.pet_name:
        values.append(SlotValue(leet_speak(info.pet_name), 0.30))
    else:
        values = [
            SlotValue(leet_speak(info.first_name), 0.70),
            SlotValue(leet_speak(info.last_name), 0.30),
        ]
    return Slot(name="leet_name", values=values, apply_case=True)


def make_birth_year_4_slot(info: PersonalInfo) -> Slot:
    yyyy = info.dob[4:8]
    return Slot(name="birth_year_4", values=[SlotValue(yyyy, 1.0)])


def make_birth_year_2_slot(info: PersonalInfo) -> Slot:
    yy = info.dob[6:8]
    return Slot(name="birth_year_2", values=[SlotValue(yy, 1.0)])


def make_mmdd_slot(info: PersonalInfo) -> Slot:
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    return Slot(
        name="mmdd",
        values=[
            SlotValue(mm + dd, 0.70),
            SlotValue(dd + mm, 0.30),
        ],
    )


def make_mmddyy_slot(info: PersonalInfo) -> Slot:
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    yy = info.dob[6:8]
    return Slot(
        name="mmddyy",
        values=[
            SlotValue(mm + dd + yy, 0.50),
            SlotValue(dd + mm + yy, 0.30),
            SlotValue(mm + yy, 0.20),
        ],
    )


def make_mmddyyyy_slot(info: PersonalInfo) -> Slot:
    mm = info.dob[0:2]
    dd = info.dob[2:4]
    yyyy = info.dob[4:8]
    return Slot(
        name="mmddyyyy",
        values=[
            SlotValue(mm + dd + yyyy, 0.50),
            SlotValue(dd + mm + yyyy, 0.30),
            SlotValue(mm + yyyy, 0.20),
        ],
    )


def make_current_year_slot() -> Slot:
    now = datetime.now()
    return Slot(
        name="current_year",
        values=[
            SlotValue(str(now.year), 0.70),
            SlotValue(str(now.year + 1), 0.30),
        ],
    )


def make_separator_slot() -> Slot:
    return Slot(
        name="separator",
        values=[
            SlotValue("_", 0.45),
            SlotValue(".", 0.35),
            SlotValue("-", 0.20),
        ],
    )


# -- Static slots --

SEQ_123 = Slot(name="seq_123", values=[SlotValue("123", 1.0)])
SEQ_1234 = Slot(name="seq_1234", values=[SlotValue("1234", 1.0)])
SEQ_12345 = Slot(name="seq_12345", values=[SlotValue("12345", 1.0)])

SEQ_DIGITS = Slot(
    name="seq_digits",
    values=[
        SlotValue("123", 0.55),
        SlotValue("1234", 0.30),
        SlotValue("12345", 0.15),
    ],
)

BANG_SLOT = Slot(
    name="bang",
    values=[
        SlotValue("!", 0.65),
        SlotValue("!!", 0.35),
    ],
)

LITERAL_123_BANG = Slot(name="123_bang", values=[SlotValue("123!", 1.0)])
LITERAL_4EVER = Slot(name="4ever", values=[SlotValue("4ever", 1.0)])

SPECIAL_SUFFIX_SLOT = Slot(
    name="special_suffix",
    values=[
        SlotValue("69", 0.25),
        SlotValue("420", 0.25),
        SlotValue("007", 0.20),
        SlotValue("99", 0.15),
        SlotValue("01", 0.15),
    ],
)

DIGIT_1_SLOT = Slot(name="digit_1", values=[SlotValue("1", 1.0)])

ILOVE_PREFIX = Slot(
    name="ilove_prefix",
    values=[SlotValue("ilove", 0.60), SlotValue("iLove", 0.40)],
)


# -- Grammar builder --


def build_grammar(info: PersonalInfo) -> list[Template]:
    name = make_name_slot(info)
    compound = make_compound_slot(info)
    initials = make_initials_slot(info)
    leet_name = make_leet_name_slot(info)
    birth_year_4 = make_birth_year_4_slot(info)
    birth_year_2 = make_birth_year_2_slot(info)
    mmdd = make_mmdd_slot(info)
    mmddyy = make_mmddyy_slot(info)
    mmddyyyy = make_mmddyyyy_slot(info)
    current_year = make_current_year_slot()
    separator = make_separator_slot()

    templates = [
        # Category: name_based
        Template("name_seq", [name, SEQ_DIGITS], 0.105, "name_based"),          # T01
        Template("name_digit1", [name, DIGIT_1_SLOT], 0.050, "name_based"),     # T02
        Template("name_bang", [name, BANG_SLOT], 0.037, "name_based"),           # T03
        Template("name_123bang", [name, LITERAL_123_BANG], 0.025, "name_based"), # T04
        Template("name_double", [name, name], 0.018, "name_based"),             # T05
        Template("compound", [compound], 0.025, "name_based"),                  # T06
        Template("name_4ever", [name, LITERAL_4EVER], 0.012, "name_based"),     # T07
        Template("ilove_name", [ILOVE_PREFIX, name], 0.031, "name_based"),      # T08
        Template("name_special", [name, SPECIAL_SUFFIX_SLOT], 0.018, "name_based"),  # T09
        Template("initials_year4", [initials, birth_year_4], 0.050, "name_based"),   # T10
        Template("initials_mmdd", [initials, mmdd], 0.031, "name_based"),            # T11
        Template("initials_mmddyyyy", [initials, mmddyyyy], 0.018, "name_based"),    # T12
        Template("initials_seq", [initials, SEQ_DIGITS], 0.025, "name_based"),       # T13

        # Category: name_dob
        Template("name_year4", [name, birth_year_4], 0.111, "name_dob"),        # T14
        Template("name_year2", [name, birth_year_2], 0.068, "name_dob"),        # T15
        Template("name_mmdd", [name, mmdd], 0.068, "name_dob"),                 # T16
        Template("name_mmddyy", [name, mmddyy], 0.037, "name_dob"),            # T17
        Template("name_mmddyyyy", [name, mmddyyyy], 0.025, "name_dob"),        # T18
        Template("name_curyear", [name, current_year], 0.031, "name_dob"),      # T19
        Template("name_sep_year4", [name, separator, birth_year_4], 0.018, "name_dob"),  # T20
        Template("name_sep_mmdd", [name, separator, mmdd], 0.012, "name_dob"),           # T21

        # Category: dob_name
        Template("mmdd_name", [mmdd, name], 0.037, "dob_name"),                 # T22
        Template("year4_name", [birth_year_4, name], 0.018, "dob_name"),        # T23
        Template("mmddyy_name", [mmddyy, name], 0.012, "dob_name"),            # T24

        # Category: dob_only
        Template("dob_mmddyyyy", [mmddyyyy], 0.019, "dob_only"),               # T25
        Template("dob_mmddyy", [mmddyy], 0.013, "dob_only"),                   # T26
        Template("dob_mmdd_seq", [mmdd, SEQ_DIGITS], 0.013, "dob_only"),        # T27

        # Category: leet_speak
        Template("leet_seq", [leet_name, SEQ_DIGITS], 0.037, "leet_speak"),     # T28
        Template("leet_year4", [leet_name, birth_year_4], 0.025, "leet_speak"), # T29
        Template("leet_bang", [leet_name, BANG_SLOT], 0.012, "leet_speak"),      # T30
    ]

    total_prob = sum(t.base_prob for t in templates)
    assert abs(total_prob - 1.0) < 0.05, (
        f"Template probabilities sum to {total_prob}, expected ~1.0"
    )

    return templates


# -- Template expansion --


# Cartesian product of all slots in a template. Each combination's probability
# is the product of the template's base_prob, each slot value's prob, and
# (if apply_case) the casing variant's prob.
def expand_template(template: Template) -> list[tuple[str, float]]:
    expansions = [("", template.base_prob)]
    for slot in template.slots:
        new_expansions = []
        for prefix, prefix_prob in expansions:
            for sv in slot.values:
                if slot.apply_case:
                    for cased, case_prob in case_expand(sv.value):
                        new_expansions.append(
                            (prefix + cased, prefix_prob * sv.prob * case_prob)
                        )
                else:
                    new_expansions.append(
                        (prefix + sv.value, prefix_prob * sv.prob)
                    )
        expansions = new_expansions
    return expansions


# -- Diverse top-N selection --


# Pick the top N passwords by probability, but cap each template at
# max_per_template entries so the list shows variety across patterns.
def _select_diverse_top(
    scored: list[tuple[str, float, str]],
    n: int = 30,
    max_per_template: int = 2,
) -> list[tuple[str, float]]:
    seen_lower: set[str] = set()
    template_counts: dict[str, int] = {}
    result: list[tuple[str, float]] = []

    for pw, prob, tname in scored:
        key = pw.lower()
        if key in seen_lower:
            continue
        if template_counts.get(tname, 0) >= max_per_template:
            continue
        seen_lower.add(key)
        template_counts[tname] = template_counts.get(tname, 0) + 1
        result.append((pw, prob))
        if len(result) == n:
            break

    return result


# -- Main generation function --


def generate_passwords_pcfg(info: PersonalInfo) -> CategorizedPasswords:
    templates = build_grammar(info)

    all_passwords: list[tuple[str, float, str, str]] = []
    for template in templates:
        for pw, prob in expand_template(template):
            if len(pw) >= MIN_LENGTH:
                all_passwords.append((pw, prob, template.category, template.name))

    # Deduplicate: keep highest probability per password
    best: dict[str, tuple[float, str, str]] = {}
    for pw, prob, cat, tname in all_passwords:
        if pw not in best or prob > best[pw][0]:
            best[pw] = (prob, cat, tname)

    # Build category sets
    categories: dict[str, set[str]] = {
        k: set() for k in ["name_based", "leet_speak", "name_dob", "dob_name", "dob_only"]
    }
    scored: list[tuple[str, float, str]] = []
    for pw, (prob, cat, tname) in best.items():
        categories[cat].add(pw)
        scored.append((pw, prob, tname))

    scored.sort(key=lambda x: (-x[1], x[0]))

    # Diverse top 30: max 2 per template name
    top_30 = _select_diverse_top(scored, n=30, max_per_template=2)

    return CategorizedPasswords(
        name_based=categories["name_based"],
        leet_speak=categories["leet_speak"],
        name_dob=categories["name_dob"],
        dob_name=categories["dob_name"],
        dob_only=categories["dob_only"],
        top_passwords=top_30,
    )
