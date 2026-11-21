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


@pytest.fixture(autouse=True)
def outside_git(tmp_path, monkeypatch):
    # git looks no higher than the test's own folder, so a temp folder that
    # happens to sit inside some repository is still no repository here
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))


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
    # the master's own process, not this one: a worker from the master's process is refused (rule 32)
    assert run(where, "claim", "--kind", "master", "--card", "docs/run.md", "--pid", str(os.getppid())) == 0
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


# ---- the signed number of workers -----------------------------------------

def sign(main, workers, run=7):
    """A signed plan in main's docs/runs/<run>; workers None leaves the line out."""
    plan = main / "docs" / "runs" / str(run) / "plan-signed.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    line = "" if workers is None else f"Workers at once: {workers}\n"
    plan.write_text(f"# Plan for run {run}\n\n## Agents\nThree workers at once, in prose.\n{line}\n"
                    "## His words\n\"go\"\n", encoding="utf-8")


def test_a_signed_plan_of_three_refuses_the_fourth_worker(where, capsys):
    sign(where[1], 3)
    for n in range(1, 4):
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 4"
    code, out = claim(where, capsys)
    assert code == 1
    assert out.strip() == ("REFUSE: the signed plan (docs/runs/7/plan-signed.md) signs 3 workers at once, "
                           "and 3 are running")
    assert len(os.listdir(where[0])) == 3


def test_a_signed_plan_of_three_with_two_running_allows_the_third(where, capsys):
    sign(where[1], 3)
    for _ in range(2):
        claim(where, capsys)
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 3 of 4"


def test_the_newest_signed_plan_is_the_one_read(where, capsys):
    sign(where[1], 1, run=6)
    sign(where[1], 2, run=10)
    for _ in range(2):
        assert claim(where, capsys)[0] == 0
    code, out = claim(where, capsys)
    assert code == 1
    assert "(docs/runs/10/plan-signed.md) signs 2 workers" in out


def test_a_signed_plan_with_no_line_allows_past_three_as_today(where, capsys):
    sign(where[1], None)
    sign(where[1], "<n>", run=8)  # the blank's placeholder, left in
    for n in range(1, 5):
        code, out = claim(where, capsys)
        assert code == 0
        assert out.splitlines()[0] == f"ALLOW: seat {n} of 4"
    code, out = claim(where, capsys)
    assert out.strip() == "REFUSE: the cap of 4 is full (4 seats taken)"


def test_a_signed_line_outside_agents_binds_nobody(where, capsys):
    plan = where[1] / "docs" / "runs" / "7" / "plan-signed.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("## The path\nWorkers at once: 1\n\n## Agents\nfour\n", encoding="utf-8")
    for _ in range(2):
        assert claim(where, capsys)[0] == 0


def test_a_checker_or_a_master_is_not_refused_by_the_signed_line(where, capsys):
    sign(where[1], 1)
    assert claim(where, capsys)[0] == 0
    code, out = claim(where, capsys)
    assert code == 1 and "signs 1 workers at once, and 1 are running" in out
    for kind in ("checker", "master", "conductor"):
        assert run(where, "claim", "--kind", kind, "--card", "x.md", "--pid", str(ALIVE)) == 0
        assert capsys.readouterr().out.startswith("ALLOW:")


