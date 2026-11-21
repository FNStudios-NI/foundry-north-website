# Tests for where_am_i.py. Each test builds a fresh project in a temp folder
# from the template's own files (conftest.py says how), adds the files a stage
# needs, and runs the tool as Rhys would.
# The first three hold the readings from before runs were numbered;
# the next walk numbered runs through signed, run, review and ready;
# the last hold the lines said after the stage and the desks: his time, the
# Python, the remote, and how full the conversation is; and the very last, the
# dash reaching a pipe whole.
# Every run is given a --zone-file in its own temp folder: his real
# his-time-zone.txt is never made, read or written by a test.
# Every run is of a copy of the tool with no harvest.py beside it (tool_copy): a house's own harvest.py --count line belongs to it, not to these tests (the master's 11:59 line, 12 Nov 2026).

import datetime
import importlib.util
import json
import re
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parent.parent.parent
TOOL = TEMPLATE / "tools" / "where_am_i.py"
# The tool prints a dash; both sides read and write it as UTF-8, whatever the console.
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
# A test run from inside a session must not read that session's own log.
ENV.pop("CLAUDE_CODE_SESSION_ID", None)

# The tool loaded in this process too, so his time and the Python can be read with a clock and a PATH the test controls.
_spec = importlib.util.spec_from_file_location("where_am_i_for_tests", TOOL)
where = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(where)


@pytest.fixture(scope="session", autouse=True)
def tool_copy(tmp_path_factory):
    """Copy the tool and the neighbours it loads (upgrade.py, and status.py beside that) into a folder of their own;
    every run is of that copy."""
    global TOOL
    folder = tmp_path_factory.mktemp("tool")
    for name in ("where_am_i.py", "upgrade.py", "status.py"):
        shutil.copy2(TOOL.parent / name, folder / name)
    TOOL = folder / "where_am_i.py"


@pytest.fixture
def project(fresh_project):
    return fresh_project


def no_zone(project):
    """Point the tool at a zone file in the test's own folder, so no test reads his real one.
    A test that gives its own --zone-file after these words is read with that one: the last one wins."""
    return ("--zone-file", str(project.parent / "no-zone.txt"))


def put(project, path, text="x\n"):
    file = project / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")


def close(project, n):
    decisions = project / "docs" / "decisions.md"
    decisions.write_text(decisions.read_text(encoding="utf-8") + f"\n## Run {n} closed\n", encoding="utf-8")


def first_line(project, *extra):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *no_zone(project), *extra],
                          capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert done.returncode == 0, done.stderr
    return done.stdout.splitlines()[0]


def as_json(project, *extra):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), "--json", *no_zone(project), *extra],
                          capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def said(project, *extra, env=ENV):
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *no_zone(project), *extra],
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
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *no_zone(project)], capture_output=True, text=True, encoding="utf-8", env=ENV)
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
AT_110K = "conversation: 11% full (110,000 of 1,000,000 tokens; hand over at 450,000)"


def test_no_remote_is_said_for_a_repository_with_none(project):
    git(project, "init", "-q")
    assert NO_REMOTE in said(project)
    assert as_json(project)["remote"] is False


def test_no_remote_is_said_for_a_folder_that_is_no_repository(project):
    assert NO_REMOTE in said(project)


def test_nothing_is_said_of_the_remote_once_one_is_set(project):
    git(project, "init", "-q")
    git(project, "remote", "add", "origin", str(project.parent / "none.git"))
    # the remote's own lines only: the his-time line names a temp folder called after this test
    assert not [line for line in said(project) if line.startswith(("remote", "no remote"))]
    assert as_json(project)["remote"] is True


def test_a_log_at_110000_reads_11_full_of_a_million_whatever_the_model(project):
    at = log(project, reply(20000, 60000, 30000, model="claude-opus-5-5"))
    assert said(project, *at)[-3] ==AT_110K
    assert as_json(project, *at)["conversation"] == {"used": 110000, "window": 1000000, "percent": 11,
                                                     "hand_over_at": 450000}
    # the session's id can come from the environment instead
    assert said(project, *at[:2], env={**ENV, "CLAUDE_CODE_SESSION_ID": "s1"})[-3] ==AT_110K


