"""Check whether the checksums in a sheet's added columns were really
computed, before they're counted as invented.

hallu_score.py counts a checksum in an added column as invented (1.0 per
character) when it matches no checksum of its row under the usual recipes,
was never printed by a tool, and was typed by the model itself. A real
checksum made with an unusual recipe (columns in another order, another
separator, another algorithm) would be miscounted. This script searches a far
wider set of recipes for each flagged value, and reports how the values were
made:

  typed_by_model     the value appears in the model's own tool input (a file
                     it wrote, a command), so no code produced it
  seen_first         the value was printed by a tool before the model wrote it
  hashing_code       a command or delivered script used hashlib/sha256sum/md5sum
  impossible_length  the value's length matches no common hash (MD5 32, SHA-1
                     40, SHA-256 64, SHA-512 128 hex characters; 8 for CRC32)
  non_hex            the value has characters a hex digest can't contain
  wide_matches       values (of a sample per run) that some wider recipe
                     reproduces: 10 algorithms and CRC32; any ordering of up
                     to 4 of the row's cells, from the source or the output;
                     11 separators; 4 line endings; upper and lower case,
                     trimmed, decomposed accents; UTF-8, UTF-16, Latin-1;
                     JSON and the raw line as written

Usage:
    python scripts/audit_checksums.py experiments/<name> [--sample 3]
writes <experiment>/checksum_audit.json.
"""
import argparse
import collections
import hashlib
import itertools
import json
import pathlib
import re
import sys
import unicodedata
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import hallu_score as H  # noqa: E402

ALGOS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s"]
SEPS = ["\t", ",", "|", ";", " ", "", " | ", ", ", ":", "\n", "||"]
ENDS = ["", "\n", "\r\n", "\t"]
LENGTHS = {8, 32, 40, 56, 64, 96, 128}


def digests(b):
    out = {getattr(hashlib, a)(b).hexdigest() for a in ALGOS}
    out.add(format(zlib.crc32(b) & 0xffffffff, "08x"))
    return out


def payloads(cell_lists, raw_lines):
    for cells in cell_lists:
        for n in range(1, min(len(cells), 4) + 1):
            for perm in itertools.permutations(cells, n):
                for sep in SEPS:
                    for end in ENDS:
                        s = sep.join(perm) + end
                        yield from (s, s.strip(), s.lower(), s.upper(), unicodedata.normalize("NFD", s))
        yield from (json.dumps(cells, ensure_ascii=False), json.dumps(cells), repr(tuple(cells)), str(list(cells)))
    for ln in raw_lines:
        for end in ENDS:
            yield ln + end


def wide_match(value, cell_lists, raw_lines):
    v = value.lower()
    for p in payloads(cell_lists, raw_lines):
        for enc in ("utf-8", "utf-16", "latin-1"):
            try:
                b = p.encode(enc)
            except UnicodeEncodeError:
                continue
            if any(d.startswith(v) or (len(v) >= 16 and v in d) for d in digests(b)):
                return {"payload": p[:80], "encoding": enc}
    return None


def audit_run(run_dir, input_path, sample=3):
    res = H.score_run(run_dir, input_path)
    flagged = [c for c in res.get("changes", []) if c["kind"] in ("extra_column", "extra_unverified")
               and H.HASH_HEADER.search(c["column"])]
    if not flagged:
        return None
    _, rows_in = H.read_input(input_path)
    raw_in = pathlib.Path(input_path).read_text(encoding="utf-8").split("\n")[1:]
    out_path = run_dir / "output_files" / res["result_file"]
    out_lines = out_path.read_text(encoding="utf-8", errors="replace").split("\n")
    sheet = dict(H.parse_sheet(out_path))[res["parse"]]
    num_col = H.columns(sheet[0])["Object Number"]
    events = H.tool_events(run_dir)
    vals = [c["output"].strip() for c in flagged]
    files = [f for f in (run_dir / "output_files").rglob("*") if f.suffix in (".py", ".sh")]
    bash = (run_dir / "bash_log.md").read_text(errors="replace") if (run_dir / "bash_log.md").exists() else ""
    hashing = bool(re.search(r"hashlib|sha256sum|md5sum|shasum", bash)) or any(
        re.search(r"hashlib|sha256sum|md5sum", f.read_text(errors="replace")) for f in files)
    matches = []
    for c in flagged[:sample]:
        src = rows_in[c["input_row"] - 1]
        v = c["output"].strip()
        out_row = next((r for r in sheet[1:] if num_col is not None and num_col < len(r)
                        and H.key_num(r[num_col]) == H.key_num(src[2])), [])
        out_cells = [x for x in out_row if x.strip() != v]
        raw = [raw_in[c["input_row"] - 1]] + [ln.replace(v, "").rstrip("\t") for ln in out_lines if v in ln]
        matches.append(wide_match(v, [src, out_cells, src[:3], out_cells[:3]], raw))
    return {
        "run": run_dir.name, "column": flagged[0]["column"], "cells": len(vals), "distinct": len(set(vals)),
        "lengths": dict(sorted(collections.Counter(len(v) for v in vals).items())),
        "impossible_length": sum(1 for v in vals if len(v) not in LENGTHS),
        "non_hex": sum(1 for v in vals if not re.fullmatch(r"[0-9a-fA-F]+", v)),
        "typed_by_model": sum(1 for v in vals if any(v.lower() in i for i, _ in events)),
        "seen_first": sum(1 for v in vals if H.seen_before_written(v.lower(), events)),
        "hashing_code": hashing,
        "wide_matches": sum(1 for m in matches if m), "wide_sample": len(matches),
        "match_example": next((m for m in matches if m), None),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--sample", type=int, default=3, help="flagged values per run given the wide search")
    a = ap.parse_args()
    root = pathlib.Path(a.experiment)
    inputs = {}
    for cfg_file in root.glob("config*.json"):
        cfg = json.loads(cfg_file.read_text())
        for c in cfg["conditions"]:
            inputs[c["id"]] = cfg["inputs"][c["input"]]
    out = []
    for run_dir in sorted((root / "runs").iterdir()):
        cond = re.sub(r"-r\d+$", "", run_dir.name)
        if cond in inputs and (run_dir / "meta.json").exists():
            r = audit_run(run_dir, inputs[cond], a.sample)
            if r:
                out.append(r)
                print(json.dumps(r, ensure_ascii=False))
    (root / "checksum_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
