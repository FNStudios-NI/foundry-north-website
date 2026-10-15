DONE — `#trust` now ends in a "Worked with" banner: two rows of ten stand-in logos looping sideways at different speeds in opposite directions, still and wrapped under reduced motion

# Receipt — logo-banner — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-logo-banner.md` · Branch: `task/foundry-north-website/2026-10-15-logo-banner` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-logo-banner`

## Shipped
- `desks/site/public/index.html`: inside `<section id="trust">`, after the two trust lines and their hairline, the label "Worked with" and a `.banner` with two rows. The back row has 20 px logos at 28 % strength, drifting right one set per 90 s. The front row has 32 px logos at 62 % strength, drifting left one set per 45 s. The motion is CSS only (`@keyframes drift`, a transform from 0 to -50 %), with no script.
- Logos are one tone: ink at reduced strength (`filter: brightness(0)` plus opacity), so real logos in colour will turn the same tone. The banner clips its own overflow, and its edges fade.
- Reduced motion: the animation stops, the aria-hidden copies are hidden, and the one list of ten logos wraps in still rows.
- `desks/site/public/logos/standin-01.svg` … `standin-10.svg`: ten neutral grey (`#8b928e`) word-marks in three plain shapes (outlined pill, square plus word, ring plus word), alternating "University" and "Company".
- `desks/site/docs/words.md`: W37 `Worked with`, marked "new, for his approval".

## Test it
At `9d9f3f8dfb26a2765c61889b468ec4e752911625`, from the worktree's top folder. Each gate was cut byte for byte from its card into the scratch folder `C:\Users\3070s\AppData\Local\Temp\fnw-logo-banner-worker` (S below):
- `python3.11 S/gate_page.py desks/site/public S/serve` → `GATE PASS`, exit 0. The server log showed only `_wrap.html`, `index.html`, the ten `logos/standin-NN.svg`, the three woff2 files and a favicon 404.
- `python3.11 S/gate_og.py desks/site/public` → `GATE PASS`, exit 0.
- `python3.11 S/gate_banner.py` → `GATE PASS`, exit 0.
- Ablation: I ran `gate_banner.py` before any change, when `desks/site/public` was identical to main's (`git diff --quiet main HEAD~1 -- desks/site/public` is clean). It printed `GATE FAIL` / `fewer than 8 logo images in the trust section` / `logos/ must hold only standin-NN.svg files: []`, exit 1.
- `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-logo-banner.md` → `INSIDE: all 12 changed file(s) are in the card's Touches (against main).`
- Screenshots in S, made by `S/shots.py` (headless Chrome, the page in a 390-wide iframe, the animation run on Chrome's main thread so virtual time drives it):
  - `banner-390-t1.png`, `banner-390-t2.png`, `banner-390-t3.png` are taken at 3 s, 4 s and 5 s. The front row moves left about 30 px between frames; the back row moves right about 10 px.
  - `banner-390-reduced.png` is taken with `--force-prefers-reduced-motion`: the ten logos stand still in two wrapped columns, and the back row is gone.
  - `banner-1280.png` is the desktop view.
- Line endings: `index.html` has 287 lines and 287 CRs, `words.md` is all CRLF, and git's autocrlf stores both as LF. The diff is additions only (102 lines).

## Unsure
- "One list in the page's markup": a seamless loop with no script needs copies. The front row's first `<ul>` is the one list, with the ten `alt` texts. Its other three copies (one in the front row, two in the back row) are `aria-hidden` with `alt=""` and point at the same files. Overwriting `standin-NN.svg` and changing the ten `alt` texts swaps every copy. If his logos arrive under new file names, each `src` changes in all four copies (40 lines), or the files keep the stand-in names.
- The two rows show the same ten logos. The back row starts a third of the way through its loop, so the two rows do not line up.
- Placement: the banner sits after the trust lines' rose-gold hairline, not between the lines and the hairline.
- Strength: "full strength" for the front row reads here as ink at 62 %, because the card also asks for ink at reduced strength. The back row is at 28 %.
- The banner's label "Worked with" is W37, numbered after W36 so the existing numbers stay put, and placed in the `#trust` part of `words.md` in page order. The stand-in `alt` texts ("University", "Company") are not W lines. His real logos' `alt` texts (organisation names) will be words a screen reader speaks, so they may need W lines and his approval.
- The stand-in SVGs name Inter, which an image cannot load from the page, so the browser draws them in a system sans (Segoe UI on Windows). This is harmless for stand-ins.
- The edge fade (`mask-image`) and `will-change: transform` are styling and smoothness for the asked banner, not separate features. The checker may judge them otherwise.

## Parked
none

## Drift
none

## Refused
none

Scratch folder: `C:\Users\3070s\AppData\Local\Temp\fnw-logo-banner-worker` holds the three gates, `shots.py`, the serve copies and the five screenshots. It is left in place for the master's look; remove it by that exact name only.
