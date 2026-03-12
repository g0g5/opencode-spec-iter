#!/usr/bin/env python3
"""Install the Spec Iter plugin to a target directory."""

import shutil
import subprocess
import sys
from pathlib import Path


def create_agent_directory(project_root: Path):
    """Create .speciter/ directory with sub-directories in project root."""
    speciter_dir = project_root / ".speciter"
    print(f"Ensuring agent directory exists: {speciter_dir}")

    subdirs = ["iterations"]

    for subdir in subdirs:
        full_path = speciter_dir / subdir
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")

    # Create iters.json with empty iterations array
    iters_file = speciter_dir / "iters.json"
    if not iters_file.exists():
        iters_file.write_text('{"iterations": []}')
        print(f"Created file: {iters_file}")
    else:
        print(f"File already exists: {iters_file}")


def init_git_repo(project_root: Path):
    """Try to init local git repo. If already exists, skip."""
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
        return


def get_target_directory() -> Path:
    """Return target directory from CLI arg or interactive prompt."""
    if len(sys.argv) > 2:
        print("Error: Too many arguments.")
        print(f"Usage: python {Path(__file__).name} [target_directory]")
        sys.exit(1)

    if len(sys.argv) == 2:
        target_input = sys.argv[1].strip()
    else:
        target_input = input("Enter target directory path: ").strip()

    if not target_input:
        print("Error: No target directory provided.")
        sys.exit(1)

    return Path(target_input).expanduser().resolve()


def main():
    print("Spec Iter Plugin Installer")
    print("=" * 40)

    target_path = get_target_directory()
    src_path = Path(__file__).parent / "src"
    dest_path = target_path / ".opencode"

    if not src_path.exists():
        print(f"Error: Source directory not found: {src_path}")
        sys.exit(1)

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
            sys.exit(0)

    if dest_path.exists():
        overwrite = (
            input(f".opencode already exists. Overwrite? (y/n): ").strip().lower()
        )
        if overwrite != "y":
            print("Installation cancelled.")
            sys.exit(0)
        shutil.rmtree(dest_path)

    shutil.copytree(src_path, dest_path)

    gitignore_path = target_path / ".gitignore"
    entries_to_add = [".speciter/", ".opencode/commands/", ".opencode/scripts/"]

    existing_entries = set()
    if gitignore_path.exists():
        existing_entries = set(gitignore_path.read_text().splitlines())

    new_entries = [e for e in entries_to_add if e not in existing_entries]
    if new_entries:
        with open(gitignore_path, "a") as f:
            if existing_entries and not list(existing_entries)[-1].endswith("\n"):
                f.write("\n")
            for entry in new_entries:
                f.write(f"{entry}\n")
        print(f"Updated .gitignore with: {', '.join(new_entries)}")

    print(f"\nInstalled to: {dest_path}")
    print("Installation complete!")

    # Initialize project after installation
    print("\nInitializing project...")
    create_agent_directory(target_path)
    init_git_repo(target_path)
    print("Spec Iter plugin is ready to use.")


if __name__ == "__main__":
    main()
