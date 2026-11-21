# record.py: write one line or one heading into a record, stamped from the clock.
#
# What it is for
#   The run record (docs/runs/<n>/run.md) is what the next master, the
#   checker and the review read, and every line in it carries this
#   computer's clock. So do the headings of docs/decisions.md and a desk's
#   docs/asks.md, and the lines of a log, and the lessons of
#   docs/lessons.md. This tool writes one of them, the time read from the
#   clock in the same step that writes it. Six ways:
#
#   --section "<heading>" "<text>"
#       appends one line,
#           - <hh:mm> · <text>
#       as the last line under the heading you name, in the newest run's
#       run.md (the highest <n>), or in the file you name with --file.
#       A heading that is not in the file is refused, never made: a new
#       section would be a record nobody planned to read. Under "It works"
#       a text of fewer than four parts is refused: the form is
#       <card> · pass | fail · <who looked> · <how>, because It works lines
#       were typed from memory, not from a look (design 0.9.0, Part 7).
#       Under "Shutdown list" a text with no status ends " · open": shutdown.py
#       cannot see a line without one (L031).
#
#   --week go | --week close
#       writes under "## Go" of the newest run's run.md
#           - <hh:mm> · Week read at Go: <n>%
#           - <hh:mm> · Week read at the close: <n>%
#       <n> is the seven_day percent in the state window.py leaves, never typed,
#       because scoreboard.py works its usage column from these two lines. A
#       reading older than 10 minutes, or none, is refused; so is a second line
#       of the same kind.
#
#   --handover --next "<…>" [--running, --merges, --window, --ids "<…>"]
#       appends under "## Handover" of the run record, as --section does,
#           - <hh:mm> · running: … · merges: … · next: … · window: … · ids: …
#       (the fields given, in that order). It has no field for orders or
#       rules and takes no line of its own: a handover that restated a rule
#       moved workers into the master's thread (design 0.9.0, Part 1).
#
#   A write aimed at a docs/runs/<n>/run.md that is not there yet (the
#   newest run folder's, or one named with --file) first copies
#   docs/blanks/run.md there, <n> and foundry-north-website filled in (project.yaml's
#   name:), its first note line dropped; never over a file that is there.
#   Why: a run with no record of its own was met in engine-motion-graphics'
#   runs 4 and 5 (design 0.9.0, Part 1).
#
#   --file <file> --entry "<title>"
#       writes a new heading at the file's end, one blank line before it:
#           ## <yyyy-mm-dd hh:mm> — <title>     in a decisions file or a log
#           ## <yyyy-mm-dd hh:mm> · <title>     in a file named asks.md
#       (the forms of docs/blanks/decisions-entry.md and asks-entry.md). The
#       entry's body is written after it by the edit tools. It is refused in
#       a run record: a file named run.md, and whenever no --file is named.
#
#   --file <file> --last "<text>"
#       appends one line as the last line of the file's last "## " section:
#           - <hh:mm> · <text>
#       or, with --who "<who>", the form of a reply under an asks entry:
#           - **<hh:mm> — <who>:** <text>
#       It is refused with no --file.
#
#   --lesson "<what happened>" --from "<from>" --kind <kind>
#            --about <file> --line "<the exact line>" [--seen "<seen>"]
#            [--sort routine|his|template] [--limits made] [--same L<nnn>]
#       appends one lesson as the last line of docs/lessons.md (or of the
#       file you name with --file), numbered one past the highest L there:
#           - L<nnn> · <yyyy-mm-dd hh:mm> · <from> · <kind> · <what happened> · file: <file> · "<the exact line>" · sort: <sort>[ · limits: made][ · same: L<nnn>] · seen: <seen>
#       (" · seen: <seen>" only when given). sort: is always written: given,
#       or template for the word template or a template-owned file
#       (upgrade.py's list), else his. Refused as routine: --limits made, and
#       an --about workflow file holding a step or Tag: line tagged
#       foundation (the whole file goes to him). --same names an earlier
#       lesson in the file, refused when it is not there. Why: lessons
#       waited weeks for a review, and a "no person" rule nobody had ruled
#       was copied forward (design 0.9.0, Part 4; his rulings 2 and 5).
#       <from> is run <n>, planning,
#       exploration, research, job <name> or session; <kind> is change,
#       works, misfire or track; --about is the file: the lesson lands in,
#       or the word template. Refused: a file: under docs/research/, a log
#       or a findings file, or one that is not a file of the project (read
#       two folders up from the lessons file), a path resolving outside it
#       included, since no master there reads it; file: unknown (only the
#       adopt's backlog writes it); a works or misfire with no --seen (it
#       is the evidence for a lock); " · " inside a part, or " · seen: "
#       inside the line; a newline anywhere. The number is read and the
#       line written while holding <file>.lock, so two writers at once never
#       share a number; a lock held 10 seconds is a refusal, and one older
#       than 60 seconds is taken as stale.
#
#   A file that does not exist is refused, never made. So is a text, or an
#   --entry title, that starts with a clock time (h:mm or hh:mm, a date
#   before it or not, after any leading spaces, *, - or _): the tool stamps
#   the time, never type one. In engine-motion-graphics' run 3 the master
#   typed times on top of the stamp (03:39 and 03:40 for 03:33 and 03:34),
#   so lines carried two times and one was wrong; four corrections. A time
#   later in the text (merged at 10:40) is recorded. It prints RECORDED:
#   and the line, and exits 0, or REFUSE: and why, and exits 1, the file
#   left as it was. It keeps the file's own line endings, writes that one
#   file and nothing else (with --lesson, its lock file too, removed
#   after), and never commits.
#
# Why the rule exists
#   In run 2 most of the master's actions were clerk work, and the clock
#   was one of them: a model can misread the time or forget to look, and a
#   script cannot. Deterministic work sits on the lowest rung that does it
#   properly, a script (design § 4, the cost ladder). In the job scout's
#   planning six times were typed, not read (two decisions headings, four
#   log lines), and two more by guess into a card and an asks entry: a
#   planning master has no run record, so the tool reaches those files too.
#   --lesson: lessons went into findings files, handovers or nowhere, and
#   a file nobody is made to read is never read (the upgrade design of
#   12 Nov, § 2, causes 3 and 4). So every lesson, from any work, goes to
#   one file in one numbered form ("one place where everything leaves
#   logs", his ruling of 12 Nov), naming a file: the next master is made
#   to read, and the upgrade at every review reads it from there.
#
# How to run it (from the project's top folder)
#   python template/tools/record.py --section "Merges" "<text>"
#   python template/tools/record.py --section "Orders" "<text>" --file docs/runs/3/run.md
#   python template/tools/record.py --week go
#   python template/tools/record.py --handover --running "<…>" --merges "<…>" --next "<…>" --window "<…>" --ids "<…>"
#   python template/tools/record.py --file docs/decisions.md --entry "<title>"
#   python template/tools/record.py --file desks/<desk>/docs/asks.md --last --who "PLAN (<desk>)" "<text>"
#   python template/tools/record.py --lesson "<what happened>" --from "run 4" --kind works --about docs/blanks/card.md --line "<the exact line>" --seen "<his verdict, a number or a pass line>"
#   After the adopt, the same from tools/record.py.
#
# Python 3 standard library only. No network.

