# Tests for check.py. Each test makes a throwaway git repo under tmp_path
# holding a card whose gate is a few bash commands and a committed receipt,
# then runs the tool in it as a checker would, with its scratch also under
# tmp_path. No real receipt of this repo is read or changed; the one test
# that reads real cards only reads them.

import importlib.util
import os
import re
import subprocess
import sys

import pytest

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(TOOLS, "check.py")
_spec = importlib.util.spec_from_file_location("check_for_tests", TOOL)
_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_check)
find_bash = _check.find_bash  # the bash the tool runs the gate in
CARD = "card.md"
RECEIPT = "receipt.md"
RECEIPT_TEXT = "DONE — the work is done\n\n# Receipt — test — 2026-11-17\n\n## Shipped\nwork.txt\n"


def git(repo, *args):
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def card(*gate):
    """A card whose Gate section holds the given commands, each followed by ' → '."""
    spans = "; and ".join(f"`{command}` → exit 0" for command in gate)
    return (f"# piece — test — 2026-11-17\n\n## Goal\nThe work.\n\n"
            f"## Gate — run it; done means this passes\n{spans}.\n"
            f"Ablation: take `work.txt` away and it fails.\n\n"
            f"## Touches\n`work.txt` · `{RECEIPT}`\n")


@pytest.fixture
def make_repo(tmp_path):
    def make(*gate, card_text=None):
        repo = tmp_path / "branch"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Test")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "config", "core.autocrlf", "false")
        (repo / "work.txt").write_text("committed\n", encoding="utf-8")
        (repo / CARD).write_text(card_text if card_text is not None else card(*gate),
                                 encoding="utf-8", newline="\n")
        (repo / RECEIPT).write_text(RECEIPT_TEXT, encoding="utf-8", newline="\n")
        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "the work")
        return repo
    return make


@pytest.fixture
def scratch(tmp_path):
    return tmp_path / "scratch"


