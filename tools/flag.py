# flag.py: raise the running master's flag for the signal box.
#
# What it is for
#   A running master keeps one flag in its newest run's folder,
#   docs/runs/<n>/flag.txt, so the signal box can tell how the run stands
#   (`tracks.md`, "The flag" and "The four flags"). This tool writes it in
#   tracks.md's form: one line, `<flag> <UTC time> <one plain line why>`,
#   for example `working 2026-10-07T05:10Z started the merge-check worker`.
#   The file is overwritten, never appended, and never committed.
#   Why: in run 2 the masters raised their flags by hand, and the box reads
#   the first word and knows no others, so a flag typed wrong is a flag lost.
#
# How to run it (from the project's folder)
#   python tools/flag.py <working | needs-you | handed-over | done> "<why>"
#   It prints FLAG: and the line it wrote (exit 0). Any other flag, an empty
#   why, or no docs/runs/<n>/ here is a REFUSE (exit 1), and nothing is written.
#
# Python 3 standard library only.

import datetime
import os
import sys

FLAGS = ("working", "needs-you", "handed-over", "done")


def newest_run(project):
    runs = os.path.join(project, "docs", "runs")
    numbers = [int(n) for n in os.listdir(runs) if n.isdigit() and os.path.isdir(os.path.join(runs, n))] \
        if os.path.isdir(runs) else []
    return os.path.join(runs, str(max(numbers))) if numbers else None


def main(argv):
    if len(argv) != 3:
        print(f"REFUSE: give a flag and a why: flag.py <{' | '.join(FLAGS)}> \"<why>\"")
        return 1
    flag, why = argv[1], " ".join(argv[2].split())  # one plain line
    if flag not in FLAGS:
        print(f"REFUSE: {flag!r} is not a flag; the box knows only {', '.join(FLAGS)}")
        return 1
    if not why:
        print("REFUSE: the why is empty; say in one plain line why")
        return 1
    run = newest_run(os.getcwd())
    if run is None:
        print("REFUSE: no docs/runs/<n>/ here; run it from the project's folder")
        return 1
    line = f"{flag} {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%MZ} {why}"
    with open(os.path.join(run, "flag.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(f"FLAG: {line}  ({os.path.join(run, 'flag.txt')})")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # a why in any letters prints in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv))