import argparse
import datetime
import json
import os
import re
import sys
import time

RUNS = "docs/runs"
HANDOVER = ("running", "merges", "next", "window", "ids")  # no field for orders or rules
WEEK = {"go": "Week read at Go", "close": "Week read at the close"}
WEEK_FRESH = 10 * 60  # seconds a reading of the week counts for
READ_FIRST = "read the window first: python tools/window.py"
STATUS = re.compile(r"open|closed \d{2}:\d{2}(?: \([^()]+\))?")  # the whole of a line's last part


class Refuse(Exception):
    pass


def newest_run():
    """The run.md of the highest-numbered run folder under docs/runs/, from
    here, whether or not it is there yet (open_run makes it from the blank)."""
    numbers = []
    if os.path.isdir(RUNS):
        for name in os.listdir(RUNS):
            if name.isdigit() and os.path.isdir(f"{RUNS}/{name}"):
                numbers.append(int(name))
    if not numbers:
        raise Refuse(f"there is no run folder at {RUNS}/<n>/ here")
    return f"{RUNS}/{max(numbers)}/run.md"


RUN_RECORD = re.compile(r"(?:^|/)docs/runs/(\d+)/run\.md$")


def open_run(path):
    """A run's record that is not there yet is copied from docs/blanks/run.md,
    <n> and foundry-north-website filled in, its first note line dropped. True when it
    opened one; never over a file that is there."""
    where = os.path.abspath(path).replace("\\", "/")
    match = RUN_RECORD.search(where)
    if not match or os.path.exists(path):
        return False
    if not os.path.isdir(os.path.dirname(os.path.abspath(path))):
        raise Refuse(f"there is no run folder for {path}; a run is never invented")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(where))))
    blank = os.path.join(root, "docs", "blanks", "run.md")
    try:
        with open(blank, "rb") as f:
            text = f.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        raise Refuse(f"{path} is not there and the blank {blank} could not be read")
    project = os.path.basename(root)
    card = os.path.join(root, "project.yaml")
    if os.path.isfile(card):
        with open(card, encoding="utf-8", errors="replace") as f:
            project = next((line[5:].strip() for line in f if line.startswith("name:") and line[5:].strip()), project)
    lines = text.splitlines(keepends=True)[1:]  # the note to whoever copies it
    while lines and not lines[0].strip():
        lines.pop(0)
    text = "".join(lines).replace("<n>", match.group(1)).replace("foundry-north-website", project)
    with open(path, "xb") as f:
        f.write(text.encode("utf-8"))
    return True


