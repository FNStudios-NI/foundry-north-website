"""where_am_i.py -- says what stage a project is at, read from its files.

What it is for:
  Open any project and ask "where are we?". This tool looks at which files
  exist and answers in one line: the stage, then the one next thing to do.
  Then one line for each desk in desks/, with that desk's own stage.

Why the rule exists:
  In the old system a status was typed by hand, and it was wrong for three
  weeks. So here nothing is typed and nothing is stored. The files are the
  truth: if the file that proves a stage exists, the project is at that stage.
  This tool only reads. It never writes a file, and it touches no network
  but one read of the template's tags (the template line, below).

How to run it:
  python tools/where_am_i.py                  (the project this tools/ sits in)
  python tools/where_am_i.py <project-folder>
  python tools/where_am_i.py <project-folder> --json   (the same, as JSON)
  python tools/where_am_i.py --session <id> --logs <folder> --window <n>
                                              (which conversation to read; see below)
  python tools/where_am_i.py --zone-file <path>   (his zone from another file; see below)

After the stage line and the desk lines it says his time and the Python,
then two more things, each read fresh and never stored.

  his time: 18:30, Wed 28 Oct (UTC+8) · this computer 10:30
    Rhys's own time, then this computer's: the clock is read once, his time
    is that reading in UTC plus his offset, and this computer's is the same
    reading in its own local time. His zone is read from one file every
    project on the machine reads: his-time-zone.txt in the agentic-meta
    folder that holds cap_check.py's seats folder (agentic-meta under
    %LOCALAPPDATA%, or ~/.local/share/agentic-meta/ with no LOCALAPPDATA).
    --zone-file <path> reads another file instead. Its first non-blank line is UTC, or UTC then
    + or - then hours, with optional :mm (UTC+8, UTC-5, UTC+05:30): a fixed
    offset, so no time-zone database is used. With no such file it says
    "his time: not known (no zone in <the file>; one line such as UTC+8)";
    with a line of another form, "his time: not known (<the file> says
    "<the line>"; one line such as UTC+8)". Neither changes the exit code.
    Why: a master once gave him a timeline in this machine's clock while he
    was hours ahead, a wrong plan for his day. His zone of 28 Oct 2026 is
    UTC+8, his word: "we are 8 hours now". The file sits beside the seats
    folder because T3's worktrees sit outside a project's parent folders, so
    only a machine-wide place reaches every agent, and the seats folder's
    parent already is one.

  python: python3.11
    The first of python, python3, py -3, then each python3.N on the PATH
    (highest N first) that runs, prints "Python 3." for --version, is not
    under a WindowsApps folder, and imports pytest. With none, it says
    "python: none found with pytest". Each try has a timeout of a few
    seconds, and nothing is installed or written.
    Why: bare python here is the Windows Store's shortcut, and only one of
    the Pythons has pytest, so each agent once spent a few failed calls
    guessing a name.

  no remote: the record is on this machine only
    Said when the project folder is a git repository with no remote, or is
    no git repository at all. With a remote, nothing is said. If git cannot
    be run it says "remote: not read (git could not be run)", never a guess.
    "git remote" is a local question: no network is touched.
    Why: a project's plan was once signed before anybody noticed the project
    had no online copy. A record on one machine is lost with that machine.

  conversation: 11% full (110,000 of 1,000,000 tokens; hand over at 450,000)
    How full this session's conversation is, read from the session's own
    log. The count is the last main-thread reply's input_tokens +
    cache_read_input_tokens + cache_creation_input_tokens. A line marked
    isSidechain is a helper's and is left out. The session is --session
    <id>, or the environment's CLAUDE_CODE_SESSION_ID; its log is <id>.jsonl
    anywhere under --logs (default ~/.claude/projects). The window is
    --window <n>, or one million, whatever model the log names. The percent
    is rounded down. The mark is 450,000 tokens: a master hands over there.
    With no session id, no log, or no reply in the log, it says
    "conversation: not read (<why>)", and the exit code does not change.
    Why: a master hands over at a number to read, not a judgement by eye.
    The million and the mark are his words of 28 Oct 2026: "i always use the
    1m context model so change this for good" and "like 450K is a good mark".

Then the upgrade's lines. The lessons file and the closing block are read by
upgrade.py, which sits beside this file and is loaded from there (as land.py
loads record.py); this tool uses its waiting() and check() and never reads
either itself. The workflow files' tags are read by status.py, loaded the
same way.

  lessons: 3 waiting, the oldest 2026-11-10
    Said on every open of a folder with docs/lessons.md (or "lessons: none
    waiting"), after the conversation line, with " · upgrade due" at its end
    when DUE_COUNT (15) or more wait or the oldest is DUE_DAYS (14) days old
    or more. Why: a project that works in sessions must see its backlog every
    time a master opens it (the upgrade design of 12 Nov 2026, § 2 cause 6);
    the two numbers are the design's § 7 call, and his to change.

  template: 0.9.1 · newest 0.9.2 · update due
    Said on every open, after the lessons line: project.yaml's
    template_version, the newest template/<x.y.z> tag, compared as numbers
    (0.10.0 is newer than 0.9.2), and " · update due" when it is behind. The
    tag is read from the first that answers: the project folder itself when
    it holds template/VERSION (the template's home), then a folder beside it
    that holds one (git tag --list), then git ls-remote of TEMPLATE_REMOTE,
    with no sign-in window or prompt. All of it within 5 seconds; none
    answering, "newest not read". With no template_version line, "version
    not in project.yaml". --template-home and --template-remote name others,
    for tests. Why: a project fell behind the template and nobody said so;
    his words of 21 Nov 2026, "this needs to be an automatic catch"
    (tracks.md rule 46: a tool says it, not a line to remember).

  house lessons waiting: 2
    Said only where a harvest.py sits beside this file (this house's own
    tool; --harvest <path> names another, for tests): it is run as
    "<this Python> <harvest.py> --count" in the project's folder, for 20
    seconds at most, and its first line is printed when it starts "house
    lessons waiting:". A failure says "house lessons waiting: not read
    (<why>)". With no harvest.py nothing is said. Why: the design's Part 5
    says this tool prints the line here, while the template carries no road
    to any house (§ 7's call), so the house's tool does the counting.

  foundations: desks/hero-film/workflow.md step 1 Intake · 1 job; desks/hero-film/workflow.md step 4 Style ideas to the client · 1 job
  foundations: none
    Said on every open: each step (or a workflow's own Tag: line) tagged
    `foundation · <n> job(s)` in the project's workflow files, as status.py
    reads them. The brief is never read for them, so a "Locked: none" line is
    never taken for a way named "none". Why: the design of 17 Nov 2026,
    Part 3, his rulings 3 and 4 of 17 Nov 07:43, and 12 Nov fault 1.

With --json these are "his_time" (its time, day, zone and computer, or null,
with "his_time_why" saying why), "python" (the name, or null), "remote"
(true, false, or null when not read), "conversation" (its used, window,
percent and hand_over_at, or null when not read), "lessons" (its waiting,
oldest and due, or null with no docs/lessons.md), "template" (its version,
newest and due; version or newest null when not read), "foundations" (each one's
file, step, name and jobs; step null for a workflow's own Tag: line) and
"house_lessons" (the line, or null with no harvest.py).

Runs are numbered. A project runs many times, and each run has its own
folder, docs/runs/<n>/, starting at 1:
  docs/runs/<n>/plan-signed.md   the plan as Rhys signed it
  docs/runs/<n>/run.md           the run record
  docs/runs/<n>/review.html      the review page
A run is closed by an entry in docs/decisions.md whose heading says
"Run <n> closed" (like ## 2026-10-07 09:00 — Run 1 closed). After that the
project is ready for run <n+1>. Why: a project that could run only once read
"review" for ever after its first review, and its second run had nowhere to go.

The stages. Before the brief, the project is new, unless docs/decisions.md
already holds a dated ruling (a line starting "## " and a date, like
## 2026-10-05). Then it is a fault: Rhys has ruled, so discovery has begun,
but the brief that should have been written at that first ruling is missing.
After the brief, the tool reads only the NEWEST run folder (the highest n)
and the "Run <n> closed" entries.
A desk's stage is worked out the same way, inside its own folder.
  new        | no docs/brief.md, no dated ruling           | start discovery
  fault      | no docs/brief.md, a dated ruling            | write the brief from docs/decisions.md, then carry on discovery
  discovery  | docs/brief.md, no run folder with a plan    | carry on discovery, ending in the plan page for Rhys to sign
  signed     | newest run has plan-signed.md, no run.md    | start run <n>
  run        | newest run has run.md, no review.html       | finish run <n>, then open the review session
  review     | newest run has review.html, not yet closed  | Rhys keeps or undoes each piece, then run <n> is closed in docs/decisions.md
  ready      | "Run <n> closed" for the newest run         | run <n+1> — plan it
"Run <n> closed" is read before the files, so a closed run is never reported
as signed, even if its plan is the only file in its folder. A new plan goes
in a new folder, docs/runs/<n+1>/.

The upgrade gate. In a folder with docs/lessons.md, a closed newest run is
ready only once upgrade.py's check() passes for the newest closing entry.
Until then the stage is review and the line reads
  review: run <n> — the upgrade is not done (<k> lessons unanswered)
k being the waiting lessons dated at or before the close; when k is 0 and the
check still fails, its first fault stands in place of the count. Why: the
stage is read from the files, and a close without the upgrade is not a close
(design Part 3). Without docs/lessons.md nothing is gated, whatever the
decisions say: a house on an older version, or mid-review, closes as it
always has (§ 7a answer 3).

One more fault, a stop until it is put right: docs/plan-signed.md,
docs/run.md or docs/review.md at the top of docs/. These are the old
single-run paths and are no longer read. Move them into docs/runs/1/ (the
review becomes review.html, a page). This is checked before the brief: a
project with run files is not new.

It refuses (one line, non-zero exit) when the folder is not a project:
no CLAUDE.md and no docs/ folder.
"""

