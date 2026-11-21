# upgrade.py: the upgrade's list, written from the files, and the check of its close.
#
# What it holds
#   Every review ends with the upgrade: each lesson the project has learnt
#   and not yet put to Rhys, sorted so he can answer it. This tool reads
#   these things and nothing else:
#     - docs/lessons.md, the lessons as record.py --lesson writes them;
#     - the closing entries in docs/decisions.md and any docs/decisions-*.md
#       (a heading "## <yyyy-mm-dd hh:mm> — Run <n> closed ..." or
#       "— Review closed ..."), each with its "### The upgrade" table
#       | L-numbers | his answer | the line as kept | where it is |;
#     - the workflow files' tags, read by status.py beside it: a step or a
#       Tag: line tagged `foundation · <n> job(s)` is a foundation;
#     - for a first-time run, its plan's "First time:" line and its record's
#       Go start (docs/runs/<n>/plan-signed.md and run.md).
#   With no option it prints every lesson not answered in any closing block,
#   in groups: 0 needs thought (named by the master, kept out of approve
#   all), 1 lines to keep, change or drop (approve all), 2 suggested
#   foundations, 2a candidate tracks, 3 foundations to reopen as trials and
#   the foundations, 4 for the template; then 0a his lessons (the oldest
#   HIS_SHOWN with sort: his, the rest counted), 5 on probation (each kept
#   line ending " [new L<nnn> <date>]", with its git revert), 6 retire (a
#   new line no works lesson names by same: after RETIRE_AFTER_JOBS closes
#   since its date; and a rule of tracks.md or worker-rules.md, a numbered
#   line "<n>. **...**", that no lesson, counter line or docs/ file named
#   in the last RETIRE_UNNAMED_JOBS closes, that git held before the first of
#   those closes, and that no receipt part applied since), 7 refuse, narrow or strike (a
#   lesson whose same: chain holds SIGHTINGS). A lesson on a
#   docs/blanks/<name> the template does not ship is the house's own. With --check it checks every closing entry
#   since the last passing one, oldest first: a row for every lesson it had
#   to answer, each kept
#   line found word for word in its file, each workflow file's "## Upgrades"
#   line, a foundation row's file holding a foundation tag, and the
#   first-time close.
#   Two functions are loaded by its neighbours (where_am_i.py loads this file
#   beside it): waiting(project) and check(project).
#
# Why it exists
#   The counted review fell due three times and ran once: it was a memory
#   test that nothing checked (the upgrade design of 12 Nov 2026, § 2 cause
#   1). Here the list comes from the files, never from memory, and a close
#   without its upgrade is seen. His rulings of 12 Nov 09:14 (docs/decisions.md,
#   "The upgrade ruled"): 2, the "needs thought" group, highlighted and kept
#   out of approve all; 8, candidate tracks; 9, numbers inform his word,
#   never judge it. So this tool judges nothing: it lists the evidence and
#   checks the record. Every way of working with a works lesson is
#   suggested, whatever the count; a foundation is his word.
#   The three words (design of 17 Nov 2026, Part 3; his rulings 3 and 4 of
#   17 Nov 07:43): foundations are read from the workflow files' tags, never
#   from a brief line that "none" could be mistaken for; and a first-time run
#   closes only with its workflow file written.
#   Lessons on probation (design Part 4; his rulings 2 and 5 of 17 Nov
#   07:43): lessons waited weeks for a review, and a house blank was filed for
#   the template (12 Nov fault 2); so his wait five at a time, routine ones are
#   listed with their undo and retired unless a job backs them up, and no
#   close is passed over because a later one passed.
#   Retirement (design Part 5; his ruling 2 of 17 Nov 07:43, "the record never
#   forgets; what agents read stays small"): a rule nobody needs leaves what
#   agents read for docs/retired.md, moved and never deleted, with its undo.
#   A rule is named by its use too (L035): the first list named rules written
#   that same day, and rules every receipt's Parked, Scope and Verdict apply.
#   Closes of one minute are one sitting (19 Nov 2026): they read in run order,
#   and a lesson's row may stand in either, so the table can sit in the older.
#   The house's catch (his words of 21 Nov 2026, "this feature is broken and
#   needs reworked. this needs to be an automatic catch"; tracks.md rule 46, a
#   tool that refuses the act): where a harvest.py sits beside this file (the
#   template's home only), --check runs it with --waiting-before the run's Go
#   (measures.py's start_of, loaded from beside it) at each "Run <n> closed" it
#   checks, and refuses the close while lessons from the other projects that
#   waited before its Go are not carried; a Go or a harvest it cannot read
#   refuses too, for a catch that passes when it cannot look is the fault. A
#   run whose Go is before CATCH_BEGAN (run 9's) is not judged by it.
#
# How to run it (from the project's top folder)
#   python tools/upgrade.py                          the list
#   python tools/upgrade.py --needs-thought L012,L019
#   python tools/upgrade.py --json                   the same groups, as JSON
#   python tools/upgrade.py --check                  each close since the last passing one: UPGRADE DONE:,
#                                                    or one REFUSE: line per fault; exit 1 on any fault
#   python tools/upgrade.py --retire <file> <n>      moves rule <n> of <file> (its numbered line and its
#                                                    Why: lines) to docs/retired.md, leaving the line
#                                                    "<n>. Retired <yyyy-mm-dd>: docs/retired.md."
#   python tools/upgrade.py --restore <file> <n>     puts it back in place of that line, with a restored
#                                                    note under its entry in docs/retired.md
#   --project <folder> reads another project (default: the folder it is run in).
#   --harvest <path> names the harvest.py --check runs (default: one beside this file, if any).
#   Only --retire and --restore write files, and neither commits. It touches no
#   network. Python 3 standard library only.

