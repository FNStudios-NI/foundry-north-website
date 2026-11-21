# Tests for plan_check.py. Each test writes a plan page under tmp_path,
# breaks one thing in the clean plan, runs the tool as the master would and
# checks that exactly that one refusal comes back.
#   python -B -m pytest template/tools/tests/test_plan_check.py -q

import importlib.util
import os
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plan_check.py")
BLANK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "docs", "blanks", "page.html")

# The clean plan's items: (piece, mark, lane, touches).
ITEMS = [
    ("1", "proven", "full", "template/tools/land.py template/tools/tests/test_land.py"),
    ("2", "documented", "standard", "desks/road/scripts/sync.py"),
    ("3", "proven", "light", "docs/decisions.md docs/archive/decisions-era-2.md"),
]

# Evidence under a question: an item block with no data-piece, never a plan item.
EVIDENCE = ('<section class="item" data-mark="assumed"><h3>What the spike saw</h3>'
            '<fieldset data-q="1"><legend>1. Which road?</legend><textarea></textarea></fieldset></section>')


def page(items=ITEMS, budget="About 6 hours of work, 40% of his week",
         hard_stop="Stop at 14:00, or after 9 pieces",
         acts="The probe: every class allowed. His acts: git push --dry-run, seen working.", extra=""):
    blocks = []
    for item in items:
        attrs = " ".join(f'{name}="{value}"' for name, value in item.items()) if isinstance(item, dict) else (
            f'data-piece="{item[0]}" data-mark="{item[1]}" data-lane="{item[2]}" data-touches="{item[3]}"')
        blocks.append(f'<section class="item" {attrs}><h3>Piece</h3></section>')
    lines = ['<meta charset="utf-8">', "<h1>Plan</h1>"]
    if budget is not None:
        lines.append(f"<p>Budget: <span data-budget>{budget}</span></p>")
    if hard_stop is not None:
        lines.append(f"<p>Hard stop: <span data-hard-stop>{hard_stop}</span></p>")
    if acts is not None:
        lines.append(f"<p>Tried before you sign: <span data-acts-tried>{acts}</span></p>")
    return "\n".join(lines + blocks + [extra]) + "\n"


