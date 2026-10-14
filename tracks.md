# Tracks — the project's side of the signal box

The signal box is a small program, always on, that decides who has the work machine: his AI projects or the video work.
It starts a project's master when there is room, and stops and restarts masters around his usage window.
It reads every project's plan and flag, and nothing else; this file is what a project keeps so the box can read it.
Why: when his usage window ran out, every thread stopped, and nothing started them again when it reset (a run once stood still for over two hours).

These rules are a contract: the box is built against them, word for word. Change one only as an ask to the master, never as an edit here alone.
Why: a rule changed on one side of a contract breaks the other side without a sound.

The box, its board and its folder belong to the box's own desk, outside the template. Where they live is a line in `docs/register.md`, never a path here.
Why: a path written here would be wrong on every machine but one, and the box could not move without changing every project.

## On the tracks

1. **A project is on the tracks** when its newest run's `docs/runs/<n>/plan-signed.md` holds a line beginning `Start: tracks` or `Start: now`, and that run's folder has no `review.html` yet.
   Why: the box starts only work he has signed, and a published review page means the run is over.
2. **The two starts.** He picks one on the plan page; the master writes it into `plan-signed.md` in these words.
   - `Start: tracks` — the plan goes on the tracks, and the signal box starts its master when there is room.
   - `Start: now` — a master is started by hand at once; the box still counts its track and wakes it after a limit.

   Why: his ruling, two starts, "add to tracks" or "go for it". A plan can wait for room, or run tonight; either way, once running, it is woken after a limit like the rest.

## The flag

3. **A running master keeps one flag,** in `docs/runs/<n>/flag.txt`: one line, `<flag> <UTC time> <one plain line why>`.
   For example: `working 2026-10-07T05:10Z started the merge-check worker`.
   Why: one line is all the box needs to know how the run stands, and the time tells it how long it has stood so.
4. **Overwritten, never appended.** Each new flag replaces the whole line.
   Why: the box reads only the newest state; a growing file would make it guess which line is now.
5. **Never committed.** The template's `.gitignore` lists `docs/runs/*/flag.txt`, and adopt adds that line to a project that lacks it.
   Why: the flag is a live signal, not the record. Committed, it would add a commit at every change and leave an old flag in every copy of the project.
6. **No flag file reads as `working`.**
   Why: a master that has not yet raised a flag is still running; read as idle, its track would be given away.

## The four flags

Only these four words, as written, raised with `python tools/flag.py <flag> "<why>"`, which refuses any other. Why: the box reads the first word and knows no others, and in run 2 the masters raised their flags by hand.

### working

Raised at Go, and written again with a fresh time whenever the master starts a worker or records a merge.
Why: an unchanged `working` flag of 6 hours reads to the box as a fault, and a long run is not a stuck one.

### needs-you

Raised when the master stops at an **a** key point, or writes `run paused: needs him`.
Why: a run waiting on him needs no machine, so the box can give its turn back to the video work.

### handed-over

Raised when the master's handover is written.

### done

Raised when the run's review page is published.
Why: the run is over; its track is free for the next signed plan.

## Wrap and resume

7. **The wrap message,** word for word: `Wrap line reached (85%): write your handover now, start no new workers, and raise the handed-over flag.`
   On it the master finishes any merge in hand (never stopping in the middle of one), writes its handover, starts no new workers, raises `handed-over`, and stops.
   Why: at its limit the window stops every thread mid-turn, the master with them (run 1 stood still from 11:47 to 14:10, with no handover); a handover written at 85% is one the limit cannot cut off. A merge stopped halfway leaves the try-it build in a state no handover describes.
8. **The handover** is written in the run record and holds: the workers and checkers running, the merges done and their undos, the open key points, the next step; and the id of any wake-up the master set (rule 11).
   Why: the fresh master confirms each of these against the files before it acts; eight handovers done this way were all clean. The wake-up's id is how the fresh master deletes it.
