# Tests for new_project.py: --adopt, and what a stamp copies. Each adopt test
# makes a small git project in pytest's temp folder, commits it so it is
# clean, and runs the real tool on it in a separate Python, as a person would.
# The stamp tests make a copy in pytest's temp folder the same way.
# In a project's copy, stamped or adopted, every test here is skipped, with
# the reason: that copy of the tool refuses to run (project.yaml sits beside
# its tools/ folder), so these tests only mean something in the template's
# master copy. An adopted project has no VERSION, so it is read only if there.
# No test here opens Notepad: run() adds --no-open to every stamp, and the two
# tests of the opener run the tool inside pytest with a stand-in in its place.
#   python -B -m pytest template/tools/tests/test_new_project.py -q

import json
import ntpath
import os
import subprocess
import sys
from importlib import util

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
TEMPLATE = os.path.dirname(TOOLS)
TOOL = os.path.join(TOOLS, "new_project.py")
WHERE = os.path.join(TOOLS, "where_am_i.py")
VERSION = None
if os.path.isfile(os.path.join(TEMPLATE, "VERSION")):
    with open(os.path.join(TEMPLATE, "VERSION"), encoding="utf-8") as f:
        VERSION = f.read().strip()

pytestmark = pytest.mark.skipif(
    os.path.isfile(os.path.join(TEMPLATE, "project.yaml")),
    reason="this is a project's copy of new_project.py, which refuses to run; these tests run in the template's master copy")

RECORD = {
    "CLAUDE.md": "# mine - for agents\nMy own rules.\n",
    "docs/decisions.md": "# Decisions\n\n## 2026-10-05 - his first ruling\nKeep it.\n",
    "docs/brief.md": "# Brief\nMy brief.\n",
    "docs/register.md": "# Register\nMine.\n",
    "docs/roadmap.md": "# Roadmap\nMine.\n",
    "docs/cards/2026-10-05-a.md": "# a card\n",
    "docs/pages/sheet-1.html": "<p>mine</p>\n",
    "docs/research/notes.md": "notes\n",
    "desks/road/CLAUDE.md": "# road desk\n",
    "tools/where_am_i.py": "print('an old copy')\n",
    "tools/my_own_tool.py": "print('mine')\n",
}


