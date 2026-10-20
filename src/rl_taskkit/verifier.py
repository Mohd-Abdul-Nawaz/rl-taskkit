"""Verification of submissions and validation of task well-posedness."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .runner import RunResult, run_pytest
from .schema import TaskSpec


@dataclass
class VerificationResult:
    task_id: str
    source: str
    passed: bool
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    duration_seconds: float = 0.0
    timed_out: bool = False
    errors: list[str] = field(default_factory=list)
    log: str = ""


@dataclass
class TaskValidationResult:
    task_id: str
    ok: bool
    golden_passed: bool
    initial_rejected: bool
    reasons: list[str] = field(default_factory=list)


def verify_submission(
    spec: TaskSpec,
    submission_dir: str | Path,
    timeout_seconds: int | None = None,
) -> VerificationResult:
    """Run the task's test suite against a candidate submission directory."""
    submission_dir = Path(submission_dir).resolve()
    if not submission_dir.is_dir():
        return _rejected(spec, f"submission directory not found: {submission_dir}")

    if not (submission_dir / spec.entry_point).is_file():
        return _rejected(spec, f"submission is missing the entry point {spec.entry_point!r}")

    run = run_pytest(submission_dir, spec.tests_dir, timeout_seconds or spec.timeout_seconds)
    return _from_run(spec, run, source="submission")


def _rejected(spec: TaskSpec, reason: str) -> VerificationResult:
    return VerificationResult(
        task_id=spec.id,
        source="submission",
        passed=False,
        errors=[reason],
    )


def _from_run(spec: TaskSpec, run: RunResult, source: str) -> VerificationResult:
    return VerificationResult(
        task_id=spec.id,
        source=source,
        passed=run.passed,
        tests_total=run.tests_total,
        tests_passed=run.tests_passed,
        tests_failed=run.tests_failed,
        duration_seconds=run.duration_seconds,
        timed_out=run.timed_out,
        errors=list(run.errors),
        log=run.log,
    )


def validate_task(spec: TaskSpec) -> TaskValidationResult:
    """Check that a task is well posed: the golden solution passes and the
    starter code fails."""
    golden = run_pytest(spec.golden_dir, spec.tests_dir, spec.timeout_seconds)
    initial = run_pytest(spec.initial_dir, spec.tests_dir, spec.timeout_seconds)

    reasons: list[str] = []
    if not golden.passed:
        reasons.append("golden solution does not pass the test suite")
        reasons.extend(f"  golden: {err}" for err in golden.errors[:3])
    if initial.passed:
        reasons.append("starter code already passes the test suite (degenerate task)")
    if initial.timed_out:
        reasons.append("starter code timed out; keep the slow path under the task timeout")

    return TaskValidationResult(
        task_id=spec.id,
        ok=golden.passed and not initial.passed,
        golden_passed=golden.passed,
        initial_rejected=not initial.passed,
        reasons=reasons,
    )
