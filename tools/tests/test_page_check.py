# Tests for page_check.py. Each refusal is shown by breaking one thing in
# the good plan page (in memory, never on disk) and checking that exactly
# that one refusal comes back.
#   python -B -m pytest template/tools/tests/test_page_check.py -q

import importlib.util
import os
import re
import shutil

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "pages")
EMPTY = os.path.join(PAGES, "empty-project")
FACTS = os.path.join(PAGES, "facts-project")
TALKED = os.path.join(PAGES, "talked-project")
NO_FACTS = os.path.join(PAGES, "talked-no-facts")
BRIEF_BLANK_PATH = os.path.join(HERE, "..", "..", "docs", "blanks", "brief.md")
GOOD_PATH = os.path.join(PAGES, "good-plan.html")
SHEET4_PATH = os.path.join(PAGES, "sheet-4.html")
SAMPLE_REVIEW_PATH = os.path.join(PAGES, "sample-review.html")

spec = importlib.util.spec_from_file_location("page_check", os.path.join(HERE, "..", "page_check.py"))
page_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page_check)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


GOOD = read(GOOD_PATH)


def broken(old, new, count=1):
    """The good page with one thing changed; fails loudly if the thing is not there."""
    assert old in GOOD, f"fixture has no {old!r}"
    return GOOD.replace(old, new, count)


def only_fault(html, project=FACTS):
    faults = page_check.check(html, project)
    assert len(faults) == 1, faults
    return faults[0]


def test_good_plan_is_allowed(capsys):
    assert page_check.main(["page_check.py", GOOD_PATH, "--project", FACTS]) == 0
    assert capsys.readouterr().out.strip() == "ALLOW"


def test_sample_review_is_allowed(capsys):
    # The forks page the master shows him: three forks, each its own item block (pages.md § The review page).
    assert page_check.main(["page_check.py", SAMPLE_REVIEW_PATH, "--project", EMPTY]) == 0
    assert capsys.readouterr().out.strip() == "ALLOW"


def test_sheet_4_is_refused_for_its_five_known_faults(capsys):
    assert page_check.main(["page_check.py", SHEET4_PATH, "--project", EMPTY]) == 1
    out = capsys.readouterr().out
    assert all(line.startswith("REFUSE: ") for line in out.splitlines())
    for words in ("no stage and place", "a date before the facts sheet",
                  "no \"Calls I'm making\"", "no \"Where this comes from\"",
                  "a question outside a numbered question"):
        assert words in out


# a. title block
def test_a_no_stage_and_place():
    assert "rule 4: no stage and place" in only_fault(broken("Plan · 6 of 6", "Plan"))


def test_a_review_counts_as_stage_and_place():
    # The plan page made a review is refused only for the review's own shape (n), never for rule 4.
    faults = page_check.check(broken("Plan · 6 of 6", "Review"), FACTS)
    assert all(f.startswith("pages.md, The review page") for f in faults), faults


def test_a_no_minutes():
    assert "rule 4: the title block does not say how long" in only_fault(
        broken("about 10 minutes · 2 questions", "2 questions"))


# b. design, team or plan before problem, scope and facts are in the record
ALL_THREE = "Problem, Scope and Facts are not in the record yet"


def design():
    return broken("Plan · 6 of 6", "Design · 4 of 6")


def test_b_plan_page_with_no_facts_sheet():
    fault = only_fault(GOOD, EMPTY)
    assert ALL_THREE in fault and "decisions entry" in fault and "facts sheet" not in fault


def test_b_design_page_with_the_three_steps_in_the_record():
    assert page_check.check(design(), TALKED) == []


def test_b_design_page_with_facts_missing_names_facts_alone():
    fault = only_fault(design(), NO_FACTS)
    assert "Facts is not in the record yet" in fault
    assert "Problem" not in fault and "Scope" not in fault


