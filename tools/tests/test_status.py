# Tests for status.py. Each test builds a small sample project under tmp_path
# (workflow files, and template/STATUS.md when the test needs one) and runs
# the tool there. No real project is read or written.

import importlib.util
import os
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "status.py")

SERIES = """# Series — v1.3

Version: v1.3
Tag: `on trial` · measure: episodes he keeps first time

## Steps
1. **Brief** · `foundation · 2 jobs` (ep 1, ep 2) · the master — in: his note — out: the brief — because it starts everything.
2. **Script** · `on trial` · measure: lines he rewrites · the master — in: the brief — out: the script — because.
3. **Voice** · `idea` · a helper — in: the script — out: the voice — because.

## Upgrades
- 2026-11-01 · v1.3 · first · why: start · from: ruling 1
"""

HERO = """# Hero film — v2.0

Version: v2.0
State: on trial   <run once>

## His two stops
1. The planned frames (step 9).

## Steps
1. **Intake** · `foundation · 1 job` (TetraScale) · the master — in: all — out: the read — because.
2. **The kit first** — Opus 5.5 — in: the frames — out: the kit — because.
"""

STATUS = """# Template status

## Parts
- **the act checks** · `on trial` · measure: sightings per check · files: tools/act_check.py · since 0.9.0
- **the upgrade** · `foundation · 2 jobs` · files: tools/upgrade.py · since 0.8.0

## Line limits
T6 (size-limits) fills this section.
"""


def project(tmp_path, files):
    root = tmp_path / "project"
    root.mkdir()
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8", newline="\n")
    return root


def run(root, *args):
    done = subprocess.run([sys.executable, "-B", TOOL, "--project", str(root), *args],
                          capture_output=True, text=True, encoding="utf-8")
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


def test_the_board_from_two_workflow_files_and_the_status_file(tmp_path):
    root = project(tmp_path, {"docs/series.md": SERIES, "desks/hero/workflow.md": HERO, "template/STATUS.md": STATUS})
    assert run(root).splitlines() == [
        "status board",
        "desks/hero/workflow.md · Hero film · v2.0 · on trial",
        "  step 1 · Intake · foundation · 1 job",
        "  step 2 · The kit first · untagged",
        "docs/series.md · Series · v1.3 · on trial · measure: episodes he keeps first time",
        "  step 1 · Brief · foundation · 2 jobs",
        "  step 2 · Script · on trial · measure: lines he rewrites",
        "  step 3 · Voice · idea",
        "template parts",
        "  the act checks · on trial · measure: sightings per check · since 0.9.0",
        "  the upgrade · foundation · 2 jobs · since 0.8.0",
    ]


def test_html_holds_the_one_status_board_element_with_the_same_lines(tmp_path):
    root = project(tmp_path, {"docs/series.md": SERIES, "template/STATUS.md": STATUS})
    out = run(root, "--html")
    assert out.count("<section") == 1 and out.count("data-status-board") == 1, out
    assert out.startswith('<section class="status-board" data-status-board>') and out.rstrip().endswith("</section>")
    assert "<li>step 2 · Script · on trial · measure: lines he rewrites</li>" in out, out
    assert "<li>the upgrade · foundation · 2 jobs · since 0.8.0</li>" in out, out


def test_an_untagged_step_is_listed_as_untagged(tmp_path):
    root = project(tmp_path, {"desks/hero/workflow.md": HERO})
    assert "  step 2 · The kit first · untagged" in run(root).splitlines()


def test_no_status_file_says_so_in_one_line(tmp_path):
    root = project(tmp_path, {"docs/series.md": SERIES})
    lines = run(root).splitlines()
    assert lines[-1] == "template parts: no template/STATUS.md here", lines
    assert sum("template parts" in line for line in lines) == 1


def test_an_older_state_line_with_no_tag_line_shows_its_state_as_its_tag(tmp_path):
    root = project(tmp_path, {"desks/hero/workflow.md": HERO.replace("State: on trial   <run once>",
                                                                      "State: exploring   <a candidate>")})
    assert "desks/hero/workflow.md · Hero film · v2.0 · exploring" in run(root).splitlines()


def test_blanks_template_and_untagged_files_are_not_workflow_files(tmp_path):
    root = project(tmp_path, {
        "docs/blanks/workflow.md": SERIES,
        "template/docs/method.md": SERIES,
        "docs/notes.md": "# Notes\n\nVersion: v1.0\n\n## Steps\n1. **Read** — the master\n",
        "docs/plain.md": SERIES.replace("Version: v1.3\n", ""),
    })
    assert run(root).splitlines()[:2] == ["status board", "workflows: none"]


def test_a_closed_run_with_no_workflow_is_read(tmp_path):
    spec = importlib.util.spec_from_file_location("status_for_test", TOOL)
    status = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(status)
    closed = "# Decisions\n\n## 2026-11-19 01:51 — Run 7 closed (master)\nKept.\n"

    def fact(name, files):
        (tmp_path / name).mkdir()
        return status.closed_run_without_workflow(project(tmp_path / name, files))

    assert fact("closed", {"docs/decisions.md": closed}) is True
    assert fact("archived", {"docs/decisions-archive-1.md": closed}) is True
    assert fact("has-a-file", {"docs/decisions.md": closed, "docs/series.md": SERIES}) is False
    assert fact("no-decisions", {"docs/brief.md": "# Brief\n"}) is False
    assert fact("still-open", {"docs/decisions.md": "# Decisions\n\n## 2026-11-19 01:51 — Run 8 asked for\n"}) is False
    assert fact("only-said", {"docs/decisions.md": "# Decisions\n\nRun 7 closed on the 19th.\n"}) is False
    # The board's own lines stay as they were.
    assert run(tmp_path / "closed" / "project").splitlines()[:2] == ["status board", "workflows: none"]
