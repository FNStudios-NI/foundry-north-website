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

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: ebec57c639b3fe8f5a9c66653b415a2746377b95
Exit code: 0
Verdict: PASS
Why: Every number below was run by me at ebec57c, from the worktree's top folder, scratch `C:\Users\3070s\AppData\Local\Temp\fnw-words-checker` (gates saved there from the cards). The worker's receipt quotes 7c85157; ebec57c differs from it only by the receipt.
- Card gate `gate_words.py` → `GATE PASS`, exit 0. `page_check.py docs/pages/2026-10-15-words-sheet-1.html --project .` → `ALLOW`, exit 0. `people_check.py` → `ALLOW: private project, and no file held apart holds a person's detail`, exit 0. Piece 1 `gate_page.py` → `GATE PASS`, exit 0. Piece 3 `gate_og.py` → `GATE PASS`, exit 0. `fence_check.py --card desks/site/docs/cards/2026-10-15-words.md` → `INSIDE: all 4 changed file(s) are in the card's Touches (against main).`
- Ablation: the words gate pointed at an empty `words.md` (scratch copy) → `GATE FAIL`, exit 1, 36 `not in words.md:` lines (one per page line) and `too few numbered W lines: 0`.
- Beyond the gate: I matched every backticked W line of `words.md` against `index.html` literally (all 36 present, none with an em dash, en dash, exclamation or question mark). Headlines (W8, W15, W17, W20, W23, W25, W27, W30, W34) are all under eight words (the longest, W15, is seven). I read each line against the Avoids list and found no hedge, AI claim or banned word, and no client name, price or private detail. The five ruled lines (W7, W9, W31, W32, W36) are word for word on the page and in `words.md`. Each of the 36 lines has a source; each is his voice line, the brief or "drafted".
- Page diff: `git diff` of `index.html` touches 2 lines, text only (the film frame's `aria-label` W12; the step 1 text W18), both listed as redrafts in `words.md` and on the sheet with their undo. No markup, CSS or script changed.
- Sheet (rendered in headless Chrome inside a 390-wide frame): follows pages.md. 36 item blocks, each with area, problem, links and effect and its own figure; 31 numbered questions (W1 to W6, W8, W10 to W30 except none skipped, W33 to W35), each with a, b (a text box) and a note box; c on 7 lines only (W10, W11, W13, W14, W28, W30, W33), with a recommendation naming what each letter sets in motion; the 5 ruled lines shown with "already ruled" and not asked; the read-back and one copy button; "Where this comes from" at the end. I tapped W8 b with typed words and W10 c with a note: the read-back read `W8b · W10c`, "1 note will be copied too"; with the clipboard refused (headless) the by-hand box appeared already selected. Phone read: page width 375 of 375, no sideways overflow, no diagram text below 11 px, the read-back bar about 20% of a 844-high screen with the text in its own scroll; it reads on a phone.
- Scope: is anything in this diff not asked for by the card? No. The "What I took from your message" block, the title block's "Part of: Design · 4 of 6" and the how-it-works picture are pages.md rules 4, 5 and 7, and the worker named the "Part of" line under Unsure. Judgment calls left for Rhys and the master: W18's "once a month" (the offer's one session in the month, in his files) is a new frequency claim on the public page, with its undo on the sheet; no c is offered on 24 lines. Neither blocks. Parked item (page_check knows no run-time stage) is the worker's and is not mine to act on.
