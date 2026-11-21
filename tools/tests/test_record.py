# Tests for record.py. Each test writes a throwaway run record under
# tmp_path and runs the tool there, as the master would from the project's
# top folder. No real record of this repo is read or changed.

import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

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


# A typed time at the start of a text or a title is refused: the tool stamps the time.

SECTION = "# t\n\n## A\n- 03:33 · an old line\n"


def test_typed_time_at_the_start_of_a_section_line_is_refused_and_the_file_is_unchanged(tmp_path):
    record = page(tmp_path, "r.md", SECTION)
    before = record.read_bytes()
    code, out = run(tmp_path, "--file", "r.md", "--section", "A", "03:39 · something")
    assert code == 1, out
    assert out.startswith('REFUSE: "03:39" is typed at the start of the text'), out
    assert record.read_bytes() == before


def test_typed_time_after_a_date_in_a_last_line_is_refused_with_and_without_who(tmp_path):
    asks = page(tmp_path, "asks.md", ASKS)
    before = asks.read_bytes()
    for args in (["--last", "2026-10-28 09:22 merged"],
                 ["--last", "--who", "PLAN (test)", "2026-10-28 09:22 merged"]):
        code, out = run(tmp_path, "--file", "asks.md", *args)
        assert code == 1, out
        assert out.startswith("REFUSE"), out
        assert "09:22" in out, out
        assert asks.read_bytes() == before


def test_typed_time_at_the_start_of_an_entry_title_is_refused_and_the_file_is_unchanged(tmp_path):
    decisions = page(tmp_path, "decisions.md", DECISIONS)
    before = decisions.read_bytes()
    code, out = run(tmp_path, "--file", "decisions.md", "--entry", "10:40 — a title")
    assert code == 1, out
    assert out.startswith('REFUSE: "10:40"'), out
    assert decisions.read_bytes() == before


def test_typed_time_in_bold_at_the_start_is_refused(tmp_path):
    record = page(tmp_path, "r.md", SECTION)
    before = record.read_bytes()
    code, out = run(tmp_path, "--file", "r.md", "--section", "A", "**03:39** something")
    assert code == 1, out
    assert out.startswith('REFUSE: "03:39"'), out
    assert record.read_bytes() == before


def test_typed_time_absent_or_later_in_the_text_is_recorded(tmp_path):
    record = page(tmp_path, "r.md", SECTION)
    for text in ("something", "merged at 10:40"):
        code, out = run(tmp_path, "--file", "r.md", "--section", "A", text)
        assert code == 0, out
        assert out.startswith("RECORDED"), out
        assert re.fullmatch(r"- \d\d:\d\d · " + re.escape(text), read(record).splitlines()[-1]), read(record)


def test_typed_time_needs_two_minute_digits_so_a_ratio_is_recorded(tmp_path):
    record = page(tmp_path, "r.md", SECTION)
    code, out = run(tmp_path, "--file", "r.md", "--section", "A", "3:2 frame")
    assert code == 0, out
    assert re.fullmatch(r"- \d\d:\d\d · 3:2 frame", read(record).splitlines()[-1]), read(record)


# --lesson: one numbered lesson as the last line of docs/lessons.md. Each test
# makes its own small project under tmp_path, with its own lessons file.

LESSONS = "# Lessons\n\n"


def lessons_project(tmp_path, text=LESSONS):
    (tmp_path / "docs" / "blanks").mkdir(parents=True)
    (tmp_path / "docs" / "blanks" / "card.md").write_text("# card\n", encoding="utf-8", newline="\n")
    lessons = tmp_path / "docs" / "lessons.md"
    lessons.write_text(text, encoding="utf-8", newline="\n")
    return lessons


def lesson_args(kind="change", about="docs/blanks/card.md", what="the gate ran twice", seen=None):
    args = ["--lesson", what, "--from", "run 4", "--kind", kind, "--about", about, "--line", "Run the gate once."]
    return args + (["--seen", seen] if seen is not None else [])


def refused(tmp_path, lessons, *args):
    before = lessons.read_bytes()
    code, out = run(tmp_path, *args)
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert lessons.read_bytes() == before
    assert not (tmp_path / "docs" / "lessons.md.lock").exists()
    return out


