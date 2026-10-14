# Tests for merge_check.py. Each test makes a throwaway git repo under
# tmp_path, commits one piece of work, then commits a receipt whose
# Checker run block names that commit, and runs the tool as the master would.
# No real receipt of this repo is read or changed.

import os
import subprocess
import sys

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "merge_check.py")
RECEIPT = "receipt.md"


def git(repo, *args):
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    folder = tmp_path / "branch"
    folder.mkdir()
    git(folder, "init", "-q")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.invalid")
    git(folder, "config", "commit.gpgsign", "false")
    git(folder, "config", "core.autocrlf", "false")
    (folder / "work.txt").write_text("the work\n", encoding="utf-8")
    git(folder, "add", "work.txt")
    git(folder, "commit", "-q", "-m", "the work")
    return folder


def commit_receipt(repo, *checker_lines, first="DONE — the work is done", exit_code="0"):
    checked = git(repo, "rev-parse", "HEAD")
    text = (f"{first}\n\n# Receipt — test — 2026-10-07\n\n## Shipped\nwork.txt\n\n"
            f"## Checker run 2026-10-07 — a checker, own session\n"
            f"Commit: {checked}\nExit code: {exit_code}\n\n")
    text += "\n".join(checker_lines) + "\n"
    (repo / RECEIPT).write_text(text, encoding="utf-8")
    git(repo, "add", RECEIPT)
    git(repo, "commit", "-q", "-m", "the receipt")


def run(repo):
    done = subprocess.run(
        [sys.executable, "-B", TOOL, RECEIPT], cwd=repo, capture_output=True, text=True,
    )
    return done.returncode, done.stdout + done.stderr


def test_pass_with_exit_0_is_allowed(repo):
    commit_receipt(repo, "The diff read whole.", "Verdict: PASS")
    code, out = run(repo)
    assert code == 0, out
    assert out.startswith("ALLOW"), out


def test_fail_with_exit_0_is_refused(repo):
    # The run-lines receipt of 6 Oct: the gate passed, the checker said FAIL.
    commit_receipt(repo, "Verdict: FAIL. The gate passes, but Goal 2 changes a rule.")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "FAIL" in out, out


def test_no_verdict_is_refused(repo):
    commit_receipt(repo, "The diff read whole, and it looks fine.")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "verdict" in out.lower(), out


def test_two_verdict_lines_are_refused(repo):
    commit_receipt(repo, "Verdict: PASS", "", "Verdict: PASS")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "verdict" in out.lower(), out


def test_a_word_other_than_pass_or_fail_is_refused(repo):
    commit_receipt(repo, "Verdict: PASSED with notes")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "verdict" in out.lower(), out


@pytest.mark.parametrize("line", ["**Verdict: PASS.**", "**Verdict: PASS**", "Verdict: PASS."])
def test_bold_and_full_stop_read_as_pass(repo, line):
    commit_receipt(repo, line)
    code, out = run(repo)
    assert code == 0, out
    assert out.startswith("ALLOW"), out


def test_only_the_last_checker_block_counts(repo):
    # Run-lines again: a first block said FAIL, the re-check after it said PASS.
    checked = git(repo, "rev-parse", "HEAD")
    commit_receipt(repo, "Verdict: PASS.")
    text = (repo / RECEIPT).read_text(encoding="utf-8")
    earlier = (f"## Checker run 2026-10-06 — a checker, own session\n"
               f"Commit: {checked}\nExit code: 0\n\nVerdict: FAIL. One line to settle.\n\n")
    text = text.replace("## Checker run 2026-10-07", earlier + "## Checker run 2026-10-07")
    (repo / RECEIPT).write_text(text, encoding="utf-8")
    git(repo, "commit", "-q", "-m", "two blocks", "--", RECEIPT)
    code, out = run(repo)
    assert code == 0, out
    assert out.startswith("ALLOW"), out


def test_exit_1_with_pass_is_refused(repo):
    commit_receipt(repo, "Verdict: PASS", exit_code="1")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "exit code 1" in out, out


def test_first_line_not_done_is_refused(repo):
    commit_receipt(repo, "Verdict: PASS", first="NOT DONE — the gate fails")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "DONE" in out, out


def test_run_2_two_verdict_shape_is_refused_and_says_how_to_write_it(repo):
    # Run 2's wrap-resume, 7 Oct 06:21: a verdict, then a summary line that
    # also starts "Verdict:".
    commit_receipt(repo, "Verdict: PASS", "", "Verdict: PASS — the gate passes and nothing is unasked.")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "exactly one line starts with Verdict" in out, out
    assert "Why:" in out, out


def committed_with_crlf_checkout(repo):
    # A checkout that turns LF into CRLF, as on Windows: git holds the file
    # with LF, the working copy has CRLF. A new file, as the fixture's
    # work.txt may already hold CRLF, and git then leaves it as it is.
    git(repo, "config", "core.autocrlf", "true")
    (repo / "more.txt").write_bytes(b"the work\r\nand more\r\n")
    git(repo, "add", "more.txt")
    git(repo, "commit", "-q", "-m", "more work")
    commit_receipt(repo, "Verdict: PASS")


def test_a_file_rewritten_with_the_same_contents_is_allowed(repo):
    # Run 2's relay-act, 7 Oct 11:28: a checker's ablation put a committed
    # file back byte for byte as the commit holds it. Its size changed, so
    # git status listed it; git diff --quiet found the contents the same.
    committed_with_crlf_checkout(repo)
    blob = subprocess.run(["git", "show", "HEAD:more.txt"], cwd=repo, capture_output=True).stdout
    assert blob == b"the work\nand more\n"
    (repo / "more.txt").write_bytes(blob)
    code, out = run(repo)
    assert code == 0, out
    assert out.startswith("ALLOW"), out


def test_a_real_change_in_the_working_copy_is_refused(repo):
    committed_with_crlf_checkout(repo)
    (repo / "more.txt").write_bytes(b"other work\n")
    code, out = run(repo)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "more.txt" in out, out
