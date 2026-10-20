"""rl-taskkit: reproducible RL environments for code-model training."""

__version__ = "0.1.0"

from .schema import TaskSpec, TaskSpecError, load_task
from .verifier import TaskValidationResult, VerificationResult, validate_task, verify_submission

__all__ = [
    "TaskSpec",
    "TaskSpecError",
    "TaskValidationResult",
    "VerificationResult",
    "load_task",
    "validate_task",
    "verify_submission",
    "__version__",
]