def plant_named(where, name, **data):
    os.makedirs(where[0], exist_ok=True)
    data = {"card": "docs/cards/old.md", "kind": "worker", "pid": ALIVE,
            "time": "2026-10-06T09:00:00", **data}
    with open(os.path.join(where[0], name + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_a_signed_count_matches_an_old_claim_by_its_project_name(where, capsys):
    sign(where[1], 2)
    plant_named(where, "old-same", project="project")  # no main checkout in it
    plant_named(where, "old-other", project="another-project")
    code, out = claim(where, capsys)
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 3 of 4"
    code, out = claim(where, capsys)
    assert code == 1
    assert "signs 2 workers at once, and 2 are running" in out


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def a_repository(folder):
    folder.mkdir(parents=True)
    git(folder, "init", "-q")
    git(folder, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
    return folder


def test_two_worktrees_of_one_repository_count_together(tmp_path, capsys):
    seats = str(tmp_path / "seats")
    main = a_repository(tmp_path / "studio")
    one, two = tmp_path / "task-studio-one", tmp_path / "task-studio-two"
    git(main, "worktree", "add", "-q", "-b", "one", str(one))
    git(main, "worktree", "add", "-q", "-b", "two", str(two))
    other = a_repository(tmp_path / "other")
    sign(main, 2)
    sign(other, 2)

    def claim_in(project):
        code = cap_check.main(["cap_check.py", "--seats", seats, "--project", str(project), "claim",
                               "--kind", "worker", "--card", "x.md", "--pid", str(ALIVE)])
        return code, capsys.readouterr().out

    assert claim_in(other)[0] == 0  # another repository's worker
    assert claim_in(one)[0] == 0
    assert claim_in(two)[0] == 0
    code, out = claim_in(main)
    assert code == 1
    assert out.strip() == ("REFUSE: the signed plan (docs/runs/7/plan-signed.md) signs 2 workers at once, "
                           "and 2 are running")
    code, out = claim_in(one)
    assert code == 1
    mains = set()
    for name in os.listdir(seats):
        with open(os.path.join(seats, name), encoding="utf-8") as f:
            mains.add(os.path.normcase(json.load(f)["main"]))
    assert len(mains) == 2  # the studio's two worktrees name one main checkout
    assert os.path.normcase(cap_check.main_checkout(str(two))) == os.path.normcase(cap_check.main_checkout(str(main)))
    assert claim_in(other)[0] == 0  # the other repository still has a seat of its signed two


def test_no_repository_or_no_git_makes_the_project_its_own_worktree_main(where, monkeypatch):
    project = str(where[1])
    assert cap_check.main_checkout(project) == project

    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(cap_check.subprocess, "run", no_git)
    assert cap_check.main_checkout(project) == project


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


# ---- the usage window -----------------------------------------------------
# The reading is planted in window.py's form beside the test's own seats
# folder (or where --window names), never in the machine-wide folder.

RESETS = int(time.time()) + 3 * 3600


def window(where, word, percent, age=60, resets_at=RESETS, path=None):
    path = path or os.path.join(os.path.dirname(where[0]), "window.json")
    read_at = int(time.time()) - age
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"read_at": read_at, "five_hour": {"percent": percent, "resets_at": resets_at},
                   "seven_day": {"percent": 4, "resets_at": resets_at + 86400},
                   "word": word, "previous": None}, f)
    return cap_check.clock(read_at)


def claim_kind(where, capsys, kind, *more):
    code = run(where, *more, "claim", "--kind", kind, "--card", "docs/cards/x.md", "--pid", str(ALIVE))
    return code, capsys.readouterr().out


def claim_id(out):
    return out.splitlines()[1].split()[1]


def test_a_fresh_wrap_now_window_refuses_a_worker_and_a_checker_and_allows_a_master(where, capsys):
    read = window(where, "wrap now", 96)
    for kind in ("worker", "checker"):
        code, out = claim_kind(where, capsys, kind)
        assert code == 1
        assert out.strip() == (f"REFUSE: the usage window reads 96% (wrap now, read {read}); it resets at "
                               f"{cap_check.clock(RESETS)} this computer; no new agent until then")
    assert not os.path.isdir(where[0]) or not os.listdir(where[0])  # nothing written
    code, out = claim_kind(where, capsys, "master")
    assert code == 0
    assert out.splitlines()[0] == "ALLOW: seat 1 of 4"


def test_an_old_wrap_now_window_allows(where, capsys):
    window(where, "wrap now", 96, age=30 * 60)
    assert claim_kind(where, capsys, "worker")[0] == 0


def test_no_window_file_allows(where, capsys):
    assert claim_kind(where, capsys, "worker")[0] == 0
    with open(os.path.join(os.path.dirname(where[0]), "window.json"), "w", encoding="utf-8") as f:
        f.write('{"word": "wrap now"}')  # not window.py's form
    assert claim_kind(where, capsys, "worker")[0] == 0


def test_a_slow_down_window_marks_three_refuses_a_fourth_allows_one_after_a_release(where, capsys):
    ids = [claim_id(claim_kind(where, capsys, "worker")[1]) for _ in range(3)]
    window(where, "slow down", 80)
    code, out = claim_kind(where, capsys, "worker")
    assert code == 1
    assert out.strip() == ("REFUSE: the usage window reads 80% (slow down); this project held 3 agents "
                           "at 75% and holds 3; one new agent only as one finishes")
    assert len(os.listdir(where[0])) == 3
    with open(os.path.join(os.path.dirname(where[0]), "window-marks.json"), encoding="utf-8") as f:
        assert [m["mark"] for m in json.load(f)] == [3]
    run(where, "release", ids[0])
    capsys.readouterr()
    assert claim_kind(where, capsys, "checker")[0] == 0
    code, out = claim_kind(where, capsys, "worker")
    assert code == 1
    assert "held 3 agents at 75% and holds 3" in out
    assert claim_kind(where, capsys, "master")[0] == 0  # a master is never refused for the window


def test_a_slow_down_window_mark_of_zero_allows_one_claim_and_refuses_a_second(where, tmp_path, capsys):
    other = tmp_path / "elsewhere"
    other.mkdir()
    reading = str(other / "window.json")
    window(where, "slow down", 75, path=reading)
    code, out = claim_kind(where, capsys, "worker", "--window", reading)
    assert code == 0
    first = claim_id(out)
    code, out = claim_kind(where, capsys, "worker", "--window", reading)
    assert code == 1
    assert "held 0 agents at 75% and holds 1" in out
    assert os.path.isfile(other / "window-marks.json")  # the mark lives beside the reading it names
    run(where, "release", first)
    capsys.readouterr()
    assert claim_kind(where, capsys, "worker", "--window", reading)[0] == 0


def test_another_projects_claims_do_not_count_against_the_window_mark(where, tmp_path, capsys):
    ids = [claim_id(claim_kind(where, capsys, "worker")[1]) for _ in range(2)]
    plant_named(where, "other-one", project="another", main=str(tmp_path / "another"))
    window(where, "slow down", 85)
    code, out = claim_kind(where, capsys, "worker")
    assert code == 1
    assert "held 2 agents at 75% and holds 2" in out
    os.remove(os.path.join(where[0], "other-one.json"))
    plant_named(where, "other-two", project="another", main=str(tmp_path / "another"))
    run(where, "release", ids[0])
    capsys.readouterr()
    assert claim_kind(where, capsys, "worker")[0] == 0  # 1 of this project's 2, the other's not counted


def test_a_new_resets_at_starts_a_new_window_mark(where, capsys):
    ids = [claim_id(claim_kind(where, capsys, "worker")[1]) for _ in range(3)]
    gone = int(time.time()) - 60  # a reset that has just passed
    window(where, "slow down", 90, resets_at=gone)
    assert claim_kind(where, capsys, "worker")[0] == 1  # marks 3
    for cid in ids[:2]:
        run(where, "release", cid)
    capsys.readouterr()
    assert claim_kind(where, capsys, "worker")[0] == 0  # 1 of 3; now 2
    window(where, "slow down", 76)  # the next five hours
    code, out = claim_kind(where, capsys, "worker")
    assert code == 1
    assert "held 2 agents at 75% and holds 2" in out
    with open(os.path.join(os.path.dirname(where[0]), "window-marks.json"), encoding="utf-8") as f:
        assert [(m["resets_at"], m["mark"]) for m in json.load(f)] == [(RESETS, 2)]  # the past one dropped


def test_list_prints_the_window_line(where, capsys):
    claim_kind(where, capsys, "worker")
    read = window(where, "slow down", 80)
    assert run(where, "list") == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "1 of 4 seats taken"
    assert out[-1] == f"window: 80% · slow down · read {read}"
    window(where, "slow down", 80, age=25 * 60)
    assert run(where, "list") == 0
    assert capsys.readouterr().out.splitlines()[-1] == "window: no recent reading"


# ---- a worker is its own thread (tracks.md rule 32) -----------------------

def master_claim(where, capsys, pid=ALIVE):
    assert run(where, "claim", "--kind", "master", "--card", "docs/runs/7/run.md", "--pid", str(pid)) == 0
    return claim_id(capsys.readouterr().out)


def test_a_worker_claim_from_the_masters_process_is_refused(where, capsys):
    held = master_claim(where, capsys)
    code, out = claim(where, capsys)
    assert code == 1
    assert out.strip() == ("REFUSE: a worker is its own thread (tracks.md rule 32); "
                           f"this claim resolves to the master's own session ({held})")
    assert os.listdir(where[0]) == [held + ".json"]  # nothing written


def test_a_checker_reader_or_conductor_from_the_masters_process_is_allowed(where, capsys):
    master_claim(where, capsys)
    for kind in ("checker", "reader", "conductor"):
        code, out = claim_kind(where, capsys, kind)
        assert code == 0 and out.startswith("ALLOW:")


def test_a_worker_walking_up_to_the_masters_claude_is_refused_and_its_own_thread_allowed(where, capsys, tree):
    tree({ALIVE: (420, "python.exe", 6), 420: (300, "bash.exe", 5), 300: (100, "claude.exe", 2),
          301: (100, "claude.exe", 4), 100: (0, "t3.exe", 1)})
    held = master_claim(where, capsys, pid=300)
    code, out = own_claim(where, capsys)
    assert code == 1 and f"master's own session ({held})" in out
    assert run(where, "claim", "--kind", "worker", "--card", "x.md", "--pid", "301") == 0  # its own thread


def test_a_dead_master_claim_does_not_refuse_a_worker(where, capsys):
    master_claim(where, capsys, pid=DEAD)  # a master that has ended; its id may be taken again
    code, out = claim(where, capsys, pid=DEAD)
    assert code == 0 and out.startswith("ALLOW:")
