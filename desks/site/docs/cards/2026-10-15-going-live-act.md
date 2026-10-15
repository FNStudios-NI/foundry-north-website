# going-live-act — site — 2026-10-15
Lane: standard · an Opus worker, a Sonnet checker (the inspector), then the scripts (the gate passes, fence INSIDE)

Desk: `desks/site/`
Kind: document
Heavy: no
Branch: `task/foundry-north-website/2026-10-15-going-live-act` · Worktree: the T3 worktree made for this branch at launch · Order: asks entry `2026-10-15 06:20` · run 1, piece 5

## Goal
When done:
1. `docs/operator-acts/2026-10-15-going-live.txt`, copied from `docs/blanks/act-file.txt`, takes Rhys through going live in the Cloudflare dashboard (a web browser on his laptop or Pandora; he is signed in to Cloudflare and GitHub there), one step each with its Why and its Pass line (the exact words or sight he should see):
   a. Create a Pages project by connecting Git: give Cloudflare's GitHub app access to the private repository `FNStudios-NI/foundry-north-site` only; production branch `main`; no framework, no build command, build output folder `/` (the repository's top holds `index.html`).
   b. Pass: the project's `<name>.pages.dev` address shows the page (he checks the name "Foundry North" and the tagline).
   c. Add the custom domain `www.foundrynorthstudios.co.uk`, then the bare `foundrynorthstudios.co.uk`, in the project's Custom domains tab.
   d. Pass: each domain reads Active, and both addresses show the page.
2. The facts it rests on (read through his Cloudflare key at 06:40 today, `docs/decisions.md`, the 03:48 entry's last line): the zone is on Cloudflare and active; the bare address and `www` each hold an A row `217.160.0.70` and an AAAA row `2001:8d8:100f:f000::25b`, proxied (IONOS, the old host behind today's error 525); MX (three Zoho rows) and the SPF TXT are DNS only; no Pages project exists yet.
3. What Cloudflare does when a custom domain is added over a name that already has A/AAAA rows is read from Cloudflare's current documentation (developers.cloudflare.com, Pages › Custom domains, and any page it links on existing records) and written in the file with its link. If the docs say Cloudflare replaces or asks to replace them, the step says what he will see and what to press. The fallback, for when the domain will not go Active because of those rows: delete only these four rows, by name and value: A `foundrynorthstudios.co.uk` 217.160.0.70, AAAA `foundrynorthstudios.co.uk` 2001:8d8:100f:f000::25b, A `www` 217.160.0.70, AAAA `www` 2001:8d8:100f:f000::25b; then retry the step. It says plainly: never touch the MX rows, the TXT rows, `portal`, `pick` or anything else. It also covers CAA rows (the docs warn they can block the certificate): what he sees if one blocks, and to stop and tell the master, not to change it.
4. Its undo, as a last section: how to remove the custom domains (the page goes back to the error) and re-add the four rows with their values, in that order.
5. A "Sources" section at the end: each Cloudflare documentation page used, with its address and the date read, and which step rests on it.
6. Plain words, for his phone or laptop: no step needs a terminal; about 20 to 30 minutes in total, said at the top.
Not in this card: doing any of it (his act, K4); any API call that writes. Reading the docs on the web is allowed; nothing is sent.
Must merge first: none. Inputs: `docs/decisions.md` at main (the 03:48 entry's last line); `docs/brief.md` § Facts.

## Gate — run it; done means this passes
Save as `gate_act.py` in your scratch folder; from the worktree's top folder: `python <scratch>/gate_act.py` → `GATE PASS` (exit 0).

```python
import re, sys
t = open("docs/operator-acts/2026-10-15-going-live.txt", encoding="utf-8").read()
fails = []
steps = re.findall(r"^STEP \d+", t, re.M)
passes = re.findall(r"^Pass:", t, re.M)
if len(steps) < 4: fails.append("fewer than 4 steps")
if len(passes) < len(steps): fails.append("a step without its Pass line")
for need in ("foundry-north-site", "217.160.0.70", "2001:8d8:100f:f000::25b", "pages.dev", "www.foundrynorthstudios.co.uk", "CAA", "developers.cloudflare.com", "Sources"):
    if need not in t: fails.append("missing: " + need)
if not re.search(r"never touch[^\n]*MX", t, re.I): fails.append("no plain 'never touch ... MX' line")
if re.search(r"(delete|remove)[^\n]*\b(MX|TXT|portal|pick)\b", t, re.I) and not re.search(r"never", t, re.I): fails.append("a delete of MX/TXT/portal/pick")
if "<" in t and re.search(r"<[A-Za-z ]+>", t): fails.append("a blank's <placeholder> left in")
print("GATE PASS" if not fails else "GATE FAIL\n" + "\n".join(fails)); sys.exit(1 if fails else 0)
```
Ablation: remove the Pass line of one step (in scratch) and the gate fails.
The inspector (the checker) also opens each source address in the Sources section and checks each step against it, and says per step: matches · differs (how) · not covered by the docs.
Forbidden: a change outside Touches; any write to Cloudflare, DNS or GitHub; the key's value anywhere (`C:\Users\3070s\.foundry-north-website\cloudflare-token.txt` is not read by this card at all); a push to `main`.
Scratch (worker and checker alike): `C:\Users\3070s\AppData\Local\Temp\fnw-going-live-worker` · `C:\Users\3070s\AppData\Local\Temp\fnw-going-live-checker`; each is named in its receipt and removed by that exact name only, never a pattern.

## Touches
`docs/operator-acts/2026-10-15-going-live.txt` · `desks/site/docs/cards/receipts/2026-10-15-going-live-act-close.md`

## Read first
`desks/site/CLAUDE.md` · `docs/blanks/act-file.txt` · `docs/operator-acts/2026-10-15-cloudflare-key.txt` (an act file he has used) · `docs/brief.md` § Facts · `operator.md` · `worker-rules.md`

## Refusals
`worker-rules.md` § Refusals — stop that act, write `Refused:` in the receipt, carry on.

## Budget
About 40 minutes of work, about 20 to 30 minutes of Rhys's (at K4). Hard stop at 60 turns.
