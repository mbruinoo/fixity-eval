

Great question. Here's how I'd approach it — the key idea is to preserve a **per-row cryptographic link** between the original and standardized data so you can later verify that every standardized row traces back to an unmodified source row, and that no rows were dropped or fabricated.

## Design

```
┌──────────────────────┐       standardize        ┌──────────────────────────────┐
│   SOURCE ROW         │  ──────────────────────►  │   STANDARDIZED ROW           │
│                      │                           │                              │
│  raw col values      │                           │  cleaned col values          │
│                      │                           │  + source_checksum (SHA-256) │
│                      │                           │  + row_index                 │
└──────────────────────┘                           └──────────────────────────────┘

                                                          │
                                              also writes │
                                                          ▼
                                                   ┌──────────────┐
                                                   │  MANIFEST     │
                                                   │  .json        │
                                                   │               │
                                                   │ file-level    │
                                                   │ checksums +   │
                                                   │ row count +   │
                                                   │ per-row       │
                                                   │ source hashes │
                                                   └──────────────┘
```

There are **three layers**:

| Layer | What it proves |
|---|---|
| **Row-level `source_checksum`** | This standardized row was produced from *that specific* raw row — detects cell-level tampering |
| **File-level source checksum** | The input file hasn't been modified since processing — detects any byte-level change |
| **File-level output checksum** | The output file hasn't been modified after writing — detects post-hoc edits to the "clean" file |

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer — with checksum auditing.

Produces:
  1. A standardized .tsv with two extra columns:
       • row_index     – 1-based row number in the source file (excluding header)
       • source_hash   – SHA-256 of the original row's tab-joined values
  2. A .manifest.json sidecar file containing:
       • source file path, size, and SHA-256
       • output file SHA-256
       • row count
       • per-row source hashes (for independent verification)
       • timestamp and script version

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv]
    python standardize_inventory.py --verify output.tsv          # verify mode
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

