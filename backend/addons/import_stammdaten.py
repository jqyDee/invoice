"""
import_stammdaten.py
====================
Reads all *.TXT files from the stammdaten/ directory and writes a human-reviewable,
idempotent SQL file to import real patients into the DB.

Each INSERT is guarded with WHERE NOT EXISTS so the file is safe to re-run.

Usage
-----
    python import_stammdaten.py                              # ./stammdaten -> import_patients.sql
    python import_stammdaten.py --stammdaten-dir /path/dir  # custom directory
    python import_stammdaten.py --out custom.sql            # custom output file

File format (one field per line)
---------------------------------
    Line  1  label               4-letter code
    Line  2  gender              Frau → FEMALE, Mann → MALE
    Line  3  last_name
    Line  4  first_name
    Line  5  street
    Line  6  street_number
    Line  7  postal_code
    Line  8  city
    Line  9  birthday            DD.MM.YY or DD.MM.YYYY
    Line 10  kilometers_to_travel
    Line 11  dr                  dropped
    Line 12  email               optional, may be empty
    Line 13  type                dropped (HP or KG)
    Line 14  phone               optional, may be absent
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional


# ── helpers ───────────────────────────────────────────────────────────────────

def parse_date(s: str) -> Optional[date]:
    parts = s.strip().split(".")
    if len(parts) != 3:
        return None
    d, m, y = parts
    if len(y) == 2:
        y = "19" + y  # all known patients born pre-2000
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def sql_str(value) -> str:
    """Escape a Python value to a safe SQL string literal or NULL."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


# ── TXT parser ────────────────────────────────────────────────────────────────

def parse_txt_file(path: Path) -> Optional[dict]:
    """Parse a single stammdaten .TXT file into a patient dict."""
    try:
        lines = path.read_text(encoding="iso-8859-1").splitlines()
    except Exception as e:
        print(f"  ⚠  Could not read {path.name}: {e}", file=sys.stderr)
        return None

    # Pad to at least 14 lines so index access is safe
    while len(lines) < 14:
        lines.append("")

    label         = lines[0].strip()
    gender_raw    = lines[1].strip()
    last_name     = lines[2].strip()
    first_name    = lines[3].strip()
    street        = lines[4].strip()
    street_number = lines[5].strip()
    postal_code   = lines[6].strip()
    city          = lines[7].strip()
    birthday_raw  = lines[8].strip()
    km_raw        = lines[9].strip()
    # line 10 (index 10): dr — dropped
    email_raw     = lines[11].strip() if len(lines) > 11 else ""
    # line 12 (index 12): type — dropped
    phone_raw     = lines[13].strip() if len(lines) > 13 else ""

    # Gender
    if gender_raw == "Frau":
        gender = "FEMALE"
    elif gender_raw == "Mann":
        gender = "MALE"
    else:
        print(f"  ⚠  {path.name}: unknown gender '{gender_raw}', defaulting to MALE", file=sys.stderr)
        gender = "MALE"

    # Birthday
    birthday = parse_date(birthday_raw)
    if birthday is None:
        print(f"  ⚠  {path.name}: could not parse birthday '{birthday_raw}'", file=sys.stderr)

    # Kilometers
    try:
        km = float(km_raw)
    except ValueError:
        print(f"  ⚠  {path.name}: could not parse km '{km_raw}', defaulting to 0.0", file=sys.stderr)
        km = 0.0

    return {
        "label":               label,
        "gender":              gender,
        "last_name":           last_name,
        "first_name":          first_name,
        "street":              street,
        "street_number":       street_number,
        "postal_code":         postal_code,
        "city":                city,
        "birthday":            birthday,
        "kilometers_to_travel": km,
        "email":               email_raw or None,
        "telephone":           phone_raw or None,
    }


def load_stammdaten(directory: Path) -> list[dict]:
    patients = []
    txt_files = sorted(directory.glob("*.TXT"))
    if not txt_files:
        print(f"  ⚠  No .TXT files found in {directory}", file=sys.stderr)
        return patients

    for path in txt_files:
        label = path.stem  # filename without extension
        if label == "TEST":
            print(f"  Skipping {path.name} (TEST label)")
            continue
        patient = parse_txt_file(path)
        if patient:
            patients.append(patient)

    return patients