def run(tmp_path, html):
    path = tmp_path / "plan.html"
    path.write_text(html, encoding="utf-8")
    done = subprocess.run([sys.executable, "-B", TOOL, str(path)], capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout.splitlines()


def refused_once(tmp_path, html, *words):
    code, out = run(tmp_path, html)
    assert code == 1, out
    assert len(out) == 1, out
    assert out[0].startswith("REFUSE: "), out
    for w in words:
        assert w in out[0], out
    return out[0]


def with_item(piece):
    return ITEMS + [piece]


def test_clean_plan_allowed(tmp_path):
    assert run(tmp_path, page()) == (0, ["ALLOW"])


def test_assumed_item_refused(tmp_path):
    refused_once(tmp_path, page(with_item(("4", "assumed", "full", "template/tracks.md"))), "piece 4", "assumed")


def test_risk_item_allowed(tmp_path):
    assert run(tmp_path, page(with_item(("4", "risk", "full", "template/tracks.md")))) == (0, ["ALLOW"])


def test_item_with_no_mark_refused(tmp_path):
    item = {"data-piece": "4", "data-lane": "full", "data-touches": "template/tracks.md"}
    refused_once(tmp_path, page(with_item(item)), "piece 4", "no mark")


def test_item_with_no_lane_refused(tmp_path):
    item = {"data-piece": "4", "data-mark": "proven", "data-touches": "template/tracks.md"}
    refused_once(tmp_path, page(with_item(item)), "piece 4", "no lane")


def test_light_lane_on_a_tool_refused(tmp_path):
    refused_once(tmp_path, page(with_item(("4", "proven", "light", "docs/notes.md tools/plan_check.py"))),
                 "piece 4", "light lane", "tools/plan_check.py")


def test_light_lane_on_a_skill_refused(tmp_path):
    refused_once(tmp_path, page(with_item(("4", "proven", "light", ".claude/skills/run/SKILL.md"))),
                 "piece 4", "light lane", ".claude/skills/run/SKILL.md")


def test_light_lane_under_template_refused(tmp_path):
    refused_once(tmp_path, page(with_item(("4", "proven", "light", "template/operator.md"))),
                 "piece 4", "light lane", "template/operator.md")


def test_light_lane_naming_nothing_refused(tmp_path):
    item = {"data-piece": "4", "data-mark": "proven", "data-lane": "light"}
    refused_once(tmp_path, page(with_item(item)), "piece 4", "names nothing")


def test_no_budget_refused(tmp_path):
    refused_once(tmp_path, page(budget=None), "no budget")


def test_no_hard_stop_refused(tmp_path):
    refused_once(tmp_path, page(hard_stop=None), "no hard stop")


def test_budget_still_a_placeholder_refused(tmp_path):
    refused_once(tmp_path, page(budget="&lt;budget: hours of work, share of his week&gt;"), "budget", "placeholder")


def test_hard_stop_still_a_placeholder_refused(tmp_path):
    refused_once(tmp_path, page(hard_stop="&lt;hard stop&gt;"), "hard stop", "placeholder")


def test_no_acts_tried_refused(tmp_path):
    refused_once(tmp_path, page(acts=None), "no record of the acts tried", "data-acts-tried")


def test_acts_tried_allowed(tmp_path):
    html = page(acts=None)
    assert "data-acts-tried" not in html
    tried = "<p data-acts-tried>The probe: commit and push allowed, merge asks him. His acts: none.</p>"
    assert run(tmp_path, html + tried) == (0, ["ALLOW"])


def test_acts_tried_empty_refused(tmp_path):
    refused_once(tmp_path, page(acts=""), "data-acts-tried", "empty")


def test_acts_tried_still_a_placeholder_refused(tmp_path):
    refused_once(tmp_path, page(acts="&lt;each command you will run, and what was seen&gt;"),
                 "data-acts-tried", "placeholder")


def test_the_blank_as_a_plan_page_holds_placeholders_only():
    with open(BLANK, encoding="utf-8") as f:
        blank = f.read().replace("&lt;Stage&gt; · &lt;n&gt; of 6", "Plan · 6 of 6", 1)
    assert "Plan · 6 of 6" in blank
    # Read in this process: the blank's long placeholders are quoted back cut short, with a "…".
    spec = importlib.util.spec_from_file_location("plan_check_for_the_blank", TOOL)
    plan_check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plan_check)
    out = plan_check.check(blank)
    assert len(out) == 5, out
    assert "no mark" in out[0] and "no lane" in out[1], out
    for line, attr in zip(out[2:], ("data-budget", "data-hard-stop", "data-acts-tried")):
        assert attr in line and "placeholder" in line, out


def test_evidence_block_without_a_piece_ignored(tmp_path):
    assert run(tmp_path, page(extra=EVIDENCE)) == (0, ["ALLOW"])


def test_every_fault_listed(tmp_path):
    items = ITEMS + [("4", "assumed", "light", "template/VERSION"), {"data-piece": "5"}]
    code, out = run(tmp_path, page(items, budget=None, hard_stop="&lt;hard stop&gt;"))
    assert code == 1
    assert len(out) == 6, out
    assert all(line.startswith("REFUSE: ") for line in out), out


# Piece 2 creates a schedule; his act edits it (run 6 lesson 21).
CREATES = ITEMS[:1] + [{"data-piece": "2", "data-mark": "documented", "data-lane": "standard",
                        "data-touches": "desks/road/scripts/sync.py",
                        "data-creates": "schedule:morning-report"}] + ITEMS[2:]


def acts(*lis):
    return "<ol>" + "".join(f"<li {attrs}>Set its model</li>" for attrs in lis) + "</ol>"


def test_act_editing_what_a_piece_creates_ordered_too_early_refused(tmp_path):
    html = page(CREATES, extra=acts('data-act="1" data-edits="schedule:morning-report" data-after="go"'))
    refused_once(tmp_path, html, "act 1 edits schedule:morning-report", "which piece 2 creates",
                 "ordered before it", "Put 2 in its data-after")


