# Contract — site

What this desk hands the rest of the project. Other desks build against it, so changing it is an ask to the master, never an experiment.
Why: the desks share one repo, and this file is the seam between them.

## What it hands the rest
- **The site: `desks/site/public/`.** The website's files, at the top of that folder as the site serves them. It is the only part of this project that may be public.
- **The way across: `tools/send_site.py`.** The only way the site crosses to `foundry-north-site`, its own repository, which Cloudflare publishes. It sends what git holds in `desks/site/public/` at `HEAD` and nothing else, and refuses a symbolic link or an uncommitted change in that folder. Stand-in for tests: a local bare repository, given with `--repo`.
