# Register — foundry-north-website

Every secret this project uses: its name and where it lives, never its value. Why: a pointer is safe in git; a value is a leak.
Read the end dates before any long run. Why: a seven-day sign-in once expired in the middle of a run, and a lapsed sign-in failed 122 takes before this register existed.

| secret (its name, never its value) | machine | pointer (where it lives) | door (the one tool that uses it, and its one job) | who renews it | ends on |
|---|---|---|---|---|---|
| Cloudflare API token "foundry-north-website master" (Zone Read, DNS Read, Cloudflare Pages Edit; zone foundrynorthstudios.co.uk only) | Pandora | `C:\Users\3070s\.foundry-north-website\cloudflare-token.txt`, outside the project | the master's reads of the zone's records and its Pages set-up (his letter 4a, 15 Oct 2026) | Rhys | none set; he deletes it in Cloudflare's API Tokens page |

## People

Every third person this project touches, by role only ("the user"). Their name, health, employer and history live in a text file outside the project, one word or phrase per line, and the pointer below names that file. Why: a project that will ever be shared must never hold a person's details; `tools/people_check.py` reads these files and refuses any page that holds one.

| role | pointer to their details, outside the project | ends on |
|---|---|---|
| his private business facts (client counts, revenue, the trial and first client runs: the digest's Private lines), which never go on the public site | `C:\Users\3070s\.foundry-north-website\private-words.txt` | none |
