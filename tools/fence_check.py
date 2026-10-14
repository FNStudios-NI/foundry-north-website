# fence_check.py - says whether a working copy has stayed inside its fence.
#
# What it is for:
#   Every card names, under "## Touches", the only files its worker may
#   change. This tool checks that the worker kept to that list. It has two
#   rules:
#     1. The card's fence (--card). Every file changed against the base
#        branch, committed or not, must be named in the card's Touches. A
#        path in backticks that ends in / is a folder and covers everything
#        under it. Paths are read from the top of the repo.
#        A file named in the Touches of any card in the same folder whose
#        "Branch:" line names the same branch is inside too, so a continue
#        card's fence covers its whole branch.
#     2. The main checkout's fence (--main). In the main checkout, any
#        uncommitted change outside the record is outside the fence. The
#        record is docs/ and desks/<any desk>/docs/.
#   It prints INSIDE: ... and exits 0, or OUTSIDE: followed by each
#   offending file on its own line, and exits 1.
#
# Why the rules exist:
#   The desks are folders in one repo, so the card's fence is the only thing
#   keeping one desk's worker out of another desk's files.
#   The main checkout belongs to the master, for the record and checked
#   merges only. All building happens in a worktree, so two writers never
#   share one copy. Run in a worktree, --main says so and passes.
#   A card with no Touches section is refused, not passed: a fence nobody
#   wrote down cannot be kept.
#   The cards on one branch share one fence because on 7 Oct at 06:16 the
#   road desk's two continue cards each named only their own files, and
#   this tool refused both checked merges until their Touches were widened
#   (run 2's record, docs/runs/2/run.md, lines 81 and 220). A card on
#   another branch adds nothing.
#
# How to run it (from inside the working copy you want to check):
#   python template/tools/fence_check.py --card <card-file>                  (checks against main)
#   python template/tools/fence_check.py --card <card-file> --base <branch>  (checks against another branch)
#   python template/tools/fence_check.py --main                              (checks the main checkout)
#
# It only reads: it asks git for the facts and changes nothing.
# Python 3, standard library only. No network.

import argparse
import os
import re
import subprocess
import sys

RECORD = "docs/ and desks/*/docs/"


def refuse(reason):
    print("Refused: " + reason)
    sys.exit(1)


def git(*args):
    """Run a git command that only reads, and return what it printed."""
    # --no-optional-locks stops git status refreshing the index file, so the
    # tool never writes, even to git's own files.
    result = subprocess.run(["git", "--no-optional-locks"] + list(args),
                            capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="replace")


def nul_list(text):
    return [item for item in text.split("\0") if item]


def uncommitted_files():
    """Every file with a change not yet committed: staged, unstaged or new."""
    out = git("status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all")
    if out is None:
        refuse("git could not read the state of this working copy.")
    # Each entry is two status letters, a space, then the path.
    return {entry[3:] for entry in nul_list(out)}


def touches_in(lines):
    """The paths in backticks under a card's ## Touches heading, or None if it has none."""
    section = None
    for line in lines:
        if re.match(r"^##\s+Touches\s*$", line):
            section = []
        elif section is not None and re.match(r"^#{1,2}\s", line):
            break
        elif section is not None:
            section.append(line)
    if section is None:
        return None
    paths = []
    for path in re.findall(r"`([^`]+)`", "\n".join(section)):
        path = path.strip().replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        if path:
            paths.append(path)
    return paths


def branch_of(lines):
    """The branch a card's "Branch:" line names, or None."""
    for line in lines:
        match = re.match(r"^\s*Branch:\s*`([^`]+)`", line)
        if match:
            return match.group(1).strip()
    return None


