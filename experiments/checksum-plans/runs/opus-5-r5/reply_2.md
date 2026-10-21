## What's worth hashing (and why each one answers a different question)

A single file checksum only answers "did these bytes change?" For reconciling a standardized file against its source months later, you actually want four digests at three granularities:

| Digest | Scope | Question it answers |
|---|---|---|
| `source.sha256` | whole input file, raw bytes | "Is this the exact file I processed?" |
| `output.sha256` | whole output file, raw bytes | "Has the clean file been edited since I made it?" (i.e. *has someone opened it in Excel*) |
| `source_hash` | one input row, as read | "Which source row did this row come from, and has that row changed at source?" |
| `record_hash` | one output row, normalized | "Has this standardized record been altered, and did my rule change affect it?" |

Plus one non-row digest that saves the most grief:

| `ruleset_fingerprint` | script source + options | "Output differs — was that the data, or did I change the rules?" |

Without the last one, every rule tweak looks like data corruption.

## Design decisions that actually matter

**Canonicalize before hashing, and version the canonicalization.** A row hash is only reproducible if the serialization is injective. Joining fields with a delimiter is not: `("a\tb", "c")` and `("a", "b\tc")` collide. I length-prefix every field (`name:len:bytes`) and stamp the spec with a version string (`msi-1`) that gets bumped whenever the serialization changes, so old manifests remain interpretable.

**Hash raw cells for `source_hash`, normalized values for `record_hash`.** The source hash deliberately sees trailing spaces, NBSPs, and curly quotes — those are exactly the invisible edits you want flagged. The record hash sees only the cleaned output, so cosmetic noise at source doesn't churn it.

**Hash decoded text, not file bytes, at row level.** Re-saving the source as UTF-8 instead of CP1252 changes the file digest but should *not* change row digests. That split is a feature: file digest = "same artifact", row digests = "same content".

**Identity ≠ integrity.** A content hash changes when a record is legitimately corrected, so a corrected row looks like delete + insert. Pair the hash with a stable key (object number) so the diff can distinguish `CHANGED` from `ADDED`/`REMOVED`.

**Truncate for the spreadsheet, keep full in the manifest.** 16 hex chars = 64 bits; at 100 000 rows the birthday collision probability is ~2.7 × 10⁻¹⁰. Fine for integrity, and it keeps the column readable.

**Prefix the digest (`s256:9f2c…`).** A bare hex string like `5e1234567890abcd` is parsed by Excel and Google Sheets as scientific notation and silently destroyed. The `s256:` prefix forces text and documents the algorithm.

**Rows become self-validating.** Because `record_hash` covers the row's own fields, you can detect manual edits to the clean file *without* the manifest. This guards against accidents, not adversaries — see the caveat at the end.

## Drop-in additions to the script

Add near the top:

```python
import hashlib, json, platform
from datetime import datetime, timezone
from pathlib import Path

# Bump whenever the canonical serialization below changes. Old manifests keep
# their own spec string, so they stay verifiable.
HASH_SPEC = "msi-1"
DIGEST_LEN = 16          # hex chars kept in the TSV; 0 = full 64
DIGEST_PREFIX = "s256"   # keeps spreadsheets from parsing digests as numbers

# Fields covered by record_hash. Deliberately excludes flags (diagnostics),
# the hash columns themselves, and pass-through extras.
RECORD_FIELDS = ["date", "date_earliest", "date_latest",
                 "title", "object_number", "link"]


def _frame(name: str, value: str) -> bytes:
    """Injective field encoding: name:bytelen:utf8bytes."""
    b = (value or "").encode("utf-8")
    return name.encode("utf-8") + b":" + str(len(b)).encode("ascii") + b":" + b


def digest(pairs, spec: str = HASH_SPEC, length: int = DIGEST_LEN,
           prefix: str = DIGEST_PREFIX) -> str:
    h = hashlib.sha256()
    h.update(spec.encode("ascii") + b"\x00")
    for name, value in pairs:
        h.update(_frame(name, value) + b"\x1f")
    hexd = h.hexdigest()
    return f"{prefix}:{hexd[:length] if length else hexd}"


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_pairs(rec: dict, extras: list[str]):
    """Raw, pre-normalization cells, in a fixed order."""
    return ([(c, rec[c]) for c in CANON] +
            [("x:" + n, rec["_extras"].get(n, "")) for n in extras])


def record_pairs(row: dict):
    return [(f, row.get(f, "")) for f in RECORD_FIELDS]


def ruleset_fingerprint(args) -> str:
    """Fingerprint of (this script, the options that affect output)."""
    try:
        tool = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except OSError:
        tool = "unavailable"
    ignore = {"input", "output", "report", "manifest", "verify", "quiet",
              "against_source", "strict"}
    opts = {k: v for k, v in sorted(vars(args).items()) if k not in ignore}
    h = hashlib.sha256()
    h.update(tool.encode() + b"\x00")
    h.update(json.dumps(opts, sort_keys=True, default=str).encode())
    return f"{DIGEST_PREFIX}:{h.hexdigest()[:16]}", tool
```

