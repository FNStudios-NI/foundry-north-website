# Tests for act_check.py: what each check catches, what it must not catch,
# the switches, the counter and the hook's never-break promise, and the
# session-log reader. Every test that runs the hook points LOCALAPPDATA and
# CLAUDE_PROJECT_DIR at its own temp folder, so nothing touches the real
# counter or any project.

import datetime
import importlib.util
import json
import os
import subprocess
import sys

import pytest

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(TOOLS, "act_check.py")
_spec = importlib.util.spec_from_file_location("act_check_for_tests", TOOL)
ac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ac)


# ---- heredoc-write ------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "cat > \"$S/notes.md\" <<'EOF'\nline one\nEOF",
    "cat <<EOF > out.txt\nhello\nEOF",
    "cat <<-EOF >> log.txt\n\thello\n\tEOF",
    "cat <<'EOF' | tee notes.md\nbody with > and ' marks\nEOF",
    "echo probe > \"$S/probe.txt\"",
    "printf 'a\\nb\\n' >> f.txt",
    "cd x && echo hi > y.txt",
    "git commit -m \"$(cat <<'EOF'\nThe message.\nEOF\n)\" -- a.py",
])
def test_heredoc_write_catches_bash(command):
    assert ac.find(command, "bash") == ["heredoc-write"]


@pytest.mark.parametrize("command", [
    "echo probe > \"$env:TEMP\\probe.txt\"",
    "Write-Output 'x' >> f.txt",
    "@'\nline\n'@ | Set-Content notes.md",
    "Set-Content -Path notes.md -Value @'\nline\n'@",
    "echo hi | Out-File f.txt",
    "git commit -m @'\nThe message.\n'@",
])
def test_heredoc_write_catches_powershell(command):
    assert ac.find(command, "powershell") == ["heredoc-write"]


@pytest.mark.parametrize("command", [
    "python x.py > \"$S/out.txt\"",
    "git log > f",
    "pytest -q 2>&1",
    "ls > /dev/null",
    "ls 2>/dev/null",
    "echo hello",
    "echo $?",
    "grep '<<' notes.md",
    "echo \"a << b\"",
    "python3 - <<'EOF'\nprint(1)\nEOF",
    "echo done >&2",
    "git commit -F \"$S/msg.txt\" -- a.py",
])
def test_heredoc_write_lets_these_be(command):
    assert "heredoc-write" not in ac.find(command, "bash")


@pytest.mark.parametrize("command", [
    "python x.py > out.txt",
    "echo hello",
    "git log | Select-Object -First 3",
    "Get-Content f.txt 2>$null",
])
def test_heredoc_write_lets_these_be_powershell(command):
    assert "heredoc-write" not in ac.find(command, "powershell")


# ---- wildcard-delete -----------------------------------------------------------

@pytest.mark.parametrize("command,shell", [
    ("rm \"$S\"/probe*.txt", "bash"),
    ("rm -rf /tmp/t090-*", "bash"),
    ("cd x && rm file?.log", "bash"),
    ("rmdir build*", "bash"),
    ("Remove-Item C:\\temp\\*.txt", "powershell"),
    ("del \"$env:TEMP\\probe*\"", "powershell"),
    ("Remove-Item -Path x -Include *.log -Recurse", "powershell"),
    ("ri .\\out?", "powershell"),
])
def test_wildcard_delete_catches(command, shell):
    assert ac.find(command, shell) == ["wildcard-delete"]


@pytest.mark.parametrize("command,shell", [
    ("git rm notes.md", "bash"),
    ("rm \"$S/probe.txt\"", "bash"),
    ("rm -rf /tmp/t090-act-checks-w", "bash"),
    ("find . -name '*.py'", "bash"),
    ("ls *.md", "bash"),
    ("rm -f out.txt && echo $?", "bash"),
    ("Remove-Item -Recurse -Force C:\\temp\\scratch-w", "powershell"),
    ("Get-ChildItem *.md", "powershell"),
])
def test_wildcard_delete_lets_these_be(command, shell):
    assert "wildcard-delete" not in ac.find(command, shell)


