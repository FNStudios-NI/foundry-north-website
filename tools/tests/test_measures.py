# Tests for measures.py. Each test makes up a project (a run folder with
# run.md and plan-signed.md, the landed cards' own files and, where a test
# closes the run, docs/decisions.md) and a folder of session logs under
# tmp_path, then runs the tool on them as the master would at the review.
# No real run record, card, decision or log is read.

import datetime as dt
import json
import os
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "measures.py")
PROJECT = "demo-project"
MAIN = "C:\\Users\\someone\\Projects\\" + PROJECT
WORKTREES = "C:\\Users\\someone\\.t3\\worktrees\\" + PROJECT + "\\"

RECORD = """# Run 9 — demo-project

## Go
- Start: 2026-10-07 05:00
- Planned end: 2026-10-07 09:00

## Unforeseen key points
One line per key point nobody saw coming.
- 06:10 · the page server stopped · restarted it

## Blockers
Work that cannot go on without him.
- 07:00 · his act A1 not done · waits for him
- 07:05 · the laptop is off · waits for him

## Merges
One line per merge into the try-it build, with its undo.
- 05:40 · template alpha · squash 1111111 · undo: `git revert 1111111`
- 06:20 · road road-beta (with road-beta-2) · squash 2222222 · undo: `git revert 2222222`
- 06:30 · the adopt of 0.9.0 here (the master's, inline) · commit 3333333 · undo: `git revert 3333333`
- 07:10 · template gamma · squash 4444444 · undo: `git revert 4444444`
"""

IT_WORKS = """
## It works
- 08:01 · alpha · pass · ran it on run 2 and read the four headings
- 08:05 · template gamma · fail · the page would not open
"""

PLAN = """# Plan for run 9 — demo-project

## The path
- piece one · template
- piece two · road
- piece three · template
- piece four · proving

## Key points
- K1 · a checked piece joins the main line · c
"""