9. **`/run go`** starts a signed plan: the master opens the run (the run skill's § 1.6, Go) and raises `working`.
   A start with no one beside it (`/run go — started by the signal box, Start: tracks`) whose signed plan neither records the sign-off sitting nor waives it in his words raises `needs-you` ("the sign-off sitting is due") and stops.
   Why: the sitting is where each act the run needs is tried once with him watching (the run skill's § 1.3); a run started without it meets its first refusal with no one there to clear it.
10. **`/run carry on from the handover`** starts a fresh master. It reads the newest handover in the run record, confirms each running worker against it, writes `taken over at <time>`, raises `working`, and archives the old master's thread if no one else has.
    A master cut off before its handover is taken over the same way, from the run record and the last commits (as run 1's successor did at 14:28).
    A fresh master after every reset, never a warmed old thread. Why: masters are built to restart from files, and a warmed thread carries a context nobody can see the size of; a successor not proven alive loses the run.
11. **With no signal box running** (no box line in `docs/register.md`, or the board it names not rewritten in the last 10 minutes), the master reads the window itself, whenever it is woken: `claude -p "ok" --model sonnet --output-format stream-json --verbose`, and from its `rate_limit_event` the five-hour window's `unifiedWindows.five_hour.utilization` and `.resetsAt`.
    Never on a timer of its own, and never while nothing waits or runs: a read sends a message, and a message opens a new five-hour window.
    At 85% or more, or unreadable, it wraps itself as in rule 7, and before stopping sets its wake-up with T3's `schedule_task`: a fixed time a few minutes after the reset, or, when the window cannot be read, five hours from now; a fresh thread, first message `/run carry on from the handover`.
    The fresh master deletes that schedule once it has fired, since a fixed time repeats daily. Without T3: it raises `needs-you`, with the reset time in its line.
    Why: with no box, nothing else wakes a stopped run; run 1 waited from 11:47 until he opened a successor at 14:28. One wake-up at the reset is not a poll; a polling clock once burned 13 points of his allowance in 23 minutes, doing nothing.
    An unreadable window gives no reset time, so its wake-up is set five hours from now, the latest a reset can be: a wake-up that fires into a spent window fails, and schedules nothing after it.

## Cut-offs

12. **A run stops at the first of these:**
    1. **Done:** every signed piece is landed or parked.
    2. **Blocked:** nothing can move without him. Everything stops, he gets one message, and nothing watches or wakes until he replies.
    3. **Budget:** the share of his week he signed for is spent.
    4. **Stuck:** the same piece fails its check twice, and is parked for his review. Other work carries on.
    5. **Hard stop:** the planned end plus 50%, unless he extends it.

    Why: run 2 was planned at 6½ hours and ran 13, and its measures and review never happened.
13. **New ideas mid-run go on the next run's list,** unless they are a blocker.
    Why: in run 2 new work joined mid-run, and the run never reached its own finish line.

## The shutdown list

14. **Everything a run starts is written on its shutdown list as it starts:** sessions, seats, background scripts, watches, scheduled wake-ups and page servers.
    The list is the `## Shutdown list` of the run record, `docs/runs/<n>/run.md`, one line per item, in this form:
    `- <hh:mm> · <kind> · <what> · <id> · <how it stops> · open | closed <hh:mm>`
    Why: run 2 left the signal box running, and two daily wake-ups that only a deletion stops.
15. **At any stop, `tools/shutdown.py` closes it:** it stops each item it can, marks it closed, and lists what is left for the master to close by hand, with `--closed <id>`, until it confirms nothing is left.
    Why: a script stops each item and names what it could not, so nothing is left running unseen, as the signal box and two wake-ups were after run 2.
    Close a shutdown item only with `shutdown.py --closed <id>`, which stamps the clock; never type a time.
    Why: run 3's review note of 07:43: the master typed close times by estimate, and ten were 2 to 6 minutes off the tools' own stamps.
    A child task's shutdown line closes by archiving its thread (`t3_thread_organize`), not by its turn's end: that is what stops its process.
    Why: run 3's review note of 08:18: a finished checker's claude.exe, a T3 child task, stayed alive and idle after its task completed, until its thread was archived.

## Exchanges

Between this project and another, the template holds the rule, never a mailbox: a project's own mailbox stays in that project.

16. **The side that asks owns the exchange:** it opens it, waits for the answer, and closes it with a "closed" letter.
    Why: an exchange nobody closes leaves its watch running, and the other side never knows the question is answered.
17. **A watch lives only while an exchange is open,** and waits up to 2 hours per wake.
    Why: a watch with no open exchange waits for nothing, and every wake is a message from his window (rule 11).
18. **A listener that must answer from the project's knowledge wakes a fresh small master** to read the files and answer.
    Why: the answer lives in the files, and a warmed old thread carries a context nobody can see the size of (rule 10).

## Moved from the run skill

Detail of `.claude/skills/run/SKILL.md`, kept here so the skill stays at 180 lines or fewer. The signal box reads none of it.

19. **The permission probe — before he sits down.** For each class of act the plan needs (start a worker, commit, push a branch, run a check tool, merge, undo, put the try-it build on the server, write to the build database), ask whether it would be allowed, without doing it. Put the answers on the plan page he signs.
    Why: a refused class found now costs a minute; found at 3am it costs a night.
20. **Register end dates against the run's end.** Read every "ends on" in `docs/register.md` against when the run should finish. A sign-in that ends before then is renewed first, by him.
    Why: a seven-day sign-in once expired in the middle of a run.
21. **His acts** (anything only his hands can do) go in one file from `docs/blanks/act-file.txt`, opened for him on the machine where he will type, as `operator.md` says. Anything he must approve is one numbered list with "approve all" first.
    Why: a terminal paste loses characters, and launches once sat for hours waiting on his hand.
22. **The cap.** At most four agents at a time, masters counted (workers, checkers, desk conductors and the master; a reader counts inside its parent's seat and claims none; his ruling, 6 Oct, and the 0.5.0 design's call 6), unless he has lifted the cap in words. A lift in his words (`docs/cap-lifted.md`) holds while the studio is idle and four holds on a take; `cap_check.py` holds that itself, so no claim past the fourth is marked `--heavy` by hand.
    Why: four beside a take is his ruling, on his caution and the ramp's memory readings until the road desk measures more; the work machine did not crash at fifteen agents (the 5 Oct stop was his own shutdown, his correction of 6 Oct). The tool counts a claim only while its process id lives (run 1).
    **Heavy work waits until video generation is idle.** A card marked `Heavy: yes` is claimed with `tools/cap_check.py claim --heavy` before its worker, checker or reader starts; its REFUSE while a take is running is a stop. Never stop or restart video generation to make room.
    Why: slower takes are fine; a crash is not.
23. **Where you are.** Runs are numbered, each in its own folder `docs/runs/<n>/`: `signed` means the newest run has `plan-signed.md` and no `run.md`; `run` means it has `run.md` and no `review.html`; `review` means it has `review.html` and no `Run <n> closed` entry; `ready` means it is closed and run <n+1> is next.
    Why: a status typed by hand was wrong for three weeks; the files cannot be. A project that could run only once read `review` for ever.
24. **Review notes.** One line per lesson, as it happens, in the run record's review notes, from `docs/blanks/review-note.md`: each ends in the exact line it should become.
    Why: a rule that lives only in memory fails; the merge rule held only once it was an exact line.
25. **A counted review of the run skill.** Count the `Run <n> closed` entries in `docs/decisions.md`; never keep the count by hand. At every third closed run, the review session ends with the run skill's own review: each review note since the last one, put to him as keep · change · drop with the line it would become. A change is made in the template's master copy, so every project gets it, never as a local edit in a project.
    Why: the last review was left to good intentions and came five days and seven runs late.
26. **When the project is finished, say so in its record:** a decisions entry headed `Project finished`, with the date.
    Why: the next queued project starts when the one before reports done, not at a guessed time.
27. **The night queue reads `run paused: needs him` as done:** the next project starts, and this run's blocker waits for the morning.
    Why: one stuck project must not hold a night's work for the others.
28. **Each worker's orders end:** as your last act, send one line to the master's thread (`t3_thread_send`): '<card> ended: <DONE | NOT DONE | REFUSED | BLOCKED> at <commit>'.
    Why: run 3's review note of 07:14: a worker launched as its own T3 thread does not wake the master when its turn ends, so "wait to be told" had no teller.
29. **A light-lane document that restates his rulings** gets the master's read of at least ten lines against their sources before it lands; a source that exists is not a source that agrees.
    Why: run 3's review note of 08:00: a light-lane summary's gate checked that each line had a real source, not that it said what the source says; one of 54 rulings came out backwards, caught only by the master's read of eleven lines.
30. **An It works line's numbers** are counted from the record in the same step that writes it, never from memory.
    Why: run 3's review note of 08:23: the master typed counts into It works lines from memory, and two were wrong against the record.
31. **A planning master hands over by the same rule** as a run's master (the run skill's § 8): when its conversation passes half its size, read from the `conversation:` line of `python tools/where_am_i.py`, or the usage window nears its limit, whichever comes first; with no fixed point in discovery.
    Why: his answer 2 of "The upgrade asked for", 13 Oct 2026: the job scout's planning thread passed 350 items, and a fixed hand-over at the design step would cost a re-read on short discoveries.
32. **How a master starts a worker and a checker under T3.** A worker by `t3_thread_launch` with a worktree strategy, base `main`, `startFromOrigin` false, its model and effort named (its lane's, the run skill's § 3), and its desk folder the first line of its orders. Its orders name its card, tell it to claim its own seat as its first act (`python tools/cap_check.py claim --kind worker --card <card>`, with no `--pid`), and end with rule 28's last-act line, sent to the master's thread id. A checker is a `delegate_task` child of the master's thread, naming its model, with the run skill's § 3 orders, claiming its seat as `--kind checker`. Each landing is followed by the window read (rule 11), `flag.py working`, the thread archived (rule 36) and its shutdown lines closed with `shutdown.py --closed <id>`.
    Why: on the job scout the handover of 10 Oct 07:44 had to carry this recipe, and the successor masters had to be told how to start an agent; no file of the template held it.
33. **A page server for his review** runs with the longest limit and never as a background job of the thread he will answer in: a detached process, or the machine's lasting server. It goes on the shutdown list (rule 14), and at a mid-run stop it is kept with `python tools/shutdown.py --keep <id>`.
    Why: run 4's review notes of 8 Oct 13:24 and 13 Oct 08:55: a page server started as a background job stopped at the job's 30-minute default limit while the page waited for him; and one run as a background job of the thread he answers in made T3 refuse his pasted letters, so he had to ask again.
34. **One small change he asks for after a run has closed** runs on his words as the signature: one checked piece, a ceiling of 1% of his week, and a decisions entry; anything bigger is a plan.
    Why: his answer 5 of "The upgrade asked for", 13 Oct 2026: on the job scout a plan and a sitting for one small card would have cost more than the card.
35. **When he says he is going to bed,** the master tells him how close the run is to its budget, so he can raise it first.
    Why: his words on the job scout, 10 Oct 03:23: "so it's not like a fear of hitting it when asleep".
36. **Masters archive finished worker and checker threads without asking him** (`t3_thread_organize`).
    Why: his answer 7 of "The upgrade asked for", 13 Oct 2026: archiving is what stops their processes (rule 15); on the job scout he declined the archive actions of 10 Oct, and finished threads were left unarchived through the whole run.
37. **A master never stops without its handover line,** a stop on a question included: the line is written in the run record (rule 8) before the question is put to him.
    Why: the job scout's third master wrote none (10 Oct 11:23): its last message asked him to choose, and the fourth master found the run "as left" and had to read it from the files.
