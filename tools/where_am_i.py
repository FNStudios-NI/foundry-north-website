"""where_am_i.py -- says what stage a project is at, read from its files.

What it is for:
  Open any project and ask "where are we?". This tool looks at which files
  exist and answers in one line: the stage, then the one next thing to do.
  Then one line for each desk in desks/, with that desk's own stage.

Why the rule exists:
  In the old system a status was typed by hand, and it was wrong for three
  weeks. So here nothing is typed and nothing is stored. The files are the
  truth: if the file that proves a stage exists, the project is at that stage.
  This tool only reads. It never writes a file, and it touches no network.

How to run it:
  python tools/where_am_i.py                  (the project this tools/ sits in)
  python tools/where_am_i.py <project-folder>
  python tools/where_am_i.py <project-folder> --json   (the same, as JSON)
  python tools/where_am_i.py --session <id> --logs <folder> --window <n>
                                              (which conversation to read; see below)

After the stage line and the desk lines it says two more things, each read
fresh and never stored.

  no remote: the record is on this machine only
    Said when the project folder is a git repository with no remote, or is
    no git repository at all. With a remote, nothing is said. If git cannot
    be run it says "remote: not read (git could not be run)", never a guess.
    "git remote" is a local question: no network is touched.
    Why: a project's plan was once signed before anybody noticed the project
    had no online copy. A record on one machine is lost with that machine.

  conversation: 50% full (500,000 of 1,000,000 tokens)
    How full this session's conversation is, read from the session's own
    log. The count is the last main-thread reply's input_tokens +
    cache_read_input_tokens + cache_creation_input_tokens. A line marked
    isSidechain is a helper's and is left out. The session is --session
    <id>, or the environment's CLAUDE_CODE_SESSION_ID; its log is <id>.jsonl
    anywhere under --logs (default ~/.claude/projects). The window is
    --window <n>, or one million when the log's requestedModel ends [1m],
    or 200,000. The percent is rounded down.
    With no session id, no log, or no reply in the log, it says
    "conversation: not read (<why>)", and the exit code does not change.
    Why: Rhys's rule is that a master hands over when its conversation
    passes half its size. That needs a number to read, not a judgement by eye.

With --json these are "remote" (true, false, or null when not read) and
"conversation" (its used, window and percent, or null when not read).

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

One more fault, a stop until it is put right: docs/plan-signed.md,
docs/run.md or docs/review.md at the top of docs/. These are the old
single-run paths and are no longer read. Move them into docs/runs/1/ (the
review becomes review.html, a page). This is checked before the brief: a
project with run files is not new.

It refuses (one line, non-zero exit) when the folder is not a project:
no CLAUDE.md and no docs/ folder.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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
    """How full a session's conversation is: ({used, window, percent}, None), or (None, why it was not read)."""
    if not session:
        return None, "no session id"
    name = session + ".jsonl"
    log = next((Path(top) / name for top, _, files in os.walk(logs) if name in files), None)
    if log is None:
        return None, "no log for this session"
    used = model = None
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
                    used, model = count, e.get("requestedModel")
    except OSError:
        return None, "the log could not be read"
    if used is None:
        return None, "no reply in the log"
    if window is None:
        window = 1_000_000 if str(model or "").endswith("[1m]") else 200_000
    return {"used": used, "window": window, "percent": used * 100 // window}, None


def main():
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
    args = parser.parse_args()
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

    remote = has_remote(folder)
    talk, why = conversation(args.session, args.logs, args.window)

    if args.json:
        print(json.dumps({"stage": stage, "proof": proof, "next": action, "run": run, "desks": desks,
                          "remote": remote, "conversation": talk}, indent=2))
    else:
        print(f"{stage}: {action}")
        for d in desks:
            print(f"desks/{d['desk']}: {d['stage']}: {d['next']}")
        if remote is None:
            print(REMOTE_NOT_READ)
        elif not remote:
            print(NO_REMOTE)
        if talk:
            print(f"conversation: {talk['percent']}% full ({talk['used']:,} of {talk['window']:,} tokens)")
        else:
            print(f"conversation: not read ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