def test_act_ordered_after_the_piece_that_creates_what_it_edits_allowed(tmp_path):
    html = page(CREATES, extra=acts('data-act="1" data-edits="schedule:morning-report" data-after="2"'))
    assert run(tmp_path, html) == (0, ["ALLOW"])


def test_act_with_no_edits_refused(tmp_path):
    html = page(CREATES, extra=acts('data-act="1" data-edits="none" data-after="go"', 'data-act="2" data-after="go"'))
    refused_once(tmp_path, html, "act 2 does not say what it edits", 'data-edits="none"')


def test_page_with_no_act_allowed(tmp_path):
    html = page(CREATES)
    assert "data-act=" not in html
    assert run(tmp_path, html) == (0, ["ALLOW"])


# The trials of a signed plan (contract 8; his ruling 4 of 17 Nov 07:43 and call 2).
TRIALS = [
    "the options board a stage earlier · file: desks/hero-film/workflow.md · measure: shots he sends back at the first cut · reads: shots sent back",
    "planned frames · file: desks/hero-film/workflow.md · measure: shots re-rendered after his notes · reads: re-renders",
    "the kit first · file: desks/hero-film/workflow.md · measure: props drawn more than one way · reads: props drawn twice",
    "plates at full size · file: desks/hero-film/workflow.md · measure: his notes on edges and hands · reads: edge notes",
    "the act checks · file: template · measure: sightings per check · reads: sightings",
]


def signed_plan(trials=TRIALS, section=True):
    text = "# Plan for run 3 — test\n\n## The path\n- the film · hero-film\n\n"
    if section:
        text += "## Trials\n" + "".join(f"- {t}\n" for t in trials) + "\n"
    return text + "## Budget and hard stop\n- Budget: 5% of his week\n"


def run_md(tmp_path, text):
    path = tmp_path / "plan-signed.md"
    path.write_text(text, encoding="utf-8")
    done = subprocess.run([sys.executable, "-B", TOOL, str(path)], capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout.splitlines()


def test_a_plan_with_five_trials_allowed(tmp_path):
    assert run_md(tmp_path, signed_plan()) == (0, ["ALLOW"])


def test_a_plan_with_no_trials_section_allowed(tmp_path):
    assert run_md(tmp_path, signed_plan(section=False)) == (0, ["ALLOW"])


def test_a_trial_with_no_measure_refused(tmp_path):
    trials = TRIALS[:4] + ["the act checks · file: template · reads: sightings"]
    code, out = run_md(tmp_path, signed_plan(trials))
    assert code == 1 and out == ['REFUSE: trial "the act checks" has no measure:. '
                                 "Write what its measure says, so the trial can be judged."], out


def test_a_trial_with_no_reads_refused(tmp_path):
    trials = TRIALS[:4] + ["the act checks · file: template · measure: sightings per check"]
    code, out = run_md(tmp_path, signed_plan(trials))
    assert code == 1 and len(out) == 1 and out[0].startswith('REFUSE: trial "the act checks" has no reads:'), out


def test_two_trials_reading_the_same_thing_with_case_and_spaces_aside_refused_naming_both(tmp_path):
    trials = TRIALS[:4] + ["the options board in the player · file: desks/hero-film/workflow.md · "
                           "measure: shots he asks back · reads: Shots  Sent back "]
    code, out = run_md(tmp_path, signed_plan(trials))
    assert code == 1 and len(out) == 1, out
    assert out[0].startswith('REFUSE: trials "the options board a stage earlier" and '
                             '"the options board in the player" both read "Shots  Sent back"'), out


def test_a_sixth_trial_refused(tmp_path):
    trials = TRIALS + ["the render queue · file: desks/hero-film/workflow.md · measure: minutes waiting · reads: minutes waiting"]
    code, out = run_md(tmp_path, signed_plan(trials))
    assert code == 1 and len(out) == 1 and out[0].startswith("REFUSE: the plan carries 6 trials. Five at most"), out