def test_lesson_of_each_kind_is_written_numbered_in_order_and_stamped(tmp_path):
    lessons = lessons_project(tmp_path)
    before = stamp()
    for kind, seen in (("change", None), ("works", "his verdict: \"that one works\""),
                       ("misfire", "2 of 5 failed"), ("track", None)):
        code, out = run(tmp_path, *lesson_args(kind, seen=seen))
        assert code == 0, out
        assert out.startswith("RECORDED: docs/lessons.md") and "- L00" in out, out
    after = stamp()
    lines = read(lessons).splitlines()
    assert lines[:2] == ["# Lessons", ""], lines
    body = lines[2:]
    assert len(body) == 4, lines
    form = r'- (L\d{3}) · (\d{4}-\d\d-\d\d \d\d:\d\d) · run 4 · (\w+) · the gate ran twice · ' \
           r'file: docs/blanks/card\.md · "Run the gate once\." · sort: template( · seen: .+)?'
    found = [re.fullmatch(form, line) for line in body]
    assert all(found), body
    assert [m.group(1) for m in found] == ["L001", "L002", "L003", "L004"], body
    assert [m.group(3) for m in found] == ["change", "works", "misfire", "track"], body
    assert all(m.group(2) in (before, after) for m in found), (body, before, after)
    assert body[1].endswith(' · seen: his verdict: "that one works"'), body
    assert body[2].endswith(" · seen: 2 of 5 failed"), body
    assert found[0].group(4) is None and found[3].group(4) is None, body


def test_lesson_number_is_one_past_the_highest_in_the_file(tmp_path):
    old = ('- L007 · 2026-11-01 10:00 · planning · change · a · file: template · "b"\n'
           '- L041 · 2026-11-02 10:00 · session · change · a · file: template · "b"\n'
           '- L003 · 2026-11-03 10:00 · research · change · a · file: template · "b"\n')
    lessons = lessons_project(tmp_path, LESSONS + old)
    code, out = run(tmp_path, *lesson_args())
    assert code == 0, out
    text = read(lessons)
    assert text.startswith(LESSONS + old), text
    assert text[len(LESSONS + old):].startswith("- L042 · "), text


def test_lesson_file_under_docs_research_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    (tmp_path / "docs" / "research").mkdir()
    (tmp_path / "docs" / "research" / "reader.md").write_text("x\n", encoding="utf-8")
    out = refused(tmp_path, lessons, *lesson_args(about="docs/research/reader.md"))
    assert "docs/research/" in out, out


def test_lesson_file_a_log_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    for name in ("log.md", "research-log.md"):
        (tmp_path / "docs" / name).write_text("x\n", encoding="utf-8")
        out = refused(tmp_path, lessons, *lesson_args(about=f"docs/{name}"))
        assert "a log" in out, out


def test_lesson_file_a_findings_file_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    (tmp_path / "docs" / "findings-for-the-framework.md").write_text("x\n", encoding="utf-8")
    out = refused(tmp_path, lessons, *lesson_args(about="docs/findings-for-the-framework.md"))
    assert "findings" in out, out


def test_lesson_file_that_does_not_exist_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(about="docs/blanks/nothing.md"))
    assert "not a file of the project" in out, out


def test_lesson_about_template_is_allowed(tmp_path):
    lessons = lessons_project(tmp_path)
    code, out = run(tmp_path, *lesson_args(about="template"))
    assert code == 0, out
    assert ' · file: template · "Run the gate once."' in read(lessons).splitlines()[-1], read(lessons)


def test_lesson_about_unknown_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(about="unknown"))
    assert "backlog" in out, out


def test_lesson_works_and_misfire_with_no_seen_are_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    for kind in ("works", "misfire"):
        out = refused(tmp_path, lessons, *lesson_args(kind))
        assert "--seen" in out, out


def test_lesson_typed_time_at_the_start_of_what_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(what="10:40 the gate ran twice"))
    assert out.startswith('REFUSE: "10:40"'), out


def test_lesson_dot_separator_in_what_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(what="the gate · ran twice"))
    assert "what" in out, out


