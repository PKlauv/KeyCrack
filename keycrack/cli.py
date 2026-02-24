import argparse
import re
import time

from keycrack.generator import PersonalInfo, generate_passwords


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="KeyCrack - Password awareness tool"
    )
    parser.add_argument("--first", help="First name")
    parser.add_argument("--last", help="Last name")
    parser.add_argument("--dob", help="Date of birth (MMDDYYYY)")
    parser.add_argument("--pet", help="Pet name (optional)", default="")
    return parser.parse_args()


def prompt_interactive() -> dict:
    print("KeyCrack - Password Awareness Tool")
    print("=" * 40)
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    dob = input("Date of birth (MMDDYYYY): ").strip()
    pet = input("Pet name (optional, press Enter to skip): ").strip()
    return {"first": first, "last": last, "dob": dob, "pet": pet}


def display_results(passwords: set[str], elapsed: float) -> None:
    sorted_passwords = sorted(passwords)
    print(f"\nGenerated {len(sorted_passwords):,} unique passwords "
          f"in {elapsed:.4f} seconds.\n")
    sample_size = min(50, len(sorted_passwords))
    print(f"Sample (first {sample_size}):")
    print("-" * 40)
    for pw in sorted_passwords[:sample_size]:
        print(pw)
    print("-" * 40)
    print(f"... and {len(sorted_passwords) - sample_size:,} more.")


def main() -> None:
    args = parse_args()

    if args.first and args.last and args.dob:
        first = args.first
        last = args.last
        dob = args.dob
        pet = args.pet or ""
    else:
        data = prompt_interactive()
        first = data["first"]
        last = data["last"]
        dob = data["dob"]
        pet = data["pet"]

    dob = validate_dob(dob)

    clean_first = strip_to_alpha(first)
    clean_last = strip_to_alpha(last)
    clean_pet = strip_to_alpha(pet) if pet else ""

    info = PersonalInfo(
        first_name=clean_first,
        last_name=clean_last,
        dob=dob,
        pet_name=clean_pet if clean_pet else None,
    )

    start = time.perf_counter()
    passwords = generate_passwords(info)
    elapsed = time.perf_counter() - start

    # Add original (non-stripped) names as extra variants if they differ
    originals = {first, last}
    if pet:
        originals.add(pet)
    originals.discard(clean_first)
    originals.discard(clean_last)
    originals.discard(clean_pet)
    originals.discard("")
    for orig in originals:
        passwords.add(orig)

    display_results(passwords, elapsed)