def test_a_helpers_line_is_left_out_of_the_count(project):
    at = log(project, reply(20000, 60000, 30000), reply(1000, 2000, 3000, helper=True))
    assert said(project, *at)[-3] ==AT_110K


def test_the_window_is_one_million_or_the_one_named(project):
    at = log(project, reply(100000, 200000, 200000, model="claude-opus-5-5[1m]"))
    assert said(project, *at)[-3] =="conversation: 50% full (500,000 of 1,000,000 tokens; hand over at 450,000)"
    assert said(project, *at, "--window", "2000000")[-3] =="conversation: 25% full (500,000 of 2,000,000 tokens; hand over at 450,000)"


def test_no_session_id_reads_not_read(project):
    assert said(project)[-3] =="conversation: not read (no session id)"
    assert as_json(project)["conversation"] is None
    at = log(project, json.dumps({"type": "user"}))
    assert said(project, *at)[-3] =="conversation: not read (no reply in the log)"
    assert said(project, *at[:2], "--session", "s2")[-3] =="conversation: not read (no log for this session)"


# His time and the Python, said after the desks and before the remote.

# One reading of the clock, in UTC, that the tests hold still: 02:30 on Wed 28 Oct 2026.
NOW = datetime.datetime(2026, 10, 28, 2, 30, tzinfo=datetime.timezone.utc)
HIS_TIME = re.compile(r"his time: (\d\d):(\d\d), \w{3} \d{1,2} \w{3} \(UTC\+8\) · this computer \d\d:\d\d")


def zone(project, line):
    """Write a zone file beside the project; return the words that point the tool at it."""
    put(project.parent, "zone.txt", line)
    return ("--zone-file", str(project.parent / "zone.txt"))


def test_his_time_is_the_utc_clock_plus_his_offset(project):
    computer = f"{NOW.astimezone():%H:%M}"  # this computer's local time, from the same reading
    zone(project, "UTC+8\n")
    assert where.his_time(project.parent / "zone.txt", NOW) == (
        {"time": "10:30", "day": "Wed 28 Oct", "zone": "UTC+8", "computer": computer}, None)
    zone(project, "\n  UTC-5  \n")  # the first non-blank line, spaces dropped
    assert where.his_time(project.parent / "zone.txt", NOW)[0] == {
        "time": "21:30", "day": "Tue 27 Oct", "zone": "UTC-5", "computer": computer}
    zone(project, "\ufeffUTC+05:30\n")  # a half-hour zone, written by Notepad with its mark at the front
    assert where.his_time(project.parent / "zone.txt", NOW)[0] == {
        "time": "08:00", "day": "Wed 28 Oct", "zone": "UTC+5:30", "computer": computer}
    zone(project, "UTC\n")
    assert where.his_time(project.parent / "zone.txt", NOW)[0]["time"] == "02:30"


def test_his_time_line_says_his_time_now(project):
    lines = said(project, *zone(project, "UTC+8\n"))
    found = [m for m in map(HIS_TIME.fullmatch, lines) if m]
    assert found, lines
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    # read a moment apart, so a minute either side is allowed
    assert (now.hour * 60 + now.minute - int(found[0][1]) * 60 - int(found[0][2])) % 1440 in (0, 1, 1439)


def test_no_zone_file_says_not_known(project):
    path = os.path.abspath(project.parent / "no-zone.txt")
    assert f"his time: not known (no zone in {path}; one line such as UTC+8)" in said(project)
    answer = as_json(project)
    assert answer["his_time"] is None
    assert answer["his_time_why"] == f"no zone in {path}; one line such as UTC+8"