import argparse
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# "upgrade due": this many lessons waiting, or the oldest this many days old (design § 7, his to change).
DUE_COUNT = 15
DUE_DAYS = 14

# upgrade.py, beside this file: the one reading of the lessons file and the closing block.
_spec = importlib.util.spec_from_file_location("upgrade_for_where_am_i",
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "upgrade.py"))
upgrade = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upgrade)

NEW = ("new", None, "start discovery")
DISCOVERY = ("discovery", "docs/brief.md", "carry on discovery, ending in the plan page for Rhys to sign")

# No brief, but a dated ruling in decisions.md: discovery has begun and the brief is missing.
FAULT = ("fault", "docs/decisions.md",
         "rulings exist but docs/brief.md is missing — write the brief from docs/decisions.md, then carry on discovery")
RULING = re.compile(r"## \d{4}-\d{2}-\d{2}")

# The single-run paths from before runs were numbered. Never read now; finding one is a fault.
OLD_PATHS = ["docs/plan-signed.md", "docs/run.md", "docs/review.md"]
OLD_FAULT = "run files at the old paths — move them into docs/runs/1/ (the review becomes review.html)"

# A heading in decisions.md that closes a run, like "## 2026-10-07 09:00 — Run 1 closed".
CLOSED = re.compile(r"## .*\bRun (\d+) closed\b", re.IGNORECASE)

