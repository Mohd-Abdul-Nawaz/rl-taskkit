"""Allow ``python -m rl_taskkit``."""
import sys

from .cli import main

sys.exit(main())
