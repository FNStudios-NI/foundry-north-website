# logo-banner — site — 2026-10-15
Lane: standard · an Opus worker, a Sonnet checker, then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: screen
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-logo-banner` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 07:04` · run 1, piece 7

## Goal
His words (07:04): "logos of the university's and bigger companies we have worked with … can you get a banner with the example logos that move across like a banner in 2 layers with a parallax motion."
When done:
1. Inside `<section id="trust">`, after the two trust lines, a banner of logos: two rows, each scrolling sideways in an endless loop, the two rows at different speeds (and, if it reads better, opposite directions) so they move like two layers with a parallax depth: the back row smaller, fainter and slower; the front row larger, full strength and faster. Pure CSS animation (transform only, so it runs smoothly on a phone); no script needed for the loop. A short label above it in his voice, for his approval with the page (e.g. "Worked with", no em dash, no exclamation mark).
2. Stand-in logos now: 8 to 12 plain SVG marks in `desks/site/public/logos/`, named `standin-01.svg`, `standin-02.svg`, …, each a neutral grey rounded word-mark reading "University" or "Company" (no real name, no real logo, nothing that looks like one). The rows read their logos from one list in the page's markup, so swapping in his real logos is replacing the files and their `alt` text, nothing else. Logos in the Rose look: one tone (ink at reduced strength, or the label colour), not their own colours; on hover or focus nothing is needed.
3. Phone first: no sideways scroll of the page at 360 px (the banner clips its own overflow inside its own box); `prefers-reduced-motion: reduce` stops the motion and shows the logos still, wrapped in rows. Each logo has an `alt`; the moving duplicate copies (for the seamless loop) are `aria-hidden="true"`.
4. Nothing else on the page changes.
Not in this card: his real logos (dropped in when he sends them); his film (piece 8).
Must merge first: none (pieces 1, 2, 3 are on main). Inputs: `desks/site/public/` at main.

## Gate — run it; done means this passes
The piece 1 gate (in `desks/site/docs/cards/2026-10-15-the-page.md`) prints `GATE PASS` on the changed folder, and the piece 3 gate (in `2026-10-15-search-preview.md`) prints `GATE PASS`; and this check, saved as `gate_banner.py` in scratch and run from the worktree top, `python <scratch>/gate_banner.py` → `GATE PASS`:

```python
import os, re, sys
pub = "desks/site/public"
h = open(os.path.join(pub, "index.html"), encoding="utf-8").read()
fails = []
trust = re.search(r'<section[^>]*id="trust".*?</section>', h, re.S)
if not trust: fails.append("no trust section")
else:
    t = trust.group(0)
    imgs = re.findall(r'<img[^>]*src="logos/[^"]+\.svg"[^>]*>', t)
    if len(imgs) < 8: fails.append("fewer than 8 logo images in the trust section")
    for i in imgs:
        if 'alt="' not in i: fails.append("a logo without alt: " + i[:60])
    if t.count("aria-hidden") < 1: fails.append("duplicate rows not hidden from screen readers")
css = h + "".join(open(os.path.join(r, f), encoding="utf-8").read() for r, _, fs in os.walk(pub) for f in fs if f.endswith(".css"))
if len(re.findall(r"@keyframes", css)) < 1 or not re.search(r"animation[^;]*\d+(\.\d+)?s", css): fails.append("no CSS loop animation")
if not re.search(r"prefers-reduced-motion:\s*reduce", css): fails.append("no reduced-motion rule")
logos = sorted(f for f in os.listdir(os.path.join(pub, "logos"))) if os.path.isdir(os.path.join(pub, "logos")) else []
if not logos or any(not re.fullmatch(r"standin-\d\d\.svg", f) for f in logos): fails.append("logos/ must hold only standin-NN.svg files: %s" % logos)
print("GATE PASS" if not fails else "GATE FAIL\n" + "\n".join(fails)); sys.exit(1 if fails else 0)
```
Ablation: run `gate_banner.py` on main's folder (before this card): it fails.
Also: a short screen recording or three screenshots a second apart, inside a 390-wide frame, showing the rows moving at different speeds, kept in scratch and named in the receipt, for the master's look.
Forbidden: a change outside Touches; any real company or university name or logo; anything loaded from another site; a script library; a push to `main`.
Scratch (worker and checker alike): `C:\Users\3070s\AppData\Local\Temp\fnw-logo-banner-worker` · `C:\Users\3070s\AppData\Local\Temp\fnw-logo-banner-checker`; each is named in its receipt and removed by that exact name only, never a pattern.

## Touches
`desks/site/public/` · `desks/site/docs/words.md` (the banner's label as one new W line, marked "new, for his approval") · `desks/site/docs/cards/receipts/2026-10-15-logo-banner-close.md`

## Read first
`desks/site/CLAUDE.md` · `desks/site/public/index.html` · `docs/brief.md` § Design · `desks/site/docs/words.md` · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 45 minutes of work, about 3 minutes of Rhys's look on the preview. Hard stop at 60 turns.
