"""Score every TSV a run delivered, before and after each follow-up.

hallu_score.py scores only a run's final output_files/. Runs with
"followups" (run_tools.py) also keep earlier files in
output_files_before_followup<N>/. This scores each TSV in each of those
folders against the input, and writes <experiment>/stage_scores.json.

Usage:
    python scripts/score_stages.py experiments/spike-11
"""
import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hallu_score import score_run  # noqa: E402


def main():
    root = pathlib.Path(sys.argv[1])
    cfg = json.loads((root / "config.json").read_text())
    out = []
    for run_dir in sorted((root / "runs").iterdir()):
        cond = next(c for c in cfg["conditions"] if run_dir.name.startswith(c["id"]))
        src = cfg["inputs"][cond["input"]]
        stages = sorted(run_dir.glob("output_files_before_followup*")) + [run_dir / "output_files"]
        for stage in stages:
            for f in sorted(stage.glob("*.tsv")) if stage.exists() else []:
                with tempfile.TemporaryDirectory() as tmp:
                    d = pathlib.Path(tmp) / run_dir.name
                    (d / "output_files").mkdir(parents=True)
                    shutil.copy(f, d / "output_files" / f.name)
                    res = score_run(d, src)
                res.update({"stage": stage.name, "file": f.name})
                res.pop("examples", None)
                out.append(res)
                print(f"{run_dir.name:28} {stage.name:32} {f.name:34} rows={res.get('output_rows')} "
                      f"inv={res.get('invented_rows')} miss={res.get('missing_rows')} "
                      f"t1={res.get('rows_by_tier', {}).get('tier1_content')} fixity={res.get('fixity_error_rate')}")
    (root / "stage_scores.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
