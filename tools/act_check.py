# act_check.py: three checks on the shell commands an agent runs.
#
# What it holds, and why
#   Every rule held by a tool held; every rule left as text drifted. The
#   no-heredoc rule was broken in 25 of 35 receipts in engine-motion-graphics,
#   because the harness itself tells agents to use heredocs (template 0.9.0
#   design, Part 2 and § The cause). His ruling 1 of 17 Nov 2026 07:52: the
#   checks warn and count for one project, then refuse on his word at that
#   project's review. So each check has a switch, and 0.9.0 ships `warn`.
#   The three checks, each found in one shell command (Bash or PowerShell):
#     heredoc-write     a file written by a heredoc, an echo or printf (or a
#                       PowerShell here-string) redirect; any heredoc inside
#                       git commit (worker-rules.md rule 16)
#     wildcard-delete   rm, rmdir, del, Remove-Item and their aliases with a
#                       * or ? in a path (worker-rules.md § Refusals 6)
#     path-in-subshell  a $( ) holding only a file path, which runs the file
#                       as a command (lesson L020)
#   find(command, shell) returns the names found; everything else calls it.
#   A fourth, read from the Stop hook and not from a command:
#     turn-end-running  the agent ends its turn while a shell command it
#                       started still runs (worker-rules.md rule 15); the
#                       Stop hook's input lists them as background_tasks
#   The message for each check is the MESSAGES table just below.
#
# The switches, one line per check in the project's project.yaml
#   act_check_heredoc_write:     warn | refuse | off
#   act_check_wildcard_delete:   warn | refuse | off
#   act_check_path_in_subshell:  warn | refuse | off
#   act_check_turn_end_running:  warn | refuse | off
#   A missing or unreadable line reads `warn`. `off`: not looked at, nothing
#   written. `warn`: the act goes through, the agent is told after it, and
#   the sighting is counted. `refuse`: the act is stopped, the agent is told
#   why, and the sighting is counted. Each sighting is counted once.
#
# As a hook (the project's .claude/settings.json runs it with the tool
# call's JSON on its input)
#   PreToolUse acts only on a check switched `refuse` (it denies the act);
#   PostToolUse and PostToolUseFailure act only on a check switched `warn`
#   (the message reaches the agent as added context). Stop: `refuse` holds
#   the turn open once with the message; `warn` only counts, since any
#   message to the agent there would hold its turn open.
#   The hook never breaks a session: any error inside it (no project.yaml,
#   bad JSON, its own fault) lets the act through silently, exit 0.
#
# The counter
#   %LOCALAPPDATA%/agentic-meta/act-checks/<project name>.log
#   (~/.local/share/agentic-meta/act-checks/ with no LOCALAPPDATA): the
#   folder beside cap_check.py's seats, the name from project.yaml's name:,
#   so every worktree of one project writes one file and no branch carries
#   it. One line per sighting, the scoreboard's contract:
#   <yyyy-mm-dd hh:mm:ss> · foundry-north-website · <check> · <warn|refuse> · <session id> · <the command's first 80 characters, each newline shown as ⏎>
#   The time is this machine's clock, as record.py stamps it.
#
# How to run it by hand
#   python tools/act_check.py --log <session .jsonl> [--count] [--project <dir>]
#   reads every Bash and PowerShell command in a session log and prints one
#   line per sighting, in the counter's form, with the log's session id. It
#   writes nothing unless --count is given; then it appends those lines to
#   the counter too. Checks switched `off` are skipped.
#
# Python 3 standard library only.

import datetime
import json
import os
import re
import sys

