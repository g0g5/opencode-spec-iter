#!/usr/bin/env python3
"""Dynamically generate LLM agent prompt for creating/updating AGENTS.md."""

import os
import subprocess
import sys


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
    instruction_files = ["CLAUDE.md", "AGENTS.md", ".cursorrules"]

    # Scan for instruction files
    found_files = find_instruction_files(instruction_files)
    has_agents_md = "AGENTS.md" in found_files

    # Get git commits
    commits = get_recent_commits()

    # Build the prompt
    prompt_parts = []

    # Beginning of prompt
    if has_agents_md:
        prompt_parts.append(
            "You are now facing an established project with AGENTS.md. "
            "The AGENTS.md may need update. Create a TODO list and follow the workflow strictly:"
        )
    else:
        prompt_parts.append(
            "You are now facing an project without AGENTS.md. "
            "You need to create AGENTS.md. Create a TODO list and follow the workflow strictly:"
        )

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
    if has_agents_md:
        prompt_parts.append(
            "- Inspect workspace, focusing on project structure changes which may conflict existing AGENTS.md"
        )
    else:
        prompt_parts.append("- Inspect workspace to understand:")
        prompt_parts.append(
            "  - WHAT — Describe the tech stack, project structure, and purpose of each major directory/package. In monorepos, explicitly list every app and shared package with a one-line description of what it does."
        )
        prompt_parts.append(
            "  - WHY — State the project's purpose and the role of each major component."
        )
        prompt_parts.append(
            "  - HOW — Specify only the most universally-needed commands: how to build, run tests, run typechecks, and verify changes. Do not list every possible command—only the ones used in nearly every task."
        )

    prompt_parts.append("")  # Empty line

    # Final generation instruction
    prompt_parts.append("- Write concise AGENTS.md following this structure:")
    prompt_parts.append("")
    prompt_parts.append("```markdown")
    prompt_parts.append("## Project Overview")
    prompt_parts.append("[One sentence: what this project does and its core stack.]")
    prompt_parts.append("")
    prompt_parts.append("## Structure Map")
    prompt_parts.append(
        "[Bullet list of agent-facing directories/files (exclude dot-prefixed internals)."
    )
    prompt_parts.append(
        "In monorepos, list each app/package with one-line description.]"
    )
    prompt_parts.append("")
    prompt_parts.append("## Development Guide")
    prompt_parts.append("[Minimal workflow: how to build, test, and verify changes.]")
    prompt_parts.append("```")
    prompt_parts.append("")
    prompt_parts.append("**Rules:**")
    prompt_parts.append("- Be concise: no long prose, no unnecessary details")
    prompt_parts.append("- Focus on what agents need to know to be productive")
    prompt_parts.append("- Exclude obvious or rarely-used information")

    return "\n".join(prompt_parts)


def main():
    """Main entry point."""
    prompt = generate_prompt()
    print(prompt)


if __name__ == "__main__":
    main()