Three edits inside `main()`:

```python
# 1. in the per-row loop, BEFORE any normalization:
        src_hash = digest(source_pairs(rec, extras))

# 2. after `row` is built, before flags are attached:
        row["source_hash"] = src_hash
        row["record_hash"] = digest(record_pairs(row))

# 3. in the output field list, before "flags":
    fields += ["source_hash", "record_hash"]
```

And after the file is written, emit the manifest:

```python
    if a.manifest:
        fp, tool_sha = ruleset_fingerprint(a)
        ordered = hashlib.sha256(
            "\n".join(r["record_hash"] for r in out_rows).encode()).hexdigest()
        unordered = hashlib.sha256(
            "\n".join(sorted(r["record_hash"] for r in out_rows)).encode()).hexdigest()
        manifest = {
            "manifest_version": 1,
            "hash_spec": HASH_SPEC,
            "digest_prefix": DIGEST_PREFIX,
            "digest_len": DIGEST_LEN,
            "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool": {"name": Path(__file__).name, "sha256": tool_sha,
                     "python": platform.python_version()},
            "ruleset_fingerprint": fp,
            "options": {k: v for k, v in sorted(vars(a).items())},
            "source": {
                "path": str(Path(a.input).resolve()),
                "bytes": Path(a.input).stat().st_size,
                "sha256": file_sha256(a.input),
                "encoding": encoding,          # returned by read_table
                "delimiter": a.delimiter,
                "rows": len(rows),
                "column_mapping": {str(k): v for k, v in mapping.items()},
                "extras": extras,
            },
            "output": {
                "path": str(Path(a.output).resolve()) if a.output != "-" else "-",
                "sha256": file_sha256(a.output) if a.output != "-" else None,
                "rows": len(out_rows),
                "record_digest_ordered": "sha256:" + ordered,
                "record_digest_unordered": "sha256:" + unordered,
            },
            "counts": dict(generic),
        }
        Path(a.manifest).write_text(json.dumps(manifest, indent=2,
                                               ensure_ascii=False) + "\n",
                                    encoding="utf-8")
```

This needs `read_table` to also return the mapping and encoding it used (`return rows, extras, mapping, encoding`), and two new flags:

```python
    p.add_argument("--manifest", metavar="PATH",
                   help="write a JSON provenance/checksum manifest")
    p.add_argument("--verify", metavar="MANIFEST",
                   help="verify a previous run instead of standardizing")
    p.add_argument("--against-source", action="store_true",
                   help="with --verify, also re-read the source and diff row by row")
```

The `record_digest_unordered` is the useful one in practice: sorting the clean file or re-ordering rows is a legitimate editorial act that shouldn't invalidate the content fingerprint, whereas the ordered digest tells you whether row order itself changed.

## The verifier