SCRIPT_VERSION = "2.0.0"


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CHECKSUM UTILITIES                                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def hash_string(s: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_row(values: list[str]) -> str:
    """
    Compute a deterministic SHA-256 for a row.

    The values are joined with a tab character before hashing.
    This matches the physical layout of the .tsv, making it possible
    to recompute the hash from the raw file without parsing.
    """
    canonical = "\t".join(v for v in values)
    return hash_string(canonical)


def hash_file(filepath: str) -> str:
    """Return the SHA-256 hex digest of an entire file (binary read)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(
    *,
    source_path: str,
    output_path: str,
    row_checksums: list[dict],
    source_file_hash: str,
    output_file_hash: str,
    row_count: int,
) -> dict:
    """Build the manifest dictionary."""
    return {
        "schema_version": "1.0",
        "script_version": SCRIPT_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(Path(source_path).resolve()),
            "size_bytes": os.path.getsize(source_path),
            "sha256": source_file_hash,
        },
        "output": {
            "path": str(Path(output_path).resolve()),
            "size_bytes": os.path.getsize(output_path),
            "sha256": output_file_hash,
        },
        "row_count": row_count,
        "rows": row_checksums,
    }


def write_manifest(manifest: dict, output_path: str) -> str:
    """Write the manifest JSON sidecar. Returns the manifest path."""
    manifest_path = output_path + ".manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest_path


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  VERIFICATION MODE                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def verify(output_path: str) -> bool:
    """
    Verify a standardized file against its manifest.

    Checks performed:
      1. Output file SHA-256 matches manifest.
      2. Source file SHA-256 matches manifest (if source still exists).
      3. Row count matches.
      4. Each row's embedded source_hash matches the manifest's record.
    """
    manifest_path = output_path + ".manifest.json"

    if not os.path.exists(manifest_path):
        print(f"✖  Manifest not found: {manifest_path}", file=sys.stderr)
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_ok = True

    # --- Check 1: output file integrity ---
    print("🔍 Checking output file integrity...")
    actual_output_hash = hash_file(output_path)
    expected_output_hash = manifest["output"]["sha256"]
    if actual_output_hash == expected_output_hash:
        print("   ✅ Output file SHA-256 matches.")
    else:
        print(f"   ✖  Output file SHA-256 MISMATCH.\n"
              f"      Expected: {expected_output_hash}\n"
              f"      Actual:   {actual_output_hash}", file=sys.stderr)
        all_ok = False

    # --- Check 2: source file integrity (if still available) ---
    source_path = manifest["source"]["path"]
    if os.path.exists(source_path):
        print("🔍 Checking source file integrity...")
        actual_source_hash = hash_file(source_path)
        expected_source_hash = manifest["source"]["sha256"]
        if actual_source_hash == expected_source_hash:
            print("   ✅ Source file SHA-256 matches.")
        else:
            print(f"   ✖  Source file SHA-256 MISMATCH.\n"
                  f"      Expected: {expected_source_hash}\n"
                  f"      Actual:   {actual_source_hash}", file=sys.stderr)
            all_ok = False
    else:
        print(f"   ⚠  Source file not found at {source_path}; skipping source check.")

    # --- Check 3 & 4: row count and per-row hashes ---
    print("🔍 Checking per-row source hashes...")
    manifest_rows = manifest["rows"]

    with open(output_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        output_rows = list(reader)

    if len(output_rows) != manifest["row_count"]:
        print(f"   ✖  Row count mismatch. Manifest says {manifest['row_count']}, "
              f"file has {len(output_rows)}.", file=sys.stderr)
        all_ok = False

    mismatches = 0
    for i, (out_row, manifest_row) in enumerate(
        zip(output_rows, manifest_rows), start=1
    ):
        embedded_hash = out_row.get("source_hash", "")
        manifest_hash = manifest_row.get("source_hash", "")

        if embedded_hash != manifest_hash:
            print(f"   ✖  Row {i}: embedded source_hash ≠ manifest source_hash.",
                  file=sys.stderr)
            mismatches += 1
            all_ok = False

    if mismatches == 0:
        print(f"   ✅ All {len(output_rows)} row hashes match.")
    else:
        print(f"   ✖  {mismatches} row(s) failed hash verification.", file=sys.stderr)

    # --- Summary ---
    print()
    if all_ok:
        print("🎉 Verification PASSED — data integrity confirmed.")
    else:
        print("🚨 Verification FAILED — data may have been modified.", file=sys.stderr)

    return all_ok


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  FIELD STANDARDIZERS  (same logic as before, included for completeness) ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

MONTH_MAP = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09",
    "september": "09", "oct": "10", "october": "10", "nov": "11",
    "november": "11", "dec": "12", "december": "12",
}

DATE_FORMATS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y",
    "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
    "%Y/%m/%d", "%Y", "%B %Y", "%b %Y",
]

TITLE_LOWERCASE = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
    "at", "by", "in", "of", "on", "to", "up", "as", "is", "if",
    "it", "no", "not", "per", "via", "vs", "vs.",
}

HEADER_ALIASES = {
    "date": "date", "dates": "date", "year": "date",
    "accession date": "date", "title": "title", "object title": "title",
    "artwork title": "title", "name": "title", "object number": "object_number",
    "objectnumber": "object_number", "object_number": "object_number",
    "accession number": "object_number", "accession no": "object_number",
    "accession no.": "object_number", "acc. no.": "object_number",
    "inventory number": "object_number", "id": "object_number",
    "link": "link", "url": "link", "uri": "link", "web link": "link",
    "permalink": "link",
}

CANONICAL_FIELDS = ["date", "title", "object_number", "link"]

OUTPUT_HEADER_LABELS = {
    "date": "Date", "title": "Title", "object_number": "Object Number",
    "link": "Link", "row_index": "Row Index", "source_hash": "Source Hash",
}


def _normalize_date_string(raw: str) -> str:
    text = raw.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("–", "-").replace("—", "-")
    return text


def _try_parse_exact(text: str) -> str | None:
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            if fmt == "%Y":
                return str(dt.year)
            if fmt in ("%B %Y", "%b %Y"):
                return dt.strftime("%Y-%m")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_written_month(text: str) -> str | None:
    m = re.match(
        r"(?P<month>[A-Za-z]+)\.?\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})", text
    )
    if not m:
        m = re.match(
            r"(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]+)\.?,?\s+(?P<year>\d{4})", text
        )
    if m:
        month_str = m.group("month").lower().rstrip(".")
        mm = MONTH_MAP.get(month_str)
        if mm:
            return f"{int(m.group('year')):04d}-{mm}-{int(m.group('day')):02d}"
    return None


def standardize_date(raw: str) -> str:
    if not raw or not raw.strip():
        return "Unknown"
    text = _normalize_date_string(raw)
    if text.lower() in ("unknown", "n/a", "n.a.", "none", "?", "undated", "nd", "n.d."):
        return "Unknown"
    m = re.match(r"(\d{1,2})(st|nd|rd|th)\s+century", text, re.IGNORECASE)
    if m:
        century = int(m.group(1))
        start = (century - 1) * 100
        return f"{start:04d}/{start + 99:04d} ({m.group(1)}{m.group(2)} century)"
    approx_prefix = ""
    approx_match = re.match(
        r"(ca\.?|c\.?|circa|~|approx\.?|approximately)\s*", text, re.IGNORECASE
    )
    if approx_match:
        approx_prefix = "ca. "
        text = text[approx_match.end():]
    range_match = re.match(r"(\d{4})\s*(?:-|to|–|—)\s*(\d{4})", text, re.IGNORECASE)
    if range_match:
        return f"{approx_prefix}{range_match.group(1)}/{range_match.group(2)}"
    result = _parse_written_month(text)
    if result:
        return f"{approx_prefix}{result}"
    result = _try_parse_exact(text)
    if result:
        return f"{approx_prefix}{result}"
    m = re.match(r"(\d{4})", text)
    if m:
        return f"{approx_prefix}{m.group(1)}"
    return raw.strip()


def _title_case_word(word: str, first: bool) -> str:
    if len(word) >= 2 and word.isupper():
        return word
    lower = word.lower()
    if first or lower not in TITLE_LOWERCASE:
        return word.capitalize()
    return lower


def standardize_title(raw: str) -> str:
    if not raw or not raw.strip():
        return "Untitled"
    text = re.sub(r"\s+", " ", raw.strip())
    if text.endswith(".") and not text.endswith("..."):
        text = text[:-1].strip()
    words = text.split()
    return " ".join(_title_case_word(w, i == 0) for i, w in enumerate(words))


def standardize_object_number(raw: str) -> str:
    if not raw or not raw.strip():
        return "Unknown"
    text = re.sub(r"\s+", " ", raw.strip().upper())
    if text.lower() in ("unknown", "n/a", "none", "?"):
        return "Unknown"
    prefix = ""
    number_part = text
    pm = re.match(r"^([A-Z]{1,10})[.\s\-]+(.+)$", text)
    if pm:
        prefix = pm.group(1) + " "
        number_part = pm.group(2)
    segments = re.split(r"[.\-/]", number_part)
    if all(s.isdigit() for s in segments if s):
        pad = max(max((len(s) for s in segments if s), default=3), 3)
        segments = [s.zfill(pad) for s in segments if s]
        return f"{prefix}{'.'.join(segments)}"
    return f"{prefix}{'.'.join(s for s in segments if s)}"


def standardize_link(raw: str) -> str:
    if not raw or not raw.strip():
        return ""
    text = raw.strip()
    if text.lower() in ("n/a", "none", "unknown", "?", "-"):
        return ""
    text = text.rstrip(".,;!? ")
    if not re.match(r"^https?://", text, re.IGNORECASE):
        if re.match(r"^[a-zA-Z0-9]", text):
            text = "https://" + text
        else:
            return ""
    try:
        parsed = urlparse(text)
    except ValueError:
        return ""
    if not parsed.hostname:
        return ""
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    port = parsed.port
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None
    netloc = f"{hostname}:{port}" if port else hostname
    cleaned = urlunparse((scheme, netloc, parsed.path, parsed.params,
                          parsed.query, parsed.fragment))
    if parsed.path in ("", "/") and not parsed.query and not parsed.fragment:
        cleaned = cleaned.rstrip("/")
    return cleaned


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PIPELINE                                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def _map_header(raw_header: str) -> str | None:
    return HEADER_ALIASES.get(raw_header.strip().lower())


def read_and_standardize(filepath: str) -> tuple[list[dict], list[dict]]:
    """
    Read, standardize, and compute per-row checksums in a single pass.

    Returns:
        (standardized_rows, row_checksums)

    Each standardized row includes 'row_index' and 'source_hash'.
    Each row_checksum entry is {"row_index": int, "source_hash": str}.
    """
    standardized_rows = []
    row_checksums = []

    with open(filepath, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter="\t")
        raw_headers = next(reader)
        mapped = [_map_header(h) for h in raw_headers]

        missing = set(CANONICAL_FIELDS) - set(h for h in mapped if h)
        if missing:
            print(f"⚠  Warning: unmapped columns {missing}. "
                  f"Raw headers: {raw_headers}", file=sys.stderr)
            if len(raw_headers) >= 4:
                mapped = CANONICAL_FIELDS[:len(raw_headers)]
            else:
                print("✖  Fatal: fewer than 4 columns.", file=sys.stderr)
                sys.exit(1)

        for line_num, values in enumerate(reader, start=1):
            # --- Checksum the raw values before any transformation ---
            src_hash = hash_row(values)

            # Map to dict
            row = {}
            for col_name, value in zip(mapped, values):
                if col_name:
                    row[col_name] = value

            if not any(row.values()):
                print(f"  ℹ  Skipping empty row at line {line_num + 1}",
                      file=sys.stderr)
                continue

            # Standardize
            std = {
                "date": standardize_date(row.get("date", "")),
                "title": standardize_title(row.get("title", "")),
                "object_number": standardize_object_number(
                    row.get("object_number", "")
                ),
                "link": standardize_link(row.get("link", "")),
                "row_index": str(line_num),
                "source_hash": src_hash,
            }
            standardized_rows.append(std)
            row_checksums.append({
                "row_index": line_num,
                "source_hash": src_hash,
            })

    return standardized_rows, row_checksums


OUTPUT_FIELDNAMES = [
    "date", "title", "object_number", "link", "row_index", "source_hash"
]


def write_inventory(filepath: str, rows: list[dict]) -> None:
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=OUTPUT_FIELDNAMES, delimiter="\t", extrasaction="ignore",
        )
        writer.writerow({f: OUTPUT_HEADER_LABELS.get(f, f) for f in OUTPUT_FIELDNAMES})
        writer.writerows(rows)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  MAIN                                                                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory .tsv with checksum auditing."
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- standardize sub-command (default) ---
    std_parser = subparsers.add_parser("standardize", help="Standardize a .tsv file.")
    std_parser.add_argument("input", help="Path to the input .tsv file.")
    std_parser.add_argument("-o", "--output", default=None,
                            help="Output .tsv path.")
    std_parser.add_argument("--dry-run", action="store_true",
                            help="Print to stdout instead of writing.")

    # --- verify sub-command ---
    ver_parser = subparsers.add_parser("verify",
                                       help="Verify a standardized file.")
    ver_parser.add_argument("output", help="Path to the standardized .tsv file.")

    args = parser.parse_args()

    # Default to "standardize" if no sub-command given (for backward compat)
    if args.command is None:
        # Re-parse treating the first positional as input to standardize
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            args.command = "standardize"
            args.input = sys.argv[1]
            args.output = None
            args.dry_run = "--dry-run" in sys.argv
            for i, a in enumerate(sys.argv):
                if a in ("-o", "--output") and i + 1 < len(sys.argv):
                    args.output = sys.argv[i + 1]
        else:
            parser.print_help()
            sys.exit(1)

    # ----- Verify mode -----
    if args.command == "verify":
        ok = verify(args.output)
        sys.exit(0 if ok else 1)

    # ----- Standardize mode -----
    if args.output is None:
        base = args.input.rsplit(".", 1)[0]
        args.output = f"{base}_standardized.tsv"

    print(f"📂 Reading: {args.input}")
    source_file_hash = hash_file(args.input)
    print(f"   Source SHA-256: {source_file_hash}")

    rows, row_checksums = read_and_standardize(args.input)
    print(f"✅ Standardized {len(rows)} rows.")

    if args.dry_run:
        print()
        print("\t".join(OUTPUT_HEADER_LABELS.get(f, f) for f in OUTPUT_FIELDNAMES))
        for row in rows:
            print("\t".join(row.get(f, "") for f in OUTPUT_FIELDNAMES))
        return

    write_inventory(args.output, rows)
    output_file_hash = hash_file(args.output)

    manifest = build_manifest(
        source_path=args.input,
        output_path=args.output,
        row_checksums=row_checksums,
        source_file_hash=source_file_hash,
        output_file_hash=output_file_hash,
        row_count=len(rows),
    )
    manifest_path = write_manifest(manifest, args.output)

    print(f"💾 Written to: {args.output}")
    print(f"   Output SHA-256:  {output_file_hash}")
    print(f"📋 Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
```

## What Changed and Why

### 1. Per-row `source_hash` — embedded in the output

```
Date    Title              Object Number   Link                    Row Index   Source Hash
2024-01-15  The Starry Night   2024.001.005    https://museum.org/x    1       a3f2…b710
```

The hash is computed **before any transformation** by tab-joining the raw cell values and taking SHA-256. This means you can always go back to the source file, grab line N, hash it the same way, and confirm it matches.

### 2. Sidecar manifest file (`.manifest.json`)

```json
{
  "schema_version": "1.0",
  "script_version": "2.0.0",
  "created_utc": "2025-01-15T12:00:00+00:00",
  "source": {
    "path": "/data/inventory.tsv",
    "size_bytes": 10842,
    "sha256": "e3b0c44298fc1c14..."
  },
  "output": {
    "path": "/data/inventory_standardized.tsv",
    "size_bytes": 12201,
    "sha256": "9f86d081884c7d65..."
  },
  "row_count": 347,
  "rows": [
    {"row_index": 1, "source_hash": "a3f2...b710"},
    {"row_index": 2, "source_hash": "7c1e...9a03"}
  ]
}
```

The manifest is the **single source of truth** for auditing. It lives alongside the output file and is independent of it — so even if someone edits the `.tsv`, the manifest catches it.

### 3. Built-in verification mode

```bash
# After standardizing
python standardize_inventory.py standardize inventory.tsv

# Later, verify nothing was tampered with
python standardize_inventory.py verify inventory_standardized.tsv
```

```
🔍 Checking output file integrity...
   ✅ Output file SHA-256 matches.
🔍 Checking source file integrity...
   ✅ Source file SHA-256 matches.
🔍 Checking per-row source hashes...
   ✅ All 347 row hashes match.

🎉 Verification PASSED — data integrity confirmed.
```

### Why SHA-256 on the raw tab-joined values?

| Alternative | Problem |
|---|---|
| Hash the standardized values | Can't detect if standardization logic changed or was applied to different source data |
| Hash individual cells | Doesn't catch column-swap or reordering tampering |
| CRC32 / MD5 | Not collision-resistant enough for audit purposes |
| Hash the entire file only | Can't pinpoint *which* row was altered |

Hashing the **raw, pre-transformation, tab-joined row** means the checksum is a tamper-evident seal tying each cleaned row to its exact original, and SHA-256 on the full row is both simple and robust.
