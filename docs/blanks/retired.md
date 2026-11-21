# Retired — foundry-north-website

The rules moved out of what agents read: each was a numbered rule of `tracks.md` or `worker-rules.md` that nobody named in five closed jobs. Why: his ruling 2 of 17 Nov 2026, "the record never forgets; what agents read stays small"; long rule files are what agents drift from, so a rule nobody needs leaves them and is kept here word for word, never deleted.
Written only by `python tools/upgrade.py --retire <file> <n>`, which leaves `<n>. Retired <yyyy-mm-dd>: docs/retired.md.` in the rule's place, so no other rule's number moves; `python tools/upgrade.py --restore <file> <n>` puts it back and notes it under its entry.
A line here is listed at the review like a merged piece, with its undo.
One line per retired rule, in this form, its Why: lines kept under it after `  | `:
`- <yyyy-mm-dd> · <file> · "<the line, word for word>" · why: <one line> · undo: <the command that puts it back>`
