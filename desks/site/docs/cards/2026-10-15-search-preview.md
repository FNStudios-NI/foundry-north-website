# search-preview — site — 2026-10-15
Lane: light · a Sonnet helper, then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: screen
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-search-preview` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 06:20` · run 1, piece 3

## Goal
When done:
1. `desks/site/public/index.html`'s `<head>` holds: a `<title>`, a `<meta name="description">`, `<link rel="canonical" href="https://foundrynorthstudios.co.uk/">`, and the Open Graph tags `og:title`, `og:description`, `og:url` (`https://foundrynorthstudios.co.uk/`), `og:type` (`website`), `og:image` (an absolute address, `https://foundrynorthstudios.co.uk/og.png`), plus `twitter:card` `summary_large_image`.
2. One preview picture `desks/site/public/og.png`, 1200 × 630, in the page's Rose look: the name "Foundry North" and the tagline "An engine that understands you better every month." set in the page's own Inter (from `desks/site/public/fonts/`), on the porcelain base. Made by drawing an HTML frame at 1200 × 630 in headless Chrome and saving the shot; the frame itself stays in scratch, not in `public/`.
3. The title and description words follow the page's own draft words (no em dash, no exclamation mark, no price, no client name); piece 2 will put them to him with the rest.
Nothing else on the page changes.
Must merge first: piece 1, the-page (on main). Inputs: `desks/site/public/` at main after piece 1's landing.

## Gate — run it; done means this passes
Save the script below as `gate_og.py` in your scratch folder, then, from the worktree's top folder:
`python <scratch>/gate_og.py desks/site/public` → `GATE PASS` (exit 0).

```python
import html.parser, os, struct, sys
pub = sys.argv[1]
class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.m = {}; s.title = ""; s._t = False
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "meta": s.m[a.get("property") or a.get("name")] = a.get("content")
        if tag == "link" and a.get("rel") == "canonical": s.m["canonical"] = a.get("href")
        s._t = tag == "title"
    def handle_data(s, d):
        if s._t: s.title += d
    def handle_endtag(s, tag): s._t = False
p = P(); p.feed(open(os.path.join(pub, "index.html"), encoding="utf-8").read())
fails = [k for k in ("description", "canonical", "og:title", "og:description", "og:url", "og:type", "og:image", "twitter:card") if not p.m.get(k)]
if not p.title.strip(): fails.append("title")
if p.m.get("canonical") != "https://foundrynorthstudios.co.uk/": fails.append("canonical address")
if p.m.get("og:image") != "https://foundrynorthstudios.co.uk/og.png": fails.append("og:image address")
png = os.path.join(pub, "og.png")
if not os.path.isfile(png): fails.append("og.png missing")
else:
    w, h = struct.unpack(">II", open(png, "rb").read()[16:24])
    if (w, h) != (1200, 630): fails.append("og.png is %dx%d" % (w, h))
print("GATE PASS" if not fails else "GATE FAIL\n" + "\n".join(fails)); sys.exit(1 if fails else 0)
```
Ablation: run the gate on main's `desks/site/public` (before this card): it fails.
Also: the piece 1 gate (in `desks/site/docs/cards/2026-10-15-the-page.md`) still prints `GATE PASS` on the changed folder.
Forbidden: a change outside Touches; any change to the page outside its `<head>`; a push to `main`.
Scratch: `C:\Users\3070s\AppData\Local\Temp\fnw-search-preview-worker`; named in the receipt and removed by that exact name only, never a pattern.

## Touches
`desks/site/public/` · `desks/site/docs/cards/receipts/2026-10-15-search-preview-close.md`

## Read first
`desks/site/CLAUDE.md` · `desks/site/public/index.html` · `docs/brief.md` § Design · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 25 minutes of work, about 2 minutes of Rhys's try (the preview picture, shown with the words sheet). Hard stop at 40 turns.
