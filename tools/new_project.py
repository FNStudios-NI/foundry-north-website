# new_project.py - makes a new project from the template.
#
# What it is for:
#   Every new project starts as a stamped copy of this template. This tool
#   makes that copy in one go, so nobody copies folders by hand and forgets
#   a step. It:
#     - copies the template folder to <folder>/<name>, leaving out
#       __pycache__ folders. .gitkeep files are copied, so a folder that is
#       empty but for one (a test fixture such as tools/tests/pages/
#       empty-project/) arrives too;
#     - renames dot-claude/ to .claude/ in the copy (the template keeps it
#       as dot-claude so it is not mistaken for this repo's own settings);
#     - puts the project's name wherever the template has the placeholder
#       (the word project in angle brackets);
#     - writes project.yaml, the identity card: the name, the day it was
#       born and the template version it was stamped from. Nothing else,
#       because the card holds only facts that never change;
#     - writes .gitignore, holding __pycache__/ and .pytest_cache/, so
#       neither Python's cache nor pytest's gets into the project's git, and
#       the first test run leaves no untracked folder; and
#       docs/runs/*/flag.txt, the master's flag for the signal box, which is
#       a live signal and never committed (tracks.md says why);
#     - writes his reminder, docs/operator-acts/<date>-github-repository.txt,
#       from docs/blanks/github-reminder.txt with the project's name filled
#       in: the steps to make the project's empty private repository on
#       GitHub's website, which is his own act at every birth (his ruling);
#     - runs git init on branch main and makes one first commit of
#       everything stamped. If git is missing or the commit fails, it says so
#       in plain words and the stamped copy stands. Where git has no name to
#       commit as (his work machine sets one per repository, none for the
#       machine), the new repository is given the name and email the
#       template's own repository uses, and the stamp says so: otherwise no
#       project born there could make its first commit, or any later one;
#     - opens the reminder in Notepad by Notepad's full path (a bare notepad
#       opens the wrong program on his laptop), without waiting on it, and
#       prints the next command, the online step. With --no-open it prints
#       the reminder's full path and opens nothing: for tests, checkers and
#       a machine with no Notepad.
#
# Going online (--online):
#   A project's record must not sit on one machine only: the job scout's did
#   for 19 hours 46 minutes, and when it was noticed the machine's sign-in
#   could neither make nor reach a repository. So he makes the empty private
#   repository at the project's birth, from the reminder, and pastes its
#   address back. The online step then sets origin to that address (refusing
#   if a different origin is already set), pushes main, and checks it
#   arrived: git ls-remote must read the same commit as the project's HEAD.
#   That check alone decides what it prints. "ONLINE: <address> holds
#   <commit>" and exit 0; or "NOT ONLINE:" with git's own words, one plain
#   line, and exit 1.
#   It never tries to make the repository: no GitHub command-line tool and
#   no web call, because making one is his act and this machine's sign-in
#   was refused when it tried.
#
# Why the rules exist:
#   Names are lowercase letters, digits and single hyphens, never starting
#   or ending with a hyphen, because spaces and apostrophes in a name an
#   agent touches caused trouble from an earlier project's first day, and the house
#   ruled lowercase with hyphens. Names Windows keeps for itself (con, prn,
#   aux, nul, com1 to com9, lpt1 to lpt9) are refused too: they pass the
#   letters rule and then fail or misbehave as folders.
#   It never writes over a folder that is already there, because that could
#   destroy work. When it refuses, it makes nothing.
#   It never makes a copy inside the template itself, because that copy
#   would then be copied into every later project.
#   It builds the copy in a hidden staging folder beside the target, and
#   renames it into place only when it is complete. If anything fails, the
#   staging folder is removed and the target does not exist, so a re-run
#   is never stuck on a half copy.
#   Every project gets its own copy of this file, but that copy refuses to
#   run: it knows it is in a project because project.yaml sits beside its
#   tools/ folder. Run there, it would stamp a copy of the project as if it
#   were the template. New projects are made from the template's master copy.
#   The online step is the one thing a project's copy does run, because it
#   reads nothing of the template: it only pushes the project it is given.
#   For the same reason the test that runs adopt on the template itself is
#   skipped in a project's copy, saying why; it runs only in the master copy.
#   It is a dry run unless you add --go, so you can see what it would do
#   before it does it.
#
# Adopting (--adopt):
#   A project that already has a record (this project, later the Manager)
#   gets the template's working files laid over it instead of a fresh copy:
#   .claude/skills/, .claude/settings.json, tools/, pages.md, operator.md,
#   worker-rules.md, tracks.md, docs/blanks/ and desks/_desk/. Each is
#   overwritten with the template's version, because those files are the
#   template's to own, except .claude/settings.json (below).
#   .claude/settings.json is joined, never overwritten, because settings are
#   his: an earlier adopt wrote over this project's own and took its
#   superpowers plugin away at every version. The project's file and the
#   template's are joined key by key at every depth: a key only the project
#   has is kept; a key only the template has is added; a list gains the
#   template's items it lacks, at its end; where both hold a key with
#   different values, the project's is kept. The dry run and --go print one
#   line per key kept, differing or added. A joined file the same as the one
#   there is not written, and is listed under what it leaves alone. With no
#   settings file the template's is written; a settings file that is not a
#   JSON object makes the adopt refuse before it writes anything.
#   The record is the project's own, so it is never written: CLAUDE.md,
#   docs/decisions.md, docs/brief.md, docs/register.md, docs/roadmap.md,
#   docs/cards/, docs/pages/, docs/research/ and every desk but _desk.
#   project.yaml is written only if missing; if present, only its
#   template_version line changes (added if it has none).
#   .gitignore is the project's own, but adopt adds any of the template's
#   ignore lines it is missing (making the file if there is none), at the
#   end, and leaves its other lines as they are, in their order. Why: an
#   adopted project, this one among them, would otherwise commit its
#   master's flag. The dry run lists the lines it would add; a .gitignore
#   that holds them all is listed under what it would leave alone.
#   It refuses a folder that is not a project (no CLAUDE.md and no docs/),
#   the template itself, and a project with uncommitted changes, so every
#   change it makes can be seen with git diff and undone with git checkout.
#
# How to run it (from any folder):
#   python template/tools/new_project.py <name> --into <folder>         (dry run: shows what it would make)
#   python template/tools/new_project.py <name> --into <folder> --go    (makes it, commits it, opens his reminder)
#   python template/tools/new_project.py <name> --into <folder> --go --no-open   (the same, opening nothing)
#   python template/tools/new_project.py --online <project folder> --remote <address>   (pushes main and checks it arrived)
#   python tools/new_project.py --online . --remote <address>           (the same, from inside the project, with its own copy)
#   python template/tools/new_project.py --adopt foundry-north-website              (dry run: shows what it would write and leave alone)
#   python template/tools/new_project.py --adopt foundry-north-website --go         (writes it)
#
# Python 3, standard library only. No network but git's own, in the online
# step only: its push and its ls-remote.

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TEMPLATE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME_RULE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WINDOWS_NAMES = {"con", "prn", "aux", "nul"} | {"com%d" % n for n in range(1, 10)} | {"lpt%d" % n for n in range(1, 10)}
LEAVE_OUT_FOLDERS = {"__pycache__"}
RENAME_FOLDERS = {"dot-claude": ".claude"}
GITIGNORE = "__pycache__/\n.pytest_cache/\ndocs/runs/*/flag.txt\n"
# Built in two halves so this file, which is copied too, never holds the placeholder itself.
PLACEHOLDER = b"<" + b"project>"
# What --adopt writes, as paths in the copy: a folder (ending /) means everything under it.
ADOPT_WRITES = [".claude/skills/", ".claude/settings.json", "tools/", "pages.md", "operator.md",
                "worker-rules.md", "tracks.md", "roles/", "docs/blanks/", "desks/_desk/"]
