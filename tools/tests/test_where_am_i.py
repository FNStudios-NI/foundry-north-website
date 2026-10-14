# Tests for where_am_i.py. Each test builds a fresh project in a temp folder
# from the template's own files (conftest.py says how), adds the files a stage
# needs, and runs the tool as Rhys would.
# The first three hold the readings from before runs were numbered;
# the next walk numbered runs through signed, run, review and ready;
# the last hold the two lines said after the stage and the desks: the remote,
# and how full the conversation is.

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parent.parent.parent
TOOL = TEMPLATE / "tools" / "where_am_i.py"
# The tool prints a dash; both sides read and write it as UTF-8, whatever the console.
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
# A test run from inside a session must not read that session's own log.
ENV.pop("CLAUDE_CODE_SESSION_ID", None)


@pytest.fixture
def project(fresh_project):
    return fresh_project


def put(project, path, text="x\n"):
    file = project / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")


def close(project, n):
    decisions = project / "docs" / "decisions.md"
    decisions.write_text(decisions.read_text(encoding="utf-8") + f"\n## Run {n} closed\n", encoding="utf-8")


def first_line(project, *extra):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *extra],
                          capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert done.returncode == 0, done.stderr
    return done.stdout.splitlines()[0]


def as_json(project, *extra):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), "--json", *extra],
                          capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def said(project, *extra, env=ENV):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *extra],
                          capture_output=True, text=True, encoding="utf-8", env=env)
    assert done.returncode == 0, done.stderr
    return done.stdout.splitlines()


def git(project, *words):
    subprocess.run(["git", "-C", str(project), *words], check=True, capture_output=True)


def reply(sent, read, made, helper=False, model="claude-opus-5-5"):
    return json.dumps({"type": "assistant", "isSidechain": helper, "requestedModel": model,
                       "message": {"usage": {"input_tokens": sent, "cache_read_input_tokens": read,
                                             "cache_creation_input_tokens": made, "output_tokens": 5}}})


def log(project, *lines):
    """Write session s1's log beside the project; return the words that point the tool at it."""
    logs = project.parent / "logs"
    put(logs, "x/s1.jsonl", "".join(line + "\n" for line in lines))
    return ("--logs", str(logs), "--session", "s1")


# The readings that must not change.

def test_new(project):
    assert first_line(project) == "new: start discovery"


def test_fault_brief_missing(project):
    close(project, 1)  # not a dated ruling: still new
    assert first_line(project) == "new: start discovery"
    put(project, "docs/decisions.md", "## 2026-10-05 — first sheet\n")
    assert first_line(project).startswith("fault: rulings exist but docs/brief.md is missing")


def test_discovery(project):
    put(project, "docs/brief.md")
    assert first_line(project) == "discovery: carry on discovery, ending in the plan page for Rhys to sign"
    (project / "docs" / "runs" / "1").mkdir(parents=True)  # a folder with no plan yet
    assert first_line(project).startswith("discovery:")


# Numbered runs.