def test_lesson_missing_part_bad_from_newline_or_seen_in_the_line_is_refused(tmp_path):
    lessons = lessons_project(tmp_path)
    good = lesson_args()
    for flag in ("--from", "--kind", "--about", "--line"):
        at = good.index(flag)
        refused(tmp_path, lessons, *(good[:at] + good[at + 2:]))
    for flag, value in (("--from", "run four"), ("--kind", "idea"), ("--line", "one\ntwo"),
                        ("--line", "Run it · seen: twice")):
        at = good.index(flag)
        refused(tmp_path, lessons, *(good[:at + 1] + [value] + good[at + 2:]))


def test_lesson_with_no_lessons_file_is_refused_and_nothing_is_made(tmp_path):
    (tmp_path / "docs").mkdir()
    code, out = run(tmp_path, *lesson_args(about="template"))
    assert code == 1, out
    assert out.startswith("REFUSE"), out
    assert list((tmp_path / "docs").iterdir()) == []


def test_lesson_refused_while_a_fresh_lock_is_held(tmp_path):
    lessons = lessons_project(tmp_path)
    lock = tmp_path / "docs" / "lessons.md.lock"
    lock.write_text("", encoding="utf-8")
    before = lessons.read_bytes()
    code, out = run(tmp_path, *lesson_args())
    assert code == 1, out
    assert out.startswith("REFUSE") and "lock" in out, out
    assert lessons.read_bytes() == before
    assert lock.exists()  # another writer's lock is never taken while fresh


def test_lesson_takes_a_stale_lock(tmp_path):
    lessons = lessons_project(tmp_path)
    lock = tmp_path / "docs" / "lessons.md.lock"
    lock.write_text("", encoding="utf-8")
    old = datetime.datetime.now().timestamp() - 120
    os.utime(lock, (old, old))
    code, out = run(tmp_path, *lesson_args())
    assert code == 0, out
    assert read(lessons).splitlines()[-1].startswith("- L001 · "), read(lessons)
    assert not lock.exists()


def test_lesson_two_writers_at_once_in_threads_never_share_a_number(tmp_path, monkeypatch):
    # Run in this process so the read can be slowed: each writer pauses after
    # reading the file, which is when a second writer without the lock would
    # read the same highest number.
    import importlib.util
    import threading
    import time
    spec = importlib.util.spec_from_file_location("record_under_test", TOOL)
    record = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(record)
    lessons = lessons_project(tmp_path)
    slow = record.load

    def load(path):
        text = slow(path)
        time.sleep(0.3)
        return text

    monkeypatch.setattr(record, "load", load)
    codes = []
    writers = [threading.Thread(target=lambda: codes.append(record.main(
        ["record.py", "--file", str(lessons), *lesson_args(about="template")]))) for _ in range(4)]
    for writer in writers:
        writer.start()
    for writer in writers:
        writer.join()
    assert codes == [0, 0, 0, 0], codes
    numbers = [line.split(" · ")[0] for line in read(lessons).splitlines()[2:]]
    assert sorted(numbers) == ["- L001", "- L002", "- L003", "- L004"], read(lessons)


# --handover: the Handover line built from named fields, never typed.

def handover_lines(folder):
    lines = (folder / "docs/runs/2/run.md").read_text(encoding="utf-8").splitlines()
    return lines[lines.index("## Handover") + 2:]


def test_handover_is_built_from_the_named_fields_in_order_and_stamped(tmp_path):
    folder = project(tmp_path)
    before = clock()
    code, out = run(folder, "--handover", "--ids", "claim 1, thread 2", "--next", "land T3",
                    "--window", "40%", "--merges", "T1 squash abc1234", "--running", "T2 worker")
    after = clock()
    assert code == 0, out
    (line,) = handover_lines(folder)
    match = re.fullmatch(r"- (\d\d:\d\d) · running: T2 worker · merges: T1 squash abc1234 · next: land T3"
                         r" · window: 40% · ids: claim 1, thread 2", line)
    assert match, line
    assert match.group(1) in (before, after)


def test_handover_with_next_alone_is_written_and_with_no_next_is_refused(tmp_path):
    folder = project(tmp_path)
    code, out = run(folder, "--handover", "--running", "T2 worker")
    assert code == 2 and "--handover needs --next" in out, out
    assert handover_lines(folder) == []
    code, out = run(folder, "--handover", "--next", "land T3")
    assert code == 0, out
    (line,) = handover_lines(folder)
    assert re.fullmatch(r"- \d\d:\d\d · next: land T3", line), line


