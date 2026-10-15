DONE — `tools/send_site.py` sends only what git holds in `desks/site/public/` to the site's repository, refuses otherwise, and the contract says so

# Receipt — send-site — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-send-site.md` · Branch: `task/foundry-north-website/2026-10-15-send-site` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-send-site`

## Shipped
- `tools/send_site.py`: clones the site's repository (default `foundry-north-site`, or `--repo`) into its own temp folder, makes the clone's tree exactly the files git holds under `desks/site/public/` at `HEAD`, commits naming the project's commit, pushes `main`; `SENT:` / `NOTHING TO SEND` / `REFUSE:`; `--dry-run` pushes nothing.
- Refuses a symbolic link (or any non-file) in `public/` at `HEAD`, any uncommitted change under `public/` (edit, new file, removal), and a staged clone holding any path not in that list or any file not byte for byte as git holds it here.
- `tools/tests/test_send_site.py`: 8 tests, every one against a local bare repository under `tmp_path`.
- `desks/site/docs/contract.md` § What it hands the rest: `desks/site/public/` is the site and the only part that may be public; `tools/send_site.py` is the only way it crosses to `foundry-north-site`, which Cloudflare publishes.

## Test it
At `c3b32fd230f1d2128cebbd280e95059c56bde328`, in the worktree:

`python3.11 -B -m pytest tools/tests/test_send_site.py -q -p no:cacheprovider --basetemp "C:/Users/3070s/AppData/Local/Temp/fnw-send-site-worker"` →
```
........                                                                 [100%]
8 passed in 13.01s
```
The card's gate as written, `python3.11 -B -m pytest tools/tests/test_send_site.py -q`, gives `8 errors in 2.70s` on this machine, before any test runs: `PermissionError: [WinError 5] Access is denied: 'C:\Users\3070s\AppData\Local\Temp\pytest-of-3070s'` (pytest's shared temp folder, not this card's; see Parked). Hence `--basetemp` pointed at this card's named scratch, and `-p no:cacheprovider` so no cache folder is left in the worktree.

The 8: a send of a small public folder, with files outside it, leaves the remote's tree equal to it, its commit message naming the project's commit · a second send prints `NOTHING TO SEND`, remote unchanged · a file `git rm`ed from `public/` is gone from the remote · refusal on uncommitted changes, three cases (an edit, a new file, a removal), remote unchanged · refusal on a symbolic link, remote unchanged · `--dry-run` lists the files and the remote stays empty.
The symbolic-link test is not skipped anywhere: the link is made in git's index (`update-index --cacheinfo 120000,…`), as a commit from any machine would hold it, so no system symlink is needed.

Ablation (the tool reading the whole of `HEAD` instead of `desks/site/public/`: `ls-tree` without `-- PUBLIC`, paths unstripped), same command: `3 failed, 5 passed in 15.50s` — `test_sends_only_the_public_folder`, `test_a_file_removed_from_public_is_removed_from_the_site`, `test_dry_run_says_what_would_cross_and_pushes_nothing` (its output listed `tools/secret_plan.py` and `desks/site/docs/words.md` crossing). Undone; 8 passed again.

Not run by the worker: any send or `--dry-run` against the real `foundry-north-site` (refusal 5 and the card: the first real send is the master's). `desks/site/public/` does not exist at this branch's base, so the tool would refuse here with `git holds nothing under desks/site/public/ at HEAD`.

Scratch: `C:\Users\3070s\AppData\Local\Temp\fnw-send-site-worker`, used as pytest's `--basetemp` (pytest itself empties it at each run). Removed at the end by that exact name.

## Unsure
- One refusal the card did not list: `git holds nothing under desks/site/public/ at HEAD`. Without it a send from a checkout where `public/` is not yet landed would wipe the site to an empty tree. Strip it if unwanted.
- The staged-clone check also compares each file's blob id with the project's, so a line-ending or attribute filter in the clone cannot change a file on the way; a mismatch refuses. The tool runs git with `core.autocrlf=false` for the same reason.
- Untracked files under `public/` count as uncommitted changes and refuse (the card's "what crosses is what git holds"); files ignored by `.gitignore` there do not.
- The first send replaces whatever `foundry-north-site` already holds (a README made with the repository, say) with `public/` alone, as the card asks ("nothing else").
- `SENT:` and `NOTHING TO SEND` carry a few words after them (the short commits and the repository); the commit message carries the full project commit.

## Parked
- `C:\Users\3070s\AppData\Local\Temp\pytest-of-3070s` denies this user access (`icacls`: Access is denied), so every `tmp_path` test in this project errors on this machine unless `--basetemp` is given. Not this card's folder; not touched.

## Drift
none

## Refused
none

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: 413c0610a4a2a68822911ff4fa479a2fb04efa0e
Exit code: 0
Verdict: PASS
Why: Gate as written (`python3.11 -B -m pytest tools/tests/test_send_site.py -q`) errors on this machine before any test runs (8 errors, `PermissionError` on the shared `pytest-of-3070s` temp folder, as the worker said). Re-run in my own process with `-p no:cacheprovider --basetemp C:/Users/3070s/AppData/Local/Temp/fnw-send-site-checker/base`: `8 passed in 13.60s`, exit 0; worktree status clean after. Ablation in a scratch copy (`ls-tree` without `-- PUBLIC`, paths unstripped): `3 failed, 5 passed` — `test_sends_only_the_public_folder` (the tree-equals test), `test_a_file_removed_from_public_is_removed_from_the_site`, `test_dry_run_says_what_would_cross_and_pushes_nothing` (listed `tools/secret_plan.py` crossing); the worktree was not touched. Goal points 1-5 read against the diff: clone/stage/commit naming the project commit/push of `main`, `SENT:` / `NOTHING TO SEND` (1); `REFUSE:` exit 1 for a symbolic link, uncommitted changes (edit, new file, removal, untracked) and an extra or differing file in the staged clone, each refusal test also checking the remote unchanged (2); `--dry-run` pushes nothing, tested (3); contract § What it hands the rest says the two required things (4); standard library and git only, comment head in the style of the other tools (5). Every test uses a local bare repository under `tmp_path`; nothing touches the real remote. Fence: `INSIDE: all 4 changed file(s) are in the card's Touches (against main).` No CR in the three tracked files. Scope question — is anything in this diff not asked for by the card? One small thing, yes, already declared in the worker's Unsure: the refusal `git holds nothing under desks/site/public/ at HEAD` (two lines in `public_files()`; no test depends on it). It is a safety guard that stops an empty send wiping the site, not something the card listed; the master may keep it or strip it. The blob-id comparison in `stage()` and `core.autocrlf=false` serve the card's "exactly the files git holds" and are not extra. Nothing else unasked. Not run: any send or dry run against the real `foundry-north-site`.
