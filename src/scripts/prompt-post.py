#!/usr/bin/env python3
"""Dynamically generate LLM agent prompt for post-implementation tasks."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from iter_manager import IterManager


def get_git_status() -> str:
    """Get concise git status output."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip() or "No changes"
    except subprocess.CalledProcessError:
        return "Unable to get git status"
    except FileNotFoundError:
        return "Git not found"


def get_git_diff() -> str:
    """Get concise git diff output (short stat)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip() or "No changes"
    except subprocess.CalledProcessError:
        return "Unable to get git diff"
    except FileNotFoundError:
        return "Git not found"


def generate_prompt(iter_id: str) -> str:
    """Generate prompt for post-implementation tasks."""
    manager = IterManager()

    try:
        iteration_path = manager.get_iteration_path(iter_id)
        resolved_id = manager.resolve_iteration_id(iter_id)
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

    git_status = get_git_status()
    git_diff = get_git_diff()

    return f"""You execute post-implementation tasks for iteration `{iter_id}`.
Current iteration stage: `{current_stage}` (check with `python ./.opencode/scripts/iter_manager.py status {iter_id}`).

Follow this workflow strictly:

1. Review local changes (already provided below):

Git Status:
```
{git_status}
```

Git Diff (stats):
```
{git_diff}
```

2. Create the iteration completion report at:
   - `{iteration_path}/FINISHED.md`
   - Keep it concise and implementation-focused.

3. Commit all changes, regardless created by this iteration or not.

4. Run command `python ./.opencode/scripts/iter_manager.py update {iter_id} post`"""


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
