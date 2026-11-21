# plan_check.py: may this plan go to Rhys for his signature?
#
# What it is for
#   Before the plan page goes to him, this reads its plan items and says
#   ALLOW, or REFUSE with one line per fault. A fresh execution master runs
#   from the signed plan alone, so the plan must hold everything it needs.
#   It never judges what the words mean, and it writes nothing.
#
# What it reads (the same markup as the plan blank, pages.md)
#   A plan item is
#     <section class="item" data-piece="<n>"
#              data-mark="proven | documented | assumed | risk"
#              data-lane="light | standard | full"
#              data-touches="<paths, space-separated>"
#              data-creates="<names, space-separated>">
#   An item block with no data-piece (the evidence under a question) is
#   not a plan item. The budget is the text of the element marked
#   data-budget; the hard stop, the text of the one marked data-hard-stop;
#   the record of the acts tried, the text of the one marked
#   data-acts-tried.
#   Each of his acts is an element in the page's list of his acts:
#     <li data-act="<n>"
#         data-edits="<names, space-separated, or none>"
#         data-after="<the piece numbers that land before it, or go>">
#   data-creates names what a piece creates, data-edits what an act
#   edits; a name is any word the plan uses for the thing (a path,
#   schedule:morning-report), compared letter for letter. go is at Go,
#   before any piece. A name, a piece list or a number still a
#   <placeholder> is read as nothing, as an empty value is.
#
# What it refuses, and why
#   a. An item marked assumed (data-mark="assumed", ❓). Every assumed item
#      is spiked before he signs, and the signed plan holds none (his
#      ruling 7 of 8 Oct 06:03). An item he signs as a known risk
#      (data-mark="risk") is allowed: by his word, when its spike would
#      need his hands (the design's call 10, approved in ruling 9).
#   b. An item with no mark (ruling 7: every item carries one).
#   c. An item with no lane (ruling 4: the master proposes each piece's
#      lane on the plan and he signs it).
#   d. A light lane on an item whose data-touches names a tool (tools/), a
#      skill (skills/) or anything under template/, or names nothing.
#      Light work is checked by scripts only, so it is kept off the parts
#      everything else runs on (ruling 4: "a script refuses a light lane
#      on tools, skills or the template").
#   e. A page with no budget or no hard stop, or either still a
#      <placeholder> (ruling 5: the cut-offs, with their numbers, on the
#      plan page; run 2 ran twice its length).
#   f. A page with no record of the acts tried (no element marked
#      data-acts-tried), or with it empty or still a <placeholder>. It
#      holds the permission probe's answers (tracks.md rule 19) and each
#      command of his acts, dry-run or its refusal looked for. The job
#      scout's plan was signed with neither, and every block after his
#      signature was an act or a door nobody had tried.
#   g. An act whose data-edits names a thing a piece's data-creates names,
#      when that piece is not in the act's data-after. The Manager's plan
#      filed his Settings act first, but T3 sets model and workspace per
#      task, so the schedules his act edits had to exist first; the plan
#      page said nothing of what an act edits, so no check could see it
#      (run 6 lesson 21).
#   h. An act with no data-edits at all. The check asks what each act
#      edits (the same lesson); an act that edits nothing says "none".
#   A page with no act (no element marked data-act) gives neither.
#   A mark or lane that is not one of the words above counts as none.
#
# The trials (design of 17 Nov 2026, Part 3; his ruling 4 of 17 Nov 07:43
# and call 2): two trials on one project could not be told apart when
# quality moved. A signed plan (docs/runs/<n>/plan-signed.md) may carry
#   ## Trials
#   - <what is on trial> · file: <the workflow file, or template> · measure: <what it says> · reads: <a short name>
# and is refused for each line with no measure: or no reads:, for two lines
# whose reads: match with case and spaces aside (naming both), and for more
# than five lines. A plan with no ## Trials reads as before. A .md plan is
# read for its trials only; a page is read as above.
#
# How to run it
#   python template/tools/plan_check.py <plan page or plan-signed.md>
#   It prints ALLOW and exits 0, or one "REFUSE: ..." line per fault and
#   exits 1.
#
# Python 3 standard library only.

import importlib.util
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))

# The page is read the way page_check reads it.
_spec = importlib.util.spec_from_file_location("page_check_for_plan", os.path.join(TOOLS, "page_check.py"))
page_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(page_check)

MARKS = ("proven", "documented", "assumed", "risk")
LANES = ("light", "standard", "full")
PLACEHOLDER = re.compile(r"<[^<>]*>")


def is_plan_item(node):
    return page_check.is_item(node) and "data-piece" in node.attrs


def heavy_path(path):
    """True if the path is a tool, a skill, or under template/."""
    p = "/" + path.replace("\\", "/").strip().lstrip("./").strip("/") + "/"
    return "/tools/" in p or "/skills/" in p or p.startswith("/template/")


def words(value):
    """The space-separated words of an attribute, a <placeholder> read as nothing."""
    return PLACEHOLDER.sub(" ", value or "").split()