def test_handover_takes_no_line_of_its_own(tmp_path):
    folder = project(tmp_path)
    before = (folder / "docs/runs/2/run.md").read_bytes()
    code, out = run(folder, "--handover", "--next", "land T3", "workers report in the master's thread")
    assert code == 2 and "--handover takes no line of its own" in out, out
    assert (folder / "docs/runs/2/run.md").read_bytes() == before


def test_handover_has_no_field_for_orders_or_rules(tmp_path):
    folder = project(tmp_path)
    before = (folder / "docs/runs/2/run.md").read_bytes()
    for field in ("--orders", "--rules", "--text"):
        code, out = run(folder, "--handover", "--next", "land T3", field, "workers report here")
        assert code == 2 and "unrecognized arguments" in out, out
    assert (folder / "docs/runs/2/run.md").read_bytes() == before


def test_a_handover_field_without_handover_is_refused(tmp_path):
    folder = project(tmp_path)
    code, out = run(folder, "--section", "Merges", "a line", "--next", "land T3")
    assert code == 2 and "--next goes with --handover" in out, out


# A run's record that is not there yet is opened from the blank.

BLANK = os.path.join(os.path.dirname(os.path.dirname(TOOL)), "docs", "blanks", "run.md")


def blank_project(tmp_path, name="demo"):
    folder = project(tmp_path)
    (folder / "docs" / "blanks").mkdir()
    with open(BLANK, "rb") as f:
        (folder / "docs" / "blanks" / "run.md").write_bytes(f.read())
    if name:
        (folder / "project.yaml").write_text(f"name: {name}\nkind: tool\n", encoding="utf-8")
    (folder / "docs" / "runs" / "3").mkdir()
    return folder


