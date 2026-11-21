# Tests for window.py. Every run reads a saved output (--from), never claude,
# and is given a --state and a --zone-file in the test's own temp folder, with
# LOCALAPPDATA pointed there too: the machine-wide agentic-meta folder (his
# window.json and his-time-zone.txt) is never made, read or written by a test.
# window-36.jsonl beside this file is the one saved reading, in the shape read
# on this machine on 12 Nov 2026; the others are written in the temp folder.

import datetime
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "window.py"
SAVED_36 = Path(__file__).resolve().parent / "window-36.jsonl"
RESETS = 1794483600
WEEK_RESETS = 1794862800

_spec = importlib.util.spec_from_file_location("window_for_tests", TOOL)
window = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(window)


def saved(tmp_path, utilization, resets=RESETS, name="reading.jsonl"):
    """A saved stream-json output whose rate_limit_event reads utilization."""
    event = {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "resetsAt": resets,
             "unifiedWindows": {"five_hour": {"utilization": utilization, "resetsAt": resets, "status": "allowed"},
                                "seven_day": {"utilization": 0.04, "resetsAt": WEEK_RESETS, "status": "allowed"}}}}
    path = tmp_path / name
    path.write_text('{"type":"system","subtype":"init"}\n' + json.dumps(event) + '\n{"type":"result","result":"ok"}\n',
                    encoding="utf-8")
    return path


def previous(tmp_path, percent, minutes_ago, resets=RESETS):
    """A state file holding one earlier reading."""
    state = tmp_path / "window.json"
    state.write_text(json.dumps({"read_at": int(time.time()) - minutes_ago * 60,
                                 "five_hour": {"percent": percent, "resets_at": resets},
                                 "seven_day": {"percent": 4, "resets_at": WEEK_RESETS},
                                 "word": "full pace", "previous": None}), encoding="utf-8")
    return state


def run(tmp_path, source, *extra, zone=None):
    zone_file = tmp_path / "zone.txt"
    if zone is not None:
        zone_file.write_text(zone + "\n", encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "LOCALAPPDATA": str(tmp_path / "localappdata")}
    return subprocess.run([sys.executable, "-B", str(TOOL), "--from", str(source), "--state", str(tmp_path / "window.json"),
                           "--zone-file", str(zone_file), *extra],
                          capture_output=True, text=True, encoding="utf-8", env=env)


def lines(done):
    return done.stdout.strip().splitlines()


def in_minutes(minutes):
    """A five-hour reset this many minutes from the clock."""
    return int(time.time()) + minutes * 60


def last_line(percent, rose_from, over_minutes, to_reset):
    """word_of's last line at an exact moment: percent, having risen from rose_from, to_reset minutes before the reset."""
    read_at = int(time.time())
    resets = read_at + to_reset * 60
    return window.word_of({"five_hour": {"percent": percent, "resets_at": resets}},
                          {"read_at": read_at - over_minutes * 60, "five_hour": {"percent": rose_from, "resets_at": resets}},
                          read_at)[1]


def test_window_36_reads_full_pace(tmp_path):
    done = run(tmp_path, SAVED_36)
    assert done.returncode == 0, done.stderr
    out = lines(done)
    assert len(out) == 3
    assert out[0].startswith("window: 36% · resets ")
    assert out[1].startswith("week: 4% · resets ")
    assert out[2] == "full pace"
    assert "stop" not in done.stdout


def test_window_80_reads_slow_down(tmp_path):
    done = run(tmp_path, saved(tmp_path, 0.80))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "slow down"
    assert "stop" not in done.stdout


def test_window_95_reads_wrap_now(tmp_path):
    done = run(tmp_path, saved(tmp_path, 0.95))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "wrap now (at 95%)"


def test_window_pace_70_then_85_reads_wrap_now(tmp_path):
    resets = in_minutes(60)
    previous(tmp_path, 70, minutes_ago=10, resets=resets)
    done = run(tmp_path, saved(tmp_path, 0.85, resets=resets))
    assert done.returncode == 0, done.stderr
    last = lines(done)[-1]
    assert last.startswith("wrap now (the pace would pass 95% within ")
    assert json.loads((tmp_path / "window.json").read_text(encoding="utf-8"))["word"] == "wrap now"


def test_window_74_with_23_minutes_to_the_reset_reads_slow_down(tmp_path):
    resets = in_minutes(23)  # 65% to 74% in 10 minutes: 95% in about 23.3 minutes, just after the reset
    previous(tmp_path, 65, minutes_ago=10, resets=resets)
    done = run(tmp_path, saved(tmp_path, 0.74, resets=resets))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "slow down"
    assert json.loads((tmp_path / "window.json").read_text(encoding="utf-8"))["word"] == "slow down"