# ---- path-in-subshell ----------------------------------------------------------

@pytest.mark.parametrize("command", [
    "echo $(note-to-chris.md)",
    "echo $($S/probe.txt)",
    "x=\"$(docs/notes.md)\"",
    "y=$(C:\\temp\\a.txt)",
])
def test_path_in_subshell_catches(command):
    assert ac.find(command, "bash") == ["path-in-subshell"]


@pytest.mark.parametrize("command", [
    "echo $(cat f)",
    "echo $(git rev-parse HEAD)",
    "echo $(pwd)",
    "echo $(date +%H)",
    "echo $((1+2))",
    "echo '$(note.md)'",
])
def test_path_in_subshell_lets_these_be(command):
    assert "path-in-subshell" not in ac.find(command, "bash")


def test_path_in_subshell_lets_a_powershell_member_be():
    assert ac.find("Write-Host \"$($item.Name)\"", "powershell") == []


def test_find_returns_the_names_in_order():
    command = "echo x > \"$S/a.txt\"; rm \"$S\"/a*.txt; echo $($S/a.txt)"
    assert ac.find(command, "bash") == ["heredoc-write", "wildcard-delete", "path-in-subshell"]


def test_find_on_nothing():
    assert ac.find("", "bash") == []
    assert ac.find(None, "bash") == []


# ---- switches, counter and the hook -------------------------------------------

@pytest.fixture
def project(tmp_path, monkeypatch):
    folder = tmp_path / "project"
    folder.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(folder))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    return folder


def card(folder, extra=""):
    (folder / "project.yaml").write_text("name: demo-film\nkind: project\n" + extra, encoding="utf-8")


def counter(tmp_path):
    path = tmp_path / "local" / "agentic-meta" / "act-checks" / "demo-film.log"
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def call(event, command, tool="Bash", session="s-1"):
    return json.dumps({"session_id": session, "hook_event_name": event, "tool_name": tool,
                       "tool_input": {"command": command}})


