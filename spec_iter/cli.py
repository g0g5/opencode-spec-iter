#!/usr/bin/env python3
"""Install the Spec Iter plugin to a target directory."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_source_directory() -> Path:
    """Resolve plugin source directory from packaged assets."""
    package_dir = Path(__file__).resolve().parent
    bundled_src = package_dir / "bundled_src"
    if bundled_src.exists():
        return bundled_src

    raise FileNotFoundError("Could not locate bundled plugin source files.")


def create_agent_directory(project_root: Path) -> None:
    """Create .speciter/ directory with required defaults in project root."""
    speciter_dir = project_root / ".speciter"
    print(f"Ensuring agent directory exists: {speciter_dir}")

    iteration_dir = speciter_dir / "iterations"
    iteration_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {iteration_dir}")

    iters_file = speciter_dir / "iters.json"
    if not iters_file.exists():
        iters_file.write_text('{"iterations": []}', encoding="utf-8")
        print(f"Created file: {iters_file}")
    else:
        print(f"File already exists: {iters_file}")


def init_git_repo(project_root: Path) -> None:
    """Initialize git repository when missing."""
    git_dir = project_root / ".git"
    if git_dir.exists():
        print(f"Git repository already exists: {git_dir}")
        return

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Initialized git repository in: {project_root}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Skipped git initialization.")


def get_target_directory(argv: list[str]) -> Path:
    """Return target directory from CLI arg or interactive prompt."""
    if len(argv) > 2:
        print("Error: Too many arguments.")
        print(f"Usage: {Path(argv[0]).name} [target_directory]")
        raise SystemExit(1)

    if len(argv) == 2:
        target_input = argv[1].strip()
    else:
        target_input = input("Enter target directory path: ").strip()

    if not target_input:
        print("Error: No target directory provided.")
        raise SystemExit(1)

    return Path(target_input).expanduser().resolve()


def _append_gitignore_entries(gitignore_path: Path, entries: list[str]) -> None:
    existing_text = ""
    existing_entries: set[str] = set()

    if gitignore_path.exists():
        existing_text = gitignore_path.read_text(encoding="utf-8")
        existing_entries = set(existing_text.splitlines())

    new_entries = [entry for entry in entries if entry not in existing_entries]
    if not new_entries:
        return

    with gitignore_path.open("a", encoding="utf-8") as file:
        if existing_text and not existing_text.endswith("\n"):
            file.write("\n")
        for entry in new_entries:
            file.write(f"{entry}\n")

    print(f"Updated .gitignore with: {', '.join(new_entries)}")


def run(argv: list[str]) -> int:
    print("Spec Iter Plugin Installer")
    print("=" * 40)

    target_path = get_target_directory(argv)
    src_path = _resolve_source_directory()
    dest_path = target_path / ".opencode"

    if not target_path.exists():
        create = (
            input(f"Target directory does not exist. Create it? (y/n): ")
            .strip()
            .lower()
        )
        if create == "y":
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {target_path}")
        else:
            print("Installation cancelled.")
            return 0

    if dest_path.exists():
        overwrite = (
            input(".opencode already exists. Overwrite? (y/n): ").strip().lower()
        )
        if overwrite != "y":
            print("Installation cancelled.")
            return 0
        shutil.rmtree(dest_path)

    shutil.copytree(src_path, dest_path)

    gitignore_path = target_path / ".gitignore"
    entries_to_add = [".speciter/", ".opencode/commands/", ".opencode/scripts/"]
    _append_gitignore_entries(gitignore_path, entries_to_add)

    print(f"\nInstalled to: {dest_path}")
    print("Installation complete!")

    print("\nInitializing project...")
    create_agent_directory(target_path)
    init_git_repo(target_path)
    print("Spec Iter plugin is ready to use.")
    return 0


def main() -> int:
    """Console script entrypoint."""
    return run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