def test_b_plan_page_with_the_record_and_no_sheet(capsys):
    # 9 Oct: the early steps were talked through on his word, and no page was made for them.
    assert not os.path.exists(os.path.join(TALKED, "docs", "pages"))
    assert page_check.main(["page_check.py", GOOD_PATH, "--project", TALKED]) == 0
    assert capsys.readouterr().out.strip() == "ALLOW"


def test_b_the_brief_blank_as_a_brief_names_all_three(tmp_path):
    os.makedirs(tmp_path / "docs")
    shutil.copy(BRIEF_BLANK_PATH, tmp_path / "docs" / "brief.md")
    assert ALL_THREE in only_fault(GOOD, str(tmp_path))


def test_b_facts_sheet_and_no_brief_still_passes():
    assert not os.path.exists(os.path.join(FACTS, "docs", "brief.md"))
    assert page_check.check(design(), FACTS) == []


# c. a calendar date on a stage 1 to 3 page
def test_c_date_on_a_scope_page():
    fault = only_fault(broken("Plan · 6 of 6", "Scope · 2 of 6"))
    assert "a date before the facts sheet" in fault and "20 October" in fault


def test_c_iso_date_counts_and_title_block_does_not():
    html = broken("Plan · 6 of 6", "Facts · 3 of 6").replace("around 20 October", "soon")
    html = html.replace("<div><b>Sheet</b>", "<div><b>Date</b>5 Oct 2026</div><div><b>Sheet</b>")
    assert page_check.check(html, FACTS) == []
    assert "2026-10-20" in only_fault(html.replace("soon", "on 2026-10-20"))


SOURCE = "<li>The facts sheet, and your message after sheet 4.</li>"
DATED_SOURCE = SOURCE + "<li>2026-10-05-first-walk.html</li>"


def test_c_dated_file_name_under_where_this_comes_from_is_allowed():
    html = broken("Plan · 6 of 6", "Scope · 2 of 6").replace("around 20 October", "soon")
    assert page_check.check(html.replace(SOURCE, DATED_SOURCE), FACTS) == []


def test_c_same_date_in_the_body_is_refused():
    html = broken("Plan · 6 of 6", "Scope · 2 of 6").replace("around 20 October", "soon")
    html = html.replace("soon", "soon (see 2026-10-05-first-walk.html)")
    fault = only_fault(html, FACTS)
    assert "a date before the facts sheet" in fault and "2026-10-05" in fault


def test_c_a_page_with_no_stage_is_held_while_facts_is_not_in_the_record():
    # The good page's "around 20 October", on a page whose stage cannot be read.
    html = broken("Plan · 6 of 6", "Plan")
    assert "rule 4" in only_fault(html, TALKED)
    faults = page_check.check(html, NO_FACTS)
    assert len(faults) == 2 and any("a date before the facts sheet" in f for f in faults), faults


# d. the two bottom headings
def test_d_no_calls_im_making():
    assert "rule 17" in only_fault(broken("<h2>Calls I'm making</h2>", "<h2>My calls</h2>"))


def test_d_no_where_this_comes_from():
    assert "rule 21" in only_fault(broken("<h2>Where this comes from</h2>", "<h2>Sources</h2>"))


# e. a sheet came before, and nothing is written back
def test_e_no_what_i_took():
    fault = only_fault(broken("<h2>What I took from your message</h2>", "<h2>Your answers</h2>"))
    assert "rule 3" in fault


# f. no picture before the first question
def test_f_no_svg():
    # With every picture gone, each item block is refused too (k); nothing else is.
    faults = page_check.check(re.sub(r"<svg.*?</svg>", "", GOOD, flags=re.S), FACTS)
    assert any(f.startswith("rule 7") for f in faults)
    assert all(f.startswith(("rule 7", "rule 31")) for f in faults), faults


def test_f_svg_after_the_first_question():
    # The page's own picture goes, and item 1's picture moves under its question.
    svgs = re.findall(r"<svg.*?</svg>", GOOD, flags=re.S)
    html = GOOD.replace(svgs[0], "")
    q1 = re.search(r'<section class="q" data-q="1">.*?</section>', html, flags=re.S).group(0)
    html = html.replace(svgs[1], "").replace(q1, q1 + svgs[1])
    assert "rule 7" in only_fault(html)