def test_a_newest_run_with_no_record_is_opened_from_the_blank_then_written(tmp_path):
    folder = blank_project(tmp_path)
    older = (folder / "docs/runs/2/run.md").read_bytes()
    code, out = run(folder, "--section", "Merges", "piece · squash abc1234")
    assert code == 0, out
    assert (folder / "docs/runs/2/run.md").read_bytes() == older
    assert out.startswith("OPENED: docs/runs/3/run.md from docs/blanks/run.md"), out
    text = (folder / "docs/runs/3/run.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "# Run 3 — demo", lines[:3]  # the note line dropped
    assert "<n>" not in text and "foundry-north-website" not in text
    assert "--card docs/runs/3/run.md" in text
    merges = lines.index("## Merges")
    assert re.fullmatch(r"- \d\d:\d\d · piece · squash abc1234", lines[merges + 3]), lines[merges:merges + 5]


def test_a_named_run_record_is_opened_with_the_folders_name_when_no_project_yaml(tmp_path):
    folder = blank_project(tmp_path, name=None)
    code, out = run(folder, "--handover", "--next", "land T3", "--file", "docs/runs/3/run.md")
    assert code == 0, out
    text = (folder / "docs/runs/3/run.md").read_text(encoding="utf-8")
    assert text.startswith(f"# Run 3 — {folder.name}"), text[:40]
    assert re.search(r"\n- \d\d:\d\d · next: land T3\r?\n", text), text


def test_an_existing_record_is_never_opened_over_and_a_refusal_leaves_none(tmp_path):
    folder = blank_project(tmp_path)
    code, out = run(folder, "--section", "Merges", "a line", "--file", "docs/runs/2/run.md")
    assert code == 0 and "OPENED" not in out, out
    assert (folder / "docs/runs/2/run.md").read_text(encoding="utf-8").startswith("# Run 2 — test")
    code, out = run(folder, "--section", "Mergers", "a line")
    assert code == 1 and out.startswith("REFUSE"), out
    assert not (folder / "docs/runs/3/run.md").exists()
    code, out = run(folder, "--section", "Merges", "a line", "--file", "docs/runs/9/run.md")
    assert code == 1 and "a run is never invented" in out, out
    assert not (folder / "docs/runs/9").exists()


# An It works line names who looked.

def test_an_it_works_line_without_who_looked_is_refused(tmp_path):
    record = page(tmp_path, "run.md", "# Run 2 — test\n\n## It works\nOne line per card.\n")
    before = record.read_bytes()
    code, out = run(tmp_path, "--file", "run.md", "--section", "It works", "stamps-seats · pass · the gate ran")
    assert code == 1, out
    assert out.startswith("REFUSE: an It works line is") and "<who looked>" in out, out  # its "·" print in UTF-8
    assert record.read_bytes() == before
    code, out = run(tmp_path, "--file", "run.md", "--section", "It works",
                    "stamps-seats · pass · his watch · the handover line shown on his phone")
    assert code == 0, out
    assert re.search(r"- \d\d:\d\d · stamps-seats · pass · his watch · the handover line", read(record))


# --lesson's sort, limits and same (contract 2), and the two lessons never routine (ruling 5).

HOUSE_FLOW = ("# Hero film — v2.0\n\nVersion: v2.0\n\n## Steps\n"
              "1. **Intake** · `{tag}` · the master — in: x — out: y — because.\n"
              "2. **The kit** · `on trial` · measure: his notes · the master — in: x — out: y — because.\n")


def sorts_project(tmp_path, flow_tag="idea", file_tag=None):
    """A lessons file with one lesson (L001), a house file, a house blank and a workflow file."""
    lessons = lessons_project(tmp_path, LESSONS + '- L001 · 2026-11-01 10:00 · run 1 · change · a · file: template · "b"\n')
    (tmp_path / "docs" / "method.md").write_text("# Method\n", encoding="utf-8", newline="\n")
    (tmp_path / "docs" / "blanks" / "shot-list.md").write_text("# shots\n", encoding="utf-8", newline="\n")
    flow = HOUSE_FLOW.format(tag=flow_tag)
    if file_tag:
        flow = flow.replace("Version: v2.0\n", f"Version: v2.0\nTag: `{file_tag}`\n")
    (tmp_path / "docs" / "hero.md").write_text(flow, encoding="utf-8", newline="\n")
    return lessons


def written(lessons):
    return read(lessons).splitlines()[-1]


def test_lesson_sort_is_his_by_default_for_a_house_file_and_a_house_blank(tmp_path):
    lessons = sorts_project(tmp_path)
    for about in ("docs/method.md", "docs/blanks/shot-list.md"):
        code, out = run(tmp_path, *lesson_args(about=about))
        assert code == 0, out
        assert written(lessons).endswith(f' · file: {about} · "Run the gate once." · sort: his'), written(lessons)


def test_lesson_sort_is_template_by_default_for_the_word_template_and_a_template_file(tmp_path):
    lessons = sorts_project(tmp_path)
    for about in ("template", "docs/blanks/card.md"):
        code, out = run(tmp_path, *lesson_args(about=about))
        assert code == 0, out
        assert written(lessons).endswith(f' · file: {about} · "Run the gate once." · sort: template'), written(lessons)


def test_lesson_sort_given_is_written_as_given(tmp_path):
    lessons = sorts_project(tmp_path)
    for about, sort in (("docs/method.md", "routine"), ("docs/method.md", "template"), ("template", "his")):
        code, out = run(tmp_path, *lesson_args(about=about), "--sort", sort)
        assert code == 0, out
        assert written(lessons).endswith(f' · "Run the gate once." · sort: {sort}'), written(lessons)
    code, out = run(tmp_path, *lesson_args(about="docs/method.md"), "--sort", "mine")
    assert code == 2 and "invalid choice" in out, out  # argparse: only routine, his or template


def test_lesson_limits_and_same_are_written_after_sort_and_before_seen(tmp_path):
    lessons = sorts_project(tmp_path)
    code, out = run(tmp_path, *lesson_args("works", about="docs/method.md", seen="3 of 3"),
                    "--limits", "made", "--same", "L1")
    assert code == 0, out
    assert written(lessons).endswith(' · "Run the gate once." · sort: his · limits: made · same: L001 · seen: 3 of 3'), \
        written(lessons)
    code, out = run(tmp_path, *lesson_args(about="docs/method.md"), "--same", "L002")
    assert code == 0, out
    assert written(lessons).endswith(' · "Run the gate once." · sort: his · same: L002'), written(lessons)


def test_lesson_same_naming_no_lesson_in_the_file_is_refused(tmp_path):
    lessons = sorts_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(about="docs/method.md"), "--same", "L009")
    assert "REFUSE: --same L009: no lesson L009 in docs/lessons.md" in out, out
    out = refused(tmp_path, lessons, *lesson_args(about="docs/method.md"), "--same", "the first one")
    assert "is not a lesson's number" in out, out