def test_window_84_with_20_minutes_to_the_reset_reads_slow_down(tmp_path):
    resets = in_minutes(20)  # 79% to 84% in 10 minutes: 95% in 22 minutes, after the reset
    previous(tmp_path, 79, minutes_ago=10, resets=resets)
    done = run(tmp_path, saved(tmp_path, 0.84, resets=resets))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "slow down"
    # 95% falling exactly at the reset, inside the tick: the pace alone would say wrap now.
    assert last_line(84, 73, over_minutes=20, to_reset=20) == "slow down"


def test_window_pace_reaching_95_before_the_reset_reads_wrap_now():
    # The real reading of 12 Nov 11:17: 74%, 19 minutes to 95%, 23 minutes to the reset.
    assert last_line(74, 53, over_minutes=19, to_reset=23) == "wrap now (the pace would pass 95% within 19 minutes)"
    assert last_line(96, 90, over_minutes=10, to_reset=2) == "wrap now (at 96%)"  # 95% or more, whatever the reset


def test_window_slow_pace_keeps_the_word_of_its_percent():
    assert last_line(40, 39, over_minutes=10, to_reset=60) == "full pace"
    assert last_line(80, 79, over_minutes=10, to_reset=60) == "slow down"
    # 95% more than one tick after the reset: the pace says nothing, so the percent's word stands.
    assert last_line(74, 65, over_minutes=10, to_reset=3) == "full pace"


def test_window_pace_from_reading_40_minutes_old_not_counted(tmp_path):
    previous(tmp_path, 70, minutes_ago=40)
    done = run(tmp_path, saved(tmp_path, 0.85))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "slow down"


def test_window_pace_under_another_reset_not_counted(tmp_path):
    previous(tmp_path, 70, minutes_ago=10, resets=RESETS - 5 * 3600)
    done = run(tmp_path, saved(tmp_path, 0.85))
    assert done.returncode == 0, done.stderr
    assert lines(done)[-1] == "slow down"


def test_window_no_rate_limit_event_exits_1_state_unchanged(tmp_path):
    state = previous(tmp_path, 40, minutes_ago=5)
    before = state.read_bytes()
    source = tmp_path / "no-event.jsonl"
    source.write_text('{"type":"system","subtype":"init"}\n{"type":"result","result":"ok"}\n', encoding="utf-8")
    done = run(tmp_path, source)
    assert done.returncode == 1
    assert lines(done) == ["window: unreadable (no rate_limit_event)",
                           "wrap now (window unreadable; rule 11: wake-up five hours from now)"]
    assert state.read_bytes() == before


def test_window_state_file_holds_the_reading(tmp_path):
    earlier = json.loads(previous(tmp_path, 30, minutes_ago=50).read_text(encoding="utf-8"))
    before = int(time.time())
    done = run(tmp_path, SAVED_36, "--json")
    assert done.returncode == 0, done.stderr
    record = json.loads((tmp_path / "window.json").read_text(encoding="utf-8"))
    assert set(record) == {"read_at", "five_hour", "seven_day", "word", "previous"}
    assert before <= record["read_at"] <= int(time.time())
    assert record["five_hour"] == {"percent": 36, "resets_at": RESETS}
    assert record["seven_day"] == {"percent": 4, "resets_at": WEEK_RESETS}
    assert record["word"] == "full pace"
    earlier.pop("previous")
    assert record["previous"] == earlier
    assert json.loads(done.stdout) == record
    assert [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")] == []


def test_window_his_time_with_zone_utc8(tmp_path):
    done = run(tmp_path, SAVED_36, zone="UTC+8")
    assert done.returncode == 0, done.stderr
    his = datetime.datetime.fromtimestamp(RESETS, datetime.timezone.utc) + datetime.timedelta(hours=8)
    here = datetime.datetime.fromtimestamp(RESETS).astimezone()
    out = lines(done)
    assert f"resets {here:%H:%M} this computer ({his:%H:%M}, {his:%a} {his.day} {his:%b} his)" in out[0]
    week = datetime.datetime.fromtimestamp(WEEK_RESETS, datetime.timezone.utc) + datetime.timedelta(hours=8)
    assert f"({week:%H:%M}, {week:%a} {week.day} {week:%b} his)" in out[1]


def test_window_his_time_not_known_without_zone(tmp_path):
    done = run(tmp_path, SAVED_36)
    assert done.returncode == 0, done.stderr
    out = lines(done)
    assert "(his time not known)" in out[0]
    assert "(his time not known)" in out[1]
