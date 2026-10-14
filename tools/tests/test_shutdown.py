# Tests for shutdown.py. Every test writes its own run record in pytest's
# tmp_path, and fakes the four things that touch the machine: whether an id
# is running and when it started, stopping a process, the cap_check it runs
# to release a seat, and whose seat a claim is. No real process is stopped,
# no real seat released and no real claim read.
#   python -B -m pytest template/tools/tests/test_shutdown.py -q

import datetime
import importlib.util
import os
import re
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("shutdown", os.path.join(HERE, "..", "shutdown.py"))
shutdown = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shutdown)

DAY = datetime.datetime(2026, 10, 8)

HEAD = """# Run 3 — test

## Go
- Start: 2026-10-08 06:54

## Shutdown list
Everything this run starts. One line each: started · kind · what · its id · how it stops · open, or closed at hh:mm.
"""

TAIL = """
## Handover
- 07:30 · process · not in the list, so never read · pid 4444 · stop it · open
"""


@pytest.fixture
def machine(monkeypatch):
    """The faked machine: running ids and their start times, the caller's own claims, and what
    was stopped and released."""
    state = {"running": {}, "stopped": [], "released": [], "release_says": "RELEASED: {id}", "own": set()}

    def fake_run(cmd, **kwargs):
        assert cmd[:3] == [shutdown.sys.executable, shutdown.CAP_CHECK, "release"], cmd
        state["released"].append(cmd[3])
        return subprocess.CompletedProcess(cmd, 0, stdout=state["release_says"].format(id=cmd[3]), stderr="")

    def fake_stop(pid):
        state["stopped"].append(pid)
        state["running"].pop(pid, None)
        return True

    monkeypatch.setattr(shutdown.subprocess, "run", fake_run)
    monkeypatch.setattr(shutdown, "pid_alive", lambda pid: pid in state["running"])
    monkeypatch.setattr(shutdown, "started_at", lambda pid: state["running"].get(pid))
    monkeypatch.setattr(shutdown, "stop_process", fake_stop)
    monkeypatch.setattr(shutdown, "own_seat", lambda claim_id: claim_id in state["own"])
    return state


def record(tmp_path, *lines):
    run = tmp_path / "docs" / "runs" / "3"
    run.mkdir(parents=True)
    (run / "run.md").write_text(HEAD + "".join(line + "\n" for line in lines) + TAIL, encoding="utf-8")
    return run


def go(run, capsys, *args):
    code = shutdown.main(["shutdown.py", str(run), *args])
    return code, capsys.readouterr().out


def text(run):
    return (run / "run.md").read_text(encoding="utf-8")


CLOSED_NOW = re.compile(r" · closed \d{2}:\d{2}$", re.MULTILINE)


def test_a_seat_is_released_with_the_cap_check_beside_it_and_marked_closed(tmp_path, capsys, machine):
    run = record(tmp_path, "- 06:54 · seat · the master's seat · 20261008-065457-master-6840-489c · `cap_check.py release` · open")
    code, out = go(run, capsys)
    assert machine["released"] == ["20261008-065457-master-6840-489c"]
    assert code == 0 and out.rstrip().endswith("NOTHING LEFT")
    assert re.search(r"20261008-065457-master-6840-489c · `cap_check.py release` · closed \d{2}:\d{2}\n", text(run))


def test_a_seat_already_gone_is_closed(tmp_path, capsys, machine):
    machine["release_says"] = "NOT FOUND: no claim {id} in the seats folder"
    run = record(tmp_path, "- 06:54 · seat · a seat · 20261008-065457-master-1-aaaa · release it · open")
    code, out = go(run, capsys)
    assert code == 0 and len(CLOSED_NOW.findall(text(run))) == 1


@pytest.mark.parametrize("kind", ["process", "watch", "server"])
def test_a_running_process_started_before_the_line_is_stopped(tmp_path, capsys, machine, kind):
    machine["running"][5120] = DAY.replace(hour=7, minute=11, second=48)  # within the line's minute
    run = record(tmp_path, f"- 07:11 · {kind} · the page server · pid 5120 · stop it · open")
    code, out = go(run, capsys)
    assert machine["stopped"] == [5120]
    assert "STOPPED" in out and code == 0
    assert len(CLOSED_NOW.findall(text(run))) == 1


