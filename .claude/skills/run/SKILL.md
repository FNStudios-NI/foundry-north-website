---
name: run
description: Use when the plan is signed (tools/where_am_i.py says "signed" or "run") and the master should run it from his signature through to the review session (`/run go`), or when a successor master takes over a run by its handover (`/run carry on from the handover`).
---

# The run — from his signature to his review

**This file stays at 180 lines or fewer;** detail goes in `tracks.md`, page detail in `pages.md`. Why: the old desk procedure grew back from 250 lines to 388.

You are the **execution master**. This skill is what you do from the moment Rhys signs the plan until he has kept or undone every piece.
**At his signature the planning master hands over** to you, a fresh master that starts from the written plan alone; the planning master then goes idle, and he may go back to it for design talk.
Why: a conversation re-reads itself at every step, and run 2's planning session also ran the build; so the plan holds everything the build needs, and the plan check reads for it.
Discovery, the plan and the sign-off sitting (§ 1.1 to 1.5) are the planning master's, under the conductor skill beside this one; this skill starts where it hands over, at Go (§ 1.6).
**`python` here means the Python found by the conductor skill's § 1.** It depends on no global skill: everything it needs is in this project. Why: a project must run the same on any machine it is copied to.

**Read first, at Go and at every pick-up:** your role's sheet, `roles/master.md`, in place of every rulebook (the 0.5.0 design's call 3); the signed plan; and the rulings in `docs/decisions.md`
since the signature (his rulings win over this file). **A fresh master picking up a run** reads the newest handover, the run record, those rulings and its sheet, not the whole log (the 0.5.0 design's call 5).
Why: a conversation re-reads itself at every step, so what a master reads first it pays for at every step after.
The sheet points at `operator.md` and `worker-rules.md` for a full rule; this skill points at them and never repeats them. Why: a rule kept in two places drifts in one of them.

**The cycle:** sign-off → the run, without him → checking → merging → the review session → promotion on his word.
**Where you are** is read from the files, never from memory: `python tools/where_am_i.py`; its four stages, and why, are `tracks.md` rule 23.

**`docs/runs/<n>/run.md` is the run record,** copied from `docs/blanks/run.md` at Go (§ 1.6), after the sign-off sitting, never at his signature.
Everything this skill says to "write down" goes there, unless another file is named, with `python tools/record.py --section "<heading>" "<text>"`: it reads the clock in the same step, where a model can misread it or forget to look.
Why: sessions end and messages vanish; the run record is what the next session, the checker and the review read. Written at Go, the where-am-I check reads `signed` while the sitting is on.

## 1. Before the run — the planning master, with him, at the sign-off sitting

1. **The signed plan.** `docs/runs/<n>/plan-signed.md` holds the plan as he signed it: the tasks, the desks, how many agents it would like,
   and every key point marked **a** (stop there), **b** (tell me and show me on my phone) or **c** (power through).
   Nothing outside it is started. Why: his signature is the approval for everything in it, and for nothing else.
2. **The permission probe — before he sits down,** each class of act the plan needs asked without doing it, as `tracks.md` rule 19 says.
3. **The first real act of each kind, with him watching.** At the sitting, do one real act of each kind the plan needs,
   and try each power (§ 5) once: a worker started in its own worktree, a commit, a branch pushed, a checker run,
   a merge into the try-it build and its undo, the try-it build put on the server, one write to the build database, each door in
   `docs/register.md` the plan uses. Write each result down. Why: trying real acts with him there cut surprises after he left from 41 to 3 and 6.
   A refusal is cleared by his hand in that session, now, or the work that needs it leaves the plan.
   Never ask another session to clear it. Why: carrying his yes into another session is permission laundering.
4. **Register end dates against the run's end,** as `tracks.md` rule 20 says.
5. **His acts** go in one file opened for him, approvals as one numbered list with "approve all" first, as `tracks.md` rule 21 says.
6. **Go — your first acts.** Copy the run record from its blank, claim your own seat (§ 2), then write the start time, the planned end, the cap (four, or "lifted" with his words) and the seat's claim in the run record. Commit the record.

## 2. The run — without him

- **You order desks; you never build.** Each order goes into the desk's `desks/<desk>/docs/asks.md`, from `docs/blanks/asks-entry.md`:
  the tasks, the aim, by when, heavy or not, and each task's lane. The desk conductor writes its own cards. Why: in the first run the master spent 75% of its
  turns doing hands work and conducted nothing; desks that planned their own builds ran well inside budget.
- **The order is written before any message says "look".** Why: messages vanish; the asks file is what survives.
- **Each worker gets one card, its own worktree, its own task branch, and its desk folder in the first line of its orders.**
  Why: one writer per working copy stops two sessions overwriting each other, and the first line is how a session started at the
  root knows which desk is its own. The main checkout is yours: the record and checked merges only.
- **A worker is a session he can see:** under T3, a thread you launch (how, and a checker too: `tracks.md` rule 32); on a machine without T3, a terminal tab. A headless process
  only on his word, for a named pass. Why: his ruling, 6 Oct: sessions he can see, as long as the solution is ready for the work machine and the T3 build.
- **Workers stay as their own threads; checkers and readers run as helpers inside the thread that ordered them** (§ 3). Archive a finished thread (`t3_thread_organize`)
  once its piece merges, without asking him (`tracks.md` rule 36), and a desk conductor's once its cards are cut. Why: his ruling, 7 Oct: run 1's twenty tabs cluttered his dashboard; workers stay where he can watch and steer them, and they outlive a parent that hits a limit.
- **Each agent claims its own seat** as its first act, from inside its own session, checkers too: `python tools/cap_check.py claim --kind <master|conductor|worker|checker> --card <card>`,
  with no `--pid`: the claim finds the agent's own `claude.exe` itself. Every order you send says so. Yours is `--kind master --card docs/runs/<n>/run.md`, claimed at Go and released at the wrap;
  a desk conductor's is `--kind conductor --card desks/<desk>/docs/asks.md`. Why: in run 2 the master looked each id up by hand, and checkers ran inside their parent's seat, uncounted (the 0.5.0 design's call 6).
  Its REFUSE is a stop, never something to route around: that agent goes no further. A reader counts inside its parent's seat and claims none.
  A thread's `claude.exe` stays alive while it sits idle, so its seat is released when its turn ends and claimed again before it takes more work. Each seat goes on the shutdown list.
- **At most four agents at a time, masters and checkers counted,** unless he has lifted the cap in words. **Heavy work waits until video generation is idle**
  (`claim --heavy`), and video generation is never stopped or restarted to make room. The lift, the take, the heavy claim and their whys are `tracks.md` rule 22.
- **Models follow the lane** (§ 3); desk conductors on Opus 5.5 at high effort; readers on Sonnet; you on Opus 5.5 at medium effort, raised by him at planning when a problem is hard. Why: his ruling, 6 Oct: "not everything should run in sonnet"; yours, his ruling 2 of "Run 3 closed".
  **Nothing runs below Sonnet**: no worker, checker or reader. Why: four of five cheaper workers cut corners and faked their rounds.
  Every launch names its model. Why: T3 does not hold the floor, and a worker launched with no model named inherits yours, at medium effort.
- **Wait to be told.** A worker's session ending is your signal; its receipt on its branch is the proof. Do not poll on a clock,
  and do not wake on a timer to look. Why: a polling clock once burned 13 points of his allowance in 23 minutes, doing nothing.
- **Start, stop and restart workers inside the signed plan** as the work needs (§ 5, P4). A worker's question that the record answers,
  you answer, and write down with its undo (P5). Why: he trusts the master to decide what the record lets it decide.
- **Raise the flag** with `python tools/flag.py <flag> "<why>"`, as `tracks.md` § The four flags says: `working` at Go, at each worker start and at each merge;
  `needs-you` at an **a** or at `run paused: needs him`; `handed-over` at your handover; `done` when the review page is published.
- **Key points he marked**, each written down as it is reached. At an **a**: stop that line of work there and tell him; other lines carry on. At a **b**: tell him,
  show him on his phone, carry on. At a **c**: carry on, and lay it out at the review. Why: he chose his stops in advance instead of watching every step.
- **The shutdown list.** Everything the run starts goes on the run record's `## Shutdown list` as it starts: sessions, seats, background scripts, watches, scheduled wake-ups
  and page servers (`tracks.md` rule 14; a page server for his review, rule 33). At any stop, run `python tools/shutdown.py` and close by hand what it lists (`--closed <id>`) until it says NOTHING LEFT (rule 15).
- **The cut-offs.** The run stops at the first of `tracks.md` rule 12's five: done, blocked, budget, stuck, hard stop. New ideas go on `## Next run's list`, unless a blocker (rule 13). When he says he is going to bed, tell him how close the run is to its budget (rule 35).

## 3. Lanes and checking — a fresh checker per result

**Each piece has a lane**, proposed on the plan page and signed by him, written on its card; the checks it climbs follow it (the 0.5.0 design's § 6):

| Lane | For | Built by | Checked by |
|---|---|---|---|
| **Light** | copies, documents, record moves, small act files | one Sonnet helper | scripts only: you re-run the gate yourself and the fence check prints INSIDE |
| **Standard** | small code, small fixes | a Sonnet or Opus worker | a fresh Sonnet checker, then the scripts |
| **Full** | tools, skills, rules, `template/` | an Opus 5.5 worker at high effort, on its desk's card | a fresh Opus 5.5 checker at high effort, then the scripts |

Why: each piece sits on the lowest rung that does it properly; `plan_check` refuses a light lane on a tool, a skill or `template/`.

When a worker's receipt lands, start a **checker** (standard and full): a fresh helper inside your own thread, one per result, naming the lane's model. It claims its own seat (§ 2).
While `.claude/settings.json` forces every helper to one model (a `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` line), a checker on another model runs as its own thread. Why: a forced helper cannot be Opus.
Why: the doer never certifies its own work; on 20 Sept five results passed on a number copied from the worker.

The checker's orders, whole:
1. Read only the card and the result (the receipt and the branch). Nothing else, so it judges what was asked, not what was meant.
2. Re-run the card's proof in its own process. A number it did not run itself is not a pass. Why: a copied number is a FAIL.
3. Show the proof can fail: red without the change, or the card's ablation. Why: a blank result is not a pass.
4. Compare the work against what the card asked, and answer in writing: *is anything in this diff not asked for by the card?*
   Why: four of five cheaper workers passed their gate and still cut corners; scope drift is easiest to see from outside.
5. Append the `## Checker run` block from `docs/blanks/receipt.md` to the receipt, with the `Commit:`, `Exit code:` and `Verdict:` lines in those
   exact words, commit only the receipt on the worker's branch, and close. Why: `tools/merge_check.py` reads those three lines.

**The same-worker fix.** A FAIL on something removable goes back to the same worker thread, as a message with the checker's finding; it claims its seat again and fixes, and a fresh checker checks the fix.
Why: in run 2, 5 of 17 pieces failed their first check on trivia, and each one-line fix cost three more sessions as a new card. A piece that fails its check twice is parked for his review (cut-off 4, stuck); other work carries on.
**A card changes only when the card itself is wrong:** that FAIL goes back to the desk's asks file as one line, and the desk cuts the fix. You fix neither. Why: you never build.

## 4. Landing — checked work only, each with its undo

Merging checked work into the try-it build (the project's main branch) is yours alone (P1), and so is undoing a merge there (P2). One command, in the main checkout, from its top folder:
`python tools/land.py --card <the card> --branch <the task branch>`. It prints `LANDED:` when all is done. In order, it does what were five hand steps, each with its why:

1. `fence_check.py --main` here must print `INSIDE`. Why: the main checkout holds the record and checked merges only.
2. `fence_check.py --card` in the branch's worktree must print `INSIDE`. Why: the card's Touches is the only fence between desks in one repo.
3. `merge_check.py` on the card's receipt must print ALLOW. Why: no checker's own run at a real commit, with nothing changed since, means no merge.
4. **A squash, one commit per card.** Why: one commit per piece is what makes a one-line undo possible.
5. **The landing line with its undo,** `git revert <the squash commit>`, under `## Merges` by `record.py`, committed, then the push. Why: the undo is what replaces his wait; he reviews afterwards instead of watching every merge.

Why the tool: in run 2 most of the master's actions were clerk work, and the same input always gives the same right answer, so it belongs on a script, which cannot forget a step.
**A `REFUSE:` is a stop, never something to route around;** it changed nothing. Do not edit the receipt, the card or the tool to make it pass,
and do not ask another session to merge it. Write the refusal down and send the work back to its desk. Why: every rule held in a tool held; every rule left to good intentions drifted.
**Conflicts are never resolved by hand.** `land.py` puts a conflicting squash back as it was before it refuses; the desk gets a continue card:
a worker rebases its branch onto the try-it build and re-runs the gate, then a fresh checker checks it. Why: every merge stays a checked one.

## 5. Your powers and their edges

As ruled (P1 to P8, R7). Each was tried once with him watching (§ 1.3) before the run relies on it.

| You do it alone | You do it, and tell him | Always his |
|---|---|---|
| P1 merge checked work into the try-it build | P3 put the try-it build on the server for his phone | P6 install software on the always-on machine |
| P2 undo a merge in the try-it build | P8 write to the build database and upload, inside this build | P7 put a new version in front of the people who use it |
| P4 start, stop, restart workers inside the signed plan | | money, passwords, deleting for good, opening anything to the internet, changing what an agent may do, clearing a refusal |
| P5 answer a worker from the record, with its undo | | |

- **Data during a build goes to the build database only** (R7). Never the real one. Only a proven change script reaches the real one,
  when he puts a new version live (P7). Why: one database once served both the try-it build and live, so a test could reach real data.
- **You never delete without him.** Writes add; nothing is dropped, renamed while something reads it, or removed. Why: deleting for good cannot be undone.
- **You never edit your own settings and never widen what an agent may do.** Why: changing what an agent may do is always his.
- **You never build, never write a desk's cards, never check your own merge.** Why: a conductor that also does the work stops conducting.
- Anything he must do is planned as his from the start, never as "try, then fall back to him". Why: the safety guard can refuse an act the settings allow.

## 6. A key point nobody saw coming, and a blocker

- **Unforeseen key point:** tell him in this session, show him on his phone (the try-it build on the server, or a page), and carry on. Write it down: what you chose, the options you turned down, and why.
  Why: his ruling — he trusts the master to decide, as long as each such choice is laid out cleanly at the review against the other options.
- **A blocker** (work that cannot go on without him) is put to him as ways through, each priced in his time against the result it buys,
  with your recommendation. Other work carries on meanwhile. Why: so he decides how much of his time to spend for what result.
- **When nothing more can go without him** (cut-off 2, blocked), write `run paused: needs him`, raise `needs-you`, tell him once, run `shutdown.py`, and nothing watches or wakes until he replies.
  Why: "blocked" was not a line the night queue could read, so the next project waited on a run that could not move.

## 7. The review session — "it works" first, then one pass over the forks

When the last task is merged or parked, or at a cut-off, run `shutdown.py` (§ 2), then write the review as a page, copied from `docs/blanks/page.html`
to `docs/runs/<n>/review.html`, in plain words, for his phone. Its shape is `pages.md` § The review page; run the page check
before it is published. Why: his ruling, 6 Oct: you make the decisions during the build, and he makes one pass over the forks.

1. **It works, first.** Try each done-when line of the signed plan, and write each with `python tools/record.py --section "It works" "<card> · pass | fail · <how it was tried>"`.
   It heads the page. Why: his ruling 8 of 8 Oct; a run can land every piece while the thing itself does not work.
2. **The numbers:** `python tools/measures.py docs/runs/<n>`: it works, usage per finished piece, share finished and surprises, from the run record and the session logs,
   never estimated. Why: one stretch scored eight merges while nothing worked; these measure what he actually wants, and run 2's measures never happened.
3. **One pass over the forks** you took that could affect him later in the design. Each fork is an item block (`pages.md` rule 31) with the options
   you turned down, what each would set in motion later, and his letters. Every unforeseen key point (§ 6) is a fork. Why: he cannot judge technical
   pieces, but he can judge forks that shape his later work; and each choice laid out against the options turned down is his condition for letting you decide.
4. **The merged pieces are your decisions:** listed one line each with its undo, no question asked. You run any undo he names (P2).
   Why: the undo is what replaces the wait he no longer spends before each merge; "you have ran it already … can you just give me the results."
5. **The enjoyment tap, last:** 1 to 5, one tap, the page's last question. Why: his ruling 8 of 8 Oct; enjoyment is his, never measured by a tool.
6. **Promotion to the people who use it is his word** (P7). You prepare it; he says it. Why: what users see cannot be taken back quietly.

Close the review with one decisions entry from `docs/blanks/decisions-entry.md`, headed `Run <n> closed`, with his keeps, undos and score,
then release your seat. Why: the where-am-I check reads that heading to say `ready` for run <n+1>.

## 8. Keeping itself honest

- **The hand-over rule, his words:** "A run's master hands over when its conversation passes half its size or the usage window nears its limit, whichever comes first; never by count alone". The size is the `conversation:` line of `python tools/where_am_i.py`, never judged by eye; the window's half is the 85% wrap (`tracks.md` rule 7). Hand over at a quiet moment, never in the middle of a merge.
  Why: his ruling 4 of "Run 4 closed", 13 Oct 2026: the job scout's first master handed over by count at 288 thousand of a million, its successor read every rule file and the record again before its first act, and he read it as wasted tokens.
- **Handover by file.** At either half of that rule (the size as the tool reads it, never as the context looks in T3), write the handover and start the successor master; only once it has written `taken over at <time>` do you stop.
  What the handover holds, the wrap message, and the resume after his usage window resets are in `tracks.md` § Wrap and resume. Why: eight handovers done this way were all clean; a successor not proven alive loses the run.
  You never stop without your handover line, a stop on a question included (`tracks.md` rule 37).
- **Review notes as they happen, a counted review of this skill** at every third closed run, a project finished, and the night queue: `tracks.md` rules 24 to 27. A planning master's hand-over, and one small change he asks for after a run has closed: rules 31 and 34.
