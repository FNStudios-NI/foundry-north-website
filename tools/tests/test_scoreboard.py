# Tests for scoreboard.py. Each test builds a sample project under tmp_path
# (a closing entry, a run record and its plan, two cards, a lessons file with
# a "[new …]" mark, a retired line) and a counter file in a LOCALAPPDATA
# folder under tmp_path, and runs the tool there. No real project, record or
# counter of this machine is read or changed.
#   python -B -m pytest template/tools/tests/test_scoreboard.py -q

import os
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scoreboard.py")

HEADER = ("| run | closed | template | made | enjoyment | his questions | his minutes | finished | surprises "
          "| sightings | lessons landed | lessons retired | usage per finished piece |")

DECISIONS = """# Decisions — sample-house

## 2026-11-08 09:00 — Plan signed for run 3
His rulings:

| # | Ruled | His letter and words | Why | Undo |
|---|---|---|---|---|
| 1 | A ruling of the sign-off, not the close | a | x | y |

## 2026-11-10 18:30 — Run 3 closed (review master)
Page: `docs/runs/3/review.html`.

His rulings:

| # | Ruled | His letter and words | Why | Undo |
|---|---|---|---|---|
| 1 | The look stays | a — "yes" | x | y |
| 2 | The list is kept by hand | b — none | x | y |
| 3 | Pieces stay | none named | x | y |

My calls (not ruled by him):

| # | Call | Why | Undo |
|---|---|---|---|
| 1 | A call | x | y |
| 2 | Another | x | y |

Enjoyment: 5 — "good".
"""

RUN = """# Run 3 — sample-house

## Go
- Start: 2026-11-09 09:00

## Unforeseen key points
- <hh:mm> · <the key point> · chose: <…> · turned down: <each option> · why: <one line>
- 11:00 · the feed was down · chose: wait · turned down: none · why: x

## Blockers
- 12:00 · a password · ways through: his · my recommendation: his

## Merges
- <hh:mm> · <card> · squash <commit> · undo: `git revert <commit>`
- 10:00 · alpha · squash 1111111 · undo: `git revert 1111111`
- 14:00 · beta · squash 2222222 · undo: `git revert 2222222`
"""

PLAN = "# Plan\n\n## The path\n- 1 · alpha · template\n- 2 · beta · template\n- 3 · gamma · template\n"

COUNTER = [
    "2026-11-09 08:59:59 · sample-house · heredoc-write · warn · s1 · cat <<EOF > a",      # before Go
    "2026-11-09 09:30:00 · sample-house · heredoc-write · warn · s1 · cat <<EOF > b",
    "2026-11-10 12:00:00 · sample-house · wildcard-delete · warn · s2 · rm -rf /tmp/x*",
    "2026-11-10 18:30:40 · sample-house · heredoc-write · warn · s3 · cat <<EOF > c",
    "2026-11-10 18:31:00 · sample-house · path-in-subshell · warn · s3 · $(a.txt)",       # after the close
]

LESSONS = """# Lessons

- L001 · 2026-11-09 10:00 · worker · works · the rule held · file: worker-rules.md · "Claim the seat first." · sort: routine
- L002 · 2026-11-09 11:00 · worker · broke · a second · file: worker-rules.md · "Run the gate." · sort: routine
"""

RULES = ("# Worker rules\n\nClaim the seat first. [new L001 2026-11-09]\n"
         "An older one. [new L000 2026-11-01]\nRun the gate.\n")

RETIRED = ("# Retired\n\n- 2026-11-10 · tracks.md · \"An old line.\" · why: unused · undo: git revert 3333333\n"
           "- 2026-10-01 · tracks.md · \"Older.\" · why: unused · undo: git revert 4444444\n")


def project(tmp_path, closed=True):
    root = tmp_path / "sample-house"
    (root / "docs" / "runs" / "3").mkdir(parents=True)
    (root / "docs" / "cards").mkdir()
    (root / "project.yaml").write_text("name: sample-house\ntemplate_version: 0.9.0\n", encoding="utf-8")
    text = DECISIONS if closed else DECISIONS.split("## 2026-11-10 18:30")[0]
    (root / "docs" / "decisions.md").write_text(text, encoding="utf-8")
    (root / "docs" / "runs" / "3" / "run.md").write_text(RUN, encoding="utf-8")
    (root / "docs" / "runs" / "3" / "plan-signed.md").write_text(PLAN, encoding="utf-8")
    for card, piece in (("alpha", 1), ("beta", 2)):
        (root / "docs" / "cards" / f"2026-11-09-{card}.md").write_text(
            f"# {card}\nOrder: asks entry · run 3, piece {piece}\n", encoding="utf-8")
    (root / "docs" / "lessons.md").write_text(LESSONS, encoding="utf-8")
    (root / "worker-rules.md").write_text(RULES, encoding="utf-8")
    (root / "docs" / "retired.md").write_text(RETIRED, encoding="utf-8")
    local = tmp_path / "local"
    (local / "agentic-meta" / "act-checks").mkdir(parents=True)
    (local / "agentic-meta" / "act-checks" / "sample-house.log").write_text("\n".join(COUNTER) + "\n", encoding="utf-8")
    return root, local