def test_a_process_whose_id_is_gone_is_closed_not_stopped(tmp_path, capsys, machine):
    run = record(tmp_path, "- 07:11 · watch · the inbox watch · claude.exe 777 · stop it · open")
    code, out = go(run, capsys)
    assert machine["stopped"] == []
    assert "GONE" in out and code == 0
    assert len(CLOSED_NOW.findall(text(run))) == 1


def test_a_reused_id_is_listed_and_never_stopped(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=40)  # a new process took the id after 07:11
    run = record(tmp_path, "- 07:11 · process · the signal box · pid 5120 · stop it · open")
    before = text(run)
    code, out = go(run, capsys)
    assert machine["stopped"] == []
    assert code == 1 and "LEFT: 1" in out and "reused id" in out
    assert text(run) == before


def test_a_start_time_that_cannot_be_read_is_never_stopped(tmp_path, capsys, machine, monkeypatch):
    machine["running"][5120] = DAY.replace(hour=7)
    monkeypatch.setattr(shutdown, "started_at", lambda pid: None)
    run = record(tmp_path, "- 07:11 · server · a page server · pid 5120 · stop it · open")
    code, out = go(run, capsys)
    assert machine["stopped"] == [] and code == 1 and "cannot be read" in out


@pytest.mark.parametrize("kind", ["thread", "child", "schedule", "tunnel"])
def test_t3_kinds_and_any_other_are_listed_for_the_master_with_how_it_stops(tmp_path, capsys, machine, kind):
    run = record(tmp_path, f"- 07:11 · {kind} · worker forms · T3 mcp:2e2e00de, claude.exe 12828 · archive the thread once it lands · open")
    before = text(run)
    code, out = go(run, capsys)
    assert code == 1 and "LEFT: 1" in out
    assert "for the master to close by hand: archive the thread once it lands" in out
    assert machine["stopped"] == [] and machine["released"] == []
    assert text(run) == before


def test_a_closed_line_is_left_alone(tmp_path, capsys, machine):
    machine["running"][5296] = DAY.replace(hour=7)
    run = record(tmp_path, "- 07:00 · process · the conductor · pid 5296 · stop it · closed 07:10",
                 "- 07:00 · seat · its seat · 20261008-070055-conductor-5296-624a · release it · closed 07:10")
    before = text(run)
    code, out = go(run, capsys)
    assert code == 0 and out.strip() == "NOTHING LEFT"
    assert machine["stopped"] == [] and machine["released"] == []
    assert text(run) == before


def test_closed_marks_one_item_closed_by_hand(tmp_path, capsys, machine):
    run = record(tmp_path, "- 07:11 · thread · worker forms · T3 mcp:2e2e00de, claude.exe 12828 · archive it · open",
                 "- 07:11 · thread · worker seats · T3 mcp:2272d93d, claude.exe 17828 · archive it · open")
    code, out = go(run, capsys, "--closed", "mcp:2e2e00de")
    assert code == 1 and "LEFT: 1" in out and "mcp:2272d93d" in out
    assert re.search(r"mcp:2e2e00de, claude\.exe 12828 · archive it · closed \d{2}:\d{2}\n", text(run))
    assert "mcp:2272d93d, claude.exe 17828 · archive it · open\n" in text(run)
    code, out = go(run, capsys, "--closed", "T3 mcp:2272d93d, claude.exe 17828")
    assert code == 0 and out.rstrip().endswith("NOTHING LEFT")


def test_closed_with_an_unknown_id_changes_nothing(tmp_path, capsys, machine):
    run = record(tmp_path, "- 07:11 · thread · worker forms · T3 mcp:2e2e00de · archive it · open")
    before = text(run)
    code, out = go(run, capsys, "--closed", "mcp:ffffffff")
    assert code == 1 and out.startswith("REFUSE") and text(run) == before


def test_left_lists_each_open_line_and_a_line_not_in_the_form(tmp_path, capsys, machine):
    run = record(tmp_path, "- 07:11 · schedule · the wake-up · T3 schedule 42 · delete the schedule · open",
                 "- 07:12 · a line with too few parts · open")
    code, out = go(run, capsys)
    assert code == 1
    assert "LEFT: 2" in out
    assert "  - 07:11 · schedule · the wake-up · T3 schedule 42 · delete the schedule · open" in out
    assert "not in the shutdown list's form" in out
    assert "never read" not in out  # the next section's bullet is not on the list


