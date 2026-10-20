import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import hallu_score as H  # noqa: E402
import score_claude_ai as S  # noqa: E402


def test_separate_tables_in_a_plain_text_copy_stay_separate(tmp_path):
    t = tmp_path / "transcript.txt"
    sample = "\n".join(f"{i}\tx\t1.{i}\thttp://m/{i}" for i in range(30))
    t.write_text("Issue\tFix\nquotes\tremoved\n\nHere is the file:\n" + sample +
                 "\n\n" + S.DEBRIEF + "\nreply\tquoted\n", encoding="utf-8")
    rows = H.table_from_text(S.replies(t))
    assert len(rows) == 30 and rows[0][0] == "0"


def test_the_debrief_reply_is_left_out(tmp_path):
    t = tmp_path / "transcript.txt"
    t.write_text("before\n" + S.DEBRIEF + " after", encoding="utf-8")
    assert "after" not in S.replies(t)
