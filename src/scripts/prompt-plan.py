#!/usr/bin/env python3
"""Dynamically generate LLM agent prompt for creating plan."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from iter_manager import IterManager


def generate_prompt(iter_id: str) -> str:
    """Generate prompt based on iteration spec existence."""
    manager = IterManager()

    try:
        spec_path = manager.get_spec_path(iter_id)
        iteration_path = manager.get_iteration_path(iter_id)
    except (ValueError, FileNotFoundError) as e:
        return f"Error: {e}"

    if not Path(spec_path).exists():
        return (
            f"SPEC.md not found at {spec_path}. "
            f"Check path with `python ./.opencode/scripts/iter_manager.py path {iter_id} spec`, "
            "then tell the user to run `/spec` to create SPEC.md first."
        )

    return f"""You need to create the implementation plan based on {spec_path}

Follow this workflow strictly:

1. Create the implementation plan from the spec.
   - Produce a clear and concise implementation plan.
   - Structure the plan as phases with step-by-step actions under each phase.
   - Do not include time schedules, dates, deadlines, or milestones.

2. Save the plan document.
   - Save the plan as `{iteration_path}/PLAN.md`.
   - Run command `python ./.opencode/scripts/iter_manager.py update {iter_id} planned`"""


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Error: Iteration ID required", file=sys.stderr)
        sys.exit(1)

    iter_id = sys.argv[1]
    prompt = generate_prompt(iter_id)
    print(prompt)


if __name__ == "__main__":
    main()
