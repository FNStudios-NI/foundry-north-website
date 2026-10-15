DONE — his film now plays in the 16:9 frame like a header (silent, looping, no controls) under the rose waveform, and holds still on its first frame under reduced motion

# Receipt — the-film — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-the-film.md` · Branch: `task/foundry-north-website/2026-10-15-the-film` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-the-film`

## Shipped
- `desks/site/public/film/foundry-north-header.mp4`: his web copy, copied byte for byte (24,052,230 bytes, the same SHA-256 as `Downloads\foundry-north-studios-header-video-low-bitrate.mp4`, `fc95a53f…fecc00`).
- `desks/site/public/index.html`: in `.frame`, a `<video src="film/foundry-north-header.mp4" autoplay muted loop playsinline preload="auto" aria-hidden="true">` comes before the waveform SVG, so the SVG draws on top. A CSS rule `.frame > video{object-fit:cover}` makes it fill the frame. The corners, hairline, shadow, waveform and its pulse are untouched.
- Reduced motion: one inline script line after the video. If `prefers-reduced-motion: reduce` matches, it removes `autoplay`, pauses the film and sets it to 0 s, so the first frame shows.
- "Film coming soon" (`<p class="soon">`) and its now-unused `.frame .soon` CSS rule are gone. The frame's `aria-label` reads `Our film: a short loop from the studio.`
- `desks/site/docs/words.md`: W13 is removed. W12 is the new line, marked "redrafted, for his approval".

## Test it
At `907024c121798bfc296eec2ee18fdf2a163121ba`, from the worktree's top folder. Each gate was cut byte for byte from its card into the scratch folder `C:\Users\3070s\AppData\Local\Temp\fnw-film-worker` (S below), with `id="trust"` changed to `id="logos"` in `gate_banner.py` as the card says:
- Ablation: `python3.11 S/gate_film.py` ran before any change, on a tree identical to main's `desks/site/`. It printed `GATE FAIL` / `film file missing` / `no video in the film section` / `'Film coming soon' still on the page`, exit 1.
- `python3.11 S/gate_page.py desks/site/public S/serve` → `GATE PASS`, exit 0 (this includes the 360 px sideways-scroll check). The server printed a `ConnectionResetError` traceback for `film/foundry-north-header.mp4` because headless Chrome closed while the film was still streaming. It is harmless, and the gate's verdict does not depend on it.
- `python3.11 S/gate_og.py desks/site/public` → `GATE PASS`, exit 0.
- `python3.11 S/gate_words.py` → `GATE PASS`, exit 0.
- `python3.11 S/gate_banner.py` → `GATE PASS`, exit 0.
- `python3.11 S/gate_film.py` → `GATE PASS`, exit 0.
- `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-the-film.md` → `INSIDE: all 3 changed file(s) are in the card's Touches (against main).`
- Playback, by `S/play.py` (the page in a 390-wide iframe, the film read after 3 s):
  - With `--autoplay-policy=no-user-gesture-required`, it printed `t=3.00 paused=false autoplay=true w=1920`.
  - With that flag and `--force-prefers-reduced-motion`, it printed `t=0.00 paused=true autoplay=false w=1920`.
- Screenshots in S, by `S/shots.py` (headless Chrome with the same autoplay flag, scrolled to `#film`):
  - `film-w390.png`: the frame in a 390-wide iframe.
  - `film-w1280.png`: the frame at 1280 wide.
  - Both show the film (a speaker on a rooftop, a bridge behind) with the rose waveform and the rounded, hairlined frame drawn over it.
- Line endings: `index.html` (292 lines, 292 CRs) and `words.md` (74 lines, 74 CRs) are still all CRLF. `git diff --stat main...HEAD` shows 5 insertions and 5 deletions in text, plus the film.
- His files in Downloads are unchanged: the low-bitrate copy is still 24,052,230 bytes and the original is still 47,856,444 bytes. The original is not in the project.

