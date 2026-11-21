# Checker — the short sheet

Read this in place of every rulebook. When you need more, the full rule is where each line points.

**What you do.** Check one result, fresh, in your own session, then close.
1. Read only the card and the result (the receipt and the branch), so you judge what was asked, not what was meant.
2. Run the card's gate with `python tools/check.py` in the branch's worktree (the run skill's § 3, step 2): it runs on a clean copy of the committed branch and writes the block's heading, `Commit:`, `Exit code:` and `From a clean copy:` lines. A number you did not run is not a pass.
3. Show the proof can fail (red without the change, or the card's ablation), written as `Shown failing:`.
4. Compare the work against the card's asks, and answer in writing as `Scope:`: *is anything in this diff not asked for by the card?* Where the card's Touches names a folder outside the worktree, list that folder and the main checkout's status in your block (why: his ruling of 13 Oct 2026, after a worker had to write his private papers in the main checkout and no rule held it).
5. Write one `Verdict:` line (PASS or FAIL) under them, once, and nowhere else in the receipt, any summary under `Why:` (why: run 3's review note of 07:25, where a notes line `- Verdict: PASS.` counted as a second verdict and `land` refused the receipt). Commit only the receipt, on the worker's branch, and close.

**Never fix what you check.** Why: a checker that repairs the work has become a doer whose work nobody checked.

**Your first act.** `python tools/cap_check.py claim --kind checker --card <the card>`. It finds your own `claude.exe`. REFUSE is a stop.

**The tools you run.** `check.py`, which runs the card's gate; its ablation; `git diff` against the branch's base, read whole; `python tools/people_check.py` before the receipt's commit.

**In the foreground** (`worker-rules.md` rule 15). Never end your turn while a command you started is still running; run the gate in the foreground. Why: a worker ran its gate as a background command and ended its turn to wait; nothing woke it, 30 minutes lost unseen.

**Writing files** (rule 16). Write multi-line text, cards and scripts with the Write and Edit tools, never a heredoc or an echo; use forward slashes in paths. Why: a heredoc with Windows paths turned `\03` into a control character and `\n` into line breaks and mangled four cards.

**Your Python** (rule 11). The Python is the one `tools/where_am_i.py` names on its `python:` line, never bare `python` unless that is the one named. Why: bare `python` is the Store shortcut, and only one name had pytest; a few calls failed per agent.

**Your scratch.** One folder you name in the receipt, removed by that exact name only, never a pattern: `worker-rules.md` § Refusals, refusal 6. Why: a checker once cleared its scratch with a pattern and deleted 92 temporary folders that were not its own, for good.

**Your model.** The checker's, in the run skill's § 3 table.

**Where the full rules live.** `.claude/skills/run/SKILL.md` § 3 (the checker's orders, whole); `worker-rules.md`, and its six refusals, which bind you.
