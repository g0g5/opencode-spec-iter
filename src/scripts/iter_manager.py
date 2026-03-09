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


def to_kebab_case(name: str) -> str:
    """Convert string to lowercase kebab-case."""
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    name = name.strip("-")
    return name.lower()


class IterManager:
    """Core iteration management class for spec-driven development."""

    VALID_STAGES = ["new", "spec", "plan", "execute", "post", "completed"]

    def __init__(self, speciter_dir: Path = Path(".speciter")):
        self.speciter_dir = speciter_dir
        self.iters_file = speciter_dir / "iters.json"
        self.iterations_dir = speciter_dir / "iterations"

    def load_iters(self) -> dict:
        """Load iters.json or return empty structure."""
        if self.iters_file.exists():
            with open(self.iters_file, "r") as f:
                return json.load(f)
        return {"iterations": []}

    def save_iters(self, data: dict):
        """Save iters.json."""
        self.speciter_dir.mkdir(parents=True, exist_ok=True)
        with open(self.iters_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_iteration_path(self, iter_id: str) -> str:
        """Get iteration directory path by ID (numeric)."""
        resolved_id = self.resolve_iteration_id(iter_id)
        return (self.iterations_dir / resolved_id).as_posix()

    def verify_iters_file_exists(self):
        """Check if iters.json exists, raise FileNotFoundError if not."""
        if not self.iters_file.exists():
            raise FileNotFoundError(
                "iters.json not found. Run 'iter_manager new <name>' to create the first iteration."
            )

    def resolve_iteration_id(self, iter_id: str) -> str:
        """Resolve numeric iteration ID to iteration name.

        Numeric IDs start from 1 (1 = most recent iteration).
        """
        self.verify_iters_file_exists()
        data = self.load_iters()
        iterations = data.get("iterations", [])

        # Parse as numeric ID
        try:
            num_id = int(iter_id)
            if num_id < 1:
                raise ValueError(f"Iteration ID must be >= 1, got {num_id}")
            if num_id > len(iterations):
                raise ValueError(
                    f"Iteration #{num_id} not found (only {len(iterations)} iterations)"
                )
            # Return the name of the iteration at position num_id-1 (0-indexed)
            return iterations[num_id - 1]["name"]
        except ValueError as e:
            if "Iteration" in str(e):
                raise
            raise ValueError(f"Invalid iteration ID '{iter_id}': must be a number >= 1")

    def verify_iteration_exists(self, iter_id: str) -> bool:
        """Check if iteration exists in iters.json."""
        try:
            self.resolve_iteration_id(iter_id)
            return True
        except ValueError:
            return False

    def create_iteration(self, name: str) -> tuple[str, str]:
        """Create a new iteration. Returns (kebab_name, iteration_dir)."""
        kebab_name = to_kebab_case(name)
        if not kebab_name:
            raise ValueError(f"Invalid iteration name '{name}'")

        iteration_dir = self.iterations_dir / kebab_name
        iteration_dir.mkdir(parents=True, exist_ok=True)

        data = self.load_iters()

        for it in data.get("iterations", []):
            if it["name"] == kebab_name:
                raise ValueError(f"Iteration '{kebab_name}' already exists")

        timestamp = datetime.now().isoformat()
        new_iter = {"time": timestamp, "name": kebab_name, "stage": "new"}
        data["iterations"].append(new_iter)
        data["iterations"].sort(key=lambda x: x["time"], reverse=True)

        self.save_iters(data)
        return kebab_name, iteration_dir.as_posix()

    def list_iterations(self, n: Optional[int] = None) -> list[dict]:
        """Return list of iterations sorted by timestamp (most recent first)."""
        self.verify_iters_file_exists()
        data = self.load_iters()
        iterations = data.get("iterations", [])
        if n is not None:
            iterations = iterations[:n]
        return iterations

    def get_spec_path(self, iter_id: str) -> str:
        """Get SPEC.md path for an iteration."""
        resolved_id = self.resolve_iteration_id(iter_id)
        return (self.iterations_dir / resolved_id / "SPEC.md").as_posix()

    def get_plan_path(self, iter_id: str) -> str:
        """Get PLAN.md path for an iteration."""
        resolved_id = self.resolve_iteration_id(iter_id)
        return (self.iterations_dir / resolved_id / "PLAN.md").as_posix()

    def update_iteration_stage(self, iter_id: str, stage: str):
        """Update iteration stage."""
        self.verify_iters_file_exists()
        if stage not in self.VALID_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Valid stages: {', '.join(self.VALID_STAGES)}"
            )

        resolved_id = self.resolve_iteration_id(iter_id)
        data = self.load_iters()
        found = False

        for it in data.get("iterations", []):
            if it["name"] == resolved_id:
                it["stage"] = stage
                it["time"] = datetime.now().isoformat()
                found = True
                break

        if not found:
            raise ValueError(f"Iteration '{iter_id}' not found")

        data["iterations"].sort(key=lambda x: x["time"], reverse=True)
        self.save_iters(data)


# Global instance for cmd_* functions
_manager = IterManager()


def cmd_new(name: str):
    """Create a new iteration."""
    try:
        kebab_name, iteration_dir = _manager.create_iteration(name)
        print(f"Created iteration: {kebab_name}")
        print(f"Directory: {iteration_dir}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_list(n: Optional[int] = None):
    """List iterations sorted by timestamp."""
    try:
        iterations = _manager.list_iterations(n)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not iterations:
        print("No iterations found")
        return

    for idx, it in enumerate(iterations, 1):
        print(f"{idx}. {it['name']} ({it['stage']})")


def cmd_spec(iter_id: str):
    """Print SPEC.md path or error."""
    try:
        spec_path = _manager.get_spec_path(iter_id)
        if Path(spec_path).exists():
            print(spec_path)
        else:
            print(f"Error: SPEC.md not found for iteration {iter_id}")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_plan(iter_id: str):
    """Print PLAN.md path or error."""
    try:
        plan_path = _manager.get_plan_path(iter_id)
        if Path(plan_path).exists():
            print(plan_path)
        else:
            print(f"Error: PLAN.md not found for iteration {iter_id}")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_update(iter_id: str, stage: str):
    """Update iteration stage."""
    try:
        _manager.update_iteration_stage(iter_id, stage)
        print(f"Updated iteration {iter_id} stage to: {stage}")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


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
    spec_parser.add_argument("id", help="Iteration ID (number, 1-based)")

    # plan command (iteration id + plan)
    plan_parser = subparsers.add_parser(
        "plan", help="Get PLAN.md path for an iteration"
    )
    plan_parser.add_argument("id", help="Iteration ID (number, 1-based)")

    # update command (iteration id + update + stage)
    update_parser = subparsers.add_parser("update", help="Update iteration stage")
    update_parser.add_argument("id", help="Iteration ID (number, 1-based)")
    update_parser.add_argument(
        "stage", choices=IterManager.VALID_STAGES, help="New stage"
    )

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
