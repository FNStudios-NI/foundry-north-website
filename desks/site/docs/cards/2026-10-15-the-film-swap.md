# the-film-swap — site — 2026-10-15
Lane: standard · an Opus worker, a Sonnet checker, then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: screen
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-the-film-swap` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 07:04` · run 1, piece 8 (his new film, a swap)

## Goal
His words: "file send" (his new export, 15 Oct, after "i want to change the vide slightly"). Piece 8 is on main; this card swaps the film file only.
When done:
1. `desks/site/public/film/foundry-north-header.mp4` is replaced, byte for byte, by `C:\Users\3070s\Downloads\foundry-north-studios-header-video-low-bitrate-fixed.mp4` (25,959,232 bytes, under Cloudflare's 25 MiB = 26,214,400; read only, never moved or changed). Same path and name, so the page's markup does not change.
2. Nothing else changes: not the page, not the words.
Must merge first: none (piece 8 on main). Inputs: the file above.

## Gate — run it; done means this passes
The piece 1, piece 3 and words gates (cut from `2026-10-15-the-page.md`, `2026-10-15-search-preview.md`, `2026-10-15-words.md`) and `gate_logos.py` (from `2026-10-15-logos-in.md`) print `GATE PASS`; and this, saved as `gate_film.py` in scratch, `python <scratch>/gate_film.py` → `GATE PASS`:

```python
import hashlib, os, re, sys
src = r"C:\Users\3070s\Downloads\foundry-north-studios-header-video-low-bitrate-fixed.mp4"
dst = "desks/site/public/film/foundry-north-header.mp4"
h = open("desks/site/public/index.html", encoding="utf-8").read()
fails = []
if not os.path.isfile(dst): fails.append("film file missing")
else:
    if os.path.getsize(dst) >= 25 * 1048576: fails.append("film is 25 MiB or more")
    if hashlib.sha256(open(dst, "rb").read()).hexdigest() != hashlib.sha256(open(src, "rb").read()).hexdigest(): fails.append("film is not his file byte for byte")
film = re.search(r'<section[^>]*id="film".*?</section>', h, re.S)
v = re.search(r"<video[^>]*>", film.group(0)) if film else None
if not v: fails.append("no video in the film section")
else:
    tag = v.group(0)
    for a in ("autoplay", "muted", "loop", "playsinline", 'src="film/foundry-north-header.mp4"'):
        if a not in tag and a not in film.group(0): fails.append("video lacks " + a)
    if "controls" in tag: fails.append("video has controls")
    if "<svg" not in film.group(0) or 'class="b"' not in film.group(0): fails.append("the waveform overlay is gone")
if "Film coming soon" in h: fails.append("'Film coming soon' still on the page")
if not re.search(r"prefers-reduced-motion", h): fails.append("no reduced-motion handling")
print("GATE PASS" if not fails else "GATE FAIL\n" + "\n".join(fails)); sys.exit(1 if fails else 0)
```
Ablation: `gate_film.py` on main (before this card) fails on the byte-for-byte check.
Also: one screenshot of the frame at 390 wide with the new film playing under the waveform, in scratch, named in the receipt.
Forbidden: a change outside Touches; changing, moving or deleting his film files in Downloads; the 47.9 MB original anywhere in the project; a push to `main`.
Scratch (worker and checker alike): `C:\Users\3070s\AppData\Local\Temp\fnw-film-swap-worker` · `C:\Users\3070s\AppData\Local\Temp\fnw-film-swap-checker`; removed by that exact name only.

## Touches
`desks/site/public/film/foundry-north-header.mp4` · `desks/site/docs/cards/receipts/2026-10-15-the-film-swap-close.md`

## Read first
`desks/site/CLAUDE.md` · `desks/site/public/index.html` · `desks/site/docs/words.md` · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 10 minutes of work, about 2 minutes of Rhys's look. Hard stop at 20 turns.
