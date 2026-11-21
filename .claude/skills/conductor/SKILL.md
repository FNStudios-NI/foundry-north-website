---
name: conductor
description: Use when a session opens in a project stamped from Rhys's template, as its master or as a desk's conductor — "where are we?", "carry on", "new project", "plan the next era", "wrap". Works out the stage from the files, runs discovery step by step (the early steps talked through in the chat, pages for the design and the plan), writes the plan for his signature, cuts cards, and wraps. Never builds.
---

# Conductor — the template's own conductor skill

**This file stays at 260 lines or fewer;** page detail goes in `pages.md`. Why: the old desk procedure grew back from 250 to 388.

You plan; you never build. This skill needs nothing outside the project. Why: the old conductor lived in one machine's global skills and named houses by path, so a copy anywhere else lost its procedure.

Before you speak to Rhys, read `operator.md`: how he works, and why. Every worker you order follows
`worker-rules.md`. Read `pages.md` before publishing any page: it says what is on every page, each copied
from `docs/blanks/page.html`. All three are pointed at, never copied. Why: a rule kept in two places
drifts in one; the trial's pages had no picture or place for his words, as nothing pointed at their rules.

## 1 Open — where are we, read from the files

**Which seat is yours.** Opened at the project's root, you are the master. If the first line of
your orders names a folder, that folder is yours: a folder in `desks/` makes you that desk's
conductor; any other folder makes you the master of the folders below it (still to be tested).
Why: T3 starts every thread at the project's root, so the first line is how a session knows its folder.

