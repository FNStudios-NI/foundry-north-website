# page_check.py: may this page be published?
#
# What it is for
#   Before a page goes to Rhys, this reads it and says ALLOW, or REFUSE
#   with one line per rule it breaks. The rules are in pages.md; this
#   checks the ones a machine can see in the page's structure. It never
#   judges what the words mean, and it writes nothing.
#
# What it checks
#   a. The title block has the stage and its place ("Scope · 2 of 6", or
#      "Review") and "about N minutes".                         (rule 4)
#   b. A Design, Team or Plan page (4 to 6 of 6) comes after Problem,
#      Scope and Facts are in the record: the project's docs/brief.md
#      holds each one's section ("## The problem", "## Scope", "## Facts")
#      with words of its own under it, more than the blank's <...> and
#      its labels. One line names every step that is missing. A project
#      whose docs/pages/ holds a *facts-sheet*.html passes as it is.
#   c. A Problem, Scope or Facts page (1 to 3 of 6) has no calendar date
#      outside its title block and its "Where this comes from" section
#      (a source's file name is not a promise). If the stage cannot be
#      read, the page is held to this whenever Facts is not in the
#      record yet: no section with words, and no facts sheet.
#   d. There is a heading "Calls I'm making" (rule 17) and a heading
#      "Where this comes from" (rule 21).
#   e. If docs/pages/ already holds a sheet, there is a heading starting
#      "What I took".                                           (rule 3)
#   f. A picture (an inline <svg>) comes before the first question.
#                                                               (rule 7)
#   g. Every question has a box (<textarea>) inside it.        (rule 15)
#   h. No "?" in a label, caption or h2/h3 outside a numbered question.
#                              (note 7's line; pages.md has no number yet)
#   i. A button whose words hold both "Copy" and "notes".      (rule 20)
#   j. The first line is <meta charset="utf-8">.
#                                (pages.md, How a page is built)
#   k. Every item block (a <section class="item">) holds its own inline
#      <svg> and all four parts, data-part="area", "problem", "links"
#      and "effect"; and every question sits inside an item block.
#                                                               (rule 31)
#   l. Every plan item (an item block with data-piece) carries its mark,
#      its lane and its cost: data-mark and data-lane on the block, and
#      its own data-part="mark", "lane" and "cost".             (rule 31)
#   m. A plan page (Plan · 6 of 6) shows the budget and the hard stop:
#      an element with data-budget and one with data-hard-stop, each with
#      words in it.                    (pages.md, The plan page)
#   n. A review page's first item block is headed "It works", and its last
#      question is the enjoyment tap: five letters, 1 to 5.
#                                      (pages.md, The review page)
#   A question is an element with data-q, or a <fieldset> outside one.
#   An item's own svg and parts are those not inside an item within it.
#
# Why the rule exists
#   The page rules were prose, and the trial's best page (sheet 4, 5 Oct)
#   still broke five of them. A check that refuses holds a shape better.
#
# How to run it
#   python template/tools/page_check.py <page.html> --project <project folder>
#   It prints ALLOW and exits 0, or one "REFUSE: ..." line per fault and
#   exits 1.
#
# Python 3 standard library only.

import glob
import os
import re
import sys
from html.parser import HTMLParser

STAGES = {"problem": 1, "scope": 2, "facts": 3, "design": 4, "team": 5, "plan": 6}
STAGE_PLACE = re.compile(r"\b(Problem|Scope|Facts|Design|Team|Plan)\s*·\s*([1-6])\s+of\s+6\b", re.I)
REVIEW = re.compile(r"\bReview\b", re.I)
MINUTES = re.compile(r"\babout\s+\d+\s+minutes?\b", re.I)

MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?"
         r"|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?")
DATE = re.compile(
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+" + MONTH + r"(?![A-Za-z])"   # 7 October, 5 Oct
    r"|\b" + MONTH + r"\s+\d{1,2}(?:st|nd|rd|th)?\b"             # October 7
    r"|\b\d{4}-\d{2}-\d{2}\b")                                   # 2026-10-07

# The steps that are talked through, each with its heading in docs/brief.md (the brief blank's).
RECORD = (("Problem", "## The problem"), ("Scope", "## Scope"), ("Facts", "## Facts"))
RECORD_STEP = {heading.lower(): step for step, heading in RECORD}
BLANK_ONLY = re.compile(r"<[^>]*>|^[ \t]*(?:In|Out|Later):", re.M)

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
NOT_WORDS = {"script", "style"}
READ_ATTRS = ("aria-label", "alt", "title", "placeholder")


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

    def text(self, skip=NOT_WORDS):
        parts = []
        for c in self.children:
            if isinstance(c, str):
                parts.append(c)
            elif c.tag not in skip:
                parts.append(c.text(skip))
        return " ".join(" ".join(parts).split())

    def inside(self, test):
        p = self.parent
        while p is not None:
            if test(p):
                return True
            p = p.parent
        return False