def test_dry_run_says_what_it_would_do_and_writes_nothing(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 06:54 · seat · the master's seat · 20261008-065457-master-6840-489c · release it · open",
                 "- 07:11 · server · a page server · pid 5120 · stop it · open",
                 "- 07:11 · watch · a gone watch · pid 6000 · stop it · open",
                 "- 07:11 · thread · worker forms · T3 mcp:2e2e00de · archive it · open")
    before = (run / "run.md").read_bytes()
    code, out = go(run, capsys, "--dry-run")
    assert code == 0
    assert "WOULD RELEASE" in out and "WOULD STOP" in out and "WOULD CLOSE" in out and "WOULD LEAVE" in out
    assert out.rstrip().endswith("DRY RUN: nothing changed")
    assert machine["stopped"] == [] and machine["released"] == []
    assert (run / "run.md").read_bytes() == before


def test_the_newest_run_is_read_when_none_is_named(tmp_path, capsys, machine, monkeypatch):
    run = record(tmp_path, "- 07:11 · thread · worker forms · T3 mcp:2e2e00de · archive it · open")
    (tmp_path / "docs" / "runs" / "2").mkdir()
    monkeypatch.chdir(tmp_path)
    code = shutdown.main(["shutdown.py", "--closed", "mcp:2e2e00de"])
    assert code == 0 and "NOTHING LEFT" in capsys.readouterr().out
    assert len(CLOSED_NOW.findall(text(run))) == 1


def test_a_record_with_windows_line_endings_keeps_them(tmp_path, capsys, machine):
    run = record(tmp_path, "- 07:11 · watch · a gone watch · pid 6000 · stop it · open")
    (run / "run.md").write_bytes(text(run).replace("\n", "\r\n").encode("utf-8"))
    go(run, capsys)
    data = (run / "run.md").read_bytes()
    assert data.count(b"\r\n") == data.count(b"\n")
    assert re.search(rb"pid 6000 \xc2\xb7 stop it \xc2\xb7 closed \d{2}:\d{2}\r\n", data)


def test_a_kept_server_is_not_stopped_stays_open_and_is_named(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 07:11 · server · the page server his phone uses · pid 5120 · stop it · open")
    before = text(run)
    code, out = go(run, capsys, "--keep", "pid 5120")
    assert machine["stopped"] == [] and 5120 in machine["running"]
    assert text(run) == before
    assert "KEPT: server · the page server his phone uses · pid 5120\n      the master named it" in out
    assert "STOPPED" not in out


def test_the_callers_own_seat_is_left_open_and_named_while_another_is_released(tmp_path, capsys, machine):
    machine["own"].add("20261008-065457-master-6840-489c")
    run = record(tmp_path, "- 06:54 · seat · the master's seat · 20261008-065457-master-6840-489c · `cap_check.py release` · open",
                 "- 07:02 · seat · a worker's seat · 20261008-070210-worker-7312-0b1e · `cap_check.py release` · open")
    code, out = go(run, capsys)
    assert machine["released"] == ["20261008-070210-worker-7312-0b1e"]
    assert "20261008-065457-master-6840-489c · `cap_check.py release` · open\n" in text(run)
    assert re.search(r"20261008-070210-worker-7312-0b1e · `cap_check.py release` · closed \d{2}:\d{2}\n", text(run))
    assert ("KEPT: seat · the master's seat · 20261008-065457-master-6840-489c\n"
            "      the seat of the session running this") in out


def test_with_only_kept_items_open_it_ends_nothing_left(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 07:11 · server · a page server · pid 5120 · stop it · open",
                 "- 07:12 · thread · worker forms · T3 mcp:2e2e00de, claude.exe 12828 · archive it · open",
                 "- 07:13 · watch · a gone watch · pid 6000 · stop it · open")
    code, out = go(run, capsys, "--keep", "5120", "--keep", "mcp:2e2e00de")
    assert code == 0 and out.rstrip().endswith("NOTHING LEFT")
    assert out.count("KEPT: ") == 2 and "LEFT:" not in out
    assert machine["stopped"] == []
    assert len(re.findall(r" · open$", text(run).split("## Handover")[0], re.MULTILINE)) == 2


def test_with_a_kept_item_and_one_other_left_it_ends_left_1(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 07:11 · server · a page server · pid 5120 · stop it · open",
                 "- 07:12 · thread · worker forms · T3 mcp:2e2e00de · archive it · open")
    code, out = go(run, capsys, "--keep", "pid 5120")
    assert code == 1
    ending = out[out.index("LEFT: 1"):]
    assert "mcp:2e2e00de" in ending and "pid 5120" not in ending
    assert "KEPT: server · a page server · pid 5120" in out and "LEFT: 2" not in out


@pytest.mark.parametrize("wanted, count", [("pid 9999", 0), ("pid", 2)])
def test_a_keep_that_matches_no_open_line_or_more_than_one_is_refused(tmp_path, capsys, machine, wanted, count):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 07:11 · server · a page server · pid 5120 · stop it · open",
                 "- 07:12 · watch · a gone watch · pid 6000 · stop it · open",
                 "- 06:54 · seat · a seat · 20261008-065457-worker-1-aaaa · release it · open")
    before = (run / "run.md").read_bytes()
    code, out = go(run, capsys, "--keep", "pid 5120", "--keep", wanted)
    assert code == 1 and out.startswith(f"REFUSE: {count} open lines have the id {wanted}; nothing changed")
    assert machine["stopped"] == [] and machine["released"] == []
    assert (run / "run.md").read_bytes() == before