TYPED = re.compile(r"[\s*_-]*((?:\d{4}-\d\d-\d\d[ T])?\d{1,2}:\d\d)(?!\d)")


def typed_time(text):
    """A text that starts with a clock time is refused: the tool stamps the time."""
    match = TYPED.match(text)
    if match:
        raise Refuse(f'"{match.group(1)}" is typed at the start of the text; the tool stamps the time; never type one')


def named(path, name):
    return os.path.basename(path).lower() == name


def load(path):
    """The file's text. A file that is not there is refused, never made."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        raise Refuse(f"the file {path} could not be read")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse(f"the file {path} is not saved as UTF-8 text")


def save(path, content, lines, ended):
    # Keep the file's own line endings.
    newline = "\r\n" if "\r\n" in content else "\n"
    out = newline.join(lines)
    if ended:
        out += newline
    with open(path, "wb") as f:
        f.write(out.encode("utf-8"))


def append(path, heading, text, who=None):
    """Append a stamped line as the last line under '## <heading>', or, with
    no heading, under the file's last '## ' section. The heading and the line."""
    content = load(path)
    lines = content.splitlines()
    if heading is None:
        start = next((i for i in reversed(range(len(lines))) if re.match(r"^##\s", lines[i])), None)
        if start is None:
            raise Refuse(f'the file {path} has no "## " section to write under')
    else:
        wanted = heading.strip()
        start = next((i for i, line in enumerate(lines)
                      if re.match(r"^##\s", line) and line[2:].strip() == wanted), None)
        if start is None:
            raise Refuse(f'the file {path} has no "## {wanted}" section')
    end = start + 1
    while end < len(lines) and not re.match(r"^#{1,2}\s", lines[end]):
        end += 1
    # The last line under the heading: after the section's last line that is not blank.
    last = end - 1
    while last > start and not lines[last].strip():
        last -= 1
    now = datetime.datetime.now().strftime("%H:%M")
    line = f"- {now} · {text}" if who is None else f"- **{now} — {who.strip()}:** {text}"
    under = lines[start].strip()
    lines.insert(last + 1, line)
    save(path, content, lines, content.endswith(("\n", "\r")))
    return under, line


def with_status(text):
    """A Shutdown list line, ending ' · open' when it has no status of its own."""
    parts = text.rsplit(" · ", 1)
    return text if len(parts) == 2 and STATUS.fullmatch(parts[1].strip()) else text.rstrip() + " · open"


def _window():
    """window.py beside this file: where its state lives stays its own rule."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "window_for_record", os.path.join(os.path.dirname(os.path.abspath(__file__)), "window.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def week_percent():
    """The seven_day percent in window.py's state, when that reading is under 10 minutes old."""
    try:
        with open(_window().default_state(), encoding="utf-8") as f:
            reading = json.load(f)
        read_at, percent = reading["read_at"], reading["seven_day"]["percent"]
    except (OSError, ValueError, KeyError, TypeError):
        raise Refuse(f"there is no reading of the week; {READ_FIRST}")
    if type(read_at) not in (int, float) or type(percent) is not int:
        raise Refuse(f"the reading of the week could not be read; {READ_FIRST}")
    if not 0 <= time.time() - read_at <= WEEK_FRESH:
        raise Refuse(f"the reading of the week is older than 10 minutes; {READ_FIRST}")
    return percent