# g. a question with no box
def test_g_question_with_no_textarea():
    html = broken('<label class="box">Note for question 1<textarea data-note placeholder="Anything to add or change (optional)"></textarea></label>', "")
    assert "rule 15" in only_fault(html)


# h. a question asked outside a numbered question
def test_h_question_in_a_caption():
    html = broken("the dashed step happens outside the system.</figcaption>",
                  "the dashed step happens outside the system. Is that clear?</figcaption>")
    fault = only_fault(html)
    assert "a question outside a numbered question" in fault and fault.startswith("note 7's line")


def test_h_question_in_a_label_outside_the_fieldset():
    # Sheet 4's fault: a question hidden in a note box's label, outside the numbered fieldset.
    html = ('<svg></svg><div class="q"><fieldset><legend>1. Which?</legend><textarea></textarea></fieldset>'
            '<label>Note for question 1, and where is it?</label><textarea></textarea></div>')
    faults = page_check.check(html, EMPTY)
    assert any("a question outside a numbered question" in f and "where is it" in f for f in faults)


# i. no copy button for letters and notes
def test_i_no_copy_button():
    assert "rule 20" in only_fault(broken(">Copy my letters and notes<", ">Copy my letters<"))


# j. no charset line first
def test_j_no_charset_line():
    fault = only_fault(broken('<meta charset="utf-8">\n', ""))
    assert fault.startswith("pages.md, How a page is built") and 'charset="utf-8"' in fault


# k. every item explained the way a pilot's manual does, and every question inside an item
ITEM_1 = '<section class="item stack" id="path">'
ITEM_2 = '<section class="item stack" id="done">'


def item(n):
    start = GOOD.index(ITEM_1 if n == 1 else ITEM_2)
    return start, GOOD.index('<section class="q"', start)


def test_k_item_with_no_picture():
    start, end = item(1)
    svg = re.search(r"<svg.*?</svg>", GOOD[start:end], flags=re.S).group(0)
    fault = only_fault(GOOD[:start] + GOOD[start:end].replace(svg, "") + GOOD[end:])
    assert fault.startswith("rule 31") and "no picture of its own" in fault and "Two paths" in fault


def test_k_item_missing_a_part():
    start, end = item(2)
    part = re.search(r'<div data-part="links">.*?</div>', GOOD[start:end], flags=re.S).group(0)
    fault = only_fault(GOOD[:start] + GOOD[start:end].replace(part, "") + GOOD[end:])
    assert fault.startswith("rule 31") and "missing" in fault and "links" in fault


def test_k_question_outside_any_item():
    fault = only_fault(broken(ITEM_2, '<section class="stack" id="done">'))
    assert fault.startswith("rule 31") and "outside any item" in fault and "2" in fault


BLANK = read(os.path.join(HERE, "..", "..", "docs", "blanks", "page.html"))


def test_k_the_blank_holds_it():
    assert BLANK.count('<section class="item') >= 1
    assert not [f for f in page_check.check(BLANK, FACTS) if f.startswith("rule 31")]


# l. every plan item carries its mark, its lane and its cost
PIECE = '<section class="item stack" id="piece-1" data-piece="1" data-mark="proven" data-lane="standard"'


def piece_without(old, new=""):
    start = GOOD.index(PIECE)
    end = GOOD.index("</section>", start)
    assert old in GOOD[start:end], f"plan item has no {old!r}"
    return GOOD[:start] + GOOD[start:end].replace(old, new, 1) + GOOD[end:]


def test_l_plan_item_missing_its_mark():
    part = re.search(r'<div data-part="mark">.*?</div>', GOOD, flags=re.S).group(0)
    fault = only_fault(piece_without(part))
    assert fault.startswith("rule 31") and "Naming and sorting: mark" in fault


