# cap_check.py: may one more agent start now?
#
# When it runs
#   The master runs it before any worker, checker or reader starts, every
#   time, one claim per agent. ALLOW means start it. REFUSE is a stop:
#   that agent does not start, and the master waits or asks him. It is
#   never a question to argue with or a step to work around.
#   The master claims its own seat (--kind master) when it opens a run and
#   releases it at the wrap; each desk conductor claims its own seat
#   (--kind conductor) the same way.
#   Each agent claims its own seat as its first act, from inside its own
#   thread, with no --pid: the claim finds the agent's own claude.exe
#   itself. A checker run as a T3 child task claims a seat of its own the
#   same way, so checkers count like any agent (call 6 of the 0.5.0
#   design). In run 2 the master looked each id up by hand, and checkers
#   ran inside their parent's seat, uncounted.
#
# What it holds
#   1. The cap. At most 4 agents at once beside a take, checkers counted
#      (his rulings, 5 Oct), masters and desk conductors counted (his
#      rulings, 6 Oct).
#   2. His lift, for an idle studio only. Only his word lifts the cap: the
#      master writes his words and a number into foundry-north-website/docs/cap-lifted.md,
#      and the first number in that file is the cap while the studio is
#      idle. While it is on a take the cap is 4 whatever the file says: a
#      claim for a fifth seat is refused, naming the take. Claims already
#      held are left alone; no new one starts until under four. His ruling,
#      6 Oct: "eight while the studio is idle; four again the moment a take
#      starts", and his "No cap" later that day kept four beside a take.
#      No file means 4, take or not.
#   3. Heavy work waits for an idle studio. A claim marked --heavy is
#      refused while the studio is on a take.
#
# Where the seats are
#   One machine-wide folder, %LOCALAPPDATA%\agentic-meta\seats\, so two
#   projects on one machine share the one cap. Each claim is one small
#   JSON file: the project, the card, the kind, the process id, the
#   process's start time, the time.
#   A claim is alive only while a process with its id is running and
#   started at the time the claim recorded. Windows reuses process ids, so
#   an id alone could make a dead claim, whose id a new process has taken,
#   read as alive until released (parked by the first cap-check worker,
#   6 Oct). A claim written before start times were kept (none in its
#   file) is judged by its id alone. A dead claim is not counted, and the
#   next claim deletes it.
#   claim holds a lock (claim.lock in the seats folder) while it counts
#   and writes, so of many claims made at once no more than the cap are
#   allowed. Without it, two claims at the same instant could both see a
#   free seat (parked by the same worker). With several T3 threads started
#   in a burst, both faults happen for real. A lock older than 10 seconds
#   was left by a claim that died, and the next claim clears it, so one
#   crash never blocks every later claim.
#
# "On a take" means
#   nvidia-smi reports a graphics card busier than 30 per cent, or a
#   process named in foundry-north-website/docs/studio-processes.txt (one name per
#   line; the file may be absent) is running. No nvidia-smi and no such
#   file means idle.
#   The 30 is a guess, not a measurement. The road desk's measured number
#   replaces it.
#
# How to run it (from the project's folder)
#   python tools/cap_check.py claim --kind worker|checker|reader|master|conductor --card <path> [--heavy] [--pid <id>]
#   python tools/cap_check.py release <claim-id>
#   python tools/cap_check.py list
#   --pid is the agent's process id; left out, it is the nearest claude.exe
#   above the process that ran this tool, found by walking up its parents.
#   No claude.exe above it is a REFUSE that says to pass --pid. --seats <folder> and --project <folder> point it elsewhere
#   (tests use --seats so they never touch the machine-wide folder).
#   claim prints ALLOW (exit 0) or REFUSE (exit 1). It never stops,
#   starts or signals any process.
#
# Python 3 standard library only.

import argparse
import datetime
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time

CAP = 4
GPU_BUSY_OVER = 30  # a guess; the road desk's measured number replaces it
KINDS = ("worker", "checker", "reader", "master", "conductor")
LOCK_NAME = "claim.lock"
LOCK_STALE = 10  # seconds; a lock this old was left by a claim that died
LOCK_WAIT = 20  # seconds a claim waits for the lock before it refuses


def default_seats():
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "agentic-meta", "seats")


# ---- is a process alive ---------------------------------------------------

def pid_alive(pid):
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel32.OpenProcess(0x1000, False, pid)  # query only
        if not handle:
            return ctypes.get_last_error() == 5  # access denied: it exists
        try:
            code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return True
            return code.value == 259  # still running
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)  # signal 0 sends nothing; it only asks
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def process_started(pid):
    """When the process with this id started, as a whole number; None when
    it cannot be read (no such process, no access, or no way on this system)."""
    if pid <= 0:
        return None
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel32.OpenProcess(0x1000, False, pid)  # query only
        if not handle:
            return None
        try:
            times = [wintypes.FILETIME() for _ in range(4)]
            if not kernel32.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
                return None
            return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        finally:
            kernel32.CloseHandle(handle)
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as f:
            return int(f.read().rsplit(")", 1)[1].split()[19])  # field 22, starttime
    except (OSError, ValueError, IndexError):
        return None


