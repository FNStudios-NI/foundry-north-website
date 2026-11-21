# land.py: land one checked piece of work on main, with one command.
#
# What it is for
#   When a card's branch has been built and checked, the master lands it.
#   This tool does the whole landing, in order:
#     1. The main checkout's fence: fence_check.py --main --card <card>, here.
#     2. The card's fence on the branch: fence_check.py --card <card>, run
#        in the branch's own worktree (found by git worktree list).
#     2a. The size check: size_check.py, run in the branch's worktree; a file
#        it takes over its line limit stops the landing. Why: what agents read
#        stays small (design 0.9.0, Part 5; his ruling 2 of 17 Nov 07:43).
#     3. The merge check: merge_check.py on the receipt the card's Touches
#        names (its own, <card>-close.md, when it names more than one),
#        run in the branch's worktree. Before it, the receipt's Run lines
#        are stamped under its Card: line, one per session log in the
#        harness's folder for the worktree (--logs, ~/.claude/projects),
#            Run: <model> · <effort> · <start> · <end> · <n> turns
#        or "Run: no session log found", and the receipt committed alone
#        on the branch. Why: Run lines typed from memory drifted (design
#        0.9.0, Part 1); a tool has nothing to misremember.
#     4. git merge --squash <branch>, and one commit: its first line, then
#        the whole message of the branch's last commit that changes more than
#        the receipt. Why: an adopt's reasons were lost from main's log (L033).
#     5. The merge line, with its undo, under "## Merges" in the newest
#        docs/runs/<n>/run.md (record.py opens it from the blank if it is
#        not there yet), written by record.py and committed by naming
#        that file alone.
#     6. git push origin main.
#   Before all, a card whose Branch line names a run that a decisions file
#   closes ("Run <n> closed") is refused: its line would land in a closed
#   run's record (engine-motion-graphics' runs 4 and 5; design Part 1).
#   Each check is the copy in the same folder as this tool, so it runs from
#   template/tools/ now and from tools/ after the adopt.
#   It refuses at the first failed check with nothing changed: it prints
#   REFUSE: <which check> — <its output> and exits 1, and git status and
#   git log read as before. A squash that conflicts is undone before it
#   refuses. If only the push fails, it says so, with the landed commit and
#   its undo, and exits 2. It prints LANDED: and exits 0 when all is done.
#   An untracked file outside the record that the card does not touch is a
#   stray: it does not stop the landing, and it is named on one line,
#   STRAY (left as found, not landed): ..., after LANDED: or PUSH FAILED:.
#   It is never added, moved, deleted or committed. What still stops the
#   landing: a change to a tracked file outside the record (modified,
#   deleted or staged), and an untracked file at a path the card's Touches
#   names or under a folder it names, since the squash would meet it.
#
#   Strays pass because in run 5 an untracked specs-for-manager/, left in
#   the main checkout, stopped every landing until it was dealt with by
#   hand (docs/runs/5/run.md, Unforeseen key points 15:13), and a folder
#   with two writers meets the same (run 6 lessons, row 25). The squash
#   and the record commit take only what they name, so a stray is never
#   landed; it is said, so the master still sees it.
#
# Why the rule exists
#   In run 2 most of the master's actions were clerk work: the checks one
#   by one, the squash, the record line, the clock, the push. The same input
#   always gives the same right answer there, so it belongs on the lowest
#   rung that does it properly, a script, not the top model, which can
#   forget a step (design § 4, the cost ladder).
#
# How to run it (in the main checkout, from its top folder)
#   python template/tools/land.py --card <card-file> --branch <branch> [--logs <folder>]
#   After the adopt, the same from tools/land.py.
#
# Python 3 standard library only. Its only network step is the push.

import argparse
import datetime as dt
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
# A heading in a decisions file that closes a run, as where_am_i.py reads it.
CLOSED = re.compile(r"## .*\bRun (\d+) closed\b", re.IGNORECASE)

_spec = importlib.util.spec_from_file_location("record_for_land", os.path.join(TOOLS, "record.py"))
record = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(record)


class Refuse(Exception):
    def __init__(self, check, output):
        super().__init__(f"{check} — {output.strip()}")


def run(cmd, cwd=".", stdin=None):
    """Run one command; return (exit code, what it printed)."""
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, input=stdin)
    out = (done.stdout + done.stderr).decode("utf-8", errors="replace")
    return done.returncode, out.strip()


def git(*args, cwd=".", stdin=None):
    return run(["git", *args], cwd=cwd, stdin=stdin)


def tool(name, *args, cwd="."):
    return run([sys.executable, "-B", os.path.join(TOOLS, name), *args], cwd=cwd)


