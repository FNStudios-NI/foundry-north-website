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