def week_line(path, kind, percent):
    """Write the week's reading under '## Go', once of each kind. The heading and the line."""
    inside = False
    for line in load(path).splitlines():
        if re.match(r"^#{1,2}\s", line):
            inside = bool(re.match(r"^##\s", line)) and line[2:].strip() == "Go"
        elif inside and re.match(rf"- \d\d:\d\d · {WEEK[kind]}:", line):
            raise Refuse(f'{path} already has its "{WEEK[kind]}" line; the week is read once at each end')
    return append(path, "Go", f"{WEEK[kind]}: {percent}%")


def entry(path, title):
    """Write '## <yyyy-mm-dd hh:mm> — <title>' at the file's end, one blank line before it."""
    if path is None or named(path, "run.md"):
        raise Refuse("--entry is never written in a run record: a heading there is never invented. "
                     "Name a decisions file, a log or an asks.md with --file")
    content = load(path)
    lines = content.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        lines.append("")
    mark = "·" if named(path, "asks.md") else "—"
    heading = f"## {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} {mark} {title.strip()}"
    lines.append(heading)
    save(path, content, lines, True)
    return heading


LESSONS = "docs/lessons.md"
KINDS = ("change", "works", "misfire", "track")
FROM = re.compile(r"(run \d+|planning|exploration|research|job \S.*|session)")
NUMBER = re.compile(r"- L(\d+) · ")
LOCK_WAIT = 10   # seconds a writer waits for the lock before refusing
LOCK_STALE = 60  # seconds after which a lock is taken as left behind
SORTS = ("routine", "his", "template")
SAME = re.compile(r"L(\d+)")


