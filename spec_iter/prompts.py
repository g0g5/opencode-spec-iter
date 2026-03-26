"""Prompt generators for Spec Iter commands."""

from __future__ import annotations

from importlib import resources
import subprocess
from pathlib import Path

from spec_iter.iterations import IterManager
from spec_iter.project import display_path


class PromptError(RuntimeError):
    """Raised when prompt generation cannot proceed."""


def _load_template(template_name: str) -> str:
    try:
        return (
            resources.files("spec_iter")
            .joinpath("templates", template_name)
            .read_text(encoding="utf-8")
            .strip("\n")
        )
    except FileNotFoundError as exc:
        raise PromptError(f"Prompt template not found: {template_name}") from exc


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
    spec_path = manager.get_spec_path(iter_id)
    iteration_path = manager.get_iteration_path(iter_id)

    if not spec_path.exists():
        raise PromptError(
            f"SPEC.md not found at {display_path(spec_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} spec`, then tell the user to run `/spec` to create SPEC.md first."
        )

    return _render_template(
        _load_template("plan.md"),
        {
            "spec_path": display_path(spec_path),
            "plan_path": display_path(iteration_path / "PLAN.md"),
            "iter_id": iter_id,
        },
    )


def generate_exec_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    plan_path = manager.get_plan_path(iter_id)
    spec_path = manager.get_spec_path(iter_id)

    if not plan_path.exists():
        raise PromptError(
            f"PLAN.md not found at {display_path(plan_path, project_root)}. "
            f"Check path with `spec-iter path {iter_id} plan`, then tell the user to run `/plan` to create PLAN.md first."
        )

    return _render_template(
        _load_template("exec.md"),
        {
            "plan_path": display_path(plan_path),
            "spec_path": display_path(spec_path),
            "iter_id": iter_id,
        },
    )


def generate_post_prompt(project_root: Path, iter_id: str) -> str:
    manager = IterManager(project_root)
    iteration_path = manager.get_iteration_path(iter_id)
    git_status = _git_output(project_root, "status", "--short")
    git_diff = _git_output(project_root, "diff", "--stat")

    return _render_template(
        _load_template("post.md"),
        {
            "iter_id": iter_id,
            "git_status": git_status,
            "git_diff": git_diff,
            "finished_path": display_path(iteration_path / "FINISHED.md"),
        },
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
        _load_template("agentsmd_intro_with.md")
        if has_agents_md
        else _load_template("agentsmd_intro_without.md"),
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

    prompt_parts.append(_load_template("agentsmd_inspect_workspace.md"))

    if has_agents_md:
        prompt_parts.append(_load_template("agentsmd_focus_existing.md"))

    prompt_parts.append("")
    prompt_parts.append(_load_template("agentsmd_write_block.md"))
    return "\n".join(prompt_parts)