def git(folder, *args):
    return subprocess.run(["git", "-C", str(folder), "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                           "-c", "core.autocrlf=false", *args], capture_output=True, text=True, check=True).stdout


def make_project(root, files=RECORD, card="name: mine\nborn: 2026-10-05\n"):
    project = root / "mine"
    for path, text in files.items():
        (project / path).parent.mkdir(parents=True, exist_ok=True)
        (project / path).write_bytes(text.encode("utf-8"))
    if card is not None:
        (project / "project.yaml").write_bytes(card.encode("utf-8"))
    git(project.parent, "init", "-q", str(project))
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "start")
    return project


# The stamp's first commit is made as this name, so it never needs the machine's own.
IDENTITY = {"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


def run(*args, tool=TOOL, env=None):
    """Run the tool in a separate Python. A stamp always gets --no-open, so no test opens Notepad."""
    args = [str(a) for a in args]
    if "--into" in args and "--no-open" not in args:
        args.append("--no-open")
    return subprocess.run([sys.executable, "-B", str(tool), *args], capture_output=True, text=True,
                          env=dict(os.environ, **IDENTITY) if env is None else env)


def snapshot(project):
    return {path: (project / path).read_bytes() for path in RECORD if path != "tools/where_am_i.py"}


def test_dry_run_lists_and_writes_nothing(tmp_path):
    project = make_project(tmp_path)
    result = run("--adopt", project)
    assert result.returncode == 0, result.stdout + result.stderr
    writes, leaves = result.stdout.split("Would leave alone:")
    assert "  .claude/skills/conductor/SKILL.md" in writes
    assert "  tools/where_am_i.py" in writes
    assert "  pages.md" in writes
    assert "  desks/_desk/CLAUDE.md" in writes
    for path in ["CLAUDE.md", "docs/decisions.md", "docs/brief.md", "docs/cards/", "desks/road/"]:
        assert "  " + path + "\n" in leaves
    assert git(project, "status", "--porcelain") == ""


def test_go_writes_template_files_and_never_the_record(tmp_path):
    project = make_project(tmp_path)
    before_record = snapshot(project)
    before_stage = subprocess.run([sys.executable, "-B", WHERE, str(project)], capture_output=True, text=True).stdout
    result = run("--adopt", project, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    for path in [".claude/skills/conductor/SKILL.md", ".claude/settings.json", "tools/where_am_i.py", "pages.md",
                 "operator.md", "worker-rules.md", "tracks.md", "docs/blanks/receipt.md", "desks/_desk/CLAUDE.md"]:
        assert (project / path).is_file(), path
    with open(WHERE, "rb") as f:
        assert (project / "tools/where_am_i.py").read_bytes() == f.read()
    assert snapshot(project) == before_record
    assert not (project / "VERSION").exists()
    after_stage = subprocess.run([sys.executable, "-B", project / "tools/where_am_i.py", str(project)],
                                 capture_output=True, text=True).stdout
    assert after_stage.splitlines()[0] == before_stage.splitlines()[0]


def test_adopt_writes_the_role_sheets(tmp_path):
    project = make_project(tmp_path)
    assert run("--adopt", project, "--go").returncode == 0
    for role in ["master", "worker", "checker", "reader"]:
        with open(os.path.join(TEMPLATE, "roles", role + ".md"), "rb") as f:
            assert (project / "roles" / (role + ".md")).read_bytes() == f.read(), role


def test_name_from_project_yaml_replaces_the_placeholder(tmp_path):
    project = make_project(tmp_path, card="name: the-real-name\nborn: 2026-10-05\n")
    assert run("--adopt", project, "--go").returncode == 0
    skill = (project / ".claude/skills/conductor/SKILL.md").read_text(encoding="utf-8")
    assert "the-real-name" in skill
    assert "<" + "project>" not in skill


def test_project_yaml_only_its_version_line_changes(tmp_path):
    project = make_project(tmp_path, card="name: mine\nborn: 2026-10-05\ntemplate_version: 0.0.1\nkind: desk\n")
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / "project.yaml").read_text(encoding="utf-8") == \
        "name: mine\nborn: 2026-10-05\ntemplate_version: %s\nkind: desk\n" % VERSION


def test_project_yaml_without_a_version_line_gets_one_added(tmp_path):
    project = make_project(tmp_path)
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / "project.yaml").read_text(encoding="utf-8") == \
        "name: mine\nborn: 2026-10-05\ntemplate_version: %s\n" % VERSION


def test_missing_project_yaml_is_written(tmp_path):
    project = make_project(tmp_path, card=None)
    assert run("--adopt", project, "--go").returncode == 0
    card = (project / "project.yaml").read_text(encoding="utf-8")
    assert "template_version: %s\n" % VERSION in card
    assert "adopted: 20" in card


def test_refuses_uncommitted_changes_and_writes_nothing(tmp_path):
    project = make_project(tmp_path)
    (project / "docs/brief.md").write_text("changed\n", encoding="utf-8")
    result = run("--adopt", project, "--go")
    assert result.returncode == 1
    assert "uncommitted changes" in result.stdout
    assert not (project / "pages.md").exists()


def test_refuses_the_template_itself():
    result = run("--adopt", TEMPLATE, "--go")
    assert result.returncode == 1
    assert "Refused" in result.stdout and "template itself" in result.stdout


def test_refuses_a_folder_that_is_not_a_project(tmp_path):
    folder = tmp_path / "loose"
    folder.mkdir()
    (folder / "notes.txt").write_text("hello\n", encoding="utf-8")
    result = run("--adopt", folder, "--go")
    assert result.returncode == 1
    assert "not a project" in result.stdout
    assert os.listdir(folder) == ["notes.txt"]


def test_stamp_copies_gitkeep_files(tmp_path):
    result = run("probe", "--into", tmp_path, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "probe/tools/tests/pages/empty-project/.gitkeep").is_file()


def ignored(project, path):
    """True if git, in project, ignores path."""
    return subprocess.run(["git", "-C", str(project), "check-ignore", "-q", path]).returncode == 0


def test_stamp_gitignore_holds_pytest_cache(tmp_path):
    assert ".pytest_cache/" in run("probe", "--into", tmp_path).stdout
    assert run("probe", "--into", tmp_path, "--go").returncode == 0
    assert (tmp_path / "probe/.gitignore").read_text(encoding="utf-8") == \
        "__pycache__/\n.pytest_cache/\ndocs/runs/*/flag.txt\n"


def test_stamp_ignores_the_flag(tmp_path):
    assert "docs/runs/*/flag.txt" in run("probe", "--into", tmp_path).stdout
    assert run("probe", "--into", tmp_path, "--go").returncode == 0
    probe = tmp_path / "probe"
    git(probe, "init", "-q")
    (probe / "docs/runs/1").mkdir(parents=True)
    (probe / "docs/runs/1/flag.txt").write_text("working 2026-10-07T05:10Z started a worker\n", encoding="utf-8")
    (probe / "docs/runs/1/plan-signed.md").write_text("# Plan for run 1\n", encoding="utf-8")
    assert ignored(probe, "docs/runs/1/flag.txt")
    assert not ignored(probe, "docs/runs/1/plan-signed.md")


def test_stamp_plan_blank_holds_both_starts(tmp_path):
    assert run("probe", "--into", tmp_path, "--go").returncode == 0
    lines = (tmp_path / "probe/docs/blanks/plan-signed.md").read_text(encoding="utf-8").splitlines()
    assert any(line.startswith("Start: tracks — ") for line in lines)
    assert any(line.startswith("Start: now — ") for line in lines)
    assert (tmp_path / "probe/tracks.md").is_file()


def test_adopt_copies_gitkeep_and_adds_the_missing_gitignore_lines(tmp_path):
    project = make_project(tmp_path, files=dict(RECORD, **{".gitignore": "__pycache__/\n"}))
    writes, leaves = run("--adopt", project).stdout.split("Would leave alone:")
    assert "  .gitignore (would add: .pytest_cache/, docs/runs/*/flag.txt;" in writes
    assert "  .gitignore\n" not in leaves
    assert (project / ".gitignore").read_bytes() == b"__pycache__/\n"
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / "tools/tests/pages/empty-project/.gitkeep").is_file()
    assert (project / ".gitignore").read_bytes() == b"__pycache__/\n.pytest_cache/\ndocs/runs/*/flag.txt\n"


