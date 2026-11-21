# Tests for land.py. Each test builds a throwaway project under tmp_path:
# a bare origin, a main checkout cloned from it with a card and a run record,
# and the card's branch in its own worktree, built and checked. Then it runs
# the tool in the main checkout, as the master would. Nothing here pushes to
# this repo's real origin or writes to its real record.

import datetime as dt
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "land.py")
BRANCH = "task/test/piece"
CARD = "desks/d/docs/cards/piece.md"
RECEIPT = "desks/d/docs/cards/receipts/piece-close.md"
RUN = "docs/runs/1/run.md"


def git(repo, *args):
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def configure(repo):
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "config", "core.autocrlf", "false")


def write(repo, path, text):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def project(tmp_path):
    return make_project(tmp_path)


@pytest.fixture
def short_project():
    # A short folder of its own, never tmp_path: the log folder is named from the worktree's whole path, past 260 characters under a long --basetemp (L032, L051).
    short = tempfile.mkdtemp(prefix="rl")
    try:
        yield make_project(pathlib.Path(short), worktree_name="w")
    finally:
        shutil.rmtree(short, onerror=lambda func, path, _: (os.chmod(path, stat.S_IWRITE), func(path)))


def make_project(tmp_path, worktree_name="worktree"):
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "-q", "-b", "main")
    configure(main)
    write(main, "work.txt", "the old work\n")
    write(main, "readme.txt", "a tracked file no card touches\n")
    write(main, CARD, f"# piece — d — 2026-10-08\n\n## Goal\nThe work.\n\n"
                      f"## Touches\n`work.txt` · `new.txt` · `tools/` · `{RECEIPT}`\n\n## Read first\nnothing\n")
    write(main, RUN, "# Run 1 — test\n\n## Merges\nOne line per merge, with its undo.\n\n## Handover\n")
    git(main, "add", ".")
    git(main, "commit", "-q", "-m", "the start")
    git(main, "remote", "add", "origin", str(origin))
    git(main, "push", "-q", "origin", "main")
    worktree = tmp_path / worktree_name
    git(main, "worktree", "add", "-q", "-b", BRANCH, str(worktree), "main")
    configure(worktree)
    return main, worktree, origin


def build(worktree, verdict="PASS", extra=None, message="the work"):
    """The worker's commit, then the receipt with the checker's block naming it."""
    write(worktree, "work.txt", "the new work\n")
    git(worktree, "add", "work.txt")
    if extra:
        write(worktree, extra, "outside the fence\n")
        git(worktree, "add", extra)
    git(worktree, "commit", "-q", "-m", message)
    receipt(worktree, verdict)


def receipt(worktree, verdict="PASS"):
    """The receipt, its checker's block naming the branch as it stands, in a commit of its own."""
    checked = git(worktree, "rev-parse", "HEAD")
    write(worktree, RECEIPT, f"DONE — the work is done\n\n# Receipt — piece — 2026-10-08\n\n"
                             f"## Checker run 2026-10-08 — a checker, own session\n"
                             f"Commit: {checked}\nExit code: 0\n"
                             f"From a clean copy: /tmp/c/clean-0123456789ab · 1 command · exit codes 0\n"
                             f"Shown failing: took work.txt away, and the gate failed\n"
                             f"Verdict: {verdict}\n")
    git(worktree, "add", RECEIPT)
    git(worktree, "commit", "-q", "-m", "the receipt")


