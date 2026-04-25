"""
generate_import_sql.py
======================
Reads 2025.csv / 2026.csv and writes a human-reviewable SQL file instead of
touching the database directly.

The output is structured so you can:
  - Read it top to bottom — one clearly labelled block per invoice
  - Comment out or delete any block you don't want
  - Run the whole file (or just selected blocks) against your DB

Usage
-----
    python generate_import_sql.py                          # both years -> import_invoices.sql
    python generate_import_sql.py --year 2025              # only 2025
    python generate_import_sql.py --csv-dir /path/to/csvs  # custom CSV location
    python generate_import_sql.py --out custom_name.sql    # custom output file

Assumptions
-----------
  - Patient rows already exist in the DB. The script uses a subquery
        (SELECT patient_id FROM patient WHERE label = '....')
    so no hard-coded patient IDs are needed.
  - invoice_date.date_id and invoice.invoice_id are SERIAL / AUTOINCREMENT.
    The script uses a CTE-based INSERT … RETURNING pattern (PostgreSQL) so
    child rows can reference the generated parent ID without knowing it upfront.
    → See the note at the bottom if you use SQLite instead.
  - All imported invoices get status PAYMENT_DUE and the current timestamp
    for created_at / updated_at.

Output structure (per invoice)
-------------------------------
    -- ══════════════════════════════════════════════
    -- Invoice HEGE020125H  [HP]  patient: HEGE  date: 2025-01-02
    -- ══════════════════════════════════════════════
    WITH new_invoice AS (
        INSERT INTO invoice (...) VALUES (...) RETURNING invoice_id
    ),
    new_date_1 AS (
        INSERT INTO invoice_date (...) ... RETURNING date_id
    ),
    ...
    INSERT INTO invoice_item (...) VALUES ...;
    -- [items for date 1]
    -- [items for date 2]
    -- etc.
"""

from __future__ import annotations

import ast
import argparse
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional


# ── helpers ──────────────────────────────────────────────────────────────────

def parse_date(s: str) -> Optional[date]:
    parts = s.strip().split(".")
    if len(parts) != 3:
        return None
    d, m, y = parts
    if len(y) == 2:
        y = "20" + y
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def parse_amount(s: str) -> float:
    return float(s.strip().replace(",", "."))


def invoice_date_from_number(inv_num: str) -> Optional[date]:
    m = re.search(r"(\d{2})(\d{2})(\d{2})H?$", inv_num)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        return date(2000 + int(year), int(month), int(day))
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
    # String: escape single quotes by doubling them
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


# ── CSV parsers (identical to import_invoices.py) ────────────────────────────

def _split_list_from_tail(text: str):
    depth = 0
    for i, c in enumerate(text):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return text[: i + 1], text[i + 1:]
    return text, ""


def parse_hp_row(line: str) -> dict:
    line = line.strip()
    idx = line.index(";[[")
    semicol_part = line[:idx]
    list_str_full = line[idx + 1:]

    cols = semicol_part.split(";")
    label       = cols[0].strip()
    invoice_num = cols[1].strip()
    km_count    = int(cols[2].strip())

    list_str, remainder = _split_list_from_tail(list_str_full)
    diagnosis = remainder.lstrip(";").strip() or None

    raw_sessions = ast.literal_eval(list_str)

    dates = []
    for session in raw_sessions:
        date_str, numbers_str, descriptions_str, amounts_str = session
        numbers      = numbers_str.split("\n")
        descriptions = descriptions_str.split("\n")
        amounts      = [parse_amount(a) for a in amounts_str.split("\n")]
        items = [
            {"number": num, "description": desc, "amount": amt, "quantity": 1}
            for num, desc, amt in zip(numbers, descriptions, amounts)
        ]
        dates.append({"date": parse_date(date_str), "items": items})

    return {
        "label": label,
        "invoice_number": invoice_num,
        "type": "HP",
        "kilometers_at_billing": km_count,
        "diagnosis": diagnosis,
        "invoice_date": invoice_date_from_number(invoice_num),
        "dates": dates,
    }