NO_REMOTE = "no remote: the record is on this machine only"
REMOTE_NOT_READ = "remote: not read (git could not be run)"

# What a reply's conversation holds: the three counts of what was sent in.
USED = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")

# His mark: a master hands over when its conversation passes this many tokens (28 Oct 2026).
HAND_OVER_AT = 450_000

# His zone: UTC, or UTC then a sign, hours and optional :mm. A fixed offset, no time-zone database.
ZONE = re.compile(r"UTC(?:([+-])(\d{1,2})(?::(\d{2}))?)?")
ZONE_HINT = "one line such as UTC+8"

# The names tried for the Python, in the conductor skill's order; each python3.N on the PATH follows.
PYTHONS = [["python"], ["python3"], ["py", "-3"]]
PYTHON_3N = re.compile(r"python3\.(\d+)(?:\.exe)?", re.IGNORECASE)
PROBE_TIMEOUT = 5

# The date, and the time if it has one, at the head of a closing heading.
CLOSED_WHEN = re.compile(r"## (\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)")
HOUSE = "house lessons waiting:"
HARVEST_TIMEOUT = 20

# The template's home online, where the newest template/<x.y.z> tag is read when no home sits beside the
# project: a pointer, not a credential. The whole reading of the tag takes TEMPLATE_WAIT seconds at most.
TEMPLATE_REMOTE = "https://github.com/FNStudios-NI/agentic-meta-system.git"
TEMPLATE_WAIT = 5
TEMPLATE_TAG = re.compile(r"(?:^|\trefs/tags/)template/([\d.]+)$")
TEMPLATE_VERSION = re.compile(r"^template_version:\s*[\"']?([^\s\"'#]+)", re.M)
# No sign-in window or prompt from git, ever.
QUIET_GIT = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}


