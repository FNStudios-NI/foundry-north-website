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

3. Retired 2026-11-19: docs/retired.md.
4. **Overwritten, never appended.** Each new flag replaces the whole line.
   Why: the box reads only the newest state; a growing file would make it guess which line is now.
5. Retired 2026-11-21: docs/retired.md.
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

7. **The wrap message,** word for word: `Wrap line reached (95%): finish the merge in hand, commit everything, write your handover, stop your workers at a safe point, and raise the handed-over flag.`
   The window has three lines, read with `python tools/window.py`, whose last line's word is what the master acts on. Under 75%, `full pace`. From 75%, `slow down`: the run keeps working, one new agent only as one finishes, and the window read every 5 minutes (rule 40). At `wrap now` (95%, or the pace would pass 95% before the next tick and before the reset; a pace reaching 95% at the reset, or up to one tick after it, reads `slow down`): the master finishes any merge in hand (never stopping in the middle of one), commits everything, writes its handover, stops its workers, checkers and desk conductors at a safe point, raises `handed-over`, and stops.
   Why: at its limit the window stops every thread mid-turn, the master with them (run 1 stood still from 11:47 to 14:10, with no handover); a handover written before 95% is one the limit cannot cut off. A merge stopped halfway leaves the try-it build in a state no handover describes.
   Why 75% and 95%, in place of the old single wrap line: his ruling of 28 Oct 2026 (decisions 14:12, its lines of 14:39 and 15:42), "i would like it to start wrapping up at 95% but i think it should slow down after 75% to make it less likley to hit it by accident"; that day the old wrap line left about nine minutes at two runs' pace (about 1.7 points a minute), and needed a reading inside them. From 75% the run keeps working: his 15:42 correction.
