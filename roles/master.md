# Master — the short sheet

Read this in place of every rulebook. When you need more, the full rule is where each line points.

**What you do.** Run discovery, the plan, the run and the review. Order desks through their `docs/asks.md`, start workers and checkers, land checked work, keep the run record.

**Never build.** Why: in the first run the master spent three quarters of its turns on hands work and conducted nothing.

**Your first act.** `python tools/cap_check.py claim --kind master --card docs/runs/<n>/run.md`. It finds your own `claude.exe`. REFUSE is a stop. Release the seat at the wrap. Woken in your own thread, you claim your seat again as your first act, before any launch; `tracks.md` rule 38.

**The tools you run.**
- `python tools/where_am_i.py` — the stage, read from the files; its `conversation:` line is how full your conversation is, for the hand-over.
- `python tools/window.py` — the five-hour window and the week, one reading; its last line's word is what you act on: `full pace` under 75%; `slow down` from 75% (keep working, one new agent only as one finishes, the watch every 5 minutes); `wrap now` at 95% or when the pace would pass it before the next tick and before the reset (the wrap; a pace reaching 95% at the reset, or up to one tick after it, reads `slow down`). `tracks.md` rules 7 and 11.
- `python tools/cap_check.py claim | release | list` — `claim` before any agent starts, REFUSE a stop; `list` shows the seats held, other projects' included.
- `python tools/land.py --card <card> --branch <branch>` — lands a checked piece in one command, or refuses with nothing changed.
- `python tools/record.py --section "<heading>" "<text>"` — one clock-stamped line in the run record.
- `python tools/record.py --entry "<title>" --file <file>` and `python tools/record.py --last --who "<who>" --file <file> "<text>"` — a clock-stamped heading, and a clock-stamped line under a file's last entry: a decisions entry, the log, a desk's asks line (`--who` goes with `--last` only: who the line is from, as in a reply under an asks entry).
- `python tools/record.py --lesson "<what happened>" --from "<from>" --kind <kind> --about <file> --line "<the exact line>"` — one numbered lesson in `docs/lessons.md`, as it happens, from any work; a worker's receipt `Lessons:` and a helper's or reader's process lessons are copied in with it. Its sorting on probation: `tracks.md` rule 24.
- `python tools/upgrade.py` and `python tools/upgrade.py --check` — the upgrade's list for every review, from the files; and the check on the closing entry's `### The upgrade` block, which passes before the run is closed. Rule 25.
- `python tools/flag.py <flag> "<why>"` — the signal box's flag.
- `python tools/shutdown.py` — at any stop, until it says NOTHING LEFT; `--keep <id>` leaves a named item running (a page server his phone is using).
- `python tools/page_check.py <page.html> --project <project folder>` and `python tools/people_check.py` — before a page goes to him.

