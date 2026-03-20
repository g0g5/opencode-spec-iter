"""Project root discovery and user-facing path helpers."""

from __future__ import annotations

import os
from pathlib import Path


class ProjectNotInitializedError(FileNotFoundError):
    """Raised when no Spec Iter project can be located."""


def find_project_root(start: Path | None = None) -> Path:
    """Locate the nearest initialized Spec Iter project from ``start`` upward."""
    current = (start or Path.cwd()).resolve()

    for candidate in (current, *current.parents):
        speciter_dir = candidate / ".speciter"
        if speciter_dir.is_dir() or (speciter_dir / "iters.json").exists():
            return candidate

    raise ProjectNotInitializedError(
        "No Spec Iter project found from the current directory. Run `spec-iter init`."
    )


def display_path(path: Path, start: Path | None = None) -> str:
    """Return a cwd-relative path when possible, otherwise an absolute POSIX path."""
    base = (start or Path.cwd()).resolve()
    target = path.resolve()

    try:
        return Path(os.path.relpath(target, base)).as_posix()
    except ValueError:
        return target.as_posix()
