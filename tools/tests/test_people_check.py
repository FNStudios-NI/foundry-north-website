# Tests for people_check.py. Each test builds a fresh project in a temp folder
# from the template's own files (conftest.py says how), fills in a brief and a
# register, and runs the tool as Rhys would.
# The people list always lives outside the copy, as the rule says.
# The copy leaves out the tests folders: this file holds the test words.

import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join("tools", "people_check.py")
ROW_HEADER = "| role | pointer to their details, outside the project | ends on |"


@pytest.fixture
def setup(fresh_project, tmp_path):
    project = fresh_project
    people = tmp_path / "people"
    people.mkdir()
    details = people / "the-user.txt"
    details.write_text("Marlowe\nasthma\n", encoding="utf-8")
    return project, details


@pytest.mark.skipif(os.path.isfile(os.path.join(ROOT, "project.yaml")),
                    reason="this is a project's copy: its docs/register.md is the project's own record; "
                           "the template's register blank is checked in the template's master copy")
def test_the_template_register_blank_holds_the_people_table():
    with open(os.path.join(ROOT, "docs", "register.md"), encoding="utf-8") as f:
        assert ROW_HEADER in f.read()


def write_brief(project, shared_line, body="We help the user plan their week."):
    text = "# Brief — test\n"
    if shared_line is not None:
        text += shared_line + "\n"
    text += "\n## The problem\n" + body + "\n"
    (project / "docs" / "brief.md").write_text(text, encoding="utf-8")


def add_person(project, role, pointer):
    register = project / "docs" / "register.md"
    text = register.read_text(encoding="utf-8")
    assert ROW_HEADER in text, "the register blank lost its People table"
    register.write_text(text.rstrip("\n") + f"\n| {role} | `{pointer}` | 2027-01-01 |\n",
                        encoding="utf-8")


def run(project):
    done = subprocess.run(
        [sys.executable, "-B", TOOL], cwd=project, capture_output=True, text=True,
    )
    return done.returncode, done.stdout + done.stderr


def snapshot(folder):
    return sorted(
        (os.path.relpath(os.path.join(r, f), folder), os.path.getmtime(os.path.join(r, f)))
        for r, _, files in os.walk(folder) for f in files
    )


def test_private_project_is_allowed(setup):
    project, details = setup
    write_brief(project, "Shared: never", body="Marlowe has asthma.")
    add_person(project, "the user", details)
    assert run(project) == (0, "ALLOW: private project\n")


def test_never_followed_by_words_reads_as_never(setup):
    project, details = setup
    write_brief(project, "Shared: never — it is for family only", body="Marlowe has asthma.")
    add_person(project, "the user", details)
    assert run(project) == (0, "ALLOW: private project\n")


def test_yes_followed_by_words_reads_as_yes(setup):
    project, details = setup
    write_brief(project, "Shared: yes — may go public", body="Marlowe likes mornings.")
    add_person(project, "the user", details)
    assert run(project) == (1, "REFUSE: docs/brief.md holds a detail of the user\n")


def test_shared_project_with_a_name_refuses_without_printing_it(setup):
    project, details = setup
    write_brief(project, "Shared: yes — it may go public", body="Marlowe likes mornings.")
    add_person(project, "the user", details)
    code, out = run(project)
    assert code == 1
    assert out.splitlines() == ["REFUSE: docs/brief.md holds a detail of the user"]
    assert "marlowe" not in out.lower() and "asthma" not in out.lower()


def test_shared_project_by_role_only_is_allowed(setup):
    project, details = setup
    write_brief(project, "Shared: yes — it may go public", body="the user likes mornings.")
    add_person(project, "the user", details)
    code, out = run(project)
    assert code == 0 and out.startswith("ALLOW:")


def test_no_shared_line_refuses_naming_the_brief(setup):
    project, details = setup
    write_brief(project, None)
    assert run(project) == (1, "REFUSE: the brief has no Shared line\n")


def test_the_blank_brief_unfilled_is_refused(setup):
    project, _ = setup
    shutil.copy(project / "docs" / "blanks" / "brief.md", project / "docs" / "brief.md")
    code, out = run(project)
    assert code == 1 and "Shared line is not filled" in out


def test_missing_details_file_refuses_naming_the_role_not_the_path(setup, tmp_path):
    project, _ = setup
    write_brief(project, "Shared: yes")
    add_person(project, "the carer", tmp_path / "people" / "gone.txt")
    assert run(project) == (1, "REFUSE: the details file for the carer does not exist\n")


def test_details_file_inside_the_project_is_refused(setup):
    project, _ = setup
    write_brief(project, "Shared: yes")
    (project / "people.txt").write_text("Marlowe\n", encoding="utf-8")
    add_person(project, "the user", "people.txt")
    code, out = run(project)
    assert code == 1 and "inside the project" in out and "Marlowe" not in out


