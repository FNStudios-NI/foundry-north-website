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
spec = importlib.util.spec_from_file_location("scoreboard_for_test", os.path.join(HERE, "..", "scoreboard.py"))
scoreboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoreboard)


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


TWO_TAPS = "the last two questions are not the two taps"


def tap_q(n, html=REVIEW):
    return re.search(r'<section class="q" data-q="%d">.*?</section>' % n, html, flags=re.S).group(0)


def test_n_review_whose_last_question_is_not_the_tap():
    words = ('<section class="q" data-q="5"><h3>5. Enjoyment, and why?</h3>'
             '<label class="box">Your words<textarea data-words></textarea></label></section>')
    faults = page_check.check(REVIEW.replace(tap_q(5), words), EMPTY)
    assert len(faults) == 1 and TWO_TAPS in faults[0], faults


def test_n_a_tap_short_of_five_letters_is_refused():
    html = REVIEW.replace('<label class="opt"><input type="radio" name="q4" value="5">', '<label class="opt"><input type="radio" name="q4" value="x">', 1)
    faults = page_check.check(html, EMPTY)
    assert len(faults) == 1 and TWO_TAPS in faults[0], faults


def test_n_review_with_the_enjoyment_tap_alone_is_refused():
    # The 0.8.0 review: one tap. The thing made comes first now (his ruling 1 of 17 Nov 2026).
    faults = page_check.check(REVIEW.replace(tap_q(4), ""), EMPTY)
    assert len(faults) == 1 and TWO_TAPS in faults[0] and "made" in faults[0], faults


def test_n_review_with_the_taps_the_wrong_way_round_is_refused():
    made, enjoyment = tap_q(4), tap_q(5)
    html = REVIEW.replace(made + "\n    " + enjoyment, enjoyment + "\n    " + made)
    assert html != REVIEW
    faults = page_check.check(html, EMPTY)
    assert len(faults) == 1 and TWO_TAPS in faults[0], faults


# p. the status board first on a plan or review page, and the scoreboard on a review
BOARD = re.search(r'    <section class="status-board" data-status-board>.*?</section>\n', GOOD, flags=re.S).group(0)
NOT_FIRST = "the first element after the title block is not the status board"


def test_p_plan_page_with_no_board_is_refused():
    fault = only_fault(GOOD.replace(BOARD, ""))
    assert fault.startswith("pages.md, The plan page") and NOT_FIRST in fault and "status.py --html" in fault


def test_p_plan_page_with_the_board_under_its_heading_is_refused():
    h1 = "<h1>The plan: what gets built, in what order, and your part in it</h1>"
    html = GOOD.replace(BOARD, "").replace(h1, h1 + "\n" + BOARD)
    assert "data-status-board" in html
    assert NOT_FIRST in only_fault(html)


def test_p_only_a_plan_or_review_page_needs_the_board():
    assert page_check.check(GOOD.replace(BOARD, "").replace("Plan · 6 of 6", "Design · 4 of 6"), FACTS) == []


def test_p_review_with_no_board_is_refused():
    review_board = re.search(r'    <section class="status-board" data-status-board>.*?</section>\n', REVIEW, flags=re.S).group(0)
    faults = page_check.check(REVIEW.replace(review_board, ""), EMPTY)
    assert len(faults) == 1 and faults[0].startswith("pages.md, The review page") and NOT_FIRST in faults[0], faults


SCOREBOARD_SECTION = re.search(r"    <section data-scoreboard>.*?</section>\n", REVIEW, flags=re.S).group(0)


def test_p_review_with_no_scoreboard_is_refused():
    faults = page_check.check(REVIEW.replace(SCOREBOARD_SECTION, ""), EMPTY)
    assert len(faults) == 1 and "no scoreboard" in faults[0] and "--last 5 --html" in faults[0], faults


def scored_project(tmp_path, n=7):
    """A project whose docs/scoreboard.md holds n rows, runs 1 to n."""
    (tmp_path / "docs").mkdir()
    rows = [[str(i), f"2026-11-{i:02d} 18:00", "0.9.0", "4", "5", "3", "—", "2/2", "1", "none", "0", "0", "—"]
            for i in range(1, n + 1)]
    (tmp_path / "docs" / "scoreboard.md").write_text(scoreboard.as_table(rows) + "\n", encoding="utf-8")
    return str(tmp_path), rows


