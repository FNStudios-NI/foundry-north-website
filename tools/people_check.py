# people_check.py: does this project hold a third person's details?
#
# When it runs
#   Before the receipt's commit, and before any page is published.
#   Its REFUSE is a stop: nothing is committed or published until the
#   files it names hold the person by role only ("the user").
#
# What it is for
#   His ruling (5 Oct 2026): a project that always stays private may keep
#   a third person's details. A project that will ever be shared keeps
#   people by role only; their details live outside the project, with a
#   pointer in docs/register.md. This checks the record against that.
#   His ruling (6 Oct 2026): a project may stay private while one folder
#   in it may be public, as the template's master copy "might be in some
#   instances public but all the stuff around that will stay private".
#   Such a folder holds no person and no private fact of his, so it is
#   checked as a shared project is, and the rest of the tree is not.
#
# What it does
#   1. Reads the "Shared:" line of docs/brief.md.
#      No Shared line, or one not filled -> REFUSE.
#   2. If never, reads the "Held apart:" line under it: the folders that
#      may be public. No such line, or "none" -> ALLOW, exit 0, as before
#      the line existed. Folders named -> only the files inside them are
#      checked, by 3 and 4; every file outside them is passed. Folders
#      named with no docs/register.md, or no People rows in it -> REFUSE:
#      a folder held apart with nothing to hold it against is not held.
#   3. If yes, or for the folders held apart, reads the "## People" table
#      of docs/register.md. Each row's pointer is a text file outside the
#      project holding the words that must not appear, one per line (a
#      name, a condition, an employer).
#   4. Reads every tracked file, whatever its kind, unless it is binary (a
#      NUL byte in its first 8 KB), and prints one REFUSE line per file
#      holding any such word, naming the file and the role, never the word.
#   It only reads. It writes nothing and never prints a person's detail.
#
# How to run it
#   From the project's folder:   python tools/people_check.py
#   Or from anywhere:            python tools/people_check.py --project <dir>
#   It exits 0 for ALLOW, 1 for REFUSE.
#
# Python 3 standard library only.

import os
import re
import subprocess
import sys

BINARY_SNIFF = 8192  # a NUL byte in this many first bytes marks a binary file
SHARED_LINE = re.compile(r"^[\s>*_-]*Shared:[*_]*\s*(.*)$", re.IGNORECASE)
HELD_LINE = re.compile(r"^[\s>*_-]*Held apart:[*_]*\s*(.*)$", re.IGNORECASE)
PEOPLE_HEADING = re.compile(r"^##\s+People\b")
ANY_HEADING = re.compile(r"^##\s")
TABLE_RULE = re.compile(r"^\|[\s|:-]*\|$")

# Stops git from tidying its own index while it answers, so this tool
# writes nothing at all, not even git's housekeeping.
GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")


class Refuse(Exception):
    pass


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8-sig", errors="replace")


def brief_lines(project):
    brief = os.path.join(project, "docs", "brief.md")
    if not os.path.isfile(brief):
        raise Refuse("there is no brief at docs/brief.md")
    return read_text(brief).splitlines()


def shared_answer(project):
    """Return 'never' or 'yes' from the brief's Shared line."""
    for line in brief_lines(project):
        m = SHARED_LINE.match(line)
        if not m:
            continue
        answer = m.group(1).strip().lower()
        # The blank's own line, "never | yes — <his words>", is not an answer.
        if "|" in answer or "<" in answer:
            raise Refuse("the brief's Shared line is not filled: keep never or yes")
        if re.match(r"never\b", answer):
            return "never"
        if re.match(r"yes\b", answer):
            return "yes"
        raise Refuse("the brief's Shared line says neither never nor yes")
    raise Refuse("the brief has no Shared line")


def held_apart(project):
    """Return the folders the brief's Held apart line names; [] for none."""
    for line in brief_lines(project):
        m = HELD_LINE.match(line)
        if not m:
            continue
        answer = m.group(1).strip()
        # The blank's own line, "<folders that may be public, or none>", is not an answer.
        if "<" in answer:
            raise Refuse("the brief's Held apart line is not filled: name the folders, or none")
        folders = []
        # Words after a dash are his, as on the Shared line, not folders.
        for word in re.split(r"[,\s]+", answer.split("—")[0]):
            word = word.strip("`*_").replace("\\", "/").strip("/")
            if word.startswith("./"):
                word = word[2:]
            if word and word.lower() != "none":
                folders.append(word)
        return folders
    return []


