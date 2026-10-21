## What each checksum is actually for

"Add checksums" usually collapses four different questions into one. It's worth keeping them separate, because they fail independently:

| Question | Artifact |
|---|---|
| Is the source file still the exact one I cleaned? | SHA‑256 of the **input bytes** |
| Has the clean file been edited since the run? | SHA‑256 of the **output bytes** |
| Which source row produced *this* output row, and has that row's content changed? | **Per‑row digest**, carried in a ledger |
| Would re-running the pipeline still produce this output? | **Pipeline fingerprint** (script + options + Python/Unicode versions) + determinism |

A single file hash answers only the first two. The per‑row digest is the one that does real work for a registrar: it gives every row a stable identity even when the object number is missing, duplicated, or itself got reformatted, so a later diff can say "row 214's title changed in the source" rather than "the file is different."

## The part that's easy to get wrong: canonicalization

Hashing `"\t".join(row)` is brittle — a re-export from Excel changes line endings, adds a BOM, pads trailing empty columns, and flips `’` between NFC and NFD, and every digest breaks for no substantive reason. So define the serialization explicitly, and compute **two** row digests:

- **`source_sha256` (verbatim):** cells exactly as read, joined with `U+001F`, trailing empty cells dropped, CRLF→LF, UTF‑8 encoded. Changes if *anything* changes — the chain-of-custody digest.
- **`content_sha256` (canonical):** same, but NFC‑normalized and whitespace-collapsed first. Stays stable across cosmetic re-exports, so a mismatch means someone actually edited the data.

Use a unit separator rather than a tab so that a value containing a tab can't be confused with a column boundary (`a\tb | c` and `a | b\tc` must not hash alike).

Two more digests are worth recording: a **set digest** (hash of the sorted row digests), which is invariant to row order and so survives `--sort`, and a **schema digest** over the header, so a column rename is detectable.

## Drop-in additions to the script

```python
# --------------------------------------------------------------------------- #
# Provenance: checksums, ledger, manifest
# --------------------------------------------------------------------------- #

import hashlib
import json
import os
import platform
from datetime import datetime, timezone

HASH_ALG = "sha256"
UNIT_SEP = "\x1f"
PIPELINE_NAME = "standardize_inventory.py"
PIPELINE_VERSION = "1.1.0"
MANIFEST_VERSION = "1.0"

# Options that can change the output. Anything not listed here must not affect it.
MATERIAL_OPTIONS = (
    "no_header", "date_style", "dayfirst", "fix_caps", "straight_quotes",
    "strip_final_period", "keep_fragment", "keep_tracking", "dedupe", "sort",
    "add_sort_columns",
)


def _h(data: bytes) -> str:
    return hashlib.new(HASH_ALG, data).hexdigest()


def file_digest(path: str) -> str:
    """SHA-256 of a file's bytes, streamed."""
    h = hashlib.new(HASH_ALG)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _serialize(cells: list[str]) -> bytes:
    cells = [c.replace("\r\n", "\n").replace("\r", "\n") for c in cells]
    while cells and cells[-1] == "":
        cells.pop()                      # trailing empty columns are not data
    return UNIT_SEP.join(cells).encode("utf-8")


def row_digest(cells: list[str]) -> str:
    """Verbatim digest: changes if any byte of the row changes."""
    return _h(_serialize(cells))


def content_digest(cells: list[str]) -> str:
    """Canonical digest: ignores BOM/NFD/whitespace noise from re-exports."""
    return _h(_serialize([clean_text(c) for c in cells]))


def set_digest(digests) -> str:
    """Order-independent digest of a collection of row digests."""
    h = hashlib.new(HASH_ALG)
    for d in sorted(digests):
        h.update(bytes.fromhex(d))
    return h.hexdigest()


def pipeline_fingerprint(args) -> dict:
    opts = {k: getattr(args, k) for k in MATERIAL_OPTIONS}
    opts_blob = json.dumps(opts, sort_keys=True, separators=(",", ":")).encode()
    try:
        script_sha = file_digest(os.path.abspath(__file__))
    except OSError:
        script_sha = None
    return {
        "name": PIPELINE_NAME,
        "version": PIPELINE_VERSION,
        "script_sha256": script_sha,
        "options": opts,
        "options_sha256": _h(opts_blob),
        "python": platform.python_version(),
        "unicode_version": unicodedata.unidata_version,  # NFC results depend on this
        "hash_algorithm": HASH_ALG,
        "row_serialization": "cells joined by U+001F, trailing empties dropped, UTF-8",
    }


LEDGER_FIELDS = ["source_row", "source_sha256", "content_sha256",
                 "output_row", "output_sha256", "object_number", "status"]


def write_ledger(path: str, entries: list[dict]) -> str:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(LEDGER_FIELDS) + "\n")
        for e in entries:
            fh.write("\t".join(sanitize_cell(str(e.get(f, ""))) for f in LEDGER_FIELDS) + "\n")
    return file_digest(path)


def write_manifest(path: str, payload: dict, hmac_key: bytes | None = None) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    if hmac_key:
        import hmac
        payload = dict(payload)
        payload["hmac_sha256"] = hmac.new(hmac_key, body.encode("utf-8"),
                                          hashlib.sha256).hexdigest()
        body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body + "\n")
```