def test_run_one_through_to_ready(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/plan-signed.md")
    assert first_line(project) == "signed: run 1 — start the run"
    put(project, "docs/runs/1/run.md")
    assert first_line(project).startswith("run: run 1 —")
    put(project, "docs/runs/1/review.html")
    assert first_line(project).startswith("review: run 1 —")
    close(project, 1)
    assert first_line(project) == "ready: run 2 — plan it"


def test_second_run(project):
    put(project, "docs/brief.md")
    for name in ("plan-signed.md", "run.md", "review.html"):
        put(project, f"docs/runs/1/{name}")
    close(project, 1)
    put(project, "docs/runs/2/plan-signed.md")
    assert first_line(project) == "signed: run 2 — start the run"
    close(project, 2)
    assert first_line(project) == "ready: run 3 — plan it"


def test_review_waits_for_its_own_close(project):
    put(project, "docs/brief.md")
    for n in (1, 2):
        for name in ("plan-signed.md", "run.md", "review.html"):
            put(project, f"docs/runs/{n}/{name}")
    close(project, 1)
    assert first_line(project).startswith("review: run 2 —")
    close(project, 12)  # "Run 12 closed" does not close run 2
    assert first_line(project).startswith("review: run 2 —")


def test_newest_folder_by_number_not_by_name(project):
    put(project, "docs/brief.md")
    for n in (2, 10):
        put(project, f"docs/runs/{n}/plan-signed.md")
    assert first_line(project) == "signed: run 10 — start the run"


def test_closed_run_is_never_signed(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/plan-signed.md")
    close(project, 1)
    assert first_line(project) == "ready: run 2 — plan it"


def test_old_paths_are_a_fault(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/plan-signed.md")
    for old in ("docs/plan-signed.md", "docs/run.md", "docs/review.md"):
        copy = project.parent / ("old-" + old.split("/")[-1])
        shutil.copytree(project, copy)
        put(copy, old)
        assert first_line(copy).startswith("fault: run files at the old paths — move them into docs/runs/1/")
    # without a brief too: a project with run files is not new
    (copy / "docs" / "brief.md").unlink()
    assert first_line(copy).startswith("fault: run files at the old paths")


def test_json_ready(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/review.html")
    close(project, 1)
    answer = as_json(project)
    assert answer["stage"] == "ready"
    assert answer["run"] == 2
    assert answer["next"] == "run 2 — plan it"


def test_closed_heading_with_a_date(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/review.html")
    decisions = project / "docs" / "decisions.md"
    decisions.write_text(decisions.read_text(encoding="utf-8")
                         + "\n## 2026-10-07 09:00 — Run 1 closed (master)\n", encoding="utf-8")
    assert first_line(project) == "ready: run 2 — plan it"


def test_desks_read_their_own_runs(project):
    put(project, "docs/brief.md")
    desk = project / "desks" / "web"
    put(desk, "docs/brief.md")
    put(desk, "docs/runs/1/run.md")
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project)], capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert "desks/web: run: run 1 —" in done.stdout


def test_tool_writes_nothing(project):
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/plan-signed.md")
    before = sorted(p.relative_to(project) for p in project.rglob("*"))
    first_line(project)
    as_json(project)
    assert sorted(p.relative_to(project) for p in project.rglob("*")) == before


# After the stage and the desks: the remote, and how full the conversation is.

NO_REMOTE = "no remote: the record is on this machine only"
HALF = "conversation: 50% full (100,000 of 200,000 tokens)"


def test_no_remote_is_said_for_a_repository_with_none(project):
    git(project, "init", "-q")
    assert NO_REMOTE in said(project)
    assert as_json(project)["remote"] is False


def test_no_remote_is_said_for_a_folder_that_is_no_repository(project):
    assert NO_REMOTE in said(project)


def test_nothing_is_said_of_the_remote_once_one_is_set(project):
    git(project, "init", "-q")
    git(project, "remote", "add", "origin", str(project.parent / "none.git"))
    assert not [line for line in said(project) if "remote" in line]
    assert as_json(project)["remote"] is True


def test_a_log_at_half_reads_50_full(project):
    at = log(project, reply(20000, 50000, 30000))
    assert said(project, *at)[-1] == HALF
    assert as_json(project, *at)["conversation"] == {"used": 100000, "window": 200000, "percent": 50}
    # the session's id can come from the environment instead
    assert said(project, *at[:2], env={**ENV, "CLAUDE_CODE_SESSION_ID": "s1"})[-1] == HALF


def test_a_helpers_line_is_left_out_of_the_count(project):
    at = log(project, reply(20000, 50000, 30000), reply(1000, 2000, 3000, helper=True))
    assert said(project, *at)[-1] == HALF


def test_the_window_is_one_million_or_the_one_named(project):
    at = log(project, reply(100000, 200000, 200000, model="claude-opus-5-5[1m]"))
    assert said(project, *at)[-1] == "conversation: 50% full (500,000 of 1,000,000 tokens)"
    assert said(project, *at, "--window", "2000000")[-1] == "conversation: 25% full (500,000 of 2,000,000 tokens)"


def test_no_session_id_reads_not_read(project):
    assert said(project)[-1] == "conversation: not read (no session id)"
    assert as_json(project)["conversation"] is None
    at = log(project, json.dumps({"type": "user"}))
    assert said(project, *at)[-1] == "conversation: not read (no reply in the log)"
    assert said(project, *at[:2], "--session", "s2")[-1] == "conversation: not read (no log for this session)"
