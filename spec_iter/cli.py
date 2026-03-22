#!/usr/bin/env python3
"""Console entrypoint for the Spec Iter CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from spec_iter.init import initialize_project
from spec_iter.iterations import IterManager
from spec_iter.project import (
    ProjectNotInitializedError,
    display_path,
    find_project_root,
)
from spec_iter.prompts import (
    PromptError,
    generate_agentsmd_prompt,
    generate_exec_prompt,
    generate_plan_prompt,
    generate_post_prompt,
    generate_spec_prompt,
    generate_run_dev_prompt,
    generate_run_merge_prompt,
    generate_run_plan_prompt,
    generate_run_search_prompt,
)
from spec_iter.run_ops import (
    RunOperationError,
    ensure_worktree_ready,
    run_opencode,
    validate_worktree_name,
)


def _get_manager() -> IterManager:
    project_root = find_project_root()
    return IterManager(project_root)


def _handle_init(args: argparse.Namespace) -> int:
    result = initialize_project(Path(args.path))
    print(f"Initialized Spec Iter in {display_path(result.project_root)}")
    print(f"Managed commands: {display_path(result.commands_dir)}")

    if result.removed_legacy_scripts:
        legacy_scripts_dir = (
            result.legacy_scripts_dir or result.project_root / ".opencode" / "scripts"
        )
        print(f"Removed legacy helper scripts from {display_path(legacy_scripts_dir)}")

    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)

    return 0


def _handle_new(args: argparse.Namespace) -> int:
    manager = _get_manager()
    name, iteration_dir = manager.create_iteration(args.name)
    print(f"Created iteration: {name}")
    print(f"Directory: {display_path(iteration_dir)}")
    return 0


def _handle_list(args: argparse.Namespace) -> int:
    manager = _get_manager()
    iterations = manager.list_iterations(args.limit)

    if not iterations:
        print("No iterations found")
        return 0

    for index, iteration in enumerate(iterations, start=1):
        print(f"{index}. {iteration['name']} ({iteration['stage']})")

    return 0


def _handle_update(args: argparse.Namespace) -> int:
    manager = _get_manager()
    manager.update_iteration_stage(args.iter_id, args.stage)
    print(f"Updated iteration {args.iter_id} stage to: {args.stage}")
    return 0


def _handle_prompt(args: argparse.Namespace) -> int:
    project_root = find_project_root()

    if args.target == "agentsmd":
        if args.kind is not None:
            raise PromptError("`spec-iter prompt agentsmd` does not take a prompt kind")
        sys.stdout.write(generate_agentsmd_prompt(project_root))
        return 0

    if args.target == "spec":
        if args.kind is None:
            raise PromptError("`spec-iter prompt spec <idea>` requires an idea")
        sys.stdout.write(generate_spec_prompt(project_root, args.kind))
        return 0

    if args.kind is None:
        raise PromptError("Prompt kind is required: plan, exec, or post")

    if args.kind == "plan":
        prompt = generate_plan_prompt(project_root, args.target)
    elif args.kind == "exec":
        prompt = generate_exec_prompt(project_root, args.target)
    elif args.kind == "post":
        prompt = generate_post_prompt(project_root, args.target)
    else:
        raise PromptError(f"Unsupported prompt kind '{args.kind}'")

    sys.stdout.write(prompt)
    return 0


def _handle_path(args: argparse.Namespace) -> int:
    manager = _get_manager()
    target_path = (
        manager.get_spec_path(args.iter_id)
        if args.kind == "spec"
        else manager.get_plan_path(args.iter_id)
    )
    print(display_path(target_path))
    return 0


def _handle_run_search(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    docs_dir = project_root / ".speciter" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    topics = " ".join(args.topics)
    prompt = generate_run_search_prompt(project_root, args.lib_name, topics)
    run_opencode(prompt, project_root)
    return 0


def _handle_run_plan(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    prompt = generate_run_plan_prompt(
        project_root,
        args.iter_id,
        parallel=args.mode == "parallel",
    )
    run_opencode(prompt, project_root)
    return 0


def _handle_run_dev(args: argparse.Namespace) -> int:
    if args.phase_id < 1:
        raise ValueError(f"Phase ID must be >= 1, got {args.phase_id}")

    project_root = find_project_root()
    prompt = generate_run_dev_prompt(project_root, args.iter_id, args.phase_id)

    target_cwd = project_root
    if args.worktree is not None:
        target_cwd = ensure_worktree_ready(project_root, args.worktree)

    run_opencode(prompt, target_cwd)
    return 0


def _handle_run_merge(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    validate_worktree_name(args.worktree)

    # Merge workflow targets the most recently updated iteration by default.
    prompt = generate_run_merge_prompt(project_root, "1", args.worktree)
    run_opencode(prompt, project_root)
    return 0


def _handle_run_post(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    prompt = generate_post_prompt(project_root, args.iter_id)
    run_opencode(prompt, project_root)
    return 0


def _handle_status(args: argparse.Namespace) -> int:
    manager = _get_manager()
    print(manager.get_iteration_stage(args.iter_id))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec-iter", description="Spec-driven iterative development companion CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Initialize Spec Iter in a project"
    )
    init_parser.add_argument("path", nargs="?", default=".", help="Project path")
    init_parser.set_defaults(handler=_handle_init)

    new_parser = subparsers.add_parser("new", help="Create a new iteration")
    new_parser.add_argument("name", help="Iteration name")
    new_parser.set_defaults(handler=_handle_new)

    list_parser = subparsers.add_parser("list", help="List iterations")
    list_parser.add_argument(
        "limit", nargs="?", type=int, help="Limit to the top N iterations"
    )
    list_parser.set_defaults(handler=_handle_list)

    update_parser = subparsers.add_parser("update", help="Update an iteration stage")
    update_parser.add_argument("iter_id", help="Iteration ID (1 = most recent)")
    update_parser.add_argument(
        "stage", choices=IterManager.VALID_STAGES, help="New stage"
    )
    update_parser.set_defaults(handler=_handle_update)

    prompt_parser = subparsers.add_parser("prompt", help="Generate a prompt")
    prompt_parser.add_argument("target", help="Iteration ID, 'spec', or 'agentsmd'")
    prompt_parser.add_argument(
        "kind",
        nargs="?",
        help="Prompt kind (plan/exec/post) or spec idea",
    )
    prompt_parser.set_defaults(handler=_handle_prompt)

    path_parser = subparsers.add_parser("path", help=argparse.SUPPRESS)
    path_parser.add_argument("iter_id", help=argparse.SUPPRESS)
    path_parser.add_argument("kind", choices=["spec", "plan"], help=argparse.SUPPRESS)
    path_parser.set_defaults(handler=_handle_path)

    status_parser = subparsers.add_parser("status", help=argparse.SUPPRESS)
    status_parser.add_argument("iter_id", help=argparse.SUPPRESS)
    status_parser.set_defaults(handler=_handle_status)

    run_parser = subparsers.add_parser(
        "run",
        help="Run an OpenCode operation prompt",
    )
    run_subparsers = run_parser.add_subparsers(dest="operation", required=True)

    run_search_parser = run_subparsers.add_parser(
        "search",
        help="Run library research and save docs under .speciter/docs",
    )
    run_search_parser.add_argument("lib_name", help="Library name")
    run_search_parser.add_argument("topics", nargs="+", help="Related topics")
    run_search_parser.set_defaults(handler=_handle_run_search)

    run_plan_parser = run_subparsers.add_parser(
        "plan",
        help="Run plan generation",
    )
    run_plan_parser.add_argument("iter_id", help="Iteration ID (1 = most recent)")
    run_plan_parser.add_argument(
        "mode",
        nargs="?",
        choices=["parallel"],
        help="Optional parallel planning mode",
    )
    run_plan_parser.set_defaults(handler=_handle_run_plan)

    run_dev_parser = run_subparsers.add_parser(
        "dev",
        help="Run single-phase development in workspace or worktree",
    )
    run_dev_parser.add_argument("iter_id", help="Iteration ID (1 = most recent)")
    run_dev_parser.add_argument("phase_id", type=int, help="Phase ID (>= 1)")
    run_dev_parser.add_argument("worktree", nargs="?", help="Optional worktree name")
    run_dev_parser.set_defaults(handler=_handle_run_dev)

    run_merge_parser = run_subparsers.add_parser(
        "merge",
        help="Run merge workflow for an agent worktree",
    )
    run_merge_parser.add_argument("worktree", help="Worktree name")
    run_merge_parser.set_defaults(handler=_handle_run_merge)

    run_post_parser = run_subparsers.add_parser(
        "post",
        help="Run post-implementation workflow",
    )
    run_post_parser.add_argument("iter_id", help="Iteration ID (1 = most recent)")
    run_post_parser.set_defaults(handler=_handle_run_post)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        return args.handler(args)
    except (
        FileNotFoundError,
        ProjectNotInitializedError,
        PromptError,
        RunOperationError,
        ValueError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
