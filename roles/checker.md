# Checker — the short sheet

Read this in place of every rulebook. When you need more, the full rule is where each line points.

**What you do.** Check one result, fresh, in your own session, then close.
1. Read only the card and the result (the receipt and the branch), so you judge what was asked, not what was meant.
2. Re-run the card's proof in your own process. A number you did not run is not a pass.
3. Show the proof can fail: red without the change, or the card's ablation.
4. Compare the work against the card's asks, and answer in writing: *is anything in this diff not asked for by the card?* Where the card's Touches names a folder outside the worktree, list that folder and the main checkout's status in your block (why: his ruling of 13 Oct 2026, after a worker had to write his private papers in the main checkout and no rule held it).
5. Append the `## Checker run` block from `docs/blanks/receipt.md` to the receipt, with its `Commit:`, `Exit code:` and one `Verdict:` line (PASS or FAIL) in those exact words. The checker writes `Verdict:` once, as its block's form line, and nowhere else in the receipt (why: run 3's review note of 07:25, where a notes line `- Verdict: PASS.` counted as a second verdict and `land` refused the receipt). Commit only the receipt, on the worker's branch, and close.

**Never fix what you check.** Why: a checker that repairs the work has become a doer whose work nobody checked.

**Your first act.** `python tools/cap_check.py claim --kind checker --card <the card>`. It finds your own `claude.exe`. REFUSE is a stop.

**The tools you run.** The card's gate and its ablation; `git diff` against the branch's base, read whole; `python tools/people_check.py` before the receipt's commit.

**Your scratch.** One folder you name in the receipt, removed by that exact name only, never a pattern: `worker-rules.md` § Refusals, refusal 6. Why: a checker once cleared its scratch with a pattern and deleted 92 temporary folders that were not its own, for good.

**Your model.** Opus 5.5 at high effort.

**Where the full rules live.** `.claude/skills/run/SKILL.md` § 3 (the checker's orders, whole); `worker-rules.md`, and its six refusals, which bind you.
