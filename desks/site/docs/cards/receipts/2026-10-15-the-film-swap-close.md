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