# check -> (its switch in project.yaml, the rule, the right way)
MESSAGES = {
    "heredoc-write": (
        "act_check_heredoc_write",
        "worker-rules.md rule 16: write multi-line text, cards and scripts with the Write and Edit tools, "
        "never a heredoc or an echo",
        "write the file with the Write tool; for a commit message, write it to a file with the Write tool "
        "and run git commit -F <file>",
    ),
    "wildcard-delete": (
        "act_check_wildcard_delete",
        "worker-rules.md § Refusals 6: a pattern (a star, a question mark) in a delete command is a refusal",
        "delete by the exact name, one named file or folder at a time",
    ),
    "path-in-subshell": (
        "act_check_path_in_subshell",
        "lesson L020: a file path inside $( ) runs the file as a command",
        "read a file with the Read tool, or with cat inside $( )",
    ),
    "turn-end-running": (
        "act_check_turn_end_running",
        "worker-rules.md rule 15: never end your turn while a command you started is still running",
        "wait for the command to end (or stop it) before ending your turn; run the gate in the foreground",
    ),
}
ORDER = ["heredoc-write", "wildcard-delete", "path-in-subshell"]
ALL_CHECKS = ORDER + ["turn-end-running"]   # the fourth is read from a Stop hook, not a command
SWITCHES = ("warn", "refuse", "off")
SHELLS = {"Bash": "bash", "PowerShell": "powershell"}

# ---- reading a command ------------------------------------------------------
# mask() returns the command with every literal (quoted text, heredoc bodies,
# here-strings, comments) replaced by "_", at the same positions, so the
# patterns below see only code. Text inside $( ) stays code, even inside
# double quotes. It also returns where each heredoc or here-string began.

HEREDOC_START = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


def mask(command, shell):
    if shell == "powershell":
        return _mask_powershell(command)
    return _mask_bash(command)