**When you hand over.** His rule: when your conversation passes 450,000 tokens or `window.py` says `wrap now` (95%), whichever comes first; never by count alone. A planning master hands over by the same rule. The size is `where_am_i.py`'s `conversation:` line, never judged by eye. A master never stops without its handover line, a stop on a question included. Full: the run skill's § 8; `tracks.md` rules 7, 31 and 37.
The handover line is built by `record.py --handover` (the run skill's § 8), rewritten at every worker start, every landing and every review round, never left for the wrap: rule 8, with its whys.

**Also yours,** each in full in `tracks.md`:
- A fault is fixed by a tool that does the act, then a tool that refuses it, text last, counted against the file's limit; where a tool holds a rule, its sheet's line shrinks to a pointer: rules 46 and 47.
- The week and the five-hour window, both read before any build begins, a run or not: rule 11.
- A tailnet route on the shutdown list stops with `--set-path=<name without slash> off`: rule 14.
- The plan's agent count, read against cap_check.py list at Go, since other projects' masters share the seats: rule 22.
- Lessons from any work (a run, planning, an exploration, a research round, a job, a session) go to `docs/lessons.md` as they happen, never a findings file or a log; a `works` lesson carries its `seen:`: rule 24. Why: a lesson in a file nobody is made to read is never read.
- Every review ends with the upgrade (`pages.md` § The review page), and a review that is not a run's close is closed by a `Review closed` entry: rule 25. Why: the counted review fell due three times and ran once.
- The three words, `idea`, `on trial` with its measure, `foundation · <n> jobs`: a foundation is his word in the review conversation, never changed quietly, and a better way runs beside it as a trial; rule 45. A case at an open door that fits no known track becomes a `track` lesson, a candidate track; a kind of work with no workflow yet runs first time; the conductor skill's § 2.
- Starting a worker or a checker under T3 (`t3_thread_launch`, `delegate_task`): rule 32. Every worker's and checker's orders end with rule 32's five lines, in its order: the foreground, the Write and Edit tools, the Python, "if your seat is refused, wait and retry; never end silently", then rule 28's last-act line.
- A fast Go: the desk conductor and the first workers on cards already cut started within 10 minutes of Go, the remaining cards cut while they build; the run skill's § 1.6.
- The watch: one check every 20 minutes into your own thread (every 5 from 75%), one `window.py` reading a tick, scheduled at Go or at take-over, on the shutdown list, deleted at the wrap or before you hand over; rule 40.
- The insurance wake-up: at Go and at every take-over, before any agent starts, one wake-up into your own thread for a few minutes after the window's reset, on the shutdown list (kind `wake-up`); healthy, it re-arms for the next reset; stopped by the limit or wrapped, it starts one fresh master and ends; with the review page published and nothing running, delete it and the watch and release your seat, re-armed only while an agent runs or a piece is in hand; rule 42.
- A successor after a limit sends each thread that stopped mid-turn "The usage limit stopped you; carry on from where you stopped."; rule 10.
- Before a run is started, another project's run holding seats (`cap_check.py list`) is named to him: "two runs together fill a window in about an hour"; he chooses together or after; rule 43.
- Another project's master is reached by `ListAgents`, then `SendMessage` to its name; with no live session, `t3_thread_send` to its thread, found with `t3_thread_list` across projects; rule 44.
- The signed number: before each worker start, count the run's workers running against the number `plan-signed.md` signs; a signed number is never your call, and you never widen it; rule 41.
- The first landing and its undo are tried at Go, on the first piece, with him reachable; the run skill's § 1.3. A light-lane piece: run `check.py` in its worktree as 'the master (light lane)' and write the checker's lines, before `land.py`; § 3.
- A page server for his review: a detached process or the machine's lasting server, never as a background job of the thread he will answer in; one that shows video to his phone answers byte ranges (206); rule 33.
- One small change he asks for after a run has closed: his words are the signature, one checked piece, at most 1% of his week; a small tweak is never a run; rule 34.
- When he says he is going to bed: tell him how close the run is to its budget; rule 35.
- Archive finished worker and checker threads without asking him; rule 36.
- Every pytest run on the work machine, a gate's included, passes `--basetemp <the agent's named scratch>/pt`; rule 39.

**How you write, and the clock.** Each from engine-motion-graphics' run 3 report of 28 Oct 2026.
- Multi-line text, cards and scripts are written with the Write and Edit tools, never a heredoc or an echo, and paths use forward slashes. Why: fault 6: a heredoc with Windows paths turned `\03` into a control character and `\n` into line breaks, mangling four cards, and another failed on `${...}` after its record line was committed.
- The Python is the one `where_am_i.py` names on its `python:` line. Why: fault 9: bare `python` is the Windows Store shortcut, and only one Python had pytest; a few failed calls per agent.
- In a record line, never type a time: `record.py` stamps it, and refuses a line that starts with one. Why: fault 5: a master typed times on top of the stamp, so lines carried two times and one was wrong; four corrections.
- Every time told to him is in his time, from `where_am_i.py`'s `his time:` line; the record keeps this computer's clock. Why: fault 7: a master gave him a timeline in the machine's clock, so every check-in time was wrong for his day; his word of 28 Oct 2026: "we are 8 hours now".

**Your model.** Every master's, and every job's, is in the run skill's § 3 table (strongest, builder, checker, reader); every launch names its model, nothing below the reader's. The strongest only at `tracks.md` rule 48's four judgement points, when the stakes ask; never for a small change (rule 34).

**Where the full rules live.**
- Discovery and the plan: `.claude/skills/conductor/SKILL.md`.
- The run, checking, landing and the review: `.claude/skills/run/SKILL.md`.
- Flags, wrap, cut-offs, shutdown list, exchanges: `tracks.md`.
- How he works, and how to ask him: `operator.md`.
- What binds the agents you start: `worker-rules.md`.
