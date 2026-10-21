"""Checksum-plans study (decision record 26): what each session's plan and
follow-up answer say about checksums. Reads runs/*/reply_1.md (the plan) and
reply_2.md (the answer to the follow-up), and records for each session:

  unprompted          the plan mentions checksums or hashes before the follow-up
  levels              the levels its checksums are made at, from either reply:
                      whole file, row, column, cell (a sentence naming a
                      checksum and the level)
  source_row_kept     a checksum of each source row is kept with the result
                      (a sentence naming a checksum, a row, and the original or
                      source; candidates for the research coordinator to read)
  statements          sentences about what checksums can or can't cover, for
                      the research coordinator to read

  code_levels         the same levels read from the replies' code: what each
                      hashing call is applied to (a file's bytes, or a row's
                      cells), from the call's line and the few lines before it
  hash_columns        names in the code for stored checksums ("source_row_hash"),
                      candidates for source_row_kept

These are found by wording, so they are proposals: the research coordinator
reads every reply and records any correction in review.json. The categories
they feed are set in decision record 27, before any reply was read.

Usage:
    python scripts/classify_plans.py experiments/checksum-plans
writes <experiment>/plan_levels.json.
"""
import json
import pathlib
import re
import sys

HASH = re.compile(r"\b(?:check-?sums?|hash(?:es|ed|ing)?|sha-?(?:1|256|512)|md5|digests?|fingerprints?)\b", re.I)
LEVELS = {
    "file": re.compile(r"\b(?:(?:whole|entire|full|source|original|input|output|result(?:ing)?|"
                       r"standardi[sz]ed|raw)\s+(?:\.?tsv\s+)?files?|file[- ]level|per[- ]file|sha256sum\s+\S+\.tsv)\b", re.I),
    "row": re.compile(r"\b(?:per[- ](?:row|record|line)|row[- ](?:level|wise|by[- ]row)|(?:each|every|individual|"
                      r"single|a)\s+(?:source\s+|original\s+)?(?:row|record|line)s?|row[_ ]?(?:hash|checksum))\b", re.I),
    "column": re.compile(r"\b(?:per[- ]column|column[- ](?:level|wise)|(?:each|every|individual|single)\s+column)\b", re.I),
    "cell": re.compile(r"\b(?:per[- ](?:cell|field|value)|(?:cell|field)[- ]level|(?:each|every|individual|single)\s+"
                       r"(?:cell|field|value))\b", re.I),
}
SOURCE = re.compile(r"\b(?:source|original|input|raw|pre-?standardi[sz]ation|before)\b", re.I)
CLAIM = re.compile(r"\b(?:only|whole|entire|itself|its own|can(?:no|')t|cannot|won't|will not|impossible|"
                   r"not possible|any change|every change|wouldn't|would not)\b", re.I)


def sentences(text):
    if len(re.findall(r"^\s*```", text, flags=re.M)) % 2:  # cut off inside its code
        text += "\n```"
    text = re.sub(r"```.*?```", " ", text, flags=re.S)  # code shows how, the prose says what
    return [s.strip() for s in re.split(r"(?<=[.!?:])\s+|\n+", text) if s.strip()]


HASH_CALL = re.compile(r"hashlib\.(?:sha\d+|md5|new|blake2\w*)\s*\(|\b(?:sha256|md5|sha1)\s*\(|"
                       r"\b(?:sha256sum|shasum|md5sum)\b|Get-FileHash|\.update\s*\(", re.I)
CODE_FILE = re.compile(r"\bopen\s*\([^)]*['\"]rb['\"]|\.read\s*\(\s*(?:\d+|\w*chunk\w*)?\s*\)|\bchunk|"
                       r"\b(?:sha256sum|shasum|md5sum)\b|Get-FileHash|def\s+\w*file\w*|file_?path", re.I)
CODE_ROW = re.compile(r"\brows?\b|\brecords?\b|\bcells\b|\bfields\b|\bvalues\b|\bline\b|\.join\s*\(|"
                      r"def\s+\w*(?:row|record)\w*|iterrows|DictReader|csv\.reader", re.I)
HASH_NAME = re.compile(r"['\"]([A-Za-z_ ]*(?:hash|checksum|sha256|sha_256|md5|digest|fingerprint)[A-Za-z_ ]*)['\"]", re.I)


def code_blocks(text):
    if len(re.findall(r"^\s*```", text, flags=re.M)) % 2:  # a reply cut off inside its code
        text += "\n```"
    return re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.S)


def code_levels(text):
    """Levels of the hashing in the code: for each hashing call, its line, the
    four before it, and the signature of the function it sits in (hashing is
    often in a helper, "def row_digest(fields):") decide whether it hashes a
    file or a row."""
    levels = set()
    for block in code_blocks(text):
        lines = block.splitlines()
        for i, ln in enumerate(lines):
            if not HASH_CALL.search(ln) or ln.lstrip().startswith("#"):
                continue
            sig = next((l for l in reversed(lines[:i]) if re.match(r"\s*(?:async\s+)?def\s", l)), "")
            near = "\n".join([sig] + lines[max(0, i - 4): i + 1])
            if CODE_ROW.search(ln) or (CODE_ROW.search(near) and not CODE_FILE.search(ln)):
                levels.add("row")
            if CODE_FILE.search(near):
                levels.add("file")
    return sorted(levels)


def classify(root):
    out = []
    for d in sorted((pathlib.Path(root) / "runs").iterdir()):
        plan = (d / "reply_1.md").read_text(encoding="utf-8") if (d / "reply_1.md").exists() else ""
        answer = (d / "reply_2.md").read_text(encoding="utf-8") if (d / "reply_2.md").exists() else ""
        replies = [plan, answer]  # read one by one: a reply cut off mid-code mustn't shift the next one's fences
        hashed = [s for t in replies for s in sentences(t) if HASH.search(s)]
        levels = sorted(k for k, rx in LEVELS.items() if any(rx.search(s) for s in hashed))
        out.append({
            "run": d.name,
            "model": re.sub(r"-r\d+$", "", d.name),
            "unprompted": bool(HASH.search(plan)),
            "code_levels": sorted(set(code_levels(plan)) | set(code_levels(answer))),
            "hash_columns": sorted({m.group(1) for t in replies for b in code_blocks(t)
                                    for m in HASH_NAME.finditer(b)})[:12],
            "levels": levels,
            "source_row_kept": [s for s in hashed if LEVELS["row"].search(s) and SOURCE.search(s)][:6],
            "statements": [s for s in hashed if CLAIM.search(s)][:12],
        })
    return out


def main():
    root = pathlib.Path(sys.argv[1])
    rows = classify(root)
    (root / "plan_levels.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    for r in rows:
        print(r["run"], "unprompted" if r["unprompted"] else "-", r["levels"], "code:", r["code_levels"],
              f"source-row sentences: {len(r['source_row_kept'])}", f"statements: {len(r['statements'])}")


if __name__ == "__main__":
    main()
