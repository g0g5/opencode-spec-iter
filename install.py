#!/usr/bin/env python3
"""Install the Spec Agents plugin to a target directory."""

import shutil
import sys
from pathlib import Path


def main():
    print("Spec Agents Plugin Installer")
    print("=" * 40)

    target_input = input("Enter target directory path: ").strip()

    if not target_input:
        print("Error: No target directory provided.")
        sys.exit(1)

    target_path = Path(target_input).expanduser().resolve()
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
    entries_to_add = [".agent/", ".opencode/commands/", ".opencode/scripts/"]

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


if __name__ == "__main__":
    main()