def test_p_review_holding_the_last_five_of_seven_rows_is_allowed(tmp_path):
    project, rows = scored_project(tmp_path)
    html = REVIEW.replace(SCOREBOARD_SECTION, scoreboard.as_html(rows[-5:]) + "\n")
    assert page_check.check(html, project) == []


def test_p_review_holding_the_wrong_rows_is_refused(tmp_path):
    project, rows = scored_project(tmp_path)
    for shown in (rows, rows[:5], rows[-4:]):
        faults = page_check.check(REVIEW.replace(SCOREBOARD_SECTION, scoreboard.as_html(shown) + "\n"), project)
        assert len(faults) == 1 and "not the last 5 of docs/scoreboard.md" in faults[0], faults


def test_p_review_with_fewer_rows_shows_every_row(tmp_path):
    project, rows = scored_project(tmp_path, 3)
    assert page_check.check(REVIEW.replace(SCOREBOARD_SECTION, scoreboard.as_html(rows) + "\n"), project) == []
    faults = page_check.check(REVIEW, project)
    assert len(faults) == 1 and "shows 0 row(s), not the last 3" in faults[0], faults


def test_p_the_blank_carries_the_board_the_scoreboard_and_the_two_taps():
    as_review = BLANK.replace("&lt;Stage&gt; · &lt;n&gt; of 6", "Review", 1)
    faults = page_check.check(as_review, EMPTY)
    assert not [f for f in faults if NOT_FIRST in f or "scoreboard" in f or TWO_TAPS in f], faults


# q. a page sent to someone else, or a board of options he marks: the read-back only
SENT = ('<meta charset="utf-8">\n<title>For the builder</title>\n<body data-page-kind="%s">\n'
        '<h2>Which day suits you?</h2><p>Monday 2026-11-23, or Tuesday.</p>\n'
        '<label>Your note<textarea></textarea></label>\n'
        '<button type="button">Copy my letters and notes</button>\n</body>\n')


@pytest.mark.parametrize("kind", ["sent", "board"])
def test_q_a_sent_page_or_a_board_is_checked_for_its_read_back_only(kind):
    # No title block, no picture, a question in a heading, a box outside a question: all skipped.
    assert page_check.check(SENT % kind, EMPTY) == []
    faults = page_check.check((SENT % kind).replace("Copy my letters and notes", "Send"), EMPTY)
    assert len(faults) == 1 and faults[0].startswith("rule 20"), faults


def test_q_any_other_kind_is_checked_whole():
    faults = page_check.check(SENT % "notes", EMPTY)
    assert any(f.startswith("rule 4") for f in faults) and any(f.startswith("rule 7") for f in faults), faults


# r. a closed run and no workflow file: his own needs-thought question, naming the work (L040)
CLOSED_RUN = "# Decisions\n\n## 2026-11-19 01:51 — Run 7 closed (master)\nKept.\n"
WORKFLOW_FILE = ("# Grading — v1.0\n\nVersion: v1.0\nTag: `idea`\n\n## Steps\n"
                 "1. **Grade** · `idea` · the master — in: the cut — out: the grade — because.\n")
NOT_ASKED = "pages.md, The workflow question: this project has closed a run and has no workflow file"
NO_WORK = "pages.md, The workflow question: the question marked data-needs-thought=\"workflow\" does not name"
MARKED = 'data-needs-thought="workflow" data-work="colour grading"'


def closed_project(tmp_path, source=FACTS, decisions=CLOSED_RUN):
    root = tmp_path / os.path.basename(source)
    shutil.copytree(source, root)
    if decisions:
        (root / "docs").mkdir(exist_ok=True)
        (root / "docs" / "decisions.md").write_text(decisions, encoding="utf-8")
    return str(root)


def asked(attrs=MARKED, words="colour grading"):
    """The good plan page with its second question put as the workflow question."""
    return broken('<section class="q" data-q="2">', f'<section class="q" data-q="2" {attrs}>').replace(
        "2. What would count as success?", f"2. Should {words} get a workflow file of its own?")