def parse_kg_row(line: str) -> dict:
    line = line.strip()
    idx = line.index(";['")
    semicol_part = line[:idx]
    rest = line[idx + 1:]

    cols = semicol_part.split(";")
    label       = cols[0].strip()
    invoice_num = cols[1].strip()
    km_count    = int(cols[2].strip())
    date_strings = [c.strip() for c in cols[8:] if c.strip()]
    dates_parsed = [parse_date(d) for d in date_strings if parse_date(d)]

    desc_str, remainder = _split_list_from_tail(rest)
    amt_list_str, _ = _split_list_from_tail(remainder.lstrip(";"))

    descriptions = ast.literal_eval(desc_str)
    amounts      = ast.literal_eval(amt_list_str)

    items = [
        {"number": None, "description": desc, "amount": float(amt), "quantity": len(dates_parsed)}
        for desc, amt in zip(descriptions, amounts)
    ]

    inv_type = "KG"

    return {
        "label": label,
        "invoice_number": invoice_num,
        "type": inv_type,
        "kilometers_at_billing": km_count,
        "diagnosis": None,
        "invoice_date": invoice_date_from_number(invoice_num),
        "dates": dates_parsed,
        "shared_items": items,
    }


def parse_row(line: str) -> Optional[dict]:
    line = line.strip()
    if not line or ";" not in line:
        return None
    try:
        if "[['" in line:
            return parse_hp_row(line)
        elif "['" in line:
            return parse_kg_row(line)
    except Exception as e:
        print(f"  ⚠  Skipped (parse error): {line[:80]}…\n     {e}", file=sys.stderr)
    return None


def load_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = parse_row(line)
            if r:
                rows.append(r)
    return rows


# ── SQL generation ────────────────────────────────────────────────────────────

def invoice_block(row: dict, now_ts: str) -> str:
    """
    Render one complete, self-contained SQL block for a single invoice.
    Uses plain INSERTs with subqueries — SQLite compatible (no RETURNING).
    """
    inv_num  = row["invoice_number"]
    label    = row["label"]
    inv_type = row["type"]
    inv_date = row["invoice_date"]
    km       = row.get("kilometers_at_billing")
    diag     = row.get("diagnosis")

    # Subquery helpers that reference the already-inserted invoice row
    inv_id = f"(SELECT invoice_id FROM invoice WHERE invoice_number = {sql_str(inv_num)})"

    def date_id_subq(d):
        return (f"(SELECT date_id FROM invoice_date "
                f"WHERE invoice_id = {inv_id} AND date = {sql_str(d)})")

    lines = []

    # ── section header ────────────────────────────────────────────────────
    lines.append(f"-- {'═' * 62}")
    lines.append(f"-- Invoice {inv_num:<20} [{inv_type}]  patient: {label}  date: {inv_date}")
    lines.append(f"-- {'═' * 62}")

    # ── INSERT invoice ────────────────────────────────────────────────────
    lines.append("INSERT INTO invoice (")
    lines.append("    patient_id, invoice_number, invoice_date,")
    lines.append("    kilometers_at_billing, type, status, diagnosis,")
    lines.append("    created_at, updated_at")
    lines.append(")")
    lines.append("VALUES (")
    lines.append(f"    (SELECT patient_id FROM patient WHERE label = {sql_str(label)}),")
    lines.append(f"    {sql_str(inv_num)},")
    lines.append(f"    {sql_str(inv_date)},")
    lines.append(f"    {sql_str(km)},")
    lines.append(f"    {sql_str(inv_type)},")
    lines.append(f"    'PAYMENT_DUE',")
    lines.append(f"    {sql_str(diag)},")
    lines.append(f"    '{now_ts}', '{now_ts}'")
    lines.append(");")

    # ── HP: one date INSERT + one items INSERT per treatment date ─────────
    if inv_type == "HP":
        for d_idx, date_block in enumerate(row["dates"], start=1):
            d = date_block["date"]
            lines.append(f"")
            lines.append(f"-- Treatment date {d_idx}: {d}")
            lines.append("INSERT INTO invoice_date (invoice_id, date)")
            lines.append(f"VALUES ({inv_id}, {sql_str(d)});")

            if date_block["items"]:
                lines.append("INSERT INTO invoice_item")
                lines.append("    (invoice_id, date_id, number, description, amount, quantity, position)")
                item_rows = [
                    f"SELECT {inv_id}, {date_id_subq(d)}, "
                    f"{sql_str(item['number'] or None)}, "
                    f"{sql_str(item['description'])}, "
                    f"{sql_str(item['amount'])}, "
                    f"{sql_str(item['quantity'])}, "
                    f"{sql_str(pos)}"
                    for pos, item in enumerate(date_block["items"])
                ]
                lines.append(("\nUNION ALL\n").join(item_rows) + ";")

    # ── KG / GT: all dates in one INSERT, then shared items ───────────────
    else:
        dates = row["dates"]
        shared_items = row.get("shared_items", [])

        if dates:
            lines.append("")
            lines.append("INSERT INTO invoice_date (invoice_id, date) VALUES")
            date_rows = [f"    ({inv_id}, {sql_str(d)})" for d in dates]
            lines.append(",\n".join(date_rows) + ";")

        if shared_items:
            lines.append("INSERT INTO invoice_item")
            lines.append("    (invoice_id, date_id, number, description, amount, quantity, position)")
            item_rows = [
                f"SELECT {inv_id}, NULL, "
                f"NULL, "
                f"{sql_str(item['description'])}, "
                f"{sql_str(item['amount'])}, "
                f"{sql_str(item['quantity'])}, "
                f"{sql_str(pos)}"
                for pos, item in enumerate(shared_items)
            ]
            lines.append(("\nUNION ALL\n").join(item_rows) + ";")
        else:
            lines.append(f"SELECT {inv_id}; -- no items")

        lines.append("")
        lines.append("-- Default item link (KG)")
        lines.append("INSERT INTO invoice_default_item_association (invoice_id, default_item_id)")
        lines.append(f"VALUES ({inv_id}, 1000);")

    lines.append("")   # blank line between blocks
    return "\n".join(lines)