```python
def verify(manifest_path: str, against_source: bool = False) -> int:
    """Exit codes: 0 all good, 2 drift (expected change), 3 integrity failure."""
    man = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    spec = man.get("hash_spec", HASH_SPEC)
    dlen = man.get("digest_len", DIGEST_LEN)
    dpfx = man.get("digest_prefix", DIGEST_PREFIX)
    out_path = man["output"]["path"]
    status, drift = [], False
    fail = False

    # 1. Output file integrity -------------------------------------------------
    if out_path and out_path != "-" and Path(out_path).exists():
        actual = file_sha256(out_path)
        if actual == man["output"]["sha256"]:
            status.append(f"OK    output file digest matches ({actual[:12]}…)")
        else:
            status.append("FAIL  output file has been modified since the run")
            status.append(f"      expected {man['output']['sha256'][:12]}… got {actual[:12]}…")
            fail = True
    else:
        status.append("WARN  output file not found; row checks only")

    # 2. Source file integrity -------------------------------------------------
    src_path = man["source"]["path"]
    source_changed = None
    if Path(src_path).exists():
        actual = file_sha256(src_path)
        source_changed = actual != man["source"]["sha256"]
        status.append(("DRIFT source file has changed since the run"
                       if source_changed else "OK    source file digest matches"))
        drift |= bool(source_changed)
    else:
        status.append(f"WARN  source file missing: {src_path}")

    # 3. Per-row self-consistency of the clean file ---------------------------
    rows_out, bad_rows = [], []
    if out_path and out_path != "-" and Path(out_path).exists():
        with open(out_path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                rows_out.append(r)
                want = digest(record_pairs(r), spec, dlen, dpfx)
                if r.get("record_hash") and want != r["record_hash"]:
                    bad_rows.append((r.get("object_number", "?"),
                                     r["record_hash"], want))
        if bad_rows:
            status.append(f"FAIL  {len(bad_rows)} row(s) edited after standardization:")
            for objnum, old, new in bad_rows[:10]:
                status.append(f"      {objnum}: recorded {old} but content hashes to {new}")
            fail = True
        else:
            status.append(f"OK    {len(rows_out)} row record_hash values self-consistent")

    # 4. Row-level diff against the current source ----------------------------
    if against_source and Path(src_path).exists():
        opts = man["options"]
        rows_src, extras, _, _ = read_table(
            src_path, opts.get("delimiter", "\t"),
            opts.get("no_header", False),
            [c.strip() for c in opts.get("columns", ",".join(CANON)).split(",")])
        now = {}
        for rec in rows_src:
            key = clean_text(rec["object_number"]).upper()
            now[key] = digest(source_pairs(rec, man["source"]["extras"]), spec, dlen, dpfx)
        then = {r["object_number"].upper(): r.get("source_hash") for r in rows_out}

        added = sorted(set(now) - set(then))
        removed = sorted(set(then) - set(now))
        changed = sorted(k for k in set(now) & set(then)
                         if then[k] and now[k] != then[k])
        if added or removed or changed:
            drift = True
            status.append(f"DRIFT source rows: {len(changed)} changed, "
                          f"{len(added)} added, {len(removed)} removed")
            for label, keys in (("CHANGED", changed), ("ADDED", added),
                                ("REMOVED", removed)):
                for k in keys[:10]:
                    status.append(f"      {label:7} {k}")
                if len(keys) > 10:
                    status.append(f"      …and {len(keys) - 10} more {label.lower()}")
        else:
            status.append("OK    every source row still hashes to its recorded value")

    status.append("")
    status.append(f"ruleset fingerprint at run time: {man['ruleset_fingerprint']}")
    print("\n".join(status))
    return 3 if fail else (2 if drift else 0)
```

Wire it in as the first thing `main()` does:

```python
    if a.verify:
        return verify(a.verify, a.against_source)
```

## Workflow

```bash
# Standardize and record provenance
python3 standardize_inventory.py inventory.tsv \
    -o clean.tsv --manifest clean.manifest.json --report qa.txt

# Months later: has anyone touched the clean file?
python3 standardize_inventory.py --verify clean.manifest.json

# Has the source registry moved on, and which records does that affect?
python3 standardize_inventory.py --verify clean.manifest.json --against-source

# Interop with standard tooling
jq -r '"\(.output.sha256)  \(.output.path)"' clean.manifest.json > clean.sha256
sha256sum -c clean.sha256
```

Typical drift output:

```
OK    output file digest matches (2b41a7c9f0e3…)
DRIFT source file has changed since the run
OK    498 row record_hash values self-consistent
DRIFT source rows: 3 changed, 12 added, 0 removed
      CHANGED 1979.123.4
      CHANGED 1981.7A-B
      CHANGED TR.2004.19
      ADDED   2024.55.1
      …and 11 more added
```

Exit code 2 means "re-run me", exit code 3 means "someone edited a deliverable, investigate". That distinction makes the script safe to drop into a cron job or CI check.

## Caveats worth stating in the documentation

- **This is tamper-evident against accidents, not adversaries.** Anyone with the script can recompute `record_hash` after editing a row. If you need genuine tamper evidence, swap `hashlib.sha256()` for `hmac.new(key, …, hashlib.sha256)` with a key held outside the repository, or sign the manifest (`gpg --detach-sign`, `minisign`). The manifest is the right thing to sign — it transitively covers both files.
- **Truncated digests are for humans.** Keep `DIGEST_LEN = 0` (full 64 hex) if the file feeds an automated reconciliation at scale, or if the hashes will ever be used as join keys.
- **A changed `ruleset_fingerprint` invalidates nothing but explains everything.** When you tighten a date rule, every affected `record_hash` legitimately changes; the fingerprint difference is what tells a future reader that the rules moved, not the data.
- **Round-tripping through Excel will trip the output digest**, including when nothing visible changed — Excel rewrites line endings, drops the BOM, and will happily convert `1850-01` into a real date and `1979.123` into a float. That is the single most common real-world cause of a `FAIL`, and catching it is most of the value here.
- **Archive the manifest next to the deliverable**, not just in the working directory; it is the only record linking a clean file to the source state and rule version that produced it.
