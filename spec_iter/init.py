"""Project initialization and bundled command installation."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


MANAGED_COMMAND_FILES = (
    "agentsmd.md",
    "exec.md",
    "list-iters.md",
    "plan.md",
    "post.md",
    "spec.md",
)

LEGACY_SCRIPT_FILES = {
    "iter_manager.py",
    "prompt-agentsmd.py",
    "prompt-exec.py",
    "prompt-plan.py",
    "prompt-post.py",
}


@dataclass
class InitResult:
    project_root: Path
    commands_dir: Path
    removed_legacy_scripts: bool = False
    legacy_scripts_dir: Path | None = None
    warnings: list[str] = field(default_factory=list)


def _bundled_commands_dir() -> Path:
    return Path(__file__).resolve().parent / "commands"


def _append_gitignore_entries(gitignore_path: Path, entries: list[str]) -> None:
    existing_text = (
        gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    )
    existing_entries = set(existing_text.splitlines())
    new_entries = [entry for entry in entries if entry not in existing_entries]

    if not new_entries:
        return

    with gitignore_path.open("a", encoding="utf-8") as handle:
        if existing_text and not existing_text.endswith("\n"):
            handle.write("\n")
        for entry in new_entries:
            handle.write(f"{entry}\n")


def _install_managed_commands(project_root: Path) -> Path:
    source_dir = _bundled_commands_dir()
    commands_dir = project_root / ".opencode" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    for filename in MANAGED_COMMAND_FILES:
        shutil.copyfile(source_dir / filename, commands_dir / filename)

    return commands_dir


def _ensure_speciter_state(project_root: Path) -> None:
    speciter_dir = project_root / ".speciter"
    iterations_dir = speciter_dir / "iterations"
    docs_dir = speciter_dir / "docs"
    iterations_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    iters_file = speciter_dir / "iters.json"
    if not iters_file.exists():
        iters_file.write_text('{"iterations": []}\n', encoding="utf-8")


def _cleanup_legacy_scripts(
    project_root: Path, warnings: list[str]
) -> tuple[bool, Path | None]:
    scripts_dir = project_root / ".opencode" / "scripts"
    if not scripts_dir.exists() or not scripts_dir.is_dir():
        return False, None

    unknown_entries = []
    for entry in scripts_dir.iterdir():
        if entry.is_dir() and entry.name == "__pycache__":
            continue
        if entry.is_file() and entry.name in LEGACY_SCRIPT_FILES:
            continue
        unknown_entries.append(entry.name)

    if unknown_entries:
        warnings.append(
            ".opencode/scripts contains unmanaged files; leaving it in place "
            f"({', '.join(sorted(unknown_entries))})"
        )
        return False, scripts_dir

    shutil.rmtree(scripts_dir)
    return True, scripts_dir


def _maybe_init_git(project_root: Path, warnings: list[str]) -> None:
    if (project_root / ".git").exists():
        return

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        warnings.append("git is not available; skipped `git init`")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
        warnings.append(f"`git init` failed; continuing ({detail})")


def initialize_project(target_path: Path) -> InitResult:
    project_root = target_path.expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    _ensure_speciter_state(project_root)
    commands_dir = _install_managed_commands(project_root)
    _append_gitignore_entries(
        project_root / ".gitignore",
        [".opencode/commands/"],
    )
    removed_legacy_scripts, legacy_scripts_dir = _cleanup_legacy_scripts(
        project_root,
        warnings,
    )
    _maybe_init_git(project_root, warnings)

    return InitResult(
        project_root=project_root,
        commands_dir=commands_dir,
        removed_legacy_scripts=removed_legacy_scripts,
        legacy_scripts_dir=legacy_scripts_dir,
        warnings=warnings,
    )