def has_ruling(folder):
    """True if docs/decisions.md has a line starting '## ' and a date (yyyy-mm-dd)."""
    decisions = folder / "docs" / "decisions.md"
    if not decisions.is_file():
        return False
    text = decisions.read_text(encoding="utf-8", errors="replace")
    return any(RULING.match(line) for line in text.splitlines())


def closed_runs(folder):
    """The run numbers that have a 'Run <n> closed' heading in docs/decisions.md."""
    decisions = folder / "docs" / "decisions.md"
    if not decisions.is_file():
        return set()
    text = decisions.read_text(encoding="utf-8", errors="replace")
    return {int(m.group(1)) for m in map(CLOSED.match, text.splitlines()) if m}


def newest_run(folder):
    """The highest n with a folder docs/runs/<n>/, or None if there is none."""
    runs = folder / "docs" / "runs"
    if not runs.is_dir():
        return None
    numbers = [int(p.name) for p in runs.iterdir() if p.is_dir() and p.name.isdigit()]
    return max(numbers) if numbers else None


def close_time(folder, n):
    """The date (and time, if written) of the last 'Run <n> closed' heading in docs/decisions.md, or None."""
    text = (folder / "docs" / "decisions.md").read_text(encoding="utf-8", errors="replace")
    when = None
    for line in text.splitlines():
        m = CLOSED.match(line)
        if m and int(m.group(1)) == n:
            at = CLOSED_WHEN.match(line)
            when = at.group(1) if at else None
    return when


def upgrade_not_done(folder, n):
    """None when run n's close may stand; else what is missing, as '<k> lessons unanswered' or the first fault.

    Gated only where docs/lessons.md exists (design § 7a answer 3)."""
    if not (folder / "docs" / "lessons.md").is_file():
        return None
    passed, faults, _ = upgrade.check(folder)
    if passed:
        return None
    when = close_time(folder, n)
    k = sum(1 for lesson in upgrade.waiting(folder) if when is None or lesson["time"][:len(when)] <= when)
    if k:
        return f"{k} lessons unanswered"
    return faults[0]


def lessons_waiting(folder, today=None):
    """{waiting, oldest, due} for a folder with docs/lessons.md, or None without one."""
    if not (folder / "docs" / "lessons.md").is_file():
        return None
    left = upgrade.waiting(folder)
    if not left:
        return {"waiting": 0, "oldest": None, "due": False}
    oldest = left[0]["time"][:10]
    today = today or datetime.date.today()
    age = (today - datetime.datetime.strptime(oldest, "%Y-%m-%d").date()).days
    return {"waiting": len(left), "oldest": oldest, "due": len(left) >= DUE_COUNT or age >= DUE_DAYS}


def foundations_line(found):
    """The one foundations: line from status.foundations()."""
    return "foundations: " + ("; ".join(upgrade.status.foundation_text(f) for f in found) or "none")


def house_lessons(folder, harvest):
    """The first line of '<this Python> <harvest> --count' run in the folder, or a 'not read' line; None with no harvest."""
    if harvest is None:
        return None
    try:
        done = subprocess.run([sys.executable, str(harvest), "--count"], cwd=str(folder), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=HARVEST_TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"{HOUSE} not read (no answer in {HARVEST_TIMEOUT} seconds)"
    except (OSError, subprocess.SubprocessError) as e:
        return f"{HOUSE} not read ({e})"
    first = (done.stdout.splitlines() or [""])[0].strip()
    if done.returncode != 0:
        return f"{HOUSE} not read ({Path(harvest).name} exited {done.returncode})"
    if not first.startswith(HOUSE):
        return f"{HOUSE} not read ({Path(harvest).name} said \"{first}\")"
    return first


def _as_numbers(version):
    """A version as numbers, '0.10.0' -> (0, 10, 0), so it compares as numbers; None when it is not one."""
    parts = (version or "").split(".")
    return tuple(int(p) for p in parts) if all(p.isdigit() for p in parts) else None


def _git_lines(command, deadline):
    """The lines git printed, or None when it failed or did not answer by the deadline (time.monotonic())."""
    left = deadline - time.monotonic()
    if left <= 0:
        return None
    try:
        done = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, encoding="utf-8", errors="replace", env={**os.environ, **QUIET_GIT})
    except OSError:
        return None
    try:
        out, _ = done.communicate(timeout=left)
    except subprocess.TimeoutExpired:
        done.kill()  # never waited for again: a child it started may hold the pipe open
        return None
    return out.splitlines() if done.returncode == 0 else None


