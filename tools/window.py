# window.py: how full is the five-hour window, and the week, read once.
#
# What it holds
#   One five-hour usage window serves every project on this machine. On
#   28 Oct 2026 engine-motion-graphics' master read it at 09:19 (2%), then
#   ran review rounds with no landing, and a master read the window only at
#   a landing or a wake; the window went from 71% to 90% in 11 minutes with
#   two runs on it, and it hit its limit with no handover, no workers
#   wrapped and no wake-up set (docs/decisions.md, 28 Oct 14:12). His rule
#   (14:39, corrected 15:42): under 75% full pace; from 75% to 95% keep
#   working, one new agent only as one finishes, the window read every 5
#   minutes; everything committed, wrapped and handed over before 95%.
#   So this tool:
#   1. Reads the window as tracks.md rule 11 says:
#        claude -p "ok" --model sonnet --output-format stream-json --verbose
#      and from its rate_limit_event line takes
#      rate_limit_info.unifiedWindows.five_hour and .seven_day, each's
#      utilization (a fraction: 0.36 is 36%) and resetsAt (seconds since
#      1970, UTC).
#   2. Prints three lines:
#        window: 36% · resets 14:00 this computer (22:00, Thu 12 Nov his) · read 10:35
#        week: 4% · resets 14:00, Mon 16 Nov this computer (22:00, Mon 16 Nov his)
#        full pace
#      The last line starts with one of three words: "full pace" under 75%,
#      "slow down" from 75% to under 95%, "wrap now" at 95% or more, or when
#      the pace since the previous reading would pass 95% before the next
#      tick and before the reset, with its reason in brackets: "wrap now
#      (at 96%)", "wrap now (the pace would pass 95% within 7 minutes)".
#      Never "stop": from 75% the run keeps working (his 15:42 correction).
#      His time comes from the zone file where_am_i.py reads (loaded from
#      where_am_i.py beside this tool, so the zone stays in one place); with
#      no zone it says "(his time not known)".
#   3. The pace. The previous reading counts only when it is less than 30
#      minutes old and names the same five-hour reset; then the pace is
#      points per minute between the two, and "wrap now" is said when this
#      reading plus 20 minutes (one tick) of that pace reaches 95, before
#      the reset it names. A pace reaching 95 at the reset, or up to one tick
#      after it, says "slow down" at any percent.
#      Why: at two runs' pace 75% read once can be past 95% at the next tick;
#      and past the reset the pace starts again from nothing (L038: two masters
#      were told to wrap when the reset was about to empty the window).
#   4. One reading for the machine. Each readable reading replaces the last
#      in window.json in the machine-wide agentic-meta folder (beside seats\
#      and his-time-zone.txt: %LOCALAPPDATA%\agentic-meta\, or
#      ~/.local/share/agentic-meta/ with no LOCALAPPDATA), so every master
#      and cap_check.py read the same one. Its form: {"read_at": <seconds>,
#      "five_hour": {"percent": <n>, "resets_at": <seconds>}, "seven_day":
#      {the same}, "word": "full pace" | "slow down" | "wrap now",
#      "previous": <the reading it replaced, without its own previous, or
#      null>}. Written whole to a temporary file beside it and renamed, so a
#      reader never meets half a file.
#   5. Unreadable is said, never guessed. No claude, no rate_limit_event or
#      a field missing: it prints "window: unreadable (<why>)" and
#      "wrap now (window unreadable; rule 11: wake-up five hours from now)",
#      exits 1 and leaves window.json as it was. A readable reading exits 0,
#      whatever its word.
#   One reading per call: no loop and no timer here. A read sends a
#   message, and is never made on a clock of its own (rule 11).
#
# How to run it
#   python tools/window.py                    (reads the window now)
#   python tools/window.py --from <file>      (reads a saved output instead)
#   python tools/window.py --json             (the reading as written to window.json)
#   python tools/window.py --claude <path>    (the claude command; default claude)
#   python tools/window.py --state <path>     (another file in place of window.json)
#   python tools/window.py --zone-file <path> (his zone from another file, as where_am_i.py)
#
# Python 3 standard library only. Its only network step is the claude call.

import argparse
import datetime
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

TOOLS = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("where_am_i_for_window", os.path.join(TOOLS, "where_am_i.py"))
where_am_i = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(where_am_i)

SLOW_DOWN_AT = 75
WRAP_AT = 95
TICK_MINUTES = 20          # the watch's tick: the pace is read this far ahead
PREVIOUS_COUNTS_FOR = 30 * 60  # seconds: an older previous reading is not used for the pace
WORDS = ("full pace", "slow down", "wrap now")
UNREADABLE_WORD = "wrap now (window unreadable; rule 11: wake-up five hours from now)"


class Unreadable(Exception):
    pass


def default_state():
    """window.json beside cap_check.py's seats folder, in the machine-wide agentic-meta folder."""
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "agentic-meta", "window.json")