def land(main):
    # The session logs are the test's own folder, never the machine's real ones.
    done = subprocess.run([sys.executable, "-B", TOOL, "--card", CARD, "--branch", BRANCH,
                           "--logs", str(main.parent / "logs")],
                          cwd=main, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def state(main, origin):
    """What git status and git log say in the main checkout, and what origin holds."""
    return (git(main, "status", "--porcelain=v1", "--untracked-files=all"),
            git(main, "log", "--format=%H %s"),
            git(origin, "rev-parse", "main"),
            (main / RUN).read_bytes())


def test_lands_a_checked_branch_writes_the_line_and_pushes(project):
    main, worktree, origin = project
    build(worktree)
    code, out = land(main)
    assert code == 0, out
    assert out.startswith("LANDED"), out
    assert (main / "work.txt").read_text(encoding="utf-8") == "the new work\n"
    assert (main / RECEIPT).is_file()
    squash = git(main, "rev-parse", "--short=7", "HEAD~1")
    assert git(main, "log", "-1", "--format=%s", "HEAD~1").startswith("Land piece")
    # The record commit names the run record alone.
    assert git(main, "show", "--name-only", "--format=", "HEAD") == RUN
    lines = (main / RUN).read_text(encoding="utf-8").splitlines()
    assert re.fullmatch(rf"- \d\d:\d\d · piece · squash {squash} · undo: `git revert {squash}`",
                        lines[lines.index("## Merges") + 2]), lines
    assert git(origin, "rev-parse", "main") == git(main, "rev-parse", "HEAD")
    assert git(main, "status", "--porcelain=v1", "--untracked-files=all") == ""


@pytest.mark.parametrize("which", ["main checkout fence", "card fence", "merge check"])
def test_refuses_at_each_check_with_nothing_changed(project, which):
    main, worktree, origin = project
    if which == "main checkout fence":
        build(worktree)
        write(main, "work.txt", "a change outside the record\n")
    elif which == "card fence":
        build(worktree, extra="other-desk.txt")
    else:
        build(worktree, verdict="FAIL")
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith(f"REFUSE: {which} — "), out
    assert state(main, origin) == before


def test_lands_past_a_stray_untracked_folder_and_names_it(project):
    main, worktree, origin = project
    build(worktree)
    write(main, "specs-for-manager/guide.md", "his guide, left uncommitted\n")
    write(main, "specs-for-manager/notes/LOG.md", "a log with two writers\n")
    code, out = land(main)
    assert code == 0, out
    assert out.startswith("LANDED"), out
    assert ("STRAY (left as found, not landed): specs-for-manager/guide.md · "
            "specs-for-manager/notes/LOG.md") in out.splitlines(), out
    # Still there, still untracked, and in no commit here or on origin.
    assert (main / "specs-for-manager/guide.md").read_text(encoding="utf-8") == "his guide, left uncommitted\n"
    assert git(main, "status", "--porcelain=v1", "--untracked-files=all").splitlines() == [
        "?? specs-for-manager/guide.md", "?? specs-for-manager/notes/LOG.md"]
    assert git(main, "log", "--all", "--format=", "--name-only", "--", "specs-for-manager") == ""
    assert git(origin, "rev-parse", "main") == git(main, "rev-parse", "HEAD")


@pytest.mark.parametrize("how", ["modified", "deleted", "staged"])
def test_a_tracked_change_outside_the_record_is_refused(project, how):
    main, worktree, origin = project
    build(worktree)
    if how == "modified":
        write(main, "readme.txt", "a change outside the record\n")
    elif how == "deleted":
        (main / "readme.txt").unlink()
    else:
        write(main, "staged.txt", "a new file, staged\n")
        git(main, "add", "staged.txt")
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith("REFUSE: main checkout fence — OUTSIDE"), out
    assert "STRAY" not in out, out
    assert state(main, origin) == before


@pytest.mark.parametrize("path", ["new.txt", "tools/new.py"])
def test_an_untracked_file_the_card_touches_is_refused(project, path):
    main, worktree, origin = project
    build(worktree)
    write(main, path, "the squash would meet this\n")
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith("REFUSE: main checkout fence — OUTSIDE"), out
    assert path in out.splitlines(), out
    assert state(main, origin) == before


def test_refuses_a_conflicting_squash_with_nothing_changed(project):
    main, worktree, origin = project
    build(worktree)
    write(main, "work.txt", "main's own new work\n")
    git(main, "commit", "-q", "-am", "main moved on")
    write(main, "docs/note.md", "an uncommitted record line\n")
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith("REFUSE: squash — "), out
    assert state(main, origin) == before
    assert not (main / RECEIPT).exists()


def test_the_squash_message_carries_the_branchs_last_message_under_its_first_line(project):
    main, worktree, origin = project
    message = ("Adopt three lines\n\nThe lines adopted, each with its source.\n"
               "# a line that opens with a hash stays\n\nCo-Authored-By: A Worker <worker@example.invalid>")
    build(worktree, message=message)
    code, out = land(main)
    assert code == 0, out
    assert git(main, "log", "-1", "--format=%B", "HEAD~1") == f"Land piece (squash of {BRANCH})\n\n{message}"
    assert git(main, "log", "-1", "--format=%s", "HEAD~1") == f"Land piece (squash of {BRANCH})"


def test_a_receipt_commit_is_skipped_for_the_squash_message(tmp_path):
    (tmp_path / "a").mkdir()
    main, worktree, origin = make_project(tmp_path / "a")
    build(worktree, message="the last real work")
    write(worktree, RECEIPT, (worktree / RECEIPT).read_text(encoding="utf-8") + "\nA later word.\n")
    git(worktree, "commit", "-q", "-am", "the receipt again")
    code, out = land(main)
    assert code == 0, out
    assert git(main, "log", "-1", "--format=%B", "HEAD~1") == f"Land piece (squash of {BRANCH})\n\nthe last real work"

    # A branch that holds nothing but its receipt lands with the one line.
    (tmp_path / "b").mkdir()
    main, worktree, origin = make_project(tmp_path / "b")
    receipt(worktree)
    code, out = land(main)
    assert code == 0, out
    assert git(main, "log", "-1", "--format=%B", "HEAD~1") == f"Land piece (squash of {BRANCH})"


def test_a_failed_push_alone_says_so_with_the_undo(project):
    main, worktree, origin = project
    build(worktree)
    git(main, "remote", "set-url", "origin", str(origin.parent / "no-such-origin.git"))
    code, out = land(main)
    assert code == 2, out
    squash = git(main, "rev-parse", "--short=7", "HEAD~1")
    assert out.startswith("PUSH FAILED"), out
    assert f"git revert {squash}" in out, out


# ---- the receipt's Run lines, stamped from the session logs ---------------

def session_log(main, worktree, name, entries):
    """A small session log in the test's logs folder, where the harness keeps
    the worktree's: its path with each sign but letters and digits as '-'."""
    folder = main.parent / "logs" / re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(worktree))
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")