def check(html):
    """Return the list of reasons to refuse; an empty list means ALLOW."""
    nodes = list(page_check.Tree(html).root.walk())
    faults = []

    for item in (n for n in nodes if is_plan_item(n)):
        piece = f"piece {item.attrs.get('data-piece') or '(no number)'}"
        mark = (item.attrs.get("data-mark") or "").strip().lower()
        lane = (item.attrs.get("data-lane") or "").strip().lower()
        touches = (item.attrs.get("data-touches") or "").split()

        if mark == "assumed":
            faults.append(f"{piece}: marked assumed. The signed plan holds no assumed item: spike it "
                          "first and mark it proven or documented, or, if the spike needs his "
                          "hands, ask him to sign it as a known risk (data-mark=\"risk\").")
        elif mark not in MARKS:
            faults.append(f"{piece}: no mark. Give it data-mark=\"proven\", \"documented\", "
                          "\"assumed\" or \"risk\", with the evidence.")
        if lane not in LANES:
            faults.append(f"{piece}: no lane. Give it data-lane=\"light\", \"standard\" or \"full\" "
                          "for him to sign.")
        elif lane == "light":
            if not touches:
                faults.append(f"{piece}: a light lane that names nothing it touches. Name its "
                              "paths in data-touches; a light lane is only for what a script can check.")
            heavy = [t for t in touches if heavy_path(t)]
            if heavy:
                faults.append(f"{piece}: a light lane on {', '.join(heavy)}. A tool, a skill or "
                              "anything under template/ is a full lane, checked by an Opus inspector.")

    for attr, name in (("data-budget", "budget"), ("data-hard-stop", "hard stop"),
                       ("data-acts-tried", "record of the acts tried")):
        marked = [n for n in nodes if attr in n.attrs]
        if not marked:
            faults.append(f"the page has no {name}. Mark the element that states it with {attr}.")
        for n in marked:
            text = n.text()
            if not text:
                faults.append(f"the {name} ({attr}) is empty. Write it in.")
            elif PLACEHOLDER.search(text):
                faults.append(f"the {name} ({attr}) is still a placeholder (\"{page_check.short(text)}\"). "
                              "Write the real one in.")

    creators = [(" ".join(words(item.attrs.get("data-piece"))) or "(no number)",
                 words(item.attrs.get("data-creates"))) for item in nodes if is_plan_item(item)]
    for act in (n for n in nodes if "data-act" in n.attrs):
        number = " ".join(words(act.attrs.get("data-act"))) or "(no number)"
        if "data-edits" not in act.attrs:
            faults.append(f"act {number} does not say what it edits. Give it data-edits=\"<names>\" "
                          "or data-edits=\"none\".")
            continue
        edits = words(act.attrs.get("data-edits"))
        after = words(act.attrs.get("data-after"))
        for name in ([] if edits == ["none"] else edits):
            for p, creates in creators:
                if name in creates and p not in after:
                    faults.append(f"act {number} edits {name}, which piece {p} creates, but is ordered "
                                  f"before it. Put {p} in its data-after, or move the act.")

    return faults


MOST_TRIALS = 5


def _field(parts, key):
    """The value of the first ' · '-part starting '<key>:', a <placeholder> read as nothing."""
    for part in parts:
        if part.startswith(key + ":"):
            return PLACEHOLDER.sub("", part[len(key) + 1:]).strip()
    return ""


def trial_faults(text):
    """The faults of a plan's ## Trials section; [] with no section."""
    trials, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Trials"
            continue
        if inside and line.startswith("- "):
            trials.append(line[2:].strip())
    faults, seen = [], {}
    for trial in trials:
        parts = [p.strip() for p in trial.split(" · ")]
        what = parts[0]
        if not _field(parts, "measure"):
            faults.append(f"trial \"{what}\" has no measure:. Write what its measure says, so the trial can be judged.")
        reads = _field(parts, "reads")
        if not reads:
            faults.append(f"trial \"{what}\" has no reads:. Name the one thing its measure counts.")
            continue
        key = "".join(reads.lower().split())
        if key in seen:
            faults.append(f"trials \"{seen[key]}\" and \"{what}\" both read \"{reads}\". Two trials that count "
                          "the same thing cannot be told apart when quality moves: give one another measure, "
                          "or run it in another job (his ruling 4 of 17 Nov).")
        else:
            seen[key] = what
    if len(trials) > MOST_TRIALS:
        faults.append(f"the plan carries {len(trials)} trials. Five at most ride on one project (his ruling 4 "
                      "of 17 Nov, call 2): keep five and run the rest in another job.")
    return faults


def main(argv):
    # A page's own words are quoted back; never let the console's code page crash the check.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = argv[1:]
    if len(args) != 1:
        print("REFUSE: name one plan page, like: python template/tools/plan_check.py <plan page>")
        return 1
    page = args[0]
    try:
        if not os.path.isfile(page):
            print(f"REFUSE: no page at {page}")
            return 1
        with open(page, encoding="utf-8") as f:
            text = f.read()
        faults = trial_faults(text) if page.lower().endswith(".md") else check(text)
    except Exception as err:  # a broken check must never read as a pass
        print(f"REFUSE: the check itself failed ({type(err).__name__}: {err})")
        return 1
    if faults:
        for why in faults:
            print(f"REFUSE: {why}")
        return 1
    print("ALLOW")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