def run(repo, scratch, *extra):
    done = subprocess.run(
        [sys.executable, "-B", TOOL, RECEIPT, "--card", CARD,
         "--who", "a checker, own session", "--scratch", str(scratch), *extra],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return done.returncode, done.stdout + done.stderr


def written(repo):
    """The lines the tool appended after the receipt's own text."""
    text = (repo / RECEIPT).read_text(encoding="utf-8")
    assert text.startswith(RECEIPT_TEXT), text
    return text[len(RECEIPT_TEXT):].strip("\n").splitlines()


def copy_path(lines):
    match = re.match(r"From a clean copy: (.+?) · ", lines[3])
    assert match, lines
    return match.group(1)


def test_a_passing_gate_writes_the_four_lines_with_exit_0(make_repo, scratch):
    repo = make_repo("test -f work.txt", "grep -q committed work.txt")
    code, out = run(repo, scratch)
    assert code == 0, out
    lines = written(repo)
    assert len(lines) == 4, lines
    assert re.fullmatch(r"## Checker run \d{4}-\d\d-\d\d — a checker, own session", lines[0]), lines
    assert lines[1] == f"Commit: {git(repo, 'rev-parse', 'HEAD')}", lines
    assert lines[2] == "Exit code: 0", lines
    assert lines[3].endswith(" · 2 commands · exit codes 0, 0"), lines
    assert not any(line.startswith("Verdict") for line in lines), lines


def test_a_failing_command_writes_its_exit_code_and_the_list(make_repo, scratch):
    repo = make_repo("true", "exit 3", "exit 5", "true")
    code, out = run(repo, scratch)
    assert code == 1, out
    lines = written(repo)
    assert lines[2] == "Exit code: 3", lines
    assert lines[3].endswith(" · 4 commands · exit codes 0, 3, 5, 0"), lines


def test_a_gate_leaning_on_an_untracked_file_fails_in_the_clean_copy(make_repo, scratch):
    repo = make_repo("test -f untracked.txt")
    (repo / "untracked.txt").write_text("nobody committed me\n", encoding="utf-8")
    here = subprocess.run([find_bash(), "-c", "test -f untracked.txt"], cwd=repo)
    assert here.returncode == 0  # it passes in the working folder
    code, out = run(repo, scratch)
    assert code == 1, out
    lines = written(repo)
    assert lines[2] != "Exit code: 0", lines
    assert lines[3].endswith(" · 1 command · exit codes 1"), lines


def test_a_change_waiting_in_the_worktree_is_not_in_the_copy(make_repo, scratch):
    repo = make_repo("grep -qx committed work.txt")
    (repo / "work.txt").write_text("changed, not committed\n", encoding="utf-8")
    code, out = run(repo, scratch)
    assert code == 0, out
    assert written(repo)[2] == "Exit code: 0"
    assert (repo / "work.txt").read_text(encoding="utf-8") == "changed, not committed\n"


def test_the_gate_runs_in_order_with_S_set_to_the_scratch(make_repo, scratch):
    repo = make_repo('echo one >> "$S/order.txt"', 'echo two >> "$S/order.txt"')
    code, out = run(repo, scratch)
    assert code == 0, out
    assert (scratch / "order.txt").read_text(encoding="utf-8").split() == ["one", "two"]


def test_each_command_output_is_printed(make_repo, scratch):
    repo = make_repo("echo the-gate-speaks")
    code, out = run(repo, scratch)
    assert code == 0, out
    assert "the-gate-speaks" in out, out
    assert "Exit code: 0" in out, out


def test_dry_prints_the_commands_and_runs_nothing(make_repo, scratch):
    repo = make_repo('touch "$S/ran"', "exit 7")
    code, out = run(repo, scratch, "--dry")
    assert code == 0, out
    assert 'touch "$S/ran"' in out and "exit 7" in out, out
    assert not scratch.exists()
    assert (repo / RECEIPT).read_text(encoding="utf-8") == RECEIPT_TEXT


def test_a_card_with_no_gate_is_refused(make_repo, scratch):
    repo = make_repo(card_text="# piece\n\n## Gate — run it\nrun the tests and see.\n\n"
                               "## Touches\n`work.txt` → here\n")
    code, out = run(repo, scratch)
    assert code == 1, out
    assert out.startswith(f"REFUSE: {CARD} has no gate check.py can read"), out
    assert (repo / RECEIPT).read_text(encoding="utf-8") == RECEIPT_TEXT
    assert not scratch.exists()


def test_a_gate_typed_on_the_command_line_is_not_taken(make_repo, scratch):
    repo = make_repo("true")
    code, out = run(repo, scratch, "--gate", "true")
    assert code != 0, out
    assert (repo / RECEIPT).read_text(encoding="utf-8") == RECEIPT_TEXT


def test_the_copy_is_gone_after_the_run(make_repo, scratch):
    repo = make_repo("test -f work.txt")
    code, out = run(repo, scratch)
    assert code == 0, out
    copy = copy_path(written(repo))
    assert os.path.dirname(copy) == str(scratch).replace("\\", "/")
    assert not os.path.exists(copy)
    assert os.listdir(scratch) == []


def test_keep_leaves_the_copy(make_repo, scratch):
    repo = make_repo("test -f work.txt")
    code, out = run(repo, scratch, "--keep")
    assert code == 0, out
    copy = copy_path(written(repo))
    assert os.path.isfile(os.path.join(copy, "work.txt"))


def test_the_receipt_other_lines_untouched_and_nothing_committed(make_repo, scratch):
    repo = make_repo("true")
    head = git(repo, "rev-parse", "HEAD")
    code, out = run(repo, scratch)
    assert code == 0, out
    written(repo)  # the receipt's own text is still its start, byte for byte
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == f"M {RECEIPT}"


def real_card(name):
    """A card of this house's template desk, if this copy sits in the house."""
    folder = TOOLS
    for _ in range(4):
        path = os.path.join(folder, "desks", "template", "docs", "cards", name)
        if os.path.isfile(path):
            return path
        folder = os.path.dirname(folder)
    pytest.skip(f"{name} is not here (a stamped project holds no template desk)")


@pytest.mark.parametrize("name, count, first", [
    ("2026-11-12-upgrade-tool.md", 2, "python3.11 -B -m pytest template/tools/tests -q"),
    ("2026-11-12-version-0-8-0.md", 7, 'test "$(cat template/VERSION)" = 0.8.0'),
    ("2026-11-17-act-checks.md", 3, "python3.11 -B -m pytest template/tools/tests -q"),
])
def test_dry_reads_real_cards_gates(tmp_path, name, count, first):
    path = real_card(name)
    done = subprocess.run([sys.executable, "-B", TOOL, "unused-receipt.md", "--card", path, "--dry"],
                          cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, done.stdout
    found = re.findall(r"^  \d+\. (.*)$", done.stdout, re.MULTILINE)
    assert len(found) == count, done.stdout
    assert found[0].startswith(first), found
    assert not any(command in ("OK", "SETTINGS KEPT", "SETTINGS OK", "0") for command in found), found
