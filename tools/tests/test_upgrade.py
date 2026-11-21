# Tests for upgrade.py. Each test builds a small sample project under
# tmp_path (docs/lessons.md, docs/decisions.md, docs/brief.md and the files
# the lessons name) and runs the tool there. No real record is read or changed.

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "upgrade.py")

_spec = importlib.util.spec_from_file_location("upgrade_for_tests", TOOL)
upgrade = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upgrade)

DECISIONS = "# Decisions — test\n\nAppend-only.\n"
TABLE = "| L-numbers | his answer | the line as kept | where it is |\n|---|---|---|---|\n"


def lesson(n, kind, file, line, when="2026-11-10 09:00", what="what happened", seen=None, frm="run 1"):
    text = f'- L{n:03d} · {when} · {frm} · {kind} · {what} · file: {file} · "{line}"'
    return text + (f" · seen: {seen}" if seen else "")


def project(tmp_path, lines=(), decisions=DECISIONS, brief=None, files=None, lessons_file=True):
    root = tmp_path / "project"
    (root / "docs").mkdir(parents=True)
    if lessons_file:
        (root / "docs" / "lessons.md").write_text("# Lessons — test\n\n" + "".join(l + "\n" for l in lines),
                                                  encoding="utf-8", newline="\n")
    (root / "docs" / "decisions.md").write_text(decisions, encoding="utf-8", newline="\n")
    if brief is not None:
        (root / "docs" / "brief.md").write_text(brief, encoding="utf-8", newline="\n")
    for path, text in (files or {}).items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8", newline="\n")
    return root


def closing(title="Run 1 closed", when="2026-11-11 10:00", rows=(), block=True):
    text = f"\n## {when} — {title}\nThe run is closed.\n"
    if block:
        text += "\n### The upgrade\n" + TABLE + "".join(f"| {' | '.join(r)} |\n" for r in rows)
    return text


