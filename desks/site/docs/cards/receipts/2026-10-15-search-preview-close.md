DONE — the page has its title, description, canonical and Open Graph tags, and a 1200 × 630 preview picture in the Rose look

# Receipt — search-preview — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-search-preview.md` · Branch: `task/foundry-north-website/2026-10-15-search-preview` · Worker: Sonnet 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-search-preview`

## Shipped
- `desks/site/public/index.html`: nine lines added in `<head>` only (title, description, canonical, og:title, og:description, og:url, og:type, og:image, twitter:card). Nothing else on the page changed.
- `desks/site/public/og.png`: 1200 × 630, "Foundry North" and the tagline in the page's own Inter (SemiBold and Medium from `fonts/`) on the porcelain base `#e7ede6`, one rose-gold hairline between. Drawn from an HTML frame in headless Chrome; the frame stayed in scratch.
- Title: "Foundry North: your own mini studio". Description (and og:description): "We turn one interview into content that sounds like you. An engine that understands you better every month." Both are lines already on the page; no em dash, exclamation mark, price or client name.

## Test it
At the commit that holds this receipt (the commit before it was 95e7b67):
- `python3.11 gate_og.py desks/site/public` on main's folder before the change: `GATE FAIL` (description, canonical, og:title, og:description, og:url, og:type, og:image, twitter:card, title, canonical address, og:image address, og.png missing). The ablation fails as the card says.
- `python3.11 gate_og.py desks/site/public` after: `GATE PASS`
- `python3.11 gate_page.py desks/site/public <scratch>/serve` (piece 1 gate) after: `GATE PASS`
- `git diff --stat`: `desks/site/public/index.html | 9 +++++++++`; `og.png` new. The file keeps its CRLF working-copy endings (git stores LF).
- Looked at `og.png` by eye: Inter renders, text centred, nothing cut off.
- Not run: an Open Graph reader against the live preview (piece 6 / the master).

## Unsure
- The title and description wording is my pick from the page's own lines, using a colon in the title. Piece 2 puts them to him; either may change.
- The picture's look (type only, no waveform, one hairline) is my reading of "name and tagline on the porcelain base". He may want rose on it.
- The picture is a static file; if the words change, it must be redrawn.

## Parked
none

## Drift
none

## Refused
none

Scratch: `C:\Users\3070s\AppData\Local\Temp\fnw-search-preview-worker` (holds the gate scripts, the frame, a serve copy and og.png), removed by that exact name only.

## Checker run 2026-10-15 — the master (light lane: the scripts, re-run by the master), own session
Commit: ecdcfbff3a849ed605cf4a8d83afcfaeb533fed0
Exit code: 0
Verdict: PASS
Why: light lane, so the gate is re-run by the master, not by a checker. At ecdcfbf, the card's gate_og.py printed GATE PASS (exit 0); piece 1's gate_page.py still printed GATE PASS (exit 0); fence_check --card printed INSIDE (3 files). Ablation: gate_og.py on main's desks/site/public failed (description, canonical and the rest missing). The diff only adds the head tags and og.png, as the card asked (1200 × 630, Inter on porcelain, viewed). Scratch C:\Users\3070s\AppData\Local\Temp\fnw-search-preview-master is removed by name.
