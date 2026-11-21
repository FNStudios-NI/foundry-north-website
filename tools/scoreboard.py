# scoreboard.py: one row per closed run, so one template version can be set
# beside the next.
#
# Why it exists
#   Nothing compared one template version with the next, so a change that made
#   things worse could not be seen. His ruling 1 of 17 Nov 2026: quality first,
#   his verdict on what is made; then his time (design 0.9.0, Parts 6 and 7).
#   The row is shown, never judged: no number here decides anything.
#
# What it writes
#   docs/scoreboard.md, a table, one row per closed run, the newest last
#   (opened with its header when there is none):
#   | run | closed | template | made | enjoyment | his questions | his minutes | finished | surprises | sightings | lessons landed | lessons retired | usage per finished piece |
#   - template: the run's own version, the tag its last landing made or carried
#     (git describe at the last "squash <commit>" under ## Merges), because a row
#     written late must not wear the version of today (L036); no squash or no tag: —.
#   - made, enjoyment: his two taps, as given (— if not given); his minutes:
#     --minutes, else —.
#   - his questions: the rows of the "His rulings" table in the run's closing
#     entry ("## <yyyy-mm-dd hh:mm> — Run <n> closed", in docs/decisions*.md).
#   - finished (<landed>/<planned>) and surprises, as measures.py works them
#     out (loaded beside this file, as land.py loads its neighbours).
#   - sightings: <check> <n> per check, comma-separated, from the act-check
#     counter (act_check.py's counter_path) between the run's Go start and its
#     closing heading's time; "none" when there are none.
#   - lessons landed: " [new L<nnn> <yyyy-mm-dd>]" marks dated in the run, in
#     the files docs/lessons.md names; lessons retired: docs/retired.md lines
#     dated in the run.
#   - usage per finished piece: <n>% of his week, (close - Go) / finished pieces
#     to one decimal, from the two lines record.py --week stamps under ## Go, so
#     the number is read and never typed. — with a reading missing, no finished
#     piece, or a close below Go (the week reset between them).
#   A second row for the same run is refused; a run with no closing entry is
#   refused. Nothing else is written.
#
# How to run it (from the project's top folder)
#   python tools/scoreboard.py --run <n> --made <1-5> --enjoyment <1-5> [--minutes <n>]
#   python tools/scoreboard.py --last 5 [--html]    prints the last five rows, writes nothing;
#                                                   --html prints them as one <section data-scoreboard>
#
# Python 3 standard library only. No network.

import argparse
import html
import importlib.util
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
COLUMNS = ("run", "closed", "template", "made", "enjoyment", "his questions", "his minutes", "finished",
           "surprises", "sightings", "lessons landed", "lessons retired", "usage per finished piece")
FILE = os.path.join("docs", "scoreboard.md")
NONE = "—"
DATE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · ")
COUNTED = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) · [^·]* · ([\w-]+) · ")
SQUASH = re.compile(r"squash ([0-9a-f]{7,40})")
WEEK = re.compile(r"^- \d{2}:\d{2} · Week read at (Go|the close): (\d+)%$")


class Refuse(Exception):
    pass


