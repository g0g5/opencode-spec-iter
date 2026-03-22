# SPEC: `spec-iter run <operation>`

## Overview

Add a new `spec-iter run <operation>` command family that invokes OpenCode CLI operations through Python `subprocess`, using:

```bash
opencode run "<operation prompt>"
```

Supported operations:

- `search`
- `plan`
- `dev`
- `merge`
- `post`

This command complements existing `spec-iter prompt ...` behavior by adding direct operation execution.

## Goals

- Provide one entrypoint for operation execution: `spec-iter run <operation> ...`.
- Centralize operation prompt templates in package code.
- Support both single-workspace and multi-worktree execution for parallel development.
- Keep iteration-aware behavior consistent with current id resolution and path helpers.

## Non-Goals

- Replacing existing `spec-iter prompt` commands.
- Changing iteration metadata model (`iters.json` schema, stage values, id ordering).
- Auto-pushing branches or opening PRs.

## CLI Contract

Primary shape:

```bash
spec-iter run <operation> [...args]
```

### Operation: `search`

Usage:

```bash
spec-iter run search <lib-name> <topics>
```

Prompt template:

```text
Do web search to find out latest documentation of <library name>, about <related topics to iteration's goal>, return highly concise code examples of how to use the library with minimal prose. Save the findings as .speciter/docs/<lib-goal>.md
```

Behavior:

- Build and run one `opencode run "..."` prompt using the provided `lib-name` and `topics`.
- Ensure `.speciter/docs/` exists before invocation.
- `<lib-goal>` is derived from `lib-name` + `topics` in kebab-case.
- Run from project root so the relative output path resolves correctly.

### Operation: `plan`

Usage:

```bash
spec-iter run plan <iter-id> [parallel]
```

Prompt template:

- Default mode: reuse `prompts.py` `generate_plan_prompt` content.
- Parallel mode: same base prompt plus an additional instruction:
  - identify phases that can run independently on different worktrees,
  - group independent phases by worktree assignment.

Behavior:

- Resolve `<iter-id>` with existing 1-based id logic.
- Invoke `opencode run "..."` with the generated prompt.
- If `SPEC.md` is missing, fail with the same validation behavior as plan prompt generation.

### Operation: `dev`

Usage:

```bash
spec-iter run dev <iter-id> <phase-id> [<worktree>]
```

Prompt template:

```text
Read {display_path(spec_path)} and {display_path(plan_path)}, ONLY complete phase <phase number>. After completion, take a note what you completed in PLAN.md after the phase you worked on.
```

Behavior:

- Resolve `<iter-id>` and required paths (`SPEC.md`, `PLAN.md`) using current helpers.
- Without `<worktree>`:
  - run in current project workspace,
  - execute `opencode run "..."`.
- With `<worktree>`:
  - create worktree and branch from main:

```bash
git worktree add .speciter/worktrees/<worktree> -b agent/<worktree> main
```

  - run `opencode run "..."` with CWD set to:

```bash
.speciter/worktrees/<worktree>/
```

- If worktree already exists, reuse it if clean and on `agent/<worktree>` branch; otherwise fail with a clear error.

### Operation: `merge`

Usage:

```bash
spec-iter run merge <worktree>
```

Prompt template:

```text
Read {display_path(spec_path)} and {display_path(plan_path)}, make sure all phases of <worktree> are completed; if not, abort immediately. merge <worktree> branch back to main branch, resolve the conflicts respecting SPEC; after merge, remove the <worktree> branch and worktree .speciter/worktrees/<worktree>/.
```

Behavior:

- Require `<worktree>` argument (no implicit merge target).
- Invoke via `opencode run "..."` from project root.
- Prompt must instruct agent to:
  - verify mapped phases for the worktree are complete,
  - merge `agent/<worktree>` into `main`,
  - resolve conflicts according to `SPEC.md`,
  - remove branch and worktree after successful merge.

### Operation: `post`

Usage:

```bash
spec-iter run post <iter-id>
```

Prompt template:

- Reuse `prompts.py` `generate_post_prompt`.

Behavior:

- Resolve `<iter-id>` with existing id semantics.
- Invoke `opencode run "..."` with generated post prompt.

## Internal Design

### CLI wiring

- Add `run` subcommand in `spec_iter/cli.py`.
- Add operation-specific argument parsers under `run`.
- Dispatch to operation handlers that:
  - build prompt text,
  - run `subprocess.run(["opencode", "run", prompt], ...)`.

### Prompt generation

- Extend `spec_iter/prompts.py` with run-operation helpers:
  - `generate_run_search_prompt(...)`
  - `generate_run_plan_prompt(iter_id, parallel=False)`
  - `generate_run_dev_prompt(iter_id, phase_id)`
  - `generate_run_merge_prompt(iter_id, worktree)` (or equivalent merge helper)
  - post uses `generate_post_prompt(...)` directly.
- Reuse `display_path(...)` for human-readable path embedding.

### Execution helper

- Add a shared helper to execute OpenCode:

```python
subprocess.run(["opencode", "run", prompt], cwd=target_cwd, check=True)
```

- Error handling:
  - `FileNotFoundError` for missing `opencode` -> clear message.
  - non-zero exit -> bubble stderr summary and return exit code `1`.

### Worktree management

- Add utility helpers for:
  - `.speciter/worktrees/<name>` path resolution,
  - worktree creation,
  - validation of existing worktree state.
- Branch naming convention: `agent/<worktree>`.

## Init Changes

Update `spec-iter init` behavior:

- Ensure these directories always exist:
  - `.speciter/iterations/`
  - `.speciter/docs/`
  - `.speciter/worktrees/`
- Keep existing `.speciter/iters.json` creation behavior.
- After git initialization checks, run `git branch -m main` to normalize default branch name.
  - If rename fails, print warning and continue.

## UX and Error Messages

- Clear errors for invalid operation args and missing required files.
- For iteration-scoped operations, preserve current id resolution messages.
- For worktree operations, include the exact problematic path/branch in errors.

## Acceptance Criteria

- `spec-iter run search <lib-name> <topics>` invokes `opencode run` with the search template and `.speciter/docs/` target.
- `spec-iter run plan <iter-id>` invokes default plan-generation-derived prompt.
- `spec-iter run plan <iter-id> parallel` includes independent-phase worktree grouping instruction.
- `spec-iter run dev <iter-id> <phase-id>` runs in current workspace.
- `spec-iter run dev <iter-id> <phase-id> <worktree>` creates/uses `.speciter/worktrees/<worktree>` and runs there.
- `spec-iter run merge <worktree>` invokes merge workflow prompt for `agent/<worktree>` -> `main` and cleanup.
- `spec-iter run post <iter-id>` reuses post prompt behavior and invokes `opencode run`.
- `spec-iter init` creates `.speciter/docs/` and `.speciter/worktrees/` and attempts `git branch -m main`.

## Validation Plan

- `python -m compileall spec_iter`
- In a temp initialized repo:
  - run `spec-iter init`
  - verify `.speciter/docs/` and `.speciter/worktrees/` exist
  - run each operation with representative inputs:
    - `spec-iter run search react hooks`
    - `spec-iter run plan 1`
    - `spec-iter run plan 1 parallel`
    - `spec-iter run dev 1 1`
    - `spec-iter run dev 1 2 ui-phase`
    - `spec-iter run merge ui-phase`
    - `spec-iter run post 1`
- Verify failures are clear when:
  - `opencode` is unavailable,
  - iteration id is invalid,
  - required `SPEC.md`/`PLAN.md` is missing,
  - worktree state is inconsistent.