class Tree(HTMLParser):
    """A forgiving tree: an end tag closes back to its matching open tag."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.open = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.open[-1])
        self.open[-1].children.append(node)
        if tag not in VOID:
            self.open.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, attrs, self.open[-1])
        self.open[-1].children.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.open) - 1, 0, -1):
            if self.open[i].tag == tag:
                del self.open[i:]
                return

    def handle_data(self, data):
        self.open[-1].children.append(data)


def is_question(node):
    return "data-q" in node.attrs or (
        node.tag == "fieldset" and not node.inside(lambda p: "data-q" in p.attrs))


def is_titleblock(node):
    return "titleblock" in node.classes()


PARTS = ("area", "problem", "links", "effect")
PLAN_PARTS = ("mark", "lane", "cost")
TAP = ["1", "2", "3", "4", "5"]


def is_item(node):
    return node.tag == "section" and "item" in node.classes()


def item_of(node):
    """The nearest item block holding this node, or None."""
    p = node.parent
    while p is not None and not is_item(p):
        p = p.parent
    return p


def headings(root):
    return [re.sub(r"[‘’]", "'", n.text()) for n in root.walk()
            if re.fullmatch(r"h[1-6]", n.tag)]


def source_spans(root):
    """Each "Where this comes from" section, as (parent, first, end) child positions:
    from its heading to the next heading of the same or higher level, or the
    end of the element that holds it."""
    spans = []
    for h in root.walk():
        if re.fullmatch(r"h[1-6]", h.tag) and h.text().lower().startswith("where this comes from"):
            level, kids = int(h.tag[1]), h.parent.children
            first = kids.index(h)
            end = first + 1
            while end < len(kids) and not (isinstance(kids[end], Node) and any(
                    re.fullmatch(r"h[1-6]", n.tag) and int(n.tag[1]) <= level for n in kids[end].walk())):
                end += 1
            spans.append((h.parent, first, end))
    return spans


def words_outside_titleblock(node, skip=()):
    """Every word he could read outside the title block, attributes included,
    leaving out the (parent, first, end) child spans in skip."""
    if is_titleblock(node) or node.tag in NOT_WORDS:
        return
    for name in READ_ATTRS:
        if node.attrs.get(name):
            yield node.attrs[name]
    for i, c in enumerate(node.children):
        if any(p is node and first <= i < end for p, first, end in skip):
            continue
        if isinstance(c, str):
            yield c
        else:
            yield from words_outside_titleblock(c, skip)


def short(text, n=60):
    return text if len(text) <= n else text[: n - 1] + "…"


def in_record(project):
    """The steps whose section of docs/brief.md holds words of its own:
    more than the brief blank's <…> placeholders and its In, Out and Later labels."""
    path = os.path.join(project, "docs", "brief.md")
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    under, step = {}, None
    for line in lines:
        if re.match(r"#{1,2}\s", line):
            step = RECORD_STEP.get(" ".join(line.lower().split()))
        elif step:
            under.setdefault(step, []).append(line)
    return {s for s, body in under.items() if re.search(r"\w", BLANK_ONLY.sub("", "\n".join(body)))}


