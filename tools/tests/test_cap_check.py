# Tests for cap_check.py. Every test points the tool at its own empty seats
# folder and its own small project folder (pytest's tmp_path), so nothing
# machine-wide is ever written. "Alive" claims use this test's own process id.
#   python -B -m pytest template/tools/tests/test_cap_check.py -q

import importlib.util
import json
import os
import subprocess
import sys
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("cap_check", os.path.join(HERE, "..", "cap_check.py"))
cap_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap_check)

ALIVE = os.getpid()
DEAD = 999999


@pytest.fixture
def where(tmp_path):
    seats = tmp_path / "seats"
    project = tmp_path / "project"
    (project / "docs").mkdir(parents=True)
    return str(seats), project


def run(where, *args):
    seats, project = where
    return cap_check.main(["cap_check.py", "--seats", seats, "--project", str(project), *args])


def claim(where, capsys, pid=ALIVE, heavy=False):
    args = ["claim", "--kind", "worker", "--card", "docs/cards/x.md", "--pid", str(pid)]
    code = run(where, *(args + ["--heavy"] if heavy else args))
    return code, capsys.readouterr().out


@pytest.fixture
def no_gpu(monkeypatch):
    monkeypatch.setattr(cap_check.shutil, "which", lambda name: None)


def test_four_seats_then_the_fifth_is_refused(where, capsys):
    for n in range(1, 5):
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 4"
    code, out = claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: the cap of 4 is full")
    assert len(os.listdir(where[0])) == 4


def test_a_master_takes_a_seat_like_any_other(where, capsys):
    assert run(where, "claim", "--kind", "master", "--card", "docs/run.md", "--pid", str(ALIVE)) == 0
    assert capsys.readouterr().out.splitlines()[0] == "ALLOW: seat 1 of 4"
    for n in range(2, 5):
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 4"
    code, out = claim(where, capsys)
    assert code == 1
    assert out.strip() == "REFUSE: the cap of 4 is full (4 seats taken)"


def test_release_frees_a_seat(where, capsys):
    ids = []
    for _ in range(4):
        _, out = claim(where, capsys)
        ids.append(out.splitlines()[1].split()[1])
    assert run(where, "release", ids[1]) == 0
    assert capsys.readouterr().out.strip() == f"RELEASED: {ids[1]}"
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 4 of 4"


def test_release_of_an_unknown_claim_fails(where, capsys):
    assert run(where, "release", "no-such-claim") == 1
    assert capsys.readouterr().out.startswith("NOT FOUND:")
    assert run(where, "release", "../seats") == 1


def test_a_dead_claim_is_not_counted_and_the_next_claim_deletes_it(where, capsys):
    claim(where, capsys)
    claim(where, capsys, pid=DEAD)
    assert len(os.listdir(where[0])) == 2
    assert run(where, "list") == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "1 of 4 seats taken"
    assert f"pid {DEAD}" not in out
    assert "1 dead claim(s) not counted" in out
    code, out = claim(where, capsys)
    assert out.splitlines()[0] == "ALLOW: seat 2 of 4"
    assert len(os.listdir(where[0])) == 2  # the dead one is gone


def test_the_claim_file_holds_project_card_kind_pid_time(where, capsys):
    claim(where, capsys)
    (name,) = os.listdir(where[0])
    with open(os.path.join(where[0], name), encoding="utf-8") as f:
        data = json.load(f)
    assert data["project"] == "project"
    assert data["card"] == "docs/cards/x.md"
    assert data["kind"] == "worker"
    assert data["pid"] == ALIVE
    assert data["time"]


def test_his_word_lifts_the_cap(where, capsys, no_gpu):
    (where[1] / "docs" / "cap-lifted.md").write_text('8 — "forget the cap"\n', encoding="utf-8")
    for _ in range(4):
        claim(where, capsys)
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 5 of 8"


