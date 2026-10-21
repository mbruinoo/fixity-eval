# What checksums can and can't buy you

A hash proves **integrity** ("these bytes are the bytes I saw") and **provenance** ("this output row was derived from *that* input row"). It cannot prove the transformation was *correct* — only that it was applied to known input and hasn't drifted since. Designing for that distinction gives three separate layers:

| Layer | Question it answers | Where it lives |
|---|---|---|
| **File fixity** | Has either file been altered since the run? | Sidecar manifest (BagIt-compatible SHA-256) |
| **Row provenance** | Which source row produced this output row, and is that source row still identical? | `source_hash` column + manifest |
| **Rule replay** | Does re-running today's script on the same source still produce these values? | `result_hash` column + `ruleset_version` |

## Canonicalization is the whole game

Hashing `"\t".join(fields)` is broken: `("a\tb", "c")` and `("a", "b\tc")` hash identically, and the digest changes if the exporter switches quoting style or line endings. Hash a **length-prefixed (netstring) serialization of the parsed cells** instead, with a role tag so the same tuple hashed as "source" and as "result" can never collide.

Decide explicitly what each digest covers:

- `source_hash` covers **every column of the source row as read, byte-exact** — no cleaning, no NFC, including columns the script ignores. Any change to the source is supposed to break it.
- `result_hash` covers **only the four canonical output fields** — never the derived date columns, the `issues` column, or the hash columns themselves (self-reference).

## Code: add to `standardize_inventory.py`

```python
# =========================================================================
# FIXITY — canonicalization, digests, manifest, verification
# =========================================================================
import hashlib
import json
import platform
from pathlib import Path

HASH_ALGO = "sha256"            # file level: full digest, interoperable with bagit/shasum
ROW_DIGEST_BITS = 96            # row level: truncated so the TSV stays readable
CANON_VERSION = "canon/1"       # bump ONLY if the serialization below changes
RULESET_VERSION = "rules/1.0.0" # bump on ANY change to a normalizer's behaviour

HASHED_FIELDS = ("date", "title", "object_number", "link")  # covered by result_hash
_HEX = ROW_DIGEST_BITS // 4


def canonical_blob(fields, role: bytes) -> bytes:
    """Unambiguous byte serialization: role, canon version, then netstrings.

    Length prefixes guarantee ('a\\tb','c') and ('a','b\\tc') cannot collide,
    and make the digest independent of the source file's quoting style,
    line terminators and column padding.
    """
    out = bytearray(role + b"\x00" + CANON_VERSION.encode("ascii") + b"\x00")
    for f in fields:
        b = ("" if f is None else str(f)).encode("utf-8")
        out += b"%d:" % len(b) + b + b","
    return bytes(out)


def digest(fields, role: bytes, truncate: bool = True) -> str:
    h = hashlib.new(HASH_ALGO, canonical_blob(fields, role)).hexdigest()
    return h[:_HEX] if truncate else h


def source_digest(raw_row) -> str:
    """Hash of the complete source record, exactly as parsed."""
    return digest(raw_row, b"source")


def result_digest(std_row: dict) -> str:
    """Hash of the standardized values only."""
    return digest([std_row[k] for k in HASHED_FIELDS], b"result")


def collection_digest(row_digests) -> str:
    """Order-independent digest of a whole set of rows.

    Sorting first means re-sorting the file does not break the digest, while
    any insertion, deletion or edit does. Use the unsorted sequence instead
    if row order is itself significant.
    """
    h = hashlib.new(HASH_ALGO, b"collection\x00" + CANON_VERSION.encode() + b"\x00")
    for d in sorted(row_digests):
        h.update(d.encode("ascii") + b"\n")
    return h.hexdigest()


def file_digest(path) -> tuple[str, int]:
    h, n = hashlib.new(HASH_ALGO), 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


# ---- manifest -----------------------------------------------------------

MANIFEST_OPTIONS = ("no_header", "keep_case", "untitled", "objnum_upper",
                    "force_https", "keep_fragment", "keep_trailing_slash",
                    "dedupe", "sort", "derived_dates", "issues_column",
                    "reference_year")


def build_manifest(args, rep, src_path, out_path, src_digests, out_rows, dropped):
    src_hash, src_size = file_digest(src_path)
    manifest = {
        "manifest_version": 1,
        "created_utc": datetime.datetime.now(datetime.timezone.utc)
                               .replace(microsecond=0).isoformat(),
        "tool": {
            "name": "standardize_inventory.py",
            "ruleset_version": RULESET_VERSION,
            "canon_version": CANON_VERSION,
            "script_sha256": hashlib.sha256(
                Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "unicode_version": unicodedata.unidata_version,  # NFC can change between releases
        },
        "options": {k: getattr(args, k, None) for k in MANIFEST_OPTIONS},
        "algorithm": {"name": HASH_ALGO, "row_digest_bits": ROW_DIGEST_BITS,
                      "hashed_output_fields": list(HASHED_FIELDS)},
        "source": {
            "path": os.path.basename(src_path),
            "bytes": src_size,
            f"{HASH_ALGO}": src_hash,
            "rows": rep.rows_in,
            "collection_digest": collection_digest(src_digests),
        },
        "output": {
            "path": os.path.basename(out_path) if out_path else "<stdout>",
            "rows": rep.rows_out,
            "collection_digest": collection_digest(r["result_hash"] for r in out_rows),
            # file hash is filled in after the file is closed
        },
        "dropped_source_hashes": sorted(dropped),   # explains rows absent from output
        "flags": dict(rep.issues),
    }
    return manifest
```