8. **The handover** is one line in the run record, built by `record.py --handover` from its named fields (the run skill's § 8), rewritten at every worker start, every landing and every review round, never left for the wrap.
   Why: the fresh master confirms each field against the files before it acts, and the ids are how the old timers are found; it has no field for orders, since a handover that restated a rule once moved workers into the master's thread (the 0.9.0 design, Part 1). Never left for the wrap: engine-motion-graphics' handover stood at 10:17 when the limit hit at 11:01 (decisions 28 Oct 2026 14:12).
9. **`/run go`** starts a signed plan: the master opens the run (the run skill's § 1.6, Go) and raises `working`.
   A start with no one beside it (`/run go — started by the signal box, Start: tracks`) whose signed plan neither records the sign-off sitting nor waives it in his words raises `needs-you` ("the sign-off sitting is due") and stops.
   Why: the sitting is where each act the run needs is tried once with him watching (the run skill's § 1.3); a run started without it meets its first refusal with no one there to clear it.
10. **`/run carry on from the handover`** starts a fresh master. It reads the newest handover in the run record, confirms each running worker against it, writes `taken over at <time>`, raises `working`, and archives the old master's thread if no one else has.
    A master cut off before its handover is taken over the same way, from the run record and the last commits (as run 1's successor did at 14:28).
    A successor after a limit lists the run's threads (`t3_thread_list`) and sends each worker, checker or desk conductor that stopped mid-turn (not running, its end line of rule 28 not come) `The usage limit stopped you; carry on from where you stopped.` with `t3_thread_send`. Why: at the limit every thread stops mid-turn, and none sends its end line (rule 28).
    A fresh master after every reset, never a warmed old thread. Why: masters are built to restart from files, and a warmed thread carries a context nobody can see the size of; a successor not proven alive loses the run.
11. **With no signal box running** (no box line in `docs/register.md`, or the board it names not rewritten in the last 10 minutes), the master reads the window itself, whenever it is woken: `python tools/window.py`, one reading, the five-hour window and the week together (`unifiedWindows.five_hour` and `unifiedWindows.seven_day`, each's `.utilization` and `.resetsAt`), written to the machine's one reading file; its last line's word (`full pace`, `slow down` or `wrap now`) is what the master acts on, as rule 7 says.
    Both are read, and written down, before any build begins, a run or not (a port, or one small change of rule 34).
    Why: the decisions of 16 Oct 2026 18:05, call 5: the travel planner's port began with neither read, so its ceiling on his week could not be checked afterwards.
    Never on a timer of its own: the watch's tick (rule 40) is the one timer, bounded, one reading a tick, beside the one wake-up at the reset (rule 42); and never while nothing waits or runs: a read sends a message, and a message opens a new five-hour window.
    At `wrap now`, or unreadable, it wraps itself as in rule 7. Its wake-up for the reset is already set: the insurance wake-up of rule 42, scheduled at Go and at every take-over, never left for the wrap. Without T3: it raises `needs-you`, with the reset time in its line.
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
    A tailnet route's how it stops names the route without its slash: `tailscale serve --https=443 --set-path=<name without slash> off`.
    Why: the website's run 1 review note of 15 Oct 2026 10:14: named with its slash, `tailscale serve` said the handler did not exist, and removed nothing.
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

Detail of `.claude/skills/run/SKILL.md`, and how the rules themselves are kept (rules 45 to 48), here so the skill stays within its limit. The signal box reads none of it.

19. **The permission probe — before he sits down.** For each class of act the plan needs (start a worker, commit, push a branch, run a check tool, merge, undo, put the try-it build on the server, write to the build database), ask whether it would be allowed, without doing it. Put the answers on the plan page he signs.
    Why: a refused class found now costs a minute; found at 3am it costs a night.
20. **Register end dates against the run's end.** Read every "ends on" in `docs/register.md` against when the run should finish. A sign-in that ends before then is renewed first, by him.
    Why: a seven-day sign-in once expired in the middle of a run.
21. **His acts** (anything only his hands can do) go in one file from `docs/blanks/act-file.txt`, opened for him on the machine where he will type, as `operator.md` says. Anything he must approve is one numbered list with "approve all" first.
    Why: a terminal paste loses characters, and launches once sat for hours waiting on his hand.
22. **The cap.** At most four agents at a time, masters counted (workers, checkers, desk conductors and the master; a reader counts inside its parent's seat and claims none; his ruling, 6 Oct, and the 0.5.0 design's call 6), unless he has lifted the cap in words. A lift in his words (`docs/cap-lifted.md`) holds while the studio is idle and four holds on a take; `cap_check.py` holds that itself, so no claim past the fourth is marked `--heavy` by hand.
    Why: four beside a take is his ruling, on his caution and the ramp's memory readings until the road desk measures more; the work machine did not crash at fifteen agents (the 5 Oct stop was his own shutdown, his correction of 6 Oct). The tool counts a claim only while its process id lives (run 1).
    The plan's agent count is read against cap_check.py list at Go, since other projects' masters share the seats.
    Why: the Manager's run 1 review note of 16 Oct 2026 12:11: the website's master held a seat, so that run had two worker seats, not the three its plan counted on.
    **Heavy work waits until video generation is idle.** A card marked `Heavy: yes` is claimed with `tools/cap_check.py claim --heavy` before its worker, checker or reader starts; its REFUSE while a take is running is a stop. Never stop or restart video generation to make room.
    Why: slower takes are fine; a crash is not.
23. **Where you are.** Runs are numbered, each in its own folder `docs/runs/<n>/`: `signed` means the newest run has `plan-signed.md` and no `run.md`; `run` means it has `run.md` and no `review.html`; `review` means it has `review.html` and no `Run <n> closed` entry, or one that `upgrade.py --check` does not yet pass (rule 25); `ready` means it is closed and run <n+1> is next.
    Why: a status typed by hand was wrong for three weeks; the files cannot be. A project that could run only once read `review` for ever.
24. **Lessons, from any work.** Every lesson, from a run, planning, an exploration, a research round, a job or a session, is written as it happens with `python tools/record.py --lesson ...` into `docs/lessons.md`, in the form of `docs/blanks/review-note.md`: each ends in the exact line it should become, and its `file:` is one the next master is made to read (a skill, a desk's `CLAUDE.md`, a blank, `worker-rules.md`, `roles/`, `operator.md`, `tracks.md`, `pages.md`, `CLAUDE.md`, the brief, or `template`), never a findings file, a log or `docs/research/`.
    A worker writes its lessons in its receipt's `Lessons:` part, and the master copies each in with `record.py --lesson`. Helpers and readers end their returns with their process lessons, one line each in the lesson's form, and the master copies them in the same way. A `works` lesson (and a `misfire`) carries its `seen:`: his verdict quoted, a number or a pass line; `record.py` refuses one without.
    Each lesson is sorted on probation: `--sort routine` lands the same day, in the file it names, as a small checked piece with its undo, marked new; a later `works` lesson naming it (`--same L<nnn>`) keeps it, and one with nothing behind it is listed to retire. Never routine, and refused by the tool: a line that would change a step tagged `foundation`, or one that limits what may be made (`--limits made`: a look, a subject, a style). Unsorted reads `his`: it waits for his review, five at most shown; the template's (`--about template`) is carried to the template's house the day it is written. A lesson that repeats one names it with `--same L<nnn>`; at its third sighting the upgrade lists it to refuse, narrow or strike.
    Why: a rule that lives only in memory fails; the merge rule held only once it was an exact line. One file, from any work: a lesson in a file nobody is made to read is never read (the upgrade design of 12 Nov 2026, causes 3 and 4; his ruling 10 that day, "one place where everything leaves logs"). Through the master: one writer for the record. `seen:`: a `works` lesson is the evidence for a foundation. Probation: his ruling 5 of 17 Nov 2026 07:43; the "no person" rule nobody had ruled, copied forward in engine-motion-graphics, cost two rebuilds.
25. **The upgrade, at every review.** Every review ends with the upgrade: its list from `python tools/upgrade.py`, never from memory, put to him as the review page's upgrade section (`pages.md` § The review page), after the forks and before the two taps. The closing entry carries a `### The upgrade` block, one row per lesson with his answer and where the line now is, and `python tools/upgrade.py --check` passes before the run is closed; until it does, `where_am_i.py` reads `review`. A review he calls that is not a run's close (an era's end, a deep review) carries the same section and is closed by a decisions entry headed `Review closed`.
    The run skill's own review is this upgrade: its notes are lessons whose `file:` is the run skill, listed `for the template`; a change is made in the template's master copy, so every project gets it, never as a local edit in a project. The same upgrade lists every foundation (rule 45), and he ticks any to reopen as a trial.
    Why: the last review was left to good intentions and came five days and seven runs late. Why every review, with no count: the old count, a review at each third closed run, fell due three times and ran once, a memory test nothing checked, and no way of working was ever made a foundation in any house (the upgrade design of 12 Nov 2026, § 1 and § 2, cause 1, and § 7a answer 8). The foundations listed: his ruling 3 of "Run 6 asked for", 17 Oct 2026: a settled process is not a run, but every so often becomes one again, to make sure it is still the right way of doing things.
26. **When the project is finished, say so in its record:** a decisions entry headed `Project finished`, with the date.
    Why: the next queued project starts when the one before reports done, not at a guessed time.
27. Retired 2026-11-19: docs/retired.md.
28. **Each worker's orders end:** as your last act, send one line to the master's thread (`t3_thread_send`): '<card> ended: <DONE | NOT DONE | REFUSED | BLOCKED> at <commit>'.
    Why: run 3's review note of 07:14: a worker launched as its own T3 thread does not wake the master when its turn ends, so "wait to be told" had no teller.
29. **A light-lane document that restates his rulings** gets the master's read of at least ten lines against their sources before it lands; a source that exists is not a source that agrees.
    Why: run 3's review note of 08:00: a light-lane summary's gate checked that each line had a real source, not that it said what the source says; one of 54 rulings came out backwards, caught only by the master's read of eleven lines.
30. **An It works line's numbers** are counted from the record in the same step that writes it, never from memory.
    Why: run 3's review note of 08:23: the master typed counts into It works lines from memory, and two were wrong against the record.
31. **A planning master hands over by the same rule** as a run's master (the run skill's § 8): when its conversation passes 450,000 tokens, read from the `conversation:` line of `python tools/where_am_i.py`, or the usage window nears its limit, whichever comes first; with no fixed point in discovery.
    Why: his answer 2 of "The upgrade asked for", 13 Oct 2026: the job scout's planning thread passed 350 items, and a fixed hand-over at the design step would cost a re-read on short discoveries.
    Why 450,000 tokens: his words of 28 Oct 2026, "i always use the 1m context model so change this for good" and "like 450K is a good mark"; two planning masters of engine-motion-graphics handed over on reading alone, at about 70K and 110K, measured against 200,000.
32. **How a master starts a worker and a checker under T3.** A worker by `t3_thread_launch` with a worktree strategy, base `main`, `startFromOrigin` false, its model and effort named (its lane's, the run skill's § 3), and its desk folder the first line of its orders. Its orders name its card, tell it to claim its own seat as its first act (`python tools/cap_check.py claim --kind worker --card <card>`, with no `--pid`), and end with these five lines, in this order: "Never end your turn while a command you started is still running; run the gate in the foreground." · "Write multi-line text, cards and scripts with the Write and Edit tools, never a heredoc or an echo; use forward slashes in paths." · "The Python is `<the name on where_am_i.py's python: line>`." · "If your seat is refused, wait and retry; never end silently." · rule 28's last-act line, sent to the master's thread id. A checker is a `delegate_task` child of the master's thread, naming its model, with the run skill's § 3 orders, claiming its seat as `--kind checker`, its orders ending the same five lines. Each landing is followed by the window read (rule 11), `flag.py working`, the thread archived (rule 36) and its shutdown lines closed with `shutdown.py --closed <id>`.
    Why: on the job scout the handover of 10 Oct 07:44 had to carry this recipe, and the successor masters had to be told how to start an agent; no file of the template held it. The first three lines are `worker-rules.md` rules 15, 16 and 11, each with its why; the retry line, rule 1's. The meta-system's run 7 plan (28 Oct 2026) bound its master to exactly these five, in this order; the act checks only warn (`operator.md` § What only his hands do), so the five are kept.
33. **A page server for his review** runs with the longest limit and never as a background job of the thread he will answer in: a detached process, or the machine's lasting server. It goes on the shutdown list (rule 14), and at a mid-run stop it is kept with `python tools/shutdown.py --keep <id>`.
    Why: run 4's review notes of 8 Oct 13:24 and 13 Oct 08:55: a page server started as a background job stopped at the job's 30-minute default limit while the page waited for him; and one run as a background job of the thread he answers in made T3 refuse his pasted letters, so he had to ask again.
    A page server that will show video to his phone answers byte ranges (206); python -m http.server does not.
    Why: the website's run 1 review note of 15 Oct 2026 09:02: its film did not play on his phone, since iPhone Safari plays no video from a server that answers a range request with the whole file.
34. **One small change he asks for after a run has closed** runs on his words as the signature: one checked piece, a ceiling of 1% of his week, and a decisions entry; anything bigger is a plan.
    A run is a process or a build; a small tweak is never a run, and takes this path. A foundation is not a run either, until he reopens it as a trial (rules 25 and 45).
    Why: his answer 5 of "The upgrade asked for", 13 Oct 2026: on the job scout a plan and a sitting for one small card would have cost more than the card. What a run is: his ruling of 17 Oct 2026, "A run is a process or a build": "a small tweak would never be a run".
35. **When he says he is going to bed,** the master tells him how close the run is to its budget, so he can raise it first.
    Why: his words on the job scout, 10 Oct 03:23: "so it's not like a fear of hitting it when asleep".
36. **Masters archive finished worker and checker threads without asking him** (`t3_thread_organize`).
    Why: his answer 7 of "The upgrade asked for", 13 Oct 2026: archiving is what stops their processes (rule 15); on the job scout he declined the archive actions of 10 Oct, and finished threads were left unarchived through the whole run.
37. **A master never stops without its handover line,** a stop on a question included: the line is written in the run record (rule 8) before the question is put to him.
    Why: the job scout's third master wrote none (10 Oct 11:23): its last message asked him to choose, and the fourth master found the run "as left" and had to read it from the files.
38. **A master woken in its own thread claims its seat again as its first act, before any launch** (`python tools/cap_check.py claim --kind master --card docs/runs/<n>/run.md`).
    Why: the Manager's run 1 review note of 16 Oct 2026 16:16: the master's first `claude.exe` had ended, so after its wake-up its seat had vanished from `cap_check.py list`, and the run went uncounted for hours.
39. **Every pytest run on the work machine, a gate's included, passes `--basetemp <the agent's named scratch>/pt`;** the default temp folder is refused there.
    Why: three projects met it, the Manager (its run 1, 16 Oct 2026 12:17), the travel planner (its port's tests) and the ports playbook's step 9: pytest's default temp folder was access-denied, and gates passed only with `--basetemp`.
40. **The watch.** At Go the master schedules one check every 20 minutes into its own thread (every 5 minutes from 75%, as its prompt says): T3 `schedule_task`, schedule `{"type":"interval","everyMs":1200000}`, bound to its own thread, its prompt the one below, word for word. It goes on the shutdown list as it is scheduled (rule 14), kind `watch`, its id the scheduled task's, how it stops `delete_scheduled_task`, and it is deleted at the wrap.
    A master that hands over deletes its watch (`delete_scheduled_task`) and closes its line; its successor schedules its own at take-over (rule 10). Why: the watch is bound to the old master's thread, and would wake a thread no one runs.
    The prompt the master schedules, whole:
    `The watch: one short turn, and nothing else. Call t3_thread_list. For each worker, checker or desk conductor of this run whose line on the run record's shutdown list is open: a thread whose status is not running and whose end line (tracks.md rule 28) has not come, or one running whose updatedAt is more than 20 minutes old, is nudged with t3_thread_send ("Finish in the foreground and send your end line.") and written down with record.py as a key point nobody saw coming (the run skill's § 6). Then run python tools/window.py once and act on its last line's word. slow down: if this watch runs every 20 minutes (list_scheduled_tasks), schedule it again every 5 minutes, {"type":"interval","everyMs":300000}. full pace: if it runs every 5 minutes, schedule it again every 20 minutes, {"type":"interval","everyMs":1200000}. To schedule it again: schedule_task with this prompt, word for word, bound to this thread; delete the old watch with delete_scheduled_task; close its shutdown line with shutdown.py --closed <old id>, write the new watch's line (kind watch, its new id), and rewrite the handover line with the new id (tracks.md rule 8). wrap now: the wrap of tracks.md rule 7, in this turn. Otherwise, write one line with record.py under "The watch", the window's reading in it, and end the turn.`
    The watch's reading is the one timed read of rule 11: one call a tick, bounded, and only while the run has something waiting or running; a read sends a message, so no other clock reads the window, but the wake-up of rule 42.
    Why the watch reads the window: on 28 Oct 2026 engine-motion-graphics read the window only at landings, ran review rounds with none from 10:17 to 11:01, and never saw the climb (decisions 14:12). Why every 5 minutes from 75%: his 15:42 line, the window read more often, every 5 minutes; that day the window went from 71% to 90% in 11 minutes.
    Why: engine-motion-graphics' run 3 report of 28 Oct 2026, fault 1: a worker ran its gate as a background command and ended its turn to wait; nothing woke it, rule 28's end line never came, and 30 minutes were lost unseen, found only when he asked "why are you not running". It replaces the run skill's old "wait to be told" timer line and keeps that line's why (a polling clock once burned 13 points of his allowance in 23 minutes, doing nothing): the watch is bounded, one short turn in 20 minutes (in 5 from 75%), the list and the window read and nothing else.
41. **The signed number.** Before each worker start the master counts the run's workers running against the number of workers at once that `plan-signed.md` signs. A signed number is never the master's call, and the master never widens it; more workers is a change to the plan, which is his. The seats cap of rule 22 still holds beside it.
    `cap_check.py claim --kind worker` refuses a worker claim past a plan's `Workers at once: <n>` line (in its `## Agents`); a plan without that line binds by the master's count alone.
    Why: engine-motion-graphics' run 3 report of 28 Oct 2026, fault 3: its master started a fourth worker against the signed three and called it "the master's call"; it withdrew the line and interrupted the worker before its first act.
42. **The insurance wake-up.** At Go and at every take-over, before any agent starts, the master schedules one wake-up into its own thread for a few minutes after the five-hour window's reset, read from `python tools/window.py` (five hours from now when the window cannot be read, rule 11): T3 `schedule_task`, a fixed time (`{"type":"fixed_time","timeOfDay":"<hh:mm>"}`, the reset on this computer's clock plus a few minutes), bound to its own thread, its prompt the one below, word for word. It goes on the shutdown list as it is scheduled (rule 14), kind `wake-up`, its id the scheduled task's, how it stops `delete_scheduled_task`, and its id goes in the handover line (rule 8).
    At the wrap (rule 7) it is kept: it is what starts the successor after the reset. A master that hands over to a successor it starts itself deletes it with its watch (rule 40), and the successor schedules its own. With the review page published and nothing running, the master deletes it and its watch and releases its seat until he replies; a wake-up is re-armed only while an agent runs or a piece is in hand. Why: two wakes on 17 Nov 2026 cost about a point of his week each, with nothing to rescue (his ruling 6 of "Run 7 closed", L039).
    The prompt the master schedules, whole:
    `The wake-up: one short turn. Claim your seat again (tracks.md rule 38). Run python tools/window.py. If the run record's handover holds a "taken over at" line written after your own last line, a successor runs this run: delete this wake-up with delete_scheduled_task, close its shutdown line with shutdown.py --closed <its id>, release your seat, and end the turn. If the run's review page is published and no agent runs, the run waits only for him: delete this wake-up and your watch with delete_scheduled_task, close their shutdown lines with shutdown.py --closed <id>, release your seat, and end the turn. If your last turn ended on its own and your handover line in the run record is current (tracks.md rule 8), the run is healthy: re-arm only while an agent runs or a piece is in hand (with neither, do as for a published review page), and end the turn. To re-arm: schedule_task with this prompt, word for word, bound to this thread, at a fixed time a few minutes after the reset window.py names (five hours from now if it cannot read the window); delete this wake-up with delete_scheduled_task; close its shutdown line with shutdown.py --closed <its id>, write the new one's (kind wake-up, its new id), and rewrite the handover line with the new id. Otherwise (the usage limit stopped your last turn mid-turn, or you wrapped and raised handed-over): delete this wake-up and your watch with delete_scheduled_task, close their shutdown lines with shutdown.py --closed <id>, start one fresh master with t3_thread_launch, its first message /run carry on from the handover, release your seat, and end the turn. Start nothing else, and do no more of the run.`
    Why: nothing can be written once the limit hits, so the wake-up must already exist: on 28 Oct 2026 engine-motion-graphics' master had set none when the limit hit, and the wake-up rule set it only at the wrap line, a reading that had to fall inside about nine minutes (decisions 14:12). A fixed time repeats daily, hence the re-arm for each new reset. One master runs a run at a time: the woken master either keeps the run or starts one successor, deletes its own timers and ends, so there is never a second master, and the successor still comes from the files (rule 10).
43. **Another project's run.** Before a run is started, the master reads `python tools/cap_check.py list`; another project's run holding seats is named to him with what it means for the window, in these words, "two runs together fill a window in about an hour", and he chooses together or after.
    Why: the meta-system's run 7 was started beside engine-motion-graphics' run 3 and priced against the window as if alone; together they took about 1.7 points a minute (decisions 28 Oct 2026 14:12, call 1). One five-hour window serves every project on the machine.
44. **Reaching another project's master.** Through the machine's local sessions: `ListAgents`, then `SendMessage` to its name; when it has no live session, `t3_thread_send` to its thread, found with `t3_thread_list` across projects.
    Why: his correction of 28 Oct 2026 15:05: call 3 of the 14:12 entry said another project's master could not be reached from here; it is reached through the local sessions, as the Manager seat was on 17 Oct. With no live session: on 12 Nov 2026 engine-motion-graphics' reviewer had none for `ListAgents`, and a `t3_thread_send` to its thread, found by `t3_thread_list` across projects, was delivered (L037).
45. **The three words.** Every step of a workflow file, and every part of the template (its `STATUS.md`), carries one tag: `idea`, `on trial` with its measure, or `foundation · <n> jobs`, in the form of `docs/blanks/workflow.md`; `python tools/status.py` prints the board. A foundation is his word in the review conversation, from doing the work, testing it and talking it through; numbers inform it and never judge it. A way of working with no file cannot be a foundation: its first step writes it into one. A foundation is never changed quietly: a better way runs as a trial beside it, in the plan's `## Trials` (`plan_check.py` refuses a trial with no measure, two that read the same thing, or a sixth), and replaces it if it wins. A template part is a foundation only after it has worked in two kinds of project.
    Why: his ruling 9 of 12 Nov 2026, the reviews and the doing, testing and talking decide; the file: his ask for "foundations for future work to build apon or test against", so every use leaves evidence for or against it. The three words: the old word read as more than it was (his ruling of 17 Nov 2026 in engine-motion-graphics); trials that clash cannot say why quality moved, and a part proven in one kind of project may fail in the next (his rulings 3 and 4 of 17 Nov 2026 07:43).
46. **The order of fixes.** A fault is fixed first by a tool that does the act, so nothing is left to type; then, where the act is the agent's own, by a tool that refuses the wrong one and names the right one; text last, only for judgement no tool can hold, counted against its file's limit (rule 47). Where a tool does or refuses a thing, the sheet's line shrinks to a pointer to the tool, never grows.
    Why: every rule held by a tool held, and every rule left as text drifted: the no-heredoc rule broke in 25 of 35 of engine-motion-graphics' receipts, since the harness itself tells agents to use heredocs (the 0.9.0 design, § The cause).
47. **Size limits and retirement.** Each file an agent is made to read has a line limit in the template's `STATUS.md`; `land.py` refuses a landing that takes one over it (`python tools/size_check.py`), so a new line replaces or merges with an old one. A rule nobody named in five closed jobs is listed by `upgrade.py` to retire, moved with `--retire <file> <n>` to `docs/retired.md` with its undo (`--restore`), and listed at the review like a merged piece; nothing is deleted.
    Why: his ruling 2 of 17 Nov 2026 07:43: the record never forgets, and what agents read stays small; long rule files are what agents drift from.
48. **Jobs by role.** The sheets name four: strongest, builder, checker, reader; the models behind them are named once, in the run skill's § 3. The strongest works only at four judgement points, and only when the stakes ask for it: a design for the template or a workflow before he signs; sorting a review into one page when it holds more than a handful of open items; the creative design step of a workflow; a second opinion on anything headed for foundation. A small change (rule 34) never uses it.
    Why: his ruling 6 of 17 Nov 2026 07:43, "only when we need to bring out the big guns": the expensive model works only where a wrong call costs him weeks; and a new model is one edit (call 4).