def test_a_closed_run_with_no_workflow_and_no_question_is_refused(tmp_path):
    assert only_fault(GOOD, closed_project(tmp_path)).startswith(NOT_ASKED)
    review = closed_project(tmp_path, EMPTY)
    assert only_fault(REVIEW, review).startswith(NOT_ASKED)
    # A page sent to someone else, or a board he marks, is still read for its read-back alone.
    assert page_check.check(SENT % "sent", review) == [] and page_check.check(SENT % "board", review) == []


def test_the_board_line_alone_is_refused(tmp_path):
    board = '    <section class="status-board" data-status-board>\n<h2>status board</h2>\n<p>workflows: none</p>\n</section>\n'
    assert only_fault(broken(BOARD, board), closed_project(tmp_path)).startswith(NOT_ASKED)


def test_the_workflow_question_naming_the_work_passes(tmp_path):
    root = closed_project(tmp_path)
    assert page_check.check(asked(), root) == []
    assert page_check.check(asked(words="Colour  grading"), root) == []  # his sentence's capitals and spacing


def test_a_workflow_question_naming_no_work_is_refused(tmp_path):
    root = closed_project(tmp_path)
    for page in (asked('data-needs-thought="workflow"'),                                  # no data-work
                 asked('data-needs-thought="workflow" data-work="  "'),                   # data-work with no words
                 asked(words="this kind of work"),                                        # other words in its text
                 asked(words="colour gradings"),                                          # not those same words
                 asked(words="this work").replace('scanned and marked"></textarea>',
                                                  'scanned and marked">colour grading</textarea>')):  # only in his box
        assert only_fault(page, root).startswith(NO_WORK)
    # The mark on anything but a question is no question.
    page = broken('<section class="q" data-q="2">', f'<section class="q" data-q="2"><p {MARKED}>colour grading</p>')
    assert only_fault(page, root).startswith(NOT_ASKED)


def test_a_project_with_a_workflow_file_is_not_asked(tmp_path):
    root = closed_project(tmp_path)
    with open(os.path.join(root, "docs", "grading.md"), "w", encoding="utf-8") as f:
        f.write(WORKFLOW_FILE)
    assert page_check.check(GOOD, root) == []


def test_a_project_with_no_closed_run_is_not_asked(tmp_path):
    (tmp_path / "none").mkdir()
    assert page_check.check(GOOD, closed_project(tmp_path / "none", decisions=None)) == []
    (tmp_path / "open").mkdir()
    still_open = "# Decisions\n\n## 2026-11-19 01:51 — Run 8 asked for\nRun 7 closed last week, in a sentence.\n"
    assert page_check.check(GOOD, closed_project(tmp_path / "open", decisions=still_open)) == []


# o. a review page of a project with docs/lessons.md holds the upgrade
LESSONS = os.path.join(PAGES, "lessons-project")
UPGRADE_PATH = os.path.join(PAGES, "sample-review-upgrade.html")
UPGRADE = read(UPGRADE_PATH)


def upgrade_faults(html, project=LESSONS):
    return [f for f in page_check.check(html, project) if "upgrade" in f]


def only_upgrade_fault(html):
    faults = page_check.check(html, LESSONS)
    assert len(faults) == 1 and "upgrade" in faults[0], faults
    return faults[0]


def group(kind):
    """The sample's group of this kind, whole, as it stands in the page."""
    return re.search(r'    <div class="group" data-group="%s">.*?\n    </div>\n' % kind, UPGRADE, flags=re.S).group(0)


def test_upgrade_filled_sample_is_allowed_with_a_lessons_file(capsys):
    assert os.path.isfile(os.path.join(LESSONS, "docs", "lessons.md"))
    assert page_check.main(["page_check.py", UPGRADE_PATH, "--project", LESSONS]) == 0
    assert capsys.readouterr().out.strip() == "ALLOW"


def test_upgrade_old_sample_is_refused_with_a_lessons_file():
    fault = only_upgrade_fault(REVIEW)
    assert fault.startswith("pages.md, The review page: no upgrade section")


def test_upgrade_old_sample_is_allowed_without_a_lessons_file():
    assert not os.path.exists(os.path.join(EMPTY, "docs", "lessons.md"))
    assert page_check.check(REVIEW, EMPTY) == []


