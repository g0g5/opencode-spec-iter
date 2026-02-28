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
    print(f"\nInstalled to: {dest_path}")
    print("Installation complete!")


if __name__ == "__main__":
    main()
