# Retired — foundry-north-website

The rules moved out of what agents read: each was a numbered rule of `tracks.md` or `worker-rules.md` that nobody named in five closed jobs. Why: his ruling 2 of 17 Nov 2026, "the record never forgets; what agents read stays small"; long rule files are what agents drift from, so a rule nobody needs leaves them and is kept here word for word, never deleted.
Written only by `python tools/upgrade.py --retire <file> <n>`, which leaves `<n>. Retired <yyyy-mm-dd>: docs/retired.md.` in the rule's place, so no other rule's number moves; `python tools/upgrade.py --restore <file> <n>` puts it back and notes it under its entry.
A line here is listed at the review like a merged piece, with its undo.
One line per retired rule, in this form, its Why: lines kept under it after `  | `:
`- <yyyy-mm-dd> · <file> · "<the line, word for word>" · why: <one line> · undo: <the command that puts it back>`

- 2026-11-19 · tracks.md · "3. **A running master keeps one flag,** in `docs/runs/<n>/flag.txt`: one line, `<flag> <UTC time> <one plain line why>`." · why: nobody named it in the last 5 closed jobs (upgrade.py's retire list) · undo: python tools/upgrade.py --restore tracks.md 3
  |    For example: `working 2026-10-07T05:10Z started the merge-check worker`.
  |    Why: one line is all the box needs to know how the run stands, and the time tells it how long it has stood so.
- 2026-11-19 · tracks.md · "27. **The night queue reads `run paused: needs him` as done:** the next project starts, and this run's blocker waits for the morning." · why: nobody named it in the last 5 closed jobs (upgrade.py's retire list) · undo: python tools/upgrade.py --restore tracks.md 27
  |     Why: one stuck project must not hold a night's work for the others.
- 2026-11-21 · tracks.md · "5. **Never committed.** The template's `.gitignore` lists `docs/runs/*/flag.txt`, and adopt adds that line to a project that lacks it." · why: nobody named it in the last 5 closed jobs (upgrade.py's retire list) · undo: python tools/upgrade.py --restore tracks.md 5
  |    Why: the flag is a live signal, not the record. Committed, it would add a commit at every change and leave an old flag in every copy of the project.
