NOT DONE — the banner is moved and four of five gates pass, but the words gate fails, as it already does on main, on the stand-in alts "University" and "Company", which this card forbids adding to words.md

# Receipt — logo-banner-move — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-logo-banner-move.md` · Branch: `task/foundry-north-website/2026-10-15-logo-banner-move` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-logo-banner-move`

## Shipped
- `desks/site/public/index.html`: the "Worked with" label and the banner (both rows, all four lists, byte for byte as landed in piece 7) moved out of `#trust` into a new `<section id="logos">` after `#film` and before `#how`.
- `#trust` is back to its two trust lines and its hairline, identical to before piece 7.
- Spacing only: `#trust .with{margin-top:56px}` became `#logos .with{margin-top:64px}`, and `#logos .with{margin-top:96px}` at 860 px and up. No other CSS changed.
- `desks/site/docs/words.md`: W37 moved, unchanged, under a new `## #logos` heading between `#film` and `#how`.

## Test it
Scratch: `C:\Users\3070s\AppData\Local\Temp\fnw-banner-move-worker`. Each gate was cut by script from its card's code block (`gate_banner.py` with `id="trust"` changed to `id="logos"`, nothing else), and run from the worktree top at `388d9c2d66bd7c1d4f171cd58054617695d7dc83`:
- `python3.11 <scratch>/gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_og.py desks/site/public` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_banner.py` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_move.py` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_words.py` → `GATE FAIL`, exit 1: `not in words.md: University` ×5, `not in words.md: Company` ×5
- Ablation, `gate_move.py` with its path pointed at main's `index.html` (`git show main:…` into `<scratch>/main/`) → `GATE FAIL`, exit 1: `logos section not between film and how: [7896, -1, 12957]`, `logos still inside the trust section`
- The same words gate pointed at main's `index.html` and `words.md` → the same `GATE FAIL` (the ten alts), exit 1. The fail is from piece 7, not from this move.
- Byte checks by script: the moved block equals main's banner block; the `#trust` section equals the one at `50098f9^`; against main, the page's lines differ only by the new section's open and close, one blank line and the two spacing rules (one replaced, one added).
- Line endings: both files CRLF in the worktree (291 lines / 291 CRs; 73 / 73), stored as LF by git. `git diff --stat`: index.html 31+/27−, words.md 4+/1−.
- Screenshots in scratch: `shot-390.png` (a 390-wide frame) and `shot-1280.png` (1280 wide), each from the film frame through the banner to the "How it works" heading.

## Unsure
- The words gate: the card makes it a gate and also says nothing else in `words.md` changes. It cannot pass without two W lines for the stand-in alts "University" and "Company" (piece 7's receipt left them out on purpose), or without changing the gate. Master's call: a one-line card adding them (marked stand-in), or ruling the gate passes with those two alts set aside.
- Spacing: about 70 px film to label and 90 px banner to "How it works" on a phone; about 100 px and 140 px at 1280 (the second gap is `.sec`'s existing top padding, untouched). His eye may want them even.
- The new section has no `aria-label`: "Worked with" is visible text above the logos, and an `aria-label` would be a new word for `words.md`, which the card closes.

## Parked
- The words gate fails on main since piece 7 (stand-in alts not in `words.md`); see Unsure.

## Drift
none

## Refused
none