### Hooks into the existing script

```python
# 1. read_rows(): keep the raw record alongside the mapped one
        out.append(({f: (r[i] if i < len(r) else "") for f, i in mapping.items()},
                    list(r)))                       # (mapped, raw)

# 2. process_row(): stamp both digests onto the result
    std = {"date": date_disp, "title": title, ...}
    std["source_hash"] = source_digest(raw_row)
    std["result_hash"] = result_digest(std)
    return std

# 3. main(): track dropped rows and emit the manifest
    dropped = set()
    ...
            if key in seen and args.dedupe:
                dropped.add(out["source_hash"])
                continue
    ...
    if args.hash_columns:
        keys += ["source_hash", "result_hash"]
        headers += ["source_hash", "result_hash"]
    write_rows(processed, args.output, headers, keys)

    if args.manifest:
        m = build_manifest(args, rep, args.input, args.output,
                           src_digests, processed, dropped)
        if args.output:
            m["output"][HASH_ALGO], m["output"]["bytes"] = file_digest(args.output)
        Path(args.manifest).write_text(
            json.dumps(m, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")

# 4. new CLI options
    p.add_argument("--manifest", help="write a JSON fixity/provenance manifest")
    p.add_argument("--hash-columns", action="store_true",
                   help="add source_hash and result_hash columns to the output")
    p.add_argument("--reference-year", type=int, default=CURRENT_YEAR,
                   help="year used for 'date in the future' checks "
                        "(pin this for reproducible runs)")
    p.add_argument("--verify", metavar="MANIFEST",
                   help="verify a standardized file against its manifest and source")
```

### The verifier

```python
def verify(manifest_path, source_path, standardized_path) -> int:
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    problems = Counter()
    note = lambda kind, msg: (problems.update([kind]),
                              print(f"  [{kind}] {msg}", file=sys.stderr))

    # --- Layer 1: file fixity ------------------------------------------
    for label, path, rec in (("source", source_path, m["source"]),
                             ("output", standardized_path, m["output"])):
        got, size = file_digest(path)
        if rec.get(HASH_ALGO) and got != rec[HASH_ALGO]:
            note("file-modified", f"{label} {HASH_ALGO} {got} != {rec[HASH_ALGO]}")

    # --- Layer 2 + 3: provenance and replay -----------------------------
    if m["tool"]["ruleset_version"] != RULESET_VERSION:
        print(f"NOTE: manifest was written by {m['tool']['ruleset_version']}, "
              f"this script is {RULESET_VERSION}; value drift below is expected "
              f"and should be re-baselined, not 'fixed'.", file=sys.stderr)

    args = argparse.Namespace(**m["options"])
    src_index = {}
    for mapped, raw in read_rows(source_path, args.no_header):
        src_index.setdefault(source_digest(raw), []).append(mapped)

    seen_source = set()
    rep = Report()
    with open(standardized_path, newline="", encoding="utf-8-sig") as fh:
        for n, row in enumerate(csv.DictReader(fh, delimiter="\t"), start=2):
            sh, rh = row.get("source_hash"), row.get("result_hash")
            if not sh or not rh:
                note("unhashed-row", f"output row {n} carries no digests")
                continue
            seen_source.add(sh)
            if sh not in src_index:
                note("orphan-row", f"output row {n}: source {sh} not in {source_path}")
                continue
            replay = process_row(src_index[sh][0], n, args, rep)
            if replay["result_hash"] != rh:
                changed = [f for f in HASHED_FIELDS
                           if (row.get(FIELD_TO_HEADER[f], "") != replay[f])]
                note("value-drift", f"output row {n} ({sh}): {', '.join(changed) or 'edited in place'}")

    for sh in set(src_index) - seen_source - set(m.get("dropped_source_hashes", [])):
        note("missing-from-output", f"source row {sh} has no standardized row")

    print(f"verified against {manifest_path}: "
          f"{'OK' if not problems else dict(problems)}", file=sys.stderr)
    return 0 if not problems else 2
```

