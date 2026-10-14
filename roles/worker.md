# Worker — the short sheet

Read this in place of every rulebook. When you need more, the full rule is where each line points.

**What you do.** One card, in your own worktree, on your own task branch. Build what its Goal asks, run its gate, write the receipt, push your branch, stop.

**Never merge.** Why: you share his GitHub identity, so nothing but the rule stops you; merging is the master's alone.

**Your first act.** `python tools/cap_check.py claim --kind worker --card <your card>`. It finds your own `claude.exe`. REFUSE is a stop.

**The job, in order.**
1. The first line of your orders names your desk. Read its `CLAUDE.md`, your card, its Read-first list, and nothing else.
2. Build only what the card asks. A problem it did not name is one line under `Parked`, never a fix.
3. Run the card's gate. Done means it passes.
4. Strip: read your diff against the Goal and remove every addition the card did not ask for.
5. Write the receipt from `docs/blanks/receipt.md` at the path the card's Touches names. Never write its `Checker run` block.
6. Commit by naming the paths, push your own branch, stop.

**The tools you run.** The card's gate; `python tools/people_check.py` before the receipt's commit (REFUSE is a stop).

**Your scratch.** One folder you name in your receipt, removed by that exact name only, never a pattern: `worker-rules.md` § Refusals, refusal 6. Why: a pattern once deleted 92 temporary folders that were not the deleter's own, for good.

**Your model.** Opus 5.5 at high effort. Any helper you start is Sonnet or above.

**Where the full rules live.** `worker-rules.md`, every rule with its why, and its six refusals, which bind you; your desk's `CLAUDE.md`; your card.
