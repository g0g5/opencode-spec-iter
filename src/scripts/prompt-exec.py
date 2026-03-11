#!/usr/bin/env python3
"""Dynamically generate LLM agent prompt for executing plan."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from iter_manager import IterManager


def generate_prompt(iter_id: str) -> str:
    """Generate prompt based on iteration plan existence."""
    manager = IterManager()

    try:
        resolved_id = manager.resolve_iteration_id(iter_id)
        plan_path = manager.get_plan_path(iter_id)
        spec_path = manager.get_spec_path(iter_id)
        current_stage = next(
            (
                it["stage"]
                for it in manager.list_iterations()
                if it["name"] == resolved_id
            ),
            "unknown",
        )
    except (ValueError, FileNotFoundError) as e:
        return f"Error: {e}"

    if not Path(plan_path).exists():
        return (
            f"PLAN.md not found at {plan_path}. "
            f"Check path with `python ./.opencode/scripts/iter_manager.py path {iter_id} plan`, "
            "then tell the user to run `/plan` to create PLAN.md first."
        )

    return f"""You orchestrate execution of `{plan_path}`.
Your role is coordination and oversight only. Do not write or edit any files yourself.
Current iteration stage: `{current_stage}` (check with `python ./.opencode/scripts/iter_manager.py status {iter_id}`).

Follow this workflow strictly:

1. Read `{plan_path}` to understand the implementation plan. Use `todowrite` to create and maintain a todo list for all plan phases.

2. Delegate exactly one implementation phase at a time to one `@general` agent.
   - Never run multiple implementation agents in parallel; this avoids edit conflicts.

3. For each delegated phase, send this exact instruction to the `@general` agent:
   - `Read {spec_path} and {plan_path}, complete phase <phase number>.`

4. When a phase is finished, delegate the next phase to a new `@general` agent.

5. After all phases are complete, report what was done to the user.

6. Run command `python ./.opencode/scripts/iter_manager.py update {iter_id} execute`"""


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
