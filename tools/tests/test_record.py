# Tests for record.py. Each test writes a throwaway run record under
# tmp_path and runs the tool there, as the master would from the project's
# top folder. No real record of this repo is read or changed.

import datetime
import os
import re
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record.py")

RUN = ("# Run 2 — test\n\n"
       "## Orders\nOne line per order.\n- 06:58 · template · tasks 1 · the aim\n\n"
       "## Merges\nOne line per merge into the try-it build, with its undo.\n\n"
       "## Handover\nWritten before the context fills.\n")


def project(tmp_path):
    for n, text in [(1, "# Run 1 — test\n\n## Merges\n"), (2, RUN)]:
        folder = tmp_path / "docs" / "runs" / str(n)
        folder.mkdir(parents=True)
        (folder / "run.md").write_text(text, encoding="utf-8", newline="\n")
    return tmp_path


def run(folder, *args):
    done = subprocess.run([sys.executable, "-B", TOOL, *args], cwd=folder, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def clock():
    return datetime.datetime.now().strftime("%H:%M")


def test_writes_under_the_named_section_of_the_newest_run_with_the_clock(tmp_path):
    folder = project(tmp_path)
    before = clock()
    code, out = run(folder, "--section", "Merges", "piece · squash abc1234 · undo: `git revert abc1234`")
    after = clock()
    assert code == 0, out
    assert out.startswith("RECORDED"), out
    lines = (folder / "docs/runs/2/run.md").read_text(encoding="utf-8").splitlines()
    merges = lines.index("## Merges")
    written = lines[merges + 2]
    match = re.fullmatch(r"- (\d\d:\d\d) · piece · squash abc1234 · undo: `git revert abc1234`", written)
    assert match, written
    assert match.group(1) in (before, after), (match.group(1), before, after)
    # The blank before the next heading stays, and the next section is untouched.
    assert lines[merges + 3] == "" and lines[merges + 4] == "## Handover", lines
    assert (folder / "docs/runs/1/run.md").read_text(encoding="utf-8") == "# Run 1 — test\n\n## Merges\n"


def test_appends_after_the_last_line_under_the_section(tmp_path):
    folder = project(tmp_path)
    code, out = run(folder, "--section", "Orders", "template · tasks 2 · the next aim",
                    "--file", "docs/runs/2/run.md")
    assert code == 0, out
    lines = (folder / "docs/runs/2/run.md").read_text(encoding="utf-8").splitlines()
    orders = lines.index("## Orders")
    assert lines[orders + 2] == "- 06:58 · template · tasks 1 · the aim", lines
    assert re.fullmatch(r"- \d\d:\d\d · template · tasks 2 · the next aim", lines[orders + 3]), lines
    assert lines[orders + 4] == "", lines


def test_an_unknown_section_is_refused_and_the_file_is_unchanged(tmp_path):
    folder = project(tmp_path)
    record = folder / "docs/runs/2/run.md"
    before = record.read_bytes()
    code, out = run(folder, "--section", "Mergers", "piece · squash abc1234")
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert "Mergers" in out, out
    assert record.read_bytes() == before


# --entry and --last: a decisions file, a log or a desk's asks.md, named with --file.

DECISIONS = ("# Decisions\n\n"
             "## 2026-10-01 09:00 — An old entry (test)\nPage: no page.\n")

ASKS = ("# Asks\n\n"
        "## 2026-10-01 09:00 · master → test · ORDER\nTasks: 1 · aim: the old aim\n"
        "- **09:05 — PLAN (test):** one card\n\n"
        "## 2026-10-02 10:00 · master → test · ORDER\nTasks: 2 · aim: the new aim\n")


def page(tmp_path, name, text, newline="\n"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8", newline=newline)
    return path


def read(path):
    return path.read_bytes().decode("utf-8")


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def test_entry_writes_a_new_heading_at_the_files_end_with_the_clocks_date_and_time(tmp_path):
    decisions = page(tmp_path, "decisions.md", DECISIONS)
    before = stamp()
    code, out = run(tmp_path, "--file", "decisions.md", "--entry", "A new entry (test)")
    after = stamp()
    assert code == 0, out
    assert out.startswith("RECORDED"), out
    text = read(decisions)
    # The old entry stays as it was, then one blank line, then the heading, the file's last line.
    assert text.startswith(DECISIONS + "\n## "), text
    match = re.fullmatch(r"## (\d{4}-\d\d-\d\d \d\d:\d\d) — A new entry \(test\)\n", text[len(DECISIONS) + 1:])
    assert match, text
    assert match.group(1) in (before, after), (match.group(1), before, after)


def test_entry_in_a_file_named_asks_md_takes_the_asks_form(tmp_path):
    asks = page(tmp_path, "asks.md", ASKS)
    code, out = run(tmp_path, "--file", "asks.md", "--entry", "master → test · GO")
    assert code == 0, out
    assert out.startswith("RECORDED"), out
    text = read(asks)
    assert text.startswith(ASKS + "\n## "), text
    assert re.fullmatch(r"## \d{4}-\d\d-\d\d \d\d:\d\d · master → test · GO\n", text[len(ASKS) + 1:]), text


def test_last_with_who_writes_a_reply_under_the_newest_asks_entry(tmp_path):
    asks = page(tmp_path, "asks.md", ASKS)
    before = clock()
    code, out = run(tmp_path, "--file", "asks.md", "--last", "--who", "PLAN (test)", "three cards")
    after = clock()
    assert code == 0, out
    assert out.startswith("RECORDED"), out
    text = read(asks)
    # After the last line of the newest entry, and the older entry untouched.
    assert text.startswith(ASKS + "- **"), text
    match = re.fullmatch(r"- \*\*(\d\d:\d\d) — PLAN \(test\):\*\* three cards\n", text[len(ASKS):])
    assert match, text
    assert match.group(1) in (before, after), (match.group(1), before, after)


def test_entry_is_refused_in_a_run_record_and_the_file_is_unchanged(tmp_path):
    folder = project(tmp_path)
    record = folder / "docs/runs/2/run.md"
    before = record.read_bytes()
    # Named with --file, and with no --file (the newest run's record).
    for args in (["--file", "docs/runs/2/run.md", "--entry", "A heading nobody planned"],
                 ["--entry", "A heading nobody planned"]):
        code, out = run(folder, *args)
        assert code == 1, out
        assert out.startswith("REFUSE"), out
        assert record.read_bytes() == before


def test_windows_line_endings_are_kept_after_entry_and_after_last(tmp_path):
    decisions = page(tmp_path, "decisions.md", DECISIONS, newline="\r\n")
    code, out = run(tmp_path, "--file", "decisions.md", "--entry", "A new entry (test)")
    assert code == 0, out
    code, out = run(tmp_path, "--file", "decisions.md", "--last", "the entry's first line")
    assert code == 0, out
    raw = decisions.read_bytes()
    assert raw.startswith(DECISIONS.replace("\n", "\r\n").encode("utf-8") + b"\r\n## "), raw
    assert raw.count(b"\r\n") == raw.count(b"\n") == DECISIONS.count("\n") + 3, raw
    assert raw.endswith(b"\r\n") and b"\r\r" not in raw, raw
    # The plain form of a --last line, under the heading --entry made.
    lines = raw.decode("utf-8").split("\r\n")
    assert re.fullmatch(r"## \d{4}-\d\d-\d\d \d\d:\d\d — A new entry \(test\)", lines[-3]), lines
    assert re.fullmatch(r"- \d\d:\d\d · the entry's first line", lines[-2]), lines


def test_a_missing_file_is_refused_and_not_made(tmp_path):
    for args in (["--file", "decisions.md", "--entry", "A new entry (test)"],
                 ["--file", "decisions.md", "--last", "a line"],
                 ["--file", "decisions.md", "--section", "Merges", "a line"]):
        code, out = run(tmp_path, *args)
        assert code == 1, out
        assert out.startswith("REFUSE"), out
        assert not (tmp_path / "decisions.md").exists()
    assert list(tmp_path.iterdir()) == []


def test_last_is_refused_with_no_file_and_the_run_record_is_unchanged(tmp_path):
    folder = project(tmp_path)
    record = folder / "docs/runs/2/run.md"
    before = record.read_bytes()
    code, out = run(folder, "--last", "a line for whichever section comes last")
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert record.read_bytes() == before