import argparse
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HIS_SHOWN = 5          # his lessons shown at the top of a review; the rest counted
RETIRE_AFTER_JOBS = 3  # closes since a new line's date with no works lesson naming it
SIGHTINGS = 3          # lessons chained by same: before "refuse, narrow or strike"
RETIRE_UNNAMED_JOBS = 5  # closes in which nobody named a rule before it is listed to retire

# status.py, beside this file: the one reading of the workflow files' tags.
_spec = importlib.util.spec_from_file_location("status_for_upgrade",
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.py"))
status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(status)
# act_check.py, beside this file, read when the counter is (contract 1); a copy of this tool without it reads no counter.
ACT_CHECK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "act_check.py")
# The house's catch: harvest.py beside this file (the template's home only), and measures.py for a run's Go.
HARVEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harvest.py")
MEASURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "measures.py")
CATCH_BEGAN = "2026-11-21 03:32"   # run 9's Go as its record reads it, the first run with the catch
HARVEST_TIMEOUT = 60
WAITING_BEFORE = re.compile(r"waiting before (\d{4}-\d{2}-\d{2} \d{2}:\d{2}): (\d+)")

ANSWERS = ("keep", "change", "drop", "foundation", "trial", "reopen", "not now")
# The answers of a block written before 0.9.0, read as their new words (the record never forgets).
OLD_ANSWERS = {"lock": "foundation", "unlock": "trial"}
# The files the template owns: a change to one is listed for the template, never edited in the project.
TEMPLATE_FILES = ("tracks.md", ".claude/skills/run/SKILL.md", ".claude/skills/conductor/SKILL.md",
                  "operator.md", "worker-rules.md", "pages.md")
TEMPLATE_FOLDERS = ("roles/", "tools/")
# The blanks the template ships (template/docs/blanks/); any other docs/blanks/<name> is the house's own.
TEMPLATE_BLANKS = ("act-file.txt", "asks-entry.md", "brief.md", "card.md", "decisions-entry.md",
                   "github-reminder.txt", "lessons.md", "page.html", "plan-signed.md", "receipt.md",
                   "retired.md", "review-note.md", "run.md", "workflow.md")
# The files whose numbered rules may be listed to retire, and the line a retired rule leaves.
RULE_FILES = ("tracks.md", "worker-rules.md")
RULE = re.compile(r"^(\d+)\. \*\*(.+?)\*\*")
STUB = "{n}. Retired {date}: docs/retired.md."
STUB_LINE = re.compile(r"^(\d+)\. Retired \d{4}-\d{2}-\d{2}: docs/retired\.md\.$")
NAMED = re.compile(r"(?:`?([\w./-]+\.md)`?\s+)?\brule (\d+)\b", re.IGNORECASE)
COUNTED = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) · [^·]* · ([\w-]+) · ")
KEPT = "  | "            # a retired rule's continuation line, kept word for word under its entry
# The committed receipts of the project and its desks, and the worker-rules.md rules their parts apply (L035).
RECEIPTS = (":(glob)docs/cards/receipts/*-close.md", ":(glob)desks/*/docs/cards/receipts/*-close.md")
PARKED_APPLIES, SCOPE_APPLIES, VERDICT_APPLIES = (4,), (5, 6, 13), (14,)

LESSON = re.compile(r"- L(\d+) · ")
HEADING = re.compile(r"## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) — (.+?)\s*$")
CLOSING_TITLE = re.compile(r"(Run \d+ closed|Review closed)")
RUN_CLOSED = re.compile(r"Run (\d+) closed")
L_NUMBER = re.compile(r"\bL(\d+)\b")
FIRST_TIME = re.compile(r"^(?:- )?First time:\s*(.+?)\s*$", re.M)
GO_START = re.compile(r"^- Start:\s*(\d{4}-\d{2}-\d{2})", re.M)
DATED = re.compile(r"^(?:- )?(\d{4}-\d{2}-\d{2})\b")
SEEN = " · seen: "
SORT = re.compile(r" · sort: (routine|his|template)\b")
SAME = re.compile(r" · same: L(\d+)\b")
MARK = re.compile(r" \[new L(\d+) (\d{4}-\d{2}-\d{2})\]\s*$")


def _read(path):
    return path.read_text(encoding="utf-8", errors="replace")


def _clean(name):
    """A file name as written in a lesson or a row: outer backticks off, forward slashes."""
    name = name.strip()
    while len(name) >= 2 and name[0] == name[-1] and name[0] in "`\"":
        name = name[1:-1].strip()
    name = name.replace("\\", "/")
    return name[2:] if name.startswith("./") else name


def _time(text):
    return datetime.datetime.strptime(text, "%Y-%m-%d %H:%M")


# ---- the reads ----