def _mask_bash(s):
    out = list(s)
    starts = []
    pending = []          # heredoc delimiters whose bodies begin at the next newline
    stack = ["code"]      # code | dq ; each "$(" pushes code, its ")" pops
    depth = [0]           # plain "(" nesting inside each code level
    i, n = 0, len(s)

    def blank(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = "_"

    while i < n:
        c = s[i]
        top = stack[-1]
        if top == "dq":
            if c == "\\" and i + 1 < n:
                blank(i, i + 2)
                i += 2
            elif c == '"':
                stack.pop()
                depth.pop()
                i += 1
            elif s.startswith("$(", i) and not s.startswith("$((", i):
                stack.append("code")
                depth.append(0)
                i += 2
            else:
                blank(i, i + 1)
                i += 1
            continue
        # code
        if c == "\\" and i + 1 < n:
            i += 2
        elif c == "'":
            end = s.find("'", i + 1)
            end = n if end < 0 else end
            blank(i + 1, end)
            i = end + 1
        elif c == '"':
            stack.append("dq")
            depth.append(0)
            i += 1
        elif c == "#" and (i == 0 or s[i - 1] in " \t\n;&|("):
            end = s.find("\n", i)
            end = n if end < 0 else end
            blank(i, end)
            i = end
        elif s.startswith("<<<", i):
            i += 3
        elif s.startswith("<<", i):
            m = HEREDOC_START.match(s, i)
            if m:
                starts.append(i)
                pending.append(m.group(3))
                i = m.end()
            else:
                i += 2
        elif c == "\n" and pending:
            i += 1
            for word in pending:
                # the body runs to a line that is the delimiter alone
                while i < n:
                    end = s.find("\n", i)
                    end = n if end < 0 else end
                    line = s[i:end]
                    blank(i, end)
                    i = end + 1
                    if line.strip() == word:
                        break
            pending = []
        elif s.startswith("$(", i) and not s.startswith("$((", i):
            stack.append("code")
            depth.append(0)
            i += 2
        elif c == "(":
            depth[-1] += 1
            i += 1
        elif c == ")":
            if depth[-1] > 0:
                depth[-1] -= 1
            elif len(stack) > 1:
                stack.pop()
                depth.pop()
            i += 1
        else:
            i += 1
    return "".join(out), starts


def _mask_powershell(s):
    out = list(s)
    starts = []
    stack = ["code"]
    depth = [0]
    i, n = 0, len(s)

    def blank(a, b):
        for k in range(a, b):
            out[k] = "_"

    while i < n:
        c = s[i]
        top = stack[-1]
        if top == "dq":
            if c == "`" and i + 1 < n:
                blank(i, i + 2)
                i += 2
            elif c == '"':
                if s.startswith('""', i):
                    blank(i, i + 2)
                    i += 2
                else:
                    stack.pop()
                    depth.pop()
                    i += 1
            elif s.startswith("$(", i):
                stack.append("code")
                depth.append(0)
                i += 2
            else:
                blank(i, i + 1)
                i += 1
            continue
        if s.startswith("@'", i) or s.startswith('@"', i):
            q = s[i + 1]
            close = "\n" + q + "@"
            end = s.find(close, i + 2)
            end = n if end < 0 else end + len(close)
            starts.append(i)
            blank(i + 2, max(i + 2, end - 2))
            i = end
        elif c == "`" and i + 1 < n:
            i += 2
        elif c == "'":
            j = i + 1
            while j < n:
                if s[j] == "'" and s.startswith("''", j):
                    j += 2
                elif s[j] == "'":
                    break
                else:
                    j += 1
            blank(i + 1, min(j, n))
            i = j + 1
        elif c == '"':
            stack.append("dq")
            depth.append(0)
            i += 1
        elif c == "#" and (i == 0 or s[i - 1] in " \t\n;|("):
            end = s.find("\n", i)
            end = n if end < 0 else end
            blank(i, end)
            i = end
        elif s.startswith("$(", i):
            stack.append("code")
            depth.append(0)
            i += 2
        elif c == "(":
            depth[-1] += 1
            i += 1
        elif c == ")":
            if depth[-1] > 0:
                depth[-1] -= 1
            elif len(stack) > 1:
                stack.pop()
                depth.pop()
            i += 1
        else:
            i += 1
    return "".join(out), starts


def pieces(masked, pipes=True):
    """(start, end) of each simple command: split on newline, ; && || and, if pipes, |."""
    cut = r"\n|;|&&|\|\||\|" if pipes else r"\n|;|&&|\|\|"
    spans, at = [], 0
    for m in re.finditer(cut, masked):
        spans.append((at, m.start()))
        at = m.end()
    spans.append((at, len(masked)))
    return spans


def words(masked, original, a, b):
    """The words of masked[a:b], each as its original text."""
    return [original[a + m.start():a + m.end()] for m in re.finditer(r"\S+", masked[a:b])]


LEAD = {"(", "{", "then", "do", "else", "!", "sudo", "command", "builtin", "&"}


def first_words(ws):
    """The words with leading keywords and brackets dropped, so the first is the command."""
    while ws:
        if ws[0] in LEAD:
            ws = ws[1:]
        elif ws[0][0] in "({":
            ws = ([ws[0][1:]] if ws[0][1:] else []) + ws[1:]
        else:
            break
    return ws


# A redirect of standard output to a file: >, >>, 1>, &>, *>, >|; never 2>,
# >&2, > /dev/null, > $null or >( ).
REDIRECT = re.compile(r"(?<![<>&\w=-])([01*&]?)(>>?\|?)(?![&(>])[ \t]*(\S*)")
NULL_TARGETS = {"/dev/null", "$null", "nul", "NUL", "''", '""'}


def writes_a_file(masked, original, a, b):
    for m in REDIRECT.finditer(masked, a, b):
        target = original[m.start(3):m.end(3)]
        if not target or target in NULL_TARGETS:
            continue
        return True
    return False


GIT_COMMIT = re.compile(r"\bgit\b[^\n;&|]*?\bcommit\b")
TEE = re.compile(r"\btee\b")
PS_WRITERS = re.compile(r"\|\s*(Out-File|Set-Content)\b", re.IGNORECASE)
PS_WRITER_CMDS = re.compile(r"(?<![\w-])(Out-File|Set-Content)\b", re.IGNORECASE)
ECHOES_BASH = {"echo", "printf"}
ECHOES_PS = {"echo", "write-output"}
DELETERS = {"rm", "rmdir", "del", "erase", "rd", "ri", "remove-item"}


def _heredoc_write(command, shell, masked, starts):
    if starts and GIT_COMMIT.search(masked):
        return True
    if shell == "powershell":
        for a, b in pieces(masked, pipes=False):
            ws = first_words(words(masked, command, a, b))
            here = any(a <= st < b for st in starts)
            echo = bool(ws) and ws[0].lower() in ECHOES_PS
            if (here or echo) and (writes_a_file(masked, command, a, b)
                                   or PS_WRITERS.search(masked, a, b)
                                   or (here and PS_WRITER_CMDS.search(masked, a, b))):
                return True
        return False
    for a, b in pieces(masked, pipes=False):
        if any(a <= st < b for st in starts):
            if writes_a_file(masked, command, a, b) or TEE.search(masked, a, b):
                return True
    for a, b in pieces(masked):
        ws = first_words(words(masked, command, a, b))
        if ws and ws[0] in ECHOES_BASH and writes_a_file(masked, command, a, b):
            return True
    return False


def _wildcard_delete(command, shell, masked):
    for a, b in pieces(masked):
        ws = first_words(words(masked, command, a, b))
        if not ws:
            continue
        name = ws[0].lower() if shell == "powershell" else ws[0]
        if name not in DELETERS:
            continue
        for w in ws[1:]:
            if w.startswith("-") and shell == "bash":
                continue
            if w.startswith("-") and ":" not in w:
                continue
            if "*" in w or "?" in w.replace("$?", ""):
                return True
    return False


PATHISH_END = re.compile(r"\.[A-Za-z]{1,5}$")


def _path_in_subshell(command, shell, masked):
    for m in re.finditer(r"\$\((?!\()", masked):
        # the matching ")" in the masked text
        level, j = 1, m.end()
        while j < len(masked) and level:
            if masked[j] == "(":
                level += 1
            elif masked[j] == ")":
                level -= 1
            j += 1
        if level:
            continue
        inner = command[m.end():j - 1].strip()
        if not inner or re.search(r"\s", inner) or inner.startswith("("):
            continue
        if "/" in inner or "\\" in inner:
            return True
        if not inner.startswith("$") and PATHISH_END.search(inner):
            return True
    return False


def find(command, shell="bash"):
    """The checks one shell command trips, in ORDER. shell: "bash" or "powershell"."""
    if not isinstance(command, str) or not command.strip():
        return []
    shell = "powershell" if str(shell).lower() in ("powershell", "pwsh") else "bash"
    masked, starts = mask(command, shell)
    found = []
    if _heredoc_write(command, shell, masked, starts):
        found.append("heredoc-write")
    if _wildcard_delete(command, shell, masked):
        found.append("wildcard-delete")
    if _path_in_subshell(command, shell, masked):
        found.append("path-in-subshell")
    return found


# ---- the project, its switches and the counter ------------------------------

def project_dir():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return env
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_project(folder):
    """(name, {check: switch}) from folder/project.yaml; raises if it is missing or has no name."""
    with open(os.path.join(folder, "project.yaml"), encoding="utf-8") as f:
        text = f.read()
    fields = {}
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip("'\"")
    name = fields.get("name", "")
    if not name:
        raise ValueError("project.yaml has no name")
    switches = {}
    for check in ALL_CHECKS:
        value = fields.get(MESSAGES[check][0], "").lower()
        switches[check] = value if value in SWITCHES else "warn"
    return name, switches


def counter_path(name):
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    safe = re.sub(r"[^\w.-]", "_", name)
    return os.path.join(base, "agentic-meta", "act-checks", safe + ".log")


def counter_line(when, project, check, switch, session, command):
    shown = command.replace("\r\n", "\n").replace("\r", "\n")[:80].replace("\n", "⏎")
    return " · ".join([when.strftime("%Y-%m-%d %H:%M:%S"), project, check, switch, session or "-", shown])


def count(name, lines):
    path = counter_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")


def message(check, switch):
    _key, rule, right = MESSAGES[check]
    done = "This act was stopped and counted." if switch == "refuse" else "This act went through and was counted."
    return f"act_check: {check} (switch: {switch}). Rule: {rule}. The right way: {right}. {done}"


# ---- the hook -------------------------------------------------------------

PRE, POST, STOP = "PreToolUse", ("PostToolUse", "PostToolUseFailure"), "Stop"


def stop_hook(data):
    """turn-end-running: the agent ends its turn while a shell command it started still runs.
    The Stop hook's input lists them under background_tasks (seen live, 17 Nov 2026)."""
    running = [t for t in data.get("background_tasks") or []
               if isinstance(t, dict) and t.get("type") == "shell" and t.get("status") == "running"]
    if not running:
        return None
    name, switches = read_project(project_dir())
    switch = switches["turn-end-running"]
    if switch == "off" or (switch == "refuse" and data.get("stop_hook_active")):
        return None
    command = "\n".join(str(t.get("command", "")) for t in running)
    count(name, [counter_line(datetime.datetime.now(), name, "turn-end-running", switch,
                              data.get("session_id", ""), command)])
    if switch == "refuse":
        return {"decision": "block", "reason": message("turn-end-running", switch)}
    # warn: the turn ends; only the counter knows (a message to the agent would hold its turn open).
    return None


def hook(raw):
    """The hook's whole work: the JSON to print (or None) for one hook call's input."""
    data = json.loads(raw)
    event = data.get("hook_event_name", "")
    if event == STOP:
        return stop_hook(data)
    shell = SHELLS.get(data.get("tool_name", ""))
    if not shell or (event != PRE and event not in POST):
        return None
    command = (data.get("tool_input") or {}).get("command", "")
    name, switches = read_project(project_dir())
    acting = "refuse" if event == PRE else "warn"
    hits = [c for c in find(command, shell) if switches[c] == acting]
    if not hits:
        return None
    now = datetime.datetime.now()
    count(name, [counter_line(now, name, c, acting, data.get("session_id", ""), command) for c in hits])
    text = "\n".join(message(c, acting) for c in hits)
    if event == PRE:
        return {"hookSpecificOutput": {"hookEventName": PRE, "permissionDecision": "deny",
                                       "permissionDecisionReason": text}}
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def run_hook():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8")
        out = hook(raw)
        if out is not None:
            sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))
            sys.stdout.flush()
    except BaseException:
        pass
    return 0


