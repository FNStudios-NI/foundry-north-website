DONE — `tools/live_check.py` reads the page, the link preview, the mail and the untouched names, and says PASS or FAIL for each

# Receipt — live-check — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-live-check.md` · Branch: `task/foundry-north-website/2026-10-15-live-check` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-live-check`

## Shipped
- `tools/live_check.py`: the bare address and `www.` (200 with "Foundry North" and `id="contact"`, redirects followed), the link preview (`og:title`, `og:description`, `og:image`, the image 200 with an `image/` type), MX and SPF against the 14 Oct readings, `portal.` 200 and `pick.` 404; one `PASS`/`FAIL` line each, then `LIVE: PASS` (exit 0) or `LIVE: FAIL <n>` (exit 1).
- DNS read over DNS-over-HTTPS from `https://cloudflare-dns.com/dns-query` (JSON, `accept: application/dns-json`) through `fetch`, the tool's one network function; standard library only; `--base <url>` points the page checks at another address. A head comment in `land.py`'s style.
- `tools/tests/test_live_check.py`: 8 tests, no network: a local `http.server` on 127.0.0.1 (good page passes, missing `og:image` fails, 500 fails), recorded DoH answers through a stub of `fetch` (14 Oct answers pass, changed MX fails, changed SPF fails), and two runs of `main` (all PASS lines and exit 0; a failing run counts `LIVE: FAIL 3`, exit 1). An autouse guard in the file fails any connection or name lookup not to 127.0.0.1.

## Test it
At `0d257d8`, from the worktree's top folder.

`python3.11 -B -m pytest tools/tests/test_live_check.py -q`
```
........                                                                 [100%]
8 passed in 2.67s
```

Ablation: the MX check's `found == MX` replaced by `True` (always pass), same command:
```
FAILED tools/tests/test_live_check.py::test_changed_mx_fails - AssertionError...
1 failed, 7 passed in 2.74s
```
then `git checkout -- tools/live_check.py`, and the gate read `8 passed` again.

The guard was shown to bite once: a throwaway test calling `live_check.fetch("https://1.1.1.1/")` failed with `AssertionError: network lookup in a test: 1.1.1.1`; the test was then removed from the file.

The one networked run, by hand, 2026-10-15 about 05:30 UTC: `python3.11 tools/live_check.py`
```
FAIL page https://foundrynorthstudios.co.uk/ · 525 from https://foundrynorthstudios.co.uk/ · expected 200 with the page ("Foundry North" and id="contact")
FAIL page https://www.foundrynorthstudios.co.uk/ · 525 from https://www.foundrynorthstudios.co.uk/ · expected 200 with the page ("Foundry North" and id="contact")
FAIL preview · no page to read · expected og:title, og:description and og:image, the image 200 with an image type
PASS mx · mx.zoho.eu (10), mx2.zoho.eu (20), mx3.zoho.eu (50)
PASS spf · v=spf1 include:zoho.eu include:_spf-eu.ionos.com ~all
PASS portal. · 200 from https://portal.foundrynorthstudios.co.uk/
PASS pick. · 404 from https://pick.foundrynorthstudios.co.uk/
LIVE: FAIL 3
```
exit 1. (Before writing the tool, the real DoH answers were read once with `curl` to copy their shape into the tests' recorded answers.)

## Unsure
- The card says today prints FAIL for "the two page checks"; the preview check fails too (there is no page to read), so today's count is `LIVE: FAIL 3`, not 2.
- With `--base`, the page checks read that one address only (not `www.` beside it), and the preview reads the first page that answered 200 with the page.
- The tool prints in UTF-8 (`sys.stdout.reconfigure`, as `flag.py` and `record.py` do), so the `·` reads right when its output is piped; without it, a pipe in Git Bash showed `�`.
- The tool sends `User-Agent: foundry-north-live-check/1`; a Cloudflare bot rule after going live could treat it differently from a browser.

## Parked
- In the guard check I copied the test file once to `C:\Users\3070s\AppData\Local\Temp\x.py` (Git Bash's `/tmp`), outside my scratch folder. It holds only the test file's text, no secret. It is not deleted: deleting outside my worktree and scratch is a refusal, so its removal is the master's or Rhys's call.

## Drift
- One file written outside the card's Touches and outside the repository: `C:\Users\3070s\AppData\Local\Temp\x.py`, a stray copy of the test file (see Parked). Nothing else; the scratch folder `C:\Users\3070s\AppData\Local\Temp\fnw-live-check-worker` was never made.

## Refused
none.

## Checker run 2026-10-15 — Sonnet 5.5 checker, own session
Commit: ff62adcd4258acedeb0b8baba9dc7a25f02dc70a
Exit code: 0
Verdict: PASS
Why: Run by me at the commit above, from the worktree (plain pytest, no PermissionError, so no basetemp needed).
- Gate `python3.11 -B -m pytest tools/tests/test_live_check.py -q` → `8 passed in 2.63s`, exit 0 (card asks n ≥ 6).
- The one networked run, `python3.11 tools/live_check.py`, 2026-10-15 06:32 UTC, exit 1: `FAIL page https://foundrynorthstudios.co.uk/ · 525 …`, `FAIL page https://www.foundrynorthstudios.co.uk/ · 525 …`, `FAIL preview · no page to read …`, `PASS mx · mx.zoho.eu (10), mx2.zoho.eu (20), mx3.zoho.eu (50)`, `PASS spf · v=spf1 include:zoho.eu include:_spf-eu.ionos.com ~all`, `PASS portal. · 200 …`, `PASS pick. · 404 …`, `LIVE: FAIL 3`. This matches the card (two page checks FAIL; MX, SPF, portal, pick PASS); the third FAIL is the preview, which has no page to read, as the worker flagged under Unsure.
- Ablation, in a scratch copy (`C:\Users\3070s\AppData\Local\Temp\fnw-live-check-checker`, nothing left in the worktree): `found == MX` replaced by `True` → `FAILED tools/tests/test_live_check.py::test_changed_mx_fails`, `1 failed, 7 passed`. Red as the card requires.
- Guard: in the scratch copy I added a test that `live_check.fetch('https://1.1.1.1/')` and `socket.create_connection(('8.8.8.8', 53))` each raise `AssertionError`; `9 passed`, so the guard blocks non-127.0.0.1 connections (and name lookups). The local-server tests pass under it.
- Fence: `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-live-check.md` → `INSIDE: all 3 changed file(s) are in the card's Touches (against main).`
- Diff read whole (3 files: the tool, its tests, the receipt). Scope question, *is anything in this diff not asked for by the card?* — No. Every asked item is there: the page checks with redirect-following, the preview, MX/SPF/portal/pick, `PASS`/`FAIL` lines with `LIVE:` summary and exit codes, DoH from Cloudflare with `accept: application/dns-json`, stdlib only, `--base`, a head comment. Small extras are within the tool's own function and are declared under Unsure (the `User-Agent` header, the UTF-8 stdout reconfigure as in `flag.py`); the two `main` tests go past the six the card named but only exercise the card's output format. No DNS or Cloudflare write, no secret.
- Notes, not failures: (1) `tools/live_check.py` is CRLF like its sibling tools, but `tools/tests/test_live_check.py` is LF while the sibling tests are CRLF (a new file, so no diff noise). (2) The worker's stray `C:\Users\3070s\AppData\Local\Temp\x.py` (see Parked/Drift) still exists; I did not touch it, as it is not mine to delete. (3) The main checkout's status was clean.