def test_l_plan_item_missing_its_lane():
    fault = only_fault(piece_without(' data-lane="standard"'))
    assert fault.startswith("rule 31") and "Naming and sorting: lane" in fault


def test_l_plan_item_missing_its_cost():
    part = re.search(r'<div data-part="cost">.*?</div>', GOOD, flags=re.S).group(0)
    fault = only_fault(piece_without(part))
    assert fault.startswith("rule 31") and "Naming and sorting: cost" in fault


def test_l_an_item_with_no_piece_needs_none():
    # The forks on the good plan carry no mark, lane or cost, and are allowed: only data-piece asks for them.
    html = piece_without(' data-piece="1"')
    for part in ("mark", "lane", "cost"):
        html = re.sub(r'<div data-part="%s">.*?</div>' % part, "", html, flags=re.S)
    assert page_check.check(html, FACTS) == []


# m. a plan page shows the budget and the hard stop
def test_m_plan_page_with_no_budget():
    fault = only_fault(broken("<div data-budget>", "<div>"))
    assert fault.startswith("pages.md, The plan page") and "no budget" in fault


def test_m_plan_page_with_no_hard_stop():
    fault = only_fault(broken("<div data-hard-stop>", "<div>"))
    assert fault.startswith("pages.md, The plan page") and "no hard stop" in fault


def test_m_only_a_plan_page_needs_them():
    html = broken("<div data-budget>", "<div>").replace("<div data-hard-stop>", "<div>")
    assert page_check.check(html.replace("Plan · 6 of 6", "Design · 4 of 6"), FACTS) == []


def test_lm_the_blank_as_a_plan_page_holds_them():
    blank = BLANK.replace("&lt;Stage&gt; · &lt;n&gt; of 6", "Plan · 6 of 6", 1)
    assert "Plan · 6 of 6" in blank and 'data-piece="' in blank
    assert not [f for f in page_check.check(blank, FACTS)
                if f.startswith(("rule 31", "pages.md, The plan page"))]


# n. a review page: "It works" first, the enjoyment tap last
REVIEW = read(SAMPLE_REVIEW_PATH)


def test_n_review_whose_first_item_is_not_it_works():
    html = REVIEW.replace("<h2>It works</h2>", "<h2>What was built</h2>", 1)
    faults = page_check.check(html, EMPTY)
    assert len(faults) == 1 and "the first item block is not \"It works\"" in faults[0], faults


def test_n_review_whose_last_question_is_not_the_tap():
    tap = re.search(r'<section class="q" data-q="4">.*?</section>', REVIEW, flags=re.S).group(0)
    words = ('<section class="q" data-q="4"><h3>4. Enjoyment, and why?</h3>'
             '<label class="box">Your words<textarea data-words></textarea></label></section>')
    faults = page_check.check(REVIEW.replace(tap, words), EMPTY)
    assert len(faults) == 1 and "the last question is not the enjoyment tap" in faults[0], faults


def test_n_a_tap_short_of_five_letters_is_refused():
    html = REVIEW.replace('<label class="opt"><input type="radio" name="q4" value="5">', '<label class="opt"><input type="radio" name="q4" value="x">', 1)
    faults = page_check.check(html, EMPTY)
    assert len(faults) == 1 and "enjoyment tap" in faults[0], faults


def test_the_tool_writes_nothing(capsys):
    def snapshot():
        return sorted((root, tuple(sorted(files)), tuple(sorted(dirs)))
                      for root, dirs, files in os.walk(os.path.dirname(HERE)))
    before = snapshot()
    page_check.main(["page_check.py", SHEET4_PATH, "--project", EMPTY])
    page_check.main(["page_check.py", GOOD_PATH, "--project", FACTS])
    assert snapshot() == before


@pytest.mark.parametrize("argv", [[], ["x.html"], ["x.html", "--project"], ["x.html", "--nope", "y"]])
def test_bad_arguments_refuse(argv, capsys):
    assert page_check.main(["page_check.py", *argv]) == 1
    assert capsys.readouterr().out.startswith("REFUSE: ")