def test_dry_run_says_would_keep_for_both_kinds_and_writes_nothing(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    machine["own"].add("20261008-065457-master-6840-489c")
    run = record(tmp_path, "- 06:54 · seat · the master's seat · 20261008-065457-master-6840-489c · release it · open",
                 "- 07:11 · server · a page server · pid 5120 · stop it · open")
    before = (run / "run.md").read_bytes()
    code, out = go(run, capsys, "--dry-run", "--keep", "pid 5120")
    assert code == 0 and out.rstrip().endswith("DRY RUN: nothing changed")
    assert "WOULD KEEP: seat · the master's seat" in out and "the seat of the session running this" in out
    assert "WOULD KEEP: server · a page server · pid 5120" in out and "the master named it" in out
    assert "WOULD RELEASE" not in out and "WOULD STOP" not in out
    assert machine["stopped"] == [] and machine["released"] == []
    assert (run / "run.md").read_bytes() == before


def test_a_kept_item_is_closed_later_with_closed(tmp_path, capsys, machine):
    machine["running"][5120] = DAY.replace(hour=7, minute=11)
    run = record(tmp_path, "- 07:11 · server · a page server · pid 5120 · stop it · open")
    go(run, capsys, "--keep", "pid 5120")
    code, out = go(run, capsys, "--closed", "pid 5120")
    assert code == 0 and out.rstrip().endswith("NOTHING LEFT")
    assert len(CLOSED_NOW.findall(text(run))) == 1


def test_own_seat_is_the_claim_of_the_claude_above_this_process(tmp_path, monkeypatch):
    seats = tmp_path / "seats"
    seats.mkdir()
    (seats / "20261008-065457-master-6840-489c.json").write_text('{"pid": 6840, "started": null}', encoding="utf-8")
    (seats / "20261008-070210-worker-7312-0b1e.json").write_text('{"pid": 7312, "started": null}', encoding="utf-8")
    me = os.getpid()
    monkeypatch.setattr(shutdown.cap_check, "default_seats", lambda: str(seats))
    monkeypatch.setattr(shutdown.cap_check, "pid_alive", lambda pid: True)
    monkeypatch.setattr(shutdown.cap_check, "process_table", lambda: {
        me: (300, "python.exe"), 300: (6840, "bash.exe"), 6840: (4, "claude.exe"), 7312: (4, "claude.exe")})
    assert shutdown.own_seat("20261008-065457-master-6840-489c") is True
    assert shutdown.own_seat("20261008-070210-worker-7312-0b1e") is False
    assert shutdown.own_seat("20261008-999999-master-1-ffff") is False