def receipt_in_touches(card_path):
    """The receipt (a path ending -close.md) the card's ## Touches names."""
    try:
        with open(card_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        raise Refuse("card", f"the card {card_path} could not be read")
    section = None
    for line in lines:
        if re.match(r"^##\s+Touches\s*$", line):
            section = []
        elif section is not None and re.match(r"^#{1,2}\s", line):
            break
        elif section is not None:
            section.append(line)
    receipts = [p.strip() for p in re.findall(r"`([^`]+)`", "\n".join(section or []))
                if p.strip().endswith("-close.md")]
    if not receipts:
        raise Refuse("card", f"the card {card_path} names no receipt (a -close.md path) under ## Touches")
    own = os.path.splitext(os.path.basename(card_path))[0] + "-close.md"
    mine = [p for p in receipts if os.path.basename(p) == own]
    if mine:
        return mine[0]
    if len(receipts) > 1:
        raise Refuse("card", f"the card {card_path} names {len(receipts)} receipts under ## Touches and none "
                             f"is its own ({own}): {' · '.join(receipts)}")
    return receipts[0]


def closed_run(card_path):
    """The run the card's Branch line names, when a decisions file says it
    is closed (a 'Run <n> closed' heading, as where_am_i.py reads it)."""
    with open(card_path, encoding="utf-8", errors="replace") as f:
        line = next((l for l in f if l.startswith("Branch:")), "")
    named = re.search(r"\brun (\d+)\b", line)
    if not named:
        return None
    for path in glob.glob(os.path.join("docs", "decisions*.md")):
        with open(path, encoding="utf-8", errors="replace") as f:
            for heading in f:
                closed = CLOSED.match(heading)
                if closed and int(closed.group(1)) == int(named.group(1)):
                    return named.group(1)
    return None


def session_runs(logs, folder):
    """One 'Run:' line per session log in the harness's project folder for
    the worktree (its path with each sign but letters and digits as '-')."""
    found = os.path.join(logs, re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(folder)))
    runs = []
    for path in sorted(glob.glob(os.path.join(glob.escape(found), "*.jsonl"))):
        models, effort, stamps, turns = [], None, [], 0
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(e, dict):
                    continue
                msg = e.get("message") if isinstance(e.get("message"), dict) else {}
                if e.get("timestamp"):
                    try:
                        stamps.append(dt.datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")))
                    except ValueError:
                        pass
                if e.get("type") == "assistant":
                    if msg.get("model") and msg["model"] not in models and msg["model"] != "<synthetic>":
                        models.append(msg["model"])
                    effort = effort or e.get("effort")
                if e.get("type") == "user":
                    c = msg.get("content")
                    tool_result = isinstance(c, list) and any(
                        isinstance(x, dict) and x.get("type") == "tool_result" for x in c)
                    turns += bool(c) and not tool_result
        if stamps:
            local = sorted(s.astimezone() if s.tzinfo else s for s in stamps)
            runs.append((local[0], f"Run: {', '.join(models) or 'model unknown'} · {effort or 'effort unknown'} · "
                                   f"{local[0]:%Y-%m-%d %H:%M} · {local[-1]:%Y-%m-%d %H:%M} · {turns} turns"))
    return [line for _, line in sorted(runs)] or ["Run: no session log found"]


def stamp_runs(folder, receipt, logs):
    """Write the Run lines under the receipt's Card: line (or its title, if it
    has no Card: line), in place of any there, and commit the receipt alone
    on the branch."""
    path = os.path.join(folder, receipt)
    if not os.path.isfile(path):
        return  # the merge check names it
    with open(path, "rb") as f:
        saved = f.read()
    content = saved.decode("utf-8", errors="replace")
    lines = content.splitlines()
    head = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    lines = [l for i, l in enumerate(lines) if i >= head or not l.startswith("Run: ")]
    head = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    anchor = next((i for i in range(head) if lines[i].startswith("Card:")), None)
    if anchor is None:
        anchor = next((i for i in range(head) if lines[i].startswith("# ")), None)
    if anchor is None:
        return
    lines[anchor + 1:anchor + 1] = session_runs(logs, folder)
    newline = "\r\n" if "\r\n" in content else "\n"
    out = newline.join(lines) + (newline if content.endswith(("\n", "\r")) else "")
    if out.encode("utf-8") == saved:
        return
    with open(path, "wb") as f:
        f.write(out.encode("utf-8"))
    code, said = git("add", "--", receipt, cwd=folder)
    if code == 0:
        code, said = git("commit", "-q", "-m", "Receipt: Run lines stamped by land.py", "--", receipt, cwd=folder)
    if code != 0:
        with open(path, "wb") as f:
            f.write(saved)
        git("reset", "-q", "--", receipt, cwd=folder)
        raise Refuse("run lines", said)


def worktree_of(branch):
    """The folder of the worktree that has this branch checked out."""
    code, out = git("worktree", "list", "--porcelain")
    if code != 0:
        raise Refuse("worktree", out)
    folder = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            folder = line[len("worktree "):]
        elif line == f"branch refs/heads/{branch}":
            return folder
    raise Refuse("worktree", f"no worktree has the branch {branch} checked out")


def squash_message(card, branch, receipt):
    """The squash's first line, then the whole message of the branch's last
    commit that changes a file other than the receipt, when it has one."""
    first = f"Land {card} (squash of {branch})"
    code, commits = git("rev-list", f"HEAD..{branch}")
    if code != 0:
        raise Refuse("squash", commits)
    for commit in commits.split():
        code, files = git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", commit)
        if code != 0:
            raise Refuse("squash", files)
        if {f for f in files.split("\0") if f} - {receipt}:
            code, message = git("log", "-1", "--format=%B", commit)
            if code != 0:
                raise Refuse("squash", message)
            return f"{first}\n\n{message}"
    return first


def short_head():
    return git("rev-parse", "--short=7", "HEAD")[1]


def status():
    return git("status", "--porcelain=v1", "--untracked-files=all")[1]


def land(card_arg, branch, logs):
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        raise Refuse("main checkout", "this folder is not inside a git working copy")
    card_path = os.path.abspath(card_arg)
    os.chdir(top)
    card = os.path.splitext(os.path.basename(card_path))[0]
    receipt = receipt_in_touches(card_path)
    closed = closed_run(card_path)
    if closed:
        raise Refuse("record", f"run {closed} is closed; land into the open run's record")
    folder = worktree_of(branch)
    try:
        run_file = record.newest_run()
    except record.Refuse as why:
        raise Refuse("record", str(why))

    # 1 to 3. The checks, each the copy beside this tool; the first that fails
    # stops it. The receipt's Run lines are stamped before the merge check.
    strays = []
    for check, name, args, cwd in [
        ("main checkout fence", "fence_check.py", ["--main", "--card", card_path], top),
        ("card fence", "fence_check.py", ["--card", card_path], folder),
        ("size check", "size_check.py", [], folder),
        ("merge check", "merge_check.py", [receipt], folder),
    ]:
        if check == "merge check":
            stamp_runs(folder, receipt, logs)
        code, out = tool(name, *args, cwd=cwd)
        if code != 0:
            raise Refuse(check, out)
        if check == "main checkout fence":
            strays = [line[len("STRAY: "):] for line in out.splitlines() if line.startswith("STRAY: ")]
    stray_line = ("\nSTRAY (left as found, not landed): " + " · ".join(strays)) if strays else ""

    # 4. The squash and its one commit. A squash that went wrong is undone,
    #    but only if it changed something: git refuses some merges untouched.
    before = git("rev-parse", "HEAD")[1]
    before_status = status()
    message = squash_message(card, branch, receipt)
    code, out = git("merge", "--squash", branch)
    if code == 0:
        code, out = git("commit", "-q", "-F", "-", stdin=message.encode("utf-8"))
    if code != 0:
        if status() != before_status:
            git("reset", "--merge")
        raise Refuse("squash", out)
    squash = short_head()

    # 5. The merge line, written by record.py, committed by naming that file.
    saved = None  # a run with no record yet: record.py opens it from the blank
    if os.path.isfile(run_file):
        with open(run_file, "rb") as f:
            saved = f.read()
    code, out = tool("record.py", "--section", "Merges", "--file", run_file,
                     f"{card} · squash {squash} · undo: `git revert {squash}`")
    if code == 0:
        code, more = git("add", "--", run_file)
        if code == 0:
            code, more = git("commit", "-q", "-m", f"Record: {card} landed, squash {squash}", "--", run_file)
        out = out + "\n" + more
    if code != 0:
        git("reset", "-q", "--", run_file)
        if saved is None:
            if os.path.isfile(run_file):
                os.remove(run_file)
        else:
            with open(run_file, "wb") as f:
                f.write(saved)
        git("reset", "-q", "--keep", before)
        raise Refuse("record", out)

    # 6. The push. If it alone fails, the landing stands and is said plainly.
    code, out = git("push", "origin", "main")
    if code != 0:
        print(f"PUSH FAILED: {card} is landed on main here as squash {squash}, with its merge "
              f"line in {run_file}, but git push origin main failed — {out}\n"
              f"Undo the landing with: git revert {squash}{stray_line}")
        return 2
    print(f"LANDED: {card} · squash {squash} · undo: git revert {squash} · "
          f"merge line in {run_file} · pushed to origin main{stray_line}")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Land one checked piece of work on main.")
    parser.add_argument("--card", required=True, help="the card file")
    parser.add_argument("--branch", required=True, help="the card's task branch")
    parser.add_argument("--logs", default=os.path.join(os.path.expanduser("~"), ".claude", "projects"),
                        help="the harness's session logs (default ~/.claude/projects)")
    args = parser.parse_args(argv[1:])
    try:
        return land(args.card, args.branch, args.logs)
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
