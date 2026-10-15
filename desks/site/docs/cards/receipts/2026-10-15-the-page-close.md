DONE — `desks/site/public/index.html` is the one page in the ruled order, to style C Rose, phone first, with Inter kept in the folder

# Receipt — the-page — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-the-page.md` · Branch: `task/foundry-north-website/2026-10-15-the-page` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-the-page`

## Shipped
- `desks/site/public/index.html`: one page, blocks in order `header#name` · `#top` · `#film` · `#how` · `#founders` · `#organisations` · `#trust` · `#contact`, one inline stylesheet, no script.
- Style C Rose: the brief's palette hex values, centred, ink pill buttons, rose (`#e9b4b7` into `#d1808c`) only on the film frame's waveform and the step marks, `#c99c85` hairlines, warm shadows; tagline and "your own mini studio" in place.
- The film frame is one `.frame` with `aspect-ratio: 16 / 9`; a `<video>` or `<iframe>` put inside it fills it (`.frame > video, .frame > iframe` absolutely placed, full size).
- `desks/site/public/fonts/`: `Inter-Regular.woff2`, `Inter-Medium.woff2`, `Inter-SemiBold.woff2` and `OFL.txt` (the release's `LICENSE.txt`, which is the SIL OFL 1.1), from github.com/rsms/inter release v4.1 (`Inter-4.1.zip`), loaded by three `@font-face` rules.

## Test it
At `616a7851eecd00b02d4334232be7f587149ceb78`, from the worktree's top folder (the gate copied byte for byte from the card to the scratch folder):

`python3.11 C:/Users/3070s/AppData/Local/Temp/fnw-the-page-worker/gate_page.py desks/site/public C:/Users/3070s/AppData/Local/Temp/fnw-the-page-worker/serve`
```
GATE PASS
```
exit 0. (The server's request log, on stderr, shows only `_wrap.html`, `index.html`, the three woff2 files and a 404 for `favicon.ico`: nothing from another site.)

Ablation: the look's `style-c-rose.html` copied alone as `index.html` into `C:/Users/3070s/AppData/Local/Temp/fnw-the-page-worker/ablation`, same gate, serve folder `.../serve-ablation`:
```
GATE FAIL
sections missing or out of order: {'name': -1, 'top': -1, 'film': -1, 'how': 12495, 'founders': -1, 'organisations': -1, 'trust': 14019, 'contact': 14300}
loads something from another site
no Inter woff2 and OFL.txt in fonts/
no @font-face for Inter from fonts/
```
exit 1.

The 360 px check measures for real: the page has no `overflow-x: hidden` anywhere, so the scrollWidth the gate reads is not masked.

Screenshots for the master's K1 look, headless Chrome, in the scratch folder:
- `C:\Users\3070s\AppData\Local\Temp\fnw-the-page-worker\page-390.png` (the page inside a 390-wide iframe)
- `C:\Users\3070s\AppData\Local\Temp\fnw-the-page-worker\page-1280.png` (1280 wide)

Words check: a search of `index.html` for the digest § 7 avoid list (leverage, unlock, scale, empower, deliver, partner with, forge, alchemy, transformation, AI-powered, FN, Authority Engine), `£` and `?` finds only `initial-scale` in the viewport tag.

## Unsure
- The look's mono labels used IBM Plex Mono from Google. The card asks only for Inter kept in the folder, so labels fall back to the system mono (`ui-monospace`, Menlo, Consolas). Keeping Plex Mono in the folder too would be a later card.
- No `<title>`: the card gives the title to piece 3. Until then the browser tab shows the address.
- Left out of the look as not asked: the look bar, the scroll-in reveal and its script, and the footer (`© 2026 Foundry North Studios`). The page ends at the contact block.
- The trust block shows only its two lines; the look's "Why trust us" label became an `aria-label` (read by screen readers, not shown). The card's order puts "Built by filmmakers" first, so it comes first, which is the reverse of the look.
- The founders and organisations sections sit as two cards in one grid (side by side from 860 px). Each card's heading ("For founders", "For organisations") is an `h2`; the look's "Who it is for / Made around you." heading above them is gone, because the card gives no block for it.
- The words are the look's draft, unchanged except the top's label, now "Your own mini studio" in place of "Foundry North Studios", so the header's name is not said twice. Piece 2 owns them.
- Three static Inter weights (about 340 KB) rather than the one variable file (about 350 KB): about the same size, and plainer `@font-face` rules.

## Parked
- none

## Drift
none

## Refused
none

Scratch folder: `C:\Users\3070s\AppData\Local\Temp\fnw-the-page-worker` (the Inter download, the gate, the serve and ablation copies, the screenshot script and the two screenshots). Left in place for the master's look; remove it by that exact name only.

## Checker run <yyyy-mm-dd> — <who>, own session
Commit: <the full commit id the checker ran at>
Exit code: <the command's exit code>
Verdict: <PASS or FAIL, alone on the line>
Why: <any summary of the verdict goes here, never on a second Verdict line>
<written by the checker, never by the worker: the command and its count; red before the change; the ablation; the diff read whole; the work compared against the card's asks; the verdict. The Commit, Exit code and Verdict lines are read by `tools/merge_check.py`: keep their words as they are. Exactly one line in this block starts with `Verdict`: `Verdict: PASS` or `Verdict: FAIL`, alone; any summary goes under `Why:`. Two Verdict lines are refused.>

## Checker run 2026-10-15 — fresh Sonnet 5.5 checker, own session
Commit: bc1d3145731aa2c4eed680d095d0799ae77ab1f6
Exit code: 0
Verdict: PASS
Why: Re-ran the card's gate myself (script cut from the card into `C:\Users\3070s\AppData\Local\Temp\fnw-the-page-checker`): `python3.11 .../gate_page.py desks/site/public .../serve` printed `GATE PASS`, exit 0; the server log shows only `_wrap.html`, `index.html`, the three woff2 files and a favicon 404 (nothing from another site). Ablation (the look's `style-c-rose.html` alone as `index.html`) printed `GATE FAIL` with four failures (sections missing or out of order, loads from another site, no Inter woff2 and OFL.txt, no Inter @font-face), exit 1, so the gate can fail. `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-the-page.md`: `INSIDE: all 6 changed file(s) are in the card's Touches (against main).` Diff read whole (6 files added: index.html, three Inter woff2 with real `wOF2` headers, OFL.txt which is the SIL OFL 1.1 for The Inter Project Authors, and this receipt; no CRs, no deletes). Goal compared: the eight ids are in the ruled order; `film` is one `.frame` with `aspect-ratio: 16 / 9` that a `<video>`/`<iframe>` fills; trust holds only the two lines; contact is one email button to `mailto:rhys@foundrynorthstudios.co.uk`; the offer is "your own mini studio" and the tagline is in; a search of the page finds no em dash, en dash or dash entity, no exclamation mark in the text, no price or currency sign, no client name, no external URL; the page has no script and no `overflow-x: hidden`. Scope question, "is anything in this diff not asked for by the card?": nothing material. Small extras, none needing removal: the visible address line under the contact button (the card asks for one button; the address is shown as text too), the `.sub` "Teams, schools, companies" line (matches the card's parenthesis), the `aria-label`s, and the look's bar-pulse animation with its reduced-motion rule. Notes for the master's K1 look, not failures: the dusty rose `--lab` (#9c6f79) colours the small labels and `--hot` the focus ring, which is wider than "rose only on the waveform and the step marks" if read strictly; and the receipt's gate run is at 616a785 while the branch head is bc1d314 (receipt-only commit), so I ran at bc1d314 myself. I did not view the screenshots; the 360 px number comes from the gate.
