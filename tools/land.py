# land.py: land one checked piece of work on main, with one command.
#
# What it is for
#   When a card's branch has been built and checked, the master lands it.
#   This tool does the whole landing, in order:
#     1. The main checkout's fence: fence_check.py --main, here.
#     2. The card's fence on the branch: fence_check.py --card <card>, run
#        in the branch's own worktree (found by git worktree list).
#     3. The merge check: merge_check.py on the receipt the card's Touches
#        names, run in the branch's worktree.
#     4. git merge --squash <branch>, and one commit.
#     5. The merge line, with its undo, under "## Merges" in the newest
#        docs/runs/<n>/run.md, written by record.py and committed by naming
#        that file alone.
#     6. git push origin main.
#   Each check is the copy in the same folder as this tool, so it runs from
#   template/tools/ now and from tools/ after the adopt.
#   It refuses at the first failed check with nothing changed: it prints
#   REFUSE: <which check> — <its output> and exits 1, and git status and
#   git log read as before. A squash that conflicts is undone before it
#   refuses. If only the push fails, it says so, with the landed commit and
#   its undo, and exits 2. It prints LANDED: and exits 0 when all is done.
#
# Why the rule exists
#   In run 2 most of the master's actions were clerk work: the checks one
#   by one, the squash, the record line, the clock, the push. The same input
#   always gives the same right answer there, so it belongs on the lowest
#   rung that does it properly, a script, not the top model, which can
#   forget a step (design § 4, the cost ladder).
#
# How to run it (in the main checkout, from its top folder)
#   python template/tools/land.py --card <card-file> --branch <branch>
#   After the adopt, the same from tools/land.py.
#
# Python 3 standard library only. Its only network step is the push.

import argparse
import importlib.util
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("record_for_land", os.path.join(TOOLS, "record.py"))
record = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(record)


class Refuse(Exception):
    def __init__(self, check, output):
        super().__init__(f"{check} — {output.strip()}")


def run(cmd, cwd="."):
    """Run one command; return (exit code, what it printed)."""
    done = subprocess.run(cmd, cwd=cwd, capture_output=True)
    out = (done.stdout + done.stderr).decode("utf-8", errors="replace")
    return done.returncode, out.strip()


def git(*args, cwd="."):
    return run(["git", *args], cwd=cwd)


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
    return receipts[0]


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


def short_head():
    return git("rev-parse", "--short=7", "HEAD")[1]


def status():
    return git("status", "--porcelain=v1", "--untracked-files=all")[1]


def land(card_arg, branch):
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        raise Refuse("main checkout", "this folder is not inside a git working copy")
    card_path = os.path.abspath(card_arg)
    os.chdir(top)
    card = os.path.splitext(os.path.basename(card_path))[0]
    receipt = receipt_in_touches(card_path)
    folder = worktree_of(branch)
    try:
        run_file = record.newest_run()
    except record.Refuse as why:
        raise Refuse("record", str(why))

    # 1 to 3. The checks, each the copy beside this tool; the first that fails stops it.
    for check, name, args, cwd in [
        ("main checkout fence", "fence_check.py", ["--main"], top),
        ("card fence", "fence_check.py", ["--card", card_path], folder),
        ("merge check", "merge_check.py", [receipt], folder),
    ]:
        code, out = tool(name, *args, cwd=cwd)
        if code != 0:
            raise Refuse(check, out)

    # 4. The squash and its one commit. A squash that went wrong is undone,
    #    but only if it changed something: git refuses some merges untouched.
    before = git("rev-parse", "HEAD")[1]
    before_status = status()
    code, out = git("merge", "--squash", branch)
    if code == 0:
        code, out = git("commit", "-q", "-m", f"Land {card} (squash of {branch})")
    if code != 0:
        if status() != before_status:
            git("reset", "--merge")
        raise Refuse("squash", out)
    squash = short_head()

    # 5. The merge line, written by record.py, committed by naming that file.
    with open(run_file, "rb") as f:
        saved = f.read()
    code, out = tool("record.py", "--section", "Merges", "--file", run_file,
                     f"{card} · squash {squash} · undo: `git revert {squash}`")
    if code == 0:
        code, more = git("commit", "-q", "-m", f"Record: {card} landed, squash {squash}", "--", run_file)
        out = out + "\n" + more
    if code != 0:
        with open(run_file, "wb") as f:
            f.write(saved)
        git("reset", "-q", "--keep", before)
        raise Refuse("record", out)

    # 6. The push. If it alone fails, the landing stands and is said plainly.
    code, out = git("push", "origin", "main")
    if code != 0:
        print(f"PUSH FAILED: {card} is landed on main here as squash {squash}, with its merge "
              f"line in {run_file}, but git push origin main failed — {out}\n"
              f"Undo the landing with: git revert {squash}")
        return 2
    print(f"LANDED: {card} · squash {squash} · undo: git revert {squash} · "
          f"merge line in {run_file} · pushed to origin main")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Land one checked piece of work on main.")
    parser.add_argument("--card", required=True, help="the card file")
    parser.add_argument("--branch", required=True, help="the card's task branch")
    args = parser.parse_args(argv[1:])
    try:
        return land(args.card, args.branch)
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