def test_a_conductor_takes_a_seat_and_list_shows_it(where, capsys):
    assert run(where, "claim", "--kind", "conductor", "--card", "desks/a/docs/asks.md", "--pid", str(ALIVE)) == 0
    assert capsys.readouterr().out.splitlines()[0] == "ALLOW: seat 1 of 4"
    (name,) = os.listdir(where[0])
    with open(os.path.join(where[0], name), encoding="utf-8") as f:
        assert json.load(f)["kind"] == "conductor"
    for _ in range(3):
        claim(where, capsys)
    code, out = claim(where, capsys)
    assert code == 1
    assert out.strip() == "REFUSE: the cap of 4 is full (4 seats taken)"
    assert run(where, "list") == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "4 of 4 seats taken"
    assert "  conductor  project  desks/a/docs/asks.md" in out


def plant_a_take(where):
    me = os.path.basename(sys.executable)
    (where[1] / "docs" / "studio-processes.txt").write_text(f"not-a-real-app\n{me}\n", encoding="utf-8")
    return me


def test_the_lift_holds_only_while_the_studio_is_idle(where, capsys, no_gpu):
    (where[1] / "docs" / "cap-lifted.md").write_text("8 — eight while idle\n", encoding="utf-8")
    me = plant_a_take(where)
    for n in range(1, 5):  # under four, a take changes nothing
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 8"
    code, out = claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: the studio is on a take")
    assert me in out
    assert "the cap is 4 on a take and 8 only while idle (4 seats taken)" in out
    assert len(os.listdir(where[0])) == 4
    (where[1] / "docs" / "studio-processes.txt").write_text("not-a-real-app\n", encoding="utf-8")
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 5 of 8"


def test_a_take_leaves_seats_already_held_alone(where, capsys, no_gpu):
    (where[1] / "docs" / "cap-lifted.md").write_text("8\n", encoding="utf-8")
    for _ in range(6):
        claim(where, capsys)
    plant_a_take(where)
    code, out = claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: the studio is on a take")
    assert "(6 seats taken)" in out
    assert len(os.listdir(where[0])) == 6
    assert run(where, "list") == 0
    assert capsys.readouterr().out.splitlines()[0] == "6 of 8 seats taken"


def test_a_busy_graphics_card_holds_the_lift_to_four(where, capsys, monkeypatch):
    (where[1] / "docs" / "cap-lifted.md").write_text("8\n", encoding="utf-8")
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [12])
    for _ in range(4):
        claim(where, capsys)
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [80])
    code, out = claim(where, capsys)
    assert code == 1
    assert "graphics card 0 is 80% busy" in out


def test_a_broken_take_check_refuses_past_four(where, capsys, monkeypatch):
    (where[1] / "docs" / "cap-lifted.md").write_text("8\n", encoding="utf-8")
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [12])
    for _ in range(4):
        claim(where, capsys)

    def broken():
        raise RuntimeError("nvidia-smi failed")

    monkeypatch.setattr(cap_check, "gpu_loads", broken)
    code, out = claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: could not tell whether the studio is on a take")


def test_no_lift_file_is_four_on_a_take_as_today(where, capsys, no_gpu):
    plant_a_take(where)
    for n in range(1, 5):
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 4"
    code, out = claim(where, capsys)
    assert code == 1
    assert out.strip() == "REFUSE: the cap of 4 is full (4 seats taken)"


def test_heavy_is_refused_while_a_studio_process_runs(where, capsys, no_gpu):
    me = os.path.basename(sys.executable)
    (where[1] / "docs" / "studio-processes.txt").write_text(f"not-a-real-app\n{me}\n", encoding="utf-8")
    code, out = claim(where, capsys, heavy=True)
    assert code == 1
    assert out.startswith("REFUSE: heavy work waits; the studio is on a take")
    assert me in out
    assert not os.path.isdir(where[0]) or not os.listdir(where[0])


def test_heavy_is_allowed_with_no_file_and_no_nvidia_smi(where, capsys, no_gpu):
    code, out = claim(where, capsys, heavy=True)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 1 of 4"


def test_heavy_is_allowed_when_the_listed_studio_is_not_running(where, capsys, no_gpu):
    (where[1] / "docs" / "studio-processes.txt").write_text("not-a-real-app.exe\n", encoding="utf-8")
    code, out = claim(where, capsys, heavy=True)
    assert code == 0


def test_a_busy_graphics_card_is_a_take(where, capsys, monkeypatch):
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [12, 45])
    code, out = claim(where, capsys, heavy=True)
    assert code == 1
    assert "graphics card 1 is 45% busy" in out
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [30])
    code, out = claim(where, capsys, heavy=True)
    assert code == 0


