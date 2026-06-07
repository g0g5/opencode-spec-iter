"""Prompt generators for Spec Iter commands."""

from __future__ import annotations

from importlib import resources
import subprocess
from pathlib import Path

from spec_iter.iterations import IterManager
from spec_iter.project import display_path


class PromptError(RuntimeError):
    """Raised when prompt generation cannot proceed."""


def _load_prompt(group_name: str, prompt_name: str) -> str:
    try:
        return (
            resources.files("spec_iter")
            .joinpath(group_name, prompt_name)
            .read_text(encoding="utf-8")
            .strip("\n")
        )
    except FileNotFoundError as exc:
        raise PromptError(f"Prompt not found: {group_name}/{prompt_name}") from exc


def _load_command_prompt(prompt_name: str) -> str:
    return _load_prompt("command_prompts", prompt_name)


def _load_subagent_prompt(prompt_name: str) -> str:
    return _load_prompt("subagent_prompts", prompt_name)


def _render_template(template: str, variables: dict[str, str]) -> str:
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


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
    resolved_id = manager.resolve_iteration_id(iter_id)
    iteration_path = manager.iterations_dir / resolved_id
    spec_path = iteration_path / "SPEC.md"

    if not spec_path.exists():
        raise PromptError(
            f"SPEC.md not found at {display_path(spec_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} spec`, then tell the user to run `/spec` to create SPEC.md first."
        )

    return _render_template(
        _load_command_prompt("plan.md"),
        {
            "spec_path": display_path(spec_path),
            "plan_path": display_path(iteration_path / "PLAN.md"),
            "iter_id": resolved_id,
        },
    )


def generate_exec_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    resolved_id = manager.resolve_iteration_id(iter_id)
    iteration_path = manager.iterations_dir / resolved_id
    plan_path = iteration_path / "PLAN.md"
    spec_path = iteration_path / "SPEC.md"

    if not plan_path.exists():
        raise PromptError(
            f"PLAN.md not found at {display_path(plan_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} plan`, then tell the user to run `/plan` to create PLAN.md first."
        )

    exec_phase_prompt = _render_template(
        _load_subagent_prompt("exec-phase.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
        },
    )

    return _render_template(
        _load_command_prompt("exec.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
            "iter_id": resolved_id,
            "exec_phase_prompt": exec_phase_prompt,
        },
    )


def generate_iter_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    resolved_id = manager.resolve_iteration_id(iter_id)
    iteration_path = manager.iterations_dir / resolved_id
    spec_path = iteration_path / "SPEC.md"
    plan_path = iteration_path / "PLAN.md"

    if not spec_path.exists():
        raise PromptError(
            f"SPEC.md not found at {display_path(spec_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} spec`, then tell the user to run `/spec` to create SPEC.md first."
        )

    create_plan_prompt = _render_template(
        _load_subagent_prompt("create-plan.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
            "iter_id": resolved_id,
        },
    )
    exec_phase_prompt = _render_template(
        _load_subagent_prompt("exec-phase.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
        },
    )

    return _render_template(
        _load_command_prompt("iter.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
            "iter_id": resolved_id,
            "create_plan_prompt": create_plan_prompt,
            "exec_phase_prompt": exec_phase_prompt,
        },
    )


def generate_post_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    resolved_id = manager.resolve_iteration_id(iter_id)
    iteration_path = manager.iterations_dir / resolved_id
    spec_path = iteration_path / "SPEC.md"
    git_status = _git_output(project_root, "status", "--short")
    git_diff = _git_output(project_root, "diff", "--stat")

    return _render_template(
        _load_command_prompt("post.md"),
        {
            "spec_path": display_path(spec_path),
            "git_status": git_status,
            "git_diff": git_diff,
            "finished_path": display_path(iteration_path / "FINISHED.md"),
            "iter_id": resolved_id,
        },
    )


def generate_spec_prompt(project_root: Path) -> str:
    agentsmd_step = ""
    if not (project_root / "AGENTS.md").is_file():
        agentsmd_step = """

6. Create a minimal AGENTS.md:
   - Do not use `agents-md` skill or other similar skills, create directly with only following two components:
   - Project overview (by iteration goal and current status)
   - Tech stack"""

    return _render_template(
        _load_command_prompt("spec.md"),
        {
            "agentsmd_step": agentsmd_step,
            "research_prompt": _load_subagent_prompt("research.md"),
        },
    )