def people_rows(project, held=False):
    """Return [(role, pointer)] from the register's People table."""
    register = os.path.join(project, "docs", "register.md")
    if not os.path.isfile(register):
        if held:
            raise Refuse("folders are held apart and there is no docs/register.md to hold them against")
        raise Refuse("the project is shared and there is no docs/register.md")
    rows, inside = [], False
    for line in read_text(register).splitlines():
        if PEOPLE_HEADING.match(line):
            inside = True
            continue
        if inside and ANY_HEADING.match(line):
            break
        line = line.strip()
        if not inside or not line.startswith("|") or TABLE_RULE.match(line):
            continue
        cells = [c.strip().strip("`").strip() for c in line.strip("|").split("|")]
        if cells[0].lower() == "role":
            continue
        rows.append((cells[0] or "a person with no role", cells[1] if len(cells) > 1 else ""))
    return rows


def details_of(project, role, pointer):
    """Read one person's words from their file outside the project."""
    if not pointer:
        raise Refuse(f"the People row for {role} has no pointer")
    path = os.path.expandvars(os.path.expanduser(pointer))
    if not os.path.isabs(path):
        path = os.path.join(project, path)
    path = os.path.realpath(path)
    if not os.path.isfile(path):
        raise Refuse(f"the details file for {role} does not exist")
    try:
        inside = os.path.normcase(os.path.commonpath([path, project])) == os.path.normcase(project)
    except ValueError:  # on another drive
        inside = False
    if inside:
        raise Refuse(f"the details file for {role} is inside the project")
    words = [w.strip() for w in read_text(path).splitlines() if w.strip()]
    if not words:
        raise Refuse(f"the details file for {role} holds no words")
    return words


def word_pattern(words):
    """One pattern matching any of the words, whole and in any case."""
    parts = [r"\s+".join(map(re.escape, w.split())) for w in words]
    return re.compile(r"(?<!\w)(?:" + "|".join(parts) + r")(?!\w)", re.IGNORECASE)


def project_files(project):
    """The files git tracks or would commit; every file if not in git."""
    try:
        done = subprocess.run(
            ["git", "-C", project, "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"],
            capture_output=True, env=GIT_ENV,
        )
        in_git = done.returncode == 0
    except FileNotFoundError:
        in_git = False
    if in_git:
        names = done.stdout.decode("utf-8", errors="replace").split("\0")
    else:
        names = []
        for root, dirs, files in os.walk(project):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                names.append(os.path.relpath(os.path.join(root, f), project))
    return sorted({n.replace(os.sep, "/") for n in names if n})


def is_binary(path):
    with open(path, "rb") as f:
        return b"\0" in f.read(BINARY_SNIFF)


def in_folders(name, folders):
    return any(name == f or name.startswith(f + "/") for f in folders)


def check(project):
    """Return (allow_reason, refuse_lines)."""
    if not os.path.isdir(project):
        raise Refuse(f"no project folder at {project}")
    folders = None  # None: the whole project is checked
    if shared_answer(project) == "never":
        folders = held_apart(project)
        if not folders:
            return "private project", []
    people = [(role, word_pattern(details_of(project, role, pointer)))
              for role, pointer in people_rows(project, held=folders is not None)]
    if not people:
        if folders is not None:
            raise Refuse("folders are held apart and the register lists no people to hold them against")
        return "shared project, and the register lists no people", []

    def hide(text):
        # A role or a file name could itself hold a detail; never print it.
        for _, pattern in people:
            text = pattern.sub("[a detail]", text)
        return text

    refusals = []
    for name in project_files(project):
        if folders is not None and not in_folders(name, folders):
            continue
        path = os.path.join(project, name)
        if not os.path.isfile(path) or is_binary(path):
            continue
        text = read_text(path)
        roles = [hide(role) for role, pattern in people if pattern.search(text)]
        if roles:
            refusals.append(f"{hide(name)} holds a detail of {' and '.join(roles)}")
    if folders is not None:
        return "private project, and no file held apart holds a person's detail", refusals
    return "shared project, and no file holds a person's detail", refusals


def main(argv):
    args = argv[1:]
    project = "."
    if args[:1] == ["--project"] and len(args) == 2:
        project = args[1]
    elif args:
        print("REFUSE: run it as: python tools/people_check.py [--project <dir>]")
        return 1
    project = os.path.realpath(project)
    try:
        reason, refusals = check(project)
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1
    except Exception as err:  # a broken check must never read as a pass
        # Only the kind of failure: its message could carry a detail.
        print(f"REFUSE: the check itself failed ({type(err).__name__})")
        return 1
    if refusals:
        for line in refusals:
            print(f"REFUSE: {line}")
        return 1
    print(f"ALLOW: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