### Hooking it into `main()`

Four small edits:

```python
    # 1. Before processing — fingerprint the source.
    source_sha = file_digest(args.input) if args.input != "-" else None
    schema_sha = _h(_serialize(rows[0])) if start_row else None
    ledger: list[dict] = []

    # 2. Inside the per-row loop, right after `raw = {...}`:
    src_digest = row_digest(row)
    src_content = content_digest(row)

    #    …and when a row is dropped by --dedupe:
    ledger.append({"source_row": n, "source_sha256": src_digest,
                   "content_sha256": src_content, "output_row": "",
                   "output_sha256": "", "object_number": objnum,
                   "status": "dropped_duplicate"})
    continue

    #    …and on the successful path, attach the digests to the cleaned record:
    cleaned.append({..., "_src_row": n, "_src_sha": src_digest,
                    "_src_content": src_content})

    # 3. While writing the output file, record each written row's digest
    #    (do this after sorting, so output_row numbers are the final ones):
    for out_no, r in enumerate(cleaned, start=2):           # row 1 is the header
        out_cells = [sanitize_cell(r[f]) for f in fields]
        fh.write("\t".join(out_cells) + "\n")
        ledger.append({"source_row": r["_src_row"], "source_sha256": r["_src_sha"],
                       "content_sha256": r["_src_content"], "output_row": out_no,
                       "output_sha256": row_digest(out_cells),
                       "object_number": r["object_number"], "status": "emitted"})
    ledger.sort(key=lambda e: e["source_row"])

    # 4. After the output file is closed — hash it and write the sidecars.
    if args.manifest:
        ledger_path = args.ledger or (os.path.splitext(args.output)[0] + ".ledger.tsv")
        emitted = [e for e in ledger if e["status"] == "emitted"]
        manifest = {
            "manifest_version": MANIFEST_VERSION,
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pipeline": pipeline_fingerprint(args),
            "source": {
                "path": os.path.abspath(args.input),
                "bytes": os.path.getsize(args.input),
                "sha256": source_sha,
                "schema_sha256": schema_sha,
                "column_map": order,
                "rows_read": len(rows) - start_row,
                "row_set_sha256": set_digest(e["source_sha256"] for e in ledger),
            },
            "output": {
                "path": os.path.abspath(args.output),
                "bytes": os.path.getsize(args.output),
                "sha256": file_digest(args.output),
                "columns": fields,
                "rows_written": len(emitted),
                "row_set_sha256": set_digest(e["output_sha256"] for e in emitted),
            },
            "ledger": {"path": os.path.abspath(ledger_path),
                       "sha256": write_ledger(ledger_path, ledger)},
            "counts": {"dropped_duplicates": len(ledger) - len(emitted),
                       "issues": len(issues)},
        }
        write_manifest(args.manifest, manifest)
```

Note the ordering: the output file's digest is computed from the bytes on disk *after* writing, and stored outside that file. Never embed a file's own checksum in itself.

### The verify mode