def run(root, *args):
    done = subprocess.run([sys.executable, "-B", TOOL, "--project", str(root), *args],
                          capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout + done.stderr


def listed(root, *args):
    code, out = run(root, "--json", *args)
    assert code == 0, out
    return {g["key"]: g for g in json.loads(out)["groups"]}


def numbers(group):
    return [item["n"] for item in group["items"]]


def workflow(name, steps, version="v1.0", upgrades=()):
    """A workflow file in contract 4's form: (n, name, tag) per step, the tag as written between backticks."""
    text = f"# {name} — {version}\n\nVersion: {version}\n\n## Steps\n"
    text += "".join(f"{n}. **{step}** · `{tag}` · the master — in: x — out: y — because.\n" for n, step, tag in steps)
    return text + "\n## Upgrades\n" + "".join(f"- {line}\n" for line in upgrades)


SERIES = workflow("Series", [(1, "Brief", "foundation · 2 jobs"), (2, "Script", "on trial")], "v1.3")


def test_a_lessons_file_of_every_kind_lists_each_in_its_group(tmp_path):
    root = project(tmp_path, [
        lesson(1, "change", "CLAUDE.md", "Read the brief first."),
        lesson(2, "change", "unknown", "", what="an old note (before the upgrade)"),
        lesson(3, "works", "docs/method.md", "the method", seen="4 of 4 passed"),
        lesson(4, "track", "docs/method.md", "a script-only start"),
        lesson(5, "change", "tracks.md", "A template line."),
        lesson(6, "misfire", "docs/series.md", "the series", seen="his verdict: wrong"),
    ], files={"CLAUDE.md": "x\n", "docs/method.md": "m\n", "docs/series.md": SERIES})
    g = listed(root)
    assert numbers(g["needs_thought"]) == []
    assert numbers(g["lines"]) == ["L001", "L002"]
    assert [i["file"] for i in g["foundations"]["items"]] == ["docs/method.md"]
    assert [l["n"] for l in g["foundations"]["items"][0]["waiting"]] == ["L003"]
    assert numbers(g["tracks"]) == ["L004"]
    assert [[l["n"] for l in i["misfires"]] for i in g["trials"]["items"]] == [["L006"]]
    assert numbers(g["template"]) == ["L005"]
    code, out = run(root)
    assert code == 0, out
    for title in ("0. needs thought (0)", "1. lines to keep, change or drop — approve all (2)",
                  "2. suggested foundations (1)", "2a. candidate tracks (1)",
                  "3. foundations to reopen as trials (1)", "foundations (1)", "4. for the template (1)"):
        assert title in out, out
    assert out.index("0. needs thought") < out.index("1. lines") < out.index("2. suggested foundations") \
        < out.index("2a. candidate") < out.index("3. foundations to reopen") < out.index("4. for the template")
    assert 'L001 · change · file: CLAUDE.md · "Read the brief first."' in out
    assert "none" in out.split("0. needs thought (0)")[1].split("1. lines")[0]
    assert "lock" not in out.replace("block", ""), out


def test_every_backlog_lesson_lands_in_approve_all_whatever_its_kind(tmp_path):
    root = project(tmp_path, [
        lesson(1, "works", "unknown", "", what="an old note (before the upgrade)", seen="a pass"),
        lesson(2, "misfire", "unknown", "", what="an old note (before the upgrade)", seen="it broke"),
        lesson(3, "track", "unknown", "", what="an old note (before the upgrade)"),
        lesson(4, "change", "unknown", "", what="an old note (before the upgrade)"),
    ])
    g = listed(root)
    assert numbers(g["lines"]) == ["L001", "L002", "L003", "L004"]
    assert g["foundations"]["items"] == [] and g["trials"]["items"] == [] and g["tracks"]["items"] == []


def test_needs_thought_moves_a_lesson_to_group_0_and_out_of_approve_all(tmp_path):
    root = project(tmp_path, [lesson(1, "change", "CLAUDE.md", "One."), lesson(2, "change", "CLAUDE.md", "Two.")],
                   files={"CLAUDE.md": "x\n"})
    g = listed(root, "--needs-thought", "L002")
    assert numbers(g["needs_thought"]) == ["L002"]
    assert numbers(g["lines"]) == ["L001"]
    code, out = run(root, "--needs-thought", "L009")
    assert code == 1 and "REFUSE: --needs-thought L009" in out, out


def test_a_template_owned_file_lands_for_the_template(tmp_path):
    owned = ["tracks.md", ".claude/skills/run/SKILL.md", ".claude/skills/conductor/SKILL.md", "operator.md",
             "worker-rules.md", "roles/checker.md", "pages.md", "docs/blanks/card.md", "tools/land.py", "template"]
    lines = [lesson(i + 1, "change", f, f"line {i + 1}") for i, f in enumerate(owned)]
    lines.append(lesson(len(owned) + 1, "change", "docs/method.md", "a project line"))
    root = project(tmp_path, lines)
    g = listed(root)
    assert numbers(g["template"]) == [f"L{i + 1:03d}" for i in range(len(owned))]
    assert numbers(g["lines"]) == [f"L{len(owned) + 1:03d}"]


def test_a_foundation_file_with_a_waiting_misfire_is_a_foundation_to_reopen_as_a_trial(tmp_path):
    hero = workflow("Hero film", [(1, "Intake", "foundation · 1 job"), (2, "The kit", "on trial")], "v2.0")
    root = project(tmp_path, [lesson(7, "misfire", "docs/hero.md", "the hero film", seen="it broke on a bare brief")],
                   files={"docs/hero.md": hero})
    g = listed(root)
    [item] = g["trials"]["items"]
    assert item["file"] == "docs/hero.md"
    assert item["foundations"] == [{"file": "docs/hero.md", "step": 1, "name": "Intake", "jobs": 1}]
    assert [l["n"] for l in item["misfires"]] == ["L007"]
    [held] = g["foundation"]["items"]
    assert held["name"] == "Intake"
    code, out = run(root)
    assert "docs/hero.md (docs/hero.md step 1 Intake · 1 job) — misfire: L007" in out, out


def test_the_foundations_group_lists_every_foundation_of_the_workflow_files(tmp_path):
    whole = SERIES.replace("Version: v1.3\n", "Version: v1.3\nTag: `foundation · 3 jobs`\n")
    brief = "# Brief\n\nLocked: Hero film v2.0 — docs/hero.md — since 2026-11-01 — proven by L003\n"
    root = project(tmp_path, [], brief=brief, files={"docs/series.md": whole, "docs/hero.md": "h\n"})
    g = listed(root)
    assert g["foundation"]["items"] == [
        {"file": "docs/series.md", "step": None, "name": "Series", "jobs": 3},
        {"file": "docs/series.md", "step": 1, "name": "Brief", "jobs": 2}]  # the brief's line is never read
    code, out = run(root)
    assert "     foundations (2)\n        docs/series.md · 3 jobs\n        docs/series.md step 1 Brief · 2 jobs" in out, out


def test_a_lesson_answered_in_an_earlier_block_is_not_listed(tmp_path):
    decisions = DECISIONS + closing(rows=[("L001", "drop", "", "")])
    root = project(tmp_path, [lesson(1, "change", "CLAUDE.md", "Old."), lesson(2, "change", "CLAUDE.md", "New.")],
                   decisions=decisions, files={"CLAUDE.md": "x\n"})
    assert numbers(listed(root)["lines"]) == ["L002"]
    assert [l["n"] for l in upgrade.waiting(root)] == ["L002"]


def test_a_block_in_a_decisions_part_file_counts_too(tmp_path):
    root = project(tmp_path, [lesson(1, "change", "CLAUDE.md", "Old.")], files={
        "CLAUDE.md": "x\n",
        "docs/decisions-2026.md": "# Decisions, part\n" + closing(rows=[("L001", "drop", "", "")])})
    assert upgrade.waiting(root) == []


def test_a_not_now_works_lesson_is_raised_again_only_with_a_new_works_lesson(tmp_path):
    decisions = DECISIONS + closing(rows=[("L001", "not now", "", "docs/method.md")])
    first = [lesson(1, "works", "docs/method.md", "the method", seen="3 of 3")]
    root = project(tmp_path, first, decisions=decisions, files={"docs/method.md": "m\n"})
    assert listed(root)["foundations"]["items"] == []
    root2 = project(tmp_path / "again", first + [
        lesson(2, "works", "docs/method.md", "the method", when="2026-11-12 09:00", seen="his verdict: good")],
        decisions=decisions, files={"docs/method.md": "m\n"})
    [item] = listed(root2)["foundations"]["items"]
    assert [l["n"] for l in item["waiting"]] == ["L002"]
    assert [l["n"] for l in item["earlier_not_now"]] == ["L001"]
    code, out = run(root2)
    assert "docs/method.md — works: L002 (seen: his verdict: good) · earlier, answered not now: L001 (seen: 3 of 3)" in out, out


def passing(tmp_path):
    lines = [lesson(1, "change", "CLAUDE.md", "Read the brief first."),
             lesson(2, "change", "tracks.md", "A template line."),
             lesson(3, "works", "docs/method.md", "the method", seen="4 of 4"),
             lesson(4, "change", "unknown", "", what="old note (before the upgrade)"),
             lesson(5, "change", "docs/method.md", "Step 2 waits for his | mark."),
             lesson(6, "change", "CLAUDE.md", "after the close", when="2026-11-12 08:00")]
    rows = [("L001", "keep", '"Read the brief first."', "`CLAUDE.md`"),
            ("L002", "keep", "A template line.", "template"),
            ("L003", "foundation", "the method", "docs/method.md"),
            ("L004", "drop", "", ""),
            ("L005", "change", "Step 2 waits for his \\| mark, then goes on.", "docs/method.md")]
    files = {"CLAUDE.md": "# x\n\nRead the brief first.\n",
             "docs/method.md": "# Method — v1.1\n\nVersion: v1.1\n\n## Steps\n"
                               "1. **The method** · `foundation · 1 job` · the master — in: x — out: y — because.\n\n"
                               "Step 2 waits for his | mark, then goes on.\n\n## Upgrades\n"
                               "2026-11-11 · v1.1 · step 2 waits · why: he asked · from: L005\n"
                               "2026-11-11 · v1.1 · a foundation · why: he said so · from: L003\n"}
    brief = "# Brief\n\nFoundations: never written here.\n"
    return lines, rows, files, brief


def test_check_passes_a_block_answering_every_lesson_with_each_kept_line_found(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 0, out
    assert out.strip() == "UPGRADE DONE: Run 1 closed", out
    assert upgrade.check(root) == (True, [], "Run 1 closed")
    assert [l["n"] for l in upgrade.waiting(root)] == ["L006"]  # dated after the close, still waits


def test_check_refuses_a_missing_row_naming_its_l_number(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows[1:]), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L001 has no row in Run 1 closed"], out


def test_check_refuses_a_kept_line_not_in_its_file_naming_the_file(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    rows[0] = ("L001", "change", "Read the whole brief first.", "CLAUDE.md")
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L001: the line as kept is not in CLAUDE.md"], out
    passed, faults, title = upgrade.check(root)
    assert not passed and title == "Run 1 closed" and len(faults) == 1


def test_check_refuses_a_workflow_file_with_no_upgrades_line(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    files["docs/method.md"] = files["docs/method.md"].replace("from: L005", "from: ruling 9")
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L005: docs/method.md has ## Upgrades and no line under it naming L005"], out


def test_check_refuses_a_foundation_or_reopen_row_on_a_workflow_file_with_no_upgrades_line(tmp_path):
    lines = [lesson(1, "works", "docs/method.md", "the method", seen="4 of 4"),
             lesson(2, "misfire", "docs/series.md", "the series", seen="it broke")]
    rows = [("L001", "foundation", "the method", "docs/method.md"), ("L002", "reopen", "", "docs/series.md")]
    files = {"docs/method.md": workflow("Method", [(1, "The method", "foundation · 1 job")],
                                        upgrades=["2026-11-11 · v1.0 · first · why: start · from: ruling 9"]),
             "docs/series.md": "# Series\n\n## Upgrades\n2026-11-11 · v1.3 · first · why: start · from: ruling 9\n"}
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == [
        "REFUSE: L001: docs/method.md has ## Upgrades and no line under it naming L001",
        "REFUSE: L002: docs/series.md has ## Upgrades and no line under it naming L002"], out
    files["docs/method.md"] += "- 2026-11-11 · v1.0 · a foundation · why: he said so · from: L001\n"
    files["docs/series.md"] += "2026-11-11 · v1.4 · reopened · why: a misfire · from: L002\n"
    root2 = project(tmp_path / "again", lines, decisions=DECISIONS + closing(rows=rows), files=files)
    code, out = run(root2, "--check")
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 1 closed", out


def test_check_refuses_a_foundation_row_whose_file_has_no_foundation_tag(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    files["docs/method.md"] = files["docs/method.md"].replace("`foundation · 1 job`", "`on trial` · measure: his notes")
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows),
                   brief="# Brief\n\nLocked: the method v1.1 — docs/method.md — since 2026-11-11 — proven by L003\n",
                   files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == [
        "REFUSE: L003: foundation of docs/method.md, and no step or Tag: line there is tagged foundation"], out


def test_check_passes_a_foundation_row_whose_file_has_a_foundation_tag_line(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    files["docs/method.md"] = (files["docs/method.md"].replace("`foundation · 1 job`", "`on trial` · measure: his notes")
                               .replace("Version: v1.1\n", "Version: v1.1\nTag: `foundation · 2 jobs`\n"))
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 1 closed", out


def test_an_old_unlock_answer_reads_as_trial_and_waits_no_more(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    rows[2] = ("L003", "unlock", "", "docs/method.md")
    root = project(tmp_path, lines, decisions=DECISIONS + closing(rows=rows), brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 1 closed", out
    assert upgrade.closings(root)[-1]["rows"][2]["answer"] == "trial"


def test_an_old_lock_answer_in_an_earlier_block_still_reads(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    earlier = closing(rows=[("L003", "lock", "the method", "docs/method.md")], when="2026-11-10 08:00")
    rest = [row for row in rows if row[0] != "L003"]
    root = project(tmp_path, lines, decisions=DECISIONS + earlier + closing(title="Run 2 closed", rows=rest),
                   brief=brief, files=files)
    assert "L003" not in [l["n"] for l in upgrade.waiting(root)]
    assert upgrade.closings(root)[0]["rows"][0]["answer"] == "foundation"
    code, out = run(root, "--check")
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 2 closed", out


def first_time(tmp_path, flow, kind="First time: a podcast"):
    """A first-time run 1, closed with every lesson answered, its Go at 2026-11-10 08:00."""
    files = {"docs/runs/1/plan-signed.md": f"# Plan for run 1 — test\n\n## The path\n{kind}\n- the pilot · main\n",
             "docs/runs/1/run.md": "# Run 1 — test\n\n## Go\n- Start: 2026-11-10 08:00\n"}
    if flow:
        files["docs/podcast.md"] = flow
    rows = [("L001", "drop", "", "")]
    return project(tmp_path, [lesson(1, "change", "CLAUDE.md", "x")], decisions=DECISIONS + closing(rows=rows),
                   files=files)


def test_the_first_time_close_is_refused_without_its_workflow_file(tmp_path):
    root = first_time(tmp_path, None)
    code, out = run(root, "--check")
    assert code == 1 and out.strip() == "REFUSE: a first-time run closes with its workflow file written (a podcast)", out
    old = workflow("Podcast", [(1, "Record", "on trial")], upgrades=["2026-11-09 · v1.0 · first · why: x · from: ruling 1"])
    root = first_time(tmp_path / "old", old)  # dated before the run's Go
    assert run(root, "--check")[0] == 1
    held = workflow("Podcast", [(1, "Record", "foundation · 1 job")],
                    upgrades=["2026-11-10 · v1.0 · first · why: x · from: ruling 1"])
    root = first_time(tmp_path / "held", held)  # a step already a foundation
    assert run(root, "--check")[0] == 1


def test_the_first_time_close_passes_with_its_workflow_file_written(tmp_path):
    flow = workflow("Podcast", [(1, "Record", "on trial"), (2, "Edit", "idea")],
                    upgrades=["2026-11-10 · v1.0 · first written from the pilot · why: first time · from: ruling 3"])
    root = first_time(tmp_path, flow)
    code, out = run(root, "--check")
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 1 closed", out
    root = first_time(tmp_path / "plain", None, kind="- the pilot, again")  # no First time: line, no workflow needed
    assert run(root, "--check") == (0, "UPGRADE DONE: Run 1 closed\n")


def test_check_reads_a_failing_earlier_close_though_the_newest_passes(tmp_path):
    lines, rows, files, brief = passing(tmp_path)
    decisions = (DECISIONS + closing(rows=rows[:3], when="2026-11-11 10:00")
                 + "\n## 2026-11-11 11:00 — Not a close\nnothing\n"
                 + closing(title="Review closed: the deep review", when="2026-11-11 12:00", rows=rows[3:]))
    root = project(tmp_path, lines, decisions=decisions, brief=brief, files=files)
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L004 has no row in Run 1 closed", "REFUSE: L005 has no row in Run 1 closed",
                                        "UPGRADE DONE: Review closed: the deep review"], out


def test_check_refuses_a_closing_entry_with_no_block(tmp_path):
    root = project(tmp_path, [lesson(1, "change", "CLAUDE.md", "x")], decisions=DECISIONS + closing(block=False))
    code, out = run(root, "--check")
    assert code == 1 and out.strip() == "REFUSE: Run 1 closed has no ### The upgrade block", out


def test_check_passes_with_no_lessons_file(tmp_path):
    root = project(tmp_path, decisions=DECISIONS + closing(block=False), lessons_file=False)
    code, out = run(root, "--check")
    assert code == 0 and out.strip() == "not gated: no docs/lessons.md", out
    passed, faults, title = upgrade.check(root)
    assert passed and faults == [] and title == "Run 1 closed"
    assert upgrade.waiting(root) == []


def test_waiting_gives_dicts_oldest_first_and_check_gives_none_with_no_close(tmp_path):
    root = project(tmp_path, [lesson(2, "works", "CLAUDE.md", "the way", when="2026-11-10 10:00", seen="a pass line"),
                              lesson(1, "change", "CLAUDE.md", "One.", when="2026-11-10 09:00")])
    found = upgrade.waiting(root)
    assert [l["n"] for l in found] == ["L001", "L002"]
    assert found[1] == {"n": "L002", "time": "2026-11-10 10:00", "from": "run 1", "kind": "works",
                        "what": "what happened", "file": "CLAUDE.md", "line": "the way", "seen": "a pass line",
                        "sort": "his", "limits": False, "same": None}
    assert found[0]["seen"] is None
    assert upgrade.check(root) == (True, [], None)


# Lessons on probation: the his, new, retire and refuse groups (contracts 2, 3 and 9),
# every close since the last passing one, and a house's own blank.

def sorted_lesson(n, kind, file, line, sort=None, same=None, when="2026-11-10 09:00", seen=None):
    """A lesson in contract 2's 0.9.0 form (no sort: writes the form before 0.9.0)."""
    text = f'- L{n:03d} · {when} · run 1 · {kind} · what happened · file: {file} · "{line}"'
    text += (f" · sort: {sort}" if sort else "") + (f" · same: {same}" if same else "")
    return text + (f" · seen: {seen}" if seen else "")


def test_the_his_group_shows_the_five_oldest_his_lessons_and_counts_the_rest(tmp_path):
    lines = [sorted_lesson(n, "change", "CLAUDE.md", f"line {n}", sort="his", when=f"2026-11-{20 - n:02d} 09:00")
             for n in range(1, 6)]
    lines += [lesson(6, "change", "CLAUDE.md", "an old line, no sort", when="2026-11-01 09:00"),
              lesson(7, "works", "CLAUDE.md", "another", when="2026-11-02 09:00", seen="a pass"),
              sorted_lesson(8, "change", "CLAUDE.md", "routine", sort="routine", when="2026-11-01 08:00"),
              sorted_lesson(9, "change", "template", "the template's", sort="template", when="2026-11-01 08:00")]
    root = project(tmp_path, lines, files={"CLAUDE.md": "x\n"})
    g = listed(root)
    assert numbers(g["his"]) == ["L006", "L007", "L005", "L004", "L003"]  # oldest first, five at most
    assert g["his"]["count"] == 7 and g["his"]["rest"] == 2
    assert "L001" in numbers(g["lines"]) and "L009" in numbers(g["template"])  # still in their own groups
    code, out = run(root)
    assert code == 0, out
    part = out.split("0a. his lessons (five at most shown) (7)\n")[1].split("\n\n")[0].splitlines()
    assert len(part) == 6 and part[-1] == "   and 2 more his lessons waiting", part
    titles = ["0. needs thought", "0a. his lessons", "1. lines", "2. suggested foundations", "2a. candidate tracks",
              "3. foundations to reopen", "4. for the template", "5. on probation (new)", "6. retire",
              "7. refuse, narrow or strike"]
    assert [out.index(t) for t in titles] == sorted(out.index(t) for t in titles), out


def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                           *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def test_a_new_mark_is_listed_with_the_git_revert_of_the_commit_that_wrote_it(tmp_path):
    lines = [sorted_lesson(2, "change", "docs/method.md", "Run the gate once.", sort="routine"),
             sorted_lesson(3, "change", "docs/method.md", "Read the brief.", sort="routine")]
    root = project(tmp_path, lines, files={"docs/method.md": "# Method\n\nRead the brief.\n"})
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "before the mark")
    (root / "docs" / "method.md").write_text("# Method\n\nRead the brief.\nRun the gate once. [new L002 2026-11-12]\n",
                                             encoding="utf-8", newline="\n")
    git(root, "commit", "-q", "-am", "the mark")
    wrote = git(root, "rev-parse", "--short", "HEAD")
    g = listed(root)
    assert g["new"]["items"] == [{"n": "L002", "date": "2026-11-12", "file": "docs/method.md",
                                  "line": "Run the gate once. [new L002 2026-11-12]", "undo": f"git revert {wrote}"}]
    code, out = run(root)
    assert f'   L002 · docs/method.md · "Run the gate once. [new L002 2026-11-12]" · undo: git revert {wrote}' in out, out


def test_a_new_mark_not_in_git_names_how_to_find_its_commit(tmp_path):
    root = project(tmp_path, [sorted_lesson(2, "change", "docs/method.md", "Run the gate once.", sort="routine")],
                   files={"docs/method.md": "Run the gate once. [new L002 2026-11-12]\n"})
    [item] = listed(root)["new"]["items"]
    assert item["undo"].startswith("git revert <the commit that wrote the mark>"), item


def retire_project(tmp_path, closes, backed=False):
    lines = [sorted_lesson(2, "change", "docs/method.md", "Run the gate once.", sort="routine")]
    if backed:
        lines.append(sorted_lesson(3, "works", "docs/method.md", "it helped", sort="his", same="L002", seen="a pass"))
    decisions = DECISIONS + "".join(closing(title=f"Run {i + 1} closed", when=f"2026-11-{13 + i} 10:00", block=False)
                                    for i in range(closes))
    return project(tmp_path, lines, decisions=decisions,
                   files={"docs/method.md": "Run the gate once. [new L002 2026-11-12]\n"})


def test_a_new_line_is_listed_to_retire_after_three_closes_and_not_after_two(tmp_path):
    assert listed(retire_project(tmp_path / "two", 2))["retire"]["items"] == []
    g = listed(retire_project(tmp_path / "three", 3))
    assert [i["n"] for i in g["retire"]["items"]] == ["L002"] and [i["n"] for i in g["new"]["items"]] == ["L002"]
    code, out = run(retire_project(tmp_path / "printed", 3))
    assert "6. retire (1)\n   L002 · docs/method.md · \"Run the gate once. [new L002 2026-11-12]\" · undo: git revert" in out, out


def test_a_new_line_a_works_lesson_names_is_not_listed_to_retire(tmp_path):
    g = listed(retire_project(tmp_path, 3, backed=True))
    assert g["retire"]["items"] == [] and [i["n"] for i in g["new"]["items"]] == ["L002"]


def test_a_third_sighting_is_listed_to_refuse_narrow_or_strike(tmp_path):
    two = [sorted_lesson(1, "misfire", "CLAUDE.md", "a heredoc", seen="it broke"),
           sorted_lesson(2, "misfire", "CLAUDE.md", "a heredoc again", same="L001", seen="it broke")]
    assert listed(project(tmp_path / "two", two, files={"CLAUDE.md": "x\n"}))["refuse"]["items"] == []
    three = two + [sorted_lesson(3, "misfire", "CLAUDE.md", "a third heredoc", same="L002", seen="it broke"),
                   sorted_lesson(4, "change", "CLAUDE.md", "unrelated")]
    root = project(tmp_path / "three", three, files={"CLAUDE.md": "x\n"})
    [item] = listed(root)["refuse"]["items"]
    assert item["n"] == "L003" and item["sightings"] == ["L001", "L002", "L003"]
    code, out = run(root)
    assert "7. refuse, narrow or strike (1)\n   L003 · misfire" in out and "sightings: L001, L002, L003" in out, out


def test_check_reads_two_closes_since_the_last_passing_one_oldest_first(tmp_path):
    lines = [lesson(1, "change", "CLAUDE.md", "One.", when="2026-11-10 09:00"),
             lesson(2, "change", "CLAUDE.md", "Two.", when="2026-11-12 09:00"),
             lesson(3, "change", "CLAUDE.md", "Three.", when="2026-11-14 09:00")]
    first = closing(title="Run 1 closed", when="2026-11-11 10:00", rows=[("L001", "drop", "", "")])
    second = closing(title="Run 2 closed", when="2026-11-13 10:00", rows=[])
    third = closing(title="Run 3 closed", when="2026-11-15 10:00", rows=[("L002, L003", "drop", "", "")])
    root = project(tmp_path, lines, decisions=DECISIONS + first + second + third, files={"CLAUDE.md": "x\n"})
    code, out = run(root, "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L002 has no row in Run 2 closed", "UPGRADE DONE: Run 3 closed"], out
    assert upgrade.check(root) == (False, ["L002 has no row in Run 2 closed"], "Run 3 closed")
    fourth = closing(title="Run 4 closed", when="2026-11-16 10:00", block=False)
    root = project(tmp_path / "again", lines, decisions=DECISIONS + first + second + third + fourth,
                   files={"CLAUDE.md": "x\n"})
    code, out = run(root, "--check")  # Run 3 is now the last passing one: only Run 4 is read
    assert code == 1 and out.strip().splitlines() == ["REFUSE: Run 4 closed has no ### The upgrade block"], out


def one_sitting(tmp_path, older_rows, newer_rows, newer_first=False, lines=None):
    """Two closes of one minute; a close given no rows says in words that the other holds the table."""
    def close(title, rows):
        if rows:
            return closing(title=title, when="2026-11-19 01:51", rows=rows)
        return f"\n## 2026-11-19 01:51 — {title}\nClosed.\n\n### The upgrade\nNone left: the other close holds the table.\n"
    older, newer = close("Run 9 closed", older_rows), close("Run 10 closed", newer_rows)
    lines = lines or [lesson(1, "change", "CLAUDE.md", "One."), lesson(2, "change", "CLAUDE.md", "Two.")]
    return project(tmp_path, lines, decisions=DECISIONS + (newer + older if newer_first else older + newer),
                   files={"CLAUDE.md": "x\n"})


def test_two_closes_of_one_sitting_pass_with_the_table_in_the_older(tmp_path):
    rows = [("L001, L002", "drop", "", "")]
    for name, newer_first in (("run-order", False), ("file-order", True)):
        root = one_sitting(tmp_path / name, rows, None, newer_first)
        assert [e["title"] for e in upgrade.closings(root)] == ["Run 9 closed", "Run 10 closed"]
        code, out = run(root, "--check")
        assert code == 0 and out.strip() == "UPGRADE DONE: Run 10 closed", out


def test_two_closes_of_one_sitting_pass_with_the_table_in_the_newer(tmp_path):
    rows = [("L001, L002", "drop", "", "")]
    for name, newer_first in (("run-order", False), ("file-order", True)):
        root = one_sitting(tmp_path / name, None, rows, newer_first)
        assert [e["title"] for e in upgrade.closings(root)] == ["Run 9 closed", "Run 10 closed"]
        code, out = run(root, "--check")
        assert code == 0 and out.strip() == "UPGRADE DONE: Run 10 closed", out
    waiting = [lesson(1, "change", "CLAUDE.md", "One."), lesson(2, "change", "CLAUDE.md", "Two."),
               lesson(3, "change", "CLAUDE.md", "Three, with no row in either.")]
    code, out = run(one_sitting(tmp_path / "missing", None, rows, lines=waiting), "--check")
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: L003 has no row in Run 9 closed",
                                        "REFUSE: L003 has no row in Run 10 closed"], out


def test_a_house_blank_is_filed_for_the_house_and_a_template_blank_for_the_template(tmp_path):
    root = project(tmp_path, [lesson(1, "change", "docs/blanks/shot-list.md", "A house line."),
                              lesson(2, "change", "docs/blanks/card.md", "A template line.")])
    g = listed(root)
    assert numbers(g["lines"]) == ["L001"] and numbers(g["template"]) == ["L002"]


def test_the_template_blank_names_are_the_blanks_the_template_ships(tmp_path):
    tools = os.path.dirname(TOOL)
    shipped = set(os.listdir(os.path.join(os.path.dirname(tools), "docs", "blanks")))
    if os.path.basename(os.path.dirname(tools)) == "template":
        assert set(upgrade.TEMPLATE_BLANKS) == shipped
    else:  # stamped in a house, whose own blanks sit beside the template's
        assert set(upgrade.TEMPLATE_BLANKS) <= shipped


# ---- rules nobody named, retired and restored (design Part 5) ----

WORKER_RULES = ("# Worker rules — test\n\n## Before you start\n\n"
                "1. **Read your card first.** Then its Read-first files.\n   Why: the card is the order.\n"
                "2. **Build only in your own worktree.** Never in the main checkout.\n\n"
                "   Why: one writer per copy.\n   A second line under it.\n\n## When you finish\n\n"
                "15. **Never end your turn while a command runs.**\n    Why: a worker once waited unseen.\n"
                "16. **Write files with the Write tool.**\n    Why: a heredoc mangled four cards.\n\n## Refusals\n\n"
                "1. **Push to main.** You push only your branch.\n   Why: nothing on GitHub stops it.\n")
TRACKS = ("# Tracks — test\n\n1. **A project is on the tracks** when its plan is signed.\n"
          "   Why: the box starts only signed work.\n2. **The two starts.** Tracks or now.\n")
ALL_RULES = [("tracks.md", 1), ("tracks.md", 2), ("worker-rules.md", 1), ("worker-rules.md", 2),
             ("worker-rules.md", 15), ("worker-rules.md", 16)]


def rules_decisions(closes):
    return DECISIONS + "".join(closing(title=f"Run {i + 1} closed", when=f"2026-11-{i + 1:02d} 10:00", block=False)
                               for i in range(closes))


def commit_before_the_closes(root, message):
    """Everything in the folder, committed on 1 Oct 2026, before every close of rules_project."""
    git(root, "add", "-A")
    old = dict(os.environ, GIT_AUTHOR_DATE="2026-10-01T10:00:00", GIT_COMMITTER_DATE="2026-10-01T10:00:00")
    subprocess.run(["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                    "commit", "-q", "-m", message], env=old, check=True, capture_output=True)


def rules_project(tmp_path, closes=5, lines=(), files=None):
    """Closes on 1 to <closes> Nov 2026, and the two rule files in git since before the first of them."""
    root = project(tmp_path, lines, decisions=rules_decisions(closes),
                   files=dict({"worker-rules.md": WORKER_RULES, "tracks.md": TRACKS}, **(files or {})))
    git(root, "init", "-q")
    commit_before_the_closes(root, "the start")
    return root


def to_retire(root):
    return [(i["file"], i["rule"]) for i in listed(root)["retire"]["items"] if "rule" in i]


def test_an_unnamed_rule_is_listed_to_retire_after_five_closes_and_not_after_four(tmp_path):
    assert to_retire(rules_project(tmp_path / "four", 4)) == []
    root = rules_project(tmp_path / "five", 5)
    assert to_retire(root) == ALL_RULES  # the refusal numbered 1 is a stop, not a rule
    code, out = run(root)
    assert ('   worker-rules.md rule 16 · "16. **Write files with the Write tool.**" · retire: python tools/upgrade.py '
            '--retire worker-rules.md 16 · undo: python tools/upgrade.py --restore worker-rules.md 16') in out, out


def test_a_rule_named_in_a_lesson_since_the_fifth_last_close_is_not_listed(tmp_path):
    root = rules_project(tmp_path, 6, lines=[
        lesson(1, "change", "worker-rules.md", "2. **Build only in your own worktree**, and say so.", when="2026-11-03 09:00"),
        lesson(2, "change", "tracks.md", "A project is on the tracks when signed.", when="2026-11-01 12:00"),
        lesson(3, "change", "CLAUDE.md", "Read your card first.", when="2026-11-05 09:00")])
    # Since 2 Nov: L001 names worker-rules.md rule 2; L002 is older; L003 names another file.
    assert to_retire(root) == [r for r in ALL_RULES if r != ("worker-rules.md", 2)]


def test_a_rule_named_in_a_receipt_or_a_docs_file_since_the_fifth_last_close_is_not_listed(tmp_path):
    root = rules_project(tmp_path, 5)
    (root / "docs" / "old.md").write_text("Held by worker-rules.md rule 16.\n", encoding="utf-8", newline="\n")
    commit_before_the_closes(root, "before the closes")
    receipt = root / "desks" / "d" / "docs" / "cards" / "receipts" / "x-close.md"
    receipt.parent.mkdir(parents=True)
    receipt.write_text("Held by `worker-rules.md` rule 15, and by rule 2.\n", encoding="utf-8", newline="\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a receipt")
    assert to_retire(root) == [("tracks.md", 1), ("worker-rules.md", 1), ("worker-rules.md", 2),
                               ("worker-rules.md", 16)]


def test_a_rule_named_by_a_counter_line_since_the_fifth_last_close_is_not_listed(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    root = rules_project(tmp_path, 5, files={"project.yaml": "name: sample\n"})
    counter = tmp_path / "local" / "agentic-meta" / "act-checks" / "sample.log"
    counter.parent.mkdir(parents=True)
    counter.write_text("2026-10-20 09:00:00 · sample · turn-end-running · warn · s1 · -\n"
                       "2026-11-04 09:00:00 · sample · heredoc-write · warn · s2 · cat <<EOF > x⏎a⏎EOF\n"
                       "2026-11-04 09:01:00 · sample · wildcard-delete · warn · s2 · rm -rf /tmp/a*\n",
                       encoding="utf-8", newline="\n")
    # heredoc-write holds worker-rules.md rule 16; the turn-end line is older than the fifth-last close.
    assert to_retire(root) == [r for r in ALL_RULES if r != ("worker-rules.md", 16)]


def test_a_rule_younger_than_five_closes_is_not_listed(tmp_path):
    root = rules_project(tmp_path, 5)
    young = WORKER_RULES.replace("\n## Refusals", "17. **Written this week.**\n    Why: a new rule.\n\n## Refusals")
    (root / "worker-rules.md").write_text(young, encoding="utf-8", newline="\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a rule written after the fifth-last close")
    unread = young.replace("\n## Refusals", "18. **Never committed.**\n    Why: no history.\n\n## Refusals")
    (root / "worker-rules.md").write_text(unread, encoding="utf-8", newline="\n")
    assert to_retire(root) == ALL_RULES  # neither 17 (too young) nor 18 (no readable history)
    no_git = project(tmp_path / "no-git", decisions=rules_decisions(5), files={"tracks.md": TRACKS})
    assert to_retire(no_git) == []


PART_RULES = "# Worker rules — test\n\n" + "".join(f"{n}. **Rule number {n}.**\n   Why: a reason.\n"
                                                    for n in (3, 4, 5, 6, 13, 14))
PARTS = "## Parked\nnone\n\n## Checker run 2026-11-19 — a checker, own session\nScope: nothing extra\nVerdict: PASS\n"


def receipt(root, path, text):
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8", newline="\n")


def test_a_rule_a_receipt_part_applies_is_not_listed(tmp_path):
    root = rules_project(tmp_path / "parts", 5, files={"worker-rules.md": PART_RULES})
    receipt(root, "docs/cards/receipts/a-close.md", "DONE\n\n## Parked\nnone\n")
    receipt(root, "desks/d/docs/cards/receipts/b-close.md", PARTS.split("\n\n", 1)[1])
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "two receipts")
    assert to_retire(root) == [("tracks.md", 1), ("tracks.md", 2), ("worker-rules.md", 3)]
    every = [("tracks.md", 1), ("tracks.md", 2)] + [("worker-rules.md", n) for n in (3, 4, 5, 6, 13, 14)]
    elsewhere = rules_project(tmp_path / "elsewhere", 5, files={"worker-rules.md": PART_RULES})
    receipt(elsewhere, "docs/cards/receipts/c-close.md", "Scope: not in a Checker run block\nVerdict: PASS\n")
    receipt(elsewhere, "docs/cards/receipts/d.md", PARTS)  # not a close's receipt
    receipt(elsewhere, "docs/notes/e-close.md", PARTS)  # not in a receipts folder
    git(elsewhere, "add", "-A")
    git(elsewhere, "commit", "-q", "-m", "parts that apply nothing")
    assert to_retire(elsewhere) == every
    before = rules_project(tmp_path / "before", 5, files={"worker-rules.md": PART_RULES})
    receipt(before, "docs/cards/receipts/f-close.md", PARTS)
    commit_before_the_closes(before, "a receipt older than the fifth-last close")
    assert to_retire(before) == every


def test_an_old_rule_nobody_applies_is_still_listed(tmp_path):
    root = rules_project(tmp_path, 6)
    receipt(root, "docs/cards/receipts/a-close.md", PARTS)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a receipt whose parts apply other rules")
    assert to_retire(root) == ALL_RULES


def test_retire_moves_the_rule_with_its_why_and_leaves_the_stub(tmp_path):
    root = rules_project(tmp_path, 5)
    code, out = run(root, "--retire", "worker-rules.md", "2")
    assert code == 0, out
    stub = re.compile(r"2\. Retired \d{4}-\d{2}-\d{2}: docs/retired\.md\.")
    after = (root / "worker-rules.md").read_text(encoding="utf-8").splitlines()
    before = WORKER_RULES.splitlines()
    assert stub.fullmatch(after[6]), after
    assert after[:6] == before[:6] and after[7:] == before[10:]  # every other rule, and its number, as it was
    retired = (root / "docs" / "retired.md").read_text(encoding="utf-8").splitlines()
    at = next(i for i, l in enumerate(retired) if l.startswith("- "))
    assert re.fullmatch(r'- \d{4}-\d{2}-\d{2} · worker-rules\.md · "2\. \*\*Build only in your own worktree\.\*\* Never '
                        r'in the main checkout\." · why: .+ · undo: python tools/upgrade\.py --restore worker-rules\.md 2',
                        retired[at]), retired
    assert retired[at + 1:] == ["  |", "  |    Why: one writer per copy.", "  |    A second line under it."]
    assert "RETIRED: worker-rules.md rule 2" in out and stub.search(out) and retired[at] in out, out
    assert ("worker-rules.md", 2) not in to_retire(root)  # the stub is not a rule


def test_restore_puts_the_rule_back_word_for_word(tmp_path):
    root = rules_project(tmp_path, 5)
    original = WORKER_RULES.replace("\n", "\r\n").encode("utf-8")
    (root / "worker-rules.md").write_bytes(original)
    assert run(root, "--retire", "worker-rules.md", "15")[0] == 0
    code, out = run(root, "--restore", "worker-rules.md", "15")
    assert code == 0, out
    assert (root / "worker-rules.md").read_bytes() == original
    retired = (root / "docs" / "retired.md").read_text(encoding="utf-8").splitlines()
    at = next(i for i, l in enumerate(retired) if l.startswith("- ") and '"15. **Never end' in l)  # kept, never deleted
    assert retired[at + 1] == "  |     Why: a worker once waited unseen."
    assert re.fullmatch(r"  Restored \d{4}-\d{2}-\d{2}: back in worker-rules\.md as rule 15\.", retired[at + 2]), retired
    assert "RESTORED: worker-rules.md rule 15" in out and retired[at + 2] in out, out
    code, out = run(root, "--restore", "worker-rules.md", "15")  # nothing left to put back
    assert code == 1 and out.startswith("REFUSE: worker-rules.md has no line"), out


def test_docs_retired_is_opened_from_the_blank_then_added_to(tmp_path):
    root = rules_project(tmp_path, 5, files={"docs/blanks/retired.md": "# Retired — sample\n\nThe head.\n"})
    code, out = run(root, "--retire", "tracks.md", "1")
    assert code == 0 and "docs/retired.md (opened from docs/blanks/retired.md):" in out, out
    code, out = run(root, "--retire", "tracks.md", "2")
    assert code == 0 and "opened from" not in out, out
    retired = (root / "docs" / "retired.md").read_text(encoding="utf-8").splitlines()
    assert retired[:4] == ["# Retired — sample", "", "The head.", ""]
    assert [l.split(" · ")[2][:3] for l in retired if l.startswith("- ")] == ['"1.', '"2.']
    assert retired[5] == "  |    Why: the box starts only signed work."


def test_the_templates_own_blank_opens_docs_retired_when_the_project_has_none(tmp_path):
    root = rules_project(tmp_path, 5)
    assert run(root, "--retire", "tracks.md", "2")[0] == 0
    blank = os.path.join(os.path.dirname(os.path.dirname(TOOL)), "docs", "blanks", "retired.md")
    with open(blank, encoding="utf-8") as f:
        head = f.read().rstrip("\n").splitlines()
    retired = (root / "docs" / "retired.md").read_text(encoding="utf-8").splitlines()
    assert retired[:len(head)] == head and retired[len(head)] == ""
    assert retired[len(head) + 1].startswith('- ') and ' · tracks.md · "2. **The two starts.**' in retired[len(head) + 1]


def test_retire_refuses_a_rule_that_is_not_there_and_changes_nothing(tmp_path):
    root = rules_project(tmp_path, 5)
    code, out = run(root, "--retire", "worker-rules.md", "9")
    assert code == 1 and out.strip() == 'REFUSE: worker-rules.md has no rule 9 (a line "9. **...**")', out
    assert (root / "worker-rules.md").read_text(encoding="utf-8") == WORKER_RULES
    assert not (root / "docs" / "retired.md").exists()


# The house's catch (his words of 21 Nov 2026, "this needs to be an automatic catch"): where a harvest.py
# sits beside upgrade.py, a run's close is refused while lessons from the other projects that waited before
# its Go are not carried. Each test runs a copy of the tools with a small stand-in harvest.py beside it.

def stand_in(first="waiting before {stamp}: {n}", n=0, code=0, go="2026-11-21 04:00"):
    """A harvest.py that checks it was asked for the run's Go and prints the contract's first line (or another)."""
    return ("import sys\n"
            f"assert sys.argv[1:] == ['--waiting-before', {go!r}], sys.argv\n"
            f"print({first!r}.format(stamp=sys.argv[2], n={n}))\n"
            "print('house-x: no lessons file')\n"
            f"sys.exit({code})\n")


def catch(tmp_path, harvest=None, go="- Start: 2026-11-21 04:00", closed="2026-11-21 10:00"):
    """Run 9 closed with a block that passes, its record's Go line, and a copy of the tools with the harvest
    (a stand-in's text) beside it, or none. Returns the project and the copy's upgrade.py."""
    lines, rows, files, brief = passing(tmp_path)
    files = dict(files, **{"docs/runs/9/run.md": f"# Run 9 — test\n\n## Go\n{go}\n"})
    rows = rows + [("L006", "drop", "", "")]
    root = project(tmp_path, lines, decisions=DECISIONS + closing("Run 9 closed", closed, rows), brief=brief,
                   files=files)
    tools = tmp_path / "tools"
    tools.mkdir()
    for name in os.listdir(os.path.dirname(TOOL)):
        # Never a harvest.py from beside upgrade.py: a house keeps its own there (L054); only harvest= gives one.
        if name.endswith(".py") and name != "harvest.py":
            shutil.copy2(os.path.join(os.path.dirname(TOOL), name), tools / name)
    if harvest is not None:
        (tools / "harvest.py").write_text(harvest, encoding="utf-8")
    return root, str(tools / "upgrade.py")


def run_copy(tool, root):
    done = subprocess.run([sys.executable, "-B", tool, "--project", str(root), "--check"],
                          capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout + done.stderr


def load_copy(tool):
    spec = importlib.util.spec_from_file_location("upgrade_copy_for_tests", tool)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_close_is_refused_while_lessons_wait_uncarried_before_its_go(tmp_path):
    root, tool = catch(tmp_path, stand_in(n=3))
    code, out = run_copy(tool, root)
    fault = ("run 9's close: 3 lessons from the other projects waited before its Go and are not carried: "
             "run python tools/harvest.py")
    assert code == 1, out
    assert out.strip().splitlines() == [f"REFUSE: {fault}"], out
    # check(), which where_am_i.py and record.py load, reads the same answer.
    assert load_copy(tool).check(root) == (False, [fault], "Run 9 closed")


def test_a_close_passes_when_the_harvest_says_none_wait(tmp_path):
    root, tool = catch(tmp_path, stand_in(n=0))
    code, out = run_copy(tool, root)
    assert code == 0, out
    assert out.strip() == "UPGRADE DONE: Run 9 closed", out


def test_a_harvest_that_cannot_be_read_refuses_the_close(tmp_path):
    for i, (harvest, why) in enumerate([
            (stand_in(first="house lessons waiting: 0"), 'harvest.py said "house lessons waiting: 0"'),
            (stand_in(first="waiting before 2026-11-20 00:00: 0"), 'harvest.py said "waiting before 2026-11-20 00:00: 0"'),
            (stand_in(code=3), "harvest.py exited 3"),
            (stand_in(go="another Go"), "harvest.py exited 1")]):
        root, tool = catch(tmp_path / str(i), harvest)
        code, out = run_copy(tool, root)
        assert code == 1, out
        assert out.strip().splitlines() == [f"REFUSE: run 9's close: the harvest was not read ({why})"], out
    # A harvest that does not answer in time.
    root, tool = catch(tmp_path / "slow", "import time\ntime.sleep(20)\n")
    module = load_copy(tool)
    module.HARVEST_TIMEOUT = 1
    assert module.check(root)[1] == ["run 9's close: the harvest was not read (no answer in 1 seconds)"]
    # A Go that cannot be read refuses too.
    root, tool = catch(tmp_path / "no-go", stand_in(n=0), go="- Planned end: 2026-11-21 12:00")
    code, out = run_copy(tool, root)
    assert code == 1, out
    assert out.strip().splitlines() == ["REFUSE: run 9's close: its Go could not be read from docs/runs/9/run.md"], out


def test_no_harvest_beside_it_checks_nothing_new(tmp_path):
    root, tool = catch(tmp_path, None, go="- Planned end: 2026-11-21 12:00")
    code, out = run_copy(tool, root)
    assert code == 0, out
    assert out.strip() == "UPGRADE DONE: Run 9 closed", out
    assert load_copy(tool).check(root) == (True, [], "Run 9 closed")


def test_a_close_before_the_catch_began_is_not_judged_by_it(tmp_path):
    # Run 8's Go (19 Nov), closed after the catch began: not judged, whatever the harvest says.
    root, tool = catch(tmp_path / "go", stand_in(n=129, go="2026-11-19 03:07"), go="- Start: 2026-11-19 03:07")
    code, out = run_copy(tool, root)
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 9 closed", out
    # A close before the catch began: its Go is earlier still, so it is not read at all.
    root, tool = catch(tmp_path / "closed", stand_in(n=129), go="- Planned end: 2026-11-21 12:00",
                       closed="2026-11-21 02:57")
    code, out = run_copy(tool, root)
    assert code == 0 and out.strip() == "UPGRADE DONE: Run 9 closed", out
    # Run 9's own Go, 03:32 as its record reads it, is judged.
    root, tool = catch(tmp_path / "run-9", stand_in(n=129, go="2026-11-21 03:32"), go="- Start: 2026-11-21 03:32")
    code, out = run_copy(tool, root)
    assert code == 1 and "129 lessons from the other projects" in out, out
