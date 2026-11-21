<The lesson's form: one line per lesson in `docs/lessons.md`, written as it happens, from any work, only by the one command below, which stamps the clock and gives the number. It ends in the exact line it should become. Why: a rule that lives only in memory fails; the merge rule held only once it was an exact line. And a lesson in a file nobody is made to read is never read, so every lesson goes to one file in one form. Never copied: the tool writes the line.>

- L<nnn> · <yyyy-mm-dd hh:mm> · <from> · <kind> · <what happened, in one line> · file: <file> · "<the exact line>" · seen: <seen>

The one command that writes it (the number and the time are the tool's, never typed):
`python tools/record.py --lesson "<what happened>" --from "<from>" --kind <kind> --about <file> --line "<the exact line>" --seen "<seen>"`
- `<from>`: `run <n>`, `planning`, `exploration`, `research`, `job <name>` or `session`.
- ` · seen: <seen>` only when given; a `works` or `misfire` lesson is refused without it.

The four kinds:
- **change**: a line should be added to or changed in a file; `file:` is where it lands, the line is the line as it would read.
- **works**: a named way of working did its job, and how that was seen (his verdict quoted, a number, a pass line); `file:` is that way of working's own file. The evidence for a lock.
- **misfire**: a locked way of working went wrong, and how that was seen; `file:` is that way of working's own file. The evidence for reopening it.
- **track**: a case that fit no known track was worked out with him; the line is the candidate track as worked out.

`file:` is a file of the project the next master is made to read: a skill, a desk's `CLAUDE.md`, a blank in `docs/blanks/`, `worker-rules.md`, `roles/`, `operator.md`, `tracks.md`, `pages.md`, `CLAUDE.md`, the brief; or the word `template`, for a lesson about the template itself.
Refused: anything under `docs/research/`, a log (`log.md`, `*-log.md`, `docs/log*`), a findings file, a file that does not exist, and `unknown` (written only by the adopt's backlog). Why: a lesson in a file nobody is made to read is never read.
