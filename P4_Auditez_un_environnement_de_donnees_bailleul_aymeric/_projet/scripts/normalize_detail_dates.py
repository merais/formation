import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

# Input file path
INPUT_PATH = Path(r"g:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\sources\_data_logs_before_clean.csv")
BACKUP_PATH = INPUT_PATH.with_suffix('.bak.csv')
TMP_PATH = INPUT_PATH.with_suffix('.tmp.csv')

# Patterns for date detection
RE_DDMMYYYY = re.compile(r"^(\d{1,2})[\-/\.](\d{1,2})[\-/\.]((?:19|20)\d{2})$")
RE_YYYYMMDD = re.compile(r"^((?:19|20)\d{2})-(\d{2})-(\d{2})$")
RE_SERIAL_INT = re.compile(r"^\d{4,6}$")  # Excel-like serial dates e.g. 45518
RE_DD_MM_YYYY_SLASH = re.compile(r"^(\d{1,2})/(\d{1,2})/((?:19|20)\d{2})$")

# Excel serial base (Excel for Windows, 1900 system, ignoring the 1900 leap-year bug for simplicity)
EXCEL_BASE = datetime(1899, 12, 30)  # So that 1 -> 1899-12-31, 2 -> 1900-01-01; 45518 -> 2024-08-14


def normalize_detail(value: str) -> str:
    if value is None:
        return value
    v = value.strip()
    if not v:
        return v

    # Replace French decimal commas mistakenly in EAN or numbers; skip if contains letters or '_' (likely not a date)
    # Only proceed with date normalization if the field name indicates a date or matches date patterns.
    # We will rely on caller to pass only rows where champs == 'Date' or the value matches a date pattern.

    # Direct ISO
    m = RE_YYYYMMDD.match(v)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # dd/mm/yyyy or dd-mm-yyyy or dd.mm.yyyy
    m = RE_DDMMYYYY.match(v)
    if m:
        d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mth, d).strftime('%Y-%m-%d')
        except ValueError:
            return v

    # explicit dd/mm/yyyy
    m = RE_DD_MM_YYYY_SLASH.match(v)
    if m:
        d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mth, d).strftime('%Y-%m-%d')
        except ValueError:
            return v

    # Excel serial integer (e.g., 45518)
    if RE_SERIAL_INT.match(v):
        try:
            days = int(v)
            normalized = (EXCEL_BASE + timedelta(days=days)).strftime('%Y-%m-%d')
            return normalized
        except Exception:
            return v

    return v


def main():
    # Backup original
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(INPUT_PATH.read_bytes())

    with INPUT_PATH.open('r', encoding='utf-8', newline='') as src, TMP_PATH.open('w', encoding='utf-8', newline='') as dst:
        reader = csv.reader(src, delimiter=';')
        writer = csv.writer(dst, delimiter=';')

        header = next(reader)
        writer.writerow(header)
        # Column indices based on header
        try:
            idx_champs = header.index('champs')
            idx_detail = header.index('detail')
        except ValueError:
            raise SystemExit("Header must contain 'champs' and 'detail' columns")

        for row in reader:
            if len(row) <= max(idx_champs, idx_detail):
                writer.writerow(row)
                continue

            champs_val = row[idx_champs].strip().lower()
            detail_val = row[idx_detail]

            if champs_val == 'date':
                row[idx_detail] = normalize_detail(detail_val)

            writer.writerow(row)

    # Replace original with tmp
    TMP_PATH.replace(INPUT_PATH)


if __name__ == '__main__':
    main()