# ── SQL generation ────────────────────────────────────────────────────────────

def patient_block(p: dict, now_ts: str) -> str:
    label = p["label"]
    lines = []

    lines.append(f"-- {'═' * 48}")
    lines.append(f"-- Patient {label:<6}  {p['last_name']}, {p['first_name']}")
    lines.append(f"-- {'═' * 48}")
    lines.append("INSERT INTO patient (label, first_name, last_name, birthday, gender,")
    lines.append("    street, street_number, postal_code, city, kilometers_to_travel,")
    lines.append("    email, telephone, created_at)")
    lines.append(f"SELECT {sql_str(label)}, {sql_str(p['first_name'])}, {sql_str(p['last_name'])}, "
                 f"{sql_str(p['birthday'])}, {sql_str(p['gender'])},")
    lines.append(f"    {sql_str(p['street'])}, {sql_str(p['street_number'])}, "
                 f"{sql_str(p['postal_code'])}, {sql_str(p['city'])}, {sql_str(p['kilometers_to_travel'])},")
    lines.append(f"    {sql_str(p['email'])}, {sql_str(p['telephone'])}, '{now_ts}'")
    lines.append(f"WHERE NOT EXISTS (SELECT 1 FROM patient WHERE label = {sql_str(label)});")
    lines.append("")

    return "\n".join(lines)


def generate_sql(patients: list[dict], out_path: Path):
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with open(out_path, "w", encoding="utf-8") as f:

        f.write(f"""\
-- ============================================================
-- Patient import  —  generated {now_ts}
-- SQLite compatible — idempotent (safe to re-run)
-- ============================================================
-- HOW TO USE
-- ----------
-- 1. Review each block below. Every block is one patient.
-- 2. To skip a patient: comment out its block with /* … */
--    or delete the block.
-- 3. Run:  sqlite3 <db_file> < {out_path.name}
--
-- SAFETY NET: wrap in a transaction for easy rollback:
--
--    BEGIN;
--    .read {out_path.name}
--    -- SELECT * FROM patient ORDER BY patient_id DESC LIMIT 10;
--    COMMIT;   -- or ROLLBACK;
--
-- ============================================================

BEGIN;

""")

        ok = skipped = 0
        for p in patients:
            try:
                block = patient_block(p, now_ts)
                f.write(block + "\n")
                ok += 1
            except Exception as e:
                label = p.get("label", "?")
                f.write(f"-- ⚠  SKIPPED {label}: {e}\n\n")
                skipped += 1
                print(f"  ⚠  Error generating SQL for {label}: {e}", file=sys.stderr)

        f.write("COMMIT;\n")

    return ok, skipped


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate a reviewable, idempotent SQL import file from stammdaten .TXT files."
    )
    parser.add_argument("--stammdaten-dir", default="./stammdaten",
                        help="Directory containing .TXT files (default: ./stammdaten)")
    parser.add_argument("--out", default="import_patients.sql",
                        help="Output SQL file name (default: import_patients.sql)")
    args = parser.parse_args()

    stammdaten_dir = Path(args.stammdaten_dir)
    out_path       = Path(args.out)

    if not stammdaten_dir.is_dir():
        print(f"Error: directory not found: {stammdaten_dir}", file=sys.stderr)
        sys.exit(1)

    patients = load_stammdaten(stammdaten_dir)

    if not patients:
        print("Nothing to generate.")
        return

    print(f"  Loaded {len(patients)} patients from {stammdaten_dir}")
    ok, skipped = generate_sql(patients, out_path)

    print(f"\nWrote {out_path}  ({ok} patients, {skipped} skipped)")
    print(f"\nNext steps:")
    print(f"  1. Review {out_path}")
    print(f"  2. sqlite3 ../data/db.db < {out_path}")
    print(f"  3. sqlite3 ../data/db.db < import_invoices.sql")


if __name__ == "__main__":
    main()