def check(html, project, page_path=None):
    """Return the list of reasons to refuse; an empty list means ALLOW."""
    root = Tree(html).root
    nodes = list(root.walk())
    faults = []

    pages_dir = os.path.join(project, "docs", "pages")
    sheets = [p for p in glob.glob(os.path.join(pages_dir, "*.html"))
              if not (page_path and os.path.exists(page_path) and os.path.samefile(p, page_path))]
    has_facts = any("facts-sheet" in os.path.basename(p) for p in sheets)
    record = in_record(project)
    missing = [] if has_facts else [(step, heading) for step, heading in RECORD if step not in record]

    # a. The title block: stage and place, and the minutes.
    block = next((n for n in nodes if is_titleblock(n)), None)
    block_text = block.text() if block else ""
    stage = STAGE_PLACE.search(block_text)
    place = int(stage.group(2)) if stage else None
    if not block:
        faults.append("rule 4: no stage and place, because the page has no title block. "
                      "Add the title block from the blank, with the stage and its place "
                      "(like \"Scope · 2 of 6\", or \"Review\") and \"about N minutes\".")
    else:
        if not stage and not REVIEW.search(block_text):
            faults.append("rule 4: no stage and place in the title block. "
                          "Add the stage and its place, like \"Scope · 2 of 6\", or \"Review\" "
                          "on a review page.")
        if not MINUTES.search(block_text):
            faults.append("rule 4: the title block does not say how long the page takes. "
                          "Add \"about N minutes\" and how many questions.")

    # b. Design, Team or Plan only after Problem, Scope and Facts are in the record.
    if place and place >= 4 and missing:
        steps = [step for step, _ in missing]
        names = steps[0] if len(steps) == 1 else ", ".join(steps[:-1]) + " and " + steps[-1]
        heads = ", ".join(f"\"{heading}\"" for _, heading in missing)
        faults.append(f"pages.md, The discovery page (stage {place} of 6): {names} "
                      f"{'is' if len(steps) == 1 else 'are'} not in the record yet. "
                      f"Talk {'it' if len(steps) == 1 else 'each'} through with him, then write his "
                      f"ruling in a decisions entry and under {heads} in docs/brief.md. "
                      "This page comes after that.")

    # c. No calendar dates while Facts is not in the record; a source's file name is not one.
    facts_missing = any(step == "Facts" for step, _ in missing)
    if (place and place <= 3) or (not place and facts_missing and not REVIEW.search(block_text)):
        found = DATE.search(" ".join(" ".join(words_outside_titleblock(root, source_spans(root))).split()))
        if found:
            faults.append(f"pages.md, The discovery page: a date before the facts sheet "
                          f"(\"{found.group(0)}\" appears outside the title block and "
                          "\"Where this comes from\"). "
                          "Give sizes in build days and his hours; dates come once the facts are read.")

    # d. The two bottom sections.
    heads = [h.lower() for h in headings(root)]
    if not any(h.startswith("calls i'm making") for h in heads):
        faults.append("rule 17: no \"Calls I'm making\" heading. Add that section near the end: "
                      "each call you are taking yourself, with its undo.")
    if not any(h.startswith("where this comes from") for h in heads):
        faults.append("rule 21: no \"Where this comes from\" heading. Add that section at the "
                      "very end: the files and pages the sheet was built from.")

    # e. A sheet came before this one: write back what was taken.
    if sheets and not any(h.startswith("what i took") for h in heads):
        faults.append("rule 3: this project already has a sheet, and there is no heading "
                      "starting \"What I took\". Add one at the top, with his last answers as a "
                      "list he can correct.")

    # f. A picture before the first question.
    first_q = next((i for i, n in enumerate(nodes) if is_question(n)), None)
    first_svg = next((i for i, n in enumerate(nodes) if n.tag == "svg"), None)
    if first_svg is None or (first_q is not None and first_svg > first_q):
        faults.append("rule 7: no picture before the first question. Add the mechanism as an "
                      "inline <svg> diagram, with a caption, above the first question.")

    # g. Every question has a box for his words.
    questions = [n for n in nodes if is_question(n)]
    boxless = [n for n in questions if not any(c.tag == "textarea" for c in n.walk())]
    if boxless:
        names = ", ".join(
            short(n.attrs.get("data-q") or next((c.text() for c in n.walk() if c.tag == "legend"), n.text()), 30)
            for n in boxless)
        faults.append(f"rule 15: {len(boxless)} question(s) with no box inside ({names}). "
                      "Put a note box (<textarea>) inside every question block.")

    # h. Nothing asked outside a numbered question.
    loose = [n for n in nodes
             if n.tag in ("label", "figcaption", "h2", "h3")
             and "?" in n.text(NOT_WORDS | {"textarea"})
             and not is_question(n) and not n.inside(is_question)]
    if loose:
        said = "; ".join(f"<{n.tag}> \"{short(n.text(NOT_WORDS | {'textarea'}))}\"" for n in loose)
        faults.append("note 7's line: every question is a numbered question with a legend; "
                      "nothing is asked in a label, a caption or a heading. "
                      f"Found a question outside a numbered question: {said}. "
                      "Make each one a numbered question with its own block, or reword it so "
                      "it asks nothing.")

    # i. One button that copies letters and notes together.
    if not any(n.tag == "button" and "copy" in n.text().lower() and "notes" in n.text().lower()
               for n in nodes):
        faults.append("rule 20: no button that copies his letters and notes together. "
                      "Add the read-back with a \"Copy my letters and notes\" button.")

    # j. The text encoding is declared on the first line.
    if html.lstrip("\ufeff").split("\n", 1)[0].strip().lower() != '<meta charset="utf-8">':
        faults.append("pages.md, How a page is built: the first line is not <meta charset=\"utf-8\">. "
                      "Put that line first, as the blank has it; without it a plain page server "
                      "shows the page's \"·\" as other characters.")

    # k. Each item explained the way a pilot's manual does, and every question inside one.
    items = [n for n in nodes if is_item(n)]

    def name(item):
        h = next((c for c in item.walk() if re.fullmatch(r"h[1-6]", c.tag)), None)
        return short(h.text() if h else item.text(), 30)

    bare = [i for i in items if not any(n.tag == "svg" and item_of(n) is i for n in i.walk())]
    if bare:
        faults.append(f"rule 31: {len(bare)} item block(s) with no picture of its own "
                      f"({', '.join(name(i) for i in bare)}). Draw each item its own inline <svg> "
                      "in a <figure> inside its block: his hand in the second colour, outside the "
                      "system dashed, an arrow from cause to effect. Never one picture for many items.")
    gaps = []
    for i in items:
        found = {n.attrs.get("data-part") for n in i.walk() if item_of(n) is i}
        missing = [p for p in PARTS if p not in found]
        if missing:
            gaps.append(f"{name(i)}: {', '.join(missing)}")
    if gaps:
        faults.append(f"rule 31: item block(s) missing a part ({'; '.join(gaps)}). Every item has "
                      "all four: data-part=\"area\" (the area it belongs to), \"problem\" (the problem "
                      "it solves), \"links\" (the links in the chain around it) and \"effect\" (cause "
                      "and effect).")
    loose_q = [n for n in questions if item_of(n) is None]
    if loose_q:
        names = ", ".join(
            short(n.attrs.get("data-q") or next((c.text() for c in n.walk() if c.tag == "legend"), n.text()), 30)
            for n in loose_q)
        faults.append(f"rule 31: {len(loose_q)} question(s) outside any item block ({names}). "
                      "Put each question inside the <section class=\"item\"> of the evidence it asks about.")

    # l. Each plan item carries its mark, its lane and its cost.
    gaps = []
    for i in (i for i in items if "data-piece" in i.attrs):
        found = {n.attrs.get("data-part") for n in i.walk() if item_of(n) is i}
        missing = [p for p in PLAN_PARTS if p not in found
                   or (p != "cost" and not (i.attrs.get(f"data-{p}") or "").strip())]
        if missing:
            gaps.append(f"{name(i)}: {', '.join(missing)}")
    if gaps:
        faults.append(f"rule 31: plan item(s) missing their mark, lane or cost ({'; '.join(gaps)}). "
                      "A plan item (an item block with data-piece) carries data-mark and data-lane on "
                      "its <section>, and three more parts: data-part=\"mark\" (✅ proven, 📄 documented, "
                      "❓ assumed or ⚠ known risk, with its evidence), \"lane\" and \"cost\" (its share "
                      "of his week).")

    # m. A plan page shows the budget and the hard stop.
    if place == 6:
        for attr, what in (("data-budget", "budget"), ("data-hard-stop", "hard stop")):
            if not any(attr in n.attrs and n.text() for n in nodes):
                faults.append(f"pages.md, The plan page: no {what}. Show it as the blank does, in an "
                              f"element marked {attr}, as a default number he may change when he signs.")

    # n. A review page: "It works" first, the enjoyment tap last.
    if not stage and REVIEW.search(block_text):
        if not items or not re.sub(r"[\"“”]", "", name(items[0])).lower().startswith("it works"):
            faults.append("pages.md, The review page: the first item block is not \"It works\". "
                          "Put it first: each done-when line of the plan, tried, pass or fail.")
        last = questions[-1] if questions else None
        if last is None or [n.attrs.get("value") for n in last.walk()
                            if n.tag == "input" and n.attrs.get("type") == "radio"] != TAP:
            faults.append("pages.md, The review page: the last question is not the enjoyment tap. "
                          "End with it: one numbered question, five letters, 1 to 5.")

    return faults


def main(argv):
    # A page's own words are quoted back; never let the console's code page crash the check.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = argv[1:]
    if len(args) != 3 or args[1] != "--project":
        print("REFUSE: name one page and its project, like: "
              "python template/tools/page_check.py <page.html> --project <project folder>")
        return 1
    page, project = args[0], args[2]
    try:
        if not os.path.isfile(page):
            print(f"REFUSE: no page at {page}")
            return 1
        if not os.path.isdir(project):
            print(f"REFUSE: no project folder at {project}")
            return 1
        with open(page, encoding="utf-8") as f:
            faults = check(f.read(), project, page)
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
