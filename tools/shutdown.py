# shutdown.py: stop what a run started, and confirm nothing is left.
#
# What it is for
#   Everything a run starts goes on its shutdown list as it starts: sessions,
#   seats, background processes, watches, scheduled wake-ups and page
#   servers. At any stop the master runs this tool, which stops each item it
#   can, marks it closed in the run record, and says what is left.
#   Why: run 2 left the signal box running and two daily wake-ups that only a
#   deletion stops, and its masters raised their flags by hand (design § 8).
#
# The list it reads
#   The `## Shutdown list` of the newest run's docs/runs/<n>/run.md, or of
#   the run folder (or run.md) named. One line per item, in this form:
#     - <hh:mm> · <kind> · <what> · <id> · <how it stops> · open | closed <hh:mm>
#   A line already closed is left alone. A bullet that is not in this form is
#   counted as left, so a mistyped line is never passed over in silence.
#
# What it does with each open line
#   seat                     releases the claim with `cap_check.py release <id>`,
#                            the copy beside this file. A claim already gone
#                            is closed too.
#   process, watch, server   stops the process with that id (the id field's
#                            "pid <n>", "<name>.exe <n>", or a bare number),
#                            unless no process has that id (then it is closed),
#                            or the process now holding it started after the
#                            line's minute: Windows reuses ids, so that is
#                            someone else's process, listed and never stopped.
#                            A start time it cannot read is listed too.
#   thread, child, schedule  listed for the master to close by hand, with the
#   and any other kind       line's "how it stops". No script holds a T3 key
#                            (his call, decisions 06:49 of 8 Oct).
#   Each item it stops is marked `closed <hh:mm>` in place, the clock read in
#   the same step, and the record is written after each one, so a stop cut
#   short still leaves the record true.
#
# What it leaves running
#   --keep <id>              an open item the master names, once for each: it
#                            is not stopped and its line stays open. The tool
#                            says KEPT, and that the master named it. The id
#                            is matched as --closed matches it; one that fits
#                            no open line, or more than one, is a REFUSE with
#                            nothing changed.
#                            Why: in the job scout's run the tool was run dry
#                            only, twice, because run for real it would have
#                            stopped the page server his phone was using, so
#                            the servers stayed open on the list and the
#                            master's seat was released by hand (lesson H2).
#   the caller's own seat    a seat whose claim belongs to the claude.exe that
#                            ran this tool, found as cap_check.py finds it, is
#                            not released. The tool says KEPT, and that it is
#                            the seat of the session running this. Every other
#                            seat is released.
#                            Why: at run 4's review the tool released the seat
#                            of the very master that ran it (review note,
#                            13 Oct 08:22).
#
# How to run it (from the project's folder)
#   python tools/shutdown.py [docs/runs/<n>] [--keep <id>]... [--dry-run]
#   python tools/shutdown.py [docs/runs/<n>] --closed <id>
#   It ends by confirming: NOTHING LEFT (exit 0) when nothing but the kept
#   items is open, or LEFT: <n> and each other open line (exit 1), the kept
#   items named apart and not counted. --closed <id> marks one item the
#   master closed by hand (the whole id field, or one word of it, such as
#   mcp:0429ba1a), then confirms; it is how a kept item is closed later.
#   --dry-run says what it would do, WOULD KEEP for the kept, and changes
#   nothing (exit 0).
#
# Python 3 standard library only.

import argparse
import datetime
import importlib.util
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CAP_CHECK = os.path.join(HERE, "cap_check.py")
PROCESS_KINDS = ("process", "watch", "server")
HEADING = "## Shutdown list"

_spec = importlib.util.spec_from_file_location("cap_check_for_shutdown", CAP_CHECK)
cap_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cap_check)


# ---- the record -------------------------------------------------------------

def newest_run(project):
    runs = os.path.join(project, "docs", "runs")
    numbers = [int(n) for n in os.listdir(runs) if n.isdigit() and os.path.isdir(os.path.join(runs, n))] \
        if os.path.isdir(runs) else []
    return os.path.join(runs, str(max(numbers))) if numbers else None


def record_path(where):
    return where if os.path.isfile(where) else os.path.join(where, "run.md")


def read_lines(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().splitlines(keepends=True)


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))


def run_start(lines):
    """The run's Go time (`- Start: yyyy-mm-dd hh:mm`), or None."""
    for line in lines:
        found = re.match(r"\s*-\s*Start:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", line)
        if found:
            return datetime.datetime.strptime(found.group(1), "%Y-%m-%d %H:%M")
    return None