def process_table():
    """Every running process as {id: (parent id, name)}."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Entry(ctypes.Structure):  # PROCESSENTRY32W
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                        ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        kernel32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        kernel32.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(Entry))
        kernel32.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(Entry))
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        snap = kernel32.CreateToolhelp32Snapshot(0x2, 0)  # every process
        if not snap or snap == ctypes.c_void_p(-1).value:
            raise OSError(f"could not list processes (error {ctypes.get_last_error()})")
        table = {}
        try:
            entry = Entry()
            entry.dwSize = ctypes.sizeof(Entry)
            more = kernel32.Process32FirstW(snap, ctypes.byref(entry))
            while more:
                table[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile)
                more = kernel32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            kernel32.CloseHandle(snap)
        return table
    out = subprocess.run(["ps", "-A", "-o", "pid=,ppid=,comm="],
                         capture_output=True, text=True, errors="replace").stdout
    table = {}
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3:
            table[int(parts[0])] = (int(parts[1]), os.path.basename(parts[2].strip()))
    return table


def own_claude(table, start):
    """The id of the nearest claude.exe above process start, or None."""
    seen, pid = {start}, start
    while True:
        parent = table.get(pid, (0, ""))[0]
        if parent <= 0 or parent in seen or parent not in table:
            return None
        if plain(table[parent][1]) == "claude":
            return parent
        seen.add(parent)
        pid = parent


def claim_alive(data):
    pid = int(data["pid"])
    if not pid_alive(pid):
        return False
    if data.get("started") is None:  # written before start times were kept
        return True
    now = process_started(pid)
    return now is None or now == data["started"]  # unreadable: judged by the id


# ---- the seats ------------------------------------------------------------

def read_claims(seats):
    """Every claim in the folder as (id, data or None if unreadable)."""
    if not os.path.isdir(seats):
        return []
    claims = []
    for name in sorted(os.listdir(seats)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(seats, name), encoding="utf-8") as f:
                data = json.load(f)
            int(data["pid"])
        except (OSError, ValueError, KeyError, TypeError):
            data = None  # unreadable: counted, so a broken file never frees a seat
        claims.append((name[:-5], data))
    return claims


def split_live(claims):
    live, dead = [], []
    for cid, data in claims:
        (live if data is None or claim_alive(data) else dead).append((cid, data))
    return live, dead


def take_lock(seats):
    """Hold the seats folder's lock; returns its token, or None if it stayed
    held for LOCK_WAIT seconds by a claim still alive."""
    path = os.path.join(seats, LOCK_NAME)
    token = secrets.token_hex(8)
    deadline = time.monotonic() + LOCK_WAIT
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, PermissionError):  # Windows: a lock being deleted
            try:
                if time.time() - os.stat(path).st_mtime > LOCK_STALE:
                    os.remove(path)  # left by a claim that died
                    continue
            except (FileNotFoundError, PermissionError):
                pass  # gone or going; try again
            if time.monotonic() > deadline:
                return None
            time.sleep(0.02)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(token)
        return token


def drop_lock(seats, token):
    path = os.path.join(seats, LOCK_NAME)
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() != token:
                return  # ours was cleared as stale; this one is another claim's
        os.remove(path)
    except FileNotFoundError:
        pass


def read_cap(project):
    path = os.path.join(project, "docs", "cap-lifted.md")
    if not os.path.isfile(path):
        return CAP
    with open(path, encoding="utf-8", errors="replace") as f:
        found = re.search(r"\d+", f.read())
    return int(found.group()) if found else CAP


# ---- is the studio on a take ----------------------------------------------

def gpu_loads():
    """Each card's load in per cent; [] when there is no nvidia-smi."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return []
    done = subprocess.run(
        [exe, "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=30,
    )
    if done.returncode != 0:
        raise RuntimeError(f"nvidia-smi failed: {done.stderr.strip()[:80]}")
    return [int(line.strip()) for line in done.stdout.splitlines() if line.strip()]


def running_names():
    """The names of every running process, lower case, without .exe."""
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/fo", "csv", "/nh"],
                             capture_output=True, text=True, errors="replace").stdout
        names = [line.split('","')[0].strip('"') for line in out.splitlines() if line.strip()]
    else:
        out = subprocess.run(["ps", "-A", "-o", "comm="],
                             capture_output=True, text=True, errors="replace").stdout
        names = [os.path.basename(line.strip()) for line in out.splitlines() if line.strip()]
    return {plain(n) for n in names}


def plain(name):
    name = name.strip().lower()
    return name[:-4] if name.endswith(".exe") else name


