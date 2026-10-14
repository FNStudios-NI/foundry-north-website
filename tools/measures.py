# measures.py: the review's numbers for one run.
#
# What it is for
#   At the review, the master runs this on a run's folder and it prints
#   four measures under four headings: It works, Usage per finished piece,
#   Share finished, Surprises. It only reads. It never writes to the run
#   record or the session logs, and it never touches the internet.
#
# What it reads
#   - docs/runs/<n>/run.md, the run record:
#       its title "# Run <n> — foundry-north-website" for the project's name;
#       "## Go", the line "- Start: <yyyy-mm-dd hh:mm>", where the logs begin;
#       "## Merges", one line per card landed, as land writes it
#         ("- <hh:mm> · <yyyy-mm-dd>-<card> · ...") or as 0.4.0's were written
#         by hand ("- <hh:mm> · <desk> <card> · ...");
#       "## It works", one line per card tried, written by the review master
#         with record.py ("- <hh:mm> · <card> · pass | fail · <how it was tried>");
#       "## Unforeseen key points" and "## Blockers", the surprises.
#   - docs/runs/<n>/plan-signed.md: the lines under "## The path". A number
#     opening a line, or opening a clause after ": " or "· ", is a piece, counted
#     once however the lines group them ("- Round 1: 1 land · 2 the forms",
#     "- 1 · the usage counter · template"); with no numbers, each line is one
#     piece ("- <task> · <desk>").
#   - docs/decisions*.md at the project's top, the archive files too: the
#     heading "## <yyyy-mm-dd hh:mm> — Run <n> closed", where a closed run's
#     logs end.
#   - Each landed card's own file, <yyyy-mm-dd>-<card>.md in
#     desks/<desk>/docs/cards/ or docs/cards/: the words "piece <n>" on its
#     "Order:" line, the piece of the plan the card landed. A piece counts
#     once however many cards it was cut into. A card that names no piece of
#     the plan, or whose one file is not found, is named and left out.
#   - The session logs, Claude Code's *.jsonl files under --logs (by default
#     ~/.claude/projects/), between the run's Start and its close, or now for
#     a run not closed, or --until. Only the tokens of replies stamped inside
#     that time are counted.
#
# How a session's tokens are shared out
#   A session belongs to a landed card when its branch, its folder, or its
#   first message names the card's branch (task/foundry-north-website/<date>-<card>) or
#   worktree (task-foundry-north-website-<date>-<card>), the desk's name allowed before
#   the card's (task-foundry-north-website-<date>-road-<card>); a card land wrote with its
#   date (<yyyy-mm-dd>-<card>) is that date's branch and worktree only
#   (task/foundry-north-website/<yyyy-mm-dd>-<card>): that holds the card's worker
#   and its checker, which is told the branch in its orders. Of the rest of
#   the project's sessions (a folder named foundry-north-website in the session's
#   working folder), a conductor's first message calls /conductor; a
#   master's calls /run or /hephcofounder or starts "You are <name>-master";
#   anything else is "the rest". Each share is of the run's total.
#   Tokens are weighted as the 8 Oct reading of run 2 weighed them: input
#   + cache writes x 1.25 + cache reads x 0.1 + output x 5, each reply once.
#
# Why the tool exists
#   Run 2's measures never happened, and its usage split was read on 8 Oct
#   by a throwaway script (design 2026-10-08 § 1 and § 9; his ruling 8 of
#   06:03). Enjoyment and his own time are never measured here (ruling 8):
#   enjoyment is his tap on the review page.
#
# How to run it
#   python template/tools/measures.py docs/runs/<n> [--logs <folder>] [--until "yyyy-mm-dd hh:mm"]
#   Times are the run record's: this machine's clock.
#
# Python 3 standard library only.

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

