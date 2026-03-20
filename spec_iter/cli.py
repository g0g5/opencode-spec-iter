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
    prompt_parser.add_argument("target", help="Iteration ID or 'agentsmd'")
    prompt_parser.add_argument(
        "kind", nargs="?", choices=["plan", "exec", "post"], help="Prompt kind"
    )
    prompt_parser.set_defaults(handler=_handle_prompt)

    path_parser = subparsers.add_parser("path", help=argparse.SUPPRESS)
    path_parser.add_argument("iter_id", help=argparse.SUPPRESS)
    path_parser.add_argument("kind", choices=["spec", "plan"], help=argparse.SUPPRESS)
    path_parser.set_defaults(handler=_handle_path)

    status_parser = subparsers.add_parser("status", help=argparse.SUPPRESS)
    status_parser.add_argument("iter_id", help=argparse.SUPPRESS)
    status_parser.set_defaults(handler=_handle_status)

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
        ValueError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