# The project's own record, which --adopt never writes.
ADOPT_LEAVES = ["CLAUDE.md", "docs/decisions.md", "docs/brief.md", "docs/register.md", "docs/roadmap.md",
                "docs/cards/", "docs/pages/", "docs/research/"]
VERSION_LINE = re.compile(rb"^template_version:[^\r\n]*", re.M)
# The one file --adopt writes that is joined with the project's own, not written over.
SETTINGS = ".claude/settings.json"
# His reminder to make the repository: the blank it is written from, and where it goes in a new project.
REMINDER_BLANK = os.path.join(TEMPLATE, "docs", "blanks", "github-reminder.txt")
REMINDER = "docs/operator-acts/%s-github-repository.txt"
# Notepad by its full path: a bare notepad opens the wrong program on his laptop.
NOTEPAD = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "notepad.exe")
# What opens the reminder. A test puts a stand-in here, so no test opens Notepad.
OPENER = subprocess.Popen


def refuse(reason):
    print("Refused: " + reason)
    sys.exit(1)


def is_inside(folder, outer):
    """True if folder is outer itself or anywhere below it."""
    folder = os.path.normcase(os.path.realpath(folder))
    outer = os.path.normcase(os.path.realpath(outer))
    return folder == outer or folder.startswith(outer.rstrip(os.sep) + os.sep)