def test_a_light_claim_ignores_the_studio(where, capsys, monkeypatch):
    monkeypatch.setattr(cap_check, "gpu_loads", lambda: [99])
    code, out = claim(where, capsys)
    assert code == 0


# ---- the lock and the start time ------------------------------------------

RUNNER = r"""
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("cap_check", sys.argv[1])
cap_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap_check)
open(sys.argv[2], "w").close()
while not os.path.exists(sys.argv[3]):
    pass  # every claimer waits here, so all eight go at the same instant
sys.exit(cap_check.main(["cap_check.py"] + sys.argv[4:]))
"""


def test_eight_claims_at_once_allow_exactly_four(where, tmp_path):
    seats, project = where
    go = tmp_path / "go"
    tool = os.path.join(HERE, "..", "cap_check.py")
    claimers = []
    for n in range(8):
        args = [sys.executable, "-B", "-c", RUNNER, tool, str(tmp_path / f"ready{n}"), str(go),
                "--seats", seats, "--project", str(project),
                "claim", "--kind", "worker", "--card", "docs/cards/x.md", "--pid", str(ALIVE)]
        claimers.append(subprocess.Popen(args, stdout=subprocess.PIPE, text=True))
    deadline = time.monotonic() + 60
    while not all((tmp_path / f"ready{n}").exists() for n in range(8)):
        assert time.monotonic() < deadline, "the claimers never got ready"
        time.sleep(0.01)
    go.write_text("")
    results = [(p.wait(timeout=60), p.stdout.read()) for p in claimers]
    allowed = [out for code, out in results if code == 0]
    refused = [out for code, out in results if code == 1]
    assert len(allowed) == 4 and len(refused) == 4, results
    assert sorted(out.splitlines()[0] for out in allowed) == [f"ALLOW: seat {n} of 4" for n in range(1, 5)]
    assert all(out.startswith("REFUSE: the cap of 4 is full (4 seats taken)") for out in refused)
    names = os.listdir(seats)
    assert len(names) == 4 and all(n.endswith(".json") for n in names)  # no lock left behind


