"""Deterministic, sandboxed pytest execution."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

MAX_ERROR_SNIPPETS = 10


@dataclass
class RunResult:
    """Outcome of one sandboxed pytest run."""

    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    duration_seconds: float = 0.0
    timed_out: bool = False
    passed: bool = False
    errors: list[str] = field(default_factory=list)
    log: str = ""


def pinned_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Return a copy of ``os.environ`` pinned for reproducible runs."""
    env = os.environ.copy()
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONUTF8": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TZ": "UTC",
        }
    )
    if extra:
        env.update(extra)
    return env


def run_pytest(
    code_dir: str | Path,
    tests_dir: str | Path,
    timeout_seconds: int = 60,
    workdir: str | Path | None = None,
) -> RunResult:
    """Copy *code_dir* and *tests_dir* into a sandbox and run pytest there."""
    code_dir = Path(code_dir).resolve()
    tests_dir = Path(tests_dir).resolve()
    owned = workdir is None
    sandbox = Path(workdir).resolve() if workdir else Path(tempfile.mkdtemp(prefix="rl-taskkit-"))

    try:
        sandbox.mkdir(parents=True, exist_ok=True)
        shutil.copytree(code_dir, sandbox, dirs_exist_ok=True)
        shutil.copytree(tests_dir, sandbox / "tests", dirs_exist_ok=True)

        junit_path = sandbox / "junitxml-report.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "--junitxml",
            str(junit_path),
            "-p",
            "no:cacheprovider",
        ]
        try:
            proc = subprocess.run(
                command,
                cwd=sandbox,
                env=pinned_env({"PYTHONPATH": str(sandbox)}),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                duration_seconds=float(timeout_seconds),
                timed_out=True,
                passed=False,
                errors=[f"submission exceeded the {timeout_seconds}s time budget"],
                log=_decode(exc.stdout) + _decode(exc.stderr),
            )

        log = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return _parse_junit(junit_path, log)
    finally:
        if owned:
            shutil.rmtree(sandbox, ignore_errors=True)


def _decode(chunk: str | bytes | None) -> str:
    if chunk is None:
        return ""
    if isinstance(chunk, bytes):
        return chunk.decode("utf-8", errors="replace")
    return chunk


def _parse_junit(junit_path: Path, log: str) -> RunResult:
    if not junit_path.is_file():
        return RunResult(passed=False, errors=["pytest produced no JUnit report"], log=log)

    try:
        root = ET.parse(junit_path).getroot()
    except ET.ParseError as exc:
        return RunResult(passed=False, errors=[f"unreadable JUnit report: {exc}"], log=log)

    suites = list(root.iter("testsuite"))
    if suites:
        tests = sum(int(s.attrib.get("tests", 0)) for s in suites)
        failures = sum(int(s.attrib.get("failures", 0)) for s in suites)
        errors = sum(int(s.attrib.get("errors", 0)) for s in suites)
        try:
            duration = sum(float(s.attrib.get("time", 0.0)) for s in suites)
        except ValueError:
            duration = 0.0
    else:
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        try:
            duration = float(root.attrib.get("time", 0.0))
        except ValueError:
            duration = 0.0

    snippets: list[str] = []
    for case in root.iter("testcase"):
        for tag in ("failure", "error"):
            node = case.find(tag)
            if node is not None and len(snippets) < MAX_ERROR_SNIPPETS:
                message = node.attrib.get("message", "").strip().splitlines()
                head = message[0] if message else tag
                classname = case.attrib.get("classname", "?")
                name = case.attrib.get("name", "?")
                snippets.append(f"{classname}::{name}: {head}")

    if tests == 0:
        snippets.append("no tests were collected - check the entry point imports cleanly")

    passed = tests > 0 and failures == 0 and errors == 0
    return RunResult(
        tests_total=tests,
        tests_passed=max(tests - failures - errors, 0),
        tests_failed=failures + errors,
        duration_seconds=duration,
        passed=passed,
        errors=snippets,
        log=log,
    )
