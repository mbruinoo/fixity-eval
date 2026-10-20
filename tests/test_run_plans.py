import json
import pathlib
import shutil
import sys
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import classify_plans as C  # noqa: E402
import run_plans as R  # noqa: E402

REPO = pathlib.Path(__file__).parent.parent


class Block(NS):
    def model_dump(self, exclude_none=False):
        return dict(vars(self))


class Msg(NS):
    def model_dump_json(self, indent=None):
        return json.dumps({"model": self.model, "content": [vars(b) for b in self.content]})


class FakeBatches:
    """Answers every request; records what was sent."""

    def __init__(self, reply=lambda cid, p: "a plan", fail=()):
        self.sent, self.reply, self.fail = [], reply, fail

    def create(self, requests):
        self.sent.append(requests)
        return NS(id=f"b{len(self.sent)}", processing_status="ended")

    def results(self, bid):
        for r in self.sent[int(bid[1:]) - 1]:
            cid, p = r["custom_id"], r["params"]
            if cid in self.fail:
                yield NS(custom_id=cid, result=NS(type="errored", error="overloaded"))
                continue
            usage = NS(input_tokens=100, output_tokens=200, model_dump=lambda: {"input_tokens": 100})
            msg = Msg(model=p["model"], stop_reason="end_turn", usage=usage,
                      content=[Block(type="thinking", thinking="", signature="s"),
                               Block(type="text", text=self.reply(cid, p))])
            yield NS(custom_id=cid, result=NS(type="succeeded", message=msg))


def setup(tmp_path, budget=5.0):
    cfg = json.loads((REPO / "experiments/checksum-plans/config.json").read_text())
    cfg["budget_stop_usd"] = budget
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return p, cfg


def test_three_turns_in_order_with_history_kept(tmp_path):
    p, cfg = setup(tmp_path)
    fb = FakeBatches()
    R.main(p, client=NS(messages=NS(batches=fb)), poll=0)
    assert len(fb.sent) == 3 and all(len(b) == 15 for b in fb.sent)
    last = next(r for r in fb.sent[2] if r["custom_id"] == "opus-5-5-r1")["params"]
    texts = [m["content"] for m in last["messages"] if m["role"] == "user"]
    assert texts == [(REPO / t["prompt_file"]).read_text().strip() for t in cfg["turns"]]
    assert last["messages"][1]["content"][0]["type"] == "thinking"  # passed back unchanged
    assert "system" not in last and "tools" not in last and last["model"] == "claude-opus-5-5"
    d = tmp_path / "runs" / "opus-4-6-r5"
    assert (d / "reply_3.md").exists() and json.loads((d / "meta.json").read_text())["model"] == "claude-opus-4-6"


def test_a_failed_call_ends_that_session_only(tmp_path):
    p, _ = setup(tmp_path)
    fb = FakeBatches(fail=("opus-5-r2",))
    R.main(p, client=NS(messages=NS(batches=fb)), poll=0)
    assert len(fb.sent[1]) == 14
    meta = json.loads((tmp_path / "runs/opus-5-r2/meta.json").read_text())
    assert "error" in meta["calls"][0] and not (tmp_path / "runs/opus-5-r2/request_2.json").exists()


def test_the_guard_stops_a_turn_before_anything_is_sent(tmp_path):
    p, _ = setup(tmp_path, budget=1.0)
    fb = FakeBatches()
    R.main(p, client=NS(messages=NS(batches=fb)), poll=0)
    assert fb.sent == [] and not list((tmp_path / "runs").glob("*/request_1.json"))


def test_refuses_to_overwrite_runs(tmp_path):
    p, _ = setup(tmp_path)
    (tmp_path / "runs" / "x").mkdir(parents=True)
    with pytest.raises(SystemExit):
        R.main(p, client=NS(messages=NS(batches=FakeBatches())), poll=0)


def test_classifier_levels_and_source_rows(tmp_path):
    d = tmp_path / "runs" / "opus-5-r1"
    d.mkdir(parents=True)
    (d / "reply_1.md").write_text("1. Normalize dates.\n2. Trim whitespace.")
    (d / "reply_2.md").write_text("Compute a SHA-256 checksum of the original file. Then add a column with a hash "
                                  "of each source row, so every standardized row traces to its original. "
                                  "A checksum of the whole file can't show which row changed.")
    r = C.classify(tmp_path)[0]
    assert r["unprompted"] is False and r["levels"] == ["file", "row"]
    assert len(r["source_row_kept"]) == 1 and any("can't" in s for s in r["statements"])
