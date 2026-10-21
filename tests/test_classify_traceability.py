"""Tests for scripts/classify_traceability.py (stage 3)."""
import hashlib
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import classify_traceability as C  # noqa: E402
from test_hallu_score import HEADER, SPEC_ROWS, make_input, make_run, tsv  # noqa: E402

ROOT = pathlib.Path(__file__).parents[1]


def experiment(tmp_path, files, response="", requests=None):
    inp = make_input(tmp_path)
    make_run(tmp_path, files, response=response, requests=requests)  # tmp_path/runs/x-r1
    (tmp_path / "config.json").write_text(json.dumps(
        {"inputs": {"i": str(inp)}, "conditions": [{"id": "x", "input": "i"}]}))
    for s in ("hallu_score", "eval_fixity"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / f"{s}.py"), str(tmp_path)], check=True,
                       capture_output=True)
    return C.classify(tmp_path)[0]


def test_original_values_in_an_added_column_are_found(tmp_path):
    header = HEADER + ["Original Title"]
    out = [r + [r[1]] for r in SPEC_ROWS]
    r = experiment(tmp_path, {"met_inventory_standardized.tsv": tsv(out, header)})
    assert r["original_values_kept"] == ["Original Title"]
    assert r["object_numbers_intact"] == 1.0


def test_real_row_fingerprints_and_statements(tmp_path):
    real = [hashlib.sha256("\t".join(r).encode("utf-8")).hexdigest() for r in SPEC_ROWS]
    report = "\n".join(real)
    msgs = [{"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "bash",
                                               "input": {"command": "python3 rows.py"}}]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": report}]}]
    reply = "A file can't contain its own checksum, so I made a checksum for each row instead."
    r = experiment(tmp_path, {"met_inventory_standardized.tsv": tsv(SPEC_ROWS), "rows.txt": report},
                   response=reply, requests=msgs)
    assert r["row_fingerprints_real"] is True and r["row_fingerprints_invented"] is False
    assert r["statements"] == [reply.split(" so ")[0] + " so I made a checksum for each row instead."]


def test_invented_row_fingerprints(tmp_path):
    header = HEADER + ["Row SHA-256"]
    out = [r + ["ab" * 32] for r in SPEC_ROWS]
    text = tsv(out, header)
    typed = [{"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "create_file",
                                                "input": {"path": "x.tsv", "file_text": text}}]}]
    r = experiment(tmp_path, {"met_inventory_standardized.tsv": text}, requests=typed)
    assert r["row_fingerprints_invented"] is True and r["row_fingerprints_real"] is False
