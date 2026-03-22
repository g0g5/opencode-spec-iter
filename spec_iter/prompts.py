"""Prompt generators for Spec Iter commands."""

from __future__ import annotations

import subprocess
from pathlib import Path

from spec_iter.iterations import IterManager, to_kebab_case
from spec_iter.project import display_path


INTRO_WITH_AGENTS_MD = """You are now facing an established project with AGENTS.md. The AGENTS.md may need update. Create a TODO list and follow the workflow strictly:"""

INTRO_WITHOUT_AGENTS_MD = """You are now facing an project without AGENTS.md. You need to create AGENTS.md. Create a TODO list and follow the workflow strictly:"""

INSPECT_WORKSPACE_BLOCK = """- Inspect workspace to understand:
  - WHAT - Identify the tech stack and map the project as modules (folders or single-file modules) with one-line purpose per module. In monorepos, include every app and shared package as top-level modules.
  - WHY - State the project's purpose and the role of each major component.
  - HOW - Specify only the most universally-needed commands: how to build, run tests, run typechecks, and verify changes. Do not list every possible command-only the ones used in nearly every task."""

FOCUS_EXISTING_AGENTS_MD_LINE = "  - focusing on structure/tech stack/tooling changes which may conflict existing AGENTS.md"

WRITE_AGENTS_MD_BLOCK = """- Write concise AGENTS.md following this structure:

```markdown
## Project Overview
[One sentence: what this project does and its core stack.]

## Structure Map
[Generate a module-level tree view with one-line descriptions after `#`. Show only folders and single-file modules; do not list files inside folder modules. Exclude dot-prefixed internals. In monorepos, include each app/package as top-level modules.]

Example:

my-ts-service/
|- src/                    # Runtime application modules for the service
|  |- server.ts            # Boots HTTP server and initializes app startup flow
|  |- config.ts            # Loads and validates environment/app configuration
|  |- auth/                # Authentication and authorization module
|  |- users/               # User domain logic and related operations
|  \\- common/              # Shared utilities, types, and cross-cutting helpers
|- docs/                   # Project documentation for developers and maintainers
|  |- api/                 # API contracts, endpoint behavior, and examples
|  \\- architecture/        # System design, decisions, and module boundaries
\\- tests/                  # Automated test modules
   |- unit/                # Fast tests for isolated module behavior
   \\- integration/         # Tests for module interactions and external boundaries

## Development Guide
[Minimal workflow: how to build, test, and verify changes.]
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information"""


class PromptError(RuntimeError):
    """Raised when prompt generation cannot proceed."""


