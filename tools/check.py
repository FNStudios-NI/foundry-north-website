# check.py: the checker's tool. Runs a card's gate on a clean copy of the
# committed branch, and writes the Checker run block's facts itself.
#
# What it holds, and why
#   Checkers typed "Commit:" and "Exit code:" by hand, and ran the gate in a
#   worktree that held files the commit did not, so a pass could rest on a
#   file nobody committed (the 0.9.0 design, Part 1; lessons L113, L122,
#   L127). A tool does the mechanical half, so there is nothing to mistype:
#   it reads the branch's committed head, clones exactly that commit into
#   the checker's scratch (no untracked file, no change waiting), and runs
#   the card's gate there through bash, with S set to the scratch.
#   The gate is read from the card, never typed: every backticked span in
#   the card's "## Gate" section followed by " → " is one command, run in
#   order. A card whose gate yields no command is refused.
#
# What it writes, and what it leaves to the checker
#   It appends four lines to the receipt, and writes no other file:
#     ## Checker run <yyyy-mm-dd> — <who>
#     Commit: <the full commit id>
#     Exit code: <0, or the first command's that was not 0>
#     From a clean copy: <the copy's path> · <n> commands · exit codes <e1>, <e2>, …
#   The checker writes only its judgement under them: "Shown failing:" (the
#   ablation it ran), "Scope:" (is anything in this diff not asked for by
#   the card?), "Verdict: PASS" or "Verdict: FAIL", and "Why:". This tool
#   never writes a verdict, commits nothing and pushes nothing. The copy is
#   removed by its exact path at the end (--keep leaves it).
#
# How to run it
#   In the branch's worktree, from its top folder:
#     python tools/check.py <receipt> --card <card> --who "<model>, own session" --scratch <folder>
#   It prints each command's output as it runs, then the four lines. It
#   exits 0 when every command exited 0, 1 otherwise.
#     python tools/check.py <receipt> --card <card> --dry
#   prints the commands it found in the card's gate and runs nothing.
#
# Python 3 standard library only, with git and bash.

import argparse
import datetime
import os
import re
import shutil
import stat
import subprocess
import sys

GATE_HEADING = re.compile(r"^##\s+Gate\b")
ANY_HEADING = re.compile(r"^##\s")


class Refuse(Exception):
    pass


def gate_commands(card):
    """Every backticked span in the card's ## Gate section followed by ' → '."""
    try:
        with open(card, encoding="utf-8") as f:
            lines = f.read().lstrip("﻿").splitlines()
    except OSError:
        raise Refuse(f"no card at {card}")
    section, inside = [], False
    for line in lines:
        if GATE_HEADING.match(line):
            inside = True
            continue
        if inside and ANY_HEADING.match(line):
            break
        if inside:
            section.append(line)
    # Split on backticks: the odd parts are the spans, so spans pair up as
    # Markdown pairs them, and an expected output like `OK` is never read
    # as the start of a command.
    parts = "\n".join(section).split("`")
    commands = [parts[i] for i in range(1, len(parts) - 1, 2)
                if parts[i + 1].startswith(" → ")]
    if not commands:
        raise Refuse(f"{card} has no gate check.py can read")
    return commands


def find_bash():
    """Git's own bash on Windows (a bare 'bash' there may be WSL's); else bash."""
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            folder = os.path.dirname(os.path.realpath(git))
            for _ in range(3):
                candidate = os.path.join(folder, "bin", "bash.exe")
                if os.path.isfile(candidate):
                    return candidate
                folder = os.path.dirname(folder)
    bash = shutil.which("bash")
    if not bash:
        raise Refuse("bash is not installed or not on the PATH")
    return bash


def git(*args, cwd=None):
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    return done.returncode, done.stdout.decode("utf-8", errors="replace").strip()


def remove(path):
    """Remove the copy by its exact path; git's read-only files made writable first."""
    def writable(func, target, _):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onerror=writable)


def append(receipt, lines):
    """Append lines to the receipt, in its own line endings; nothing else changes."""
    with open(receipt, "rb") as f:
        data = f.read()
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    tail = b"" if not data or data.endswith(b"\n") else newline
    text = newline.join(line.encode("utf-8") for line in lines) + newline
    with open(receipt, "ab") as f:
        f.write(tail + newline + text)


def run(args):
    commands = gate_commands(args.card)
    if args.dry:
        print(f"{len(commands)} gate command{'s' if len(commands) != 1 else ''} in {args.card}:")
        for i, command in enumerate(commands, 1):
            print(f"  {i}. {command}")
        return 0
    if not args.who or not args.scratch:
        raise Refuse("name --who \"<model>, own session\" and --scratch <folder>")
    if not os.path.isfile(args.receipt):
        raise Refuse(f"no receipt file at {args.receipt}")
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        raise Refuse("this folder is not inside a git working copy")
    code, commit = git("rev-parse", "--verify", "HEAD^{commit}")
    if code != 0:
        raise Refuse("this branch has no commit to check")
    bash = find_bash()

    scratch = os.path.abspath(args.scratch).replace("\\", "/")
    os.makedirs(scratch, exist_ok=True)
    copy = f"{scratch}/clean-{commit[:12]}"
    if os.path.exists(copy):
        raise Refuse(f"{copy} is already there; it is not this run's to remove")
    code, out = git("clone", "--quiet", "--no-checkout", "--no-hardlinks", top, copy)
    if code == 0:
        code, out = git("-C", copy, "checkout", "--quiet", "--detach", commit)
    if code != 0:
        if os.path.exists(copy):
            remove(copy)
        raise Refuse(f"git could not make a clean copy of {commit}: {out}")

    env = dict(os.environ, S=scratch)
    codes = []
    try:
        for i, command in enumerate(commands, 1):
            print(f"== {i}/{len(commands)} $ {command}", flush=True)
            done = subprocess.run([bash, "-c", command], cwd=copy, env=env)
            print(f"== exit code {done.returncode}", flush=True)
            codes.append(done.returncode)
    finally:
        if not args.keep:
            remove(copy)

    first_bad = next((c for c in codes if c != 0), 0)
    today = datetime.date.today().isoformat()
    block = [
        f"## Checker run {today} — {args.who}",
        f"Commit: {commit}",
        f"Exit code: {first_bad}",
        f"From a clean copy: {copy} · {len(codes)} command{'s' if len(codes) != 1 else ''} · "
        f"exit codes {', '.join(str(c) for c in codes)}",
    ]
    append(args.receipt, block)
    print()
    print("\n".join(block))
    print(f"(appended to {args.receipt}; under them write Shown failing:, Scope:, Verdict: and Why:)")
    return 0 if first_bad == 0 else 1


def main(argv):
    parser = argparse.ArgumentParser(description="Run a card's gate on a clean copy of the committed branch.")
    parser.add_argument("receipt")
    parser.add_argument("--card", required=True)
    parser.add_argument("--who", help='who checks, like "Opus 5.5, own session"')
    parser.add_argument("--scratch", help="the checker's own scratch folder; the copy is made in it")
    parser.add_argument("--keep", action="store_true", help="leave the copy in the scratch")
    parser.add_argument("--dry", action="store_true", help="print the gate's commands and run nothing")
    args = parser.parse_args(argv[1:])
    # A Windows console may not hold every character a card's gate holds.
    sys.stdout.reconfigure(errors="replace")
    try:
        return run(args)
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