def lessons(project):
    """Every lesson line of docs/lessons.md, as dicts, in file order. None when there is no file."""
    path = Path(project) / "docs" / "lessons.md"
    if not path.is_file():
        return None
    found = []
    for line in _read(path).splitlines():
        line = line.rstrip()
        if not LESSON.match(line):
            continue
        parts = line.split(" · ", 6)
        if len(parts) < 7 or not parts[5].startswith("file: "):
            continue
        rest = parts[6]
        seen = None
        cut = rest.rfind(SEEN)
        if cut != -1:
            rest, seen = rest[:cut], rest[cut + len(SEEN):]
        first, last = rest.find('"'), rest.rfind('"')
        exact = rest[first + 1:last] if first != -1 and last > first else rest
        tail = rest[last + 1:] if first != -1 and last > first else ""  # contract 2's fields, after the line
        sort, same = SORT.search(tail), SAME.search(tail)
        try:
            when = _time(parts[1])
        except ValueError:
            continue
        found.append({"n": parts[0][2:], "time": parts[1], "from": parts[2], "kind": parts[3],
                      "what": parts[4], "file": _clean(parts[5][len("file: "):]), "line": exact,
                      "seen": seen, "sort": sort.group(1) if sort else "his",  # no sort: (before 0.9.0) reads his
                      "limits": " · limits: made" in tail, "same": f"L{int(same.group(1)):03d}" if same else None,
                      "_when": when, "_int": int(parts[0][3:])})
    return found


def _cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    return [cell.replace("\\|", "|").strip() for cell in re.split(r"(?<!\\)\|", row)]


def closings(project):
    """The closing entries, oldest first: title, time, the block's rows (None with no block), and faults."""
    docs = Path(project) / "docs"
    files = [docs / "decisions.md"] + sorted(docs.glob("decisions-*.md"))
    entries = []
    for order, path in enumerate(f for f in files if f.is_file()):
        entry = None
        in_block = False
        for i, line in enumerate(_read(path).splitlines()):
            if line.startswith("## "):
                in_block = False
                entry = None
                m = HEADING.match(line)
                if m and CLOSING_TITLE.match(m.group(2)):
                    try:
                        when = _time(m.group(1))
                    except ValueError:
                        continue
                    run = RUN_CLOSED.match(m.group(2))  # one minute's closes sort by run number, wherever they stand
                    entry = {"title": m.group(2), "time": m.group(1), "rows": None, "faults": [],
                             "_key": (when, 0 if run else 1, int(run.group(1)) if run else 0, order, i)}
                    entries.append(entry)
                continue
            if entry is None:
                continue
            if line.startswith("### "):
                in_block = line.strip() == "### The upgrade"
                if in_block and entry["rows"] is None:
                    entry["rows"] = []
                continue
            if in_block and line.lstrip().startswith("|"):
                cells = _cells(line)
                if cells and cells[0].lower() == "l-numbers":
                    continue
                if all(re.fullmatch(r":?-+:?", c) for c in cells if c) and any(cells):
                    continue
                numbers = [int(n) for n in L_NUMBER.findall(cells[0])] if cells else []
                if len(cells) != 4 or not numbers:
                    entry["faults"].append(f"{entry['title']}: a row of ### The upgrade is not "
                                           f"| L-numbers | his answer | the line as kept | where it is |: {line.strip()}")
                    continue
                answer = cells[1].lower()
                entry["rows"].append({"numbers": numbers, "label": cells[0],
                                      "answer": OLD_ANSWERS.get(answer, answer),
                                      "line": cells[2], "where": _clean(cells[3])})
    entries.sort(key=lambda e: e["_key"])
    return entries


# ---- what waits ----

def _answers(entries):
    """L-number (int) -> the answer it was given, from these entries' blocks (the latest wins)."""
    given = {}
    for entry in entries:
        for row in entry["rows"] or []:
            for n in row["numbers"]:
                given[n] = row["answer"]
    return given


def _public(lesson):
    return {k: v for k, v in lesson.items() if not k.startswith("_")}


def _waiting(all_lessons, entries):
    answered = _answers(entries)
    left = [l for l in all_lessons if l["_int"] not in answered]
    return sorted(left, key=lambda l: (l["_when"], l["_int"]))


def waiting(project):
    """The lessons not answered in any closing block, oldest first. [] when there is no lessons file."""
    found = lessons(project)
    if found is None:
        return []
    return [_public(l) for l in _waiting(found, closings(project))]


def template_owned(name):
    blank = re.fullmatch(r"docs/blanks/([^/]+)", name)
    return (name == "template" or name in TEMPLATE_FILES or bool(blank and blank.group(1) in TEMPLATE_BLANKS)
            or any(name.startswith(folder) for folder in TEMPLATE_FOLDERS))


def marks(project, all_lessons):
    """Each kept line ending ' [new L<nnn> <date>]' in the files the lessons name: {n, date, file, line, undo}."""
    found = []
    for name in sorted({l["file"] for l in all_lessons if l["file"] not in ("template", "unknown")}):
        path = Path(project) / name
        if not path.is_file():
            continue
        for line in _read(path).splitlines():
            m = MARK.search(line)
            if m:
                n = f"L{int(m.group(1)):03d}"
                found.append({"n": n, "date": m.group(2), "file": name, "line": line.strip(),
                              "undo": _undo(project, n, name)})
    return found


