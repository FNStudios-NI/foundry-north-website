# logo-banner-move — site — 2026-10-15
Lane: standard · an Opus worker, a Sonnet checker, then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: screen
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-logo-banner-move` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 07:04` · run 1, piece 7 (continue)

## Goal
His words (07:15), with a screenshot of the preview marking the space between the film frame and "How it works": "put it between here".
When done:
1. The logo banner (its "Worked with" label and both moving rows, exactly as landed in piece 7) is moved out of `<section id="trust">` into its own `<section id="logos">`, placed after `id="film"` and before `id="how"`. Its look, motion, reduced-motion rule, alt text and aria-hidden copies are unchanged; only spacing is adjusted so it sits well between the film frame and "How it works" on a phone and a laptop.
2. The trust section goes back to the two trust lines and its hairline, as before piece 7.
3. `desks/site/docs/words.md`: W37 "Worked with" moves to sit under the new `logos` place, between the film and how-it-works lines; nothing else in it changes.
Must merge first: piece 7 (on main). Inputs: `desks/site/public/` at main.

## Gate — run it; done means this passes
The piece 1 gate (in `desks/site/docs/cards/2026-10-15-the-page.md`) and the piece 3 gate (in `2026-10-15-search-preview.md`) print `GATE PASS`, and the words gate (in `2026-10-15-words.md`) prints `GATE PASS`; and piece 7's `gate_banner.py` (in `2026-10-15-logo-banner.md`), with its `id="trust"` changed to `id="logos"`, prints `GATE PASS`; and this, saved as `gate_move.py` in scratch, `python <scratch>/gate_move.py` → `GATE PASS`:

```python
import re, sys
h = open("desks/site/public/index.html", encoding="utf-8").read()
fails = []
f, l, w = h.find('id="film"'), h.find('id="logos"'), h.find('id="how"')
if -1 in (f, l, w) or not (f < l < w): fails.append("logos section not between film and how: %s" % [f, l, w])
t = re.search(r'<section[^>]*id="trust".*?</section>', h, re.S)
if t and "logos/" in t.group(0): fails.append("logos still inside the trust section")
print("GATE PASS" if not fails else "GATE FAIL\n" + "\n".join(fails)); sys.exit(1 if fails else 0)
```
Ablation: `gate_move.py` on main's folder (before this card) fails.
Also: two screenshots, inside a 390-wide frame and at 1280 wide, of the film frame, the banner and the start of "How it works", in scratch, named in the receipt.
Forbidden: a change outside Touches; any change to the banner's motion or marks; a real name or logo; a push to `main`.
Scratch (worker and checker alike): `C:\Users\3070s\AppData\Local\Temp\fnw-banner-move-worker` · `C:\Users\3070s\AppData\Local\Temp\fnw-banner-move-checker`; removed by that exact name only.

## Touches
`desks/site/public/index.html` · `desks/site/docs/words.md` · `desks/site/docs/cards/receipts/2026-10-15-logo-banner-move-close.md`

## Read first
`desks/site/CLAUDE.md` · `desks/site/public/index.html` · `desks/site/docs/cards/2026-10-15-logo-banner.md` · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 20 minutes of work, about 1 minute of Rhys's look. Hard stop at 30 turns.
