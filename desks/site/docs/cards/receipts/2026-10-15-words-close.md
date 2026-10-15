DONE — every readable line of the page is numbered in words.md, and the words sheet for K2 is built and checked, not published

# Receipt — 2026-10-15-words — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-words.md` · Branch: `task/foundry-north-website/2026-10-15-words` · Worker: Opus 5.5 (claude-opus-5-5[1m]) in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-words`

## Shipped
- `desks/site/docs/words.md`: all 36 lines the gate reads from the page (W1 to W36), grouped under `head` and the eight section ids in page order, each in backticks with its source; the five ruled lines marked ruled.
- `docs/pages/2026-10-15-words-sheet-1.html`: from the blank; "Words · about 30 minutes · 31 questions"; one item block per line with its own miniature-page picture; a keep · b change (text box) · c drop (only where the page survives without it), my recommendation, a note box; ruled lines shown, not asked; read-back copies letters, words and notes; where-this-comes-from at the end.
- `desks/site/public/index.html`: two lines redrafted, words only: W18 "You sit down once, on camera." → "You sit down once a month, on camera."; W12 (screen-reader label of the film frame) "A 16 by 9 frame. Film coming soon." → "A space for our film, coming soon."

## Test it
All at `7c85157`, from the worktree's top folder, scratch `C:\Users\3070s\AppData\Local\Temp\fnw-words-worker` (gates saved there from the cards).
- `python3.11 <scratch>/gate_words.py` → `GATE PASS`, exit 0.
- `python3.11 tools/page_check.py docs/pages/2026-10-15-words-sheet-1.html --project .` → `ALLOW`, exit 0.
- `python3.11 tools/people_check.py` → `ALLOW: private project, and no file held apart holds a person's detail`, exit 0.
- Piece 1: `python3.11 <scratch>/gate_page.py desks/site/public <scratch>/serve` → `GATE PASS`, exit 0.
- Piece 3: `python3.11 <scratch>/gate_og.py desks/site/public` → `GATE PASS`, exit 0.
- Ablation: the words gate with its path pointed at an empty file (`<scratch>/gate_words_ablate.py`) → `GATE FAIL`, 36 `not in words.md:` lines, one per line, exit 1.
- The sheet in headless Chrome inside a 390-wide frame (`<scratch>/probe.html`): 31 questions, 36 item blocks; tapping W8 b with a typed line and W10 c with a note gave the read-back `… W8b · W10c …`, "1 note will be copied too", and both kept in local storage; page width 375, no sideways scroll. The clipboard itself was not tried (headless).

## Unsure
- The title block carries "Part of: Design · 4 of 6" beside "Words · about 30 minutes": `page_check` refuses a page with no recognised stage, and the brief's § Design is where the line-by-line words approval is named. A run-time key point has no stage of its own in the check.
- The two redrafts (W18 "once a month", from the offer's one session on camera in the month; W12) are my calls, listed on the sheet with their undo.
- No c (drop) is offered on 24 of the 31 asked lines (c is on W10, W11, W13, W14, W28, W30, W33), where the page would lose a title, heading, button, step text or step number; his note box can still say "drop".
- Every recommendation is a (keep). W3 and W4 (the preview's title and text) are kept identical to W1 and W2.
- Each item also shows "Comes from" for its line, as part of its evidence, besides the sources at the end and in `words.md`.
- `words.md` lists numbers W1 to W36, ruled lines included, so the sheet's numbers skip the ruled W7, W9, W31, W32, W36.

## Parked
- `tools/page_check.py` knows no stage for a sheet asked during a run (a key point such as K2); it accepts only the six discovery stages or "Review".

## Drift
none. The sheet's script differs from the blank's in `answer()` only, so the copied text carries the line typed under b with the letter; the sheet adds four CSS rules (the quoted line, the ruled mark, the picture's bands). Both serve the card's asks.

## Refused
none.