def _undo(project, n, name):
    """git revert of the commit that wrote the mark (contract 3), found by git log -S."""
    try:
        done = subprocess.run(["git", "-C", str(project), "log", "--reverse", "--format=%h", f"-S[new {n} ", "--", name],
                              capture_output=True, text=True, timeout=30)
        shas = done.stdout.split() if done.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        shas = []
    return f"git revert {shas[0]}" if shas else f'git revert <the commit that wrote the mark> (git log -S"[new {n} ")'


def _chains(all_lessons):
    """L-number (int) -> the L-numbers (ints) chained to it by same:, either way, itself included."""
    group = {l["_int"]: {l["_int"]} for l in all_lessons}
    for l in all_lessons:
        if l["same"]:
            other = int(l["same"][1:])
            joined = group[l["_int"]] | group.setdefault(other, {other})
            for n in joined:
                group[n] = joined
    return group


# ---- rules nobody named (design Part 5) ----

def _words(text):
    """Text as plain lower-case words, for comparing a rule's bold words with a quoted line."""
    return " ".join(re.sub(r"[^\w]+", " ", text.lower()).split())


def _rule_spans(lines):
    """{n: (first, end, bold)} for each numbered rule '<n>. **...**' in these lines: its numbered line and
    the indented lines under it (its Why: lines). Lines under '## Refusals' are stops, not rules; the first
    rule of a number wins."""
    found, refusals = {}, False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            refusals = line.strip() == "## Refusals"
            continue
        m = RULE.match(line)
        if not m or refusals or int(m.group(1)) in found:
            continue
        end = j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j][:1] in " \t"):
            if lines[j].strip():
                end = j + 1
            j += 1
        found[int(m.group(1))] = (i, end, m.group(2))
    return found


def rules(project):
    """Each rule of RULE_FILES in the project: {file, rule, bold, line}."""
    found = []
    for name in RULE_FILES:
        path = Path(project) / name
        if not path.is_file():
            continue
        lines = _read(path).splitlines()
        for n, (first, _end, bold) in sorted(_rule_spans(lines).items()):
            found.append({"file": name, "rule": n, "bold": bold, "line": lines[first].strip()})
    return found


def _mentions(text):
    """(file, n) for each '<file> rule <n>' in the text; a bare 'rule <n>' is tracks.md's."""
    return {(os.path.basename(m.group(1)) if m.group(1) else "tracks.md", int(m.group(2)))
            for m in NAMED.finditer(text)}


