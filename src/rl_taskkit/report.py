"""Machine-readable verification reports."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .verifier import TaskValidationResult, VerificationResult

LOG_TAIL_LIMIT = 4000


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def verification_report(result: VerificationResult) -> dict[str, Any]:
    """Convert a :class:`VerificationResult` into a JSON-serializable dict."""
    return {
        "schema": "rl-taskkit.verification-report.v1",
        "generated_at": _timestamp(),
        "task_id": result.task_id,
        "source": result.source,
        "passed": result.passed,
        "timed_out": result.timed_out,
        "tests": {
            "total": result.tests_total,
            "passed": result.tests_passed,
            "failed": result.tests_failed,
        },
        "duration_seconds": round(result.duration_seconds, 4),
        "errors": list(result.errors),
        "log_tail": result.log[-LOG_TAIL_LIMIT:],
    }


def validation_report(result: TaskValidationResult) -> dict[str, Any]:
    """Convert a :class:`TaskValidationResult` into a JSON-serializable dict."""
    return {
        "schema": "rl-taskkit.task-validation-report.v1",
        "generated_at": _timestamp(),
        "task_id": result.task_id,
        "ok": result.ok,
        "golden_passed": result.golden_passed,
        "initial_rejected": result.initial_rejected,
        "reasons": list(result.reasons),
    }


def write_json(payload: dict[str, Any], path: str | Path) -> None:
    """Write *payload* as pretty-printed UTF-8 JSON."""
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_verification_lines(result: VerificationResult) -> list[str]:
    """Human-readable summary lines for one verification result."""
    status = "PASS" if result.passed else "TIMEOUT" if result.timed_out else "FAIL"
    lines = [
        f"task      : {result.task_id}",
        f"source    : {result.source}",
        f"verdict   : {status}",
        f"tests     : {result.tests_passed}/{result.tests_total} passed"
        + (f", {result.tests_failed} failed" if result.tests_failed else ""),
        f"duration  : {result.duration_seconds:.3f}s",
    ]
    if result.errors:
        lines.append("errors    :")
        lines.extend(f"  - {err}" for err in result.errors)
    return lines
