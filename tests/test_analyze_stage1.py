"""Tests for scripts/analyze_stage1.py's statistics, against values worked
out by hand or published in the exploratory phase."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "scripts"))
import analyze_stage1 as A  # noqa: E402


def test_fisher_matches_spike_32_report():
    # exploratory@0277caf:experiments/spike-32/README.md: 13/20 vs 5/20, p = 0.025
    assert round(A.fisher(13, 7, 5, 15), 3) == 0.025
    assert A.fisher(13, 7, 0, 20) < 0.0001


def test_fisher_identical_groups_is_1():
    assert A.fisher(5, 5, 5, 5) == 1.0


def test_wilson_interval():
    assert A.wilson(13, 20) == (0.433, 0.819)
    assert A.wilson(0, 20) == (0.0, 0.161)


def test_mann_whitney_separated_and_identical():
    u, p = A.mann_whitney([0.0] * 20, [0.05 + i / 100 for i in range(20)])
    assert u == 0 and p < 1e-6
    assert A.mann_whitney([0.1, 0.2], [0.1, 0.2])[1] == 1.0


def row(request, i, rate=0.0, **kw):
    r = {"run": f"{request}-r{i}", "request": request, "outcome": "sheet", "error_rate": rate,
         "upload_checksum_computed": False, "row_checksums_by_code": False, "invented_checksums": False,
         "code_on_upload": False, "code_tool_found": False}
    r.update(kw)
    return r


def test_analysis_counts_no_sheet_sessions_but_leaves_them_out_of_the_rate():
    rows = [row("base", i, 0.06) for i in range(18)] + [row("base", 99, outcome="refused", error_rate=None)]
    rows += [row("fix", i, 0.0, upload_checksum_computed=i < 13) for i in range(20)]
    rows += [row("fix-hint", i, 0.0) for i in range(20)]
    res = A.analyze(rows)
    assert res["described"]["base"]["sessions"] == 19
    assert res["described"]["base"]["error_rate"]["n"] == 18
    assert res["described"]["base"]["outcomes"] == {"sheet": 18, "refused": 1}
    assert res["main (fix vs base)"]["M1 error rate"]["significant"]
    m2 = res["main (fix vs base)"]["M2 upload checksum computed"]
    assert m2["a"] == "13/20" and m2["b"] == "0/19" and m2["significant"]
