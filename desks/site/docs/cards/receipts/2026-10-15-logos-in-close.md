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

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: bbe439d7b0a6a0d916d4d3d26fbeee225f68dc4f
Exit code: 0
Verdict: PASS
Why: I ran, in my own scratch (`fnw-logos-in-checker`), each gate cut from its card's code block, at the full commit above: `gate_logos.py` GATE PASS (exit 0); piece 1 `gate_page.py` GATE PASS; piece 3 `gate_og.py` GATE PASS; words `gate_words.py` GATE PASS, `page_check.py` ALLOW, `people_check.py` ALLOW; film `gate_film.py` GATE PASS; move `gate_move.py` GATE PASS. The older `gate_banner.py` (id="trust" changed to "logos"), which the film and move cards nest, FAILS on this branch by design: it demands 8 or more `.svg` logos and a `logos/` folder holding only `standin-NN.svg`, the very thing this card removes; the card names `gate_logos.py` in its place, so I do not count it. Ablation: `gate_logos.py` on main's `desks/site/public` (git archive into scratch) is GATE FAIL (stand-in still in the banner; 0 of 18 logos; 2 named alts; ten stand-in files left), exit 1. `tools/fence_check.py --card ...`: `INSIDE: all 31 changed file(s) are in the card's Touches (against main).`
Diff read whole: 18 PNGs in, ten stand-in SVGs out, `index.html` (`#logos` markup, `filter: grayscale(1)`, reduced-motion selector), `words.md` (W38/W39 out, W40 to W57 in, each "his logos, 15 Oct"), the receipt. Against the card's Goal: 18 distinct logos, 9 in each row, all `.png`, all trimmed (no empty margin seen), one grey tone with no own colours shown (screenshots), motion/speeds/direction/edge fade/label unchanged (CSS diff shows only the filter and the reduced-motion selector changed). Alts: I looked at all 18 source files beside the trimmed ones and every alt matches what its mark reads; the five the worker lists as short names (UCL, ICURe, Eccles, Extern, Bradley) are stated in the Unsure, and I doubt none. `Bradley` is a brushed signature; the reading is plausible, the mark itself is hard to read. Seamless loops: measured in Chrome at 390, 1280, 1920 and 2560 wide: each row's two copies are the same width and the row is exactly twice one copy, so the -50% loop lands on itself; frames at 0 and at one period are byte-identical. One edge note: the back row's copy (843 px) is shorter than the 900 px banner at desktop, so for the last ~57 px of each back-row cycle a gap opens at the row's far end, inside the fade zone and at .28 opacity; there is no jump at the wrap. Not a fail; no card ask covers it.
Screenshots (mine, in `fnw-logos-in-checker` while it lasts, removed with the folder): at 390 wide and 1280 wide, two phases of the loop; and 390 wide with reduced motion (all 18 still, wrapped). Every mark is recognisable in the front row and in the reduced-motion view. In the faint back row (opacity .28, unchanged by the card) Manchester's mark is a small grey block with tiny words, Leeds is small, UCL reads as a grey block with lighter letters (white on black in his file), and Bradley (18 px wide) reads as a faint squiggle, not as a name. For the master: if Bradley or Manchester must read, the front row is the place; the card fixed the row strengths and left the placing to the worker.
Scope: is anything in this diff not asked for by the card? No. Three edits go beyond the card's literal words and I judge each needed by it: (1) the white ground made transparent in each PNG, not a trim only (the card's own multiply example fails in the masked banner, as the worker found; filter grayscale(1) plus transparency meets goal 2); (2) the back row's first copy is no longer `aria-hidden` (needed for the gate's 18 named alts and so all 18 are heard); (3) the reduced-motion wrap selector now covers both rows. Consequence of (2) and (3): under reduced motion all 18 now show still, where before only the front row's ten stand-ins did; this is a change to reduced-motion output the card calls unchanged, but with the back row now carrying real names, hiding nine logos from reduced-motion visitors would be the worse result. The master may rule either way.