def studio_take(project):
    """Why the studio is on a take, or None when it is idle."""
    path = os.path.join(project, "docs", "studio-processes.txt")
    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            wanted = [line.strip() for line in f if line.strip()]
        if wanted:
            running = running_names()
            for name in wanted:
                if plain(name) in running:
                    return f"{name} is running"
    for i, load in enumerate(gpu_loads()):
        if load > GPU_BUSY_OVER:
            return f"graphics card {i} is {load}% busy (over {GPU_BUSY_OVER})"
    return None


# ---- the three commands ---------------------------------------------------

def claim(args):
    seats, project = args.seats, os.path.abspath(args.project)
    pid = args.pid if args.pid is not None else own_claude(process_table(), os.getpid())
    if pid is None:
        print("REFUSE: no claude.exe above this process; pass --pid <the agent's process id>")
        return 1
    cap = read_cap(project)
    why, broken = None, None
    if args.heavy or cap > CAP:  # read before the lock: the take test can take seconds
        try:
            why = studio_take(project)
        except Exception as err:  # a broken check must never read as idle
            broken = err
    if args.heavy:
        if broken is not None:
            print(f"REFUSE: could not tell whether the studio is on a take ({broken})")
            return 1
        if why:
            print(f"REFUSE: heavy work waits; the studio is on a take ({why})")
            return 1
    os.makedirs(seats, exist_ok=True)
    token = take_lock(seats)
    if token is None:
        print(f"REFUSE: the seats folder stayed locked for {LOCK_WAIT} seconds "
              f"({os.path.join(seats, LOCK_NAME)})")
        return 1
    try:
        return claim_a_seat(args, pid, seats, project, cap, why, broken)
    finally:
        drop_lock(seats, token)


def claim_a_seat(args, pid, seats, project, cap, why, broken):
    """The count and the write, run only while holding the lock."""
    live, dead = split_live(read_claims(seats))
    for cid, _ in dead:
        try:
            os.remove(os.path.join(seats, cid + ".json"))
        except FileNotFoundError:
            pass
    if cap > CAP and len(live) >= CAP:  # his lift holds only on an idle studio
        if broken is not None:
            print(f"REFUSE: could not tell whether the studio is on a take ({broken})")
            return 1
        if why:
            print(f"REFUSE: the studio is on a take ({why}); the cap is {CAP} on a take "
                  f"and {cap} only while idle ({len(live)} seats taken)")
            return 1
    if len(live) >= cap:
        print(f"REFUSE: the cap of {cap} is full ({len(live)} seats taken)")
        return 1
    now = datetime.datetime.now()
    cid = f"{now:%Y%m%d-%H%M%S}-{args.kind}-{pid}-{secrets.token_hex(2)}"
    data = {
        "project": os.path.basename(project),
        "card": args.card,
        "kind": args.kind,
        "pid": pid,
        "started": process_started(pid),
        "time": now.isoformat(timespec="seconds"),
    }
    with open(os.path.join(seats, cid + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"ALLOW: seat {len(live) + 1} of {cap}")
    print(f"claim: {cid}  (when the agent ends: python tools/cap_check.py release {cid})")
    return 0


def release(args):
    path = os.path.join(args.seats, args.claim_id + ".json")
    if os.path.basename(args.claim_id) != args.claim_id or not os.path.isfile(path):
        print(f"NOT FOUND: no claim {args.claim_id} in {args.seats}")
        return 1
    os.remove(path)
    print(f"RELEASED: {args.claim_id}")
    return 0


def list_seats(args):
    live, dead = split_live(read_claims(args.seats))
    cap = read_cap(os.path.abspath(args.project))
    print(f"{len(live)} of {cap} seats taken")
    for cid, data in live:
        if data is None:
            print(f"  {cid}  (unreadable; counted until released)")
        else:
            print(f"  {cid}  {data.get('kind')}  {data.get('project')}  "
                  f"{data.get('card')}  pid {data['pid']}  since {data.get('time')}")
    if dead:
        print(f"({len(dead)} dead claim(s) not counted; the next claim deletes them)")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(prog="cap_check.py", description="May one more agent start now?")
    parser.add_argument("--seats", default=default_seats(), help="the seats folder")
    parser.add_argument("--project", default=os.getcwd(), help="the project folder (default: here)")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("claim")
    c.add_argument("--kind", required=True, choices=KINDS)
    c.add_argument("--card", required=True)
    c.add_argument("--heavy", action="store_true")
    c.add_argument("--pid", type=int)
    r = sub.add_parser("release")
    r.add_argument("claim_id")
    sub.add_parser("list")
    for p in (c, r, sub.choices["list"]):
        p.add_argument("--seats", default=argparse.SUPPRESS)
        p.add_argument("--project", default=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 1
    try:
        return {"claim": claim, "release": release, "list": list_seats}[args.command](args)
    except Exception as err:  # a broken check must never read as a pass
        print(f"REFUSE: the check itself failed ({type(err).__name__}: {err})")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
