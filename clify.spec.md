# SPEC: Spec Iter Python CLI Companion

## Overview

Refactor Spec Iter from an installer-first package into a Python CLI companion that users install once with `uv tool install`, then run directly as `spec-iter ...` inside any initialized project.

The CLI becomes the single runtime surface for:

- project initialization,
- iteration lifecycle management,
- prompt generation for bundled OpenCode command templates.

This removes the current dependency on copied `.opencode/scripts/*.py` runtime helpers.

## Current State Findings

### Existing runtime split

- `spec_iter/cli.py` only implements installation behavior today.
- Real runtime behavior lives in copied project-local scripts under `spec_iter/bundled_src/scripts/`.
- Bundled markdown commands shell out to those copied scripts with commands like `python ./.opencode/scripts/prompt-plan.py $1`.

### Existing installer behavior

- Copies all bundled assets to `.opencode/`.
- Creates `.speciter/iterations/` and `.speciter/iters.json`.
- Appends `.speciter/`, `.opencode/commands/`, and `.opencode/scripts/` to `.gitignore`.
- Initializes git if missing.
- Uses interactive prompts for target path and overwrite decisions.

### Existing iteration behavior

- `iter_manager.py` owns iteration CRUD-like operations.
- Iteration ids are positional, 1-based, and sorted by most recent timestamp.
- Stored metadata shape is:

```json
{
  "iterations": [
    {
      "time": "2026-03-20T12:34:56.000000",
      "name": "my-iteration",
      "stage": "new"
    }
  ]
}
```

- Valid stages are `new`, `specified`, `planned`, `executed`, `completed`.

### Existing prompt generation behavior

- `prompt-plan.py` validates `SPEC.md` and emits the plan-writing prompt.
- `prompt-exec.py` validates `PLAN.md` and emits the execution-orchestration prompt.
- `prompt-post.py` collects `git status --short` and `git diff --stat`, then emits the post-work prompt.
- `prompt-agentsmd.py` inspects root instruction files and recent git commits, then emits the AGENTS.md prompt.

### Existing command template coupling

- `plan.md`, `exec.md`, `post.md`, `agentsmd.md`, and `list-iters.md` directly depend on local Python scripts.
- `spec.md` embeds instructions that tell the agent to run the old project-local script commands.

## Goals

- Make `spec-iter` the only public runtime entrypoint after installation.
- Support global installation via `uv tool install ...`, then direct invocation as `spec-iter ...`.
- Preserve the existing Spec Iter workflow and stored iteration data.
- Remove runtime dependence on copied `.opencode/scripts/` files.
- Update bundled command markdown files to call `spec-iter` directly.
- Keep project initialization simple and repeatable.

## Non-Goals

- Redesign the iteration data model.
- Change the meaning of iteration stages.
- Change the content strategy of the generated prompts beyond command-path replacements and minor wording cleanup.
- Introduce a background service, daemon, or per-project virtualenv.

## User Experience

### Installation model

Users install the tool once, for example:

```bash
uv tool install spec-iter --from git+https://github.com/g0g5/opencode-spec-iter
```

After that, usage is always direct:

```bash
spec-iter init
spec-iter new add-search
spec-iter list
spec-iter prompt 1 plan
```

`uvx` is not part of the target workflow.

### Project-local usage model

- `spec-iter init [<path>]` initializes a project for Spec Iter.
- All other commands run from inside the project and resolve project state from the current working directory.
- The CLI should search upward from the current directory to find the project root by locating `.speciter/iters.json` or `.speciter/`.
- If no initialized project is found, exit with a clear error telling the user to run `spec-iter init`.

## CLI Contract

### `spec-iter init [<path>]`

Initialize Spec Iter in the target project.

Behavior:

- Default path is the current directory.
- Create `.speciter/iterations/` if missing.
- Create `.speciter/iters.json` with an empty `iterations` array if missing.
- Install or update managed files under `.opencode/commands/`.
- Stop copying runtime helper Python scripts into `.opencode/scripts/`.
- Update `.gitignore` with `.speciter/` and `.opencode/commands/`.
- Do not add `.opencode/scripts/` to `.gitignore` anymore.
- Preserve existing project files outside the managed command set.
- Keep git initialization behavior: if `.git/` is missing, run `git init`; if unavailable, print a warning and continue.

Legacy cleanup:

- If `.opencode/scripts/` contains the old managed Spec Iter helper scripts, remove them.
- If `.opencode/scripts/` contains unknown files, leave them in place and print a warning instead of deleting them.

### `spec-iter new <iteration-name>`

Create a new iteration in the current project.

Behavior:

- Reuse existing kebab-case normalization.
- Create `.speciter/iterations/<iteration-name>/`.
- Append the new entry to `.speciter/iters.json` and keep the list sorted by descending timestamp.
- Print the created iteration name and directory.

### `spec-iter list`

List iterations for the current project.

Behavior:

- Reuse the current 1-based, most-recent-first display contract.
- Output one line per iteration in the current human-readable format: `<index>. <name> (<stage>)`.

### `spec-iter update <iter-id> <status>`

Update an iteration stage in the current project.

Behavior:

- Accept the current valid statuses only: `new`, `specified`, `planned`, `executed`, `completed`.
- Resolve ids using the existing 1-based, most-recent-first behavior.
- Update the iteration timestamp when status changes, preserving current ordering semantics.

### `spec-iter prompt <iter-id> <kind>`

Generate prompt text to stdout for iteration-scoped prompt kinds.

Supported kinds:

- `plan`
- `exec`
- `post`

Behavior:

- Emit exactly the generated prompt text to stdout on success.
- Emit errors to stderr and return exit code `1`.
- Preserve current validation behavior:
  - `plan` requires `SPEC.md`.
  - `exec` requires `PLAN.md`.
  - `post` requires a resolvable iteration id.
- Preserve current prompt semantics, but replace old runtime commands inside generated prompt text with `spec-iter ...` equivalents.

### `spec-iter prompt agentsmd`

Generate the AGENTS.md helper prompt to stdout.

Rationale:

- `agentsmd` is not iteration-scoped, so it should not require an iteration id.
- This is the one intentional shape difference from `prompt <iter-id> <kind>`.

Behavior:

- Preserve current instruction-file discovery and recent-commit discovery behavior.
- Emit prompt text to stdout.

## Internal Design

Refactor the package so runtime logic lives in importable modules instead of copied helper scripts.

Suggested module split:

- `spec_iter/cli.py` - argparse entrypoint and command dispatch.
- `spec_iter/project.py` - project-root discovery and path helpers.
- `spec_iter/init.py` - initialization and managed file installation.
- `spec_iter/iterations.py` - `IterManager` logic.
- `spec_iter/prompts.py` - prompt generators for `plan`, `exec`, `post`, `agentsmd`.

Notes:

- Reuse current business logic where possible instead of rewriting behavior.
- `iter_manager.py` and the prompt scripts should be absorbed into package modules, not copied into initialized projects.
- `install.py` should remain as a backward-compatible wrapper that maps to `spec-iter init` semantics.

## Bundled Command Template Changes

Update bundled markdown templates under `spec_iter/bundled_src/commands/` to call the global CLI.

Required changes:

- `plan.md`

```md
!`spec-iter prompt $1 plan`
```

- `exec.md`

```md
!`spec-iter prompt $1 exec`
```

- `post.md`

```md
!`spec-iter prompt $1 post`
```

- `agentsmd.md`

```md
!`spec-iter prompt agentsmd`
```

- `list-iters.md`

```md
!`spec-iter list`
```

- `spec.md`
  - replace `python ./.opencode/scripts/iter_manager.py new <iteration-name>` with `spec-iter new <iteration-name>`
  - replace `python ./.opencode/scripts/iter_manager.py update 1 specified` with `spec-iter update 1 specified`
  - remove any other references to `.opencode/scripts/` runtime helpers

## Migration Requirements

Existing initialized projects should remain usable after running `spec-iter init` again.

Migration expectations:

- Existing `.speciter/iters.json` and `.speciter/iterations/` must keep working unchanged.
- Existing iteration ids must keep resolving with current ordering rules.
- Existing projects upgraded with `init` should receive new command templates.
- Old project-local helper scripts should no longer be required for runtime behavior.

## Documentation Changes

Update project docs to match the new model.

Required documentation updates:

- `README.md`
  - replace `uvx`-based install instructions with `uv tool install`
  - describe `spec-iter init [path]`
  - document `new`, `list`, `update`, and `prompt`
  - remove explanations that describe `.opencode/scripts/*.py` as the runtime mechanism
- Any command walkthroughs should explain that bundled markdown commands now shell out to `spec-iter`, not project-local Python files.
- Project structure docs should reflect that `bundled_src/scripts/` is no longer installed as runtime payload.

## Acceptance Criteria

- After `uv tool install ...`, `spec-iter` is callable directly from the shell.
- `spec-iter init` initializes the current project without requiring interactive input.
- `spec-iter new`, `spec-iter list`, and `spec-iter update` work from any subdirectory inside an initialized project.
- `spec-iter prompt 1 plan`, `spec-iter prompt 1 exec`, and `spec-iter prompt 1 post` reproduce the current prompt-generation behavior from package code.
- `spec-iter prompt agentsmd` reproduces current AGENTS.md prompt generation behavior from package code.
- `.opencode/commands/*.md` no longer reference `python ./.opencode/scripts/...`.
- Re-running `spec-iter init` on an existing project updates managed command files without corrupting iteration data.

## Validation Plan

- Install locally with `uv tool install .` and verify the binary is on PATH.
- Run `spec-iter init` in a temp repo and verify created files and `.gitignore` entries.
- Run `spec-iter new test-iter`, `spec-iter list`, and `spec-iter update 1 specified`.
- Create sample `SPEC.md` and `PLAN.md`, then verify `spec-iter prompt 1 plan`, `spec-iter prompt 1 exec`, and `spec-iter prompt 1 post` outputs.
- Verify `spec-iter prompt agentsmd` output in repos with and without `AGENTS.md`.
- Re-run `spec-iter init` on a legacy project layout containing old `.opencode/scripts/` files and verify migration behavior.