def read_touches(card_path):
    """The card's Touches paths, and the branch it names."""
    try:
        with open(card_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        refuse('the card "%s" could not be read.' % card_path)
    except UnicodeDecodeError:
        refuse('the card "%s" is not saved as UTF-8 text.' % card_path)
    paths = touches_in(lines)
    if paths is None:
        refuse('the card "%s" has no "## Touches" section, so it has no fence to check.' % card_path)
    if not paths:
        refuse('the card "%s" names no paths in backticks under "## Touches".' % card_path)
    return paths, branch_of(lines)


def branch_touches(card_path, branch):
    """The Touches of every other card in the card's folder on the same branch."""
    folder = os.path.dirname(card_path)
    cards, paths = 0, []
    for name in sorted(os.listdir(folder)):
        other = os.path.join(folder, name)
        if (not name.endswith(".md") or not os.path.isfile(other)
                or os.path.normcase(other) == os.path.normcase(card_path)):
            continue
        try:
            with open(other, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        if branch_of(lines) == branch and touches_in(lines):
            cards += 1
            paths += touches_in(lines)
    return cards, paths


def inside_touches(path, touches):
    for allowed in touches:
        if path == allowed or (allowed.endswith("/") and path.startswith(allowed)):
            return True
    return False


def inside_record(path):
    parts = path.split("/")
    if parts[0] == "docs" and len(parts) > 1:
        return True
    return len(parts) > 3 and parts[0] == "desks" and parts[2] == "docs"


def say_outside(headline, files):
    print("OUTSIDE: " + headline)
    for path in sorted(files):
        print(path)
    sys.exit(1)


def check_card(card_path, base):
    touches, branch = read_touches(card_path)
    fence = "the card's Touches"
    if branch:
        others, more = branch_touches(card_path, branch)
        if others:
            touches += more
            fence = "the Touches of this card and %d other card(s) on %s" % (others, branch)
    if git("rev-parse", "--verify", "--quiet", base + "^{commit}") is None:
        refuse('there is no branch "%s" here to check against; name one with --base.' % base)
    fork = git("merge-base", base, "HEAD")
    if fork is None:
        refuse('this branch shares no history with "%s", so there is nothing to compare.' % base)
    committed = git("diff", "--name-only", "-z", "--no-renames", fork.strip(), "HEAD")
    if committed is None:
        refuse("git could not list the committed changes.")
    changed = set(nul_list(committed)) | uncommitted_files()
    outside = [path for path in changed if not inside_touches(path, touches)]
    if outside:
        say_outside("%d changed file(s) are not in %s (against %s):"
                    % (len(outside), fence, base), outside)
    if changed:
        print("INSIDE: all %d changed file(s) are in %s (against %s)."
              % (len(changed), fence, base))
    else:
        print("INSIDE: nothing has changed against %s." % base)


def check_main():
    dirs = git("rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    if dirs is None:
        refuse("git could not tell which checkout this is.")
    git_dir, common_dir = [os.path.normcase(os.path.realpath(d)) for d in dirs.splitlines()[:2]]
    if git_dir != common_dir:
        print("Not the main checkout: this is a linked worktree, so the main checkout's fence does not apply here.")
        return
    outside = [path for path in uncommitted_files() if not inside_record(path)]
    if outside:
        say_outside("%d uncommitted change(s) in the main checkout are outside the record (%s):"
                    % (len(outside), RECORD), outside)
    print("INSIDE: the main checkout has no uncommitted change outside the record (%s)." % RECORD)


def main():
    parser = argparse.ArgumentParser(description="Say whether a working copy has stayed inside its fence.")
    parser.add_argument("--card", help="the card whose ## Touches is the fence")
    parser.add_argument("--base", help="the branch to compare against (default: main)")
    parser.add_argument("--main", action="store_true", help="check the main checkout instead of a card")
    args = parser.parse_args()

    if args.main and (args.card or args.base):
        refuse("--main takes no card and no base; run it on its own.")
    if not args.main and not args.card:
        refuse("name a card with --card <card-file>, or check the main checkout with --main.")
    toplevel = git("rev-parse", "--show-toplevel")
    if toplevel is None:
        refuse("this folder is not inside a git working copy.")
    card_path = os.path.abspath(args.card) if args.card else None
    # Git names files from the top of the repo, and so does Touches.
    os.chdir(toplevel.strip())
    if args.main:
        check_main()
    else:
        check_card(card_path, args.base or "main")


if __name__ == "__main__":
    main()
