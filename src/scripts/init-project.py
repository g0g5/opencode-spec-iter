#!/usr/bin/env python3
"""
Agent initialization script for setting up .agent/ directory and project files.
Assumes project root is the current working directory (where python is invoked).
"""

import subprocess
from pathlib import Path


def create_agent_directory():
    """Create .agent/ directory with sub-directories in project root."""
    agent_dir = Path.cwd() / ".agent"

    subdirs = ["iterations"]

    for subdir in subdirs:
        full_path = agent_dir / subdir
        full_path.mkdir(parents=True, exist_ok=True)


def init_git_repo():
    """
    Try to init local git repo. If already exists, check git status and report.
    """
    project_root = Path.cwd()
    git_dir = project_root / ".git"

    if git_dir.exists():
        return

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return


def rename_opencode_gitignore():
    """Rename .opencode/gitignore to .opencode/.gitignore if present."""
    opencode_dir = Path.cwd() / ".opencode"
    source = opencode_dir / "gitignore"
    target = opencode_dir / ".gitignore"

    if not source.exists():
        return

    if target.exists():
        return

    source.rename(target)


def main():
    """Main entry point."""
    create_agent_directory()
    rename_opencode_gitignore()
    init_git_repo()
    print("Spec Iter plugin is ready to use.")


if __name__ == "__main__":
    main()
