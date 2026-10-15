# live-check — site — 2026-10-15
Lane: standard · an Opus worker, a Sonnet checker, then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: tool
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-live-check` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 06:20` · run 1, piece 6

## Goal
When done:
1. `tools/live_check.py` reads the live site and the domain's other answers, and prints one line per check, `PASS <check> · <what it read>` or `FAIL <check> · <what it read> · expected <what>`, then `LIVE: PASS` (exit 0) or `LIVE: FAIL <n>` (exit 1). Its checks:
   - `https://foundrynorthstudios.co.uk/` and `https://www.foundrynorthstudios.co.uk/` each answer 200 with the page (the body holds "Foundry North" and `id="contact"`); a redirect from one to the other, ending in 200 with the page, passes.
   - The link preview reads: the page's `og:title`, `og:description` and `og:image` are there, and the `og:image` address answers 200 with an image type.
   - The mail and the untouched names match the readings of 14 Oct (`docs/brief.md` § Facts): MX is `mx.zoho.eu` (10), `mx2.zoho.eu` (20), `mx3.zoho.eu` (50); the SPF text is `v=spf1 include:zoho.eu include:_spf-eu.ionos.com ~all`; `https://portal.foundrynorthstudios.co.uk/` answers 200; `https://pick.foundrynorthstudios.co.uk/` answers 404.
2. DNS is read over DNS-over-HTTPS from Cloudflare (`https://cloudflare-dns.com/dns-query`, JSON, `accept: application/dns-json`), so the tool needs no non-standard library and no `nslookup`. Python 3 standard library only. `--base <url>` points the page checks at another address (for the tests and for the preview).
3. A comment head in the tools' own style (what it is for, why, how to run it).
Must merge first: none. Inputs: `docs/brief.md` § Facts at main `1ea362c`.

## Gate — run it; done means this passes
`python -B -m pytest tools/tests/test_live_check.py -q` → `<n> passed`, n ≥ 6, with no network: the tests serve a small page from a local `http.server` on 127.0.0.1 (pass; a missing `og:image` fails; a 500 fails) and feed the DNS checks recorded answers through a stub of the tool's one fetch function (the 14 Oct answers pass; a changed MX fails; a changed SPF fails). Its `conftest`-style guard, inside the test file, fails any connection that is not to 127.0.0.1.
Also, once, by hand, with the network: `python tools/live_check.py` → today it prints FAIL for the two page checks (the site is not live; today's answer is Cloudflare's 525) and PASS for MX, SPF, `portal.` and `pick.`; paste its output in the receipt.
Ablation: make the MX check compare nothing (always pass) and the changed-MX test fails: at least 1.
Forbidden: a change outside Touches; any write to DNS or Cloudflare; a secret.
Scratch (worker and checker alike): `C:\Users\3070s\AppData\Local\Temp\fnw-live-check-worker` · `C:\Users\3070s\AppData\Local\Temp\fnw-live-check-checker`; each is named in its receipt and removed by that exact name only, never a pattern.

## Touches
`tools/live_check.py` · `tools/tests/test_live_check.py` · `desks/site/docs/cards/receipts/2026-10-15-live-check-close.md`

## Read first
`desks/site/CLAUDE.md` · `docs/brief.md` § Facts · `tools/land.py` (the house style of a tool's head comment) · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 40 minutes of work, about 1 minute of Rhys's try (the result, at K5). Hard stop at 60 turns.
