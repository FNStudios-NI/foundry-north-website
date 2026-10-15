DONE — the logo banner sits in its own `#logos` section between the film and how it works, the trust section is back as before piece 7, and all five gates print GATE PASS

# Receipt — logo-banner-move — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-logo-banner-move.md` · Branch: `task/foundry-north-website/2026-10-15-logo-banner-move` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-logo-banner-move`

## Shipped
- `desks/site/public/index.html`: the "Worked with" label and the banner (both rows, all four lists, byte for byte as landed in piece 7) moved out of `#trust` into a new `<section id="logos">` after `#film` and before `#how`.
- `#trust` is back to its two trust lines and its hairline, identical to before piece 7.
- Spacing only: `#trust .with{margin-top:56px}` became `#logos .with{margin-top:64px}`, and `#logos .with{margin-top:96px}` at 860 px and up. No other CSS changed.
- `desks/site/docs/words.md`: W37 moved, unchanged, under a new `## #logos` heading between `#film` and `#how`; W38 `University` and W39 `Company` added there for the stand-in alts, each marked "stand-in, replaced by his logos' names" (Goal 3 as corrected at 07:18).

## Test it
Scratch: `C:\Users\3070s\AppData\Local\Temp\fnw-banner-move-worker`. Each gate was cut by script from its card's code block (`gate_banner.py` with `id="trust"` changed to `id="logos"`, nothing else), and run from the worktree top at `f8a35862c5a4c718bd172f53c4ddfa4bd6f5719e`:
- `python3.11 <scratch>/gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_og.py desks/site/public` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_banner.py` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_move.py` → `GATE PASS`, exit 0
- `python3.11 <scratch>/gate_words.py` → `GATE PASS`, exit 0 (at `388d9c2`, before W38 and W39, it printed `GATE FAIL`, exit 1: `not in words.md: University` ×5, `not in words.md: Company` ×5)
- Ablation, `gate_move.py` with its path pointed at main's `index.html` (`git show main:…` into `<scratch>/main/`) → `GATE FAIL`, exit 1: `logos section not between film and how: [7896, -1, 12957]`, `logos still inside the trust section`
- Ablation, the words gate pointed at main's `index.html` and `words.md` → `GATE FAIL` (the ten alts), exit 1: the failure came from piece 7, and W38 and W39 fix it.
- Byte checks by script: the moved block equals main's banner block; the `#trust` section equals the one at `50098f9^`; against main, the page's lines differ only by the new section's open and close, one blank line and the two spacing rules (one replaced, one added).
- Line endings: both files CRLF in the worktree (291 lines / 291 CRs; 75 / 75), stored as LF by git. `git diff main --stat`: index.html 31+/27−, words.md 6+/1−.
- Screenshots in scratch: `shot-390.png` (a 390-wide frame) and `shot-1280.png` (1280 wide), each from the film frame through the banner to the "How it works" heading.

## Unsure
- Spacing: about 70 px film to label and 90 px banner to "How it works" on a phone; about 100 px and 140 px at 1280 (the second gap is `.sec`'s existing top padding, untouched). Left as they are; he judges them on the preview.
- The new section has no `aria-label`: "Worked with" is visible text above the logos, and an `aria-label` would be a new word for `words.md`, which the card closes.

## Parked
none

## Drift
none

## Refused
none

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: 888bc0d1a6abd1fec9ea216e7be7fd44986cdc58
Exit code: 0
Verdict: PASS
Why: Scratch `C:\Users\3070s\AppData\Local\Temp\fnw-banner-move-checker`; each gate cut by script from its card's code block (gate_banner.py with `id="trust"` → `id="logos"`, nothing else), run from the worktree top at the commit above. All five print `GATE PASS`, exit 0: `gate_page.py` (piece 1), `gate_og.py` (piece 3), `gate_banner.py`, `gate_move.py` (the exit code above), `gate_words.py`. Ablation: `gate_move.py` on main's `index.html` (in scratch) → `GATE FAIL`, exit 1 (`logos section not between film and how: [7896, -1, 12957]`; `logos still inside the trust section`). Diff read whole (`git diff main...HEAD`, 3 files, all in Touches; `fence_check.py` → `INSIDE: all 3 changed file(s) are in the card's Touches (against main).`). By script: the banner block (label, both rows, four lists, alts, two aria-hidden rows) is byte-identical to main's `#trust` banner; `#trust` is the two lines plus the `.sig` hairline; sorted-line diff of `index.html` against main shows only the new section's open and close, one blank line, `#logos .with{margin-top:64px}` replacing `#trust .with{margin-top:56px}`, and `#logos .with{margin-top:96px}` in the 860px+ block. `words.md`: W37 moved unchanged under a new `## #logos` between `#film` and `#how`; W38 `University` and W39 `Company` added, each marked stand-in; nothing else changed. Screenshots (mine, in scratch): `shot-390.png` (390-wide frame) and `shot-1280-full.png` (1280 wide, full page from the top). They show the film frame, a "WORKED WITH" label, the two staggered rows of stand-in marks, then "HOW IT WORKS". Measured gaps: film to label 64px and banner to "How it works" 92px at 390; 96px and 140px at 1280. The banner reads as a quiet strip between the film and the how-it-works block, with room on both sides, and nothing overflows sideways. Scope: no, nothing in this diff is unasked for by the card; the moved banner, the trust restoration, the spacing rules (the card allows spacing adjustment) and the W37/W38/W39 lines are all asked. The `git diff` of `index.html` reads large only because git shows how/who/trust as moved rather than the banner.