# ---- the fall-back's reader -----------------------------------------------

def read_log(path, folder):
    """The counter's lines for every sighting in one session log."""
    name, switches = read_project(folder)
    lines = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            try:
                entry = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(entry, dict) or entry.get("type") != "assistant":
                continue
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                shell = SHELLS.get(item.get("name", ""))
                command = (item.get("input") or {}).get("command", "")
                if not shell or not isinstance(command, str):
                    continue
                when = _local_time(entry.get("timestamp", ""))
                for check in find(command, shell):
                    if switches[check] != "off":
                        lines.append(counter_line(when, name, check, switches[check],
                                                  entry.get("sessionId", ""), command))
    return name, lines


def _local_time(stamp):
    try:
        utc = datetime.datetime.strptime(stamp[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        return utc.astimezone().replace(tzinfo=None)
    except ValueError:
        return datetime.datetime.now()


def main(argv):
    if not argv:
        return run_hook()
    import argparse
    p = argparse.ArgumentParser(description="Read a session log for the three act checks.")
    p.add_argument("--log", required=True, help="a session .jsonl")
    p.add_argument("--count", action="store_true", help="also append the lines to the counter")
    p.add_argument("--project", default=None, help="the project's folder (default: this tool's project)")
    args = p.parse_args(argv)
    name, lines = read_log(args.log, args.project or project_dir())
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for line in lines:
        print(line)
    if args.count and lines:
        count(name, lines)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