def _newest_tag(lines):
    """The newest template/<x.y.z> in git's lines, compared as numbers; None when there is none."""
    found = [v for v in (_as_numbers(m.group(1)) for m in (TEMPLATE_TAG.search(l.strip()) for l in lines or []) if m) if v]
    return ".".join(map(str, max(found))) if found else None


def newest_template(folder, home=None, remote=TEMPLATE_REMOTE, wait=TEMPLATE_WAIT):
    """The newest template/<x.y.z> tag, from the first that answers within `wait` seconds: the folder itself
    when it holds template/VERSION, then a folder beside it that holds one (or `home` in place of both), then
    git ls-remote of `remote`. None when none answers."""
    deadline = time.monotonic() + wait
    folder = Path(folder).resolve()
    if home:
        homes = [Path(home)]
    else:
        try:
            homes = [folder] + sorted(p for p in folder.parent.iterdir() if p != folder and p.is_dir())
        except OSError:
            homes = [folder]
    for place in homes:
        if (place / "template" / "VERSION").is_file():
            newest = _newest_tag(_git_lines(["git", "-C", str(place), "tag", "--list", "template/*"], deadline))
            if newest:
                return newest
    return _newest_tag(_git_lines(["git", "ls-remote", "--tags", "--refs", remote, "refs/tags/template/*"], deadline))


def template_state(folder, home=None, remote=TEMPLATE_REMOTE):
    """{version, newest, due}: project.yaml's template_version (None without one), the newest tag (None when
    not read), and whether the version is behind it."""
    yaml = folder / "project.yaml"
    found = TEMPLATE_VERSION.search(yaml.read_text(encoding="utf-8", errors="replace")) if yaml.is_file() else None
    version = found.group(1) if found else None
    newest = newest_template(folder, home, remote)
    mine, top = _as_numbers(version), _as_numbers(newest)
    return {"version": version, "newest": newest, "due": bool(mine and top and top > mine)}


def template_line(state):
    """The one template: line."""
    return (f"template: {state['version'] or 'version not in project.yaml'} · "
            + (f"newest {state['newest']}" if state["newest"] else "newest not read")
            + (" · update due" if state["due"] else ""))


def stage_of(folder):
    """Return (stage, proof file, next action, run number or None) for one project or desk folder."""
    old = [path for path in OLD_PATHS if (folder / path).is_file()]
    if old:
        return ("fault", old[0], OLD_FAULT, None)
    if not (folder / "docs" / "brief.md").is_file():
        return (*FAULT, None) if has_ruling(folder) else (*NEW, None)

    n = newest_run(folder)
    if n is None:
        return (*DISCOVERY, None)
    here = f"docs/runs/{n}"
    plan, record, review = (folder / here / name for name in ("plan-signed.md", "run.md", "review.html"))

    # Closed is read first, so a closed run's plan is never reported as signed.
    if n in closed_runs(folder):
        not_done = upgrade_not_done(folder, n)
        if not_done:
            return ("review", "docs/decisions.md", f"run {n} — the upgrade is not done ({not_done})", n)
        return ("ready", "docs/decisions.md", f"run {n + 1} — plan it", n + 1)
    if review.is_file():
        return ("review", f"{here}/review.html",
                f"run {n} — Rhys keeps or undoes each piece, then it is closed with a \"Run {n} closed\" entry in docs/decisions.md", n)
    if record.is_file():
        return ("run", f"{here}/run.md", f"run {n} — finish the run, then open the review session", n)
    if plan.is_file():
        return ("signed", f"{here}/plan-signed.md", f"run {n} — start the run", n)
    # An empty newest folder: no plan is signed for it yet.
    return (*DISCOVERY, None)


