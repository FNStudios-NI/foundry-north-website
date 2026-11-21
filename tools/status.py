# status.py: the status board, read from the workflow files and the template's status file.
#
# Why it exists
#   "Lock" froze a way of working with nothing to say how often it had
#   worked (design of 17 Nov 2026, Part 3; his rulings 3 and 4 of 17 Nov
#   07:43). Every step now carries one of three tags, and this board shows
#   them all in one place, so nobody keeps a state by hand.
#
# What it reads
#   A workflow file is any .md in the project, outside .git, template/ and
#   docs/blanks/, holding a "Version: v<n.m>" line and at least one tagged
#   step. A step is a numbered line under "## Steps":
#     <n>. **<the step's name>** · `<tag>` · <who> — in: <…> — out: <…> — <its rule>
#   and <tag> is one of `idea`, `on trial` · measure: <what it reads>, or
#   `foundation · <n> job(s)`. The file's own "Tag:" line takes the same
#   three forms; a file with an older "State:" line and no "Tag:" shows its
#   State as its tag. A step with no tag is listed as untagged.
#   Then template/STATUS.md's "## Parts":
#     - **<part>** · `<tag>` · files: <path>, <path> · since <x.y.z>
#   or one line saying there is none.
#
# How to run it
#   python tools/status.py                     the board, for the project it is run in
#   python tools/status.py --project <folder>  another project's board
#   python tools/status.py --html              the same board as one
#                                              <section class="status-board" data-status-board>
#   It writes nothing and touches no network. Python 3 standard library only.
#   upgrade.py and where_am_i.py load this file beside them, so the tags are
#   read one way everywhere.
#   closed_run_without_workflow(project) is the fact page_check.py asks him about: a run has closed and
#   no workflow file exists. Why: the board's "workflows: none" alone put no question to him (L040).

import argparse
import html
import os
import re
import sys
from pathlib import Path

VERSION = re.compile(r"^Version:\s*(v\d+\.\d+)", re.M)
STEP = re.compile(r"^(\d+)\.\s+(.*)$")
BOLD = re.compile(r"^\*\*(.+?)\*\*(.*)$")
TICKED = re.compile(r"^\s*·\s*`([^`]*)`(.*)$")
MEASURE = re.compile(r"^\s*·\s*measure:\s*(.*?)(?:\s+·\s+.*)?$")
FOUNDATION = re.compile(r"^foundation\s*·\s*(\d+)\s*jobs?$")
SINCE = re.compile(r"\bsince\s+(\S+)")
NO_STATUS = "template parts: no template/STATUS.md here"
CLOSED_RUN = re.compile(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} — Run \d+ closed\b", re.M)


def _read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def parse_tag(inner, after=""):
    """A tag from the text inside its backticks and what follows them: {"tag", "measure", "jobs"}."""
    inner = " ".join(inner.split())
    if inner == "idea":
        return {"tag": "idea", "measure": None, "jobs": None}
    if inner == "on trial":
        m = MEASURE.match(after or "")
        return {"tag": "on trial", "measure": (m.group(1).strip() or None) if m else None, "jobs": None}
    m = FOUNDATION.match(inner)
    if m:
        return {"tag": "foundation", "measure": None, "jobs": int(m.group(1))}
    return {"tag": "untagged", "measure": None, "jobs": None}


def tag_text(tag):
    """A tag as the board prints it (an older State: as it stands)."""
    if tag.get("state"):
        return tag["tag"]
    if tag["tag"] == "on trial":
        return "on trial · measure: " + (tag["measure"] or "none written")
    if tag["tag"] == "foundation":
        return f"foundation · {tag['jobs']} job" + ("" if tag["jobs"] == 1 else "s")
    return tag["tag"]


def _file_tag(text):
    """The whole workflow's tag from its Tag: line, or its older State: line shown as it stands."""
    state = None
    for line in text.splitlines():
        if line.startswith("Tag:"):
            value = line[len("Tag:"):].strip()
            m = TICKED.match(" · " + value)
            if m:
                return parse_tag(m.group(1), m.group(2))
            return parse_tag(re.split(r"\s+<", value)[0])
        if line.startswith("State:") and state is None:
            state = re.split(r"\s+<", line[len("State:"):].strip())[0].strip()
    if state:
        return {"tag": state, "measure": None, "jobs": None, "state": True}
    return {"tag": "untagged", "measure": None, "jobs": None}


def read_workflow(path, rel, strict=True):
    """One workflow file as a dict, or None when it is not one (no Version: line, or no tagged step).
    strict=False reads any file's tags the same way, for a check of one named file."""
    text = _read(path)
    version = VERSION.search(text)
    if not version and strict:
        return None
    name, steps, under = None, [], False
    for line in text.splitlines():
        if line.startswith("# ") and name is None:
            name = re.sub(r"\s+—\s+v\d+\.\d+\s*$", "", line[2:].strip())
        if line.startswith("## "):
            under = line.strip() == "## Steps"
            continue
        m = STEP.match(line) if under else None
        if not m:
            continue
        body = m.group(2)
        bold = BOLD.match(body)
        if bold:
            step_name, rest = bold.group(1).strip(), bold.group(2)
        else:
            step_name, rest = re.split(r"\s+[—·]\s+", body, maxsplit=1)[0].strip(), ""
        ticked = TICKED.match(rest)
        tag = parse_tag(ticked.group(1), ticked.group(2)) if ticked else parse_tag("")
        steps.append({"n": int(m.group(1)), "name": step_name, "tag": tag})
    if strict and not any(s["tag"]["tag"] != "untagged" for s in steps):
        return None
    return {"file": rel, "name": name or rel, "version": version.group(1) if version else None,
            "tag": _file_tag(text), "steps": steps, "text": text}