def plan_copy():
    """List every file to copy, as (path in the template, path in the copy)."""
    plan = []
    for folder, subfolders, files in os.walk(TEMPLATE):
        subfolders[:] = sorted(f for f in subfolders if f not in LEAVE_OUT_FOLDERS)
        for name in sorted(files):
            source = os.path.join(folder, name)
            parts = os.path.relpath(source, TEMPLATE).split(os.sep)
            parts = [RENAME_FOLDERS.get(p, p) for p in parts[:-1]] + parts[-1:]
            plan.append((source, os.path.join(*parts)))
    return plan


def identity_card(name):
    with open(os.path.join(TEMPLATE, "VERSION"), encoding="utf-8") as f:
        version = f.read().strip()
    born = datetime.date.today().isoformat()
    return "name: %s\nborn: %s\ntemplate_version: %s\n" % (name, born, version)


def reminder_text(name):
    """His reminder, as bytes: the blank with the project's name filled in and its line for the agent left out."""
    with open(REMINDER_BLANK, "rb") as f:
        content = f.read().replace(PLACEHOLDER, name.encode("ascii"))
    if content.startswith(b"<For the agent"):
        content = content.split(b"\n", 1)[1].lstrip(b"\r\n")
    return content


def make_copy(plan, card, name, folder, reminder_path):
    """Build the copy in a staging folder inside folder, then rename it to its name."""
    for source, copy_path in plan:
        destination = os.path.join(folder, copy_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(source, "rb") as f:
            content = f.read()
        with open(destination, "wb") as f:
            f.write(content.replace(PLACEHOLDER, name.encode("ascii")))
    with open(os.path.join(folder, "project.yaml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(card)
    with open(os.path.join(folder, ".gitignore"), "w", encoding="utf-8", newline="\n") as f:
        f.write(GITIGNORE)
    reminder = os.path.join(folder, *reminder_path.split("/"))
    os.makedirs(os.path.dirname(reminder), exist_ok=True)
    with open(reminder, "wb") as f:
        f.write(reminder_text(name))


def git(folder, *args):
    """Run git in folder: (its exit code, what it printed, its own words). The exit code is None if git is not on this machine."""
    try:
        result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, errors="replace")
    except OSError as error:
        return None, "", "git could not be run on this machine (%s)" % error
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def first_commit(target, name):
    """Make target a git repository on branch main holding one commit of everything in it. None if it did, else git's own words."""
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", name + ": stamped from the template"]):
        if args[0] == "commit" and git(target, "var", "GIT_COMMITTER_IDENT")[0] != 0:
            lend_identity(target)
        code, printed, words = git(target, *args)
        if code != 0:
            return words or printed or "git %s failed and said nothing" % args[0]
    return None


def lend_identity(target):
    """Give target's repository the name and email the template's repository commits as, and say so."""
    for key in ("user.name", "user.email"):
        code, value, _ = git(TEMPLATE, "config", key)
        if code == 0 and value and git(target, "config", key, value)[0] == 0 and key == "user.name":
            print("git has no name to commit as on this machine, so this repository was given the one the template's repository uses: " + value)


def online(argv):
    parser = argparse.ArgumentParser(description="Push a project's main to the empty private repository he made, and check it arrived.")
    parser.add_argument("--online", required=True, metavar="PROJECT", help="the project folder to put online")
    parser.add_argument("--remote", required=True, metavar="ADDRESS", help="the address of the empty repository he made")
    args = parser.parse_args(argv)

    target = os.path.abspath(args.online)
    if not os.path.exists(os.path.join(target, ".git")):
        refuse('"%s" is not a git repository; the online step pushes a project that has its first commit.' % args.online)
    code, head, words = git(target, "rev-parse", "HEAD")
    if code != 0:
        refuse('"%s" has no commit to push. git said: %s' % (args.online, words))
    code, origin, _ = git(target, "remote", "get-url", "origin")
    if code == 0 and origin != args.remote:
        refuse('"%s" already has a different origin, %s; nothing was changed.' % (args.online, origin))
    if code != 0:
        code, _, words = git(target, "remote", "add", "origin", args.remote)
        if code != 0:
            refuse("origin could not be set. git said: " + words)

    _, _, pushed = git(target, "push", "origin", "main")
    # The check: the push is believed only when the remote itself reads back the same commit.
    _, there, unread = git(target, "ls-remote", "origin", "refs/heads/main")
    if there.split()[:1] == [head]:
        print("ONLINE: %s holds %s" % (args.remote, head))
        return
    print("NOT ONLINE: %s does not hold %s. git said:" % (args.remote, head))
    for line in (pushed or unread).splitlines():
        print("  " + line)
    print("If git's words say permission was denied, this machine's sign-in cannot push there; widening it is his act, once per machine.")
    sys.exit(1)


def adopt_plan():
    """The template files --adopt writes, as (path in the template, path in the project with / between parts)."""
    plan = []
    for source, copy_path in plan_copy():
        path = copy_path.replace(os.sep, "/")
        if any(path == w or (w.endswith("/") and path.startswith(w)) for w in ADOPT_WRITES):
            plan.append((source, path))
    return plan


def adopt_leaves(target, plan):
    """What --adopt leaves alone: the record, every desk but _desk, and the template files it does not write."""
    leaves = list(ADOPT_LEAVES)
    desks = os.path.join(target, "desks")
    if os.path.isdir(desks):
        leaves += sorted("desks/%s/" % d for d in os.listdir(desks) if d != "_desk" and os.path.isdir(os.path.join(desks, d)))
    written = {path for _, path in plan}
    for _, copy_path in plan_copy():
        path = copy_path.replace(os.sep, "/")
        if path not in written and path not in leaves:
            leaves.append(path)
    return leaves


def project_name(target):
    """The name in the project's project.yaml, or its folder's name if it has none."""
    card = os.path.join(target, "project.yaml")
    if os.path.isfile(card):
        with open(card, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("name:") and line[5:].strip():
                    return line[5:].strip()
    return os.path.basename(target)


def adopted_card(target, name, version):
    """project.yaml after adopting, as (bytes, what changed): a new card if there is none, else only its version line set."""
    path = os.path.join(target, "project.yaml")
    line = b"template_version: " + version.encode("ascii")
    if not os.path.isfile(path):
        card = "name: %s\nadopted: %s\ntemplate_version: %s\n" % (name, datetime.date.today().isoformat(), version)
        return card.encode("utf-8"), "new, holding: " + card.replace("\n", "  ").strip()
    with open(path, "rb") as f:
        old = f.read()
    if VERSION_LINE.search(old):
        return VERSION_LINE.sub(lambda m: line, old, count=1), "its template_version line set to " + version
    newline = b"\r\n" if b"\r\n" in old else b"\n"
    if old and not old.endswith(b"\n"):
        old += newline
    return old + line + newline, "template_version: " + version + " added; nothing else changed"


def adopted_gitignore(target):
    """.gitignore after adopting, as (bytes, the template lines it adds): the project's lines kept as they are, the missing ones added at the end."""
    path = os.path.join(target, ".gitignore")
    old = b""
    if os.path.isfile(path):
        with open(path, "rb") as f:
            old = f.read()
    have = {line.strip() for line in old.decode("utf-8", errors="replace").splitlines()}
    missing = [line for line in GITIGNORE.splitlines() if line not in have]
    if not missing:
        return old, missing
    newline = b"\r\n" if b"\r\n" in old else b"\n"
    if old and not old.endswith(b"\n"):
        old += newline
    return old + b"".join(line.encode("utf-8") + newline for line in missing), missing


def join_settings(mine, theirs, path, notes):
    """The project's settings (mine) joined with the template's (theirs), noting each key kept, differing or added."""
    if isinstance(mine, dict) and isinstance(theirs, dict):
        joined = {}
        for key, value in mine.items():
            here = path + [key]
            joined[key] = join_settings(value, theirs[key], here, notes) if key in theirs else value
            if key not in theirs:
                notes.append(("kept", ".".join(here), None))
        for key, value in theirs.items():
            if key not in mine:
                joined[key] = value
                notes.append(("added", ".".join(path + [key]), None))
        return joined
    if isinstance(mine, list) and isinstance(theirs, list):
        lacking = [item for item in theirs if item not in mine]
        notes.extend(("added to", ".".join(path), item) for item in lacking)
        return mine + lacking
    if mine != theirs:
        notes.append(("differs", ".".join(path), theirs))
    return mine


def adopted_settings(target, template_settings):
    """.claude/settings.json after adopting, as (bytes, notes, whether it changes): the project's own joined with the template's."""
    path = os.path.join(target, *SETTINGS.split("/"))
    if not os.path.isfile(path):
        return template_settings, [], True
    with open(path, "rb") as f:
        old = f.read()
    try:
        mine = json.loads(old.decode("utf-8-sig"))
    except ValueError as error:
        refuse('"%s" is not valid JSON (%s); fix it, then adopt again. Nothing was written.' % (path, error))
    if not isinstance(mine, dict):
        refuse('"%s" holds no JSON object; fix it, then adopt again. Nothing was written.' % path)
    notes = []
    joined = join_settings(mine, json.loads(template_settings.decode("utf-8")), [], notes)
    if joined == mine:
        return old, notes, False
    newline = "\r\n" if b"\r\n" in old else "\n"
    text = json.dumps(joined, indent=2, ensure_ascii=False).replace("\n", newline) + newline
    return text.encode("utf-8"), notes, True


def settings_lines(notes, go):
    """One line per settings key the adopt kept, differs on or adds."""
    add = "added" if go else "would add"
    lines = []
    for kind, key, value in notes:
        if kind == "kept":
            lines.append("kept " + key)
        elif kind == "differs":
            lines.append("kept yours for %s, the template has %s" % (key, json.dumps(value, ensure_ascii=False)))
        elif kind == "added":
            lines.append("%s %s" % (add, key))
        else:
            lines.append("%s %s to %s" % (add, json.dumps(value, ensure_ascii=False), key))
    return lines


def uncommitted(target):
    """What git status --porcelain says about the target, or None if git cannot tell."""
    try:
        result = subprocess.run(["git", "-C", target, "status", "--porcelain"], capture_output=True, text=True)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.rstrip()


def adopt(argv):
    parser = argparse.ArgumentParser(description="Lay the template's working files over a project that already exists.")
    parser.add_argument("--adopt", required=True, metavar="PROJECT", help="the project folder to adopt the template into")
    parser.add_argument("--go", action="store_true", help="really write it (without this it is a dry run)")
    args = parser.parse_args(argv)

    target = os.path.abspath(args.adopt)
    if not os.path.isdir(target):
        refuse('the folder "%s" does not exist.' % args.adopt)
    if is_inside(target, TEMPLATE):
        refuse('"%s" is the template itself; adopt lays the template over a project, never over its own master copy.' % args.adopt)
    if not os.path.isfile(os.path.join(target, "CLAUDE.md")) and not os.path.isdir(os.path.join(target, "docs")):
        refuse('"%s" is not a project: it has no CLAUDE.md and no docs/ folder.' % args.adopt)
    status = uncommitted(target)
    if status is None:
        refuse('git could not say whether "%s" has uncommitted changes; adopt runs only on a git project with none, so its changes can be seen and undone.' % args.adopt)
    if status:
        refuse('"%s" has uncommitted changes; commit them or put them aside first, so the adopt can be seen and undone on its own. git status says:\n%s' % (args.adopt, status))

    with open(os.path.join(TEMPLATE, "VERSION"), encoding="utf-8") as f:
        version = f.read().strip()
    name = project_name(target)
    plan = adopt_plan()
    card, card_change = adopted_card(target, name, version)
    ignore, ignore_adds = adopted_gitignore(target)
    with open(dict((path, source) for source, path in plan)[SETTINGS], "rb") as f:
        settings, settings_notes, settings_change = adopted_settings(target, f.read().replace(PLACEHOLDER, name.encode("utf-8")))
    settings_report = ["  %s: %s" % (SETTINGS, line) for line in settings_lines(settings_notes, args.go)]

    if args.go:
        try:
            for source, path in plan:
                destination = os.path.join(target, *path.split("/"))
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                if path == SETTINGS:
                    if settings_change:
                        with open(destination, "wb") as f:
                            f.write(settings)
                    continue
                with open(source, "rb") as f:
                    content = f.read()
                with open(destination, "wb") as f:
                    f.write(content.replace(PLACEHOLDER, name.encode("utf-8")))
            with open(os.path.join(target, "project.yaml"), "wb") as f:
                f.write(card)
            if ignore_adds:
                with open(os.path.join(target, ".gitignore"), "wb") as f:
                    f.write(ignore)
        except Exception as error:
            print('Failed: the adopt stopped part-way (%s). Every change is in git: "git -C %s status" shows it, "git -C %s checkout -- ." undoes the changed files.' % (error, target, target))
            sys.exit(1)
        print("Adopted template %s into %s as %s. Wrote:" % (version, target, name))
    else:
        print("Dry run: nothing written. Add --go to write it.")
        print("Would adopt template %s into %s as %s, writing:" % (version, target, name))
    for _, path in plan:
        if path != SETTINGS:
            print("  " + path)
        elif settings_change:
            print("  " + path + (" (joined with yours: your settings kept, the template's added)" if settings_notes else ""))
            for line in settings_report:
                print(line)
    print("  project.yaml (" + card_change + ")")
    if ignore_adds:
        print("  .gitignore (" + ("added" if args.go else "would add") + ": " + ", ".join(ignore_adds) + "; its own lines kept as they are)")
    print("Left alone:" if args.go else "Would leave alone:")
    for path in adopt_leaves(target, plan) + ([] if ignore_adds else [".gitignore"]):
        print("  " + path)
    if not settings_change:
        print("  %s (yours, with nothing of the template's to add)" % SETTINGS)
        for line in settings_report:
            print(line)


def main():
    if any(a == "--online" or a.startswith("--online=") for a in sys.argv[1:]):
        return online(sys.argv[1:])
    if os.path.isfile(os.path.join(TEMPLATE, "project.yaml")):
        refuse("this is a project's copy of the tool; a new project is made from the template's master copy, template/tools/new_project.py.")
    if any(a == "--adopt" or a.startswith("--adopt=") for a in sys.argv[1:]):
        return adopt(sys.argv[1:])

    parser = argparse.ArgumentParser(description="Make a new project from the template.")
    parser.add_argument("name", help="the project's name: lowercase letters, digits and single hyphens")
    parser.add_argument("--into", required=True, help="the folder to make the project in")
    parser.add_argument("--go", action="store_true", help="really make it (without this it is a dry run)")
    parser.add_argument("--no-open", action="store_true", help="write his reminder and print its full path, opening nothing")
    args = parser.parse_args()

    if not NAME_RULE.match(args.name):
        refuse('"%s" is not a good name: use lowercase letters, digits and single hyphens, with no hyphen at the start or end.' % args.name)
    if args.name in WINDOWS_NAMES:
        refuse('"%s" is a name Windows keeps for itself and cannot use for a folder; pick another.' % args.name)
    if not os.path.isdir(args.into):
        refuse('the folder "%s" does not exist.' % args.into)
    if is_inside(args.into, TEMPLATE):
        refuse('"%s" is inside the template; a copy there would be copied into every later project.' % args.into)
    target = os.path.join(os.path.abspath(args.into), args.name)
    if os.path.lexists(target):
        refuse('"%s" already exists; nothing was changed.' % target)

    plan = plan_copy()
    card = identity_card(args.name)
    reminder_path = REMINDER % datetime.date.today().isoformat()

    if not args.go:
        print("Dry run: nothing made. Add --go to make it.")
        print("Would make " + target + " from " + TEMPLATE + ":")
        for _, copy_path in plan:
            print("  " + copy_path)
        print("  project.yaml, holding:")
        for line in card.splitlines():
            print("    " + line)
        print("  .gitignore, holding:")
        for line in GITIGNORE.splitlines():
            print("    " + line)
        print("  " + reminder_path + ", his reminder to make the empty private repository " + args.name + " on GitHub's website")
        print("Would then run git init on branch main and make one first commit of all of it,")
        print("open his reminder in Notepad (with --no-open: only print its full path), and print the next command, the online step.")
        return

    staging = None
    try:
        staging = tempfile.mkdtemp(prefix="." + args.name + ".staging-", dir=os.path.abspath(args.into))
        make_copy(plan, card, args.name, staging, reminder_path)
        os.rename(staging, target)
    except BaseException as error:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)
        if not isinstance(error, Exception):
            raise
        if staging is not None and os.path.lexists(staging):
            print('Failed: the copy stopped part-way (%s), and the half copy "%s" could not be removed; delete it by hand.' % (error, staging))
        else:
            print("Failed: the copy stopped part-way (%s); it was cleaned up and nothing was made." % error)
        sys.exit(1)
    print("Made " + target + " (" + str(len(plan) + 3) + " files).")

    reminder = os.path.join(target, *reminder_path.split("/"))
    failed = first_commit(target, args.name)
    if failed:
        print("Not finished: the copy stands, but git could not make its first commit. git said: " + failed)
        print("His reminder was written and not opened: " + reminder)
        sys.exit(1)
    print("Made it a git repository on branch main, with one first commit of everything stamped.")
    if args.no_open:
        print("His reminder, written and not opened: " + reminder)
    else:
        try:
            OPENER([NOTEPAD, reminder], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Opened his reminder in Notepad: " + reminder)
        except OSError as error:
            print("Notepad could not be opened (%s). His reminder is at: %s" % (error, reminder))
    print("Next, the online step, when he pastes the repository's address back. Inside " + target + ":")
    print("  python tools/new_project.py --online . --remote <the address>")


if __name__ == "__main__":
    main()
