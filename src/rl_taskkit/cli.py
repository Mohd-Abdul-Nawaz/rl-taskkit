"""Command-line interface for rl-taskkit."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import format_verification_lines, validation_report, verification_report, write_json
from .schema import TaskSpec, TaskSpecError, load_task
from .verifier import validate_task, verify_submission

EXIT_OK = 0
EXIT_VERIFICATION_FAILED = 1
EXIT_USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rl-taskkit",
        description="Reproducible RL environments for code-model training.",
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--tasks-dir",
        default="tasks",
        type=Path,
        help="directory containing task folders (default: ./tasks)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", parents=[common], help="list available tasks")

    run = sub.add_parser("run", parents=[common], help="verify a submission against a task")
    run.add_argument("task", help="task id (or a path to a task directory)")
    run.add_argument(
        "--submission",
        required=True,
        type=Path,
        help="directory containing the candidate solution",
    )
    run.add_argument("--report", type=Path, help="write a JSON report to this path")

    validate = sub.add_parser(
        "validate",
        parents=[common],
        help="check that tasks are well posed (golden passes, starter fails)",
    )
    validate.add_argument(
        "tasks",
        nargs="*",
        help="task ids to validate (default: all tasks in --tasks-dir)",
    )
    validate.add_argument("--report", type=Path, help="write a JSON report to this path")

    return parser


def _discover_task_dirs(tasks_dir: Path) -> list[Path]:
    if not tasks_dir.is_dir():
        return []
    return sorted(
        entry for entry in tasks_dir.iterdir() if entry.is_dir() and (entry / "task.yaml").is_file()
    )


def _resolve_task(tasks_dir: Path, token: str) -> TaskSpec:
    candidate = Path(token)
    if candidate.is_dir() and (candidate / "task.yaml").is_file():
        return load_task(candidate)
    return load_task(tasks_dir / token)


def cmd_list(tasks_dir: Path) -> int:
    task_dirs = _discover_task_dirs(tasks_dir)
    if not task_dirs:
        print(f"no tasks found in {tasks_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    width = max(len(entry.name) for entry in task_dirs)
    for entry in task_dirs:
        spec = load_task(entry)
        print(f"{spec.id:<{width}}  {spec.kind:<11}  {spec.language:<11}  {spec.title}")
    return EXIT_OK


def cmd_run(tasks_dir: Path, args: argparse.Namespace) -> int:
    try:
        spec = _resolve_task(tasks_dir, args.task)
    except TaskSpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    result = verify_submission(spec, args.submission)
    for line in format_verification_lines(result):
        print(line)
    if not result.passed and result.log:
        print("--- pytest output (tail) ---")
        print(result.log[-2000:])

    if args.report:
        write_json(verification_report(result), args.report)
        print(f"report written to {args.report}")

    return EXIT_OK if result.passed else EXIT_VERIFICATION_FAILED


def cmd_validate(tasks_dir: Path, args: argparse.Namespace) -> int:
    if args.tasks:
        try:
            task_dirs = [_resolve_task(tasks_dir, token).root for token in args.tasks]
        except TaskSpecError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return EXIT_USAGE_ERROR
    else:
        task_dirs = _discover_task_dirs(tasks_dir)
        if not task_dirs:
            print(f"no tasks found in {tasks_dir}", file=sys.stderr)
            return EXIT_USAGE_ERROR

    all_ok = True
    payloads = []
    for entry in task_dirs:
        try:
            spec = load_task(entry)
        except TaskSpecError as exc:
            print(f"INVALID {entry.name}: {exc}")
            all_ok = False
            continue
        result = validate_task(spec)
        payloads.append(validation_report(result))
        status = "OK  " if result.ok else "FAIL"
        golden = "pass" if result.golden_passed else "fail"
        initial = "rejected" if result.initial_rejected else "ACCEPTED(bug!)"
        print(f"{status} {spec.id:<30} golden={golden:<5} initial={initial}")
        for reason in result.reasons:
            print(f"       - {reason}")
        all_ok = all_ok and result.ok

    if args.report:
        write_json({"schema": "rl-taskkit.validation-bundle.v1", "tasks": payloads}, args.report)
        print(f"report written to {args.report}")

    return EXIT_OK if all_ok else EXIT_VERIFICATION_FAILED


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    tasks_dir = args.tasks_dir.resolve()

    if args.command == "list":
        return cmd_list(tasks_dir)
    if args.command == "run":
        return cmd_run(tasks_dir, args)
    if args.command == "validate":
        return cmd_validate(tasks_dir, args)
    parser.error(f"unknown command {args.command!r}")
    return EXIT_USAGE_ERROR


def console_main() -> None:
    """Entry point for the ``rl-taskkit`` console script (exits with the code)."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
