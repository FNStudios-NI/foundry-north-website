DONE — <what is true now, in one line> | NOT DONE — <why> | REFUSED — <which refusal>

# Receipt — <card-name> — <yyyy-mm-dd>

Card: `<path to the card>` · Branch: `<branch>` · Worker: <model> in `<worktree>`
<This file is the proof. The checker reads it, and it becomes the pull request's description. Delete this line.>

## Shipped
<five lines at most: what changed and where. Never wider than the card's Goal.>

## Test it
<each command you ran, and the exact output you saw, at <commit>. If you could not run one, write "not run by the worker" and why.>

## Unsure
<every call the master or Rhys might reverse. This section is read first.>

## Parked
<one line per problem the card did not name. Not fixed.>

## Drift
<anything written outside the card's Touches, named. Or "none".>

## Refused
<which refusal, and what it wanted to do. Or "none".>

## Lessons:
<one line per lesson, `<kind> · <what happened> · file: <file> · "<the exact line>"` (kind: change, works, misfire or track; a works or misfire ends ` · seen: <his verdict, a number or a pass line>`), or "none". The master adds the rest (the number, the time, where from) with `python tools/record.py --lesson`. Why: one writer for the record; the lessons file is the one place for every log (`tracks.md` rule 24).>

## Checker run <yyyy-mm-dd> — <who>, own session
<the worker deletes this whole block; the checker appends its own>   <why: a block the worker left in reached the checker with a second Verdict line, which merge_check refuses>   <the heading and its Commit:, Exit code: and From a clean copy: lines are written by `python tools/check.py <receipt> --card <card> --who "<who>, own session" --scratch <folder>` from a clean copy of the commit, never typed; the checker writes the four lines below>
Shown failing: <the ablation the checker ran, and what failed>
Scope: <the checker's answer to "is anything in this diff not asked for by the card?">
Verdict: <PASS or FAIL, alone on the line>
Why: <any summary of the verdict goes here, never on a second Verdict line>
<written by the checker, never by the worker: red before the change; the ablation; the diff read whole; the work compared against the card's asks; the verdict. The Commit, Exit code, From a clean copy, Shown failing and Verdict lines are read by `tools/merge_check.py`: keep their words as they are. Exactly one line in this block starts with `Verdict`: `Verdict: PASS` or `Verdict: FAIL`, alone; any summary goes under `Why:`. Two Verdict lines are refused.>
