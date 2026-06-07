"""Bootstrap helpers for running scripts from the repo root."""

from __future__ import annotations

import sys
from pathlib import Path


def add_repo_root() -> Path:
    """Ensure the repository root is available on sys.path."""
    repo_root = Path(__file__).resolve().parents[1]
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return repo_root