def local(stamp):
    return dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")


def with_card_line(worktree):
    text = (worktree / RECEIPT).read_text(encoding="utf-8")
    write(worktree, RECEIPT, text.replace("\n\n## Checker", f"\n\nCard: `{CARD}` · Branch: `{BRANCH}`\n\n## Checker", 1))
    git(worktree, "commit", "-q", "-am", "the receipt's card line")


SESSION = [
    {"type": "user", "timestamp": "2026-11-17T08:12:37.186Z", "message": {"role": "user", "content": "the orders"}},
    {"type": "assistant", "timestamp": "2026-11-17T08:13:00.000Z", "effort": "high",
     "message": {"model": "claude-opus-5-5", "content": [{"type": "tool_use", "id": "t1"}]}},
    {"type": "user", "timestamp": "2026-11-17T08:13:05.000Z",
     "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}},
    {"type": "user", "timestamp": "2026-11-17T09:40:00.000Z",
     "message": {"content": [{"type": "text", "text": "carry on"}]}},
    {"type": "assistant", "timestamp": "2026-11-17T09:41:30.000Z", "effort": "high",
     "message": {"model": "claude-opus-5-5", "content": [{"type": "text", "text": "done"}]}},
]


def test_a_run_line_is_stamped_from_a_session_log_under_the_card_line(short_project):
    main, worktree, origin = short_project
    build(worktree)
    with_card_line(worktree)
    session_log(main, worktree, "s1.jsonl", SESSION)
    session_log(main, worktree, "s2.jsonl", [
        {"type": "user", "timestamp": "2026-11-17T10:00:00Z", "message": {"content": "check it"}},
        {"type": "assistant", "timestamp": "2026-11-17T10:05:00Z", "message": {"model": "claude-fable-5-2"}}])
    code, out = land(main)
    assert code == 0, out
    lines = (main / RECEIPT).read_text(encoding="utf-8").splitlines()
    card = next(i for i, l in enumerate(lines) if l.startswith("Card:"))
    assert lines[card + 1:card + 3] == [
        f"Run: claude-opus-5-5 · high · {local('2026-11-17T08:12:37Z')} · {local('2026-11-17T09:41:30Z')} · 2 turns",
        f"Run: claude-fable-5-2 · effort unknown · {local('2026-11-17T10:00:00Z')} · "
        f"{local('2026-11-17T10:05:00Z')} · 1 turns"], lines
    assert git(worktree, "log", "-1", "--format=%s") == "Receipt: Run lines stamped by land.py"
    assert git(worktree, "show", "--name-only", "--format=", "HEAD") == RECEIPT  # the receipt alone


def test_no_session_log_is_said_and_the_landing_goes_on(project):
    main, worktree, origin = project
    build(worktree)
    code, out = land(main)
    assert code == 0 and out.startswith("LANDED"), out
    lines = (main / RECEIPT).read_text(encoding="utf-8").splitlines()
    title = lines.index("# Receipt — piece — 2026-10-08")  # no Card: line: under the title
    assert lines[title + 1] == "Run: no session log found", lines


def test_run_lines_already_there_are_replaced_not_doubled(short_project):
    main, worktree, origin = short_project
    build(worktree)
    with_card_line(worktree)
    text = (worktree / RECEIPT).read_text(encoding="utf-8")
    write(worktree, RECEIPT, text.replace(f"`{BRANCH}`\n", f"`{BRANCH}`\nRun: typed from memory\n", 1))
    git(worktree, "commit", "-q", "-am", "a typed Run line")
    session_log(main, worktree, "s1.jsonl", SESSION)
    code, out = land(main)
    assert code == 0, out
    runs = [l for l in (main / RECEIPT).read_text(encoding="utf-8").splitlines() if l.startswith("Run:")]
    assert len(runs) == 1 and runs[0].startswith("Run: claude-opus-5-5 · high · "), runs


# ---- the card's own receipt, and a closed run -----------------------------

def recard(main, touches=None, branch_line=None):
    """Rewrite the card on main (committed, so the fence reads it clean)."""
    text = (main / CARD).read_text(encoding="utf-8")
    if touches is not None:
        text = re.sub(r"(## Touches\n).*\n", lambda m: m.group(1) + touches + "\n", text)
    if branch_line is not None:
        text = text.replace("\n## Goal", f"\n{branch_line}\n\n## Goal", 1)
    write(main, CARD, text)
    git(main, "commit", "-q", "-am", "the card changed")


def test_the_cards_own_receipt_is_chosen_among_two(project):
    main, worktree, origin = project
    other = "desks/d/docs/cards/receipts/other-close.md"
    recard(main, touches=f"`work.txt` · `{other}` · `{RECEIPT}`")
    build(worktree)
    code, out = land(main)
    assert code == 0 and out.startswith("LANDED"), out  # the other was never there; its own was read
    assert not (main / other).exists()


def test_two_receipts_and_neither_its_own_is_refused_naming_them(project):
    main, worktree, origin = project
    one, two = "desks/d/docs/cards/receipts/one-close.md", "desks/d/docs/cards/receipts/two-close.md"
    recard(main, touches=f"`work.txt` · `{one}` · `{two}`")
    build(worktree)
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith("REFUSE: card — ") and one in out and two in out and "piece-close.md" in out, out
    assert state(main, origin) == before


def test_a_landing_into_a_closed_run_is_refused(project):
    main, worktree, origin = project
    write(main, "docs/decisions.md", "# Decisions\n\n## 2026-10-08 06:08 — Run 1 closed (master)\nKept.\n")
    git(main, "add", "docs/decisions.md")
    recard(main, branch_line=f"Branch: `{BRANCH}` · Order: asks entry · run 1, piece 2")
    build(worktree)
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.strip() == "REFUSE: record — run 1 is closed; land into the open run's record", out
    assert state(main, origin) == before
    assert git(worktree, "log", "-1", "--format=%s") == "the receipt"  # nothing stamped either


def test_a_landing_into_an_open_run_goes_on(project):
    main, worktree, origin = project
    write(main, "docs/decisions.md", "# Decisions\n\n## 2026-10-08 06:08 — Run 1 closed (master)\nKept.\n")
    git(main, "add", "docs/decisions.md")
    recard(main, branch_line=f"Branch: `{BRANCH}` · Order: asks entry · run 2, piece 2")
    build(worktree)
    code, out = land(main)
    assert code == 0 and out.startswith("LANDED"), out


# ---- the size check, in the branch's worktree ------------------------------

def sized(main, worktree, lines):
    """The branch adds template/STATUS.md, limiting template/tracks.md to 4 lines, and a tracks.md of this many."""
    recard(main, touches=f"`work.txt` · `template/` · `{RECEIPT}`")
    write(worktree, "template/STATUS.md", "# Template status\n\n## Line limits\n- `tracks.md` · 4 lines\n")
    write(worktree, "template/tracks.md", "".join(f"{i}. **Rule {i}.**\n" for i in range(1, lines + 1)))
    git(worktree, "add", "template")
    git(worktree, "commit", "-q", "-m", "the rules")
    build(worktree)


def test_a_landing_that_takes_a_file_over_its_limit_is_refused(project):
    main, worktree, origin = project
    sized(main, worktree, 5)
    before, branch = state(main, origin), git(worktree, "rev-parse", "HEAD")
    code, out = land(main)
    assert code == 1, out
    assert out.strip() == "REFUSE: size check — REFUSE: tracks.md is 5 lines, 1 over its limit of 4", out
    assert state(main, origin) == before
    assert git(worktree, "rev-parse", "HEAD") == branch  # refused before the Run lines were stamped


def test_a_landing_with_a_file_at_its_limit_goes_on(project):
    main, worktree, origin = project
    sized(main, worktree, 4)
    code, out = land(main)
    assert code == 0 and out.startswith("LANDED"), out
    assert (main / "template/tracks.md").is_file()