def desks_of(folder):
    """Every desk folder under desks/, skipping starters whose names begin with _."""
    desks = folder / "desks"
    if not desks.is_dir():
        return []
    return sorted(p for p in desks.iterdir() if p.is_dir() and not p.name.startswith("_"))


def has_remote(folder):
    """True if the folder's git repository has a remote; False if it has none, or the folder is no repository; None if git cannot say."""
    try:
        done = subprocess.run(["git", "-C", str(folder), "remote"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode == 0:
        return bool(done.stdout.strip())
    # git ran and would not answer. With no .git here or above, that is because there is no repository.
    here = folder.resolve()
    if not any((p / ".git").exists() for p in (here, *here.parents)):
        return False
    return None


def conversation(session, logs, window):
    """How full a session's conversation is: ({used, window, percent, hand_over_at}, None), or (None, why it was not read)."""
    if not session:
        return None, "no session id"
    name = session + ".jsonl"
    log = next((Path(top) / name for top, _, files in os.walk(logs) if name in files), None)
    if log is None:
        return None, "no log for this session"
    used = None
    try:
        with open(log, encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                # A line marked isSidechain is a helper's, not this conversation's.
                if not isinstance(e, dict) or e.get("type") != "assistant" or e.get("isSidechain"):
                    continue
                msg = e.get("message") if isinstance(e.get("message"), dict) else {}
                usage = msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
                count = sum(usage.get(key) or 0 for key in USED)
                # A line that counts nothing is an error note written in a reply's place, not a reply.
                if count:
                    used = count
    except OSError:
        return None, "the log could not be read"
    if used is None:
        return None, "no reply in the log"
    if window is None:
        window = 1_000_000
    return {"used": used, "window": window, "percent": used * 100 // window, "hand_over_at": HAND_OVER_AT}, None


def default_zone_file():
    """His zone's file: beside cap_check.py's seats folder, in the same machine-wide agentic-meta folder."""
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "agentic-meta", "his-time-zone.txt")


def his_time(zone_file, now=None):
    """His time from the zone in zone_file: ({time, day, zone, computer}, None), or (None, why it is not known).

    now is the one reading of the clock, in UTC; the default reads it here."""
    path = os.path.abspath(zone_file)
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            line = next((s.strip() for s in f if s.strip()), None)
    except OSError:
        line = None
    if line is None:
        return None, f"no zone in {path}; {ZONE_HINT}"
    m = ZONE.fullmatch(line)
    hours, minutes = (int(m.group(2) or 0), int(m.group(3) or 0)) if m else (0, 0)
    if not m or hours > 14 or minutes > 59:
        return None, f"{path} says \"{line}\"; {ZONE_HINT}"
    sign = -1 if m.group(1) == "-" else 1
    zone = "UTC" + (f"{m.group(1)}{hours}" if m.group(1) else "") + (f":{minutes:02d}" if minutes else "")
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    his = now.astimezone(datetime.timezone.utc) + sign * datetime.timedelta(hours=hours, minutes=minutes)
    return {"time": f"{his:%H:%M}", "day": f"{his:%a} {his.day} {his:%b}", "zone": zone,
            "computer": f"{now.astimezone():%H:%M}"}, None


def python_names(path=None):
    """The names to try for the Python: the skill's three, then each python3.N on the PATH, highest N first."""
    found = set()
    for folder in (os.environ.get("PATH", "") if path is None else path).split(os.pathsep):
        try:
            found.update(int(m.group(1)) for m in map(PYTHON_3N.fullmatch, os.listdir(folder or ".")) if m)
        except OSError:
            continue
    return PYTHONS + [[f"python3.{n}"] for n in sorted(found, reverse=True)]


def probe(command):
    """Run one try at a Python: (exit code, what it printed), or None if it could not run in time."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=PROBE_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.returncode, done.stdout + done.stderr


def find_python(names=None, which=shutil.which, run=probe):
    """The first name that runs, says Python 3, is not the Store's shortcut and imports pytest; None if none.

    which and run are the seams the tests use in place of the PATH and the Pythons on it."""
    for name in python_names() if names is None else names:
        where = which(name[0])
        if not where or "windowsapps" in (part.lower() for part in re.split(r"[\\/]", where)):
            continue
        version = run([where, *name[1:], "--version"])
        if not version or version[0] != 0 or not version[1].startswith("Python 3."):
            continue
        # -B so the try writes no bytecode.
        pytest = run([where, *name[1:], "-B", "-c", "import pytest"])
        if pytest and pytest[0] == 0:
            return " ".join(name)
    return None


def main():
    # UTF-8 whatever the console's code page, so the dash reaches a pipe or a file whole.
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Say what stage a project is at, read from its files.")
    parser.add_argument("folder", nargs="?", default=str(Path(__file__).resolve().parent.parent),
                        help="the project folder (default: the folder above tools/)")
    parser.add_argument("--json", action="store_true", help="print the answer as JSON")
    parser.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID"),
                        help="the session whose conversation to read (default: CLAUDE_CODE_SESSION_ID)")
    parser.add_argument("--logs", default=str(Path.home() / ".claude" / "projects"),
                        help="the folder the session logs sit under (default: ~/.claude/projects)")
    parser.add_argument("--window", type=int,
                        help="the conversation's size in tokens (default: read from the log)")
    parser.add_argument("--zone-file", default=default_zone_file(),
                        help="the file that holds his zone (default: his-time-zone.txt beside the seats folder)")
    parser.add_argument("--harvest", help="the harvest.py to run with --count (default: one beside this file, if any)")
    parser.add_argument("--template-home", help="the template's home to read the newest tag from (for tests)")
    parser.add_argument("--template-remote", default=TEMPLATE_REMOTE,
                        help="the address git ls-remote reads the newest tag from (for tests)")
    args = parser.parse_args()
    beside = Path(__file__).resolve().parent / "harvest.py"
    harvest = args.harvest or (beside if beside.is_file() else None)
    if args.window is not None and args.window < 1:
        parser.error("--window must be a whole number above 0")

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1
    if not (folder / "CLAUDE.md").is_file() and not (folder / "docs").is_dir():
        print(f"Not a project: {folder} has no CLAUDE.md and no docs/ folder.", file=sys.stderr)
        return 1

    stage, proof, action, run = stage_of(folder)
    desks = []
    for desk in desks_of(folder):
        d_stage, d_proof, d_action, d_run = stage_of(desk)
        desks.append({"desk": desk.name, "stage": d_stage, "proof": d_proof, "next": d_action, "run": d_run})

    his, his_why = his_time(args.zone_file)
    python = find_python()
    remote = has_remote(folder)
    talk, why = conversation(args.session, args.logs, args.window)
    waiting = lessons_waiting(folder)
    foundations = upgrade.status.foundations(folder)
    house = house_lessons(folder, harvest)
    template = template_state(folder, args.template_home, args.template_remote)

    if args.json:
        print(json.dumps({"stage": stage, "proof": proof, "next": action, "run": run, "desks": desks,
                          "his_time": his, "his_time_why": his_why, "python": python,
                          "remote": remote, "conversation": talk, "lessons": waiting, "template": template,
                          "foundations": foundations, "house_lessons": house}, indent=2))
    else:
        print(f"{stage}: {action}")
        for d in desks:
            print(f"desks/{d['desk']}: {d['stage']}: {d['next']}")
        if his:
            print(f"his time: {his['time']}, {his['day']} ({his['zone']}) · this computer {his['computer']}")
        else:
            print(f"his time: not known ({his_why})")
        print(f"python: {python or 'none found with pytest'}")
        if remote is None:
            print(REMOTE_NOT_READ)
        elif not remote:
            print(NO_REMOTE)
        if talk:
            print(f"conversation: {talk['percent']}% full ({talk['used']:,} of {talk['window']:,} tokens; "
                  f"hand over at {talk['hand_over_at']:,})")
        else:
            print(f"conversation: not read ({why})")
        if waiting is not None:
            line = (f"lessons: {waiting['waiting']} waiting, the oldest {waiting['oldest']}" if waiting["waiting"]
                    else "lessons: none waiting")
            print(line + (" · upgrade due" if waiting["due"] else ""))
        print(template_line(template))
        if house:
            print(house)
        print(foundations_line(foundations))
    return 0


if __name__ == "__main__":
    sys.exit(main())
