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
        print(f"Created: {full_path}")

    print(f"Agent directory structure created at: {agent_dir}")


def init_git_repo():
    """
    Try to init local git repo. If already exists, check git status and report.
    """
    project_root = Path.cwd()
    git_dir = project_root / ".git"

    if git_dir.exists():
        print(f"[INFO] Git repository already exists at: {project_root}")

        # Check git status
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                print("[GIT STATUS] Uncommitted changes:")
                print(result.stdout)
            else:
                print("[GIT STATUS] Working tree clean - no uncommitted changes.")

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to check git status: {e}")
    else:
        # Initialize git repo
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"[CREATED] Git repository initialized at: {project_root}")
            print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to initialize git repository: {e}")
        except FileNotFoundError:
            print("[ERROR] Git not found. Please install git.")


def main():
    """Main entry point."""
    print(f"Agent Initialization Script")
    print(f"Project root (cwd): {Path.cwd()}")
    print("-" * 50)

    create_agent_directory()
    print()

    init_git_repo()
    print()

    print("-" * 50)
    print("Initialization complete!")


if __name__ == "__main__":
    main()