def test_upgrade_section_after_the_tap_is_refused():
    start = UPGRADE.index("  <!-- The upgrade:")
    end = UPGRADE.index("  <!-- The pieces:")
    section = UPGRADE[start:end]
    html = UPGRADE[:start] + UPGRADE[end:]
    at = html.index('  <section class="calls stack">')
    html = html[:at] + section + html[at:]
    # Its questions now follow the tap, so check n refuses too; check o names the upgrade's place.
    faults = upgrade_faults(html)
    assert len(faults) == 1 and "not before the two taps" in faults[0], faults


def test_upgrade_needs_thought_not_first_is_refused():
    thought, lines = group("needs-thought"), group("lines")
    html = UPGRADE.replace(thought + "\n" + lines, lines + "\n" + thought)
    assert html != UPGRADE
    assert "needs-thought group is not first" in only_upgrade_fault(html)


def test_upgrade_lines_group_with_two_questions_is_refused():
    lines = group("lines")
    q = re.search(r'<section class="q" data-q="5">.*?</section>', lines, flags=re.S).group(0)
    html = UPGRADE.replace(lines, lines.replace(q, q + q.replace('data-q="5"', 'data-q="5b"')))
    assert "lines group holds 2 questions" in only_upgrade_fault(html)


def test_upgrade_lines_question_without_approve_all_is_refused():
    html = UPGRADE.replace("<legend>5. Approve all my leans on these lines</legend>",
                           "<legend>5. My leans on these lines</legend>")
    html = html.replace("<b>a.</b> Approve all my leans", "<b>a.</b> Take my leans")
    html = html.replace("<b>b.</b> Approve all but", "<b>b.</b> Take all but")
    assert "does not say \"approve all\"" in only_upgrade_fault(html)


def test_upgrade_foundations_block_with_no_question_is_refused():
    found = group("foundations")
    q = re.search(r'<section class="q" data-q="6">.*?</section>', found, flags=re.S).group(0)
    fault = only_upgrade_fault(UPGRADE.replace(found, found.replace(q, "")))
    assert "foundations item" in fault and "holds 0 questions" in fault


def test_upgrade_empty_group_without_none_is_refused():
    track = group("tracks")
    empty = '    <div class="group" data-group="tracks">\n      <h3>Candidate tracks</h3>\n    </div>\n'
    fault = only_upgrade_fault(UPGRADE.replace(track, empty))
    assert "tracks group holds nothing" in fault
    said_none = empty.replace("<h3>Candidate tracks</h3>", "<h3>Candidate tracks</h3><p>None.</p>")
    assert page_check.check(UPGRADE.replace(track, said_none), LESSONS) == []


@pytest.mark.parametrize("old,new", [("foundations", "lock"), ("trials", "unlock"), ("tracks", "track")])
def test_upgrade_a_group_named_by_the_old_words_is_refused(old, new):
    html = UPGRADE.replace(f'data-group="{old}"', f'data-group="{new}"')
    fault = only_upgrade_fault(html)
    assert f"group name(s) {new} are not the upgrade's groups" in fault and "foundations" in fault


def test_upgrade_the_locked_group_is_refused_and_foundation_is_read():
    every = '    <div class="group" data-group="%s">\n      <h3>Foundations</h3><p>None.</p>\n    </div>\n'
    at = UPGRADE.index('    <div class="group" data-group="template">')
    assert "group name(s) locked are not" in only_upgrade_fault(UPGRADE[:at] + every % "locked" + UPGRADE[at:])
    assert page_check.check(UPGRADE[:at] + every % "foundation" + UPGRADE[at:], LESSONS) == []


def test_upgrade_the_blank_holds_the_section_in_order():
    up = BLANK.index("data-upgrade")
    kinds = re.findall(r'data-group="([a-z-]+)"', BLANK[up:])
    assert kinds == ["needs-thought", "lines", "foundations", "tracks", "trials", "template"]
    as_review = BLANK.replace("&lt;Stage&gt; · &lt;n&gt; of 6", "Review", 1)
    assert upgrade_faults(as_review) == []


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
