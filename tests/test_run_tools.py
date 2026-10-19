"""The runner refuses to start on a frozen input whose checksum doesn't match
(decisions/2026-10-18-04-held-out-file.md). No model calls are made."""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parents[1]
F_SHA256 = "a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf"


def run(tmp_path, sha):
    cfg = {"model": "claude-haiku-4-5", "price_per_mtok": {"input": 1, "output": 5}, "budget_stop_usd": 0.0,
           "max_calls": 0, "repeats": 1, "inputs": {"f": str(ROOT / "data" / "met_inventory_f.tsv")},
           "input_sha256": {"f": sha}, "conditions": []}
    (tmp_path / "config.json").write_text(json.dumps(cfg))
    env = {k: v for k, v in os.environ.items() if k != "FIXITY_ANTHROPIC_API_KEY"}
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "run_tools.py"), str(tmp_path / "config.json")],
                          capture_output=True, text=True, env=env, cwd=ROOT)


def test_held_out_file_matches_its_recorded_checksum(tmp_path):
    p = run(tmp_path, F_SHA256)
    assert "doesn't match" not in p.stderr  # gets past the check (then stops: no key, no conditions)


def test_runner_refuses_a_changed_input(tmp_path):
    p = run(tmp_path, "0" * 64)
    assert p.returncode != 0 and "doesn't match the recorded" in p.stderr and "not starting" in p.stderr