def neighbour(name):
    """A tool beside this one, loaded as land.py loads its neighbours."""
    spec = importlib.util.spec_from_file_location(f"{name}_for_scoreboard", os.path.join(TOOLS, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def rows(project):
    """The table's rows in docs/scoreboard.md, each a list of cells, the header and its rule left out."""
    path = os.path.join(project, FILE)
    if not os.path.isfile(path):
        return []
    found = []
    for line in read(path).splitlines():
        if not line.strip().startswith("|"):
            continue
        row = cells(line)
        if row[0] == COLUMNS[0] or set("".join(row)) <= set("-: "):
            continue
        found.append(row)
    return found


def as_table(found):
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    return "\n".join(lines + ["| " + " | ".join(r) + " |" for r in found])


def as_html(found):
    head = "".join(f"<th>{html.escape(c)}</th>" for c in COLUMNS)
    body = ["<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>" for r in found]
    return "\n".join(['<section data-scoreboard>', "<h2>The scoreboard: the last runs</h2>",
                      '<div class="tablewrap"><table>', f"<thead><tr>{head}</tr></thead>",
                      "<tbody>", *body, "</tbody>", "</table></div>", "</section>"])


def yaml_field(project, key):
    path = os.path.join(project, "project.yaml")
    if not os.path.isfile(path):
        return None
    m = re.search(rf"^{key}:\s*(.*?)\s*$", read(path), re.M)
    return m.group(1).strip("'\"") if m and m.group(1) else None


def closing_entry(project, run, measures):
    """(heading time, body lines) of the run's closing entry, the earliest; None when there is none."""
    found = []
    for name in sorted(os.listdir(os.path.join(project, "docs"))):
        if not re.fullmatch(r"decisions.*\.md", name):
            continue
        body = None
        for line in read(os.path.join(project, "docs", name)).splitlines():
            if line.startswith("## "):
                m = measures.CLOSED.match(line)
                body = [] if m and int(m.group(2)) == run else None
                if body is not None:
                    found.append((m.group(1), body))
            elif body is not None:
                body.append(line)
    return min(found, key=lambda f: f[0]) if found else None


def his_questions(body):
    """The rows of the "His rulings" table: each row whose first cell is a number."""
    n, under = 0, False
    for line in body:
        if not under:
            under = line.strip().startswith("His rulings")
        elif line.strip().startswith("|"):
            n += bool(re.fullmatch(r"\d+", cells(line)[0]))
        elif line.strip():
            break
    return n


def finished_and_surprises(project, run, measures):
    folder = os.path.join(project, "docs", "runs", str(run))
    path = os.path.join(folder, "run.md")
    if not os.path.isfile(path):
        raise Refuse(f"no run record at {path}")
    page = measures.sections(read(path))
    start = measures.start_of(path, page.get("Go", []))
    if start is None:
        raise Refuse(f"{measures.NO_START}, in {path}")
    plan_path = os.path.join(folder, "plan-signed.md")
    plan = measures.sections(read(plan_path)) if os.path.isfile(plan_path) else {}
    landed = []
    for line in measures.bullets(page.get("Merges", [])):
        f = measures.fields(line)
        got = measures.card_of(f[1]) if len(f) > 1 else None
        if got and got[1] not in [c for _, c in landed]:
            landed.append(got)
    planned = measures.pieces(plan.get("The path", []))
    done = set()
    for desk, card in landed:
        done |= measures.named_pieces(project, desk, card) & planned
    surprises = len(measures.bullets(page.get("Unforeseen key points", []))) + len(measures.bullets(page.get("Blockers", [])))
    return start, f"{len(done)}/{len(planned)}", str(surprises), page, len(done)


def template_version(project, merges, measures):
    """The version in the tag the run's last landing made or carried; — with no squash or no tag.
    A squash counts only as a line's own part, as land.py writes it, never named in free words."""
    squashes = [m.group(1) for line in measures.bullets(merges) for m in map(SQUASH.fullmatch, measures.fields(line)) if m]
    if not squashes:
        return NONE
    try:
        done = subprocess.run(["git", "describe", "--tags", "--abbrev=0", "--match", "template/*", squashes[-1]],
                              cwd=project, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return NONE
    tag = done.stdout.strip()
    return tag[len("template/"):] if done.returncode == 0 and tag.startswith("template/") else NONE


def usage_per_piece(go, pieces):
    """<n>% of his week per finished piece, from the two stamped readings under ## Go; else —."""
    week = {}
    for line in go:
        m = WEEK.match(line.strip())
        if m:
            week.setdefault(m.group(1), int(m.group(2)))
    if not pieces or len(week) < 2 or week["the close"] < week["Go"]:
        return NONE
    return f"{(week['the close'] - week['Go']) / pieces:.1f}% of his week"


def sightings(project, start, close):
    """<check> <n> per check from the counter, between the run's start and its close."""
    name = yaml_field(project, "name")
    if not name:
        return NONE
    path = neighbour("act_check").counter_path(name)
    lo, hi = start + ":00", close + ":59"
    counts = {}
    if os.path.isfile(path):
        for line in read(path).splitlines():
            m = COUNTED.match(line)
            if m and lo <= m.group(1) <= hi:
                counts[m.group(2)] = counts.get(m.group(2), 0) + 1
    return ", ".join(f"{check} {n}" for check, n in sorted(counts.items())) or "none"


def lessons_landed(project, lo, hi):
    """The " [new L<nnn> <date>]" marks dated in the run, in the files docs/lessons.md names."""
    upgrade = neighbour("upgrade")
    named = sorted({l["file"] for l in upgrade.lessons(project) or [] if l["file"] not in ("template", "unknown")})
    n = 0
    for name in named:
        path = os.path.join(project, name)
        if os.path.isfile(path):
            for line in read(path).splitlines():
                m = upgrade.MARK.search(line)
                n += bool(m and lo <= m.group(2) <= hi)
    return str(n)


def lessons_retired(project, lo, hi):
    path = os.path.join(project, "docs", "retired.md")
    if not os.path.isfile(path):
        return "0"
    return str(sum(1 for line in read(path).splitlines() if (m := DATE.match(line)) and lo <= m.group(1) <= hi))


def tap(value, what):
    if value is None:
        return NONE
    if value not in ("1", "2", "3", "4", "5"):
        raise Refuse(f"{what} is a tap from 1 to 5, not {value!r}")
    return value


def row(project, run, made, enjoyment, minutes):
    measures = neighbour("measures")
    if any(r[0] == str(run) for r in rows(project)):
        raise Refuse(f"run {run} already has its row in {FILE}; a run is scored once")
    entry = closing_entry(project, run, measures)
    if entry is None:
        raise Refuse(f"run {run} has no closing entry (\"## <yyyy-mm-dd hh:mm> — Run {run} closed\") in docs/decisions*.md")
    close, body = entry
    start, finished, surprises, page, pieces = finished_and_surprises(project, run, measures)
    lo, hi = start[:10], close[:10]
    return [str(run), close, template_version(project, page.get("Merges", []), measures), tap(made, "--made"),
            tap(enjoyment, "--enjoyment"), str(his_questions(body)), minutes or NONE, finished, surprises,
            sightings(project, start, close), lessons_landed(project, lo, hi), lessons_retired(project, lo, hi),
            usage_per_piece(page.get("Go", []), pieces)]


def append(project, new):
    path = os.path.join(project, FILE)
    text = read(path) if os.path.isfile(path) else ""
    if not rows(project) and "| " + " | ".join(COLUMNS) + " |" not in text:
        text = text + ("\n" if text and not text.endswith("\n") else "") + as_table([]) + "\n"
    elif text and not text.endswith("\n"):
        text += "\n"
    text += "| " + " | ".join(new) + " |\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="scoreboard.py", description="Write or show the scoreboard's rows.")
    parser.add_argument("--run", type=int)
    parser.add_argument("--made")
    parser.add_argument("--enjoyment")
    parser.add_argument("--minutes", type=int)
    parser.add_argument("--last", type=int)
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args(argv[1:])
    project = os.getcwd()
    try:
        if args.last is not None:
            found = rows(project)[-args.last:] if args.last > 0 else []
            print(as_html(found) if args.html else as_table(found))
            return 0
        if args.run is None:
            raise Refuse("name the run: --run <n> --made <1-5> --enjoyment <1-5> [--minutes <n>], or --last 5")
        new = row(project, args.run, args.made, args.enjoyment, None if args.minutes is None else str(args.minutes))
        append(project, new)
    except (Refuse, OSError) as why:
        print(f"REFUSE: {why}")
        return 1
    print(as_table([new]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
