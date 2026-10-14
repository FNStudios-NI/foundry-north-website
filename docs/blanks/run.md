<The run record: copy to `docs/runs/<n>/run.md` at Go, after the sign-off sitting of run <n>, never at the signature, so the where-am-I check reads `signed` while the sitting is on. Every line carries this computer's clock, read in the same step that writes it. Why: sessions end and messages vanish; this file is what the next master, the checker and the review read. Delete this line.>

# Run <n> — foundry-north-website

## Go
- Start: <yyyy-mm-dd hh:mm>
- Planned end: <yyyy-mm-dd hh:mm>
- Cap: <four | "lifted" — "<his words>">
- Seat claimed: <hh:mm> · `python tools/cap_check.py claim --kind master --card docs/runs/<n>/run.md` → <claim id>
- Seat released: <hh:mm, at the wrap> · `python tools/cap_check.py release <claim id>`

## Shutdown list
Everything the run starts, written here as it starts: sessions, seats, background processes, watches, scheduled wake-ups and page servers. At any stop, `python tools/shutdown.py` stops each item and confirms nothing is left. Why: run 2 left the signal box running and two daily wake-ups that only a deletion stops.
- <hh:mm> · <kind> · <what> · <id> · <how it stops> · open | closed <hh:mm>

## Key points he marked
One line per key point in the signed plan, with his letter, and what happened when the run reached it.
- <hh:mm> · <the key point> · <a | b | c> · <what happened: stopped and told him | told him and showed him on his phone | carried on>

## Unforeseen key points
One line per key point nobody saw coming: what was chosen, the options turned down, and why. The review lays each one out.
- <hh:mm> · <the key point> · chose: <…> · turned down: <each option> · why: <one line>

## Blockers
Work that cannot go on without him, put to him as ways through, each priced in his time. Other work carries on.
- <hh:mm> · <the blocker> · ways through: <each, with its cost to him> · my recommendation: <one>
- <hh:mm> · run paused: needs him   <only when nothing more can go without him; the night queue reads it as done>

## Orders
One line per order, written before any message says "look".
- <hh:mm> · <desk> · tasks <n, m> · <the aim, one line> · `desks/<desk>/docs/asks.md`

## Merges
One line per merge into the try-it build, with its undo.
- <hh:mm> · <card> · squash <commit> · undo: `git revert <commit>`

## It works
One line per card, at the review: its done-when line tried, pass or fail. `measures.py` reads it, and the review page shows it first.
- <hh:mm> · <card> · pass | fail · <how it was tried>

## Next run's list
New ideas that come up mid-run go here, not into this run, unless they are a blocker.
- <hh:mm> · <the idea, in one line> · <where it came from>

## Handover
Written before the context fills, at a quiet moment, never in the middle of a merge.
- <hh:mm> · running: <each worker and checker, its card and worktree> · merges done: <each, with its undo> · open key points: <each> · next step: <one line>
- taken over at <hh:mm> by <the successor master>

## Review notes
One line per lesson, as it happens, from `docs/blanks/review-note.md`.
- <yyyy-mm-dd hh:mm> · <what happened, in one line> · the line it should become: "<the procedure line, as it would read>"