def plant_claim(where, **data):
    os.makedirs(where[0], exist_ok=True)
    data = {"project": "project", "card": "docs/cards/old.md", "kind": "worker",
            "time": "2026-10-06T09:00:00", **data}
    with open(os.path.join(where[0], "planted.json"), "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_a_claim_records_its_process_start_time(where, capsys):
    claim(where, capsys)
    (name,) = os.listdir(where[0])
    with open(os.path.join(where[0], name), encoding="utf-8") as f:
        data = json.load(f)
    assert data["started"] is not None
    assert data["started"] == cap_check.process_started(ALIVE)


def test_a_live_id_with_a_wrong_start_time_is_not_counted(where, capsys):
    started = cap_check.process_started(ALIVE)
    assert started is not None
    plant_claim(where, pid=ALIVE, started=started + 1)  # an older process that had this id
    assert run(where, "list") == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "0 of 4 seats taken"
    assert "1 dead claim(s) not counted" in out
    code, out = claim(where, capsys)
    assert out.splitlines()[0] == "ALLOW: seat 1 of 4"
    assert "planted.json" not in os.listdir(where[0])


def test_a_claim_written_before_start_times_is_judged_by_its_id(where, capsys):
    plant_claim(where, pid=ALIVE)  # no start time in the file
    assert run(where, "list") == 0
    assert capsys.readouterr().out.splitlines()[0] == "1 of 4 seats taken"
    code, out = claim(where, capsys)
    assert out.splitlines()[0] == "ALLOW: seat 2 of 4"


def test_a_stale_lock_is_cleared_and_the_next_claim_succeeds(where, capsys):
    os.makedirs(where[0])
    lock = os.path.join(where[0], cap_check.LOCK_NAME)
    with open(lock, "w", encoding="utf-8") as f:
        f.write("left by a claim that died")
    old = time.time() - cap_check.LOCK_STALE - 5
    os.utime(lock, (old, old))
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 1 of 4"
    assert not os.path.exists(lock)


def test_a_fresh_lock_is_waited_for_not_cleared(where, capsys, monkeypatch):
    monkeypatch.setattr(cap_check, "LOCK_WAIT", 0.3)
    os.makedirs(where[0])
    lock = os.path.join(where[0], cap_check.LOCK_NAME)
    with open(lock, "w", encoding="utf-8") as f:
        f.write("a claim still counting")
    code, out = claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: the seats folder stayed locked")
    assert os.listdir(where[0]) == [cap_check.LOCK_NAME]


# ---- a claim finds its own claude.exe -------------------------------------
# The process walk is faked: a made-up tree of {id: (parent id, name, start
# time)}, with the walk starting at this test's own id. Every claim still
# goes to the test's own seats folder.

@pytest.fixture
def tree(monkeypatch):
    def plant(processes):
        monkeypatch.setattr(cap_check, "process_table",
                            lambda: {pid: (parent, name) for pid, (parent, name, _) in processes.items()})
        monkeypatch.setattr(cap_check, "pid_alive", lambda pid: pid in processes)
        monkeypatch.setattr(cap_check, "process_started",
                            lambda pid: processes[pid][2] if pid in processes else None)
    return plant


def own_claim(where, capsys, kind="worker"):
    code = run(where, "claim", "--kind", kind, "--card", "docs/cards/x.md")
    return code, capsys.readouterr().out


def the_claim(where):
    (name,) = os.listdir(where[0])
    with open(os.path.join(where[0], name), encoding="utf-8") as f:
        return json.load(f)


def test_no_pid_takes_the_nearest_claude_up_the_chain(where, capsys, tree):
    tree({ALIVE: (300, "python.exe", 3), 300: (200, "claude.exe", 2), 200: (100, "claude.exe", 1),
          100: (0, "t3.exe", 0)})
    code, out = own_claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 1 of 4"
    data = the_claim(where)
    assert data["pid"] == 300
    assert data["started"] == 2


def test_no_pid_walks_two_levels_up(where, capsys, tree):
    tree({ALIVE: (410, "python3.11.exe", 4), 410: (400, "bash.exe", 3), 400: (300, "Claude.EXE", 2),
          300: (0, "t3.exe", 1)})
    code, out = own_claim(where, capsys)
    assert code == 0
    data = the_claim(where)
    assert data["pid"] == 400
    assert data["started"] == 2


def test_no_claude_above_is_a_refuse_that_says_pass_pid(where, capsys, tree):
    tree({ALIVE: (410, "python.exe", 4), 410: (400, "bash.exe", 3), 400: (300, "cmd.exe", 2),
          300: (0, "explorer.exe", 1)})
    code, out = own_claim(where, capsys)
    assert code == 1
    assert out.startswith("REFUSE: no claude.exe above this process")
    assert "--pid" in out
    assert not os.path.isdir(where[0]) or not os.listdir(where[0])


def test_pid_still_wins_over_the_walk(where, capsys, tree):
    tree({ALIVE: (300, "python.exe", 3), 300: (0, "claude.exe", 2), 555: (0, "claude.exe", 5)})
    assert run(where, "claim", "--kind", "worker", "--card", "x.md", "--pid", "555") == 0
    assert the_claim(where)["pid"] == 555


def test_a_checker_claims_its_own_claude_and_counts_toward_the_cap(where, capsys, tree):
    # the parent's claude.exe (300) holds a seat; the checker is a T3 child task
    # with its own claude.exe (301) under t3.exe, its walk starting at this test's id
    tree({ALIVE: (420, "python.exe", 6), 420: (301, "bash.exe", 5), 301: (100, "claude.exe", 4),
          300: (100, "claude.exe", 2), 100: (0, "t3.exe", 1)})
    assert run(where, "claim", "--kind", "master", "--card", "docs/run.md", "--pid", "300") == 0
    capsys.readouterr()
    code, out = own_claim(where, capsys, kind="checker")
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 2 of 4"
    claim_id = out.splitlines()[1].split()[1]
    assert "-checker-301-" in claim_id
    for _ in range(2):
        assert own_claim(where, capsys)[0] == 0
    code, out = own_claim(where, capsys, kind="checker")
    assert code == 1
    assert out.strip() == "REFUSE: the cap of 4 is full (4 seats taken)"
