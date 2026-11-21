# Tests for fence_check.py --card. Each test makes a throwaway git repo
# under tmp_path with a folder of cards committed on main, then a task
# branch that changes files, and runs the tool as the master would.
# No real card of this repo is read or changed.

import os
import subprocess
import sys

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fence_check.py")


def git(repo, *args):
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def card(branch, *touches):
    return (f"# a card — 2026-10-08\n\nBranch: `{branch}` · Worktree: its own\n\n"
            f"## Goal\nThe work.\n\n## Touches\n" + " · ".join(f"`{t}`" for t in touches)
            + "\n\n## Read first\nNothing.\n")


@pytest.fixture
def repo(tmp_path):
    # Run 2's road fixes: a first card, a continue card on the same branch,
    # each naming only its own files, and a card on another branch.
    folder = tmp_path / "repo"
    (folder / "cards").mkdir(parents=True)
    git(folder, "init", "-q")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.invalid")
    git(folder, "config", "commit.gpgsign", "false")
    git(folder, "config", "core.autocrlf", "false")
    git(folder, "checkout", "-q", "-b", "main")
    (folder / "cards" / "first.md").write_text(card("task/fix", "first.txt", "cards/receipts/first-close.md"), encoding="utf-8")
    (folder / "cards" / "continue.md").write_text(card("task/fix", "continue.txt", "cards/receipts/continue-close.md"), encoding="utf-8")
    (folder / "cards" / "other.md").write_text(card("task/other", "other.txt"), encoding="utf-8")
    git(folder, "add", "cards")
    git(folder, "commit", "-q", "-m", "the cards")
    git(folder, "checkout", "-q", "-b", "task/fix")
    return folder


def change(repo, *paths):
    for path in paths:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text("the work\n", encoding="utf-8")
    git(repo, "add", *paths)
    git(repo, "commit", "-q", "-m", "the work")


def run(repo, card_name):
    done = subprocess.run(
        [sys.executable, "-B", TOOL, "--card", os.path.join("cards", card_name)],
        cwd=repo, capture_output=True, text=True,
    )
    return done.returncode, done.stdout + done.stderr


@pytest.mark.parametrize("card_name", ["continue.md", "first.md"])
def test_cards_on_one_branch_share_one_fence(repo, card_name):
    change(repo, "first.txt", "cards/receipts/first-close.md",
           "continue.txt", "cards/receipts/continue-close.md")
    code, out = run(repo, card_name)
    assert code == 0, out
    assert out.startswith("INSIDE"), out


def test_a_card_on_another_branch_adds_nothing(repo):
    change(repo, "continue.txt", "other.txt")
    code, out = run(repo, "continue.md")
    assert code == 1, out
    assert out.startswith("OUTSIDE"), out
    assert "other.txt" in out, out
    assert "continue.txt" not in out.splitlines()[1:], out


def run_main(repo, *args):
    done = subprocess.run([sys.executable, "-B", TOOL, "--main", *args],
                          cwd=repo, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def test_main_alone_still_calls_a_stray_outside(repo):
    (repo / "specs" / "guide.md").parent.mkdir()
    (repo / "specs" / "guide.md").write_text("left uncommitted\n", encoding="utf-8")
    code, out = run_main(repo)
    assert code == 1, out
    assert out.startswith("OUTSIDE"), out
    assert "specs/guide.md" in out.splitlines(), out


def test_main_with_a_card_names_a_stray_and_passes(repo):
    (repo / "specs" / "guide.md").parent.mkdir()
    (repo / "specs" / "guide.md").write_text("left uncommitted\n", encoding="utf-8")
    code, out = run_main(repo, "--card", os.path.join("cards", "first.md"))
    assert code == 0, out
    assert out.startswith("INSIDE"), out
    assert "STRAY: specs/guide.md" in out.splitlines(), out


@pytest.mark.parametrize("path", ["cards/other.md", "continue.txt"])
def test_main_with_a_card_refuses_a_tracked_change_or_a_touched_file(repo, path):
    # cards/other.md is tracked; continue.txt is untracked but in the branch's fence.
    (repo / path).write_text("a change\n", encoding="utf-8")
    code, out = run_main(repo, "--card", os.path.join("cards", "first.md"))
    assert code == 1, out
    assert out.startswith("OUTSIDE"), out
    assert path in out.splitlines(), out
    assert "STRAY" not in out, out