### Resulting manifest

```json
{
  "algorithm": {"name": "sha256", "row_digest_bits": 96,
                "hashed_output_fields": ["date","title","object_number","link"]},
  "created_utc": "2025-03-11T14:02:07+00:00",
  "source": {"path": "inventory.tsv", "bytes": 418233, "rows": 4812,
             "sha256": "9f2c…", "collection_digest": "4b81…"},
  "output": {"path": "inventory_clean.tsv", "rows": 4806,
             "sha256": "c107…", "collection_digest": "d93a…"},
  "options": {"dedupe": true, "sort": "objnum", "reference_year": 2025, "…": "…"},
  "tool": {"ruleset_version": "rules/1.0.0", "canon_version": "canon/1",
           "script_sha256": "77ad…", "python": "3.12.2", "unicode_version": "15.0.0"},
  "dropped_source_hashes": ["1f3b9c2a7d4e8f0b5a6c1d22", "…"],
  "flags": {"date-unparsed": 1204, "link-empty": 88}
}
```

## Determinism: the part that bites

Replay verification is worthless if the script isn't a pure function of (source, options). Two real hazards, one of which is a bug in the script I gave you earlier:

1. **`CURRENT_YEAR = datetime.date.today().year`** makes the `date-implausible-year` flag time-dependent — a 2026 re-run of a 2025 file can produce different `issues`. Fixed above by threading `--reference-year` through `normalize_date()` and recording it in the manifest. (It doesn't affect `result_hash` since flags aren't hashed, but it does affect the issues report, and that's exactly the kind of silent drift you want to eliminate.)
2. **Unicode and IDNA tables are Python-version dependent.** NFC output and `host.encode("idna")` can in principle change across releases, so `unicodedata.unidata_version` and the Python version go in the manifest. Python's `str.upper()/casefold()` are locale-independent, so there's no Turkish-dotted-i trap — but don't introduce `locale.strxfrm` or `str.title()` later.

Also keep every set/dict iteration sorted before it reaches output (`"; ".join(sorted(set(...)))` already is), and never hash a dict's `repr`.

## Operational notes

- **Truncation.** 96-bit row digests give a collision probability of ~6×10⁻¹⁸ at one million rows (birthday bound ≈ n²/2^97). Dropping to 64 bits to save column width raises that to ~3×10⁻⁸ at the same scale — still fine for an inventory, but 96 bits costs only eight more characters.
- **Sidecar vs columns.** The manifest is authoritative; `--hash-columns` is for convenience when the TSV travels alone. Expect curators to open the file in Excel, which will happily turn `1975.1` into a date and `0012.4` into `12.4` — the `result_hash` mismatch is how you find out. Say so in the documentation, because the first reaction to a failed verification is usually "the checker is broken."
- **Storage.** Commit the manifest to git next to the data, or keep it on write-once storage; a hash you can edit alongside the data proves nothing. If you need tamper-*evidence* rather than tamper-*detection*, detach-sign it (`gpg --detach-sign --armor inventory_clean.manifest.json`) or publish the `collection_digest` somewhere append-only.
- **Re-baselining.** Source corrections and ruleset changes both legitimately break digests. The workflow should be: run `--verify` → if the only failures are `value-drift` *and* `ruleset_version` differs, re-run the standardizer and commit a new manifest with a message naming the rule change. Keep old manifests; the chain of them is the audit trail.
- **Cost.** Hashing is negligible next to the TSV parsing — on the order of a second per gigabyte for SHA-256. If you ever do need it faster, `hashlib.blake2b(digest_size=12)` is a drop-in for the row digests and roughly 2–3× quicker; keep SHA-256 at the file level for interoperability with existing fixity tooling.
