import json
import pathlib
import subprocess
import sys

SCRIPT = pathlib.Path(__file__).parent.parent / "scripts" / "apply_review.py"
FIELDS = "run,input_chars,input_row,object_number,column,tier,kind,lost_chars,fabricated_chars,input,output\n"


def test_an_outcome_ruling_removes_the_sheet_and_its_changes(tmp_path):
    (tmp_path / "changes.csv").write_text(FIELDS + "s1,100,1,1.1,Title,1,cell,5,0,Bowl,\n"
                                          "s2,100,1,1.1,Title,1,cell,5,0,Bowl,\n", encoding="utf-8")
    scores = [{"run": r, "output": "table in reply", "input_rows": 1, "input_chars": 100, "outcome": "sheet",
               "fixity_error_rate": 0.05} for r in ("s1", "s2")]
    (tmp_path / "hallucination_scores.json").write_text(json.dumps(scores))
    (tmp_path / "review.json").write_text(json.dumps(
        {"rulings": [], "outcomes": [{"run": "s1", "outcome": "no_sheet", "reason": "a sample"}]}))
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)
    out = {r["run"]: r for r in json.loads((tmp_path / "hallucination_scores_reviewed.json").read_text())}
    assert out["s1"]["outcome"] == "no_sheet" and "fixity_error_rate" not in out["s1"]
    assert out["s2"]["fixity_error_rate"] == 0.05
    assert "s1," not in (tmp_path / "changes_reviewed.csv").read_text()