def stamp(local):
    """A log timestamp, in UTC as Claude Code writes it, for a local clock time."""
    when = dt.datetime.strptime(local, "%Y-%m-%d %H:%M").astimezone()
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def session(logs, name, cwd, branch, first, replies):
    """One made-up session log: a first message, then replies (time, tokens)."""
    folder = logs / name.split("/")[0]
    folder.mkdir(parents=True, exist_ok=True)
    lines = [{"type": "user", "cwd": cwd, "gitBranch": branch, "timestamp": stamp(replies[0][0]),
              "message": {"role": "user", "content": first}}]
    for i, (when, tokens) in enumerate(replies):
        lines.append({"type": "assistant", "cwd": cwd, "gitBranch": branch, "timestamp": stamp(when),
                      "message": {"id": f"{name}-{i}", "model": "claude-opus-5-5",
                                  "usage": {"input_tokens": tokens, "output_tokens": 0,
                                            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}})
    (folder / (name.split("/")[-1] + ".jsonl")).write_text("\n".join(json.dumps(l) for l in lines) + "\n", encoding="utf-8")


def card(tmp_path, folder, name, order):
    """One made-up card file, with the line that carries its order."""
    cards = tmp_path / "project" / folder / "docs" / "cards"
    cards.mkdir(parents=True, exist_ok=True)
    (cards / (name + ".md")).write_text(
        f"# {name}\nLane: full\n\nBranch: `task/demo-project/{name}` · Worktree: T3's · Order: {order}\n\n"
        "## Goal\nThe made-up goal; piece 4 is named here, off the Order line.\n", encoding="utf-8")


def make_run(tmp_path, it_works=True):
    run = tmp_path / "project" / "docs" / "runs" / "9"
    run.mkdir(parents=True)
    (run / "run.md").write_text(RECORD + (IT_WORKS if it_works else ""), encoding="utf-8")
    (run / "plan-signed.md").write_text(PLAN, encoding="utf-8")
    # Each card names its own piece of the plan; delta is the master's own card.
    card(tmp_path, "desks/template", "2026-10-07-alpha", "asks entry `2026-10-07 04:00`, item 1 (run 9, piece 1)")
    card(tmp_path, "desks/road", "2026-10-07-road-beta", "asks entry `2026-10-07 04:00`, item 2 · run 9, piece 2")
    card(tmp_path, "desks/template", "2026-10-07-gamma", "asks entry `2026-10-07 04:00`, piece 3 (round 1)")
    card(tmp_path, ".", "2026-10-07-delta", "run 9's record § Orders, item 4 (run 9, piece 4)")
    logs = tmp_path / "logs"
    logs.mkdir()
    return run, logs


def close_run(tmp_path, page, heading):
    """A decisions page at the project's top with one closing heading."""
    (tmp_path / "project" / "docs" / page).write_text(
        "# Decisions\n\n" + heading + "\n1. His ruling.\n", encoding="utf-8")


def the_usual_sessions(logs):
    # alpha's worker, matched by its branch and folder.
    session(logs, "alpha-worker", WORKTREES + "task-demo-project-2026-10-07-alpha",
            "task/demo-project/2026-10-07-alpha", "desks/template is your folder. You are the worker.",
            [("2026-10-07 05:10", 600)])
    # alpha's checker, at the main checkout, matched by the branch its orders name.
    session(logs, "main/alpha-checker", MAIN, "main",
            "Act as the review sub-agent for this task. Check the branch task/demo-project/2026-10-07-alpha.",
            [("2026-10-07 05:30", 400)])
    # road-beta's worker, whose branch carries the desk's name before the card's.
    session(logs, "beta-worker", WORKTREES + "task-demo-project-2026-10-07-road-beta",
            "task/demo-project/2026-10-07-road-beta", "desks/road is your folder.",
            [("2026-10-07 06:00", 500)])
    session(logs, "master/run", WORKTREES + "t3code-abc", "t3code/abc",
            "<command-message>run</command-message> <command-name>/run</command-name> <command-args>go</command-args>",
            [("2026-10-07 05:01", 1000), ("2026-10-07 07:00", 1000)])
    session(logs, "main/conductor", MAIN, "main", "desks/road is your folder. /conductor — you are the road desk's conductor.",
            [("2026-10-07 05:05", 300)])
    session(logs, "main/probe", MAIN, "main", "This is a test. Reply with one line.",
            [("2026-10-07 05:50", 200)])
    # Another project's session in the same hours: not this run's.
    session(logs, "other/work", "C:\\Users\\someone\\Projects\\studio-os", "main", "/run go",
            [("2026-10-07 05:20", 9999)])


def run_tool(run, logs, until="2026-10-07 09:00"):
    """Run the tool; until=None leaves --until out, so the tool picks the end."""
    done = subprocess.run([sys.executable, TOOL, str(run), "--logs", str(logs)] + (["--until", until] if until else []),
                          capture_output=True, encoding="utf-8")
    assert done.returncode == 0, done.stderr
    assert "Traceback" not in done.stderr
    return done.stdout


def section(out, heading):
    part = out.split("## " + heading + "\n", 1)[1]
    return part.split("\n## ", 1)[0]


def test_it_works_reads_pass_fail_and_not_tried(tmp_path):
    run, logs = make_run(tmp_path)
    out = run_tool(run, logs)
    works = section(out, "It works")
    assert "- template alpha · pass · ran it on run 2 and read the four headings" in works
    assert "- road road-beta · not tried" in works
    assert "- template gamma · fail · the page would not open" in works
    assert "adopt" not in works


def test_a_record_with_no_it_works_reads_not_tried(tmp_path):
    run, logs = make_run(tmp_path, it_works=False)
    works = section(run_tool(run, logs), "It works")
    assert works.count("· not tried") == 3
    assert "pass" not in works and "fail" not in works


def test_usage_per_finished_piece_keeps_cards_masters_conductors_and_the_rest_apart(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    usage = section(run_tool(run, logs), "Usage per finished piece")
    # Total 4000: alpha 1000 (worker and checker), beta 500, masters 2000, conductors 300, the rest 200.
    assert "- template alpha · 1,000 · 25.0% · 2 sessions" in usage
    assert "- road road-beta · 500 · 12.5% · 1 sessions" in usage
    assert "- template gamma · 0 · 0.0% · 0 sessions" in usage
    assert "- masters · 2,000 · 50.0% · 1 sessions" in usage
    assert "- conductors · 300 · 7.5% · 1 sessions" in usage
    assert "- the rest · 200 · 5.0% · 1 sessions" in usage
    assert "- total · 4,000" in usage


def test_a_session_outside_the_runs_time_is_left_out(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    # Before Go (05:00) and after --until (09:00): neither is the run's.
    session(logs, "early-worker", WORKTREES + "task-demo-project-2026-10-06-alpha",
            "task/demo-project/2026-10-06-alpha", "desks/template is your folder.",
            [("2026-10-07 03:00", 7000)])
    session(logs, "master/late", WORKTREES + "t3code-def", "t3code/def", "/run carry on from the handover",
            [("2026-10-07 10:00", 5000)])
    usage = section(run_tool(run, logs), "Usage per finished piece")
    assert "- template alpha · 1,000 · 25.0% · 2 sessions" in usage
    assert "- masters · 2,000 · 50.0% · 1 sessions" in usage
    assert "- total · 4,000" in usage


def test_share_finished_counts_landed_pieces_against_the_plans_pieces(tmp_path):
    run, logs = make_run(tmp_path)
    share = section(run_tool(run, logs), "Share finished")
    assert "3 of 4 pieces landed (3 cards): 75%" in share
    assert "1 merge lines name no card" in share


def test_surprises_counts_and_prints_the_unforeseen_and_the_blockers(tmp_path):
    run, logs = make_run(tmp_path)
    surprises = section(run_tool(run, logs), "Surprises")
    assert "3: 1 unforeseen key points, 2 blockers" in surprises
    assert "Unforeseen - 06:10 · the page server stopped · restarted it" in surprises
    assert "Blocker - 07:00 · his act A1 not done · waits for him" in surprises
    assert "Blocker - 07:05 · the laptop is off · waits for him" in surprises


def test_it_prints_the_four_headings_in_order(tmp_path):
    run, logs = make_run(tmp_path)
    out = run_tool(run, logs)
    places = [out.index("## " + h + "\n") for h in ("It works", "Usage per finished piece", "Share finished", "Surprises")]
    assert places == sorted(places)


LAND_RECORD = """# Run 9 — demo-project

## Go
- Start: 2026-10-07 05:00

## Merges
- 05:40 · template alpha · squash 1111111 · undo: `git revert 1111111`
- 07:30 · 2026-10-07-delta · squash 5555555 · undo: `git revert 5555555`
"""

ROUNDS_PATH = """## The path
Path a, all of 0.5.0: the twelve pieces, each with its lane.
Rounds, in order, up to four pieces at once:
- Round 1, the clerk scripts first: 1 `land` and `record` · 2 the forms · 3 seats · 5 `measures`
- Round 2: 4 `shutdown` and `flag` · 6 `plan_check` · 9 the rules · 10 pages and blanks
- Round 3: 7 the run skill · 8 the conductor skill
- Round 4: 11 version 0.5.0 and the adopt · 12 the decision log's "still standing" (any time; it touches only `docs/decisions*`)

## Budget and hard stop
- Budget: 12% of his week
"""

NUMBERED_PATH = """## The path
The template desk's order, its items each with its desk and lane:
- 1 · the usage counter: `measures.py` reads a piece as `land` writes it · template · full
- 2 · the upgrade keeps a project's own settings · template · full
- 3 · the lines: masters at medium effort (his 3a); the seven kept lessons (his 4a) · template · full
- 4 · version 0.5.1, tagged `template/0.5.1`, and this project's adopt of it · template · standard
- 5 · the manual: from stamping to closing a run (decisions 09:53, call 5); written after piece 4 lands · the master's own card · standard (an Opus 5.5 worker at high)
"""


def land_sessions(logs):
    # delta's worker and checker: land wrote the card with its date, 2026-10-07-delta.
    session(logs, "delta-worker", WORKTREES + "task-demo-project-2026-10-07-delta",
            "task/demo-project/2026-10-07-delta", "desks/template is your folder. You are the worker.",
            [("2026-10-07 07:00", 300)])
    session(logs, "main/delta-checker", MAIN, "main",
            "Act as the checker. Check the branch task/demo-project/2026-10-07-delta.",
            [("2026-10-07 07:20", 100)])


def test_a_merge_line_as_land_writes_it_gets_its_sessions(tmp_path):
    run, logs = make_run(tmp_path)
    (run / "run.md").write_text(LAND_RECORD, encoding="utf-8")
    land_sessions(logs)
    usage = section(run_tool(run, logs), "Usage per finished piece")
    assert "- 2026-10-07-delta · 400 · 100.0% · 2 sessions" in usage
    assert "2026-10-07-2026-10-07" not in usage
    assert "- the rest · 0 · 0.0% · 0 sessions" in usage


def test_the_land_form_and_the_desk_form_side_by_side_in_one_record(tmp_path):
    run, logs = make_run(tmp_path)
    (run / "run.md").write_text(LAND_RECORD + "\n## It works\n- 08:01 · 2026-10-07-delta · pass · tried it\n",
                                encoding="utf-8")
    the_usual_sessions(logs)
    land_sessions(logs)
    out = run_tool(run, logs)
    usage = section(out, "Usage per finished piece")
    # Total 4400: alpha 1000, delta 400, masters 2000, conductors 300, the rest (beta, not landed here, and the probe) 700.
    assert "- template alpha · 1,000 · 22.7% · 2 sessions" in usage
    assert "- 2026-10-07-delta · 400 · 9.1% · 2 sessions" in usage
    assert "- the rest · 700 · 15.9% · 2 sessions" in usage
    assert "- 2026-10-07-delta · pass · tried it" in section(out, "It works")
    assert "2 of 4 pieces landed (2 cards): 50%" in section(out, "Share finished")


def test_share_finished_counts_run_3s_numbered_pieces_not_its_rounds(tmp_path):
    run, logs = make_run(tmp_path)
    (run / "plan-signed.md").write_text("# Plan for run 9 — demo-project\n\n" + ROUNDS_PATH, encoding="utf-8")
    share = section(run_tool(run, logs), "Share finished")
    assert "3 of 12 pieces landed (3 cards): 25%" in share


def test_share_finished_counts_run_4s_numbered_bullets_once_each(tmp_path):
    run, logs = make_run(tmp_path)
    (run / "plan-signed.md").write_text("# Plan for run 9 — demo-project\n\n" + NUMBERED_PATH, encoding="utf-8")
    share = section(run_tool(run, logs), "Share finished")
    assert "3 of 5 pieces landed (3 cards): 60%" in share


def logs_line(out):
    return next(line for line in out.splitlines() if line.startswith("Logs: "))


def a_master_after_0800(logs):
    session(logs, "master/late", WORKTREES + "t3code-def", "t3code/def", "/run carry on from the handover",
            [("2026-10-07 08:30", 5000)])


def test_a_closed_run_is_read_up_to_its_close_and_a_later_session_is_left_out(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    a_master_after_0800(logs)
    close_run(tmp_path, "decisions.md", "## 2026-10-07 08:00 — Run 9 closed (review master, somewhere)")
    out = run_tool(run, logs, until=None)
    assert logs_line(out).endswith(", 2026-10-07 05:00 to the run's close, 2026-10-07 08:00")
    usage = section(out, "Usage per finished piece")
    assert "- masters · 2,000 · 50.0% · 1 sessions" in usage
    assert "- total · 4,000" in usage


def test_a_close_entry_in_an_archive_file_is_read_too(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    a_master_after_0800(logs)
    close_run(tmp_path, "decisions.md", "## 2026-10-07 06:30 — Run 8 closed (master, somewhere)")
    close_run(tmp_path, "decisions-archive-1.md", "## 2026-10-07 08:00 — Run 9 closed (review master, somewhere)")
    out = run_tool(run, logs, until=None)
    assert logs_line(out).endswith("to the run's close, 2026-10-07 08:00")
    assert "- total · 4,000" in section(out, "Usage per finished piece")


def test_an_unclosed_run_reads_to_now(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    # Another run's close is not this run's: run 9 is still open.
    close_run(tmp_path, "decisions.md", "## 2026-10-07 06:30 — Run 8 closed (master, somewhere)")
    recent = (dt.datetime.now() - dt.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M")
    session(logs, "master/today", WORKTREES + "t3code-ghi", "t3code/ghi", "/run carry on from the handover",
            [(recent, 5000)])
    out = run_tool(run, logs, until=None)
    assert "the run's close" not in logs_line(out)
    usage = section(out, "Usage per finished piece")
    assert "- masters · 7,000 · 77.8% · 2 sessions" in usage
    assert "- total · 9,000" in usage


def test_until_wins_over_the_close(tmp_path):
    run, logs = make_run(tmp_path)
    the_usual_sessions(logs)
    a_master_after_0800(logs)
    close_run(tmp_path, "decisions.md", "## 2026-10-07 08:00 — Run 9 closed (review master, somewhere)")
    out = run_tool(run, logs, until="2026-10-07 09:00")
    assert logs_line(out).endswith(", 2026-10-07 05:00 to 2026-10-07 09:00")
    usage = section(out, "Usage per finished piece")
    assert "- masters · 7,000 · 77.8% · 2 sessions" in usage
    assert "- total · 9,000" in usage


def test_two_landed_cards_naming_one_piece_count_once(tmp_path):
    run, logs = make_run(tmp_path)
    # gamma is the second half of piece 1, as run 4's piece 3 was cut in two.
    card(tmp_path, "desks/template", "2026-10-07-gamma", "asks entry `2026-10-07 04:00`, item 1 (run 9, piece 1, second half)")
    share = section(run_tool(run, logs), "Share finished")
    assert "2 of 4 pieces landed (3 cards): 50%" in share


def test_a_landed_card_that_names_no_piece_is_named_and_not_counted(tmp_path):
    run, logs = make_run(tmp_path)
    # gamma's Order line names no piece; the "piece 4" in its Goal is not read.
    card(tmp_path, "desks/template", "2026-10-07-gamma", "run 9's record § Orders, item 5")
    share = section(run_tool(run, logs), "Share finished")
    assert "2 of 4 pieces landed (3 cards; 1 names no piece: template gamma): 50%" in share
    # road-beta's file is gone: it is not guessed at either.
    os.remove(tmp_path / "project" / "desks" / "road" / "docs" / "cards" / "2026-10-07-road-beta.md")
    share = section(run_tool(run, logs), "Share finished")
    assert "1 of 4 pieces landed (3 cards; 2 name no piece: road road-beta, template gamma): 25%" in share
