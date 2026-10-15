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

## Fix 2026-10-15
The master's first real send refused: `REFUSE: commit failed — Author identity unknown … unable to auto-detect email address`. Pandora has no global git identity, and the scratch clone does not inherit the project checkout's local one.
- `tools/send_site.py`: reads `user.name` and `user.email` from the project checkout (`git config`, so its local identity, or a global one where there is one) before cloning, and makes the site's commit with them (`git -c user.name=… -c user.email=… commit`). With either missing it refuses before cloning: `REFUSE: this checkout has no git user.name; set it here (git config user.name ...) so the site's commit has an author`. The head comment says so.
- `tools/tests/test_send_site.py`: one new test, `test_the_site_commit_takes_the_checkouts_own_identity_and_refuses_without_one`, with `HOME` and `GIT_CONFIG_GLOBAL` pointed at an empty file and `GIT_CONFIG_NOSYSTEM=1`: with no identity it refuses and the remote is unchanged; with a local identity it sends, and the site's commit carries that identity as author and committer. The fixture now gives each test project a local identity in place of the `GIT_AUTHOR_*` / `GIT_COMMITTER_*` variables, so every sending test runs as Pandora does.
- The gate now runs as written: the test file overrides `tmp_path` with a folder of its own (`tempfile.mkdtemp(prefix="test-send-site-")`, removed by its exact name after each test), so pytest's shared `pytest-of-3070s` is never opened. No machine setting changed. The Parked line above still holds for the project's other tests.

Gate, as the card writes it, at `6c6316d59efd1e530d547d852134b71d67bd4acd`: `python3.11 -B -m pytest tools/tests/test_send_site.py -q` →
```
.........                                                                [100%]
9 passed in 16.41s
```
No `test-send-site-*` folder left in Temp after it. Red before the fix (the old `tools/send_site.py` from `HEAD`, the new tests): `8 failed, 1 passed in 8.08s` — every test that commits fails as the master's send did; the dry-run test alone passes. Branch brought up to main (`0565318`) first, no conflicts.
Scratch: `C:/Users/3070s/AppData/Local/Temp/fnw-send-site-worker` (the fixed tool kept there during the red run), removed by that exact name.
Not run: any send or dry run against the real `foundry-north-site`.