def run(root, local, *args):
    env = dict(os.environ, LOCALAPPDATA=str(local))
    done = subprocess.run([sys.executable, "-B", TOOL, *args], cwd=root, env=env,
                          capture_output=True, encoding="utf-8")
    return done.returncode, done.stdout


def board(root):
    return (root / "docs" / "scoreboard.md").read_text(encoding="utf-8")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def test_a_row_from_a_sample_project_has_each_column_right(tmp_path):
    root, local = project(tmp_path)
    code, out = run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5", "--minutes", "12")
    assert code == 0, out
    lines = board(root).splitlines()
    assert lines[0] == HEADER and lines[1].startswith("|---|")
    row = dict(zip(cells(HEADER), cells(lines[2])))
    assert row == {
        "run": "3", "closed": "2026-11-10 18:30", "template": "—", "made": "4", "enjoyment": "5",
        "his questions": "3", "his minutes": "12", "finished": "2/3", "surprises": "2",
        "sightings": "heredoc-write 2, wildcard-delete 1", "lessons landed": "1", "lessons retired": "1",
        "usage per finished piece": "—"}
    assert len(lines) == 3


def test_taps_and_minutes_not_given_read_a_dash(tmp_path):
    root, local = project(tmp_path)
    assert run(root, local, "--run", "3")[0] == 0
    row = dict(zip(cells(HEADER), cells(board(root).splitlines()[2])))
    assert row["made"] == row["enjoyment"] == row["his minutes"] == "—"


def test_a_tap_outside_one_to_five_is_refused(tmp_path):
    root, local = project(tmp_path)
    code, out = run(root, local, "--run", "3", "--made", "6", "--enjoyment", "5")
    assert code == 1 and out.startswith("REFUSE: ") and "--made" in out
    assert not (root / "docs" / "scoreboard.md").exists()


def test_a_second_row_for_the_same_run_is_refused(tmp_path):
    root, local = project(tmp_path)
    assert run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5")[0] == 0
    before = board(root)
    code, out = run(root, local, "--run", "3", "--made", "2", "--enjoyment", "2")
    assert code == 1 and out.startswith("REFUSE: ") and "already has its row" in out
    assert board(root) == before


def test_a_run_with_no_closing_entry_is_refused(tmp_path):
    root, local = project(tmp_path, closed=False)
    code, out = run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5")
    assert code == 1 and out.startswith("REFUSE: ") and "no closing entry" in out
    assert not (root / "docs" / "scoreboard.md").exists()


def test_no_counter_file_reads_none(tmp_path):
    root, local = project(tmp_path)
    os.remove(local / "agentic-meta" / "act-checks" / "sample-house.log")
    assert run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5")[0] == 0
    assert dict(zip(cells(HEADER), cells(board(root).splitlines()[2])))["sightings"] == "none"


def seven_rows(root):
    rows = [f"| {i} | 2026-11-{i:02d} 18:00 | 0.9.0 | 4 | 5 | 1 | — | 1/1 | 0 | none | 0 | 0 | — |" for i in range(1, 8)]
    text = HEADER + "\n|" + "---|" * 13 + "\n" + "\n".join(rows) + "\n"
    (root / "docs" / "scoreboard.md").write_text(text, encoding="utf-8")
    return text, rows


def test_last_five_of_seven_rows_writes_nothing(tmp_path):
    root, local = project(tmp_path)
    text, rows = seven_rows(root)
    code, out = run(root, local, "--last", "5")
    assert code == 0
    lines = out.splitlines()
    assert lines[0] == HEADER and lines[2:] == rows[2:]
    assert board(root) == text


def test_last_five_as_html_is_one_scoreboard_section(tmp_path):
    root, local = project(tmp_path)
    text, rows = seven_rows(root)
    code, out = run(root, local, "--last", "5", "--html")
    assert code == 0
    assert out.count("<section data-scoreboard>") == 1 and out.strip().endswith("</section>")
    assert out.count("<tr><td>") == 5 and "<td>3</td>" in out and "<tr><td>2</td>" not in out
    assert board(root) == text