```python
def verify(manifest_path: str, recompute: bool = False) -> int:
    with open(manifest_path, encoding="utf-8") as fh:
        mf = json.load(fh)
    ok = True

    def check(label, expected, actual):
        nonlocal ok
        good = expected == actual
        ok &= good
        print(f"[{'OK ' if good else 'FAIL'}] {label}")
        if not good:
            print(f"        expected {expected}\n        actual   {actual}")

    check("source file unchanged", mf["source"]["sha256"], file_digest(mf["source"]["path"]))
    check("ledger unchanged",      mf["ledger"]["sha256"], file_digest(mf["ledger"]["path"]))

    out_now = file_digest(mf["output"]["path"])
    if out_now == mf["output"]["sha256"]:
        print("[OK ] standardized file unchanged")
    else:
        ok = False
        print("[FAIL] standardized file changed — locating edited rows…")
        with open(mf["ledger"]["path"], encoding="utf-8", newline="") as fh:
            recorded = {r["output_sha256"]: r
                        for r in csv.DictReader(fh, delimiter="\t")
                        if r["status"] == "emitted"}
        with open(mf["output"]["path"], encoding="utf-8-sig", newline="") as fh:
            rdr = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
            next(rdr, None)
            present = {row_digest(r): n for n, r in enumerate(rdr, start=2)}
        for d, r in recorded.items():
            if d not in present:
                print(f"        row {r['output_row']} ({r['object_number'] or '?'}) "
                      f"modified or deleted")
        for d, n in present.items():
            if d not in recorded:
                print(f"        row {n} added or modified after the run")

    if recompute:
        # Re-derive the output from the source with the recorded options and
        # compare row sets. Proves the clean file is the faithful product of
        # the source — not merely that both files are untouched.
        fp = mf["pipeline"]
        if fp["unicode_version"] != unicodedata.unidata_version:
            print(f"[WARN] Unicode {unicodedata.unidata_version} now vs "
                  f"{fp['unicode_version']} at run time; NFC results may differ")
        argv = [mf["source"]["path"], "-o", "-"] + options_to_argv(fp["options"])
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(argv)
        rdr = csv.reader(io.StringIO(buf.getvalue()), delimiter="\t", quoting=csv.QUOTE_NONE)
        next(rdr, None)
        check("re-run reproduces output", mf["output"]["row_set_sha256"],
              set_digest(row_digest(r) for r in rdr))

    print("\nVERIFIED" if ok else "\nVERIFICATION FAILED")
    return 0 if ok else 1
```

Wire it up with `python standardize_inventory.py verify clean.manifest.json [--recompute]`, dispatched before the normal argument parsing.

## Where the digests live

Keep the standardized TSV at four columns and put identity in the **sidecar ledger** — that's the default above. The ledger is the join table: `source_row ↔ source_sha256 ↔ output_row`. It also records rows that were *dropped*, which an output-only artifact can never tell you.

If downstream consumers won't carry a sidecar, offer `--embed-digest` to append a fifth `source_sha256` column, truncated to 16 hex characters for legibility (~1 in 10¹⁰ collision risk at 10⁵ rows; the full digest stays in the ledger). Be aware the embedded column changes the output row digests — hash the row *as written*, including that column, and the scheme stays self-consistent.

## Caveats worth writing into your procedures

- **`--recompute` only works if the pipeline is deterministic.** The script is, with one asterisk: `unicodedata.normalize` depends on the Unicode version bundled with Python, so an NFC result can in principle shift across upgrades. Recording `unidata_version` turns a silent mismatch into an explainable one. If the normalizations ever consult locale (`%B` month names) or the current date, pin or record those too — note that the "year out of expected range" check uses `date.today()`, so it affects the *report*, not the output.
- **Checksums detect change; they don't prevent it.** Anyone who can edit `clean.tsv` can regenerate `clean.manifest.json`. If you need tamper-evidence rather than error-detection, commit the manifest to version control, sign it, or pass an HMAC key held elsewhere (the `hmac_key` hook above).
- **Hashes are not a substitute for keeping the source.** If you still have `raw.tsv`, the per-row digests mainly buy you fast, unambiguous alignment. They become essential only when the source is archived off-site, is too large to re-diff, or is a live database export you can't freeze — then the digest is your only evidence of what row 214 said at the time.
- **Re-exports of the same data will break `source_sha256` but not `content_sha256`.** When verification fails, compare the content digests first: if those match, the curator re-saved the file; if they differ, the data genuinely changed.