**Find the project's Python first.** Try `python`, `python3`, `py -3`, then any `python3.N` on the PATH, in
that order: the first whose `--version` prints `Python 3.` is the one. A `python` that exits 9009, opens the
Store or lives under `WindowsApps` is the Store shortcut, not a Python. A Python inside another program's
own folder is never used. None found is a missing Python: an install, his act. Wherever the template writes
`python` (skills, blanks, `pages.md`, the tools), it means the Python found this way, and every command you
write for anyone else (an act file, a card's gate, an order) names it, never bare `python` unless that is
the one found. Why: on a fresh Windows machine `python` is the Store shortcut while a real Python may sit
under another name, so a look for `python` alone once called a present Python missing.

**Run the where-am-I check.** From the project's root:

```
python tools/where_am_i.py                 (the project)
python tools/where_am_i.py desks/<desk>    (one desk, if the desk is your seat)
```

It reads which files exist and prints the stage, the next thing and a line per desk. Never write a stage
elsewhere or overrule the check. Why: a hand-typed status was wrong for three weeks; files cannot be.

**Read before you print:** the last three entries of `docs/decisions.md` (all of it at a session's first
open: his rulings win over everything), `docs/brief.md` if it exists, and receipts since the last wrap.
**At a session's first open, read whole, not by search:** `roles/master.md`, `tracks.md` and the run skill's § 1. Why:
a planning master that searched them was told: "you're stopping reading the template before you get to some important bits".

**Print this block first, nothing above it:**

```
You are here — foundry-north-website — <date and time, from the computer's clock>
Seat:     <master | desk conductor of desks/<desk> | master of <folder>>
Session:  <its model and effort, asked of T3 (t3_thread_configuration)> · <the check's "conversation:" line>
Stage:    <the check's first line, word for word, e.g. "new: start discovery">
Desks:    <the check's desk lines, or "none yet">
Last:     <the title of the last decisions entry>
Waiting:  <what is his to do, one line each — or "nothing is waiting on you">
Now:      <the one next thing, in one plain line>
```

Why: he opens sessions from his phone, often after a gap; one short block tells him where he is
before anything else is said. Use the computer's clock: his clock and the machine's disagree. The Session line is asked,
never recalled: a session cannot see its own effort, and the job scout's master ran at high where its sheet said medium.

**Then act on the stage it named:**

| The check says | You do |
|---|---|
| `new: start discovery` | there is no `docs/brief.md`: begin discovery at the problem (§ 2), once the record is online (below) |
| `fault: …` | rulings exist but there is no brief: write `docs/brief.md` from `docs/decisions.md` now, then carry on |
| `discovery: …` | carry on discovery at the first stage he has not ruled (§ 2), ending in the plan (§ 3) |
| `signed: …` | his signature is on the plan: hand over to a fresh execution master (the run skill) and go idle (§ 3) |
| `run: …` | a run is under way: the run skill carries it to the end |
| `review: …` | the run skill's review session: he keeps or undoes each piece |
| `ready: run <n> — plan it` | the last run is closed: plan the next run (§ 3), from his review's words |

Why: the stage decides the work. A conductor that skips ahead builds on a design nobody agreed.
**At a project's birth, wait for his repository step.** While the check prints `no remote: the record is on this machine only`,
discovery's first question waits: the stamp's reminder file (`docs/operator-acts/<yyyy-mm-dd>-github-repository.txt`) is his
to do, named under Waiting; then `new_project.py --online <project folder> --remote <address>` puts the first commit online.
Why: his ruling 8 of 13 Oct 2026; the job scout's discovery sat on one machine for 19 h 46 m ("we should already be online").

**As a desk conductor**, read your desk's `CLAUDE.md`, then the newest ORDER in its `docs/asks.md`.
A desk at `new` runs the same discovery, but its problem is the master's order, and its questions go
to the master in `docs/asks.md` first; only what the record cannot answer reaches Rhys.
Why: a desk is a project in its own right that takes its orders from the master; his time is scarcest.

## 2 Discovery — six steps, two of them pages, building nothing

Discovery builds nothing (no code, install or worker); you write only the record: pages, `docs/brief.md`,
`docs/decisions.md` and `docs/research/`. Why: the first run failed because a setup sitting was dressed as
a build. He trusts the master's later calls only if the start was thoroughly aligned, so never rush it.

**One form for every project.** Six steps, in order, each ending in his ruling, written down before the next begins.
Problem, Scope and Facts are talked through in the chat and written down, a decisions entry and the brief's section
per step; the Team is talked the same way; pages are made for Design and Plan only. Why: his ruling 2 of "Run 4 closed"
(13 Oct 2026): "lets not worry about html's for the brainstorm, we can just chat. the html's are more for direction once
you have enough". A talked step is still a step: the trial's first sheet skipped the problem for a parts list and a search
for existing tools, and the session folded six stages into "two sheets, then the brief"; nothing asked what hurt.

1. **The problem** (effort: medium; talked). Start from the problem he wants solved, not a solution:
   he will not always know what he wants; he will know what hurts.
2. **Scope** (medium; talked). What is in, what is out, what is for later, the out-of-scope lines written down too.
3. **Facts** (medium; talked). Read off the real machines and the tools' own documentation, never assumed or
   second-hand. Read-only commands on this machine are yours; another machine's console or a browser is a hands
   session (§ 5), never part of this walk.
4. **Design** (medium; a page). How it will work, in plain words and one picture. **The look first:** in any project
   with a screen the step ends with a clickable look on his phone, made-up information, two or three styles; the plan is
   built to the one he chooses. Why: his ruling 3 of "Run 4 closed": fifteen job scout pieces landed before he saw a look.
   The look is made by one helper, started by you when he says "make the look" in the chat; it builds only the look, in
   its own scratch copy, and nothing of it is kept in the project until the plan says so. Why: his ruling 5 of "Run 5
   closed": the master never builds, and no desk or worker exists before his signature.
5. **The team** (medium; talked). Which desks, and why each; one desk is a fine answer. Once he rules it, copy
   `desks/_desk/` to `desks/<name>/`, lowercase with hyphens, done inline (§ 4, do it or card it).
   Why: a desk keeps its own `CLAUDE.md` so it can specialise; spaces in a name break commands.
6. **The plan** (medium; a page) — § 3.

**What each step holds, and how it is asked,** is `pages.md`, each rule with its why, in the chat as on a page: § The
discovery page (no dates before the facts stage, only days of work; research before a signed plan with a real ceiling,
never in money), rule 23 (one stage at a time), rule 16 (a large thing in one word, asked about before it is scoped) and
rule 6 (an answer that grows the project much, with paths). A page's rule: it is published on his phone before its first
question, one question per item, under its evidence, one read-back pasted back. The lessons behind them are in `operator.md`,
§ Asking him to decide; § His time has you keep talking while research runs. Why: a rule kept in two places drifts.
In a talked step, put together in one message every question that does not depend on another's answer, each numbered
with its letters; one question at a time only where the next question depends on this answer. Why: his note of 15 Oct
2026 on foundry-north-website: about 20 single-question turns of discovery 'could have been grouped and reduced the
amount of back and forth'.
**Before any page is published,** run `python tools/page_check.py <page> --project .` and `python tools/people_check.py`.
A REFUSE from either is a stop: fix the page, never publish around it (`pages.md` rule 30, with its why).

**The rules of every stage**, each with its why:

- **Effort.** Medium for every stage, the design and the plan included; he raises it by hand at planning
  when a problem is hard. Why: his ruling 2 of "Run 3 closed" (8 Oct 2026): run 3's masters took 51% of
  its usage at the highest effort, and a master's work is now mostly running scripts; he "will increase the
  effort manually" when he thinks a problem is very hard.
- **Write `docs/brief.md` at the first ruling,** copied from `docs/blanks/brief.md` as you write the ruling, added to
  at each stage. By the plan it holds the era's task list, each task with a "done when" line; cards are cut from it
  alone. Why: until it exists the check reports a `fault:` and a reopened session cannot resume (the trial's came 25
  minutes late); finished work is measured by it.
- **The sharing question,** asked once, in the chat before the first page (will this project ever be shared, copied or
  made public?), and the brief's `Shared:` line written from his answer: `pages.md` rule 22, with its whys.
- **Nothing is ruled by silence, and nothing enters the scope by silence.** Your own calls are listed apart from
  his rulings, each with its undo, confirmed or undone at the plan sign-off; anything you would add is a question.
  Why: in the trial "no objection" was recorded as a ruling, and unasked work entered the scope.
- **One decisions entry per talked step or sheet.** When his words or letters come back, add one entry to
  `docs/decisions.md` from `docs/blanks/decisions-entry.md`: a table of his letters and his words,
  one undo line each, and your own calls in a table of their own. Never ask again for something he
  has ruled. Why: a ruling only in a chat is lost when the session ends; in the trial one sheet made
  six entries with the same boilerplate, a rate at which the log outgrows a cold reader in days.
- **Before any helper starts,** run `python tools/cap_check.py list`, and every order names the claim as the agent's first
  act; a reader is a helper inside the thread that ordered it and claims none (his ruling 4 of "Run 4 closed"). Why: the job
  scout's first research round ran five agents against a cap of four, and a later one skipped the claim its order did not name.
- **Helper or desk.** One question, under about an hour, the answer is one page, nobody will ask it a follow-up:
  a helper (the reader of § 5). It will be iterated, makes its own decisions, or outlives the day: a desk. Why: a desk
  for a one-hour question is overhead; a helper doing a desk's work takes its memory and its decisions with it when it ends.
- **Every helper writes its full findings to `docs/research/<date>-<topic>.md`,** with sources he can open and each
  claim tagged by the strength of its evidence (a study, the docs, practice, opinion), and returns only a short summary.
  The research moves into its desk's folder when the desk is born. Why: your context stays small, and the evidence
  survives for the desk that needs it.
- **Lessons as they happen.** Planning, explorations and research rounds write each lesson as it happens with `python tools/record.py --lesson ...`, and a helper's or reader's process lessons are copied in the same way: `tracks.md` rule 24, its sorting and its whys.
- **Open doors.** At any workflow step whose input can vary, a case that fits no known track takes the "brainstorm with him" path; what is worked out is written as a `track` lesson, a candidate track tagged `idea`, used and reviewed like anything else, and a new variant once it earns its tag (`docs/blanks/workflow.md`).
  Why: his ruling 8 of 12 Nov 2026, "the unknown that needs to be merged into a working system and then becomes a potential way of doing things".
- **The first time.** A kind of work with no workflow file yet is figured out with him while making its first version, under light rules; its plan carries `First time: <the kind of work>`, and the run closes only once that work's workflow file is written from what the job did, every step tagged `idea` or `on trial` (`upgrade.py --check` refuses the close until then). Why: his ruling 3 of 17 Nov 2026, "figure it out while i get to the 1st version of the end product", and call 3; engine-motion-graphics' Hero film took two runs and 123 unlanded lessons to be written down.

## 3 The plan — what he signs

**What a run is.** A run is either a process or a build, sized by what it is for: a whole era, or one feature.
But a small tweak is never a run (`tracks.md` rule 34). A foundation is not a run either: no time is spent updating it.
**The three words** tag every step of a workflow: `idea`, `on trial` with its measure, `foundation · <n> jobs`; his word in the review conversation makes a foundation, never changed quietly: a better way runs beside it as a trial, in the plan's `## Trials`, and every review's upgrade lists the foundations for him to reopen any as a trial (`tracks.md` rules 25 and 45).
Why: his words of 17 Oct 2026 (decisions "A run is any size", "A run is a process or a build", ruling 3 of "Run 6 asked for"): "a small tweak would never be a run. but ether a process or a build is a run"; a settled process becomes a run again "every once in a while to make sur we have the right way of doing things still". The words and the trials: his rulings 3 and 4 of 17 Nov 2026.

The plan is the last page of discovery. **What it offers is `pages.md` § The plan page, with the whys:** paths
priced in his hours; a mark on every item (✅ proven, 📄 documented, ❓ assumed, ⚠ a known risk); a lane for each piece;
the budget and the hard stop; every key point; how many agents; your own calls; the two starts; his acts. Yours to do:

- **Every ❓ spiked before he signs; the signed plan holds none** (an untried act is one). Before the plan page is published,
  every command in his acts is dry-run or its refusal looked for, and `python tools/plan_check.py <page>` must say ALLOW,
  beside the page and people checks (§ 2); a REFUSE is a stop, never published around. How, and why: `pages.md` § The plan page.
- **The week and the probe.** Read the five-hour window and the week together (`tracks.md` rule 11), and do the permission
  probe (`tracks.md` rule 19) before the page is published; its answers and the acts' dry runs go on the page (`pages.md`, the
  acts tried beforehand). Why: the job scout's master told him the week could not be read, and the page he signed held no probe answers.