def test_the_next_run_is_appended_under_the_last(tmp_path):
    root, local = project(tmp_path)
    text, rows = seven_rows(root)
    (root / "docs" / "runs" / "8").mkdir()
    (root / "docs" / "runs" / "8" / "run.md").write_text("# Run 8 — sample-house\n\n## Go\n- Start: 2026-11-11 09:00\n",
                                                         encoding="utf-8")
    with open(root / "docs" / "decisions.md", "a", encoding="utf-8") as f:
        f.write("\n## 2026-11-12 10:00 — Run 8 closed (review master)\nHis rulings:\n\n| # | Ruled |\n|---|---|\n| 1 | x |\n")
    assert run(root, local, "--run", "8", "--made", "3", "--enjoyment", "4")[0] == 0
    lines = board(root).splitlines()
    assert lines[:9] == text.splitlines() and len(lines) == 10
    assert cells(lines[9])[:6] == ["8", "2026-11-12 10:00", "—", "3", "4", "1"]
    assert cells(lines[9])[7] == "0/0"


def git(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def repo(root):
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "commit.gpgsign", "false")


def landing(root, name):
    """One commit of a new file; its short name, as land.py writes it under ## Merges."""
    (root / name).write_text(name, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-q", "-m", name)
    return git(root, "rev-parse", "--short=7", "HEAD")


def merges(root, first, last, more=""):
    record = root / "docs" / "runs" / "3" / "run.md"
    text = record.read_text(encoding="utf-8").replace("1111111", first).replace("2222222", last)
    record.write_text(text + more, encoding="utf-8")


def template_cell(root, local):
    assert run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5")[0] == 0
    return dict(zip(cells(HEADER), cells(board(root).splitlines()[2])))["template"]


def test_the_template_column_is_the_tag_of_the_runs_last_landing(tmp_path):
    root, local = project(tmp_path / "tagged")
    (root / "project.yaml").write_text("name: sample-house\ntemplate_version: 9.9.9\n", encoding="utf-8")
    repo(root)
    first = landing(root, "first")
    git(root, "tag", "template/0.8.0")
    git(root, "tag", "other/5.0.0")
    last = landing(root, "last")  # carries 0.8.0: no tag of its own
    later = landing(root, "later")
    git(root, "tag", "template/0.9.1")
    # A later commit named in free words under ## Merges is not a landing of the run.
    merges(root, first, last, f"- 15:00 · a note: this was not in squash {later}'s message\n")
    assert template_cell(root, local) == "0.8.0"

    root, local = project(tmp_path / "untagged")  # a squash with no tag behind it
    repo(root)
    merges(root, landing(root, "first"), landing(root, "last"))
    assert template_cell(root, local) == "—"

    root, local = project(tmp_path / "unlanded")  # no squash at all
    repo(root)
    landing(root, "first")
    git(root, "tag", "template/0.8.0")
    record = root / "docs" / "runs" / "3" / "run.md"
    record.write_text(RUN.split("## Merges")[0] + "## Merges\n", encoding="utf-8")
    assert template_cell(root, local) == "—"


def usage_cell(root, local, go_lines):
    record = root / "docs" / "runs" / "3" / "run.md"
    text = record.read_text(encoding="utf-8")
    record.write_text(text.replace("- Start: 2026-11-09 09:00\n", "- Start: 2026-11-09 09:00\n" + go_lines), encoding="utf-8")
    assert run(root, local, "--run", "3", "--made", "4", "--enjoyment", "5")[0] == 0
    return dict(zip(cells(HEADER), cells(board(root).splitlines()[2])))["usage per finished piece"]


def test_usage_is_the_weeks_points_per_finished_piece(tmp_path):
    both = "- 09:00 · Week read at Go: {}%\n- 18:00 · Week read at the close: {}%\n"
    for name, go, close, cell in (("three", 10, 13, "1.5% of his week"), ("rounded", 10, 11, "0.5% of his week"),
                                  ("level", 10, 10, "0.0% of his week")):
        root, local = project(tmp_path / name)
        assert usage_cell(root, local, both.format(go, close)) == cell


def test_usage_is_a_dash_when_a_reading_is_missing(tmp_path):
    go, close = "- 09:00 · Week read at Go: 10%\n", "- 18:00 · Week read at the close: 13%\n"
    free_words = "- 09:00 · Window read at Go: five-hour 23% used; week 8% used\n"
    for name, lines in (("no-close", go), ("no-go", close), ("neither", ""), ("free-words", free_words),
                        ("reset", go.replace("10%", "60%") + close)):
        root, local = project(tmp_path / name)
        assert usage_cell(root, local, lines) == "—", name
    root, local = project(tmp_path / "no-piece")  # both readings, nothing finished
    record = root / "docs" / "runs" / "3" / "run.md"
    record.write_text(RUN.split("## Merges")[0] + "## Merges\n", encoding="utf-8")
    assert usage_cell(root, local, go + close) == "—"
