#!/usr/bin/env python3
"""Dynamically generate LLM agent prompt for creating/updating AGENTS.md."""

import os
import subprocess
import sys


INTRO_WITH_AGENTS_MD = """You are now facing an established project with AGENTS.md. The AGENTS.md may need update. Create a TODO list and follow the workflow strictly:"""

INTRO_WITHOUT_AGENTS_MD = """You are now facing an project without AGENTS.md. You need to create AGENTS.md. Create a TODO list and follow the workflow strictly:"""

INSPECT_WORKSPACE_BLOCK = """- Inspect workspace to understand:
  - WHAT — Identify the tech stack and map the project as modules (folders or single-file modules) with one-line purpose per module. In monorepos, include every app and shared package as top-level modules.
  - WHY — State the project's purpose and the role of each major component.
  - HOW — Specify only the most universally-needed commands: how to build, run tests, run typechecks, and verify changes. Do not list every possible command—only the ones used in nearly every task."""

FOCUS_EXISTING_AGENTS_MD_LINE = "  - focusing on structure/tech stack/tooling changes which may conflict existing AGENTS.md"

WRITE_AGENTS_MD_BLOCK = """- Write concise AGENTS.md following this structure:

```markdown
## Project Overview
[One sentence: what this project does and its core stack.]

## Structure Map
[Generate a module-level tree view with one-line descriptions after `#`. Show only folders and single-file modules; do not list files inside folder modules. Exclude dot-prefixed internals. In monorepos, include each app/package as top-level modules.]

Example:

my-ts-service/
├─ src/                    # Runtime application modules for the service
│  ├─ server.ts            # Boots HTTP server and initializes app startup flow
│  ├─ config.ts            # Loads and validates environment/app configuration
│  ├─ auth/                # Authentication and authorization module
│  ├─ users/               # User domain logic and related operations
│  └─ common/              # Shared utilities, types, and cross-cutting helpers
├─ docs/                   # Project documentation for developers and maintainers
│  ├─ api/                 # API contracts, endpoint behavior, and examples
│  └─ architecture/        # System design, decisions, and module boundaries
└─ tests/                  # Automated test modules
   ├─ unit/                # Fast tests for isolated module behavior
   └─ integration/         # Tests for module interactions and external boundaries

## Development Guide
[Minimal workflow: how to build, test, and verify changes.]
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information"""


def find_instruction_files(configurable_files=None):
    """Find existing agent instruction files in the project."""
    if configurable_files is None:
        configurable_files = ["CLAUDE.md", "AGENTS.md"]

    found = []
    cwd = os.getcwd()

    for filename in configurable_files:
        filepath = os.path.join(cwd, filename)
        if os.path.isfile(filepath):
            found.append(filename)

    return found


def get_recent_commits():
    """Get recent git commits if git repo exists."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def generate_prompt():
    """Generate the complete prompt string."""
    # Configuration: extendable list of instruction files to look for
    instruction_files = ["README.md", "CLAUDE.md", "AGENTS.md", ".cursorrules"]

    # Scan for instruction files
    found_files = find_instruction_files(instruction_files)
    has_agents_md = "AGENTS.md" in found_files

    # Get git commits
    commits = get_recent_commits()

    # Build the prompt
    prompt_parts = []

    # Beginning of prompt
    if has_agents_md:
        prompt_parts.append(INTRO_WITH_AGENTS_MD)
    else:
        prompt_parts.append(INTRO_WITHOUT_AGENTS_MD)

    prompt_parts.append("")  # Empty line

    # First steps
    if found_files:
        file_list = ", ".join(found_files)
        prompt_parts.append(
            f"- Read the found instruction files for context: {file_list}"
        )

    if commits:
        prompt_parts.append("- Read the following recent commit messages:")
        prompt_parts.append(commits)

    if found_files or commits:
        prompt_parts.append("")  # Empty line

    # Main steps

    prompt_parts.append(INSPECT_WORKSPACE_BLOCK)

    if has_agents_md:
        prompt_parts.append(FOCUS_EXISTING_AGENTS_MD_LINE)
    prompt_parts.append("")  # Empty line

    # Final generation instruction
    prompt_parts.append(WRITE_AGENTS_MD_BLOCK)

    return "\n".join(prompt_parts)


def main():
    """Main entry point."""
    prompt = generate_prompt()
    print(prompt)


if __name__ == "__main__":
    main()
