# Tests for send_site.py. Each test builds a throwaway project under tmp_path,
# with a small desks/site/public/ and files outside it, and a bare repository
# beside it standing in for foundry-north-site. The tool is always given that
# bare repository with --repo: nothing here reaches the real site repository.

import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "send_site.py")
PUBLIC = "desks/site/public/"
SITE = {"index.html": "<h1>Foundry North</h1>\n", "css/site.css": "body { color: #0e1512; }\n"}
OUTSIDE = {"README.md": "the project\n", "desks/site/docs/words.md": "draft words\n",
           "tools/secret_plan.py": "print('not for the site')\n"}
# Commits made here and by the tool must not ask to sign.
ENV = {**os.environ, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "commit.gpgsign", "GIT_CONFIG_VALUE_0": "false"}


def git(repo, *args, env=ENV):
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=env)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


@pytest.fixture
def tmp_path():
    # This file's own temp folder in place of pytest's: pytest's shared one
    # (pytest-of-<user>) cannot be opened on Rhys's machine, so the card's
    # gate errored there before any test ran. Made here, removed by its exact
    # name; git leaves some files in it read-only on Windows.
    folder = tempfile.mkdtemp(prefix="test-send-site-")
    yield pathlib.Path(folder)

    def unlock(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(folder, onerror=unlock)


def write(repo, path, text):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def project(tmp_path):
    site = tmp_path / "foundry-north-site.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(site))
    project = tmp_path / "project"
    project.mkdir()
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "core.autocrlf", "false")
    git(project, "config", "user.name", "Test")
    git(project, "config", "user.email", "test@example.invalid")
    for path, text in SITE.items():
        write(project, PUBLIC + path, text)
    for path, text in OUTSIDE.items():
        write(project, path, text)
    git(project, "add", ".")
    git(project, "commit", "-q", "-m", "the start")
    return project, site


def send(project, site, *more, env=ENV):
    done = subprocess.run([sys.executable, "-B", TOOL, "--repo", str(site), *more],
                          cwd=project, capture_output=True, text=True, env=env)
    return done.returncode, done.stdout + done.stderr


def remote(site):
    """What the site repository holds: its refs, and main's files with their contents."""
    refs = git(site, "for-each-ref")
    if not refs:
        return refs, {}
    names = git(site, "ls-tree", "-r", "--name-only", "main").splitlines()
    return refs, {name: git(site, "show", f"main:{name}") + "\n" for name in names}


def test_sends_only_the_public_folder(project):
    project, site = project
    code, out = send(project, site)
    assert code == 0, out
    head = git(project, "rev-parse", "HEAD")
    sent = git(site, "rev-parse", "main")
    assert re.match(rf"SENT: {sent[:7]} from {head[:7]}", out), out
    assert remote(site)[1] == SITE
    assert head in git(site, "log", "-1", "--format=%s", "main")


def test_a_second_send_with_nothing_changed_sends_nothing(project):
    project, site = project
    assert send(project, site)[0] == 0
    before = remote(site)
    code, out = send(project, site)
    assert code == 0, out
    assert out.startswith("NOTHING TO SEND"), out
    assert remote(site) == before


def test_a_file_removed_from_public_is_removed_from_the_site(project):
    project, site = project
    assert send(project, site)[0] == 0
    git(project, "rm", "-q", PUBLIC + "css/site.css")
    git(project, "commit", "-q", "-m", "no stylesheet")
    code, out = send(project, site)
    assert code == 0, out
    assert out.startswith("SENT: "), out
    assert remote(site)[1] == {"index.html": SITE["index.html"]}


@pytest.mark.parametrize("change", ["an edit", "a new file", "a removal"])
def test_refuses_uncommitted_changes_under_public(project, change):
    project, site = project
    assert send(project, site)[0] == 0
    write(project, PUBLIC + "index.html", "<h1>Foundry North, sent</h1>\n")
    git(project, "commit", "-q", "-am", "a committed change, waiting to be sent")
    if change == "an edit":
        write(project, PUBLIC + "index.html", "<h1>not yet committed</h1>\n")
    elif change == "a new file":
        write(project, PUBLIC + "draft.html", "<p>not yet committed</p>\n")
    else:
        (project / PUBLIC / "css" / "site.css").unlink()
    before = remote(site)
    code, out = send(project, site)
    assert code == 1, out
    assert out.startswith("REFUSE: uncommitted changes under desks/site/public/"), out
    assert remote(site) == before


def test_refuses_a_symbolic_link(project):
    # The link is made in git's own index, as a commit from any machine would
    # hold it, so this test runs even where the system cannot make one on disk.
    project, site = project
    assert send(project, site)[0] == 0
    target = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=project, input="../../../README.md",
                            capture_output=True, text=True, env=ENV).stdout.strip()
    git(project, "update-index", "--add", "--cacheinfo", f"120000,{target},{PUBLIC}readme.md")
    git(project, "commit", "-q", "-m", "a link out of the public folder")
    before = remote(site)
    code, out = send(project, site)
    assert code == 1, out
    assert out.startswith(f"REFUSE: {PUBLIC}readme.md is a symbolic link"), out
    assert remote(site) == before


def test_dry_run_says_what_would_cross_and_pushes_nothing(project):
    project, site = project
    code, out = send(project, site, "--dry-run")
    assert code == 0, out
    assert out.startswith("DRY RUN: would send 2 files"), out
    assert "css/site.css" in out and "index.html" in out, out
    assert remote(site) == ("", {})


def test_the_site_commit_takes_the_checkouts_own_identity_and_refuses_without_one(project, tmp_path):
    # As on Rhys's machine: no global git identity, only the checkout's own.
    project, site = project
    (tmp_path / "empty-global").write_text("", encoding="utf-8")
    bare = {**ENV, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(tmp_path / "empty-global")}
    for key in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"):
        bare.pop(key, None)
    git(project, "config", "--unset", "user.name")
    git(project, "config", "--unset", "user.email")
    code, out = send(project, site, env=bare)
    assert code == 1, out
    assert out.startswith("REFUSE: this checkout has no git user.name"), out
    assert remote(site) == ("", {})

    git(project, "config", "user.name", "Foundry North")
    git(project, "config", "user.email", "site@example.invalid")
    code, out = send(project, site, env=bare)
    assert code == 0, out
    assert out.startswith("SENT: "), out
    assert git(site, "log", "-1", "--format=%an <%ae> / %cn <%ce>", "main") ==         "Foundry North <site@example.invalid> / Foundry North <site@example.invalid>"
