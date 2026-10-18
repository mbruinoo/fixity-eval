"""Tests for scripts/hallu_score.py: SPEC.md's worked examples, the grading
rules in decisions/2026-10-18-02-grading-rules.md and the reading rules in
decisions/2026-10-18-03-reading-outputs.md.

Run with: python -m pytest tests
"""
import csv
import hashlib
import io
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "scripts"))
import hallu_score as H  # noqa: E402

HEADER = ["Object Date", "Title", "Object Number", "Link Resource"]


def link(n):
    return f"http://www.metmuseum.org/art/collection/search/{n}"


# 100 graded characters (date + title + object number), as in SPEC.md §1.
SPEC_ROWS = [
    ["ca. 1928", "René", "1.1", link(1001)],                      # 15
    ["1635–45", "Plate", "2.2", link(1002)],                      # 15
    ["1760", "Vase", "3.3", link(1003)],                          # 11
    ["", "", "4.4", link(1004)],                                  # 3
    ["1900", "Landscape with two horses.", "5.5", link(1005)],    # 33
    ["1850", "Portrait of Anna", "6.6", link(1006)],              # 23
]


def tsv(rows, header=HEADER):
    return "\n".join("\t".join(r) for r in [header] + rows) + "\n"


def make_input(tmp_path, rows=SPEC_ROWS):
    p = tmp_path / "met_inventory.tsv"
    p.write_text(tsv(rows), encoding="utf-8")
    return p


def make_run(tmp_path, files, response="", meta=None, requests=None):
    """A run folder: output_files/{name: text}, response.md, meta.json, and
    optionally request_1.json holding the session's messages."""
    d = tmp_path / "runs" / "x-r1"
    (d / "output_files").mkdir(parents=True)
    for name, text in files.items():
        (d / "output_files" / name).write_text(text, encoding="utf-8")
    (d / "response.md").write_text(response, encoding="utf-8")
    (d / "meta.json").write_text(json.dumps(meta or {}))
    if requests is not None:
        (d / "request_1.json").write_text(json.dumps({"messages": requests}))
    return d


def changed(rows, i, col, value):
    out = [list(r) for r in rows]
    out[i][HEADER.index(col)] = value
    return out


def score(tmp_path, out_rows, **kw):
    inp = make_input(tmp_path, kw.pop("input_rows", SPEC_ROWS))
    run = make_run(tmp_path, {"met_inventory_standardized.tsv": tsv(out_rows, kw.pop("header", HEADER))}, **kw)
    return H.score_run(run, inp)


def test_spec_rows_have_100_graded_characters(tmp_path):
    assert score(tmp_path, SPEC_ROWS)["input_chars"] == 100


# SPEC.md §1, worked examples on a 100-character input

def test_spec_reformat_is_free(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 1, "Object Date", "1635-1645"))
    assert r["fixity_error_rate"] == 0.0


def test_spec_dropped_accent(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 0, "Title", "Rene"))
    assert r["fixity_error_rate"] == 0.0025  # 0.25 x 1 character / 100


def test_spec_dropped_qualifier(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 0, "Object Date", "1928"))
    assert r["fixity_error_rate"] == 0.04  # "ca. " = 4 characters


def test_spec_missing_row(tmp_path):
    r = score(tmp_path, SPEC_ROWS[:5])
    assert r["missing_rows"] == 1
    assert r["fixity_error_rate"] == 0.23  # its link isn't counted (record 02, e)


def test_spec_invented_row(tmp_path):
    r = score(tmp_path, SPEC_ROWS + [["1999", "y" * 33, "9.9", link(9999)]])
    assert r["invented_rows"] == 1
    assert r["fixity_error_rate"] == round(40 / 140, 4)


# Grading rules (record 02)

def test_a_object_number_dash_is_free_but_recorded(tmp_path):
    rows = changed(SPEC_ROWS, 2, "Object Number", "14.40.872a–c")
    r = score(tmp_path, changed(rows, 2, "Object Number", "14.40.872a-c"), input_rows=rows)
    assert r["fixity_error_rate"] == 0.0
    assert [c["tier"] for c in r["changes"] if c["column"] == "Object Number"] == [3]


def test_b_letter_case_is_free_but_recorded(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 5, "Title", "PORTRAIT OF ANNA"))
    assert r["fixity_error_rate"] == 0.0
    assert [c["tier"] for c in r["changes"] if c["column"] == "Title"] == [3]


