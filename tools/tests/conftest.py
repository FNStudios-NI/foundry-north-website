# Shared by the tests that run a tool on a fresh project (test_people_check.py,
# test_where_am_i.py). The fixture fresh_project builds that project in
# pytest's temp folder from the template's own files only: what --adopt
# writes (ADOPT_WRITES in new_project.py), taken from the folder these tests
# sit in, plus a starter record written here.
# Why: in a stamped or adopted project the folder beside tools/ holds a live
# record (brief, decisions, runs, desks, register), and a copy of it changes
# what the tools see. Built this way, the same tests mean the same thing in
# the template's master copy, a stamped copy and an adopted project.

import importlib.util
import os
import shutil

import pytest

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(TOOLS)
# The master copy keeps .claude/ as dot-claude/; a project has .claude/.
CLAUDE = "dot-claude" if os.path.isdir(os.path.join(ROOT, "dot-claude")) else ".claude"

_spec = importlib.util.spec_from_file_location("new_project_for_tests", os.path.join(TOOLS, "new_project.py"))
_new_project = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_new_project)
ADOPT_WRITES = _new_project.ADOPT_WRITES

# The record a fresh project starts with: no rulings, and a register whose People table is empty.
RECORD = {
    "docs/decisions.md": "# Decisions — test\n\nAppend-only.\n",
    "docs/register.md": "# Register — test\n\n## People\n\n"
                        "| role | pointer to their details, outside the project | ends on |\n|---|---|---|\n",
}


@pytest.fixture
def fresh_project(tmp_path):
    project = tmp_path / "project"
    for path in ADOPT_WRITES:
        source = os.path.join(ROOT, CLAUDE + path[len(".claude"):] if path.startswith(".claude/") else path)
        if path.endswith("/"):
            # The tests folders are left out: they hold the test words.
            shutil.copytree(source, project / path, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "tests"))
        else:
            (project / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, project / path)
    for path, text in RECORD.items():
        (project / path).parent.mkdir(parents=True, exist_ok=True)
        (project / path).write_text(text, encoding="utf-8")
    return project