def parse(line):
    """A shutdown line as a dict, or None if it is not in the list's form."""
    parts = line.rstrip("\r\n")[2:].split(" · ")
    if len(parts) < 6 or not re.fullmatch(r"\d{2}:\d{2}", parts[0].strip()):
        return None
    status = parts[-1].strip()
    if not re.match(r"(open|closed \d{2}:\d{2})\b", status):
        return None
    return {"time": parts[0].strip(), "kind": parts[1].strip().lower(),
            "what": " · ".join(parts[2:-3]).strip(), "id": parts[-3].strip(),
            "how": parts[-2].strip(), "open": status.startswith("open")}


def shutdown_lines(lines):
    """The index of every bullet in the shutdown list, with its parse (None if
    it is not in the list's form)."""
    found, inside = [], False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            inside = line.rstrip() == HEADING
        elif inside and line.startswith("- "):
            found.append((i, parse(line)))
    return found


def mark_closed(path, index):
    """Mark one line closed at the clock's minute, read now, and write the record."""
    lines = read_lines(path)
    line = lines[index]
    body = line.rstrip("\r\n")
    end = line[len(body):]
    head, status = body.rsplit(" · ", 1)
    rest = status.strip()[len("open"):]
    lines[index] = f"{head} · closed {datetime.datetime.now():%H:%M}{rest}{end}"
    write_lines(path, lines)
    return lines[index].rstrip("\r\n")


# ---- processes and seats ----------------------------------------------------

def pid_of(id_field):
    """The process id an id field names, or None if it names none for certain."""
    found = re.search(r"(?:\bpid\b\s*:?\s*|\.exe\s+)(\d+)", id_field, re.IGNORECASE)
    if found:
        return int(found.group(1))
    return int(id_field) if id_field.strip().isdigit() else None


def pid_alive(pid):
    return cap_check.pid_alive(pid)


def started_at(pid):
    """When the process with this id started, as local time, or None if unreadable."""
    ticks = cap_check.process_started(pid)
    if ticks is None:
        return None
    if os.name == "nt":  # 100-nanosecond steps since 1601
        return datetime.datetime.fromtimestamp(ticks / 10_000_000 - 11_644_473_600)
    try:  # clock ticks since the machine booted
        with open("/proc/stat", encoding="utf-8") as f:
            boot = next(int(l.split()[1]) for l in f if l.startswith("btime "))
        return datetime.datetime.fromtimestamp(boot + ticks / os.sysconf("SC_CLK_TCK"))
    except (OSError, StopIteration, ValueError):
        return None


def stop_process(pid):
    """Stop the process and its children; True once it is gone."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True
    for _ in range(30):
        if not pid_alive(pid):
            return True
        time.sleep(0.1)
    return False


def release_seat(claim_id):
    """Release a claim with the cap_check beside this file; (closed, what it said)."""
    done = subprocess.run([sys.executable, CAP_CHECK, "release", claim_id],
                          capture_output=True, text=True)
    said = (done.stdout or done.stderr).strip()
    return said.startswith(("RELEASED", "NOT FOUND")), said


def own_seat(claim_id):
    """Whether this claim belongs to the caller's own claude.exe, found as cap_check finds it."""
    data = dict(cap_check.read_claims(cap_check.default_seats())).get(claim_id)
    if data is None or not cap_check.claim_alive(data):
        return False
    return int(data["pid"]) == cap_check.own_claude(cap_check.process_table(), os.getpid())


# ---- what to do with one line -------------------------------------------------

def line_time(item, start):
    """The line's minute as a full local time, from the run's Go date."""
    hh, mm = map(int, item["time"].split(":"))
    when = start.replace(hour=hh, minute=mm, second=0, microsecond=0)
    return when + datetime.timedelta(days=1) if when < start.replace(second=0) else when


def plan(item, start):
    """What to do: ('seat', None), ('stop', pid), ('gone', pid) or ('leave', why)."""
    kind = item["kind"]
    if kind == "seat":
        return "seat", None
    if kind not in PROCESS_KINDS:
        return "leave", f"for the master to close by hand: {item['how']}"
    pid = pid_of(item["id"])
    if pid is None:
        return "leave", "no single process id in its id field; for the master to close by hand"
    if not pid_alive(pid):
        return "gone", pid
    if start is None:
        return "leave", f"pid {pid} is running, and the record has no `- Start:` date to tell a reused id"
    began = started_at(pid)
    if began is None:
        return "leave", f"pid {pid} is running, and its start time cannot be read; never stopped unchecked"
    if began >= line_time(item, start) + datetime.timedelta(minutes=1):
        return "leave", f"pid {pid} now belongs to a process started {began:%Y-%m-%d %H:%M}, after the line: a reused id, never stopped"
    return "stop", pid


# ---- the commands -------------------------------------------------------------

