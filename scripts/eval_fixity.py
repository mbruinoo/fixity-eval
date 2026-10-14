"""Grade what a session did with a fixity follow-up, from the files it left.

For each run of an experiment (runs/<id>/) this checks the archive the model
delivered (output_files/) against the real uploaded file:

  first_answer_rate     fixity error rate of the sheet before the follow-up
  result_rate           fixity error rate of the final result
  script_on_upload      a bash command ran a script, and the upload was read
                        from its real location (uploads/) by a command or by
                        the script's own text
  before_identical      a file in the archive is byte-identical to the upload
  before_retyped        a .tsv offered as the input/original/before is not
  input_checksum        a checksum of the real upload appears in the archive
  output_checksum       a checksum of a delivered result file appears
  stale_checksums       checksum-like values that match no delivered or input
                        file (wrong, made up, or of a file that changed)
  row_checksums         the result has a column of per-row hashes
  change_log            a file lists changes (before/after)

Usage:
    python scripts/eval_fixity.py experiments/spike-21
"""
import hashlib
import json
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hallu_score import score_run  # noqa: E402

HEX = re.compile(r"\b(?:[0-9a-f]{64}|[0-9a-f]{40}|[0-9a-f]{32})\b")
TEXT = {".txt", ".md", ".tsv", ".csv", ".sh", ".py", ".json", ".log", ".sha256", ".md5"}


def digests(b):
    return {hashlib.md5(b).hexdigest(), hashlib.sha1(b).hexdigest(), hashlib.sha256(b).hexdigest()}


def rate(path, input_path):
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp) / "r"
        (d / "output_files").mkdir(parents=True)
        shutil.copy(path, d / "output_files" / path.name)
        r = score_run(d, input_path)
    return r.get("fixity_error_rate"), r


def grade(run_dir, input_path):
    original = pathlib.Path(input_path).read_bytes()
    out = run_dir / "output_files"
    before = sorted(run_dir.glob("output_files_before_followup*"))
    meta = json.loads((run_dir / "meta.json").read_text()) if (run_dir / "meta.json").exists() else {}
    g = {"run": run_dir.name, "followup_sent": bool(meta.get("followups_sent")) or bool(before),
         "followup_skipped": meta.get("followup_skipped")}
    if before:
        tsvs = sorted(before[0].glob("*.tsv"))
        g["first_answer_rate"] = rate(tsvs[-1], input_path)[0] if tsvs else None
    files = [f for f in out.rglob("*") if f.is_file()] if out.exists() else []
    tsvs = [f for f in files if f.suffix in (".tsv", ".csv")]
    identical = [f.name for f in tsvs if f.read_bytes() == original]
    named_input = [f for f in tsvs if re.search(r"orig|input|before|raw|source", f.name, re.I)]
    results = [f for f in tsvs if f.name not in identical and f not in named_input] or \
              [f for f in tsvs if f.name not in identical]
    g["before_identical"] = bool(identical)
    g["before_retyped"] = [f.name for f in named_input if f.name not in identical]
    if results:
        res = max(results, key=lambda f: f.stat().st_size)
        g["result_file"] = res.name
        g["result_rate"], r = rate(res, input_path)
        head = res.read_text(encoding="utf-8", errors="replace").split("\n")
        rows = [ln.split("\t") for ln in head if ln and not ln.startswith("#")]
        g["row_checksums"] = any(sum(1 for row in rows[1:] if len(row) > i and HEX.fullmatch(row[i].strip() or "x"))
                                 > len(rows) // 2 for i in range(max((len(x) for x in rows), default=0)))
    # checksums claimed anywhere in the archive (text files)
    claimed = set()
    for f in files:
        if f.suffix in TEXT:
            claimed |= set(HEX.findall(f.read_text(encoding="utf-8", errors="replace").lower()))
    input_d = digests(original)
    result_d = set().union(*(digests(f.read_bytes()) for f in results)) if results else set()
    known = input_d | set().union(*(digests(f.read_bytes()) for f in files)) if files else input_d
    row_hashes = set()
    if results and g.get("row_checksums"):
        for ln in results[0].read_text(encoding="utf-8", errors="replace").split("\n"):
            row_hashes |= set(HEX.findall(ln.lower()))
    g["input_checksum"] = bool(claimed & input_d)
    g["output_checksum"] = bool(claimed & result_d)
    g["stale_checksums"] = len(claimed - known - row_hashes)
    g["change_log"] = any(re.search(r"change|diff|log", f.name, re.I) and
                          re.search(r"before|after|old|new|->|→", f.read_text(encoding="utf-8", errors="replace"), re.I)
                          for f in files if f.suffix in TEXT and f.suffix != ".py")
    # did a script run on the real upload?
    log = (run_dir / "bash_log.md").read_text(encoding="utf-8") if (run_dir / "bash_log.md").exists() else ""
    ran = re.search(r"python3?\s+\S+\.py|bash\s+\S+\.sh", log)
    scripts = [f.read_text(encoding="utf-8", errors="replace") for f in files if f.suffix in (".py", ".sh")]
    reads_upload = "uploads/" in log or any("uploads" in s for s in scripts)
    g["script_on_upload"] = bool(ran and reads_upload)
    g["files"] = sorted(f.name for f in files)
    return g


def main():
    root = pathlib.Path(sys.argv[1])
    cfg = json.loads((root / "config.json").read_text())
    out = []
    for run_dir in sorted((root / "runs").iterdir()):
        cond = next((c for c in cfg["conditions"] if run_dir.name.startswith(c["id"])), None)
        if not cond:
            continue
        g = grade(run_dir, cfg["inputs"][cond["input"]])
        out.append(g)
        print(json.dumps({k: v for k, v in g.items() if k != "files"}, ensure_ascii=False))
    (root / "fixity_eval.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