def test_c1_reversed_date_range_counts(tmp_path):
    rows = changed(SPEC_ROWS, 2, "Object Date", "1760–1770")
    r = score(tmp_path, changed(rows, 2, "Object Date", "1770–1760"), input_rows=rows)
    assert [c["tier"] for c in r["changes"] if c["column"] == "Object Date"] == [1]
    assert r["fixity_error_rate"] > 0


def test_c1_reordered_title_words_count(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 5, "Title", "Anna of Portrait"))
    assert r["rows_by_tier"]["tier1_content"] == 1


@pytest.mark.parametrize("out", ["Sand-file|擦條", "Sand-file | 擦條", "Sand-file｜擦條"])
def test_c2_swapped_sides_of_the_bar_are_free(tmp_path, out):
    rows = changed(SPEC_ROWS, 1, "Title", "擦條|Sand-file")
    r = score(tmp_path, changed(rows, 1, "Title", out), input_rows=rows)
    assert r["fixity_error_rate"] == 0.0


def test_c2_dropping_one_side_of_the_bar_counts(tmp_path):
    rows = changed(SPEC_ROWS, 1, "Title", "擦條|Sand-file")
    r = score(tmp_path, changed(rows, 1, "Title", "Sand-file"), input_rows=rows)
    assert r["rows_by_tier"]["tier1_content"] == 1


@pytest.mark.parametrize("placeholder", ["[No title]", "Untitled", "Unknown"])
def test_d_placeholder_in_blank_title_is_slight(tmp_path, placeholder):
    r = score(tmp_path, changed(SPEC_ROWS, 3, "Title", placeholder))
    n = len(placeholder)
    assert [c["tier"] for c in r["changes"] if c["column"] == "Title"] == [2]
    assert r["fixity_error_rate"] == round(0.25 * n / (100 + 0.25 * n), 4)


def test_d_placeholder_in_blank_date_is_free(tmp_path):
    # Not decided in record 02; left as the exploratory scorer had it.
    r = score(tmp_path, changed(SPEC_ROWS, 3, "Object Date", "n.d."))
    assert r["fixity_error_rate"] == 0.0


def test_f_changed_characters_are_lost_and_invented(tmp_path):
    r = score(tmp_path, changed(SPEC_ROWS, 2, "Object Date", "1850"))
    c = [c for c in r["changes"] if c["column"] == "Object Date"][0]
    # "1760" -> "1850": "1" and "0" survive; "76" lost, "85" invented
    assert (c["lost_chars"], c["fabricated_chars"]) == (2, 2)
    assert r["fixity_error_rate"] == round(4 / 102, 4)


# The placeholder bug: titles that merely start with "No", "Unknown", "Untitled"

@pytest.mark.parametrize("title,out", [("Nocturne", ""), ("Nocturne", "November"),
                                       ("Northern Landscape", "Landscape"),
                                       ("Untitled (study of a horse)", "Untitled")])
def test_titles_starting_like_placeholders_are_graded(tmp_path, title, out):
    rows = changed(SPEC_ROWS, 5, "Title", title)
    r = score(tmp_path, changed(rows, 5, "Title", out), input_rows=rows)
    assert r["rows_by_tier"]["tier1_content"] == 1


# Reading outputs (record 03)

def test_a_original_copy_is_not_scored_as_the_result(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {
        "met_inventory_ORIGINAL.tsv": tsv(SPEC_ROWS).replace("René", "Rene"),  # a typed-out "original"
        "met_inventory_standardized.tsv": tsv(changed(SPEC_ROWS, 0, "Object Date", "1928")),
        "zz_unchanged_copy.tsv": tsv(SPEC_ROWS),
    })
    r = H.score_run(run, inp)
    assert r["result_file"] == "met_inventory_standardized.tsv"
    assert r["fixity_error_rate"] == 0.04


def test_a_byte_identical_copy_is_left_out(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {"a_copy.tsv": inp.read_text(encoding="utf-8"),
                              "b_result.tsv": tsv(changed(SPEC_ROWS, 0, "Object Date", "1928"))})
    assert H.score_run(run, inp)["result_file"] == "b_result.tsv"


def test_a_only_an_identical_copy_scores_zero(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {"standardized.tsv": inp.read_text(encoding="utf-8")})
    r = H.score_run(run, inp)
    assert r["outcome"] == "sheet" and r["fixity_error_rate"] == 0.0


