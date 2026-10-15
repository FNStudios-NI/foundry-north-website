DONE — his going-live act file is written: Pages from GitHub, the pages.dev check, both custom domains, the four-row fallback, CAA, undo and sources

# Receipt — going-live-act — 2026-10-15

Card: `desks/site/docs/cards/2026-10-15-going-live-act.md` · Branch: `task/foundry-north-website/2026-10-15-going-live-act` · Worker: Opus 5.5 in `C:\Users\3070s\.t3\worktrees\foundry-north-website\task-foundry-north-website-2026-10-15-going-live-act`

## Shipped
- `docs/operator-acts/2026-10-15-going-live.txt` (new, CRLF like the blank and the key act): copied from `docs/blanks/act-file.txt`; about 20 to 30 minutes and "no step needs a terminal" at the top; the 06:40 facts (the four IONOS rows by value, MX and SPF DNS only, no Pages project).
- STEP 1 to 6: Workers & Pages, Create application, Pages, Import an existing Git repository; GitHub app on "Only select repositories", foundry-north-site only; branch `main`, preset None, build command empty, output `/`; Save and Deploy; the pages.dev address shows "Foundry North" and the tagline.
- STEP 7 to 9: Custom domains, Set up a domain, `www.foundrynorthstudios.co.uk` then the bare address; Pass is "Active" and both addresses show the page. What the docs say about existing A/AAAA rows (nothing) is written with its link.
- STEP 10 to 12, the fallback: a CAA check first (stop and tell the master, change nothing), then delete only the four named rows, with a plain "Never touch the MX rows, the TXT rows, portal, pick or anything else", then remove and re-add the domain.
- STEP 13 to 15, the undo (CNAME rows, then Remove domain, then the four rows back, proxied), and a Sources section: six developers.cloudflare.com pages, each read 15 Oct 2026, with the steps that rest on each.