def test_a_line_of_another_form_says_not_known(project):
    at = zone(project, "eight hours ahead\nUTC+8\n")
    path = os.path.abspath(at[1])
    assert f'his time: not known ({path} says "eight hours ahead"; one line such as UTC+8)' in said(project, *at)
    for line in ("UTC+8h", "GMT+8", "UTC+99", "UTC+5:75", "UTC 8"):
        zone(project, line + "\n")
        assert where.his_time(at[1], NOW)[0] is None, line


def test_the_python_is_the_first_that_runs_says_3_and_has_pytest():
    names = [["python"], ["python3"], ["py", "-3"], ["python3.12"], ["python3.11"]]
    places = {"python": r"C:\Users\x\AppData\Local\Microsoft\WindowsApps\python.exe",  # the Store's shortcut
              "python3": r"C:\py2\python3.exe", "py": r"C:\Windows\py.exe",
              "python3.12": r"C:\bin\python3.12.exe", "python3.11": r"C:\bin\python3.11.exe"}
    tried = []

    def run(command):
        tried.append(command)
        if command[0] == places["python3"]:
            return (0, "Python 2.7.18\n")
        if command[0] == places["py"]:
            return None  # did not answer in time
        if command[-1] == "import pytest":
            return (0, "") if command[0] == places["python3.11"] else (1, "No module named 'pytest'")
        return (0, "Python 3.12.1\n")

    assert where.find_python(names, which=places.get, run=run) == "python3.11"
    assert not [c for c in tried if c[0] == places["python"]]  # the Store's shortcut is never run
    assert [r"C:\Windows\py.exe", "-3", "--version"] in tried
    assert where.find_python([["py", "-3"]], which=places.get, run=lambda c: (0, "Python 3.11.9\n")) == "py -3"


def test_no_python_with_pytest_is_none_found():
    places = {"python": r"C:\Users\x\AppData\Local\Microsoft\WindowsApps\python.exe", "python3.12": r"C:\bin\python3.12.exe"}

    def run(command):
        return (1, "No module named 'pytest'") if command[-1] == "import pytest" else (0, "Python 3.12.1\n")

    assert where.find_python([["python"], ["python3"], ["python3.12"]], which=places.get, run=run) is None


def test_the_python3_n_names_come_from_the_path_highest_first(tmp_path):
    for name in ("python3.9.exe", "python3.12", "python3.11.exe", "python3.exe", "pythonw.exe"):
        put(tmp_path / "a", name)
    put(tmp_path / "b", "python3.11")
    path = os.pathsep.join([str(tmp_path / "a"), str(tmp_path / "missing"), str(tmp_path / "b")])
    assert where.python_names(path) == [["python"], ["python3"], ["py", "-3"],
                                        ["python3.12"], ["python3.11"], ["python3.9"]]


def test_his_time_and_the_python_come_after_the_desks_and_before_the_remote(project):
    put(project, "desks/web/CLAUDE.md")
    lines = said(project, *zone(project, "UTC+8\n"))
    at = next(i for i, line in enumerate(lines) if line.startswith("desks/web: "))
    assert HIS_TIME.fullmatch(lines[at + 1]), lines
    assert lines[at + 2].startswith("python: "), lines
    assert lines[at + 3:] == [NO_REMOTE, "conversation: not read (no session id)",
                              "template: version not in project.yaml · newest not read", "foundations: none"]


def test_json_carries_his_time_and_the_python(project):
    answer = as_json(project, *zone(project, "UTC-5\n"))
    assert set(answer["his_time"]) == {"time", "day", "zone", "computer"}
    assert answer["his_time"]["zone"] == "UTC-5"
    assert answer["his_time_why"] is None
    assert answer["python"] is None or isinstance(answer["python"], str)