def generate_sql(rows: list[dict], out_path: Path):
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")

    with open(out_path, "w", encoding="utf-8") as f:

        # ── file header ───────────────────────────────────────────────────
        f.write(f"""\
-- ============================================================
-- Invoice import  —  generated {now_ts}
-- SQLite compatible
-- ============================================================
-- HOW TO USE
-- ----------
-- 1. Review each block below. Every block is a self-contained
--    unit for ONE invoice.
-- 2. To skip an invoice: comment out its entire block with /* … */
--    or simply delete the block.
-- 3. When satisfied, run the whole file:
--        sqlite3 <db_file> < {out_path.name}
--    Or paste individual blocks into your SQL client.
--
-- SAFETY NET: wrap everything in a transaction so you can
-- roll back if something looks wrong after running:
--
--    BEGIN;
--    .read {out_path.name}
--    -- inspect with SELECT * FROM invoice ORDER BY invoice_id DESC LIMIT 20;
--    COMMIT;   -- or ROLLBACK;
--
-- ============================================================

BEGIN;

""")

        ok = skipped = 0
        for row in rows:
            try:
                block = invoice_block(row, now_ts)
                f.write(block + "\n")
                ok += 1
            except Exception as e:
                inv = row.get("invoice_number", "?")
                f.write(f"-- ⚠  SKIPPED {inv}: {e}\n\n")
                skipped += 1
                print(f"  ⚠  Error generating SQL for {inv}: {e}", file=sys.stderr)

        f.write("COMMIT;\n")

    return ok, skipped


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate a reviewable SQL import file from invoice CSVs."
    )
    parser.add_argument("--year", choices=["2025", "2026"],
                        help="Only process one year (default: both)")
    parser.add_argument("--csv-dir", default=".",
                        help="Directory containing 2025.csv and 2026.csv")
    parser.add_argument("--out", default="import_invoices.sql",
                        help="Output SQL file name (default: import_invoices.sql)")
    args = parser.parse_args()

    csv_dir  = Path(args.csv_dir)
    out_path = Path(args.out)
    years    = [args.year] if args.year else ["2025", "2026"]

    all_rows = []
    for y in years:
        p = csv_dir / f"{y}.csv"
        if not p.exists():
            print(f"  ⚠  {p} not found — skipping")
            continue
        rows = load_csv(p)
        print(f"  Loaded {len(rows)} rows from {p.name}")
        all_rows.extend(rows)

    if not all_rows:
        print("Nothing to generate.")
        return

    ok, skipped = generate_sql(all_rows, out_path)

    print(f"\nWrote {out_path}  ({ok} invoices, {skipped} skipped)")
    print(f"\nNext steps:")
    print(f"  1. Open {out_path} and review each block")
    print(f"  2. Comment out / delete any block you don't want")
    print(f"  3. sqlite3 <db_file> < {out_path}")


if __name__ == "__main__":
    main()