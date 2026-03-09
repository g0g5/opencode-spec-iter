#!/usr/bin/env python3
"""Iteration manager for spec-driven development workflow."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

SPECITER_DIR = Path(".speciter")
ITERS_FILE = SPECITER_DIR / "iters.json"
ITERATIONS_DIR = SPECITER_DIR / "iterations"

VALID_STAGES = ["new", "spec", "plan", "execute", "post", "completed"]


def to_kebab_case(name: str) -> str:
    """Convert string to lowercase kebab-case."""
    # Replace non-alphanumeric with hyphens, collapse multiple hyphens
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    # Remove leading/trailing hyphens
    name = name.strip("-")
    # Lowercase
    return name.lower()


def load_iters() -> dict:
    """Load iters.json or return empty structure."""
    if ITERS_FILE.exists():
        with open(ITERS_FILE, "r") as f:
            return json.load(f)
    return {"iterations": []}


def save_iters(data: dict):
    """Save iters.json."""
    SPECITER_DIR.mkdir(parents=True, exist_ok=True)
    with open(ITERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def cmd_new(name: str):
    """Create a new iteration."""
    kebab_name = to_kebab_case(name)
    if not kebab_name:
        print(f"Error: Invalid iteration name '{name}'")
        sys.exit(1)

    # Create directories
    iteration_dir = ITERATIONS_DIR / kebab_name
    iteration_dir.mkdir(parents=True, exist_ok=True)

    # Load and update iters.json
    data = load_iters()

    # Check for duplicate names
    for it in data.get("iterations", []):
        if it["name"] == kebab_name:
            print(f"Error: Iteration '{kebab_name}' already exists")
            sys.exit(1)

    # Add new iteration
    timestamp = datetime.now().isoformat()
    new_iter = {"time": timestamp, "name": kebab_name, "stage": "new"}
    data["iterations"].append(new_iter)

    # Sort by timestamp, most recent first
    data["iterations"].sort(key=lambda x: x["time"], reverse=True)

    save_iters(data)
    print(f"Created iteration: {kebab_name}")
    print(f"Directory: {iteration_dir}")


def cmd_list(n: Optional[int] = None):
    """List iterations sorted by timestamp."""
    verify_iters_file_exists()
    data = load_iters()
    iterations = data.get("iterations", [])

    if not iterations:
        print("No iterations found")
        return

    # Already sorted by timestamp (most recent first)
    if n is not None:
        iterations = iterations[:n]

    for it in iterations:
        print(f"{it['name']} ({it['stage']})")


def get_iteration_path(iter_id: str) -> Path:
    """Get iteration directory path by ID (name)."""
    return ITERATIONS_DIR / iter_id


def verify_iters_file_exists():
    """Check if iters.json exists, exit with error if not."""
    if not ITERS_FILE.exists():
        print(
            "Error: iters.json not found. Run 'iter-manager new <name>' to create the first iteration."
        )
        sys.exit(1)


def verify_iteration_exists(iter_id: str) -> bool:
    """Check if iteration exists in iters.json."""
    verify_iters_file_exists()
    data = load_iters()
    for it in data.get("iterations", []):
        if it["name"] == iter_id:
            return True
    return False


def cmd_spec(iter_id: str):
    """Print SPEC.md path or error."""
    if not verify_iteration_exists(iter_id):
        print(f"Error: Iteration '{iter_id}' not found")
        sys.exit(1)

    spec_path = get_iteration_path(iter_id) / "SPEC.md"
    if spec_path.exists():
        print(spec_path)
    else:
        print(f"Error: SPEC.md not found of {iter_id}")


def cmd_plan(iter_id: str):
    """Print PLAN.md path or error."""
    if not verify_iteration_exists(iter_id):
        print(f"Error: Iteration '{iter_id}' not found")
        sys.exit(1)

    plan_path = get_iteration_path(iter_id) / "PLAN.md"
    if plan_path.exists():
        print(plan_path)
    else:
        print(f"Error: PLAN.md not found of {iter_id}")


def cmd_update(iter_id: str, stage: str):
    """Update iteration stage."""
    verify_iters_file_exists()
    if stage not in VALID_STAGES:
        print(
            f"Error: Invalid stage '{stage}'. Valid stages: {', '.join(VALID_STAGES)}"
        )
        sys.exit(1)

    data = load_iters()
    found = False

    for it in data.get("iterations", []):
        if it["name"] == iter_id:
            it["stage"] = stage
            it["time"] = datetime.now().isoformat()
            found = True
            break

    if not found:
        print(f"Error: Iteration '{iter_id}' not found")
        sys.exit(1)

    # Re-sort by timestamp
    data["iterations"].sort(key=lambda x: x["time"], reverse=True)

    save_iters(data)
    print(f"Updated {iter_id} stage to: {stage}")


def main():
    parser = argparse.ArgumentParser(description="Manage spec iterations")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # new command
    new_parser = subparsers.add_parser("new", help="Create a new iteration")
    new_parser.add_argument("name", help="Iteration name")

    # list command
    list_parser = subparsers.add_parser("list", help="List iterations")
    list_parser.add_argument("n", nargs="?", type=int, help="Limit to top N iterations")

    # spec command (iteration id + spec)
    spec_parser = subparsers.add_parser(
        "spec", help="Get SPEC.md path for an iteration"
    )
    spec_parser.add_argument("id", help="Iteration ID (name)")

    # plan command (iteration id + plan)
    plan_parser = subparsers.add_parser(
        "plan", help="Get PLAN.md path for an iteration"
    )
    plan_parser.add_argument("id", help="Iteration ID (name)")

    # update command (iteration id + update + stage)
    update_parser = subparsers.add_parser("update", help="Update iteration stage")
    update_parser.add_argument("id", help="Iteration ID (name)")
    update_parser.add_argument("stage", choices=VALID_STAGES, help="New stage")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args.name)
    elif args.command == "list":
        cmd_list(args.n)
    elif args.command == "spec":
        cmd_spec(args.id)
    elif args.command == "plan":
        cmd_plan(args.id)
    elif args.command == "update":
        cmd_update(args.id, args.stage)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