def test_lesson_routine_that_limits_what_may_be_made_is_refused(tmp_path):
    lessons = sorts_project(tmp_path)
    out = refused(tmp_path, lessons, *lesson_args(about="docs/method.md"), "--sort", "routine", "--limits", "made")
    assert out.strip() == "REFUSE: a lesson that limits what may be made is his (ruling 5)", out
    code, out = run(tmp_path, *lesson_args(about="docs/method.md"), "--limits", "made")  # his: written
    assert code == 0, out


def test_lesson_routine_on_a_workflow_file_holding_a_foundation_is_refused(tmp_path):
    for name, step, whole in (("step", "foundation · 2 jobs", None), ("tag", "idea", "foundation · 1 job")):
        folder = tmp_path / name
        lessons = sorts_project(folder, step, whole)
        out = refused(folder, lessons, *lesson_args(about="docs/hero.md"), "--sort", "routine")
        assert out.strip() == "REFUSE: docs/hero.md holds a foundation; a better way runs as a trial beside it", out
    lessons = sorts_project(tmp_path / "none")  # a workflow file with no foundation: routine is written
    code, out = run(tmp_path / "none", *lesson_args(about="docs/hero.md"), "--sort", "routine")
    assert code == 0 and written(lessons).endswith(" · sort: routine"), out


def read_080(line):
    """0.8.0's reader of one lesson line, as upgrade.lessons was at tag template/0.8.0: (line, seen)."""
    parts = line.split(" · ", 6)
    rest = parts[6]
    seen = None
    cut = rest.rfind(" · seen: ")
    if cut != -1:
        rest, seen = rest[:cut], rest[cut + len(" · seen: "):]
    first, last = rest.find('"'), rest.rfind('"')
    return (rest[first + 1:last] if first != -1 and last > first else rest), seen


def test_the_0_8_0_reader_and_upgrade_read_every_new_line_right(tmp_path):
    lessons = sorts_project(tmp_path)
    code, out = run(tmp_path, *lesson_args("works", about="docs/method.md", seen='his verdict: "that one"'),
                    "--limits", "made", "--same", "L001")
    assert code == 0, out
    code, out = run(tmp_path, *lesson_args(about="template"))
    assert code == 0, out
    new = read(lessons).splitlines()[-2:]
    assert read_080(new[0]) == ("Run the gate once.", 'his verdict: "that one"'), new
    assert read_080(new[1]) == ("Run the gate once.", None), new
    spec = importlib.util.spec_from_file_location("upgrade_for_record_tests",
                                                  os.path.join(os.path.dirname(TOOL), "upgrade.py"))
    upgrade = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upgrade)
    l1, l2, l3 = upgrade.lessons(tmp_path)
    assert (l2["line"], l2["seen"], l2["sort"], l2["limits"], l2["same"]) == \
        ("Run the gate once.", 'his verdict: "that one"', "his", True, "L001")
    assert (l3["line"], l3["seen"], l3["sort"], l3["limits"], l3["same"]) == \
        ("Run the gate once.", None, "template", False, None)
    assert l1["sort"] == "his"  # a line from before 0.9.0, with no sort:, reads as his


# --week: the week's reading, from the state window.py leaves (under tmp_path, never the real one).

WEEK_RUN = "# Run 2 — test\n\n## Go\n- 09:00 · Start (Go): this master\n\n## Merges\n"


def week_project(tmp_path):
    record = tmp_path / "docs" / "runs" / "2" / "run.md"
    record.parent.mkdir(parents=True)
    record.write_text(WEEK_RUN, encoding="utf-8", newline="\n")
    return record


def window_state(tmp_path, percent, age=0):
    """The state as window.py writes it, read <age> seconds ago; the LOCALAPPDATA that holds it."""
    local = tmp_path / "local"
    (local / "agentic-meta").mkdir(parents=True, exist_ok=True)
    reading = {"read_at": int(time.time()) - age, "five_hour": {"percent": 99, "resets_at": 1},
               "seven_day": {"percent": percent, "resets_at": 2}, "word": "full pace", "previous": None}
    (local / "agentic-meta" / "window.json").write_text(json.dumps(reading), encoding="utf-8")
    return local


