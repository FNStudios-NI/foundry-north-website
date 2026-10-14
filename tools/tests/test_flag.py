# Tests for flag.py. Each test runs it from its own project folder in
# pytest's tmp_path, so no real run's flag is ever written.
#   python -B -m pytest template/tools/tests/test_flag.py -q

import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("flag", os.path.join(HERE, "..", "flag.py"))
flag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flag)


@pytest.fixture
def project(tmp_path, monkeypatch):
    for n in ("2", "10"):
        (tmp_path / "docs" / "runs" / n).mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def raise_flag(capsys, *args):
    code = flag.main(["flag.py", *args])
    return code, capsys.readouterr().out


@pytest.mark.parametrize("name", ["working", "needs-you", "handed-over", "done"])
def test_each_of_the_four_flags_is_written_in_tracks_form(project, capsys, name):
    code, out = raise_flag(capsys, name, "started the merge-check worker")
    assert code == 0 and out.startswith("FLAG: ")
    written = (project / "docs" / "runs" / "10" / "flag.txt").read_text(encoding="utf-8")
    assert re.fullmatch(rf"{name} \d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}Z started the merge-check worker\n", written)
    assert not (project / "docs" / "runs" / "2" / "flag.txt").exists()


def test_a_fifth_flag_is_refused_and_nothing_written(project, capsys):
    code, out = raise_flag(capsys, "paused", "waiting")
    assert code == 1 and out.startswith("REFUSE")
    assert not (project / "docs" / "runs" / "10" / "flag.txt").exists()


def test_a_new_flag_overwrites_the_old_one(project, capsys):
    raise_flag(capsys, "working", "started a worker")
    raise_flag(capsys, "handed-over", "the handover is written")
    lines = (project / "docs" / "runs" / "10" / "flag.txt").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and lines[0].startswith("handed-over ")


def test_the_why_is_kept_to_one_line_and_an_empty_why_is_refused(project, capsys):
    raise_flag(capsys, "needs-you", "the sign-off sitting\nis due")
    written = (project / "docs" / "runs" / "10" / "flag.txt").read_text(encoding="utf-8")
    assert written.endswith(" the sign-off sitting is due\n") and written.count("\n") == 1
    code, out = raise_flag(capsys, "done", "   ")
    assert code == 1 and out.startswith("REFUSE")


def test_no_run_folder_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out = raise_flag(capsys, "working", "go")
    assert code == 1 and out.startswith("REFUSE")
