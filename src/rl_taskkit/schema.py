"""Task specification loading and validation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_KINDS = ("bug_fix", "feature", "refactor", "performance")


class TaskSpecError(ValueError):
    """Raised when a task directory does not contain a valid specification."""


@dataclass(frozen=True)
class TaskSpec:
    """A loaded, structurally-validated task."""

    id: str
    title: str
    language: str
    kind: str
    entry_point: str
    root: Path
    timeout_seconds: int = 60
    perf_budget_ms: int | None = None

    @property
    def golden_dir(self) -> Path:
        return self.root / "golden"

    @property
    def initial_dir(self) -> Path:
        return self.root / "initial"

    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"

    @property
    def prompt_path(self) -> Path:
        return self.root / "prompt.md"


def load_task(task_dir: str | Path) -> TaskSpec:
    """Load ``task.yaml`` from *task_dir* and validate the task layout."""
    root = Path(task_dir).resolve()
    meta_path = root / "task.yaml"
    if not meta_path.is_file():
        raise TaskSpecError(f"{root}: no task.yaml found")

    data: Any = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise TaskSpecError(f"{meta_path}: task.yaml must contain a mapping")

    required = ("id", "title", "language", "kind", "entry_point")
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise TaskSpecError(f"{meta_path}: missing required fields: {', '.join(missing)}")

    kind = str(data["kind"])
    if kind not in SUPPORTED_KINDS:
        supported = ", ".join(SUPPORTED_KINDS)
        raise TaskSpecError(f"{meta_path}: unsupported kind {kind!r} (expected one of {supported})")

    timeout_seconds = int(data.get("timeout_seconds", 60))
    if timeout_seconds <= 0:
        raise TaskSpecError(f"{meta_path}: timeout_seconds must be positive")

    perf_budget_ms: int | None = None
    if data.get("perf_budget_ms") is not None:
        perf_budget_ms = int(data["perf_budget_ms"])
        if perf_budget_ms <= 0:
            raise TaskSpecError(f"{meta_path}: perf_budget_ms must be positive")

    spec = TaskSpec(
        id=str(data["id"]),
        title=str(data["title"]),
        language=str(data["language"]),
        kind=kind,
        entry_point=str(data["entry_point"]),
        root=root,
        timeout_seconds=timeout_seconds,
        perf_budget_ms=perf_budget_ms,
    )

    for name in ("golden", "initial", "tests"):
        if not (root / name).is_dir():
            raise TaskSpecError(f"{root}: missing required directory {name!r}")
    for side in (spec.golden_dir, spec.initial_dir):
        if not (side / spec.entry_point).is_file():
            raise TaskSpecError(
                f"{root}: entry point {spec.entry_point!r} missing from {side.name!r}"
            )
    if not any(spec.tests_dir.glob("test_*.py")):
        raise TaskSpecError(f"{root}: tests/ must contain at least one test_*.py file")
    if not spec.prompt_path.is_file():
        raise TaskSpecError(f"{root}: missing prompt.md")
    return spec