def _git_output(project_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or "No changes"
    except subprocess.CalledProcessError:
        if args[:2] == ("status", "--short"):
            return "Unable to get git status"
        return "Unable to get git diff"
    except FileNotFoundError:
        return "Git not found"


def generate_plan_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    spec_path = manager.get_spec_path(iter_id)
    iteration_path = manager.get_iteration_path(iter_id)

    if not spec_path.exists():
        raise PromptError(
            f"SPEC.md not found at {display_path(spec_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} spec`, then tell the user to run `/spec` to create SPEC.md first."
        )

    return f"""You need to create the implementation plan based on {display_path(spec_path)}

Follow this workflow strictly:

1. Create the implementation plan from the spec.
   - Produce a clear and concise implementation plan.
   - Structure the plan as phases with step-by-step actions under each phase.
   - Do not include time schedules, dates, deadlines, or milestones.

2. Save the plan document.
   - Save the plan as `{display_path(iteration_path / "PLAN.md")}`.
   - Run command `spec-iter update {iter_id} planned`"""


def generate_exec_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    plan_path = manager.get_plan_path(iter_id)
    spec_path = manager.get_spec_path(iter_id)

    if not plan_path.exists():
        raise PromptError(
            f"PLAN.md not found at {display_path(plan_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} plan`, then tell the user to run `/plan` to create PLAN.md first."
        )

    return f"""You orchestrate execution of `{display_path(plan_path)}`.
Your role is coordination and oversight only. Do not write or edit any files yourself.

Follow this workflow strictly:

1. Read `{display_path(plan_path)}` to understand the implementation plan. Create and maintain a todo list for all plan phases.

2. Delegate exactly one implementation phase at a time to one `@general` agent.
   - Never run multiple implementation agents in parallel; this avoids edit conflicts.

3. For each delegated phase, send this exact instruction to the `@general` agent:
   - `Read {display_path(spec_path)} and {display_path(plan_path)}, complete phase <phase number>.`

4. When a phase is finished, delegate the next phase to a new `@general` agent.

5. After all phases are complete, report what was done to the user.

6. Run command `spec-iter update {iter_id} executed`"""


def generate_post_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    iteration_path = manager.get_iteration_path(iter_id)
    git_status = _git_output(project_root, "status", "--short")
    git_diff = _git_output(project_root, "diff", "--stat")

    return f"""You execute post-implementation tasks for iteration `{iter_id}`.

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
   - `{display_path(iteration_path / "FINISHED.md")}`
   - Keep it concise and implementation-focused.

3. Commit all changes, regardless created by this iteration or not.

4. Run command `spec-iter update {iter_id} completed`"""


def _list_research_docs(project_root: Path) -> list[str]:
    docs_dir = project_root / ".speciter" / "docs"
    if not docs_dir.exists() or not docs_dir.is_dir():
        return []

    return sorted(
        display_path(path, project_root)
        for path in docs_dir.iterdir()
        if path.is_file()
    )


def generate_spec_prompt(project_root: Path, idea: str) -> str:
    cleaned_idea = idea.strip()
    if not cleaned_idea:
        raise PromptError("Idea is required: `spec-iter prompt spec <idea>`")

    default_iteration_name = to_kebab_case(cleaned_idea) or "new-iteration"
    docs_files = _list_research_docs(project_root)
    has_docs = bool(docs_files)
    identify_step_no = 5 if has_docs else 4
    create_step_no = 6 if has_docs else 5

    lines = [
        "In this iteration, the user wants to build:",
        "",
        cleaned_idea,
        "",
        "Follow this workflow strictly:",
        "",
        "1. If any web link or file exist in user ideas, read them for the context.",
        "",
        "2. Gather requirements with the `question` tool.",
        "   - The first question must be: `Iteration name`.",
        "   - Suggest a kebab-case default iteration name derived from the user idea: "
        f"`{default_iteration_name}`.",
        "   - Keep asking follow-up questions until you have enough information to write a complete SPEC.",
        "",
        "3. Run command `spec-iter new <iteration-name>`, where `<iteration-name>` is the confirmed iteration name from step 2.",
    ]

    if has_docs:
        docs_display = ", ".join(f"`{name}`" for name in docs_files)
        lines.extend(
            [
                "",
                f"4. Read the researched external library documents in `.speciter/docs/`: {docs_display}",
            ]
        )

    lines.extend(
        [
            "",
            f"{identify_step_no}. Identify external library dependencies needed for this iteration.",
            "   - List the key libraries that are likely required.",
            "   - Delegate research to `@explore` agents, one agent per library.",
            "   - Use this exact delegation prompt template:",
            "     - `Do web search to find out latest documentation of <library name>, about <related topics to iteration's goal>, return highly concise code examples of how to use the library with minimal prose.`",
            "",
            f"{create_step_no}. Create the SPEC document.",
            "   - Write a concise but actionable SPEC using the gathered answers and library research. Avoid long prose, use researched code examples.",
            "   - Save it to: `.speciter/iterations/<iteration-name>/SPEC.md`",
            "   - Run command `spec-iter update 1 specified`",
        ]
    )

    return "\n".join(lines)


def _missing_spec_error(
    spec_path: Path, project_root: Path, iter_id: str
) -> PromptError:
    return PromptError(
        f"SPEC.md not found at {display_path(spec_path, project_root)}. "
        f"Check path with `spec-iter path {iter_id} spec`, then tell the user to run `/spec` to create SPEC.md first."
    )


def _missing_plan_error(
    plan_path: Path, project_root: Path, iter_id: str
) -> PromptError:
    return PromptError(
        f"PLAN.md not found at {display_path(plan_path, project_root)}. "
        f"Check path with `spec-iter path {iter_id} plan`, then tell the user to run `/plan` to create PLAN.md first."
    )


def generate_run_search_prompt(project_root: Path, lib_name: str, topics: str) -> str:
    lib_goal = to_kebab_case(f"{lib_name} {topics}")
    if not lib_goal:
        raise PromptError("Unable to derive docs filename from library name and topics")

    docs_path = project_root / ".speciter" / "docs" / f"{lib_goal}.md"
    return (
        "Do web search to find out latest documentation of "
        f"{lib_name}, about {topics}, return highly concise code examples of how "
        "to use the library with minimal prose. "
        f"Save the findings as {display_path(docs_path, project_root)}"
    )


def generate_run_plan_prompt(
    project_root: Path, iter_id: str, parallel: bool = False
) -> str:
    base_prompt = generate_plan_prompt(project_root, iter_id)
    if not parallel:
        return base_prompt

    parallel_instruction = """

Additional parallel planning requirement:
- Identify phases that can run independently on different worktrees.
- Group independent phases by worktree assignment."""
    return f"{base_prompt}{parallel_instruction}"


def generate_run_dev_prompt(project_root: Path, iter_id: str, phase_id: int) -> str:
    manager = IterManager(project_root)
    spec_path = manager.get_spec_path(iter_id)
    plan_path = manager.get_plan_path(iter_id)

    if not spec_path.exists():
        raise _missing_spec_error(spec_path, project_root, iter_id)
    if not plan_path.exists():
        raise _missing_plan_error(plan_path, project_root, iter_id)

    return (
        f"Read {display_path(spec_path, project_root)} and "
        f"{display_path(plan_path, project_root)}, ONLY complete phase {phase_id}. "
        "After completion, take a note what you completed in PLAN.md "
        "after the phase you worked on."
    )


def generate_run_merge_prompt(project_root: Path, iter_id: str, worktree: str) -> str:
    manager = IterManager(project_root)
    spec_path = manager.get_spec_path(iter_id)
    plan_path = manager.get_plan_path(iter_id)
    branch_name = f"agent/{worktree}"
    worktree_path = project_root / ".speciter" / "worktrees" / worktree

    if not spec_path.exists():
        raise _missing_spec_error(spec_path, project_root, iter_id)
    if not plan_path.exists():
        raise _missing_plan_error(plan_path, project_root, iter_id)

    return (
        f"Read {display_path(spec_path, project_root)} and "
        f"{display_path(plan_path, project_root)}, make sure all phases of {worktree} "
        "are completed; if not, abort immediately. "
        f"merge {branch_name} branch back to main branch, resolve the conflicts "
        "respecting SPEC; after merge, remove the "
        f"{branch_name} branch and worktree {display_path(worktree_path, project_root)}."
    )


def _find_instruction_files(project_root: Path) -> list[str]:
    candidates = ["README.md", "CLAUDE.md", "AGENTS.md", ".cursorrules"]
    return [filename for filename in candidates if (project_root / filename).is_file()]


def _get_recent_commits(project_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def generate_agentsmd_prompt(project_root: Path) -> str:
    found_files = _find_instruction_files(project_root)
    has_agents_md = "AGENTS.md" in found_files
    commits = _get_recent_commits(project_root)

    prompt_parts = [
        INTRO_WITH_AGENTS_MD if has_agents_md else INTRO_WITHOUT_AGENTS_MD,
        "",
    ]

    if found_files:
        prompt_parts.append(
            f"- Read the found instruction files for context: {', '.join(found_files)}"
        )

    if commits:
        prompt_parts.append("- Read the following recent commit messages:")
        prompt_parts.append(commits)

    if found_files or commits:
        prompt_parts.append("")

    prompt_parts.append(INSPECT_WORKSPACE_BLOCK)

    if has_agents_md:
        prompt_parts.append(FOCUS_EXISTING_AGENTS_MD_LINE)

    prompt_parts.append("")
    prompt_parts.append(WRITE_AGENTS_MD_BLOCK)
    return "\n".join(prompt_parts)