def test_a_copy_named_like_the_upload_is_not_the_result(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {"inventory.tsv": tsv(SPEC_ROWS).replace("René", "Rene"),
                              "inventory_standardized.tsv": tsv(changed(SPEC_ROWS, 0, "Object Date", "1928"))},
                   meta={"condition": {"filename": "inventory.tsv"}})
    assert H.score_run(run, inp)["result_file"] == "inventory_standardized.tsv"


def test_a_unchanged_result_beats_a_typed_copy_of_the_original(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {"inventory.tsv": tsv(SPEC_ROWS).replace("René", "Rene"),
                              "inventory_standardized.tsv": inp.read_text(encoding="utf-8")},
                   meta={"condition": {"filename": "inventory.tsv"}})
    r = H.score_run(run, inp)
    assert r["result_file"] == "inventory_standardized.tsv" and r["fixity_error_rate"] == 0.0


def test_a_tie_is_flagged_for_review(tmp_path):
    inp = make_input(tmp_path)
    run = make_run(tmp_path, {"one.tsv": tsv(changed(SPEC_ROWS, 0, "Object Date", "1928")),
                              "two.tsv": tsv(changed(SPEC_ROWS, 0, "Title", "Rene"))})
    r = H.score_run(run, inp)
    assert r["needs_review"] is True
    assert sorted(t["file"] for t in r["result_tie"]) == ["one.tsv", "two.tsv"]


def test_b_every_cell_in_quotes_is_read(tmp_path):
    buf = io.StringIO()
    csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_ALL, lineterminator="\n").writerows([HEADER] + SPEC_ROWS)
    inp = make_input(tmp_path)
    r = H.score_run(make_run(tmp_path, {"standardized.tsv": buf.getvalue()}), inp)
    assert r["fixity_error_rate"] == 0.0 and r["missing_rows"] == 0


def test_b_a_stray_quote_does_not_swallow_rows(tmp_path):
    out = changed(SPEC_ROWS, 4, "Title", '"Landscape with two horses.')
    r = score(tmp_path, out)
    assert r["missing_rows"] == 0 and r["parse"] == "no quotes"


def test_c_original_column_found_by_exact_name(tmp_path):
    header = ["Date (standardized)"] + HEADER
    out = [[r[0].replace("ca. ", "")] + r for r in SPEC_ROWS]  # years the source supports
    r = score(tmp_path, out, header=header)
    assert r["fixity_error_rate"] == 0.0
    assert r["added_columns"] == ["Date (standardized)"]


def row_sha256(row):
    return hashlib.sha256("\t".join(row).encode("utf-8")).hexdigest()


def test_c_accurate_row_checksum_is_free(tmp_path):
    header = HEADER + ["SHA-256"]
    out = [r + [row_sha256(r)] for r in SPEC_ROWS]
    r = score(tmp_path, out, header=header)
    assert r["fixity_error_rate"] == 0.0 and r["added_cells_inaccurate"] == 0


def test_c_short_row_fingerprint_is_free(tmp_path):
    header = HEADER + ["fingerprint"]
    out = [r + [row_sha256(r)[:7]] for r in SPEC_ROWS]
    assert score(tmp_path, out, header=header)["added_cells_inaccurate"] == 0


def test_c_typed_wrong_checksum_counts_as_invented(tmp_path):
    header = HEADER + ["SHA-256"]
    fake = "ab" * 32
    out = [r + [fake] for r in SPEC_ROWS[:1]] + [r + [row_sha256(r)] for r in SPEC_ROWS[1:]]
    text = tsv(out, header)
    typed = [{"role": "assistant", "content": [
        {"type": "tool_use", "id": "t1", "name": "create_file",
         "input": {"path": "/mnt/user-data/outputs/met_inventory_standardized.tsv", "file_text": text}}]}]
    r = score(tmp_path, out, header=header, requests=typed)
    assert r["added_cells_inaccurate"] == 1
    assert r["fixity_error_rate"] == round(64 / 164, 4)


def test_c_wrong_checksum_written_by_code_is_unverified(tmp_path):
    header = HEADER + ["SHA-256"]
    out = [r + ["cd" * 32] for r in SPEC_ROWS[:1]] + [r + [row_sha256(r)] for r in SPEC_ROWS[1:]]
    r = score(tmp_path, out, header=header, requests=[])
    assert r["added_cells_inaccurate"] == 0 and r["added_cells_unverified"] == 1
    assert r["fixity_error_rate"] == 0.0


