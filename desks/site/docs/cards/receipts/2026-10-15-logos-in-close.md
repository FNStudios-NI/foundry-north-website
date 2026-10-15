DONE — his 18 logos run in the two-row banner in one grey tone, each named in its alt and in words.md; the stand-ins are gone.

# Receipt — logos-in — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-logos-in.md` · Branch: `task/foundry-north-website/2026-10-15-logos-in` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-logos-in`

## Shipped
- `desks/site/public/logos/`: 18 PNGs under plain names (`cambridge.png`, `innovate-uk.png`, `royal-navy.png`, …), each trimmed to its mark in headless Chrome (canvas), its white ground made transparent; the ten `standin-NN.svg` removed.
- `desks/site/public/index.html` `#logos`: back row 9 logos, front row 9, each with a named `alt`; only the duplicate copies are `aria-hidden` (the back row's own copy now carries names too, so all 18 are heard).
- CSS: `.banner img` filter `brightness(0)` → `grayscale(1)` (one tone; row opacities .28/.62 unchanged); the reduced-motion wrap rule now covers both rows. Speeds, directions, edge fade, label untouched.
- `desks/site/docs/words.md` `## #logos`: W38 and W39 (stand-ins) out; W40–W57, one per name, in page order, marked "his logos, 15 Oct".

## Test it
From the worktree top, scratch `C:\Users\3070s\AppData\Local\Temp\fnw-logos-in-worker`, at af83298 (each gate cut from its card into scratch):
- `python3.11 <scratch>/gate_page.py desks/site/public <scratch>/serve` → `GATE PASS` (its server also logs a ConnectionResetError on the film's stream when Chrome closes; harmless, the gate's last line is the pass)
- `python3.11 <scratch>/gate_og.py desks/site/public` → `GATE PASS`
- `python3.11 <scratch>/gate_words.py` → `GATE PASS`; `python3.11 tools/page_check.py docs/pages/2026-10-15-words-sheet-1.html --project .` → `ALLOW`
- `python3.11 <scratch>/gate_film.py` → `GATE PASS`; `python3.11 <scratch>/gate_move.py` → `GATE PASS`; `python3.11 <scratch>/gate_logos.py` → `GATE PASS`
- Ablation: `gate_logos.py` run inside `<scratch>/main` (main's `desks/site/public` via `git archive main`) → `GATE FAIL`: a stand-in still in the banner; 0 of 18 logos; 2 named alts; ten stand-in files left (exit 1).
- `python3.11 tools/people_check.py` → `ALLOW: private project, and no file held apart holds a person's detail`
- Screenshots in scratch: `banner-1280.png` (1280 wide), `banner-390.png` (inside a 390-wide frame), `banner-390-reduced.png` (390 frame, reduced motion: all 18 still, wrapped). Taken through `frame.html`, an iframe sized to the width and scrolled to `#logos`.

## Unsure
- Names where the mark does not give a full name, so the words on the mark are used: `UCL` (not "University College London"), `ICURe`, `Eccles` (the mark adds "Intelligent Access & Drainage Solutions"), `Extern`, `Bradley` (a brushed signature; I read it as "Bradley", helped by his file name). He may want fuller names.
- `nacy.png` is named `royal-navy.png` (the mark reads ROYAL NAVY); `BR.png` is `brilliant-red-digital.png`.
- The card's example (`grayscale` with `mix-blend-mode: multiply`) failed in test: the banner's mask and moving rows isolate the blend, so the white grounds showed as pale boxes. Instead each file's white ground is made transparent when trimmed (a white-to-alpha step; colours are kept in the file, the page shows them grey). So the files differ from his by more than a trim.
- Which logo sits in which row: the front (larger, stronger) row has Cambridge, Brilliant Red Digital, Imperial, Royal Navy, Edinburgh, Innovate UK, King's, Sandvik, Queen's; the back row the other nine. My choice.
- Tall marks (Royal Navy, Innovate UK, King's, Bradley) read small at a fixed row height beside wide word-marks; his files are about 200 × 150, so the marks are soft on a sharp phone screen.
- Back row's first copy is no longer `aria-hidden` (it was, with stand-ins): needed so all 18 names are heard and the gate's 18 named alts hold.

## Parked
none

## Drift
The reduced-motion wrap selector was widened from the front row to both rows (`.banner .back .logos,.banner .front .logos`), since the back row now shows when still. It is inside the card's Touches; named here because Goal 4 lists reduced-motion as unchanged. The behaviour (motion stops, logos shown still and wrapped) is the same.

## Refused
none
