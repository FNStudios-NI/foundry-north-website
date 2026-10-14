# record.py: write one line or one heading into a record, stamped from the clock.
#
# What it is for
#   The run record (docs/runs/<n>/run.md) is what the next master, the
#   checker and the review read, and every line in it carries this
#   computer's clock. So do the headings of docs/decisions.md and a desk's
#   docs/asks.md, and the lines of a log. This tool writes one of them, the
#   time read from the clock in the same step that writes it. Three ways:
#
#   --section "<heading>" "<text>"
#       appends one line,
#           - <hh:mm> · <text>
#       as the last line under the heading you name, in the newest run's
#       run.md (the highest <n>), or in the file you name with --file.
#       A heading that is not in the file is refused, never made: a new
#       section would be a record nobody planned to read.
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
#   A file that does not exist is refused, never made. It prints RECORDED:
#   and the line, and exits 0, or REFUSE: and why, and exits 1, the file
#   left as it was. It keeps the file's own line endings, writes that one
#   file and nothing else, and never commits.
#
# Why the rule exists
#   In run 2 most of the master's actions were clerk work, and the clock
#   was one of them: a model can misread the time or forget to look, and a
#   script cannot. Deterministic work sits on the lowest rung that does it
#   properly, a script (design § 4, the cost ladder). In the job scout's
#   planning six times were typed, not read (two decisions headings, four
#   log lines), and two more by guess into a card and an asks entry: a
#   planning master has no run record, so the tool reaches those files too.
#
# How to run it (from the project's top folder)
#   python template/tools/record.py --section "Merges" "<text>"
#   python template/tools/record.py --section "Orders" "<text>" --file docs/runs/3/run.md
#   python template/tools/record.py --file docs/decisions.md --entry "<title>"
#   python template/tools/record.py --file desks/<desk>/docs/asks.md --last --who "PLAN (<desk>)" "<text>"
#   After the adopt, the same from tools/record.py.
#
# Python 3 standard library only. No network.

import argparse
import datetime
import os
import re
import sys

RUNS = "docs/runs"


class Refuse(Exception):
    pass


def newest_run():
    """The run.md of the highest-numbered run under docs/runs/, from here."""
    numbers = []
    if os.path.isdir(RUNS):
        for name in os.listdir(RUNS):
            if name.isdigit() and os.path.isfile(f"{RUNS}/{name}/run.md"):
                numbers.append(int(name))
    if not numbers:
        raise Refuse(f"there is no run record at {RUNS}/<n>/run.md here")
    return f"{RUNS}/{max(numbers)}/run.md"


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


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):  # a title's "→" prints in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Write one clock-stamped line or heading into a record.")
    way = parser.add_mutually_exclusive_group(required=True)
    way.add_argument("--section", help="the heading to write a line under, without the ##")
    way.add_argument("--entry", metavar="TITLE",
                     help="a new heading to write at the end of --file, without the ## and the time")
    way.add_argument("--last", action="store_true", help="write a line under the last ## section of --file")
    parser.add_argument("--who", help="with --last: who the line is from, as in a reply under an asks entry")
    parser.add_argument("--file", help="the file to write in (--section's default: the newest docs/runs/<n>/run.md)")
    parser.add_argument("text", nargs="?", help="the line, without the time (none with --entry)")
    args = parser.parse_args(argv[1:])
    if args.entry is not None and args.text is not None:
        parser.error("--entry takes the title alone: the entry's body is written after it by the edit tools")
    if args.entry is None and args.text is None:
        parser.error("the line's text is missing")
    if args.who is not None and not args.last:
        parser.error("--who goes with --last")
    try:
        if args.entry is not None:
            path = args.file
            written = entry(path, args.entry)
        elif args.last:
            if not args.file:
                raise Refuse("--last needs --file: in a run record, name the heading with --section")
            path = args.file
            written = " · ".join(append(path, None, args.text, args.who))
        else:
            path = args.file or newest_run()
            written = f"## {args.section.strip()} · {append(path, args.section, args.text)[1]}"
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1
    print(f"RECORDED: {path} · {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
