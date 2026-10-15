DONE — his new film (25,959,232 bytes) replaces the old file at the same path; nothing else changed

# Receipt — the-film-swap — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-the-film-swap.md` · Branch: `task/foundry-north-website/2026-10-15-the-film-swap` · Worker: Sonnet 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-the-film-swap`

## Shipped
`desks/site/public/film/foundry-north-header.mp4` replaced byte for byte by `C:\Users\3070s\Downloads\foundry-north-studios-header-video-low-bitrate-fixed.mp4` (24,052,230 bytes before, 25,959,232 after; under 26,214,400). The page and the words are untouched. His file in Downloads was only read.

## Test it
Run in the worktree on top of parent `6bd2373`, before the commit (the commit is the film file plus this receipt):
- `gate_film.py` → `GATE PASS`
- `gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`
- `gate_og.py desks/site/public` → `GATE PASS`
- `gate_words.py` → `GATE PASS`
- `gate_logos.py` → `GATE PASS`
- `python3.11 tools/page_check.py docs/pages/2026-10-15-words-sheet-1.html --project .` → `ALLOW`
- Ablation (`gate_film.py` on main fails the byte check): not run by the worker; the file on main was 24,052,230 bytes, a different size from his file, so it differs by construction.
- Screenshot: `C:\Users\3070s\AppData\Local\Temp\fnw-film-swap-worker\film-390.png` (390 wide; the new film playing in the frame under the waveform).
- Scratch folder: `C:\Users\3070s\AppData\Local\Temp\fnw-film-swap-worker` (left in place for the checker's look; to be removed by that exact name only).

## Unsure
- The gate scripts were cut from the cards by a small extractor in scratch, unedited.
- The screenshot was taken in headless Chrome with a script seeking the video to 3 s, so it shows one frame, not the loop.

## Parked
none

## Drift
none

## Refused
none

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: c09671cc78152e4becbd71daf6162dd497371d08
Exit code: 0
Verdict: PASS
Why: Gates cut by me from the cards' code blocks into my own scratch (`C:\Users\3070s\AppData\Local\Temp\fnw-film-swap-checker`), run from the worktree at the commit above: `gate_film.py` → `GATE PASS` (exit 0, the exit code above); `gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`; `gate_og.py desks/site/public` → `GATE PASS`; `gate_words.py` → `GATE PASS`; `gate_logos.py` → `GATE PASS`. Ablation (the worker did not run it): `gate_film.py` against main's film file (24,052,230 bytes, in scratch with the same `index.html`) → `GATE FAIL` "film is not his file byte for byte", exit 1. Diff vs main: exactly two files, the film file (modified, 24,052,230 → 25,959,232 bytes) and this receipt (added). The film's SHA-256 equals his `foundry-north-studios-header-video-low-bitrate-fixed.mp4` (`403BD21B…FBC11`, 25,959,232 bytes both; 26,214,400 limit not reached). Screenshot at 390 wide (`film-390.png` in my scratch, headless Chrome with autoplay allowed): the new film shows in the frame with the waveform drawn over it. Headless showed the frame slightly cropped on the right; the page is untouched by this diff, so I took that as a headless viewport effect, not this card's. `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-the-film-swap.md` → "INSIDE: all 2 changed file(s) are in the card's Touches (against main)." Scope question — is anything in this diff not asked for by the card? No: only the film swap and the receipt. His file in Downloads and the main checkout were only read (main checkout status empty). Not run: the card does not name the film or move gates, so I did not cut those.