def test_every_file_kind_is_read_any_case_and_one_line_per_file(setup):
    project, details = setup
    write_brief(project, "Shared: yes")
    add_person(project, "the user", details)
    for name in ("a.html", "b.txt", "c.yaml", "d.json", "f.csv", "g"):
        (project / name).write_text("she has ASTHMA", encoding="utf-8")
    (project / "e.md").write_text("Marlowe, asthma, Marlowe", encoding="utf-8")
    code, out = run(project)
    assert code == 1
    files = sorted(line.split()[1] for line in out.splitlines())
    assert files == ["a.html", "b.txt", "c.yaml", "d.json", "e.md", "f.csv", "g"]


def test_a_detail_in_a_file_name_or_role_is_never_printed(setup):
    project, details = setup
    write_brief(project, "Shared: yes")
    add_person(project, "Marlowe's carer", details)
    (project / "marlowe-notes.md").write_text("nothing here", encoding="utf-8")
    code, out = run(project)
    assert code == 1
    assert "marlowe" not in out.lower()


def test_it_writes_nothing(setup):
    project, details = setup
    write_brief(project, "Shared: yes", body="Marlowe")
    add_person(project, "the user", details)
    before = snapshot(project.parent)
    run(project)
    assert snapshot(project.parent) == before


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_in_git_it_skips_ignored_files_and_reads_new_ones(setup):
    project, details = setup
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    write_brief(project, "Shared: yes")
    add_person(project, "the user", details)
    (project / ".gitignore").write_text("scratch/\n", encoding="utf-8")
    (project / "scratch").mkdir()
    (project / "scratch" / "x.md").write_text("Marlowe", encoding="utf-8")
    (project / "new.md").write_text("Marlowe", encoding="utf-8")
    code, out = run(project)
    assert (code, out) == (1, "REFUSE: new.md holds a detail of the user\n")


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_a_tracked_yml_and_py_file_are_read(setup):
    project, details = setup
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    write_brief(project, "Shared: yes")
    add_person(project, "the user", details)
    (project / "project.yml").write_text("owner: Marlowe\n", encoding="utf-8")
    (project / "tools" / "plan.py").write_text("# for Marlowe\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(project), "add", "project.yml", "tools/plan.py"], check=True)
    code, out = run(project)
    assert code == 1
    assert out.splitlines() == ["REFUSE: project.yml holds a detail of the user",
                                "REFUSE: tools/plan.py holds a detail of the user"]


def test_a_binary_file_is_not_read(setup):
    project, details = setup
    write_brief(project, "Shared: yes")
    add_person(project, "the user", details)
    (project / "photo.bin").write_bytes(b"\x89PNG\0\0 Marlowe \0" + b"x" * 9000 + b" asthma")
    code, out = run(project)
    assert code == 0 and out.startswith("ALLOW:")


def held_project(project, details, held_line="Held apart: template/"):
    write_brief(project, "Shared: never — it is for family only\n" + held_line,
                body="Marlowe has asthma.")
    add_person(project, "the user", details)
    (project / "template").mkdir()
    (project / "template" / "clean.md").write_text("the user", encoding="utf-8")


def test_a_word_in_a_folder_held_apart_refuses(setup):
    project, details = setup
    held_project(project, details)
    (project / "template" / "x.md").write_text("Marlowe likes mornings.", encoding="utf-8")
    code, out = run(project)
    assert (code, out) == (1, "REFUSE: template/x.md holds a detail of the user\n")


def test_a_word_outside_the_folders_held_apart_is_passed(setup):
    project, details = setup
    held_project(project, details)
    (project / "docs" / "x.md").write_text("Marlowe likes mornings.", encoding="utf-8")
    code, out = run(project)
    assert code == 0 and out.startswith("ALLOW: private project")


def test_folders_held_apart_with_no_register_refuse(setup):
    project, details = setup
    held_project(project, details)
    (project / "docs" / "register.md").unlink()
    code, out = run(project)
    assert code == 1 and "held apart" in out and "no docs/register.md" in out


def test_folders_held_apart_with_no_people_rows_refuse(setup):
    project, _ = setup
    write_brief(project, "Shared: never\nHeld apart: template/")
    code, out = run(project)
    assert code == 1 and "held apart" in out and "no people" in out


def test_held_apart_none_behaves_as_before(setup):
    project, details = setup
    held_project(project, details, held_line="Held apart: none")
    (project / "template" / "x.md").write_text("Marlowe likes mornings.", encoding="utf-8")
    assert run(project) == (0, "ALLOW: private project\n")


def test_the_blank_held_apart_line_unfilled_is_refused(setup):
    project, details = setup
    held_project(project, details, held_line="Held apart: <folders that may be public, or none>")
    code, out = run(project)
    assert code == 1 and "Held apart line is not filled" in out
