# merge_check.py: may this piece of work be merged?
#
# What it is for
#   Before the master merges a branch, this reads the branch's receipt and
#   the branch's git history and says ALLOW or REFUSE, with one reason.
#   It only looks. It never merges, commits or writes anything, and it
#   never touches the internet.
#
# What it checks, in order (the first one that fails is the reason given)
#   1. The receipt file is there and is committed on this branch.
#   2. Its first line starts with DONE.
#   3. It has a "## Checker run" block that names a commit and exit code 0,
#      and holds one verdict line, and that line says PASS. Written
#      "Verdict: PASS" or "Verdict: FAIL"; bold and a full stop after the
#      word read the same. No verdict line, another word, or two verdict
#      lines in the block, and it is refused: a verdict that cannot be read
#      is not a pass. The two-line refusal says how to write it: exactly one
#      line starts with Verdict, and any summary goes under "Why:".
#   4. That commit is real, and is part of this branch's history.
#   5. Nothing but the receipt has changed since that commit: not in later
#      commits, not in files waiting to be committed, not in new files.
#      A file in the working copy is judged by its contents against the
#      commit, as "git diff --quiet" does, never by its working-copy state:
#      a file rewritten with the same contents has not changed.
#
# Why the rule exists
#   On 20 Sept five results were passed with a number copied from the
#   worker. A check that names no real commit proves nothing, and work
#   changed after its check has not been checked. So a merge needs a
#   checker's own run, at a real commit, with nothing changed since.
#   The verdict is read as well as the exit code because on 6 Oct the
#   run-lines work was merged on a checker's FAIL: its gate had passed, so
#   the exit code was 0, and this tool read only that. It was undone.
#   The two-line refusal says how to write a verdict because on 7 Oct at
#   06:21 a checker wrote "Verdict: PASS" and then a summary line
#   "Verdict: PASS — ...", and the refusal named the fault but not the fix
#   (run 2's record, docs/runs/2/run.md, line 87).
#   Contents are judged, not the working-copy state, because on 7 Oct at
#   11:28 a checker's ablation put a committed file back byte for byte:
#   git status still listed it as changed, "git diff --quiet" said it was
#   the same, and a checked PASS was refused (run 2's record, line 134).
#
# How to run it
#   Inside the branch's working copy (its worktree folder):
#     python template/tools/merge_check.py docs/cards/receipts/<card>-close.md
#   It prints one line and exits 0 for ALLOW, 1 for REFUSE.
#
# Python 3 standard library only. It asks git for the facts.

import os
import re
import subprocess
import sys

# Stops git from tidying its own index while it answers, so this tool
# writes nothing at all, not even git's housekeeping.
GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

CHECKER_HEADING = re.compile(r"^##\s+Checker run\b")
ANY_HEADING = re.compile(r"^##\s")
COMMIT_LINE = re.compile(r"^\s*(?:[-*]\s*)?Commit:\s*`?([0-9a-fA-F]{7,40})`?\s*$")
EXIT_LINE = re.compile(r"^\s*(?:[-*]\s*)?Exit code:\s*`?(-?\d+)`?\s*$")
# Any line that starts "Verdict:", bold or not, counts as a verdict line.
# The word must be PASS or FAIL, then nothing, a full stop, the bold's
# closing stars, or a space and more words ("Verdict: FAIL. The gate...").
VERDICT_LINE = re.compile(r"^\s*(?:[-*]\s+)?\**\s*Verdict\s*:", re.IGNORECASE)
VERDICT_WORD = re.compile(r"^\s*(?:[-*]\s+)?\**\s*Verdict:\s*\**\s*(PASS|FAIL)(?:[.*\s]|$)")


class Refuse(Exception):
    pass


def git(*args):
    """Run one git command; return (exit code, output text)."""
    try:
        done = subprocess.run(
            ["git", *args], capture_output=True, env=GIT_ENV,
        )
    except FileNotFoundError:
        raise Refuse("git is not installed or not on the PATH")
    return done.returncode, done.stdout.decode("utf-8", errors="replace")


def nul_list(text):
    return [p for p in text.split("\0") if p]