def _docs_text_since(project, since):
    """The lines added since that time to any docs/ file (receipts too), read from git; with no git
    history, every docs/ file whole, so a rule is never listed for want of a reading."""
    try:
        done = subprocess.run(["git", "-C", str(project), "log", f"--since={since:%Y-%m-%d %H:%M}", "--format=",
                               "-p", "--no-color", "--unified=0", "--", ":(glob)**/docs/**"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        if done.returncode == 0:
            return "\n".join(l[1:] for l in done.stdout.splitlines() if l.startswith("+") and not l.startswith("+++"))
    except (OSError, subprocess.SubprocessError):
        pass
    return "\n".join(_read(p) for p in sorted(Path(project).glob("**/docs/**/*")) if p.is_file() and ".git" not in p.parts)


def _counted_since(project, since):
    """(file, n) for each counter line (contract 1) since that time whose check holds a numbered rule."""
    if not os.path.isfile(ACT_CHECK):
        return set()
    spec = importlib.util.spec_from_file_location("act_check_for_upgrade", ACT_CHECK)
    act_check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(act_check)
    try:
        name, _ = act_check.read_project(str(project))
        with open(act_check.counter_path(name), encoding="utf-8", errors="replace") as f:
            text = f.read()
    except (OSError, ValueError):
        return set()
    named = set()
    for line in text.splitlines():
        m = COUNTED.match(line)
        if not m or m.group(2) not in act_check.MESSAGES:
            continue
        if datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") >= since:
            named |= _mentions(act_check.MESSAGES[m.group(2)][1])
    return named


def _applied_since(project, since):
    """(worker-rules.md, n) for each rule a receipt part written since that time applies, read from git."""
    try:
        done = subprocess.run(["git", "-C", str(project), "log", f"--since={since:%Y-%m-%d %H:%M}", "--format=",
                               "-p", "--no-color", "--unified=0", "--", *RECEIPTS],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return set()
    if done.returncode != 0:
        return set()
    applied, checker = set(), False
    for line in done.stdout.splitlines():
        if line.startswith("diff --git "):
            checker = False
        if not line.startswith("+") or line.startswith("+++"):
            continue
        text = line[1:].rstrip()
        if text.startswith("## "):
            checker = text.startswith("## Checker run")
            if text == "## Parked":
                applied.update(PARKED_APPLIES)
        elif checker and text.startswith("Scope:"):
            applied.update(SCOPE_APPLIES)
        elif checker and text.startswith("Verdict:"):
            applied.update(VERDICT_APPLIES)
    return {("worker-rules.md", n) for n in applied}


def _held_before(project, name, bold, since):
    """Git first holds these bold words in that file before that time. No readable history counts as young."""
    try:
        done = subprocess.run(["git", "-C", str(project), "log", "--reverse", "--format=%ct", f"-S{bold}", "--", name],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    stamps = done.stdout.split() if done.returncode == 0 else []
    return bool(stamps) and datetime.datetime.fromtimestamp(int(stamps[0])) < since


def unnamed_rules(project, all_lessons, entries):
    """The rules older than the RETIRE_UNNAMED_JOBS-th last close that nobody named or applied since: [] with fewer closes."""
    if len(entries) < RETIRE_UNNAMED_JOBS:
        return []
    since = entries[-RETIRE_UNNAMED_JOBS]["_key"][0]
    named = _mentions(_docs_text_since(project, since)) | _counted_since(project, since) | _applied_since(project, since)
    left = []
    for r in rules(project):
        if (r["file"], r["rule"]) in named:
            continue
        bold = _words(r["bold"])
        if any(l["file"] == r["file"] and l["_when"] >= since and bold and bold in _words(l["line"])
               for l in all_lessons):
            continue
        if not _held_before(project, r["file"], r["bold"], since):
            continue
        left.append({"n": f"rule {r['rule']}", "rule": r["rule"], "file": r["file"], "line": r["line"],
                     "retire": f"python tools/upgrade.py --retire {r['file']} {r['rule']}",
                     "undo": f"python tools/upgrade.py --restore {r['file']} {r['rule']}"})
    return left


def groups(project, needs_thought=()):
    """The upgrade's list: the groups in order, each {key, title, count, items}."""
    all_lessons = lessons(project) or []
    entries = closings(project)
    left = _waiting(all_lessons, entries)
    answered = _answers(entries)
    held = set(needs_thought)
    the_foundations = status.foundations(project)

    thought, lines, tracks, template = [], [], [], []
    works, misfires = {}, {}
    for l in left:
        if l["_int"] in held:
            thought.append(l)
        elif l["file"] == "unknown":  # a backlog lesson from the adopt: one line of approve all, whatever its kind
            lines.append(l)
        elif l["kind"] == "change":
            (template if template_owned(l["file"]) else lines).append(l)
        elif l["kind"] == "track":
            tracks.append(l)
        elif l["kind"] == "works":
            works.setdefault(l["file"], []).append(l)
        elif l["kind"] == "misfire":
            misfires.setdefault(l["file"], []).append(l)
        else:
            lines.append(l)  # a kind record.py does not write: shown, never dropped

    suggested = []
    for name, new in works.items():
        earlier = [l for l in all_lessons if l["file"] == name and l["kind"] == "works"
                   and answered.get(l["_int"]) == "not now"]
        suggested.append({"file": name, "waiting": [_public(l) for l in new],
                          "earlier_not_now": [_public(l) for l in earlier]})

    trials = [{"file": name, "foundations": [f for f in the_foundations if f["file"] == name],
               "misfires": [_public(l) for l in found]} for name, found in misfires.items()]

    his = [l for l in left if l["sort"] == "his"]
    on_probation = marks(project, all_lessons)
    backed = {l["same"] for l in all_lessons if l["kind"] == "works" and l["same"]}
    close_dates = [e["time"][:10] for e in entries]
    retire = [m for m in on_probation if m["n"] not in backed
              and sum(1 for d in close_dates if d > m["date"]) >= RETIRE_AFTER_JOBS]
    retire += unnamed_rules(project, all_lessons, entries)
    chains = _chains(all_lessons)
    refuse = [dict(_public(l), sightings=[f"L{n:03d}" for n in sorted(chains[l["_int"]]) if n <= l["_int"]])
              for l in left if sum(1 for n in chains[l["_int"]] if n < l["_int"]) >= SIGHTINGS - 1]

    def group(key, title, items):
        return {"key": key, "title": title, "count": len(items), "items": items}

    his_group = group("his", "0a. his lessons (five at most shown)", [_public(l) for l in his[:HIS_SHOWN]])
    his_group.update(count=len(his), rest=max(0, len(his) - HIS_SHOWN))
    return [
        group("needs_thought", "0. needs thought", [_public(l) for l in thought]),
        his_group,
        group("lines", "1. lines to keep, change or drop — approve all", [_public(l) for l in lines]),
        group("foundations", "2. suggested foundations", suggested),
        group("tracks", "2a. candidate tracks", [_public(l) for l in tracks]),
        group("trials", "3. foundations to reopen as trials", trials),
        group("foundation", "foundations", the_foundations),
        group("template", "4. for the template", [_public(l) for l in template]),
        group("new", "5. on probation (new)", on_probation),
        group("retire", "6. retire", retire),
        group("refuse", "7. refuse, narrow or strike", refuse),
    ]


# ---- the check ----

def _found(cell, text):
    """The kept line is in the text word for word: as written, or with its outer quotes or backticks set aside."""
    candidate = cell
    while True:
        if candidate and candidate in text:
            return True
        if len(candidate) >= 2 and candidate[0] == candidate[-1] and candidate[0] in "`\"":
            candidate = candidate[1:-1]
            continue
        return False


def _upgrades_lines(text):
    """The lines under a '## Upgrades' heading, or None when the file has none."""
    under, inside = None, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Upgrades"
            if inside and under is None:
                under = []
            continue
        if inside:
            under.append(line)
    return under


def first_time_fault(project, title):
    """The first-time close: None, or the fault when a first-time run closes with no workflow file written."""
    m = RUN_CLOSED.match(title or "")
    if not m:
        return None
    run = Path(project) / "docs" / "runs" / m.group(1)
    plan = run / "plan-signed.md"
    kind = FIRST_TIME.search(_read(plan)) if plan.is_file() else None
    if not kind:
        return None
    record = run / "run.md"
    start = GO_START.search(_read(record)) if record.is_file() else None
    if start:
        for flow in status.workflows(project):
            tags = {step["tag"]["tag"] for step in flow["steps"]}
            dated = [DATED.match(line.strip()) for line in _upgrades_lines(flow["text"]) or []]
            if tags <= {"idea", "on trial"} and any(d and d.group(1) >= start.group(1) for d in dated):
                return None
    return f"a first-time run closes with its workflow file written ({kind.group(1)})"


def _go_of(project, n):
    """Run n's Go, 'yyyy-mm-dd hh:mm', as measures.py's start_of reads docs/runs/<n>/run.md; None when it cannot."""
    record = Path(project) / "docs" / "runs" / str(n) / "run.md"
    if not record.is_file() or not os.path.isfile(MEASURES):
        return None
    try:
        spec = importlib.util.spec_from_file_location("measures_for_upgrade", MEASURES)
        measures = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(measures)
        go = measures.start_of(str(record), measures.sections(_read(record)).get("Go", []))
        return go if go and _time(go) else None
    except Exception:  # a Go that cannot be read refuses the close; it never stops the check
        return None


def harvest_fault(project, title, closed, harvest=HARVEST):
    """The house's catch at one close: None, or the fault while lessons from the other projects that waited
    before its run's Go are not carried. Nothing is checked with no harvest.py, for a Review closed, or for a
    run whose Go (or close, which comes after it) is before CATCH_BEGAN."""
    m = RUN_CLOSED.match(title or "")
    if not m or not harvest or not os.path.isfile(harvest):
        return None
    n, began = m.group(1), _time(CATCH_BEGAN)
    if closed < began:
        return None
    go = _go_of(project, n)
    if go is None:
        return f"run {n}'s close: its Go could not be read from docs/runs/{n}/run.md"
    if _time(go) < began:
        return None
    name = os.path.basename(str(harvest))
    try:
        done = subprocess.run([sys.executable, str(harvest), "--waiting-before", go], cwd=str(project),
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=HARVEST_TIMEOUT)
    except subprocess.TimeoutExpired:
        why = f"no answer in {HARVEST_TIMEOUT} seconds"
    except (OSError, subprocess.SubprocessError) as e:
        why = str(e)
    else:
        first = (done.stdout.splitlines() or [""])[0].strip()
        said = WAITING_BEFORE.fullmatch(first)
        if done.returncode != 0:
            why = f"{name} exited {done.returncode}"
        elif not said or said.group(1) != go:
            why = f"{name} said \"{first}\""
        elif not int(said.group(2)):
            return None
        else:
            return (f"run {n}'s close: {int(said.group(2))} lessons from the other projects waited before its Go "
                    f"and are not carried: run python tools/harvest.py")
    return f"run {n}'s close: the harvest was not read ({why})"


def checks(project, harvest=HARVEST):
    """[(passed, faults, title)] for each closing entry since the last passing one, oldest first:
    the newest always, and each earlier one back to the first that passes. [] with no lessons file or no close.
    Each close's faults include the house's catch (harvest_fault)."""
    project = Path(project)
    entries = closings(project)
    all_lessons = lessons(project)
    if all_lessons is None or not entries:
        return []
    results = []
    for at in reversed(range(len(entries))):
        sitting = [e for e in entries if e is not entries[at] and e["_key"][0] == entries[at]["_key"][0]]
        passed, faults, title = _check_close(project, all_lessons, entries[at], entries[:at], sitting)
        caught = harvest_fault(project, title, entries[at]["_key"][0], harvest)
        if caught:
            passed, faults = False, faults + [caught]
        if passed and at < len(entries) - 1:
            break
        results.append((passed, faults, title))
    return results[::-1]


def check(project, harvest=HARVEST):
    """(passed, faults, title) over every close checks() reads, title the newest's. title is None with no closing entry."""
    entries = closings(project)
    title = entries[-1]["title"] if entries else None
    faults = [fault for _, found, _ in checks(project, harvest) for fault in found]
    return not faults, faults, title


def _check_close(project, all_lessons, newest, earlier, sitting=()):
    """(passed, faults, title) for one closing entry's block, the entries before it read as earlier;
    a row in another close of its sitting (the same minute) answers a lesson too."""
    title = newest["title"]
    if newest["rows"] is None:
        return False, [f"{title} has no ### The upgrade block"], title

    faults = list(newest["faults"])
    close_time = newest["_key"][0]
    listed = [l for l in _waiting(all_lessons, earlier) if l["_when"] <= close_time]
    rowed = {n for entry in (newest, *sitting) for row in entry["rows"] or [] for n in row["numbers"]}
    for l in listed:
        if l["_int"] not in rowed:
            faults.append(f"{l['n']} has no row in {title}")

    for row in newest["rows"]:
        label, answer, where = row["label"], row["answer"], row["where"]
        if answer not in ANSWERS:
            faults.append(f"{label}: \"{answer}\" is not one of {', '.join(ANSWERS)}")
            continue
        if where == "template" or answer in ("drop", "not now"):
            continue
        path = project / where
        text = _read(path) if where and path.is_file() else None
        if answer in ("keep", "change"):
            if text is None:
                faults.append(f"{label}: {where or 'no file'} is not a file of the project")
                continue
            if not row["line"]:
                faults.append(f"{label}: no line as kept for {where}")
            elif not _found(row["line"], text):
                faults.append(f"{label}: the line as kept is not in {where}")
        elif answer == "foundation":
            flow = status.read_workflow(path, where, strict=False) if text is not None else None
            if not flow or not status.foundations(project, [flow]):
                faults.append(f"{label}: foundation of {where}, and no step or Tag: line there is tagged foundation")
        # Any row on a workflow file (one with ## Upgrades) needs its dated line there (design Part 8).
        upgrades = _upgrades_lines(text) if text is not None else None
        if upgrades is not None:
            for n in row["numbers"]:
                if not any(int(m) == n for line in upgrades for m in L_NUMBER.findall(line)):
                    faults.append(f"L{n:03d}: {where} has ## Upgrades and no line under it naming L{n:03d}")
    first_time = first_time_fault(project, title)
    if first_time:
        faults.append(first_time)
    return not faults, faults, title


# ---- retiring a rule, and putting it back (contract 6) ----

def _lines_of(path):
    """(lines, newline, whether it ends with one) of a text file, so a write keeps its line endings."""
    text = path.read_bytes().decode("utf-8")
    return text.splitlines(), ("\r\n" if "\r\n" in text else "\n"), text.endswith(("\n", "\r"))


def _write_lines(path, lines, newline, end):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((newline.join(lines) + (newline if end else "")).encode("utf-8"))


def _retired(project):
    """(path, lines, newline, opened) of docs/retired.md; opened from docs/blanks/retired.md when there is none."""
    path = Path(project) / "docs" / "retired.md"
    if path.is_file():
        lines, newline, _ = _lines_of(path)
        return path, lines, newline, False
    for blank in (Path(project) / "docs" / "blanks" / "retired.md",
                  Path(__file__).resolve().parent.parent / "docs" / "blanks" / "retired.md"):
        if blank.is_file():
            lines, newline, _ = _lines_of(blank)
            while lines and not lines[-1].strip():
                lines.pop()
            return path, lines + [""], newline, True
    raise ValueError("there is no docs/retired.md, and no docs/blanks/retired.md to open it from")


def retire(project, name, n, today=None):
    """Move rule n of the file (its numbered line and its Why: lines) to docs/retired.md, leaving its stub.
    Returns what it wrote, as lines to print; raises ValueError when it cannot."""
    today = today or datetime.date.today().isoformat()
    name = _clean(name)
    path = Path(project) / name
    if not path.is_file():
        raise ValueError(f"{name} is not a file of the project")
    lines, newline, end = _lines_of(path)
    span = _rule_spans(lines).get(n)
    if span is None:
        raise ValueError(f"{name} has no rule {n} (a line \"{n}. **...**\")")
    first, last, _bold = span
    block = lines[first:last]
    stub = STUB.format(n=n, date=today)
    entry = [f"- {today} · {name} · \"{block[0]}\" · why: nobody named it in the last {RETIRE_UNNAMED_JOBS} "
             f"closed jobs (upgrade.py's retire list) · undo: python tools/upgrade.py --restore {name} {n}"]
    entry += [KEPT + line if line else KEPT.rstrip() for line in block[1:]]
    retired, kept, r_newline, opened = _retired(project)
    _write_lines(retired, kept + entry, r_newline, True)  # the record first, so the rule is never lost
    lines[first:last] = [stub]
    _write_lines(path, lines, newline, end)
    return ([f"RETIRED: {name} rule {n} ({len(block)} lines) moved to docs/retired.md; nothing committed",
             f"{name}: {stub}",
             "docs/retired.md" + (" (opened from docs/blanks/retired.md)" if opened else "") + ":"] + entry)


def restore(project, name, n, today=None):
    """Put rule n back in place of its stub, word for word, and note it under its entry in docs/retired.md.
    Returns what it wrote, as lines to print; raises ValueError when it cannot."""
    today = today or datetime.date.today().isoformat()
    name = _clean(name)
    path = Path(project) / name
    if not path.is_file():
        raise ValueError(f"{name} is not a file of the project")
    lines, newline, end = _lines_of(path)
    at = next((i for i, l in enumerate(lines) if STUB_LINE.match(l) and int(STUB_LINE.match(l).group(1)) == n), None)
    if at is None:
        raise ValueError(f"{name} has no line \"{n}. Retired <yyyy-mm-dd>: docs/retired.md.\"")
    retired = Path(project) / "docs" / "retired.md"
    if not retired.is_file():
        raise ValueError("there is no docs/retired.md")
    r_lines, r_newline, r_end = _lines_of(retired)
    head = f" · {name} · \"{n}. "
    for i in reversed([i for i, l in enumerate(r_lines) if l.startswith("- ") and head in l]):
        j, block, restored = i + 1, [], False
        while j < len(r_lines) and r_lines[j].startswith("  "):
            if r_lines[j].startswith(KEPT.rstrip()):
                block.append(r_lines[j][len(KEPT):])
            elif r_lines[j].startswith("  Restored "):
                restored = True
            j += 1
        if not restored:
            break
    else:
        raise ValueError(f"docs/retired.md has no entry for {name} rule {n} that is not restored already")
    entry = r_lines[i]
    numbered = entry[entry.index(head) + len(head) - len(f"{n}. "):entry.rfind("\" · why: ")]
    note = f"  Restored {today}: back in {name} as rule {n}."
    lines[at:at + 1] = [numbered] + block
    _write_lines(path, lines, newline, end)
    r_lines.insert(j, note)
    _write_lines(retired, r_lines, r_newline, r_end)
    return [f"RESTORED: {name} rule {n} ({1 + len(block)} lines) put back; nothing committed",
            f"{name}:"] + [numbered] + block + ["docs/retired.md, under its entry:", note]


# ---- printing ----

def _lesson_text(l):
    return f"{l['n']} · {l['kind']} · file: {l['file']} · \"{l['line']}\" — {l['what']}"


def _seen(l):
    return f"{l['n']} (seen: {l['seen']})" if l.get("seen") else l["n"]


def show(found):
    out = []
    for g in found:
        indent = "     " if g["key"] == "foundation" else ""
        out.append(f"{indent}{g['title']} ({g['count']})")
        if not g["items"]:
            out.append(f"{indent}   none")
        for item in g["items"]:
            if g["key"] == "foundations":
                text = f"{item['file']} — works: {', '.join(_seen(l) for l in item['waiting'])}"
                if item["earlier_not_now"]:
                    text += f" · earlier, answered not now: {', '.join(_seen(l) for l in item['earlier_not_now'])}"
            elif g["key"] == "tracks":
                text = _lesson_text(item) + " · keep as a candidate, put on trial, or drop"
            elif g["key"] == "trials":
                held = "; ".join(status.foundation_text(f) for f in item["foundations"]) or "no foundation there"
                text = f"{item['file']} ({held}) — misfire: {', '.join(_seen(l) for l in item['misfires'])}"
            elif g["key"] == "foundation":
                text = status.foundation_text(item)
            elif g["key"] == "retire" and "rule" in item:
                text = f"{item['file']} {item['n']} · \"{item['line']}\" · retire: {item['retire']} · undo: {item['undo']}"
            elif g["key"] in ("new", "retire"):
                text = f"{item['n']} · {item['file']} · \"{item['line']}\" · undo: {item['undo']}"
            elif g["key"] == "refuse":
                text = _lesson_text(item) + f" · sightings: {', '.join(item['sightings'])}"
            else:
                text = _lesson_text(item)
            out.append(f"{indent}   {text}")
        if g.get("rest"):
            out.append(f"{indent}   and {g['rest']} more his lessons waiting")
        out.append("")
    return "\n".join(out).rstrip("\n")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # the dots and dashes print in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="The upgrade's list, from the files, and the check of its close.")
    parser.add_argument("--project", default=".", help="the project folder (default: here)")
    parser.add_argument("--check", action="store_true",
                        help="check the ### The upgrade block of each closing entry since the last passing one")
    parser.add_argument("--needs-thought", default="", help="L-numbers for the needs-thought group, e.g. L012,L019")
    parser.add_argument("--json", action="store_true", help="print the groups as JSON")
    parser.add_argument("--retire", nargs=2, metavar=("FILE", "N"), help="move rule N of FILE to docs/retired.md")
    parser.add_argument("--restore", nargs=2, metavar=("FILE", "N"), help="put rule N of FILE back from docs/retired.md")
    parser.add_argument("--harvest", default=HARVEST,
                        help="the harvest.py --check runs at each close (default: one beside this file, if any)")
    args = parser.parse_args(argv)
    project = Path(args.project)

    if args.retire or args.restore:
        (name, n), act = (args.retire, retire) if args.retire else (args.restore, restore)
        try:
            print("\n".join(act(project, name, int(n))))
        except ValueError as why:
            print(f"REFUSE: {why}")
            return 1
        return 0

    if lessons(project) is None:
        print("not gated: no docs/lessons.md")
        return 0

    if args.check:
        results = checks(project, args.harvest)
        if not results:
            print("nothing to check: no closing entry in docs/decisions.md")
            return 0
        for passed, faults, title in results:
            if passed:
                print(f"UPGRADE DONE: {title}")
            for fault in faults:
                print(f"REFUSE: {fault}")
        return 0 if all(passed for passed, _, _ in results) else 1

    held = [int(n) for n in L_NUMBER.findall(args.needs_thought)]
    waiting_now = {int(l["n"][1:]) for l in waiting(project)}
    unknown = [n for n in held if n not in waiting_now]
    if unknown:
        for n in unknown:
            print(f"REFUSE: --needs-thought L{n:03d} is not a waiting lesson")
        return 1
    found = groups(project, held)
    if args.json:
        print(json.dumps({"waiting": len(waiting_now), "groups": found}, ensure_ascii=False, indent=2))
    else:
        print(f"the upgrade: {len(waiting_now)} lessons waiting")
        print()
        print(show(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