def week(folder, local, kind):
    done = subprocess.run([sys.executable, "-B", TOOL, "--week", kind], cwd=folder, capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, LOCALAPPDATA=str(local), PYTHONIOENCODING="utf-8"))
    return done.returncode, done.stdout + done.stderr


def test_the_weeks_reading_is_written_at_go_and_at_the_close(tmp_path):
    record = week_project(tmp_path)
    code, out = week(tmp_path, window_state(tmp_path, 8), "go")
    assert code == 0 and out.startswith("RECORDED"), out
    code, out = week(tmp_path, window_state(tmp_path, 15), "close")
    assert code == 0 and out.startswith("RECORDED"), out
    lines = read(record).splitlines()
    assert re.fullmatch(r"- \d\d:\d\d · Week read at Go: 8%", lines[4]), lines
    assert re.fullmatch(r"- \d\d:\d\d · Week read at the close: 15%", lines[5]), lines
    assert lines[6:] == ["", "## Merges"], lines

    before = read(record)
    for kind in ("go", "close"):  # a second line of the same kind
        code, out = week(tmp_path, window_state(tmp_path, 20), kind)
        assert code == 1 and out.startswith("REFUSE") and "already has its" in out, out
    assert read(record) == before


def test_a_stale_week_reading_is_refused(tmp_path):
    record = week_project(tmp_path)
    words = "read the window first: python tools/window.py"
    code, out = week(tmp_path, tmp_path / "no-reading-here", "go")  # none at all
    assert code == 1 and out.startswith("REFUSE") and words in out, out
    code, out = week(tmp_path, window_state(tmp_path, 8, age=11 * 60), "go")
    assert code == 1 and out.startswith("REFUSE") and words in out, out
    assert read(record) == WEEK_RUN
    code, out = week(tmp_path, window_state(tmp_path, 8, age=9 * 60), "go")
    assert code == 0, out


def test_a_shutdown_line_with_no_status_ends_open(tmp_path):
    record = tmp_path / "docs" / "runs" / "2" / "run.md"
    record.parent.mkdir(parents=True)
    record.write_text("# Run 2 — test\n\n## Shutdown list\n\n## Merges\n", encoding="utf-8", newline="\n")
    for text in ("seat · the master's seat · id-1 · release it",
                 "watch · the check · id-2 · delete it · open",
                 "session · a worker · id-3 · archive it · closed 10:35",
                 "session · a worker · id-4 · archive it · closed 07:18 (task completed)",
                 "a · b · open the door",
                 "a · b · open-ended watch"):
        code, out = run(tmp_path, "--section", "Shutdown list", text)
        assert code == 0, out
    code, out = run(tmp_path, "--section", "Merges", "piece · squash abc1234")
    assert code == 0, out
    lines = [line.split(" · ", 1)[1] for line in read(record).splitlines() if line.startswith("- ")]
    assert lines == ["seat · the master's seat · id-1 · release it · open",
                     "watch · the check · id-2 · delete it · open",
                     "session · a worker · id-3 · archive it · closed 10:35",
                     "session · a worker · id-4 · archive it · closed 07:18 (task completed)",
                     "a · b · open the door · open",
                     "a · b · open-ended watch · open",
                     "piece · squash abc1234"]


def test_a_lesson_about_a_path_outside_the_project_is_refused(tmp_path):
    house = tmp_path / "house"
    lessons = sorts_project(house)
    outside = tmp_path / "outside" / "x.md"  # there, so only where it lies can refuse it
    outside.parent.mkdir()
    outside.write_text("# x\n", encoding="utf-8", newline="\n")
    for about in ("../outside/x.md", "docs/../../outside/x.md", str(outside), outside.as_posix()):
        out = refused(house, lessons, *lesson_args(about=about))
        assert "resolves outside the project" in out, out
    for about in ("docs/method.md", "template", str(house / "docs" / "method.md")):  # inside, and the word
        code, out = run(house, *lesson_args(about=about))
        assert code == 0, out