def _upgrade():
    """upgrade.py beside this file (and status.py beside that): the template's file list and the tags."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "upgrade_for_record", os.path.join(os.path.dirname(os.path.abspath(__file__)), "upgrade.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sorted_as(path, about, sort, limits):
    """The lesson's sort: as given, or template for a template-owned file, else his.
    Never routine when it limits what may be made, or its file holds a foundation (ruling 5)."""
    up = _upgrade()
    if sort is None:
        return "template" if up.template_owned(about.replace("\\", "/")) else "his"
    if sort != "routine":
        return sort
    if limits:
        raise Refuse("a lesson that limits what may be made is his (ruling 5)")
    where = about.replace("\\", "/")
    if where.startswith("template/") or re.search(r"(^|/)docs/blanks/", where) or not where.endswith(".md"):
        return sort  # never a workflow file (contract 4)
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    flow = up.status.read_workflow(os.path.join(root, about), where)
    if flow and up.status.foundations(root, [flow]):
        raise Refuse(f"{about} holds a foundation; a better way runs as a trial beside it")
    return sort


def check_file(path, about):
    """The file: must be one the next master is made to read: a file of the
    project or the word template. Why: design cause 4."""
    if about == "unknown":
        raise Refuse("file: unknown is written only by the adopt's backlog; name the file the lesson lands in, or template")
    if about == "template":
        return
    where = about.replace("\\", "/")
    name = where.rsplit("/", 1)[-1].lower()
    nobody = "a lesson in a file nobody is made to read is never read"
    if re.search(r"(^|/)docs/research/", where):
        raise Refuse(f"file: {about} is under docs/research/; {nobody}")
    if name == "log.md" or name.endswith("-log.md") or re.search(r"(^|/)docs/log", where):
        raise Refuse(f"file: {about} is a log; {nobody}")
    if "findings" in name:
        raise Refuse(f"file: {about} is a findings file; {nobody}")
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    top = os.path.normcase(os.path.realpath(root))
    target = os.path.normcase(os.path.realpath(os.path.join(root, where)))
    try:
        outside = os.path.commonpath([top, target]) != top
    except ValueError:  # another drive
        outside = True
    if outside:
        raise Refuse(f"file: {about} resolves outside the project at {root}; {nobody}")
    if not os.path.isfile(os.path.join(root, about)):
        raise Refuse(f"file: {about} is not a file of the project at {root}, nor the word template")


def take_lock(lock):
    """Make <file>.lock, waiting for a writer that holds it; a lock older
    than LOCK_STALE seconds was left behind and is taken."""
    start = time.monotonic()
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            return
        except OSError:  # held (on Windows, also while it is being removed)
            pass
        try:
            if time.time() - os.path.getmtime(lock) > LOCK_STALE:
                os.remove(lock)
                continue
        except OSError:
            pass
        if time.monotonic() - start >= LOCK_WAIT:
            raise Refuse(f"the lock {lock} was held by another writer for {LOCK_WAIT} seconds; nothing written. "
                         f"With no writer running, it is taken as stale after {LOCK_STALE} seconds")
        time.sleep(0.1)


def lesson(path, what, source, kind, about, line, seen, sort=None, limits=None, same=None):
    """Append '- L<nnn> · <stamp> · <from> · <kind> · <what> · file: <about> · "<line>" · sort: <sort>
    [ · limits: made][ · same: L<nnn>][ · seen: <seen>]' as the file's last line, numbered one past its highest L."""
    missing = [flag for flag, value in (("--from", source), ("--kind", kind), ("--about", about), ("--line", line))
               if not value]
    if missing:
        raise Refuse(f"a lesson needs {', '.join(missing)}")
    parts = {"what": what, "--from": source, "--kind": kind, "--about": about, "--line": line, "--seen": seen or ""}
    for flag, value in parts.items():
        if "\n" in value or "\r" in value:
            raise Refuse(f"{flag} holds a newline; a lesson is one line")
    if not FROM.fullmatch(source):
        raise Refuse(f'--from "{source}" is none of: run <n>, planning, exploration, research, job <name>, session')
    if kind not in KINDS:
        raise Refuse(f"--kind {kind} is none of: {', '.join(KINDS)}")
    if kind in ("works", "misfire") and not seen:
        raise Refuse(f"a {kind} lesson needs --seen (his verdict quoted, a number, a pass line): "
                     "it is the evidence for a lock")
    for flag in ("what", "--from", "--about", "--seen"):
        if " · " in parts[flag]:
            raise Refuse(f'{flag} holds " · ", which breaks the reading of the line')
    if " · seen: " in line:
        raise Refuse('--line holds " · seen: ", which breaks the reading of the line')
    typed_time(what)
    if not os.path.isfile(path):
        raise Refuse(f"the file {path} does not exist; the adopt and the stamp make it, never this tool")
    check_file(path, about)
    if same is not None and not SAME.fullmatch(same):
        raise Refuse(f"--same {same} is not a lesson's number, L<nnn>")
    sort = sorted_as(path, about, sort, limits)
    lock = path + ".lock"
    take_lock(lock)
    try:
        content = load(path)
        lines = content.splitlines()
        numbers = [int(m.group(1)) for m in map(NUMBER.match, lines) if m]
        if same is not None and int(same[1:]) not in numbers:
            raise Refuse(f"--same {same}: no lesson L{int(same[1:]):03d} in {path}")
        number = max(numbers, default=0) + 1
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        written = f'- L{number:03d} · {stamp} · {source} · {kind} · {what} · file: {about} · "{line}" · sort: {sort}'
        if limits:
            written += " · limits: made"
        if same is not None:
            written += f" · same: L{int(same[1:]):03d}"
        if seen:
            written += f" · seen: {seen}"
        lines.append(written)
        save(path, content, lines, True)
    finally:
        os.remove(lock)
    return written


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):  # a title's "→" prints in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Write one clock-stamped line or heading into a record.")
    way = parser.add_mutually_exclusive_group(required=True)
    way.add_argument("--section", help="the heading to write a line under, without the ##")
    way.add_argument("--entry", metavar="TITLE",
                     help="a new heading to write at the end of --file, without the ## and the time")
    way.add_argument("--last", action="store_true", help="write a line under the last ## section of --file")
    way.add_argument("--lesson", metavar="WHAT", help="write one numbered lesson, what happened in one line, "
                                                       f"as the last line of --file (default {LESSONS})")
    way.add_argument("--handover", action="store_true", help="write the run record's Handover line from "
                                                             "--running, --merges, --next, --window and --ids")
    way.add_argument("--week", choices=tuple(WEEK), help="write the week's reading from window.py's state under "
                                                         "## Go of the newest run's record")
    for field in HANDOVER:
        parser.add_argument(f"--{field}", help=f"with --handover: {field}" + (" (needed)" if field == "next" else ""))
    parser.add_argument("--who", help="with --last: who the line is from, as in a reply under an asks entry")
    parser.add_argument("--from", dest="source", help="with --lesson: run <n>, planning, exploration, research, "
                                                      "job <name> or session")
    parser.add_argument("--kind", help="with --lesson: " + ", ".join(KINDS))
    parser.add_argument("--about", help="with --lesson: the file: the lesson lands in, or template")
    parser.add_argument("--line", help="with --lesson: the exact line")
    parser.add_argument("--seen", help="with --lesson: his verdict, a number or a pass line (needed for works and misfire)")
    parser.add_argument("--sort", choices=SORTS, help="with --lesson: routine, his or template "
                                                      "(default: template for a template-owned file, else his)")
    parser.add_argument("--limits", choices=("made",), help="with --lesson: made, when it limits what may be made")
    parser.add_argument("--same", help="with --lesson: the earlier lesson it repeats, L<nnn>")
    parser.add_argument("--file", help="the file to write in (--section's default: the newest docs/runs/<n>/run.md)")
    parser.add_argument("text", nargs="?", help="the line, without the time (none with --entry or --lesson)")
    args = parser.parse_args(argv[1:])
    if args.entry is not None and args.text is not None:
        parser.error("--entry takes the title alone: the entry's body is written after it by the edit tools")
    if args.lesson is not None:
        if args.text is not None:
            parser.error("--lesson takes what happened as its own value; the line goes in --line")
        path = args.file or LESSONS
        try:
            written = lesson(path, args.lesson, args.source, args.kind, args.about, args.line, args.seen,
                             args.sort, args.limits, args.same)
        except Refuse as why:
            print(f"REFUSE: {why}")
            return 1
        print(f"RECORDED: {path} · {written}")
        return 0
    if args.week is not None and (args.text is not None or args.file is not None):
        parser.error("--week takes no text and no --file: the number is window.py's, the record the newest run's")
    given = {field: getattr(args, field) for field in HANDOVER if getattr(args, field) is not None}
    if args.handover:
        if args.text is not None:
            parser.error("--handover takes no line of its own: it is built from --running, --merges, --next, "
                         "--window and --ids")
        if "next" not in given:
            parser.error("--handover needs --next")
    elif given:
        parser.error(f"--{next(iter(given))} goes with --handover")
    elif args.entry is None and args.week is None and args.text is None:
        parser.error("the line's text is missing")
    if args.who is not None and not args.last:
        parser.error("--who goes with --last")
    opened = None
    try:
        if args.entry is not None:
            typed_time(args.entry)
            path = args.file
            written = entry(path, args.entry)
        elif args.handover:
            for field, value in given.items():
                if "\n" in value or "\r" in value:
                    raise Refuse(f"--{field} holds a newline; the handover is one line")
            path = args.file or newest_run()
            opened = path if open_run(path) else None
            text = " · ".join(f"{field}: {value}" for field, value in given.items())
            written = f"## Handover · {append(path, 'Handover', text)[1]}"
        elif args.week is not None:
            percent = week_percent()
            path = newest_run()
            opened = path if open_run(path) else None
            written = f"## Go · {week_line(path, args.week, percent)[1]}"
        elif args.last:
            typed_time(args.text)
            if not args.file:
                raise Refuse("--last needs --file: in a run record, name the heading with --section")
            path = args.file
            opened = path if open_run(path) else None
            written = " · ".join(append(path, None, args.text, args.who))
        else:
            typed_time(args.text)
            if args.section.strip() == "It works" and len(args.text.split(" · ")) < 4:
                raise Refuse('an It works line is "<card> · pass | fail · <who looked> · <how>" (for anything '
                             'made to be watched, his watch or "frames only"); this one has '
                             f"{len(args.text.split(' · '))} parts")
            path = args.file or newest_run()
            opened = path if open_run(path) else None
            text = with_status(args.text) if args.section.strip() == "Shutdown list" else args.text
            written = f"## {args.section.strip()} · {append(path, args.section, text)[1]}"
    except Refuse as why:
        if opened:
            os.remove(opened)  # the file left as it was: not there
        print(f"REFUSE: {why}")
        return 1
    if opened:
        print(f"OPENED: {opened} from docs/blanks/run.md")
    print(f"RECORDED: {path} · {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