def test_adopt_keeps_a_projects_own_gitignore_lines(tmp_path):
    own = b"node_modules/\r\n# my notes\r\n__pycache__/\r\n*.log"
    project = make_project(tmp_path, files=dict(RECORD, **{".gitignore": own.decode("utf-8")}))
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / ".gitignore").read_bytes() == own + b"\r\n.pytest_cache/\r\ndocs/runs/*/flag.txt\r\n"
    (project / "docs/runs/2").mkdir(parents=True)
    (project / "docs/runs/2/flag.txt").write_text("done 2026-10-07T05:10Z review published\n", encoding="utf-8")
    assert ignored(project, "docs/runs/2/flag.txt")


def test_adopt_makes_a_gitignore_when_there_is_none(tmp_path):
    project = make_project(tmp_path)
    assert not (project / ".gitignore").exists()
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / ".gitignore").read_bytes() == b"__pycache__/\n.pytest_cache/\ndocs/runs/*/flag.txt\n"


def test_adopt_leaves_a_complete_gitignore_alone(tmp_path):
    own = "docs/runs/*/flag.txt\n.pytest_cache/\nmine/\n__pycache__/\n"
    project = make_project(tmp_path, files=dict(RECORD, **{".gitignore": own}))
    leaves = run("--adopt", project).stdout.split("Would leave alone:")[1]
    assert "  .gitignore\n" in leaves
    assert run("--adopt", project, "--go").returncode == 0
    assert (project / ".gitignore").read_bytes() == own.encode("utf-8")


def settings(project):
    return json.loads((project / ".claude/settings.json").read_text(encoding="utf-8"))