def test_the_dash_reaches_a_pipe_as_utf8_whatever_the_code_page(project):
    put(project, "docs/decisions.md", "## 2026-10-05 — first sheet\n")
    env = {k: v for k, v in ENV.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    done = subprocess.run([sys.executable, "-B", str(TOOL), str(project), *no_zone(project)], capture_output=True, env=env)
    assert done.returncode == 0, done.stderr
    assert b"\xe2\x80\x94" in done.stdout.splitlines()[0]


# The upgrade: the gate on a closed run, the lessons line, the foundations line and
# the house lessons line. Each sample project has docs/lessons.md (unless the
# test is of a project without one), docs/decisions.md and docs/runs/1/.

UPGRADE_TABLE = "| L-numbers | his answer | the line as kept | where it is |\n|---|---|---|---|\n"


def lesson(n, when="2026-11-10 09:00", kind="change", file="CLAUDE.md", line="Read the brief first."):
    return f'- L{n:03d} · {when} · run 1 · {kind} · what happened · file: {file} · "{line}"\n'


def days_ago(n):
    return f"{datetime.date.today() - datetime.timedelta(days=n):%Y-%m-%d} 09:00"


def reviewed(project, lessons=None, rows=None, when="2026-11-11 10:00"):
    """Run 1 through to its review page; closed at `when` when rows is given (a list, or "none" for no block)."""
    put(project, "docs/brief.md")
    put(project, "docs/runs/1/review.html")
    if lessons is not None:
        put(project, "docs/lessons.md", "# Lessons — test\n\n" + "".join(lessons))
    if rows is not None:
        text = f"\n## {when} — Run 1 closed\nThe run is closed.\n"
        if rows != "none":
            text += "\n### The upgrade\n" + UPGRADE_TABLE + "".join(f"| {' | '.join(r)} |\n" for r in rows)
        decisions = project / "docs" / "decisions.md"
        decisions.write_text(decisions.read_text(encoding="utf-8") + text, encoding="utf-8")


def test_a_closed_run_with_no_upgrade_block_reads_the_upgrade_is_not_done(project):
    reviewed(project, [lesson(1), lesson(2)], rows="none")
    assert first_line(project) == "review: run 1 — the upgrade is not done (2 lessons unanswered)"
    answer = as_json(project)
    assert (answer["stage"], answer["run"]) == ("review", 1)


def test_lessons_after_the_close_are_not_counted_in_the_upgrade_gate(project):
    reviewed(project, [lesson(1), lesson(2, when="2026-11-12 09:00")], rows="none")
    assert first_line(project) == "review: run 1 — the upgrade is not done (1 lessons unanswered)"


def test_a_passing_upgrade_block_reads_ready(project):
    put(project, "CLAUDE.md", "# Project\n\nRead the brief first.\n")
    reviewed(project, [lesson(1), lesson(2)],
             rows=[("L001", "keep", "Read the brief first.", "CLAUDE.md"), ("L002", "drop", "", "")])
    assert first_line(project) == "ready: run 2 — plan it"


def test_an_upgrade_block_with_every_row_and_a_fault_names_the_fault(project):
    put(project, "CLAUDE.md", "# Project\n")
    reviewed(project, [lesson(1)], rows=[("L001", "keep", "Read the brief first.", "CLAUDE.md")])
    assert first_line(project) == ("review: run 1 — the upgrade is not done "
                                   "(L001: the line as kept is not in CLAUDE.md)")


def test_without_lessons_file_a_closed_run_with_no_upgrade_block_reads_ready(project):
    reviewed(project, None, rows="none")
    assert first_line(project) == "ready: run 2 — plan it"
    assert not any(line.startswith("lessons:") for line in said(project))
    assert as_json(project)["lessons"] is None


def test_three_lessons_waiting_print_the_lessons_line_with_no_upgrade_due(project):
    reviewed(project, [lesson(n, when=days_ago(13 - n)) for n in (1, 2, 3)])
    lines = said(project)
    oldest = days_ago(12)[:10]
    at = next(i for i, line in enumerate(lines) if line.startswith("conversation:"))
    assert lines[at + 1] == f"lessons: 3 waiting, the oldest {oldest}", lines
    assert as_json(project)["lessons"] == {"waiting": 3, "oldest": oldest, "due": False}


def test_fifteen_lessons_waiting_print_upgrade_due(project):
    reviewed(project, [lesson(n, when=days_ago(1)) for n in range(1, 16)])
    assert f"lessons: 15 waiting, the oldest {days_ago(1)[:10]} · upgrade due" in said(project)
    reviewed(project, [lesson(n, when=days_ago(1)) for n in range(1, 15)])
    assert f"lessons: 14 waiting, the oldest {days_ago(1)[:10]}" in said(project)


def test_one_lesson_14_days_old_prints_upgrade_due(project):
    reviewed(project, [lesson(1, when=days_ago(14))])
    assert f"lessons: 1 waiting, the oldest {days_ago(14)[:10]} · upgrade due" in said(project)
    reviewed(project, [lesson(1, when=days_ago(13))])
    assert f"lessons: 1 waiting, the oldest {days_ago(13)[:10]}" in said(project)


def test_no_lessons_waiting_say_none_waiting(project):
    reviewed(project, [])
    assert "lessons: none waiting" in said(project)


HERO = ("# Hero film — v2.0\n\nVersion: v2.0\n\n## Steps\n"
        "1. **Intake** · `foundation · 1 job` (TetraScale) · the master — in: x — out: y — because.\n"
        "2. **The kit first** · `on trial` · measure: props drawn twice · Opus 5.5 — in: x — out: y — because.\n"
        "3. **Style ideas** · `foundation · 2 jobs` · the master — in: x — out: y — because.\n")


def test_a_new_form_locked_line_in_the_brief_is_never_read_as_a_foundation(project):
    put(project, "docs/brief.md",
        "# Brief\n\nLocked: Hero film v2.0 — docs/hero.md — since 2026-11-05 — proven by L001, L002\n")
    lines = said(project)
    assert "foundations: none" in lines, lines
    assert not any("Locked" in line or "Hero film" in line for line in lines), lines
    assert as_json(project)["foundations"] == []


def test_the_foundation_steps_of_a_workflow_file_print_on_one_foundations_line(project):
    put(project, "docs/brief.md", "# Brief\n\n- Locked: Hero film — docs/hero.md — since 2026-11-05 — proven by L001\n")
    put(project, "desks/hero-film/workflow.md", HERO)
    found = [line for line in said(project) if line.startswith("foundations:")]
    assert found == ["foundations: desks/hero-film/workflow.md step 1 Intake · 1 job; "
                     "desks/hero-film/workflow.md step 3 Style ideas · 2 jobs"], found
    assert as_json(project)["foundations"][0] == {"file": "desks/hero-film/workflow.md", "step": 1,
                                                  "name": "Intake", "jobs": 1}


def test_a_locked_none_brief_reads_as_no_foundation(project):
    put(project, "docs/brief.md", "# Brief\n\nLocked: none\n")
    lines = said(project)
    assert "foundations: none" in lines, lines
    assert not any("none:" in line or "name its file" in line for line in lines), lines
    assert as_json(project)["foundations"] == []


def test_a_workflow_whose_tag_line_is_a_foundation_is_named_on_the_line(project):
    put(project, "docs/method.md", HERO.replace("Version: v2.0\n", "Version: v2.0\nTag: `foundation · 3 jobs`\n")
        .replace("`foundation · 1 job` (TetraScale)", "`idea`").replace("`foundation · 2 jobs`", "`idea`"))
    assert "foundations: docs/method.md · 3 jobs" in said(project)


def harvest_script(project, body):
    script = project.parent / "fake-harvest.py"
    script.write_text(body, encoding="utf-8")
    return ("--harvest", str(script))


def test_a_fake_harvest_house_lessons_line_is_printed(project):
    fake = harvest_script(project, "import sys\nassert sys.argv[1:] == ['--count']\n"
                                   "print('house lessons waiting: 4')\nprint('more')\n")
    assert "house lessons waiting: 4" in said(project, *fake)
    assert as_json(project, *fake)["house_lessons"] == "house lessons waiting: 4"


def test_a_failing_harvest_says_house_lessons_not_read(project):
    fake = harvest_script(project, "raise SystemExit(3)\n")
    assert "house lessons waiting: not read (fake-harvest.py exited 3)" in said(project, *fake)
    fake = harvest_script(project, "print('something else')\n")
    assert 'house lessons waiting: not read (fake-harvest.py said "something else")' in said(project, *fake)


def test_no_harvest_beside_the_tool_says_no_house_lessons(project):
    assert not any(line.startswith("house lessons") for line in said(project))
    assert as_json(project)["house_lessons"] is None


# The template line (his words of 21 Nov 2026, "this needs to be an automatic catch"). conftest.py lets git
# use local files only, so no test reaches the template's home online.

def template_home(folder, *tags):
    """A template's home: template/VERSION and a git repository holding these template/<x.y.z> tags."""
    put(folder, "template/VERSION", "0.0.1\n")
    git(folder, "init", "-q")
    git(folder, "-c", "user.name=test", "-c", "user.email=test@example.invalid", "commit", "-q", "--allow-empty", "-m", "x")
    for tag in tags:
        git(folder, "tag", f"template/{tag}")
    return folder


def on(project, version):
    put(project, "project.yaml", f"name: test\ntemplate_version: {version}\n")


def test_the_template_line_says_update_due_when_behind(project):
    template_home(project.parent / "home", "0.9.1", "0.9.2")
    reviewed(project, [])
    on(project, "0.9.1")
    lines = said(project)
    at = lines.index("lessons: none waiting")
    assert lines[at + 1] == "template: 0.9.1 · newest 0.9.2 · update due", lines   # after the lessons line
    assert as_json(project)["template"] == {"version": "0.9.1", "newest": "0.9.2", "due": True}
    on(project, "0.9.2")
    assert "template: 0.9.2 · newest 0.9.2" in said(project)
    put(project, "project.yaml", "name: test\n")
    assert "template: version not in project.yaml · newest 0.9.2" in said(project)


def test_the_template_line_reads_the_newest_tag_beside_the_project(project):
    on(project, "0.9.1")
    nowhere = str(project.parent / "no-remote")
    # A repository beside it with no template/VERSION is not the template's home.
    template_home(project.parent / "other", "9.9.9")
    (project.parent / "other" / "template" / "VERSION").unlink()
    template_home(project.parent / "home", "0.8.0", "0.9.1")
    state = where.template_state(project, remote=nowhere)
    assert where.template_line(state) == "template: 0.9.1 · newest 0.9.1", state
    # The project folder itself, when it holds template/VERSION, is read first.
    template_home(project, "0.9.0")
    assert where.template_state(project, remote=nowhere)["newest"] == "0.9.0"
    # --template-home names another.
    assert where.template_state(project, home=project.parent / "home", remote=nowhere)["newest"] == "0.9.1"


def test_the_template_line_compares_versions_as_numbers(project):
    template_home(project.parent / "home", "0.10.0", "0.9.2")
    nowhere = str(project.parent / "no-remote")
    on(project, "0.9.2")
    assert where.template_line(where.template_state(project, remote=nowhere)) == "template: 0.9.2 · newest 0.10.0 · update due"
    on(project, "0.10.0")
    assert where.template_line(where.template_state(project, remote=nowhere)) == "template: 0.10.0 · newest 0.10.0"


def test_the_template_line_says_newest_not_read_within_five_seconds(project, monkeypatch):
    # A stand-in remote that never answers: git's ssh is a Python that sleeps, so nothing leaves this machine.
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file:ssh")
    monkeypatch.setenv("GIT_SSH_COMMAND", f'"{Path(sys.executable).as_posix()}" -c "import time; time.sleep(15)"')
    on(project, "0.9.1")
    start = time.monotonic()
    state = where.template_state(project, remote="ssh://stand-in.invalid/home.git")
    took = time.monotonic() - start
    assert state == {"version": "0.9.1", "newest": None, "due": False}
    assert where.template_line(state) == "template: 0.9.1 · newest not read"
    assert 4 <= took < 5.5, took   # it waited for the stand-in, and no more than 5 seconds