def run(stdin, tmp_path, project):
    env = dict(os.environ, LOCALAPPDATA=str(tmp_path / "local"), CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run([sys.executable, "-B", TOOL], input=stdin.encode("utf-8"),
                          capture_output=True, env=env, timeout=60)


def test_a_missing_switch_reads_warn_as_shipped(project):
    card(project)
    assert ac.read_project(str(project)) == ("demo-film", {c: "warn" for c in ac.ALL_CHECKS})


def test_a_bad_switch_reads_warn_and_the_others_are_kept(project):
    card(project, "act_check_heredoc_write: maybe\nact_check_wildcard_delete: refuse\n"
                  "act_check_path_in_subshell: off\n")
    assert ac.read_project(str(project))[1] == {"heredoc-write": "warn", "wildcard-delete": "refuse",
                                                "path-in-subshell": "off", "turn-end-running": "warn"}


def test_warn_lets_the_act_through_before_and_tells_after(project, tmp_path):
    card(project)
    command = "echo probe > \"$S/probe.txt\""
    before = run(call("PreToolUse", command), tmp_path, project)
    assert before.returncode == 0 and before.stdout == b""
    after = run(call("PostToolUse", command), tmp_path, project)
    assert after.returncode == 0
    out = json.loads(after.stdout.decode("utf-8"))["hookSpecificOutput"]
    assert out["hookEventName"] == "PostToolUse"
    assert "heredoc-write" in out["additionalContext"] and "rule 16" in out["additionalContext"]
    assert "git commit -F <file>" in out["additionalContext"]
    lines = counter(tmp_path)
    assert len(lines) == 1
    assert lines[0].split(" · ")[1:5] == ["demo-film", "heredoc-write", "warn", "s-1"]


def test_warn_tells_after_a_failed_command_too(project, tmp_path):
    card(project)
    out = run(call("PostToolUseFailure", "rm \"$S\"/probe*.txt"), tmp_path, project)
    ctx = json.loads(out.stdout.decode("utf-8"))["hookSpecificOutput"]
    assert ctx["hookEventName"] == "PostToolUseFailure" and "Refusals 6" in ctx["additionalContext"]
    assert len(counter(tmp_path)) == 1


def test_refuse_stops_the_act_and_counts_once(project, tmp_path):
    card(project, "act_check_wildcard_delete: refuse\n")
    command = "rm \"$S\"/probe*.txt"
    before = run(call("PreToolUse", command), tmp_path, project)
    out = json.loads(before.stdout.decode("utf-8"))["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny"
    assert "wildcard-delete" in out["permissionDecisionReason"] and "exact name" in out["permissionDecisionReason"]
    after = run(call("PostToolUse", command), tmp_path, project)
    assert after.stdout == b""
    lines = counter(tmp_path)
    assert len(lines) == 1 and " · refuse · " in lines[0]


def test_off_is_not_looked_at_and_writes_nothing(project, tmp_path):
    card(project, "act_check_path_in_subshell: off\n")
    for event in ("PreToolUse", "PostToolUse"):
        out = run(call(event, "echo $(note-to-chris.md)"), tmp_path, project)
        assert out.returncode == 0 and out.stdout == b""
    assert counter(tmp_path) == []


def test_the_powershell_tool_is_read_as_powershell(project, tmp_path):
    card(project)
    out = run(call("PostToolUse", "Remove-Item C:\\x\\*.txt", tool="PowerShell"), tmp_path, project)
    assert "wildcard-delete" in out.stdout.decode("utf-8")


@pytest.mark.parametrize("stdin", [
    "not json at all",
    "",
    json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": None}),
])
def test_the_hook_never_breaks_a_session_on_bad_input(project, tmp_path, stdin):
    card(project)
    out = run(stdin, tmp_path, project)
    assert out.returncode == 0 and out.stdout == b"" and out.stderr == b""


def test_the_hook_never_breaks_a_session_with_no_project_yaml(project, tmp_path):
    out = run(call("PostToolUse", "echo x > f.txt"), tmp_path, project)
    assert out.returncode == 0 and out.stdout == b"" and out.stderr == b""
    assert not (tmp_path / "local").exists()


def test_the_hook_never_breaks_a_session_on_its_own_fault(project, tmp_path, monkeypatch):
    card(project)

    def broken(*_a):
        raise RuntimeError("its own fault")
    monkeypatch.setattr(ac, "find", broken)
    monkeypatch.setattr(sys, "stdin", type("In", (), {"buffer": __import__("io").BytesIO(
        call("PostToolUse", "echo x > f.txt").encode("utf-8"))})())
    assert ac.run_hook() == 0


# ---- turn-end-running, read from the Stop hook ---------------------------------

def stop(tasks, active=False):
    # the shape a Stop hook was given live, 17 Nov 2026
    return json.dumps({"session_id": "s-1", "hook_event_name": "Stop", "stop_hook_active": active,
                       "background_tasks": tasks, "session_crons": []})


RUNNING = {"id": "b1", "type": "shell", "status": "running", "description": "the gate",
           "command": "python3.11 -m pytest -q"}


def test_turn_end_running_warn_lets_the_turn_end_and_counts(project, tmp_path):
    card(project)
    out = run(stop([RUNNING]), tmp_path, project)
    assert out.returncode == 0 and out.stdout == b""
    lines = counter(tmp_path)
    assert len(lines) == 1
    assert lines[0].split(" · ")[2:] == ["turn-end-running", "warn", "s-1", "python3.11 -m pytest -q"]


def test_turn_end_running_refuse_holds_the_turn_once(project, tmp_path):
    card(project, "act_check_turn_end_running: refuse\n")
    out = json.loads(run(stop([RUNNING]), tmp_path, project).stdout.decode("utf-8"))
    assert out["decision"] == "block" and "rule 15" in out["reason"]
    assert run(stop([RUNNING], active=True), tmp_path, project).stdout == b""
    assert len(counter(tmp_path)) == 1


@pytest.mark.parametrize("tasks", [
    [],
    [dict(RUNNING, status="completed")],
    [dict(RUNNING, type="agent")],
])
def test_turn_end_running_lets_these_be(project, tmp_path, tasks):
    card(project)
    assert run(stop(tasks), tmp_path, project).stdout == b""
    assert counter(tmp_path) == []


def test_turn_end_running_off_writes_nothing(project, tmp_path):
    card(project, "act_check_turn_end_running: off\n")
    assert run(stop([RUNNING]), tmp_path, project).stdout == b""
    assert counter(tmp_path) == []


def test_the_counter_line_is_the_contract():
    when = datetime.datetime(2026, 11, 17, 8, 30, 5)
    command = "cat > f <<'EOF'\n" + "x" * 100
    line = ac.counter_line(when, "demo-film", "heredoc-write", "warn", "abc", command)
    assert line == "2026-11-17 08:30:05 · demo-film · heredoc-write · warn · abc · " + ("cat > f <<'EOF'⏎" + "x" * 100)[:80]


def test_the_counter_lives_outside_any_repository(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert ac.counter_path("demo-film") == os.path.join(str(tmp_path), "agentic-meta", "act-checks", "demo-film.log")
    monkeypatch.delenv("LOCALAPPDATA")
    assert ac.counter_path("demo-film").endswith(os.path.join(".local", "share", "agentic-meta", "act-checks",
                                                              "demo-film.log"))


# ---- the session-log reader -----------------------------------------------------

def sample_log(path):
    entries = [
        {"type": "user", "sessionId": "log-1", "timestamp": "2026-11-17T08:00:00.000Z",
         "message": {"content": "go"}},
        {"type": "assistant", "sessionId": "log-1", "timestamp": "2026-11-17T08:01:00.000Z",
         "message": {"content": [{"type": "text", "text": "rm *"},
                                 {"type": "tool_use", "name": "Bash",
                                  "input": {"command": "echo a > \"$S/a.txt\""}}]}},
        {"type": "assistant", "sessionId": "log-1", "timestamp": "2026-11-17T08:02:00.000Z",
         "message": {"content": [{"type": "tool_use", "name": "PowerShell",
                                  "input": {"command": "Remove-Item C:\\x\\*.txt"}},
                                 {"type": "tool_use", "name": "Read", "input": {"file_path": "x.md"}},
                                 {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}}]}},
    ]
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\nnot json\n", encoding="utf-8")


def test_log_prints_each_sighting_and_writes_nothing(project, tmp_path):
    card(project)
    log = tmp_path / "session.jsonl"
    sample_log(log)
    env = dict(os.environ, LOCALAPPDATA=str(tmp_path / "local"))
    out = subprocess.run([sys.executable, "-B", TOOL, "--log", str(log), "--project", str(project)],
                         capture_output=True, env=env, timeout=60)
    assert out.returncode == 0, out.stderr
    lines = out.stdout.decode("utf-8").splitlines()
    assert [l.split(" · ")[1:5] for l in lines] == [["demo-film", "heredoc-write", "warn", "log-1"],
                                                    ["demo-film", "wildcard-delete", "warn", "log-1"]]
    assert not (tmp_path / "local").exists()


def test_log_with_count_appends_to_the_counter(project, tmp_path):
    card(project)
    log = tmp_path / "session.jsonl"
    sample_log(log)
    env = dict(os.environ, LOCALAPPDATA=str(tmp_path / "local"))
    subprocess.run([sys.executable, "-B", TOOL, "--log", str(log), "--project", str(project), "--count"],
                   capture_output=True, env=env, timeout=60, check=True)
    assert len(counter(tmp_path)) == 2
