# Worker rules — every worker, checker and helper in this project

These bind every session that builds or checks, and every helper it starts. A desk or a card may add rules; it may never drop one.
Every rule here came from something that broke first.

**Build so a human can try it, write down how, then stop.** Hardening is a later card.

## Before you start

1. **The first line of your orders names your desk folder.** Read that desk's `CLAUDE.md`, then your card, then its Read-first files.
   Why: the desks share one repo, and the first line is how a session started at the root knows which desk is its own.
2. **Build only in your own worktree, on your own task branch.** Never write in the main checkout: it belongs to the master and holds only the record and checked merges. The one exception: a worker may write in one named folder outside its worktree only when its card's Touches names the folder and the reason, he is told, and its checker lists that folder and the main checkout's status.
   Why: one writer per working copy is what stops two sessions overwriting each other's work. The exception is his ruling of 13 Oct 2026: a worker once had to write his private papers in the main checkout, and no rule held it.
3. **Sonnet is the lowest model anything runs on.** Any helper you start runs on Sonnet or above, never lower. Helpers default to Sonnet in the project's settings file; a checker names Opus 5.5.
   Why: in testing, four of five cheaper workers cut corners (batched, scripted or faked their rounds), and a fan-out on the top model emptied his allowance twice.

## While you work

4. **Park, never pursue.** A problem you find that the card did not name gets one line under `Parked` in the receipt. Working on it is a scope breach, however real it is.
   Why: Parked lines are the master's inbox. Findings go up, never sideways into the card.
5. **Delete, don't build.** If you find a claim is false, remove the claim; don't build machinery until it comes true. If the Goal rests on it, write `BLOCKED` and name it. Never invent a missing input.
   Why: an unasked build is the commonest way a card grows past its test.
6. **Scope is the card's asks, not what would make its words true.** Extra sections, helpers and "while I'm here" fixes are drift, even inside a file the card names. `Shipped` is never wider than the Goal; name any drift as drift.
   Why: the checker compares your work against what was asked, not only against the gate.
7. **Tests that touch a credential.** A test that builds a client for a real service gets a fake key path and a stub sender when the client is built. Never a stub that raises, or a call limit inside the object: those go live the moment the real code lands. Where code can reach a paid service, its test setup (`conftest.py`) fails any network connection under `pytest`.
   Why: a test must never be able to spend money or touch live data.
8. **Line endings on a Windows checkout.** Files may be CRLF, LF or mixed, and text tools hide it. Measure the carriage returns in a file before editing it (`tr -cd '\r' | wc -c`), keep each file's mode, and check `git diff --stat` before you hand back.
   Why: a whole-file line-ending change hides the real change in the diff.
9. **Commit by naming the paths, except when untracking a file.** The habit is `git add -- <paths>` then `git commit -m "…" -- <paths>`. But `git commit -- <path>` records the file as it sits on disk and ignores the index, so a staged `git rm --cached <file>` with the file still on disk is silently recorded as present.
   An untracking commit runs with no paths, as the only staged change, and the receipt quotes `git ls-files <file>` empty and `git cat-file -e HEAD:<file>` failing.
   Why: found 6 Sept 2026, when a file "left" the index and was still there.

## When you finish

10. **Strip before the receipt.** Read your own diff against the card's Goal, and remove every addition the card did not ask for: an extra section, helper, option, comment or "while I'm here" fix. Each one comes out before the receipt is written.
    Why: in run 2, 5 of 17 pieces failed their first check on trivia, mostly unasked additions, and each one-line fix cost three more sessions.
11. **Write the receipt from `docs/blanks/receipt.md`.** First line DONE, NOT DONE or REFUSED. `Shipped` is five lines at most: what changed and where. `Unsure` holds every call the master or Rhys might reverse.
    Why: the receipt is the proof file the checker reads, and it becomes the pull request's description.
    Run `python tools/people_check.py` before the receipt's commit; a REFUSE is a stop. Why: a third person's details once reached git and a hosted page, and a rule left to good intentions drifts.
    For workers and checkers alike, every `python` in these rules, a card or a gate (the command above included) means the project's Python, found as the conductor skill's § 1 says (`.claude/skills/conductor/SKILL.md`), never bare `python` unless that is the one found. Why: on a fresh Windows machine `python` is the Store shortcut and exits 9009, while a real Python may sit under another name.
12. **You never certify your own work.** A checker re-runs your proof in its own session and writes the `Checker run` block. Never write that block, and never call a number "run by me" unless you ran it.
    Why: five receipts relabelled a worker's own count as "run by me" on 20 Sept.
13. **Reviewers ask the scope question.** Any review you start answers in writing: *is anything in this diff not asked for by the card?* A "yes" forces a fix, and the fix is removal.
    Why: scope drift is easiest to see from outside.
14. **A verdict is the reviewer's own block in the receipt:** its model, its run, its findings, pasted as given. A reviewer that returns nothing is absent, not a pass: say so, ask once more, then write `BLOCKED`. Never write a verdict you did not receive.
    Why: a pass nobody gave is worse than no check at all.

## Refusals

Six stops, not questions. On any of them: stop that act, write `Refused: <which> — <what it wanted to do>` in the receipt, and carry on with the rest of the card (or end, if it was the card's Goal).

1. **Push to `main` or `master`.** You push only your own task branch, and you never merge: the master does.
   Why: a worker shares Rhys's GitHub identity, so nothing on GitHub stops it.
2. **Commit a secret.** Never write a credential into any file. Read it from the environment; `docs/register.md` holds only where it lives.
   Why: a value committed to git stays in its history for good.
3. **Spend money.** No call that bills. A test that could bill is a refusal.
   Why: money is always his.
4. **Change DNS, a router, or what is open to the internet.** No bind address, port-forward, DNS record or tunnel.
   Why: his machines are reached over his private network only, and opening them is his act.
5. **Send or publish anything.** Nothing leaves the machine except your branch push and its pull request.
   Why: what is published cannot be taken back.
6. **Delete outside your worktree.** You may delete only under your own worktree and your scratch folder. Scratch is made in one folder you name yourself and say in your receipt; it is removed by that exact name only; a pattern (a star, a question mark) in any delete command outside your worktree is a refusal; and nothing in the shared Temp that you did not make is ever removed.
   Why: a delete anywhere else can destroy work that is not yours, and deleting for good is his. On 11 Oct 2026 a checker cleared its scratch with a pattern and deleted 92 temporary folders that were not its own, for good.