def test_c_checksum_printed_by_a_tool_first_is_accurate(tmp_path):
    header = HEADER + ["checksum"]
    h = "ef" * 32
    out = [r + [h] for r in SPEC_ROWS[:1]] + [r + [row_sha256(r)] for r in SPEC_ROWS[1:]]
    msgs = [{"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "bash",
                                               "input": {"command": "python3 hash_rows.py"}}]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": h}]}]
    assert score(tmp_path, out, header=header, requests=msgs)["added_cells_inaccurate"] == 0


@pytest.mark.parametrize("year,bad", [("1928", 0), ("1925", 0), ("1700", 1)])
def test_c_years_in_an_added_date_column(tmp_path, year, bad):
    header = HEADER + ["Start Year"]
    out = [r + [year if i == 0 else ""] for i, r in enumerate(SPEC_ROWS)]  # row 0 is "ca. 1928"
    r = score(tmp_path, out, header=header)
    assert r["added_cells_inaccurate"] == bad
    assert (r["fixity_error_rate"] > 0) == bool(bad)


def test_c_new_words_in_an_added_column_are_flagged_not_scored(tmp_path):
    header = HEADER + ["Artist"]
    out = [r + ["Rembrandt" if i == 0 else ""] for i, r in enumerate(SPEC_ROWS)]
    r = score(tmp_path, out, header=header)
    assert r["added_cells_unverified"] == 1 and r["fixity_error_rate"] == 0.0


@pytest.mark.parametrize("reply,meta,expected", [
    ("Could you clarify which date format you'd like?", {}, "asked_clarifying_question"),
    ("I can't standardize this file.", {}, "refused"),
    ("Without instructions I cannot change your data. Please tell me what to standardize.", {},
     "asked_clarifying_question"),
    ("Working on it", {"capped": True}, "cut_off"),
    ("Working on it", {"aborted": "RuntimeError: tool"}, "setup_fault"),
    ("I've standardized the file.", {}, "no_sheet"),
])
def test_d_sessions_without_a_sheet(tmp_path, reply, meta, expected):
    inp = make_input(tmp_path)
    r = H.score_run(make_run(tmp_path, {}, response=reply, meta=meta), inp)
    assert r["outcome"] == expected
    assert r["needs_review"] == (expected in ("refused", "asked_clarifying_question"))
    assert "fixity_error_rate" not in r


def test_table_in_reply_is_scored(tmp_path):
    rows = SPEC_ROWS * 4  # more than 20 rows: duplicates count as invented
    md = "\n".join("| " + " | ".join(r) + " |" for r in [HEADER, ["---"] * 4] + rows)
    inp = make_input(tmp_path)
    r = H.score_run(make_run(tmp_path, {}, response=md), inp)
    assert r["output"] == "table in reply" and r["invented_rows"] == 18


# General properties

def test_rate_stays_between_0_and_1(tmp_path):
    junk = [["2000", "z" * 300, f"{i}.{i}", link(5000 + i)] for i in range(10)]
    r = score(tmp_path, junk)
    assert 0 <= r["fixity_error_rate"] <= 1


def test_scoring_is_deterministic(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    out = changed(changed(SPEC_ROWS, 0, "Title", "Rene"), 2, "Object Date", "1850")
    a = score(tmp_path / "a", out)
    b = score(tmp_path / "b", out)
    assert a["fixity_error_rate"] == b["fixity_error_rate"] and a["changes"] == b["changes"]


def test_fixity_rate_recomputes_from_changes_csv(tmp_path):
    out = changed(changed(SPEC_ROWS, 0, "Title", "Rene"), 2, "Object Date", "1850")
    r = score(tmp_path, out)
    H.write_changes(tmp_path / "changes.csv", [dict(r, run="x-r1")])
    rows = list(csv.DictReader(open(tmp_path / "changes.csv", encoding="utf-8")))
    recomputed = H.fixity_error_rate(
        [{"column": c["column"], "kind": c["kind"], "tier": int(c["tier"]) if c["tier"] else None,
          "lost_chars": int(c["lost_chars"]), "fabricated_chars": int(c["fabricated_chars"])} for c in rows],
        r["input_chars"])
    assert recomputed == r["fixity_error_rate"]
