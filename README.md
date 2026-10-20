# rl-taskkit

Reproducible **RL environments for training code models**: every task ships a
prompt, buggy starter code, a golden reference solution, and a deterministic
test suite. A sandboxed verifier grades submissions and emits machine-readable
verdicts that can be used directly as reward signals.

## Why this exists

Training models to fix bugs, add features, refactor, and optimize code requires
environments that are:

- **reproducible** — pinned seeds, fixed timezone, isolated temp workspaces,
  no pytest cache plugins;
- **well posed** — every task is proven solvable (golden passes) and
  non-trivial (starter fails), checked automatically by `validate`;
- **machine-readable** — JSON verdicts with test counts, durations and error
  snippets.

## Task anatomy

```
tasks/<task-id>/
  task.yaml        # id, title, language, kind, entry_point, timeouts
  prompt.md        # what the model sees
  initial/         # buggy starter code shown to the model
  golden/          # reference solution (used by `validate`, hidden otherwise)
  tests/           # hidden test suite (including performance budgets)
```

Supported kinds: `bug_fix`, `feature`, `refactor`, `performance`.

## Quick start

```bash
pip install -e .

# list tasks
rl-taskkit list

# run the starter code (should FAIL - that is the point)
rl-taskkit run bugfix-string-normalizer --submission tasks/bugfix-string-normalizer/initial

# run the golden solution (should PASS)
rl-taskkit run bugfix-string-normalizer --submission tasks/bugfix-string-normalizer/golden

# verify all tasks are well posed, with a machine-readable report
rl-taskkit validate --report validation.json

# unit-test the harness itself (also runs every task's well-posedness check)
pytest -q
```

Exit codes: `0` = pass / all valid, `1` = submission failed / invalid task,
`2` = usage error.

## Bundled seed tasks

| task id                  | kind        | idea                                             |
| ------------------------ | ----------- | ------------------------------------------------ |
| `bugfix-string-normalizer` | bug_fix   | off-by-whitespace, missing `ValueError` handling |
| `feature-lru-cache`        | feature   | complete an O(1) LRU with deterministic eviction |
| `perf-doc-freq`            | performance | O(V·N·L) → O(total tokens) with a 1 s budget   |

## Adding a new task

1. Copy one of the seed tasks to `tasks/<new-id>/`.
2. Fill in `task.yaml`, `prompt.md`, put the buggy code in `initial/`, the
   reference solution in `golden/`, and the hidden tests in `tests/`.
3. Run `rl-taskkit validate <new-id>` until it reports `OK` — the golden
   solution must pass and the starter must fail.

## Reproducibility guarantees

Every verification runs `pytest` in a fresh temporary directory with
`PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `TZ=UTC`, and
`PYTHONPATH` pointing only at the sandbox. Per-task timeouts are enforced with
`subprocess` timeouts and reported as `timed_out` verdicts (not silent
successes).

## Docker

```bash
docker build -t rl-taskkit .
docker run --rm rl-taskkit validate --tasks-dir /app/tasks
```

## License

MIT — see `LICENSE`.