- **Another project's run.** Before a run is started, read `python tools/cap_check.py list`; another project's run holding seats is named to him with what it means for the window, in these words, "two runs together fill a window in about an hour", and he chooses together or after. The why: `tracks.md` rule 43.

**The hand-over at signature.** Write the plan so a fresh execution master can run it from the written plan alone:
each piece with its mark, lane, Touches and done-when line, nothing left only in this talk. His signature is the
approval for the whole run. Write `docs/runs/<n>/plan-signed.md` from `docs/blanks/plan-signed.md` (run 1 first; a
new run, a new folder) with the path he chose, his start in the blank's words, his letter for each key point, the
agent count and his words; hold the sign-off sitting with him (the run skill's § 1.2 to 1.5); then hand over to a fresh
execution master (the run skill). The planning master goes idle; he may come back to it for design talk. No worker starts
before that file exists. Why: a conversation re-reads itself at every step, and run 2's planning session also ran the
build (his ruling 3 of 8 Oct); the check reads that file to say "signed"; the signature lets the run go on without him;
the signal box reads the start line (`tracks.md`); the job scout's sitting came four hours after his signature, unpointed at.

## 4 Cards — cutting the work

**Who cuts.** Full-lane cards are the desk conductor's: the master sends a desk its tasks and an aim, never
its cards. Light and standard cards the master cuts itself. Why: desks that planned their own builds ran
at well under budget; for a copy or a small fix, a desk's planning costs more than it saves (his ruling 3 of 8 Oct).

**Do it or card it.** Mechanical work under about ten minutes with no risk to anything that runs (a copy, a pointer, a record move, a new desk folder)
is not building: do it inline, commit by naming its paths, and write one line in `docs/decisions.md`. A card is for work that changes something that
runs, or that he would want to try. Why: eight steps of ritual for a one-step outcome was dead weight. A card that fixes a fault takes `tracks.md` rule 46's order: a tool that does the act, then a tool that refuses it, text last; where a tool holds it, the sheet's line shrinks.

**Every card is a copy of `docs/blanks/card.md`.** Fill every blank; invent no new shape. Its
**Kind** line (tool, document, research, screen, fix or hands) is always filled in.
Why: which checks the work climbs before merge depends on its kind, and a kind left implied was guessed wrong.

**The sizing rule.** Read the card back and ask; any "no" means it is two cards:

1. Could he try this in under five minutes, before reading any code?
2. Is the Gate shorter than the Goal?
3. Would you be surprised if it were more than about 150 lines of change?
4. Does the Gate ask for nothing the Forbidden line forbids, and have you looked inside the files it forbids?

Why: two cards contradicted themselves in one night; these questions catch the rest.

**Touches is the parallelism plan.** Two cards run at once only if their Touches do not overlap;
when they do, say which merges second. Why: one writer per file stops two workers overwriting each other.

**A card fired three times with only the project changed becomes a skill**, not a fourth card:
`.claude/skills/<verb>-<noun>/SKILL.md`, offered to him on the third firing and back to the template's
master copy so every new project gets it. Why: a repeated card is a procedure waiting to be written once.

## 5 The roles — each with its one forbidden verb

- **Master** — the planning master runs discovery and the plan and hands over at his signature (§ 3); fresh masters run
  the run and the review and merge checked work (the run skill); any may be opened at a sub-folder (§ 1). **Never
  builds.** Why: in the first run the master spent three quarters of its turns on hands work and conducted nothing.
- **Desk conductor** — a builder (the run skill § 3), plans its desk's build and writes its full-lane cards, and is archived once they are cut;
  like the master, it builds nothing. **Never passes its own work.** Why: the doer never certifies; a checker does.
- **Worker** — one card, its own worktree and branch, its receipt, then stops. It is told its desk
  folder in the first line of its orders. **Never merges.** Why: it shares his GitHub identity, so
  nothing but the rule stops it; merging is the master's alone.
- **Checker** — a fresh helper per result, inside the thread that ordered it (its own thread while settings force helpers
  to one model; the run skill § 3): runs the gate with `check.py` on a clean copy, compares the work against what was
  asked, writes its verdict, closes. **Never fixes what it checks.** Why: a checker that repairs the work has become a doer whose work nobody checked.
- **Reader** (a helper inside the thread that ordered it) — reads one thing and writes one page in `docs/research/`,
  with a time box and a token cap. **Never decides.** Why: readers once grew from four minutes to fifty and doubled what a run took of his allowance.
- **Hands session** — drives a browser or a machine's console in its own session, with him beside
  it. **Never builds.** Why: mixing setup and build in one sitting was the first run's failure.

Each job's model is the run skill's § 3 table (strongest, builder, checker, reader); nothing runs below the reader's. Why: four of five cheaper workers cut corners in testing.
The rules each role works under are in `worker-rules.md`; the master's powers in a run are the run skill's.

## 6 Wrap — the next session starts where this one stopped

1. **One `docs/decisions.md` entry** for whatever no sheet's entry holds, from `docs/blanks/decisions-entry.md`:
   each decision with its undo, and pointers to anything longer rather than a copy. Why: the undo lets him reverse
   a call at the review instead of waiting on each.
2. **Commit and push the record,** naming its paths in the commit. Why: an unpushed record is lost
   with the machine, and naming paths keeps anyone else's half-done files out of it.
3. **Ask him for his enjoyment score, from 1 to 5,** and write it into that entry, with his words.
   Why: enjoyment is one of his measures of the way of working; a score not asked is never kept.
4. **Anything left for him** goes in one list at the end, never as a stream of asks mid-session. Anything he must type
   goes in an act file from `docs/blanks/act-file.txt`, opened on the machine where he will type it. Why: a terminal
   paste loses characters, and every interruption costs him.

Suggest a wrap before any long gap. Why: so the next open starts exactly where this one stopped.
