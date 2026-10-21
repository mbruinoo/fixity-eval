## What the checksums need to answer

Four different questions get conflated into "add a hash column," and they need four different digests:

| Question | Digest | Scope |
|---|---|---|
| Did the source *file* change since the run? | SHA-256 of the raw input bytes | file |
| Did *this row's* source values change? | `source_hash` over the four original cells, semantically normalized | row |
| Has the cleaned file been edited since it was produced? | `record_hash` over all output columns | row |
| Is this the same dataset, regardless of row order? | `dataset_digest` = hash of the sorted list of `record_hash` values | file |

Plus one that is easy to forget: **did the *rules* change?** If you re-run with `--circa-years 10`, every date row legitimately differs. So the manifest also stores an `options_digest` and a `hash_spec` version, letting you distinguish "the data changed" from "the tool changed."

One design rule worth stating plainly: **a content hash is not an identity.** If you key rows by their hash, every correction to a title creates a "new" row and orphans the old one. Identity should be the accession number (your actual institutional primary key), with a `file_id#line` fallback; hashes answer *changed/unchanged*, not *which row*.

## Canonicalization — the part that breaks later

A hash is only reproducible if the byte serialization is pinned. The rules below are the whole ballgame:

- Normalize to NFC and apply the same whitespace collapsing used for the data (so a re-export with a non-breaking space or a trailing tab doesn't look like a curatorial edit).
- Join fields with `U+001F` (unit separator), which cannot occur in the data, so `"a\tb" + "c"` can never collide with `"a" + "b\tc"`.
- Prefix every payload with a spec tag and a domain label (`mi-hash/1␞record␞…`) so that if you ever change these rules, old and new hashes can't silently collide, and a source hash can never equal a record hash.
- Fix the column order and record it in the manifest; `record_hash` covers all output columns *except itself*.
- Truncate to 16 hex characters (64 bits) for legibility in a spreadsheet — ample for change detection at collection scale.

## Code to add

```python
import hashlib, hmac, io, json, os, platform
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

HASH_SPEC = "mi-hash/1"      # bump if canonicalization below ever changes
RS, US = "\x1e", "\x1f"
SOURCE_FIELDS = ["date_original", "title_original",
                 "object_number_original", "link_original"]
HASH_COLUMNS = ["row_uid", "source_hash", "record_hash"]


def _canon(values):
    return US.join(unicodedata.normalize("NFC", "" if v is None else str(v))
                   for v in values)


def digest(domain, values, length=16, key=None):
    payload = (HASH_SPEC + RS + domain + RS + _canon(values)).encode("utf-8")
    mac = hmac.new(key, payload, hashlib.sha256) if key else hashlib.sha256(payload)
    return mac.hexdigest()[:length]


def bytes_digest(data, key=None):
    mac = hmac.new(key, data, hashlib.sha256) if key else hashlib.sha256(data)
    return mac.hexdigest()


def add_hashes(records, columns, file_id, length=16, key=None):
    """Attach row_uid, source_hash, record_hash. Must run before sorting/writing."""
    objcount = Counter(r["object_number"] for r in records if r["object_number"])
    for r in records:
        r["source_hash"] = digest("source", [r[f] for f in SOURCE_FIELDS], length, key)
        on = r["object_number"]
        if on and objcount[on] == 1:
            r["row_uid"] = on                      # natural key: the accession number
        else:
            r["row_uid"] = f"{file_id}#{r['_line']}"
            flags = set(filter(None, r["flags"].split(";"))) | {"UID_FALLBACK"}
            r["flags"] = ";".join(sorted(flags))   # flags are final before next loop
    covered = [c for c in columns if c != "record_hash"]
    for r in records:
        r["record_hash"] = digest("record", [r.get(c, "") for c in covered], length, key)
    return covered


def dataset_digest(records, key=None):
    """Order-independent fingerprint of the whole table."""
    blob = "\n".join(sorted(r["record_hash"] for r in records)).encode("utf-8")
    return bytes_digest(blob, key)


def load_key(path):
    if not path:
        return None
    with open(path, "rb") as fh:
        return fh.read().strip()
```

### Hooks into the existing script

**1. Read the source as bytes first**, so the digest provably matches what was parsed:

```python
    if args.input:
        with open(args.input, "rb") as fh:
            raw_bytes = fh.read()
    else:
        raw_bytes = sys.stdin.buffer.read()
    src_sha = bytes_digest(raw_bytes)
    file_id = src_sha[:8]
    text = raw_bytes.decode(args.encoding, errors="replace")
    reader = csv.reader(io.StringIO(text, newline=""), **kw)
    raw_rows = [r for r in reader]
```

**2. In `main()`, between processing and sorting:**

```python
    columns = OUT_COLUMNS + (ORIG_COLUMNS if args.keep_original else [])
    if not args.no_hash:
        columns += HASH_COLUMNS
        key = load_key(args.hmac_key_file)
        covered = add_hashes(records, columns, file_id, args.hash_length, key)
        ds_digest = dataset_digest(records, key)
```

**3. After `write_tsv(...)`, emit the sidecar manifest** (it must be written last, because it contains the digest of the finished output file):

```python
    if args.output and not args.no_hash and not args.no_manifest:
        out_sha = bytes_digest(open(args.output, "rb").read())
        opts = {k: v for k, v in sorted(vars(args).items())
                if k not in {"input", "output", "report", "review", "manifest",
                             "verify", "source", "hmac_key_file"}}
        manifest = {
            "schema": "museum-inventory-manifest/1",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool": {"name": "standardize_inventory.py", "version": VERSION,
                     "hash_spec": HASH_SPEC, "hmac": bool(args.hmac_key_file),
                     "python": platform.python_version(),
                     "unicode": unicodedata.unidata_version},
            "options": opts,
            "options_digest": digest("options", [json.dumps(opts, sort_keys=True)]),
            "source": {"path": os.path.abspath(args.input) if args.input else "<stdin>",
                       "bytes": len(raw_bytes), "sha256": src_sha, "file_id": file_id,
                       "encoding": args.encoding, "rows_read": len(body)},
            "output": {"path": os.path.abspath(args.output), "columns": columns,
                       "covered_columns": covered, "rows_written": len(records),
                       "sha256": out_sha, "dataset_digest": ds_digest},
        }
        path = args.manifest or (args.output + ".manifest.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
```

**4. New arguments:**

```python
    p.add_argument("--no-hash", action="store_true", help="omit checksum columns")
    p.add_argument("--hash-length", type=int, default=16,
                   help="hex chars kept from each SHA-256 (default: 16)")
    p.add_argument("--hmac-key-file", help="key file: makes checksums tamper-evident")
    p.add_argument("--manifest", help="manifest path (default: <output>.manifest.json)")
    p.add_argument("--no-manifest", action="store_true")
    p.add_argument("--verify", action="store_true",
                   help="verify INPUT (a cleaned file) against its manifest")
    p.add_argument("--source", help="with --verify: also reconcile against the original")
```

Also add `"UID_FALLBACK"` to the flag glossary in the docstring.

### Verification mode

```python
def verify_mode(args):
    man_path = args.manifest or (args.input + ".manifest.json")
    with open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)
    key = load_key(args.hmac_key_file)
    columns = man["output"]["columns"]
    covered = man["output"]["covered_columns"]
    length = int(man["options"].get("hash_length", 16))

    with open(args.input, "rb") as fh:
        raw = fh.read()
    file_ok = bytes_digest(raw) == man["output"]["sha256"]

    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""),
                           delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None))
    header, body = rows[0], rows[1:]
    if header != columns:
        print("FATAL: column layout differs from manifest", file=sys.stderr)
        return 2
    idx = {c: i for i, c in enumerate(header)}

    results, recs = Counter(), []
    for n, row in enumerate(body, start=2):
        rec = {c: (row[idx[c]] if idx[c] < len(row) else "") for c in columns}
        recs.append(rec)
        recomputed = digest("record", [rec[c] for c in covered], length, key)
        status = "OK" if recomputed == rec["record_hash"] else "OUTPUT_EDITED"
        results[status] += 1
        if status != "OK":
            print(f"line {n}\t{rec['row_uid']}\t{status}")

    ds_ok = dataset_digest(recs, key) == man["output"]["dataset_digest"]

    if args.source:   # three-way reconciliation against a fresh export
        with open(args.source, "rb") as fh:
            sbytes = fh.read()
        srows = list(csv.reader(io.StringIO(
            sbytes.decode(man["source"]["encoding"], errors="replace"), newline=""),
            delimiter=args.delimiter))
        srows = [r for r in srows if any(c.strip() for c in r)]
        colmap = detect_columns(srows[0]) or {n: i for i, n in enumerate(POSITIONAL)}
        body_s = srows[1:] if detect_columns(srows[0]) else srows
        src = {}
        for r in body_s:
            def g(name):
                i = colmap.get(name)
                return norm_text(r[i]) if i is not None and i < len(r) else ""
            uid = clean_objnum(g("object_number"))[0]
            if uid:
                src[uid] = digest("source", [g("date"), g("title"),
                                             g("object_number"), g("link")], length, key)
        seen = set()
        for rec in recs:
            uid = rec["row_uid"]
            seen.add(uid)
            if uid not in src:
                results["SOURCE_MISSING"] += 1
                print(f"{uid}\tSOURCE_MISSING")
            elif src[uid] != rec["source_hash"]:
                results["SOURCE_CHANGED"] += 1
                print(f"{uid}\tSOURCE_CHANGED")
        for uid in src.keys() - seen:
            results["SOURCE_NEW"] += 1
            print(f"{uid}\tSOURCE_NEW")

    print(f"\nmanifest:        {man_path}", file=sys.stderr)
    print(f"file digest:     {'OK' if file_ok else 'MISMATCH (byte-level)'}",
          file=sys.stderr)
    print(f"dataset digest:  {'OK' if ds_ok else 'MISMATCH'}", file=sys.stderr)
    for k, v in results.most_common():
        print(f"{v:7d}  {k}", file=sys.stderr)
    return 0 if ds_ok and not (results - Counter({"OK": results['OK']})) else 1
```

Wire it in at the top of `main()`: `if args.verify: return verify_mode(args)`.

### Workflow

```bash
# produce clean.tsv + clean.tsv.manifest.json
python3 standardize_inventory.py raw.tsv -o clean.tsv --report report.txt

# six months later: has anyone edited the cleaned file?
python3 standardize_inventory.py clean.tsv --verify

# and has the collections system changed upstream?
python3 standardize_inventory.py clean.tsv --verify --source raw_reexport_2026.tsv
```

Output classifies every row as `OK`, `OUTPUT_EDITED`, `SOURCE_CHANGED`, `SOURCE_MISSING`, or `SOURCE_NEW` — which is exactly the worklist a registrar needs after a re-export.

## Caveats worth writing into your procedures

**Excel will break the byte digest, and that's useful.** Opening `clean.tsv` in Excel and re-saving changes line endings and quoting, so `file digest: MISMATCH` fires on a cosmetic round-trip — hence the order-independent `dataset_digest` and per-row `record_hash` as the authoritative checks. More importantly, Excel silently coerces `1975.10` to `1975.1` and reads `date_start` as a date serial. The row hashes catch that class of corruption immediately, which is arguably the single best reason to add them to a museum inventory.

**SHA-256 alone is integrity, not tamper-evidence.** Anyone who edits a row can recompute its hash. If the file is an audit record, pass `--hmac-key-file` (key stored outside the spreadsheet, e.g. in a password manager) or detach-sign the manifest with GPG/minisign. Record which was used — the manifest has an `hmac: true/false` field for that.

**Row-level source reconciliation needs a stable natural key.** Rows without a unique object number get a `file_id#line` UID and a `UID_FALLBACK` flag; they can be checked for output edits but not matched back to a re-export, because line numbers shift. Treat `UID_FALLBACK` as a data-quality defect to fix at source.

**Version the spec, not just the tool.** `HASH_SPEC` covers the canonicalization rules; `options_digest` covers the run parameters; `unicode`/`python` record the NFC implementation. If a verification run reports mass `OUTPUT_EDITED`, compare those three fields first — nine times out of ten the rules moved, not the data.
