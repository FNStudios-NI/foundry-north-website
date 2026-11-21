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

**Read first, at Go and at every pick-up:** your role's sheet, `roles/master.md`, in place of every rulebook (the 0.5.0 design's call 3); the signed plan; and the rulings in `docs/decisions.md` since the signature (his rulings win over this file). **A fresh master picking up a run** reads the newest handover, the run record, those rulings and its sheet, not the whole log (the 0.5.0 design's call 5).
Why: a conversation re-reads itself at every step, so what a master reads first it pays for at every step after.
The sheet points at `operator.md` and `worker-rules.md` for a full rule; this skill points at them and never repeats them. Why: a rule kept in two places drifts in one of them.

**The cycle:** sign-off → the run, without him → checking → merging → the review session → promotion on his word.
**Where you are** is read from the files, never from memory: `python tools/where_am_i.py`; its four stages, and why, are `tracks.md` rule 23. It also prints `template: <version> · newest <x.y.z>`, with `update due` when the project is behind, so nobody has to remember to look.

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
   the try-it build put on the server, one write to the build database, each door in `docs/register.md` the plan uses.
   Write each result down. Why: trying real acts with him there cut surprises after he left from 41 to 3 and 6.
   The sitting tries the acts that need his hands; the first landing and its undo are tried at Go, on the first piece, with him reachable, since the landing tool writes into the run record that Go creates.
   A refusal is cleared by his hand in that session, now, or the work that needs it leaves the plan.
   Never ask another session to clear it. Why: carrying his yes into another session is permission laundering.
4. **Register end dates against the run's end,** as `tracks.md` rule 20 says.
5. **His acts** go in one file opened for him, approvals as one numbered list with "approve all" first, as `tracks.md` rule 21 says.
6. **Go — your first acts.** Copy the run record from its blank, claim your own seat (§ 2), then write the start time, the planned end, the cap (four, or "lifted" with his words) and the seat's claim in the run record. Commit the record. Read the window and write his week's reading (`python tools/window.py`, then `python tools/record.py --week go`; `tracks.md` rule 11) and, before any agent starts, schedule the insurance wake-up for a few minutes after its reset (`tracks.md` rule 42) and the watch (T3 `schedule_task`, one check every 20 minutes into your own thread, `tracks.md` rule 40); both go on the shutdown list, and their ids in the handover line.
   **A fast Go:** within 10 minutes of Go the desk conductor and the first workers on cards already cut are started; the remaining cards are cut while they build, the conductor committing each card to main as it is cut and sending you one line per card. Why: engine-motion-graphics' run 3 (fault 2): its master cut cards one by one in its own thread before starting anyone, about 15 minutes of serial work, and he had to ask why it was not working agentically.

## 2. The run — without him

- **You order desks; you never build.** Each order goes into the desk's `desks/<desk>/docs/asks.md`, from `docs/blanks/asks-entry.md`: the tasks, the aim, by when, heavy or not, and each task's lane.
  The desk conductor writes its own cards. Why: in the first run the master spent 75% of its turns doing hands work and conducted nothing; desks that planned their own builds ran well inside budget.
- **The order is written before any message says "look".** Why: messages vanish; the asks file is what survives.
- **Each worker gets one card, its own worktree, its own task branch, and its desk folder in the first line of its orders.**
  Why: one writer per working copy stops two sessions overwriting each other, and the first line is how a session started at the root knows which desk is its own. The main checkout is yours: the record and checked merges only.
- **A worker is a session he can see:** under T3, a thread you launch (how, and a checker too: `tracks.md` rule 32); on a machine without T3, a terminal tab. A headless process only on his word, for a named pass. Why: his ruling, 6 Oct: sessions he can see, as long as the solution is ready for the work machine and the T3 build.
- **Workers stay as their own threads; checkers and readers run as helpers inside the thread that ordered them** (§ 3). Archive a finished thread (`t3_thread_organize`)
  once its piece merges, without asking him (`tracks.md` rule 36), and a desk conductor's once its cards are cut. Why: his ruling, 7 Oct: run 1's twenty tabs cluttered his dashboard; workers stay where he can watch and steer them, and they outlive a parent that hits a limit.
- **Each agent claims its own seat** as its first act, from inside its own session, checkers too: `python tools/cap_check.py claim --kind <master|conductor|worker|checker> --card <card>`,
  with no `--pid`: the claim finds the agent's own `claude.exe` itself. Every order you send says so. Yours is `--kind master --card docs/runs/<n>/run.md`, claimed at Go and released at the wrap;
  a desk conductor's is `--kind conductor --card desks/<desk>/docs/asks.md`. Why: in run 2 the master looked each id up by hand, and checkers ran inside their parent's seat, uncounted (the 0.5.0 design's call 6).
  Its REFUSE is a stop, never something to route around: that agent goes no further. A reader counts inside its parent's seat and claims none.
  A thread's `claude.exe` stays alive while it sits idle, so its seat is released when its turn ends and claimed again before it takes more work. Each seat goes on the shutdown list.
- **At most four agents at a time, masters and checkers counted,** unless he has lifted the cap in words; **and never more workers at once than `plan-signed.md` signs:** before each worker start, count the run's workers running against it. A signed number is never the master's call, and you never widen it (`tracks.md` rule 41). **Heavy work waits until video generation is idle**
  (`claim --heavy`), and video generation is never stopped or restarted to make room. The lift, the take, the heavy claim and their whys are `tracks.md` rule 22.
- **Models follow the lane and the role** (§ 3's two tables); **nothing runs below the reader's model**, and every launch names its model and effort. Why: his ruling, 6 Oct: not everything should run on the cheapest model; four of five cheaper workers cut corners and faked their rounds; T3 does not hold the floor, and a worker launched with no model named inherits yours, at medium effort.
- **Wait to be told.** A worker's end line (`tracks.md` rule 28) is your signal; its receipt on its branch is the proof. Never poll on a clock: the one timer is the watch (rule 40), with the wake-up of rule 42 for the reset. Why: a polling clock once burned 13 points of his allowance in 23 minutes, doing nothing; the watch is bounded, one short turn in 20 minutes (in 5 from 75%), the list and the window read and nothing else, and a worker that stops mid-card never sends its end line (engine-motion-graphics' run 3, fault 1: 30 minutes lost unseen, found only when he asked "why are you not running").
- **Start, stop and restart workers inside the signed plan** as the work needs (§ 5, P4). A worker's question that the record answers,
  you answer, and write down with its undo (P5). Why: he trusts the master to decide what the record lets it decide.
- **Raise the flag** with `python tools/flag.py <flag> "<why>"`, as `tracks.md` § The four flags says: `working` at Go, at each worker start and at each merge;
  `needs-you` at an **a** or at `run paused: needs him`; `handed-over` at your handover; `done` when the review page is published.
- **Key points he marked**, each written down as it is reached. At an **a**: stop that line of work there and tell him; other lines carry on. At a **b**: tell him, show him on his phone, carry on. At a **c**: carry on, and lay it out at the review. Why: he chose his stops in advance instead of watching every step.
- **The window's word** (the last line of `python tools/window.py`, read at Go, at each landing, at each wake and on each watch tick): `full pace` under 75%; `slow down` from 75%: keep working, one new agent only as one finishes, the window read every 5 minutes (the watch, rule 40); `wrap now` at 95%, or when the pace would pass it before the next tick and before the reset (a pace reaching 95% at the reset, or up to one tick after it, reads `slow down`): the wrap of `tracks.md` rule 7. Why: his ruling of 28 Oct 2026 (decisions 14:12, its lines of 14:39 and 15:42); that day the old wrap line left about nine minutes at two runs' pace.
- **The handover line is rewritten at every worker start, every landing and every review round,** never left for the wrap; it carries the window lines (75% slow down, 95% wrap) and the wake-up's and the watch's ids (`tracks.md` rule 8). Why: engine-motion-graphics' handover stood at 10:17 when the limit hit at 11:01.
- **Another project's master is reached through the machine's local sessions:** `ListAgents`, then `SendMessage` to its name; when it has no live session, `t3_thread_send` to its thread, found with `t3_thread_list` across projects (`tracks.md` rule 44).
- **The shutdown list.** Everything the run starts goes on the run record's `## Shutdown list` as it starts: sessions, seats, background scripts, watches, scheduled wake-ups
  and page servers (`tracks.md` rule 14; a page server for his review, rule 33). At any stop, run `python tools/shutdown.py` and close by hand what it lists (`--closed <id>`) until it says NOTHING LEFT (rule 15).
- **The cut-offs.** The run stops at the first of `tracks.md` rule 12's five: done, blocked, budget, stuck, hard stop. New ideas go on `## Next run's list`, unless a blocker (rule 13). When he says he is going to bed, tell him how close the run is to its budget (rule 35).

## 3. Lanes and checking — a fresh checker per result

**Each piece has a lane**, proposed on the plan page and signed by him, written on its card; the checks it climbs follow it (the 0.5.0 design's § 6):

| Lane | For | Built by | Checked by |
|---|---|---|---|
| **Light** | copies, documents, record moves, small act files | one helper on the reader's model | scripts only: the master runs `check.py` (below) with `--who "the master (light lane)"` and writes the checker's lines, before land.py; the fence check prints INSIDE |
| **Standard** | small code, small fixes | a worker on the builder's or the reader's model | a fresh checker on the reader's model, then the scripts |
| **Full** | tools, skills, rules, `template/` | a builder, on its desk's card | a fresh checker, then the scripts |

Why: each piece sits on the lowest rung that does it properly; `plan_check` refuses a light lane on a tool, a skill or `template/`; and `merge_check.py` demands a Checker run block on every lane, so on the website's run 1 (15 Oct 2026) the master wrote one into a light helper's receipt with no rule to say how.

**Jobs by role, and the models behind them** — the one place a model is named, and the place `project.yaml`'s model lines will hold (`tracks.md` rule 48):

| Role | Model | Who |
|---|---|---|
| strongest | Fable 5.2 | only at `tracks.md` rule 48's four judgement points, when the stakes ask; never a small change (rule 34) |
| builder | Opus 5.5 at high effort | workers (a standard lane's may run on the reader's model), desk conductors; masters at medium effort, raised by him at planning when a problem is hard (his ruling 2 of "Run 3 closed") |
| checker | Opus 5.5 at high effort | every checker but a standard lane's, which runs on the reader's model |
| reader | Sonnet 5.5 | readers and light helpers; the lowest anything runs on |

When a worker's receipt lands, start a **checker** (standard and full): a fresh helper inside your own thread, one per result, naming its model. It claims its own seat (§ 2).
While `.claude/settings.json` forces every helper to one model (a `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` line), a checker on another model runs as its own thread. Why: a forced helper cannot be the checker's model.
Why: the doer never certifies its own work; on 20 Sept five results passed on a number copied from the worker.

The checker's orders, whole:
1. Read only the card and the result (the receipt and the branch). Nothing else, so it judges what was asked, not what was meant.
2. In the branch's worktree run `python tools/check.py <receipt> --card <card> --who "<model>, own session" --scratch <its scratch>`: it runs the card's gate on a clean copy of the committed branch and writes the block's heading, `Commit:`, `Exit code:` and `From a clean copy:` lines. Why: checkers typed those lines by hand, and a gate run beside uncommitted files could pass on them.
3. Show the proof can fail (red without the change, or the card's ablation), written as `Shown failing:`. Why: a blank result is not a pass.
4. Answer in writing, as `Scope:`: *is anything in this diff not asked for by the card?* Why: four of five cheaper workers passed their gate and still cut corners; scope drift is easiest to see from outside.
5. Write `Verdict: PASS` or `Verdict: FAIL` once, any summary under `Why:`, commit only the receipt on the worker's branch, and close. Why: `tools/merge_check.py` reads the block, and refuses one with no clean-copy or shown-failing line.

**The same-worker fix.** A FAIL on something removable goes back to the same worker thread, as a message with the checker's finding; it claims its seat again and fixes, and a fresh checker checks the fix.
Why: in run 2, 5 of 17 pieces failed their first check on trivia, and each one-line fix cost three more sessions as a new card. A piece that fails its check twice is parked for his review (cut-off 4, stuck); other work carries on.
**A card changes only when the card itself is wrong:** that FAIL goes back to the desk's asks file as one line, and the desk cuts the fix. You fix neither. Why: you never build.

## 4. Landing — checked work only, each with its undo

Merging checked work into the try-it build (the project's main branch) is yours alone (P1), and so is undoing a merge there (P2). One command, in the main checkout, from its top folder:
`python tools/land.py --card <the card> --branch <the task branch>`. It prints `LANDED:` when all is done. Its steps, in order, each with its why, are its own top comment: the two fences, the size check, the receipt's `Run:` lines, the merge check, one squash per card, the landing line with its undo (`git revert <the squash commit>`), the push.
Why the tool: in run 2 most of the master's actions were clerk work, and the same input always gives the same right answer, so it belongs on a script, which cannot forget a step. The undo is what replaces his wait; he reviews afterwards instead of watching every merge.
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
before it is published. Once it is published and nothing runs, delete your wake-up and watch and release your seat until he replies (`tracks.md` rule 42). Why: his ruling, 6 Oct: you make the decisions during the build, and he makes one pass over the forks.

1. **It works, first.** Try each done-when line of the signed plan, and write each with `python tools/record.py --section "It works" "<card> · pass | fail · <who looked> · <how>"`; for anything made to be watched, the how is his watch or "frames only". `record.py` refuses a line without the who.
   It heads the page. Why: his ruling 8 of 8 Oct; a run can land every piece while the thing itself does not work; a pass nobody watched read as one somebody had (the 0.9.0 design, Part 7).
2. **The numbers:** `python tools/measures.py docs/runs/<n>`: it works, usage per finished piece, share finished and surprises, from the run record and the session logs,
   never estimated. Why: one stretch scored eight merges while nothing worked; these measure what he actually wants, and run 2's measures never happened.
3. **One pass over the forks** you took that could affect him later in the design. Each fork is an item block (`pages.md` rule 31) with the options
   you turned down, what each would set in motion later, and his letters. Every unforeseen key point (§ 6) is a fork. Why: he cannot judge technical
   pieces, but he can judge forks that shape his later work; and each choice laid out against the options turned down is his condition for letting you decide.
4. **The merged pieces are your decisions:** listed one line each with its undo, no question asked. You run any undo he names (P2).
   Why: the undo is what replaces the wait he no longer spends before each merge; "you have ran it already … can you just give me the results."
5. **The two taps, last:** the thing made, 1 to 5, then the run's enjoyment, 1 to 5; at the close, `python tools/window.py`, then `python tools/record.py --week close`, then `python tools/scoreboard.py --run <n> --made <1-5> --enjoyment <1-5>` writes them in the scoreboard's row and counts the rest. Why: his ruling 1 of 17 Nov 2026: quality first, then his time; his ruling 8 of 8 Oct: enjoyment is his, never measured by a tool.
6. **Promotion to the people who use it is his word** (P7). You prepare it; he says it. Why: what users see cannot be taken back quietly.

Close the review with one decisions entry from `docs/blanks/decisions-entry.md`, headed `Run <n> closed`, with his keeps, undos and taps,
then release your seat. Why: the where-am-I check reads that heading to say `ready` for run <n+1>.
**The review ends with the upgrade,** after the forks and before the taps: its list from `python tools/upgrade.py`, its section `pages.md` § The review page; the closing entry carries `### The upgrade`, and `python tools/upgrade.py --check` passes before the run is closed; in the template's home it also refuses a close while lessons waited uncarried before its Go, and the harvest is what carries them. It shows his lessons (five at most), the routine ones on probation (landed in the run that learnt them, marked new) and those to retire. A step becomes `idea`, `on trial` or `foundation · <n> jobs` there, in the review conversation, from doing the work and testing it; numbers inform it and never judge it; a foundation is never changed quietly, and a better way runs beside it as a trial (`tracks.md` rules 24, 25, 45 and 47). Why: the counted review fell due three times and ran once; his ruling 9 of 12 Nov 2026, and his rulings 3 to 5 of 17 Nov 2026.

## 8. Keeping itself honest

- **The hand-over rule:** a run's master hands over when its conversation passes 450,000 tokens (his mark, 28 Oct 2026), read from the `conversation:` line of `python tools/where_am_i.py`, or the usage window nears its limit, whichever comes first; never by count alone, never judged by eye. The usage window's half of the rule is the wrap at `wrap now`, 95% (`tracks.md` rule 7); from 75% (`slow down`) the run keeps working, one new agent only as one finishes. Hand over at a quiet moment, never in the middle of a merge.
  Why: his ruling 4 of "Run 4 closed", 13 Oct 2026: the job scout's first master handed over by count at 288 thousand of a million, its successor read every rule file and the record again before its first act, and he read it as wasted tokens. Why 450,000 tokens: his words of 28 Oct 2026, "i always use the 1m context model so change this for good" and "like 450K is a good mark"; two planning masters of engine-motion-graphics handed over on reading alone, at about 70K and 110K, measured against 200,000.
- **Handover by file.** At 450,000 tokens (as the tool reads them, never as the context looks in T3), write the handover and start the successor master; only once it has written `taken over at <time>` do you stop, deleting your watch and wake-up. At the 95% wrap, write the handover and stop: your wake-up starts the successor after the reset (`tracks.md` rule 42).
  The handover line is written by `python tools/record.py --handover --running "<agents running>" --merges "<merges and their undos>" --next "<the next step, open key points>" --window "<75% slow down, 95% wrap>" --ids "<wake-up and watch ids>"`, never typed; it has no field for orders. The wrap message and the resume after his usage window resets are in `tracks.md` § Wrap and resume; at every take-over the successor schedules its own wake-up and watch before any agent starts, and after a limit nudges each thread that stopped mid-turn (rules 42, 40 and 10). Why: eight handovers done this way were all clean; a successor not proven alive loses the run.
  You never stop without your handover line, a stop on a question included (`tracks.md` rule 37).
- **Lessons as they happen, from any work, with `record.py --lesson`, and the upgrade at every review** (this skill's own notes among its lessons, for the template), and a project finished: `tracks.md` rules 24 to 26. A planning master's hand-over, and one small change he asks for after a run has closed: rules 31 and 34.