## Test it
At c3a9c6a, from the worktree's top folder, the card's gate saved as `C:\Users\3070s\AppData\Local\Temp\fnw-going-live-worker\gate_act.py`:
- `python3.11 C:/Users/3070s/AppData/Local/Temp/fnw-going-live-worker/gate_act.py` → `GATE PASS`, exit 0. The file has 15 `STEP` lines and 15 `Pass:` lines.
- Ablation: the file copied to `...\fnw-going-live-worker\abl\docs\operator-acts\` with STEP 6's Pass line removed; the gate run from `...\abl` → `GATE FAIL` / `a step without its Pass line`, exit 1.
- `git diff --stat $(git merge-base main HEAD)..HEAD` → only `docs/operator-acts/2026-10-15-going-live.txt | 202 +++`; carriage returns 202 for 202 lines (CRLF throughout).
- Docs read as markdown (`.../index.md`) on 15 Oct 2026 about 06:41: custom-domains (last updated Apr 21, 2026), get-started/git-integration, framework-guides/deploy-anything, git-integration/github-integration, debugging-pages, dns/.../create-dns-records; also `ssl/faq` (CAA section), which the file does not cite. A web search turned up no Cloudflare page that says what happens to existing A/AAAA rows when a Pages custom domain is added.

## Unsure
- **Existing A/AAAA rows:** the Custom domains page does not say whether Cloudflare replaces them, asks to replace them, or refuses, and links no page that does. So STEP 7 and 8 tell him: if a message talks of an existing record, or offers to replace records, press Cancel, write down its words, and use the fallback (delete the four rows himself). The master may prefer that he accept a replace offer if Cloudflare makes one. A forum answer (not Cloudflare's docs) quotes the error "An A, AAAA, CNAME record already exists with that host. (Code: 81053)"; I left it out because the card asks for the docs.
- The fallback and the undo are numbered STEP 10 to 15, not given their own labels, because with their own labels the extra Pass lines meant the card's ablation (remove one step's Pass line) still passed. The headings "IF A DOMAIN WILL NOT GO ACTIVE" and "UNDO" say they are conditional, and STEP 9's Pass ends "You are done: the steps below are only for trouble or undoing".
- Button names the docs do not give, written from the docs' own wording: the confirm press in STEP 7 is "press its confirm button" (the docs say only "after you confirm your DNS record"); Framework preset "None" (the docs say leave it blank or skip); `@` for the bare name in STEP 15 (not on the DNS page I read). A pages.dev address "most likely https://foundry-north-site.pages.dev": the docs say the project name makes the hostname, but not its exact form.
- STEP 4 says: if the Production branch list is empty, stop (the files have not reached the repository yet). The docs say a branch must have been pushed before one can be picked. This one line is a guard the card did not spell out.
- Deploy-anything recommends `exit 0` as the build command; the card and the Git integration page say leave it empty. I followed the card.
- The 15-minute wait before the fallback comes from Debugging Pages ("still verifying after 15 minutes").

## Parked
- The brief's § Facts line on going live (line 80) still marks "whether Pages accepts the bare address over today's proxied A records" as unknown; this act file cannot settle it, and only his K4 act will.

## Drift
none

## Refused
none

## Fix 2026-10-15
Same worker, on the inspector's three parked lines (check PASS at 97b94fc); the old `Checker run` block is removed for a fresh checker.
- STEP 12: delete the stuck name's pages.dev CNAME row first (if there is one), then "Remove domain", the order the Custom domains page gives and STEP 13 already uses.
- STEP 10: adds the other cause Debugging Pages names for a domain stuck at "Verifying": Cloudflare Access, a redirect or a Worker in the way of the HTTP check, with the same "stop, change nothing, tell me".
- Near the top: the Pages project goes in the same Cloudflare account that holds foundrynorthstudios.co.uk (Custom domains page). Sources lines updated to name these uses.
- At 7eac95f, from the worktree's top: the card's gate (cut from the card into `C:\Users\3070s\AppData\Local\Temp\fnw-going-live-worker\gate_act.py`) → `GATE PASS`, exit 0; 15 `STEP` and 15 `Pass:` lines. Ablation (a copy in `...\fnw-going-live-worker\abl` with STEP 10's Pass line removed) → `GATE FAIL` / `a step without its Pass line`, exit 1. CRLF kept: 208 carriage returns for 208 lines.
- Unsure: the menu names "Rules" and "Workers Routes" in STEP 10 are where I expect a redirect and a Worker route to show in the dashboard; the docs I read name the causes, not those menus. Access has no place to look in the zone, so STEP 10 asks only whether he knows he set it up.

## Checker run 2026-10-15 — Sonnet 5.5 checker (fix check), own session
Commit: e69bddc80e47dfe0352d7503b4267600eb926d3e
Exit code: 0
Verdict: PASS
Why: Fresh checker in the worktree; seat claimed (ALLOW, seat 2 of 4). Gate cut from the card into `C:\Users\3070s\AppData\Local\Temp\fnw-going-live-checker2\gate_act.py`, run from the worktree top at e69bddc → `GATE PASS`, exit 0. Ablation in `...\fnw-going-live-checker2\abl` (a copy with STEP 10's Pass line removed) → `GATE FAIL` / `a step without its Pass line`, exit 1. `python3.11 tools/fence_check.py --card desks/site/docs/cards/2026-10-15-going-live-act.md` → `INSIDE: all 2 changed file(s) are in the card's Touches (against main).` (exit 0). The act file is 208 lines with 208 carriage returns (CRLF kept). Nothing was written to Cloudflare, DNS or GitHub; the key file was not read. Diff read whole (`git diff 97b94fc..HEAD`: the act file, plus this receipt's old Checker run block replaced by the worker's Fix section). I opened the Custom domains and Debugging Pages docs (WebFetch) on 15 Oct 2026.
The three fixes:
- STEP 12 order: in. Custom domains says to delete the project's CNAME record first (Edit, Delete) and then "three dot icon > Remove domain". STEP 12 now says exactly that, limited to the one CNAME row whose Content is the pages.dev address, "and nothing else", then Remove domain, then re-add. Matches STEP 13's order. Correct.
- Blocked validation: in, in STEP 10 (the Why, the look under "Rules" and "Workers Routes", the Pass line, and the stop line, "stop. Do not change it or delete it. Tell me"). Debugging Pages says: "If another Cloudflare product is in the way (such as Access, a redirect, a Worker, etc.), validation cannot be completed." Matches. The docs' own fix (disable Access until verified) is not given to him, correctly: the card wants stop, change nothing, tell me. The menu names "Rules" and "Workers Routes" are the worker's own (disclosed in Unsure; not in the docs), so they may differ on his screen; if he finds nothing he is still sent on to STEP 11, which only touches the four named rows, so a missed menu cannot cause damage. Not a FAIL.
- Same account: in, near the top. Custom domains says: "that custom domain must be a zone on the Cloudflare account you have created your Pages project on." The doc states it for an apex domain; the act says "the address", which is a little wider (www is the same zone anyway) and harmless. Correct. Sources lines updated to name these uses (Custom domains: the same-account line; Debugging Pages: blocked validation; Create DNS records: STEP 12), accurate.
The fallback still names only the four A/AAAA rows (A and AAAA, bare and www, 217.160.0.70 and 2001:8d8:100f:f000::25b) in STEP 11. MX, TXT, portal and pick are named only in "Never touch" lines and in the Pass lines that check they remain. STEP 12's new delete is of one CNAME row whose Content is the pages.dev address, not any of the protected rows; STEP 13 likewise.
Is anything in this diff not asked for by the card or the fix? No. The diff to the act file is the three fixes and the matching Sources lines. The receipt change (old Checker run block removed, Fix section added) is the worker's own, as the master asked for a fresh checker; both files are in Touches (fence INSIDE). I do not require removal.
Reasoning: nothing in the act file differs from the cited docs in a way that would mislead him; the only soft spots are the worker's disclosed dashboard menu names.