def open_with_id(path, wanted):
    """The index of every open line whose id field is this id, or holds it as one word."""
    return [i for i, item in shutdown_lines(read_lines(path))
            if item and item["open"] and (wanted == item["id"] or wanted in re.split(r"[,\s]+", item["id"]))]


def refuse_id(path, wanted, matches):
    lines = read_lines(path)
    print(f"REFUSE: {len(matches)} open lines have the id {wanted}; nothing changed")
    for i in matches:
        print(f"  {lines[i].rstrip()}")
    return 1


def confirm(path, reasons, kept=()):
    left = [(i, item) for i, item in shutdown_lines(read_lines(path))
            if (item is None or item["open"]) and i not in kept]
    if not left:
        print("NOTHING LEFT")
        return 0
    lines = read_lines(path)
    print(f"LEFT: {len(left)}")
    for i, item in left:
        print(f"  {lines[i].rstrip()}")
        if item is None:
            print("      not in the shutdown list's form")
        elif i in reasons:
            print(f"      {reasons[i]}")
    return 1


def shut_down(path, dry_run, keep):
    kept = set()
    for wanted in keep:
        matches = open_with_id(path, wanted)
        if len(matches) != 1:
            return refuse_id(path, wanted, matches)
        kept.add(matches[0])
    lines = read_lines(path)
    start = run_start(lines)
    reasons = {}
    for i, item in shutdown_lines(lines):
        if item is None or not item["open"]:
            continue
        label = f"{item['kind']} · {item['what']} · {item['id']}"
        why = "the master named it with --keep" if i in kept else None
        if why is None and item["kind"] == "seat" and own_seat(item["id"]):
            why = "the seat of the session running this"
            kept.add(i)
        if why:
            print(f"{'WOULD KEEP' if dry_run else 'KEPT'}: {label}\n      {why}")
            continue
        action, detail = plan(item, start)
        if action == "leave":
            reasons[i] = detail
            print(f"{'WOULD LEAVE' if dry_run else 'LEFT'}: {label}\n      {detail}")
        elif dry_run:
            print({"seat": f"WOULD RELEASE: {label}",
                   "stop": f"WOULD STOP: {label} (pid {detail})",
                   "gone": f"WOULD CLOSE: {label} (pid {detail} is gone)"}[action])
        elif action == "seat":
            closed, said = release_seat(item["id"])
            if closed:
                print(f"RELEASED: {label} ({said})\n      {mark_closed(path, i)}")
            else:
                reasons[i] = f"the release failed: {said}"
                print(f"LEFT: {label}\n      {reasons[i]}")
        elif action == "gone":
            print(f"GONE: {label} (pid {detail} is not running)\n      {mark_closed(path, i)}")
        elif stop_process(detail):
            print(f"STOPPED: {label} (pid {detail})\n      {mark_closed(path, i)}")
        else:
            reasons[i] = f"pid {detail} did not stop"
            print(f"LEFT: {label}\n      {reasons[i]}")
    if dry_run:
        print("DRY RUN: nothing changed")
        return 0
    return confirm(path, reasons, kept)


def close_by_hand(path, wanted):
    matches = open_with_id(path, wanted)
    if len(matches) != 1:
        return refuse_id(path, wanted, matches)
    print(f"CLOSED: {mark_closed(path, matches[0])}")
    return confirm(path, {})


def main(argv):
    parser = argparse.ArgumentParser(prog="shutdown.py", description="Stop what a run started; confirm nothing is left.")
    parser.add_argument("run", nargs="?", help="the run folder or its run.md (default: the newest run here)")
    parser.add_argument("--dry-run", action="store_true", help="say what it would do; change nothing")
    parser.add_argument("--closed", metavar="ID", help="mark one item the master closed by hand")
    parser.add_argument("--keep", metavar="ID", action="append", default=[],
                        help="leave one open item running; may be given more than once")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 1
    where = args.run or newest_run(os.getcwd())
    if where is None:
        print("REFUSE: no docs/runs/<n>/ here; name the run folder")
        return 1
    path = record_path(where)
    if not os.path.isfile(path):
        print(f"REFUSE: no run record at {path}")
        return 1
    if not any(line.rstrip() == HEADING for line in read_lines(path)):
        print(f"REFUSE: {path} has no `{HEADING}`")
        return 1
    if args.closed:
        if args.dry_run:
            print("REFUSE: --closed and --dry-run together; pick one")
            return 1
        if args.keep:
            print("REFUSE: --closed and --keep together; pick one")
            return 1
        return close_by_hand(path, args.closed)
    return shut_down(path, args.dry_run, args.keep)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # the list's "·" reads as garbage in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv))
