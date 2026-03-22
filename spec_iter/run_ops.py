"""Run operation helpers for Spec Iter."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from spec_iter.project import display_path


class RunOperationError(RuntimeError):
    """Raised when `spec-iter run` execution cannot proceed."""


WORKTREE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def validate_worktree_name(worktree: str) -> None:
    """Validate worktree name for path and branch usage."""
    if not WORKTREE_NAME_RE.fullmatch(worktree):
        raise ValueError(
            "Invalid worktree name "
            f"'{worktree}'. Use letters, numbers, dots, underscores, or hyphens."
        )


def get_worktree_path(project_root: Path, worktree: str) -> Path:
    """Return the managed path for a named worktree."""
    return project_root / ".speciter" / "worktrees" / worktree


def get_worktree_branch(worktree: str) -> str:
    """Return the managed branch name for a named worktree."""
    return f"agent/{worktree}"


def run_opencode(prompt: str, target_cwd: Path) -> None:
    """Execute an OpenCode operation prompt."""
    try:
        subprocess.run(
            ["opencode", "run", prompt],
            cwd=target_cwd,
            text=True,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "`opencode` CLI not found. Install OpenCode and ensure `opencode` is in PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        if not detail:
            detail = f"exit code {exc.returncode}"
        raise RunOperationError(f"`opencode run` failed ({detail})") from exc


def _run_git(
    project_root: Path, args: list[str], context: str
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Git is not available. Install git and ensure it is in PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
        raise RunOperationError(f"{context} ({detail})") from exc


def ensure_worktree_ready(project_root: Path, worktree: str) -> Path:
    """Ensure a managed worktree exists and is safe to reuse."""
    validate_worktree_name(worktree)

    worktree_path = get_worktree_path(project_root, worktree)
    branch_name = get_worktree_branch(worktree)

    if not worktree_path.exists():
        worktree_path.parent.mkdir(parents=True, exist_ok=True)
        _run_git(
            project_root,
            [
                "worktree",
                "add",
                worktree_path.as_posix(),
                "-b",
                branch_name,
                "main",
            ],
            (
                "Failed to create worktree "
                f"{display_path(worktree_path, project_root)} on branch {branch_name}"
            ),
        )
        return worktree_path

    if not worktree_path.is_dir():
        raise RunOperationError(
            f"Worktree path exists but is not a directory: {display_path(worktree_path, project_root)}"
        )

    branch_result = _run_git(
        worktree_path,
        ["branch", "--show-current"],
        (
            "Failed to read current branch for worktree "
            f"{display_path(worktree_path, project_root)}"
        ),
    )
    current_branch = branch_result.stdout.strip()
    if current_branch != branch_name:
        raise RunOperationError(
            "Worktree "
            f"{display_path(worktree_path, project_root)} is on branch '{current_branch}', "
            f"expected '{branch_name}'"
        )

    status_result = _run_git(
        worktree_path,
        ["status", "--porcelain"],
        (
            "Failed to inspect worktree status at "
            f"{display_path(worktree_path, project_root)}"
        ),
    )
    if status_result.stdout.strip():
        raise RunOperationError(
            f"Worktree {display_path(worktree_path, project_root)} is not clean"
        )

    return worktree_path