def workflows(project):
    """Every workflow file of the project, by path."""
    project = Path(project)
    found = []
    for folder, dirs, files in os.walk(project):
        rel_folder = Path(folder).relative_to(project).as_posix()
        rel_folder = "" if rel_folder == "." else rel_folder
        keep = []
        for d in sorted(dirs):
            rel = f"{rel_folder}/{d}" if rel_folder else d
            if d == ".git" or rel == "template" or rel == "docs/blanks" or rel.endswith("/docs/blanks"):
                continue
            keep.append(d)
        dirs[:] = keep
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            rel = f"{rel_folder}/{f}" if rel_folder else f
            flow = read_workflow(Path(folder) / f, rel)
            if flow:
                found.append(flow)
    return sorted(found, key=lambda w: w["file"])


def closed_run_without_workflow(project):
    """True when a docs/decisions*.md file closes a run and the project has no workflow file."""
    closed = any(CLOSED_RUN.search(_read(p)) for p in Path(project).glob("docs/decisions*.md") if p.is_file())
    return closed and not workflows(project)


def foundations(project, flows=None):
    """Each foundation in the workflow files: {"file", "step" (None for the file's own Tag: line), "name", "jobs"}."""
    found = []
    for flow in workflows(project) if flows is None else flows:
        if flow["tag"]["tag"] == "foundation":
            found.append({"file": flow["file"], "step": None, "name": flow["name"], "jobs": flow["tag"]["jobs"]})
        for step in flow["steps"]:
            if step["tag"]["tag"] == "foundation":
                found.append({"file": flow["file"], "step": step["n"], "name": step["name"],
                              "jobs": step["tag"]["jobs"]})
    return found


def foundation_text(f):
    """One foundation as where_am_i.py and upgrade.py print it."""
    jobs = f"{f['jobs']} job" + ("" if f["jobs"] == 1 else "s")
    return f"{f['file']} step {f['step']} {f['name']} · {jobs}" if f["step"] else f"{f['file']} · {jobs}"


def parts(project):
    """template/STATUS.md's parts as {"part", "tag", "since"}, or None when there is no such file."""
    path = Path(project) / "template" / "STATUS.md"
    if not path.is_file():
        return None
    found, under = [], False
    for line in _read(path).splitlines():
        if line.startswith("## "):
            under = line.strip() == "## Parts"
            continue
        if not under or not line.startswith("- "):
            continue
        body = line[2:].strip()
        bold = BOLD.match(body)
        part, rest = (bold.group(1).strip(), bold.group(2)) if bold else (body, "")
        ticked = TICKED.match(rest)
        since = SINCE.search(rest)
        found.append({"part": part, "tag": parse_tag(ticked.group(1), ticked.group(2)) if ticked else parse_tag(""),
                      "since": since.group(1) if since else None})
    return found


def board(project):
    """The board as (kind, text) lines: kind is "head", "flow", "step", "part" or "note"."""
    out = [("head", "status board")]
    flows = workflows(project)
    if not flows:
        out.append(("note", "workflows: none"))
    for flow in flows:
        out.append(("flow", f"{flow['file']} · {flow['name']} · {flow['version']} · {tag_text(flow['tag'])}"))
        for step in flow["steps"]:
            out.append(("step", f"step {step['n']} · {step['name']} · {tag_text(step['tag'])}"))
    found = parts(project)
    if found is None:
        out.append(("note", NO_STATUS))
    else:
        out.append(("flow", "template parts"))
        for p in found:
            since = f" · since {p['since']}" if p["since"] else ""
            out.append(("part", f"{p['part']} · {tag_text(p['tag'])}{since}"))
    return out


def as_text(lines):
    return "\n".join(("  " + text) if kind in ("step", "part") else text for kind, text in lines)


def as_html(lines):
    out = ['<section class="status-board" data-status-board>']
    in_list = False
    for kind, text in lines:
        if kind in ("step", "part"):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{html.escape(text)}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        tag = {"head": "h2", "flow": "h3"}.get(kind, "p")
        out.append(f"<{tag}>{html.escape(text)}</{tag}>")
    if in_list:
        out.append("</ul>")
    out.append("</section>")
    return "\n".join(out)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # the dots and dashes print in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="The status board, from the workflow files and template/STATUS.md.")
    parser.add_argument("--project", default=".", help="the project folder (default: here)")
    parser.add_argument("--html", action="store_true", help="print the board as one data-status-board element")
    args = parser.parse_args(argv)
    project = Path(args.project)
    if not project.is_dir():
        print(f"Not a folder: {project}", file=sys.stderr)
        return 1
    lines = board(project)
    print(as_html(lines) if args.html else as_text(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
