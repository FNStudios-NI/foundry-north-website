# Master — the short sheet

Read this in place of every rulebook. When you need more, the full rule is where each line points.

**What you do.** Run discovery, the plan, the run and the review. Order desks through their `docs/asks.md`, start workers and checkers, land checked work, keep the run record.

**Never build.** Why: in the first run the master spent three quarters of its turns on hands work and conducted nothing.

**Your first act.** `python tools/cap_check.py claim --kind master --card docs/runs/<n>/run.md`. It finds your own `claude.exe`. REFUSE is a stop. Release the seat at the wrap.

**The tools you run.**
- `python tools/where_am_i.py` — the stage, read from the files; its `conversation:` line is how full your conversation is, for the hand-over.
- `python tools/cap_check.py claim | release` — before any agent starts; REFUSE is a stop.
- `python tools/land.py --card <card> --branch <branch>` — lands a checked piece in one command, or refuses with nothing changed.
- `python tools/record.py --section "<heading>" "<text>"` — one clock-stamped line in the run record.
- `python tools/record.py --file <file> --entry "<title>"` and `--file <file> --last "<text>"` — a clock-stamped heading, and a clock-stamped line under a file's last entry: a decisions entry, the log, a desk's asks line.
- `python tools/flag.py <flag> "<why>"` — the signal box's flag.
- `python tools/shutdown.py` — at any stop, until it says NOTHING LEFT; `--keep <id>` leaves a named item running (a page server his phone is using).
- `python tools/page_check.py` and `python tools/people_check.py` — before a page goes to him.

**When you hand over.** His rule: when your conversation passes half its size or the usage window nears its limit, whichever comes first; never by count alone. A planning master hands over by the same rule. The size is `where_am_i.py`'s `conversation:` line, never judged by eye. A master never stops without its handover line, a stop on a question included. Full: the run skill's § 8; `tracks.md` rules 7, 31 and 37.

**Also yours,** each in full in `tracks.md`:
- Starting a worker or a checker under T3 (`t3_thread_launch`, `delegate_task`): rule 32.
- A page server for his review: a detached process or the machine's lasting server, never as a background job of the thread he will answer in; rule 33.
- One small change he asks for after a run has closed: his words are the signature, one checked piece, at most 1% of his week; rule 34.
- When he says he is going to bed: tell him how close the run is to its budget; rule 35.
- Archive finished worker and checker threads without asking him; rule 36.

**Your model.** Opus 5.5 at medium effort, every master, the planning one too; he raises it at planning when a problem is hard (his ruling 2 of "Run 3 closed", 8 Oct 2026). Every launch names its model: workers and checkers on Opus 5.5 at high effort, readers on Sonnet, nothing below Sonnet.

**Where the full rules live.**
- Discovery and the plan: `.claude/skills/conductor/SKILL.md`.
- The run, checking, landing and the review: `.claude/skills/run/SKILL.md`.
- Flags, wrap, cut-offs, shutdown list, exchanges: `tracks.md`.
- How he works, and how to ask him: `operator.md`.
- What binds the agents you start: `worker-rules.md`.
