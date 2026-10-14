# Tests for land.py. Each test builds a throwaway project under tmp_path:
# a bare origin, a main checkout cloned from it with a card and a run record,
# and the card's branch in its own worktree, built and checked. Then it runs
# the tool in the main checkout, as the master would. Nothing here pushes to
# this repo's real origin or writes to its real record.

import os
import re
import subprocess
import sys

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
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "-q", "-b", "main")
    configure(main)
    write(main, "work.txt", "the old work\n")
    write(main, CARD, f"# piece — d — 2026-10-08\n\n## Goal\nThe work.\n\n"
                      f"## Touches\n`work.txt` · `{RECEIPT}`\n\n## Read first\nnothing\n")
    write(main, RUN, "# Run 1 — test\n\n## Merges\nOne line per merge, with its undo.\n\n## Handover\n")
    git(main, "add", ".")
    git(main, "commit", "-q", "-m", "the start")
    git(main, "remote", "add", "origin", str(origin))
    git(main, "push", "-q", "origin", "main")
    worktree = tmp_path / "worktree"
    git(main, "worktree", "add", "-q", "-b", BRANCH, str(worktree), "main")
    configure(worktree)
    return main, worktree, origin


def build(worktree, verdict="PASS", extra=None):
    """The worker's commit, then the receipt with the checker's block naming it."""
    write(worktree, "work.txt", "the new work\n")
    git(worktree, "add", "work.txt")
    if extra:
        write(worktree, extra, "outside the fence\n")
        git(worktree, "add", extra)
    git(worktree, "commit", "-q", "-m", "the work")
    checked = git(worktree, "rev-parse", "HEAD")
    write(worktree, RECEIPT, f"DONE — the work is done\n\n# Receipt — piece — 2026-10-08\n\n"
                             f"## Checker run 2026-10-08 — a checker, own session\n"
                             f"Commit: {checked}\nExit code: 0\nVerdict: {verdict}\n")
    git(worktree, "add", RECEIPT)
    git(worktree, "commit", "-q", "-m", "the receipt")


def land(main):
    done = subprocess.run([sys.executable, "-B", TOOL, "--card", CARD, "--branch", BRANCH],
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
        write(main, "stray.txt", "a change outside the record\n")
    elif which == "card fence":
        build(worktree, extra="other-desk.txt")
    else:
        build(worktree, verdict="FAIL")
    before = state(main, origin)
    code, out = land(main)
    assert code == 1, out
    assert out.startswith(f"REFUSE: {which} — "), out
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


def test_a_failed_push_alone_says_so_with_the_undo(project):
    main, worktree, origin = project
    build(worktree)
    git(main, "remote", "set-url", "origin", str(origin.parent / "no-such-origin.git"))
    code, out = land(main)
    assert code == 2, out
    squash = git(main, "rev-parse", "--short=7", "HEAD~1")
    assert out.startswith("PUSH FAILED"), out
    assert f"git revert {squash}" in out, out
