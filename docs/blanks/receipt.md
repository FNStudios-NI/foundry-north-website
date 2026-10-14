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

## Checker run <yyyy-mm-dd> — <who>, own session
Commit: <the full commit id the checker ran at>
Exit code: <the command's exit code>
Verdict: <PASS or FAIL, alone on the line>
Why: <any summary of the verdict goes here, never on a second Verdict line>
<written by the checker, never by the worker: the command and its count; red before the change; the ablation; the diff read whole; the work compared against the card's asks; the verdict. The Commit, Exit code and Verdict lines are read by `tools/merge_check.py`: keep their words as they are. Exactly one line in this block starts with `Verdict`: `Verdict: PASS` or `Verdict: FAIL`, alone; any summary goes under `Why:`. Two Verdict lines are refused.>
