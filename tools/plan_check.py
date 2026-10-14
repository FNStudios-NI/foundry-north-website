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
#              data-touches="<paths, space-separated>">
#   An item block with no data-piece (the evidence under a question) is
#   not a plan item. The budget is the text of the element marked
#   data-budget; the hard stop, the text of the one marked data-hard-stop;
#   the record of the acts tried, the text of the one marked
#   data-acts-tried.
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
#   A mark or lane that is not one of the words above counts as none.
#
# How to run it
#   python template/tools/plan_check.py <plan page>
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
            faults = check(f.read())
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