def read_output(source, claude):
    """The stream-json text: from the saved file source, or from one claude call."""
    if source:
        try:
            with open(source, encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError as e:
            raise Unreadable(f"cannot read {source}: {e.strerror}")
    command = shutil.which(claude)
    if command is None:
        raise Unreadable(f"no claude: {claude} not found")
    try:
        done = subprocess.run([command, "-p", "ok", "--model", "sonnet", "--output-format", "stream-json", "--verbose"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        raise Unreadable(f"claude could not be run: {e}")
    return done.stdout


def parse(text):
    """{five_hour: {percent, resets_at}, seven_day: {...}} from the last rate_limit_event line, or Unreadable."""
    event = None
    for line in text.splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, dict) and item.get("type") == "rate_limit_event":
            event = item
    if event is None:
        raise Unreadable("no rate_limit_event")
    windows = (event.get("rate_limit_info") or {}).get("unifiedWindows")
    if not isinstance(windows, dict):
        raise Unreadable("no rate_limit_info.unifiedWindows in the rate_limit_event")
    reading = {}
    for name in ("five_hour", "seven_day"):
        window = windows.get(name)
        if not isinstance(window, dict):
            raise Unreadable(f"no {name} in the rate_limit_event")
        for field in ("utilization", "resetsAt"):
            value = window.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise Unreadable(f"no {name}.{field} in the rate_limit_event")
        reading[name] = {"percent": round(window["utilization"] * 100), "resets_at": int(window["resetsAt"])}
    return reading


def load_previous(state):
    """The reading in the state file, without its own previous, or None."""
    try:
        with open(state, encoding="utf-8") as f:
            previous = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(previous, dict):
        return None
    previous.pop("previous", None)
    return previous


def seconds_to_wrap(reading, previous, read_at):
    """Seconds until 95% at the pace since previous, exactly, when that reading counts; else None."""
    try:
        age = read_at - previous["read_at"]
        same_reset = previous["five_hour"]["resets_at"] == reading["five_hour"]["resets_at"]
        rise = reading["five_hour"]["percent"] - previous["five_hour"]["percent"]
    except (KeyError, TypeError):
        return None
    if not (0 < age < PREVIOUS_COUNTS_FOR) or not same_reset or rise <= 0:
        return None
    return Fraction(age) * (WRAP_AT - reading["five_hour"]["percent"]) / rise


def pace_minutes(reading, previous, read_at):
    """Minutes until 95% at the pace since previous, when it reaches 95 within a tick and before the reset; else None."""
    seconds = seconds_to_wrap(reading, previous, read_at)
    if seconds is None or seconds > TICK_MINUTES * 60 or seconds >= reading["five_hour"]["resets_at"] - read_at:
        return None
    return max(1, math.ceil(seconds / 60))


def pace_meets_the_reset(reading, previous, read_at):
    """The pace reaches 95% at or after the reset, and no later than one tick after it."""
    seconds = seconds_to_wrap(reading, previous, read_at)
    to_reset = reading["five_hour"]["resets_at"] - read_at
    return seconds is not None and to_reset <= seconds <= to_reset + TICK_MINUTES * 60


def word_of(reading, previous, read_at):
    """The last line: its word, and the reason in brackets for wrap now."""
    percent = reading["five_hour"]["percent"]
    if percent >= WRAP_AT:
        return "wrap now", f"wrap now (at {percent}%)"
    minutes = pace_minutes(reading, previous, read_at) if previous else None
    if minutes is not None:
        return "wrap now", f"wrap now (the pace would pass {WRAP_AT}% within {minutes} minutes)"
    if percent >= SLOW_DOWN_AT or (previous and pace_meets_the_reset(reading, previous, read_at)):
        return "slow down", "slow down"
    return "full pace", "full pace"


def day(moment):
    return f"{moment:%a} {moment.day} {moment:%b}"


def resets(seconds, zone_file, with_day):
    """When a window resets: this computer's clock, then his."""
    moment = datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc)
    local = moment.astimezone()
    here = f"{local:%H:%M}, {day(local)}" if with_day else f"{local:%H:%M}"
    his, _ = where_am_i.his_time(zone_file, now=moment)
    there = f"{his['time']}, {his['day']} his" if his else "his time not known"
    return f"resets {here} this computer ({there})"


def write_state(state, record):
    """Write the record whole to a temporary file beside state, then rename it over state."""
    folder = os.path.dirname(os.path.abspath(state))
    os.makedirs(folder, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".window-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
            f.write("\n")
        os.replace(temporary, state)
    except BaseException:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise


def main():
    parser = argparse.ArgumentParser(description="Read the five-hour window and the week once, and say the word.")
    parser.add_argument("--from", dest="source", help="a saved stream-json output to read instead of running claude")
    parser.add_argument("--claude", default="claude", help="the claude command (default: claude)")
    parser.add_argument("--state", default=default_state(),
                        help="the reading's file (default: window.json in the machine-wide agentic-meta folder)")
    parser.add_argument("--zone-file", default=where_am_i.default_zone_file(),
                        help="the file that holds his zone (default: his-time-zone.txt beside the seats folder)")
    parser.add_argument("--json", action="store_true", help="print the reading as written to the state file")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        reading = parse(read_output(args.source, args.claude))
    except Unreadable as e:
        print(f"window: unreadable ({e})")
        print(UNREADABLE_WORD)
        return 1

    read_at = int(time.time())
    previous = load_previous(args.state)
    word, last_line = word_of(reading, previous, read_at)
    record = {"read_at": read_at, "five_hour": reading["five_hour"], "seven_day": reading["seven_day"],
              "word": word, "previous": previous}
    write_state(args.state, record)

    if args.json:
        print(json.dumps(record, indent=2))
        return 0
    now = datetime.datetime.fromtimestamp(read_at).astimezone()
    print(f"window: {reading['five_hour']['percent']}% · "
          f"{resets(reading['five_hour']['resets_at'], args.zone_file, with_day=False)} · read {now:%H:%M}")
    print(f"week: {reading['seven_day']['percent']}% · "
          f"{resets(reading['seven_day']['resets_at'], args.zone_file, with_day=True)}")
    print(last_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