## Unsure
- Autoplay in headless Chrome: without `--autoplay-policy=no-user-gesture-required`, headless Chrome left the muted film paused at 0 s (`t=0.00 paused=true autoplay=true`). Desktop and mobile browsers normally autoplay muted, `playsinline` video, but no real browser was checked here. A look in his own browser settles it.
- W12's new wording `Our film: a short loop from the studio.` is the card's example, used as given. It is for his approval.
- W13 was a ruled placeholder ("the placeholder you ruled"). It is removed because his "a)" and the card ask for that.
- Removing the `.frame .soon` CSS rule goes slightly beyond "the words leave the frame": once the words were gone, the rule styled nothing. The checker may judge it otherwise.
- The reduced-motion script runs once when the page loads. It does not react if the setting changes while the page is open.
- The film is 24 MB, and `preload="auto"` asks phones to fetch it on load. This follows the card. Mobile data use is his call.

## Parked
none

## Drift
none

## Refused
none

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: 0f76b5fc39079b715ceef71b5915752564b8efa9
Exit code: 0
Verdict: PASS
Why: Every gate the card names was cut from its card's code block into `C:\Users\3070s\AppData\Local\Temp\fnw-film-checker` and run in my own process at the commit above, from the worktree top. `gate_film.py` → `GATE PASS`, exit 0. Piece 1 `gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`, exit 0 (includes the 360 px check; the server printed a harmless `ConnectionResetError` for the streaming film). Piece 3 `gate_og.py desks/site/public` → `GATE PASS`. Words `gate_words.py` → `GATE PASS`; its two companions, `page_check.py` → `ALLOW` and `people_check.py` → `ALLOW`. Banner `gate_banner.py` (with `id="logos"`) → `GATE PASS`.
- Ablation: `gate_film.py` run against main's `index.html` (copied into scratch) → `GATE FAIL`: film file missing / no video in the film section / 'Film coming soon' still on the page; exit 1.
- Byte for byte: SHA-256 of `public/film/foundry-north-header.mp4` equals that of `Downloads\foundry-north-studios-header-video-low-bitrate.mp4` (`fc95a53f…fecc00`), both 24,052,230 bytes; the 47,856,444-byte original is still in Downloads only and not in the tree.
- Diff read whole (`git diff main...HEAD`): index.html +4/−3 lines, words.md +1/−2, the film, and the receipt. The `<video>` has `autoplay muted loop playsinline preload="auto" aria-hidden="true"`, no `controls`, sits before the waveform SVG, and gets `object-fit:cover`. The frame's border-radius, hairline, shadow, the SVG and its pulse are untouched. "Film coming soon" and W13 are gone; W12 is redrafted in both the aria-label and `words.md`, marked "redrafted, for his approval". `index.html` is still all CRLF (292/292) and `words.md` 74/74.
- Playback, my own probe (page in a 390-wide iframe, load held 5 s by a slow image, headless Chrome with `--autoplay-policy=no-user-gesture-required`): `t=4.83 paused=false muted=true loop=true`, a different scene from frame 0 (a woman in a hall), so it is playing. With `--force-prefers-reduced-motion`: `t=0.00 paused=true`, first frame (speaker on the rooftop) showing.
- Screenshots (scratch, deleted with it): 390-wide frame (`film-w390-1.png`, `film-w390-2.png`) and 1280 wide (`film-w1280-b.png`). At both widths the film fills the 16:9 frame edge to edge, the rose waveform bars draw on top of it, and the rounded corners, rose hairline and warm shadow are intact; no caption text is left in the frame. At 390 there is no sideways scroll inside the frame.
- Scope question — is anything in this diff not asked for by the card? No. The one item at the edge is the removal of the `.frame .soon` CSS rule, which styled only the deleted "Film coming soon" paragraph; it is dead-rule removal that goes with removing the words, and the worker named it. The reduced-motion script is the "few lines of script" the card allows. Nothing else changed, and no file outside Touches.
- `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-the-film.md` → `INSIDE: all 4 changed file(s) are in the card's Touches (against main).`
- Not checked: a real (non-headless) browser's autoplay; the worker flagged it, and a look in his own browser settles it. The 24 MB `preload="auto"` on phones follows the card.
