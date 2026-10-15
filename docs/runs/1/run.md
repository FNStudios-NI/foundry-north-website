# Run 1 — foundry-north-website

## Go
- Start: 2026-10-15 06:18
- Planned end: 2026-10-15 09:18 (hard stop 4½ running hours from Go, 10:48, not counting waits on him)
- Cap: four
- Seat claimed: 06:18 · `python tools/cap_check.py claim --kind master --card docs/runs/1/run.md` → 20261015-061818-master-19820-92e9
- Seat released: <hh:mm, at the wrap> · `python tools/cap_check.py release 20261015-061818-master-19820-92e9`
- 06:18 · Window read at Go (claude -p, rate_limit_event): week 18% used, five-hour window 16%. Budget 10% of his week: the run wraps at 28% of the week.

## Shutdown list
Everything the run starts, written here as it starts: sessions, seats, background processes, watches, scheduled wake-ups and page servers. At any stop, `python tools/shutdown.py` stops each item and confirms nothing is left. Why: run 2 left the signal box running and two daily wake-ups that only a deletion stops.
- 06:18 · seat · the master's seat · 20261015-061818-master-19820-92e9 · cap_check.py release · open
- 06:18 · server · page server for docs/pages, python3.11 http.server port 8741 (started by the planning master) · pid 10820 · taskkill · open
- 06:18 · server · page server for the look's scratch folder, port 8740 (started by the planning master) · pid 12596 · taskkill · open
- 06:18 · tailnet route · tailscale serve paths /fnw (→8741) and /look (→8740) on ni-h3-3070.tail552bbe.ts.net · serve-fnw-look · by hand: tailscale serve --https=443 --set-path=/fnw off, and the same for /look · open

## Key points he marked
One line per key point in the signed plan, with his letter, and what happened when the run reached it.

## Unforeseen key points
One line per key point nobody saw coming: what was chosen, the options turned down, and why. The review lays each one out.

## Blockers
Work that cannot go on without him, put to him as ways through, each priced in his time. Other work carries on.

## Orders
One line per order, written before any message says "look".

## Merges
One line per merge into the try-it build, with its undo.

## It works
One line per card, at the review: its done-when line tried, pass or fail. `measures.py` reads it, and the review page shows it first.

## Next run's list
New ideas that come up mid-run go here, not into this run, unless they are a blocker.

## Handover
Written before the context fills, at a quiet moment, never in the middle of a merge.

## Review notes
One line per lesson, as it happens, from `docs/blanks/review-note.md`.
- 2026-10-15 03:48 · Rhys, after a discovery of about 20 single-question turns: "many of these questions could have been grouped and reduced the amount of back and forth" · the line it should become, in `operator.md` § Asking him to decide and the conductor skill's § 2: "In a talked step, put together in one message every question that does not depend on another's answer, each numbered with its letters; one question at a time only where the next question depends on this answer. Why: his note of 15 Oct 2026 on foundry-north-website: about 20 single-question turns of discovery 'could have been grouped and reduced the amount of back and forth'."
- 2026-10-15 03:50 · the run skill's 1.3 asks for a merge and its undo at the sign-off sitting, but tools/land.py needs docs/runs/<n>/run.md, which 1.6 writes only at Go, after the sitting · the line it should become, in the run skill's 1.3: "The sitting tries the acts that need his hands; the first landing and its undo are tried at Go, on the first piece, with him reachable, since the landing tool writes into the run record that Go creates."
