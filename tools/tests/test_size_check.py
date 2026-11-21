# Tests for size_check.py. Each test builds a small sample folder under
# tmp_path (a STATUS.md with its ## Line limits and the files it names) and
# runs the tool on it. Nothing outside the temp folder is read but the
# template's own STATUS.md, read in the last test only.

import os
import re
import subprocess
import sys

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "size_check.py")
TEMPLATE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STATUS = ("# Template status\n\n## Parts\n- **a part** · `on trial` · measure: x · files: tools/x.py · since 0.9.0\n\n"
          "## Line limits\n- `tracks.md` · 4 lines\n- `roles/worker.md` · 2 lines\n- `pages.md` · 3 lines\n")


def sample(root, status=STATUS, sizes=None):
    root.mkdir(parents=True, exist_ok=True)
    if status is not None:
        (root / "STATUS.md").write_text(status, encoding="utf-8", newline="\n")
    for path, n in (sizes or {}).items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes("".join(f"line {i}\r\n" for i in range(n)).encode("utf-8"))
    return root


def run(*args, cwd=None):
    done = subprocess.run([sys.executable, "-B", TOOL, *args], cwd=cwd, capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).strip()


def test_files_at_or_under_their_limits_are_size_ok(tmp_path):
    root = sample(tmp_path / "t", sizes={"tracks.md": 4, "roles/worker.md": 1, "pages.md": 3})
    assert run("--root", str(root)) == (0, "SIZE OK")


def test_a_file_over_its_limit_is_refused_naming_its_lines_over(tmp_path):
    root = sample(tmp_path / "t", sizes={"tracks.md": 5, "roles/worker.md": 2, "pages.md": 3})
    assert run("--root", str(root)) == (1, "REFUSE: tracks.md is 5 lines, 1 over its limit of 4")


def test_each_file_over_has_its_own_line(tmp_path):
    root = sample(tmp_path / "t", sizes={"tracks.md": 9, "roles/worker.md": 2, "pages.md": 4})
    code, out = run("--root", str(root))
    assert code == 1
    assert out.splitlines() == ["REFUSE: tracks.md is 9 lines, 5 over its limit of 4",
                                "REFUSE: pages.md is 4 lines, 1 over its limit of 3"]


@pytest.mark.parametrize("status", [None, "# Template status\n\n## Parts\n- **a part** · `idea` · files: x · since 0.9.0\n"])
def test_no_status_file_or_no_line_limits_is_said_and_passes(tmp_path, status):
    root = sample(tmp_path / "t", status=status, sizes={"tracks.md": 900})
    assert run("--root", str(root)) == (0, "no line limits here")


def test_the_default_root_is_template_at_the_projects_top(tmp_path):
    top = tmp_path / "p"
    sample(top / "template", sizes={"tracks.md": 5})
    subprocess.run(["git", "init", "-q", str(top)], check=True, capture_output=True)
    (top / "docs").mkdir()
    assert run(cwd=top / "docs") == (1, "REFUSE: tracks.md is 5 lines, 1 over its limit of 4")
    assert run(cwd=tmp_path) == (0, "no line limits here")  # no template/ there


def test_the_templates_limits_are_contract_5s_ten():
    status = os.path.join(TEMPLATE, "STATUS.md")
    if not os.path.isfile(status):
        pytest.skip("STATUS.md is the template's own and is not stamped into projects")
    with open(status, encoding="utf-8") as f:
        text = f.read()
    limits = re.findall(r"^- `([^`]+)` · (\d+) lines\s*$", text.split("## Line limits", 1)[1], re.M)
    assert limits == [("tracks.md", "204"), ("worker-rules.md", "70"), ("operator.md", "78"), ("pages.md", "216"),
                      ("roles/master.md", "63"), ("roles/worker.md", "31"), ("roles/checker.md", "28"),
                      ("roles/reader.md", "17"), ("dot-claude/skills/conductor/SKILL.md", "260"),
                      ("dot-claude/skills/run/SKILL.md", "180")]