def test_adopt_keeps_a_projects_plugins_and_adds_the_template_env(tmp_path):
    own = '{\n  "enabledPlugins": {\n    "superpowers@claude-plugins-official": true\n  }\n}\n'
    project = make_project(tmp_path, files=dict(RECORD, **{".claude/settings.json": own}))
    assert "  .claude/settings.json: kept enabledPlugins\n" in run("--adopt", project).stdout
    result = run("--adopt", project, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "  .claude/settings.json: kept enabledPlugins\n" in result.stdout
    assert "  .claude/settings.json: added env\n" in result.stdout
    assert settings(project) == {"enabledPlugins": {"superpowers@claude-plugins-official": True},
                                 "env": {"CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"}}


def test_adopt_keeps_a_differing_setting_and_says_so(tmp_path):
    own = '{"env": {"CLAUDE_CODE_SUBAGENT_MODEL": "opus", "MINE": "1"}, "permissions": {"allow": ["Bash(git:*)"]}}'
    project = make_project(tmp_path, files=dict(RECORD, **{".claude/settings.json": own}))
    result = run("--adopt", project, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    assert '  .claude/settings.json: kept yours for env.CLAUDE_CODE_SUBAGENT_MODEL, the template has "sonnet"\n' in result.stdout
    assert "  .claude/settings.json: kept env.MINE\n" in result.stdout
    assert settings(project)["env"] == {"CLAUDE_CODE_SUBAGENT_MODEL": "opus", "MINE": "1"}
    assert settings(project)["permissions"] == {"allow": ["Bash(git:*)"]}


def test_adopt_leaves_an_unchanged_settings_file_unwritten(tmp_path):
    own = '{ "enabledPlugins": {"superpowers@claude-plugins-official": true},\n  "env": {"CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"} }\n'
    project = make_project(tmp_path, files=dict(RECORD, **{".claude/settings.json": own}))
    writes, leaves = run("--adopt", project).stdout.split("Would leave alone:")
    assert ".claude/settings.json" not in writes
    assert "  .claude/settings.json (yours, with nothing of the template's to add)\n" in leaves
    assert "  .claude/settings.json: kept enabledPlugins\n" in leaves
    result = run("--adopt", project, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "  .claude/settings.json: kept enabledPlugins\n" in result.stdout.split("Left alone:")[1]
    assert (project / ".claude/settings.json").read_bytes() == own.encode("utf-8")


def test_adopt_refuses_a_broken_settings_file_and_writes_nothing(tmp_path):
    project = make_project(tmp_path, files=dict(RECORD, **{".claude/settings.json": '{"env": {"A": "1",}\n'}))
    result = run("--adopt", project, "--go")
    assert result.returncode == 1
    assert "Refused" in result.stdout and "settings.json" in result.stdout and "not valid JSON" in result.stdout
    assert git(project, "status", "--porcelain") == ""
    assert not (project / "pages.md").exists()


def test_adopt_adds_the_template_list_items_a_list_lacks(tmp_path):
    spec = util.spec_from_file_location("new_project", TOOL)
    tool = util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    notes = []
    joined = tool.join_settings({"allow": ["a", "b"]}, {"allow": ["b", "c"]}, [], notes)
    assert joined == {"allow": ["a", "b", "c"]}
    assert tool.settings_lines(notes, True) == ['added "c" to allow']


def test_stamp_writes_the_template_settings(tmp_path):
    assert run("probe", "--into", tmp_path, "--go").returncode == 0
    with open(os.path.join(TEMPLATE, "dot-claude", "settings.json"), "rb") as f:
        assert (tmp_path / "probe/.claude/settings.json").read_bytes() == f.read()


def stamp(tmp_path):
    """A stamped project called probe in tmp_path, and its one reminder file."""
    result = run("probe", "--into", tmp_path, "--go")
    assert result.returncode == 0, result.stdout + result.stderr
    reminders = list((tmp_path / "probe/docs/operator-acts").glob("*-github-repository.txt"))
    assert len(reminders) == 1
    return tmp_path / "probe", reminders[0]


def stamp_inside_pytest(tmp_path, monkeypatch, *more):
    """Stamp probe with the tool loaded here and a stand-in for its opener; what the stand-in was called with."""
    spec = util.spec_from_file_location("new_project", TOOL)
    tool = util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    opened = []
    monkeypatch.setattr(tool, "OPENER", lambda command, **how: opened.append(command))
    for key, value in IDENTITY.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", [TOOL, "probe", "--into", str(tmp_path), "--go", *more])
    tool.main()
    return tool, opened


def test_stamp_writes_his_reminder_with_the_projects_name(tmp_path):
    dry = run("probe", "--into", tmp_path)
    assert "-github-repository.txt, his reminder" in dry.stdout
    assert "Would then run git init on branch main" in dry.stdout
    assert not (tmp_path / "probe").exists()
    project, reminder = stamp(tmp_path)
    text = reminder.read_text(encoding="utf-8")
    assert text.startswith("MAKE THE PRIVATE GITHUB REPOSITORY FOR probe ")
    assert 'ends "/probe.git"' in text
    assert "<" + "project>" not in text and "For the agent" not in text
    assert text.splitlines()[-1] == "If anything looks different from a Pass line, stop and tell me what it says."


def test_stamp_opens_his_reminder_with_notepads_full_path(tmp_path, monkeypatch):
    tool, opened = stamp_inside_pytest(tmp_path, monkeypatch)
    reminders = list((tmp_path / "probe/docs/operator-acts").glob("*-github-repository.txt"))
    assert opened == [[tool.NOTEPAD, str(reminders[0])]]
    assert ntpath.isabs(tool.NOTEPAD) and ntpath.basename(tool.NOTEPAD) == "notepad.exe"
    assert os.path.isabs(opened[0][1])


def test_no_open_opens_nothing_and_prints_the_reminders_path(tmp_path, monkeypatch, capsys):
    tool, opened = stamp_inside_pytest(tmp_path, monkeypatch, "--no-open")
    assert opened == []
    reminders = list((tmp_path / "probe/docs/operator-acts").glob("*-github-repository.txt"))
    assert "His reminder, written and not opened: %s\n" % reminders[0] in capsys.readouterr().out


def test_stamp_makes_the_first_commit_on_main(tmp_path):
    project, reminder = stamp(tmp_path)
    assert git(project, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main"
    assert git(project, "rev-list", "--count", "HEAD").strip() == "1"
    # Read with the machine's own line-ending setting, as the stamp's commit was made.
    assert subprocess.run(["git", "-C", str(project), "status", "--porcelain"], capture_output=True, text=True).stdout == ""
    committed = git(project, "ls-files").splitlines()
    assert "project.yaml" in committed and "docs/operator-acts/" + reminder.name in committed


def test_stamp_lends_the_templates_git_identity_when_the_machine_has_none(tmp_path):
    # A machine with no name to commit as: an empty global config that forbids git guessing one.
    config = tmp_path / "gitconfig"
    config.write_text("[user]\n\tuseConfigOnly = true\n", encoding="utf-8")
    env = dict(os.environ, GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_NOSYSTEM="1")
    lent = subprocess.run(["git", "-C", TEMPLATE, "config", "user.name"], capture_output=True, text=True, env=env).stdout.strip()
    if not lent:
        pytest.skip("the template's repository has no name of its own to lend")
    result = run("probe", "--into", tmp_path, "--go", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "the one the template's repository uses: " + lent in result.stdout
    assert git(tmp_path / "probe", "config", "--local", "user.name").strip() == lent
    assert git(tmp_path / "probe", "log", "-1", "--format=%an").strip() == lent


def test_stamp_without_git_says_so_and_the_copy_stands(tmp_path):
    empty = tmp_path / "no-git-here"
    empty.mkdir()
    result = run("probe", "--into", tmp_path, "--go", env=dict(os.environ, PATH=str(empty)))
    assert result.returncode == 1
    assert "the copy stands, but git could not make its first commit" in result.stdout
    assert (tmp_path / "probe/project.yaml").is_file()
    assert not (tmp_path / "probe/.git").exists()


def test_online_pushes_to_a_bare_repository_and_the_check_passes(tmp_path):
    project, _ = stamp(tmp_path)
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    result = run("--online", project, "--remote", remote)
    assert result.returncode == 0, result.stdout + result.stderr
    head = git(project, "rev-parse", "HEAD").strip()
    assert result.stdout == "ONLINE: %s holds %s\n" % (remote, head)
    assert git(remote, "rev-parse", "refs/heads/main").strip() == head
    assert git(project, "remote", "get-url", "origin").strip() == str(remote)


def test_online_says_not_online_when_the_remote_cannot_be_reached(tmp_path):
    project, _ = stamp(tmp_path)
    result = run("--online", project, "--remote", tmp_path / "nowhere.git")
    assert result.returncode == 1
    assert result.stdout.startswith("NOT ONLINE: ")
    assert "this machine's sign-in cannot push there; widening it is his act, once per machine." in result.stdout
    assert "\nONLINE: " not in result.stdout


def test_online_refuses_a_different_origin(tmp_path):
    project, _ = stamp(tmp_path)
    git(project, "remote", "add", "origin", str(tmp_path / "first.git"))
    result = run("--online", project, "--remote", tmp_path / "second.git")
    assert result.returncode == 1
    assert "Refused" in result.stdout and "different origin" in result.stdout
    assert git(project, "remote", "get-url", "origin").strip() == str(tmp_path / "first.git")


def test_online_runs_from_a_projects_own_copy_which_still_refuses_to_stamp(tmp_path):
    project, _ = stamp(tmp_path)
    own = project / "tools/new_project.py"
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    result = run("--online", project, "--remote", remote, tool=own)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("ONLINE: ")
    refused = run("another", "--into", tmp_path, "--go", tool=own)
    assert refused.returncode == 1 and "project's copy of the tool" in refused.stdout
    assert not (tmp_path / "another").exists()
