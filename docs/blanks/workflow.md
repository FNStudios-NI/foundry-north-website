<A workflow's own file: one of the project's ways of working (its method skill, or a desk's method), copied from this blank, every <blank> filled, then this note deleted (two lines). It names the workflow and its version, its open doors, its steps, and ends with its dated log of upgrades.
Why: each step's tag says how far it is proven, so each file must say what it was on any given day; his question of 12 Nov 2026, "do we need these all to be stored in a dated log format so as we upgrade and change we have a log going forward" (the upgrade design's Part 8).>

# <the workflow's name> — v<n.m>

Version: v<n.m>   <v1.0 when first written. A change raises it (v1.3 → v1.4), in the same step as its line under `## Upgrades`. Why: a trial's measure and a foundation's jobs are counted against exactly that version.>
Tag: <one of the three tags under Steps>   <the whole workflow's; a first-time job writes every step `idea` or `on trial`>

## Open doors
The steps whose input can vary, each with its known tracks, and the "brainstorm with him" path for a case that fits none. Why: his ruling 8 of 12 Nov 2026, "the unknown that needs to be merged into a working system and then becomes a potential way of doing things": not every case arrives in the shape the workflow was built for.
- Step <n> · <what can vary> · known tracks: <track> (v<n.m>, <its tag>), <…> · none fits: brainstorm with him; what is worked out is written as a `track` lesson with `python tools/record.py --lesson ... --kind track`, a candidate track, used and reviewed like anything else, and in time a foundation as a new variant with its own version.

## Steps
One line per step, in order, each with one tag; each step's rule carries its why. A foundation is never changed quietly: a better way runs as a trial beside it, and replaces it if it wins (his words, 17 Nov 2026). The tags:
- `idea`: not tried yet.
- `on trial` · measure: <what it reads>: being tested in a job, with the measure that says whether it worked, written beside it.
- `foundation · <n> job(s)`: the current way; the next job uses it as written.
1. **<the step's name>** · `<tag>` · <who: him | the master | a worker | a checker | a tool> — in: <what it starts from> — out: <what it hands on> — <its rule, with its why>

## Upgrades
One dated line per change, written in the same step as the change, never edited after; the newest last. `python tools/upgrade.py --check` refuses a kept line in this file with no line here naming its L-number.
Why: a change with no dated line leaves no way to say what the workflow was on the day a result was made.
- <yyyy-mm-dd> · v<n.m> · <what changed> · why: <one line> · from: <L-number or ruling>
