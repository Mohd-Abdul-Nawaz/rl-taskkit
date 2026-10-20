"""End-to-end tests: every bundled task must be well posed, and the CLI must work."""
import json
from pathlib import Path

import pytest

from rl_taskkit.cli import main
from rl_taskkit.report import verification_report
from rl_taskkit.schema import load_task
from rl_taskkit.verifier import validate_task, verify_submission

REPO = Path(__file__).resolve().parents[1]
TASKS = REPO / "tasks"


def task_dirs() -> list[Path]:
    return sorted(entry for entry in TASKS.iterdir() if (entry / "task.yaml").is_file())


@pytest.mark.parametrize("task_dir", task_dirs(), ids=lambda entry: entry.name)
def test_every_task_is_well_posed(task_dir: Path):
    spec = load_task(task_dir)
    result = validate_task(spec)
    assert result.ok, result.reasons


def test_verify_rejects_missing_entry_point(tmp_path: Path):
    spec = load_task(task_dirs()[0])
    (tmp_path / "wrong_file.py").write_text("x = 1\n", encoding="utf-8")
    result = verify_submission(spec, tmp_path)
    assert not result.passed
    assert any("entry point" in err for err in result.errors)


def test_verification_report_is_json_serializable():
    spec = load_task(task_dirs()[0])
    result = verify_submission(spec, spec.initial_dir)
    payload = verification_report(result)
    json.dumps(payload)  # must not raise
    assert payload["task_id"] == spec.id


def test_cli_list_tasks(capsys):
    code = main(["list", "--tasks-dir", str(TASKS)])
    out = capsys.readouterr().out
    assert code == 0
    assert "bugfix-string-normalizer" in out


def test_cli_run_golden_passes(capsys):
    task_dir = TASKS / "bugfix-string-normalizer"
    spec = load_task(task_dir)
    code = main(
        [
            "run",
            "bugfix-string-normalizer",
            "--submission",
            str(spec.golden_dir),
            "--tasks-dir",
            str(TASKS),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "PASS" in out


def test_cli_run_starter_fails(capsys):
    task_dir = TASKS / "bugfix-string-normalizer"
    spec = load_task(task_dir)
    code = main(
        [
            "run",
            "bugfix-string-normalizer",
            "--submission",
            str(spec.initial_dir),
            "--tasks-dir",
            str(TASKS),
        ]
    )
    assert code == 1


def test_cli_validate_all(capsys):
    code = main(["validate", "--tasks-dir", str(TASKS)])
    out = capsys.readouterr().out
    assert code == 0
    assert out.count("OK  ") == 3