def check(receipt_arg):
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        raise Refuse("this folder is not inside a git working copy")
    top = top.strip()

    # 1. The receipt is there, and committed on this branch.
    if not os.path.isfile(receipt_arg):
        raise Refuse(f"no receipt file at {receipt_arg}")
    code, name = git("ls-files", "--full-name", "-z", "--", receipt_arg)
    names = nul_list(name)
    if code != 0 or not names:
        raise Refuse(f"the receipt {receipt_arg} has never been committed")
    receipt = names[0]
    code, text = git("show", f"HEAD:{receipt}")
    if code != 0:
        raise Refuse(f"the receipt {receipt} is not committed on this branch")
    code, _ = git("-C", top, "diff", "--quiet", "HEAD", "--", receipt)
    if code != 0:
        raise Refuse(f"the receipt {receipt} has changes that are not committed")

    # 2. Its first line starts with DONE.
    lines = text.lstrip("﻿").splitlines()
    first = lines[0] if lines else ""
    if not first.startswith("DONE"):
        raise Refuse(f"the receipt's first line does not start with DONE: {first[:60]}")

    # 3. A Checker run block naming a commit, exit code 0 and Verdict: PASS.
    #    If there is more than one, the last one counts.
    starts = [i for i, line in enumerate(lines) if CHECKER_HEADING.match(line)]
    if not starts:
        raise Refuse("the receipt has no '## Checker run' block")
    block = []
    for line in lines[starts[-1] + 1:]:
        if ANY_HEADING.match(line):
            break
        block.append(line)
    named = [m.group(1) for m in map(COMMIT_LINE.match, block) if m]
    exits = [m.group(1) for m in map(EXIT_LINE.match, block) if m]
    if not named:
        raise Refuse("the Checker run block has no 'Commit: <commit>' line")
    if not exits:
        raise Refuse("the Checker run block has no 'Exit code: <number>' line")
    if int(exits[0]) != 0:
        raise Refuse(f"the checker's run ended with exit code {exits[0]}, not 0")
    verdicts = [line for line in block if VERDICT_LINE.match(line)]
    if not verdicts:
        raise Refuse("the Checker run block has no 'Verdict: PASS' or 'Verdict: FAIL' line")
    if len(verdicts) > 1:
        raise Refuse(f"the Checker run block has {len(verdicts)} verdict lines, not one; "
                     "exactly one line starts with Verdict, written 'Verdict: PASS' or "
                     "'Verdict: FAIL' alone, and any summary goes under 'Why:'")
    word = VERDICT_WORD.match(verdicts[0])
    if not word:
        raise Refuse(f"the checker's verdict cannot be read as PASS or FAIL: {verdicts[0].strip()[:60]}")
    if word.group(1) != "PASS":
        raise Refuse("the checker's verdict is FAIL")

    # 4. That commit is real, and part of this branch's history.
    code, full = git("rev-parse", "--verify", "--quiet", f"{named[0]}^{{commit}}")
    if code != 0:
        raise Refuse(f"the checked commit {named[0]} does not exist in this repo")
    full = full.strip()
    code, _ = git("merge-base", "--is-ancestor", full, "HEAD")
    if code != 0:
        raise Refuse(f"the checked commit {named[0]} is not in this branch's history")

    # 5. Nothing but the receipt has changed since that commit.
    code, out = git("diff", "--name-only", "--no-renames", "-z", full, "HEAD")
    if code != 0:
        raise Refuse("git could not compare the checked commit with this branch")
    for path in nul_list(out):
        if path != receipt:
            raise Refuse(f"{path} was changed and committed after the checked commit")
    code, out = git(
        "-C", top, "status", "--porcelain=v1", "-z",
        "--untracked-files=all", "--no-renames",
    )
    if code != 0:
        raise Refuse("git could not read the working copy's status")
    for entry in nul_list(out):
        path = entry[3:]
        if path == receipt:
            continue
        # A tracked file is judged by its contents: git status lists a file
        # whose size changed, as when the committed bytes are written back
        # over a CRLF checkout; git diff --quiet compares the contents.
        if not entry.startswith("??"):
            code, _ = git("-C", top, "diff", "--quiet", "HEAD", "--", path)
            if code == 0:
                continue
        raise Refuse(f"{path} is new or changed in the working copy and not committed")

    return (f"{receipt} is DONE, checked at {full[:7]} with exit code 0, "
            f"and nothing but the receipt has changed since")


def main(argv):
    if len(argv) != 2:
        print("REFUSE: name one receipt file, like: "
              "python template/tools/merge_check.py docs/cards/receipts/<card>-close.md")
        return 1
    try:
        reason = check(argv[1])
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1
    except Exception as err:  # a broken check must never read as a pass
        print(f"REFUSE: the check itself failed ({type(err).__name__}: {err})")
        return 1
    print(f"ALLOW: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