HEADING = re.compile(r"^##\s+(.*?)\s*$")
TITLE = re.compile(r"^#\s+Run\s+\S+\s+[—-]+\s+(\S+)")
START = re.compile(r"^\s*-\s*Start:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
SLUG = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
VERDICT = re.compile(r"^(pass|fail)$", re.IGNORECASE)
DATED = re.compile(r"^\d{4}-\d{2}-\d{2}-")
PIECE = re.compile(r"(?:^- |: |· )(\d+)(?=\s|$)")
# A heading in decisions.md that closes a run, as where_am_i.py reads it.
CLOSED = re.compile(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*\bRun (\d+) closed\b", re.IGNORECASE)
ORDER = re.compile(r"\bOrder:(.*)")
NAMED = re.compile(r"\bpiece (\d+)\b")
DATE_GLOB = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-"


def sections(text):
    """Map each "## " heading of a page to its lines."""
    out, name = {}, None
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            name = m.group(1)
            out.setdefault(name, [])
        elif name is not None:
            out[name].append(line)
    return out


def bullets(lines):
    return [line.strip() for line in lines if line.strip().startswith("- ")]


def fields(line):
    return [f.strip() for f in line[2:].split("·")]


def pieces(lines):
    """The plan's pieces, by number: each number opening a line or a clause
    after ': ' or '· ' once; with no numbers, one per line, counted from 1."""
    path = bullets(lines)
    numbers = {int(n) for line in path for n in PIECE.findall(line)}
    return numbers or set(range(1, len(path) + 1))


def card_of(text):
    """'template wrap-resume (amended, ...)' -> ('template', 'wrap-resume');
    'wrap-resume' -> ('', 'wrap-resume'); anything else -> None."""
    words = re.sub(r"\([^)]*\)", " ", text).split()
    if len(words) == 1 and SLUG.match(words[0]):
        return "", words[0]
    if len(words) == 2 and all(SLUG.match(w) for w in words):
        return words[0], words[1]
    return None


def local_time(text):
    return dt.datetime.strptime(text, "%Y-%m-%d %H:%M").astimezone()


def closed_at(root, run):
    """The time in the heading of the run's 'Run <n> closed' entry in
    docs/decisions*.md, the earliest if it is there twice; None if not closed."""
    times = []
    for path in glob.glob(os.path.join(glob.escape(root), "docs", "decisions*.md")):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = CLOSED.match(line)
                if m and run.isdigit() and int(m.group(2)) == int(run):
                    try:
                        times.append(local_time(m.group(1)))
                    except ValueError:
                        continue
    return min(times) if times else None


def named_pieces(root, desk, card):
    """The pieces a landed card names: each 'piece <n>' on the 'Order:' line
    of its own file. Empty when it names none, or when no one file is found."""
    name = (glob.escape(card) if DATED.match(card) else DATE_GLOB + glob.escape(card)) + ".md"
    top = glob.escape(root)
    found = glob.glob(os.path.join(top, "desks", glob.escape(desk) if desk else "*", "docs", "cards", name)) \
        + glob.glob(os.path.join(top, "docs", "cards", name))
    if len(found) != 1:
        return set()
    with open(found[0], encoding="utf-8", errors="replace") as f:
        for line in f:
            m = ORDER.search(line)
            if m:
                return {int(n) for n in NAMED.findall(m.group(1))}
    return set()


def read_log(path):
    """One session's facts: working folder, branch, first message, replies."""
    cwd = branch = first = None
    replies = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not isinstance(e, dict):
                continue
            cwd = cwd or e.get("cwd")
            branch = branch or e.get("gitBranch")
            msg = e.get("message") if isinstance(e.get("message"), dict) else {}
            if e.get("type") == "user" and first is None:
                c = msg.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                if isinstance(c, str) and c.strip():
                    first = c.strip()
            if e.get("type") == "assistant" and isinstance(msg.get("usage"), dict) and e.get("timestamp"):
                replies.append((msg.get("id") or e.get("uuid") or id(e), e["timestamp"], msg["usage"]))
    return cwd or "", branch or "", first or "", replies


def weight(u):
    n = lambda k: u.get(k) or 0
    return (n("input_tokens") + 1.25 * n("cache_creation_input_tokens")
            + 0.1 * n("cache_read_input_tokens") + 5 * n("output_tokens"))


def role(project, cards, cwd, branch, first):
    for desk, card in cards:
        # A desk's branch may carry its name before the card's: road-relay-build.
        name = re.escape(card) if not desk else "(?:" + re.escape(desk) + "-)?" + re.escape(card)
        # land writes the card with its date, which is already the branch's.
        date = "" if DATED.match(card) else r"\d{4}-\d{2}-\d{2}-"
        pat = re.compile(r"task[/-]" + re.escape(project) + r"[/-]" + date + name + r"(?![\w-])")
        if pat.search(branch) or pat.search(cwd) or pat.search(first):
            return card
    if project not in re.split(r"[\\/]", cwd):
        return None
    head = first[:200]
    if "/conductor" in head:
        return "conductors"
    if re.search(r"<command-name>/(run|hephcofounder)</command-name>|^/(run|hephcofounder)\b", head) \
            or re.match(r"you are [\w-]*master\b", head, re.IGNORECASE):
        return "masters"
    return "the rest"


def usage(project, cards, logs, lo, hi):
    """Weighted tokens per card and per role, counted once per reply."""
    totals, sessions, seen = {}, {}, set()
    lo_stamp = lo.timestamp()
    for path in glob.glob(os.path.join(logs, "**", "*.jsonl"), recursive=True):
        try:
            if os.path.getmtime(path) < lo_stamp:
                continue  # last written before the run began
        except OSError:
            continue
        cwd, branch, first, replies = read_log(path)
        who = role(project, cards, cwd, branch, first)
        if who is None:
            continue
        got = 0.0
        for key, stamp, u in replies:
            try:
                when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when.tzinfo is None:
                when = when.astimezone()
            if not (lo <= when <= hi) or key in seen:
                continue
            seen.add(key)
            got += weight(u)
        if got:
            totals[who] = totals.get(who, 0.0) + got
            sessions[who] = sessions.get(who, 0) + 1
    return totals, sessions


def main(argv):
    parser = argparse.ArgumentParser(prog="measures.py", description="Print a run's four measures.")
    parser.add_argument("run", help="the run's folder, docs/runs/<n>")
    parser.add_argument("--logs", default=os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    parser.add_argument("--until", help='"yyyy-mm-dd hh:mm", this machine\'s clock; by default the run\'s close, or now')
    args = parser.parse_args(argv[1:])
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    record_path = os.path.join(args.run, "run.md")
    try:
        with open(record_path, encoding="utf-8") as f:
            record = f.read()
    except OSError:
        print(f"no run record at {record_path}")
        return 1
    page = sections(record)
    plan_path = os.path.join(args.run, "plan-signed.md")
    plan = {}
    if os.path.exists(plan_path):
        with open(plan_path, encoding="utf-8") as f:
            plan = sections(f.read())

    title = next((TITLE.match(l) for l in record.splitlines() if TITLE.match(l)), None)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(args.run))))
    project = title.group(1) if title else os.path.basename(root)
    start = next((START.match(l).group(1) for l in page.get("Go", []) if START.match(l)), None)
    if start is None:
        print(f"no '- Start: yyyy-mm-dd hh:mm' line under ## Go in {record_path}")
        return 1
    lo = local_time(start)
    number = os.path.basename(os.path.abspath(args.run))
    close = None if args.until else closed_at(root, number)
    hi = local_time(args.until) if args.until else close or dt.datetime.now().astimezone()

    landed, others = [], 0
    for line in bullets(page.get("Merges", [])):
        f = fields(line)
        got = card_of(f[1]) if len(f) > 1 else None
        if got is None:
            others += 1
        elif got[1] not in [c for _, c in landed]:
            landed.append(got)
    cards = [c for _, c in landed]
    label = {c: (d + " " + c).strip() for d, c in landed}

    print(f"Measures — run {number} — {project}")
    print(f"Logs: {args.logs}, {lo:%Y-%m-%d %H:%M} to " + ("the run's close, " if close else "") + f"{hi:%Y-%m-%d %H:%M}")

    print("\n## It works")
    tried = {}
    for line in bullets(page.get("It works", [])):
        f = fields(line)
        if len(f) >= 3 and VERDICT.match(f[2]):
            got = card_of(f[1])
            if got:
                tried[got[1]] = (f[2].lower(), f[3] if len(f) > 3 else "")
    for c in cards:
        word, how = tried.get(c, ("not tried", ""))
        print(f"- {label[c]} · {word}" + (f" · {how}" if how else ""))
    if not cards:
        print("- no card landed")

    print("\n## Usage per finished piece")
    totals, sessions = usage(project, landed, args.logs, lo, hi)
    whole = sum(totals.values())
    print("Tokens weighted: input + cache writes x 1.25 + cache reads x 0.1 + output x 5.")
    for who in cards + ["masters", "conductors", "the rest"]:
        t = totals.get(who, 0.0)
        share = 100 * t / whole if whole else 0.0
        print(f"- {label.get(who, who)} · {t:,.0f} · {share:.1f}% · {sessions.get(who, 0)} sessions")
    print(f"- total · {whole:,.0f}")

    print("\n## Share finished")
    planned = pieces(plan.get("The path", []))
    done, unnamed = set(), []
    for desk, card in landed:
        named = named_pieces(root, desk, card) & planned
        done |= named
        if not named:
            unnamed.append(label[card])
    share = f"{100 * len(done) / len(planned):.0f}%" if planned else "no pieces read"
    without = f"; {len(unnamed)} name{'s' if len(unnamed) == 1 else ''} no piece: {', '.join(unnamed)}" if unnamed else ""
    print(f"{len(done)} of {len(planned)} pieces landed ({len(cards)} cards{without}): {share}"
          + (f" ({others} merge lines name no card)" if others else ""))

    print("\n## Surprises")
    unforeseen = bullets(page.get("Unforeseen key points", []))
    blockers = bullets(page.get("Blockers", []))
    print(f"{len(unforeseen) + len(blockers)}: {len(unforeseen)} unforeseen key points, {len(blockers)} blockers")
    for line in unforeseen:
        print(f"Unforeseen {line}")
    for line in blockers:
        print(f"Blocker {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
