# size_check.py: refuse a rule file grown past its line limit.
#
# What it does
#   Reads the limits under "## Line limits" in STATUS.md, one line each,
#       - `<path>` · <n> lines
#   (paths relative to the folder holding STATUS.md), counts each file's
#   lines as wc -l does, and prints SIZE OK (exit 0), or one line per file
#   over its limit (exit 1):
#       REFUSE: <path> is <n> lines, <m> over its limit of <limit>
#   No STATUS.md, or none of its lines under "## Line limits": it prints
#   "no line limits here" and exits 0, so a project with no limits is as before.
#   land.py runs it in the branch's worktree before the merge.
#
# Why it exists
#   Long rule files are what agents drift from, and the template only ever
#   added; so what agents read stays small and a new line replaces an old one
#   (design of 17 Nov 2026, Part 5; his ruling 2 of 17 Nov 07:43).
#
# How to run it (from the project's top folder)
#   python tools/size_check.py [--root <folder>]
#   --root is the folder holding STATUS.md (default: template/ beside the
#   project's top, the top read by git from where it is run).
#   It never writes a file and touches no network. Python 3 standard library only.

import argparse
import os
import re
import subprocess
import sys

LIMIT = re.compile(r"^- `([^`]+)` · (\d+) lines\s*$")


def default_root():
    """template/ in the project's top folder (git's top of the folder it is run in, else that folder)."""
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        top = done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else os.getcwd()
    except OSError:
        top = os.getcwd()
    return os.path.join(top, "template")


def limits(root):
    """[(path, limit)] from root/STATUS.md's ## Line limits; [] when there is none."""
    path = os.path.join(root, "STATUS.md")
    if not os.path.isfile(path):
        return []
    found, inside = [], False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f.read().splitlines():
            if line.startswith("## "):
                inside = line.strip() == "## Line limits"
                continue
            m = LIMIT.match(line) if inside else None
            if m:
                found.append((m.group(1), int(m.group(2))))
    return found


def count(path):
    """The file's lines, as wc -l counts them (its newlines)."""
    with open(path, "rb") as f:
        return f.read().count(b"\n")


def check(root):
    """(exit code, the lines to print)."""
    found = limits(root)
    if not found:
        return 0, ["no line limits here"]
    over = []
    for name, limit in found:
        path = os.path.join(root, name)
        if not os.path.isfile(path):
            continue
        n = count(path)
        if n > limit:
            over.append(f"REFUSE: {name} is {n} lines, {n - limit} over its limit of {limit}")
    return (1, over) if over else (0, ["SIZE OK"])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Refuse a rule file grown past its line limit.")
    parser.add_argument("--root", default=None, help="the folder holding STATUS.md (default: template/ at the project's top)")
    args = parser.parse_args(argv)
    code, lines = check(args.root or default_root())
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
