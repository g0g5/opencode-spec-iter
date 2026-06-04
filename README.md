# Spec Iter

Spec-driven iterative development companion CLI for [OpenCode](https://opencode.ai).

## Overview

Spec Iter installs once as a Python CLI, then runs directly inside any initialized project. It manages iteration state under `.speciter/` and installs bundled OpenCode command templates under `.opencode/commands/`.

## Installation

```bash
uv tool install spec-iter --from git+https://github.com/g0g5/opencode-spec-iter
```

You can also install from a local checkout while developing:

```bash
git clone https://github.com/g0g5/opencode-spec-iter
cd opencode-spec-iter
uv tool install .
```

## Initialize A Project

Run this once per project:

```bash
spec-iter init
```

Or point it at another directory:

```bash
spec-iter init path/to/project
```

`init` will:
- create `.speciter/iterations/`
- create `.speciter/docs/`
- create or update `.speciter/templates/`
- create `.speciter/iters.json` if missing
- install or update managed files in `.opencode/commands/`
- add `.opencode/commands/` to `.gitignore`
- run `git init` when the project is not already a git repo
- remove legacy managed helper scripts from `.opencode/scripts/` when safe

## Workflow

After `spec-iter init`, use these commands inside OpenCode.

### 1. `/spec`

Usually the first step is to switch OpenCode to Plan mode by pressing `Tab`. Discuss what you want to build with the agent, do any needed research, and clarify the idea before creating files.

When you are confident enough, switch back to Build mode and run `/spec` with no parameters. The agent will start creating `SPEC.md`. You can also run `/spec <your idea>` to jump directly into the specification process.

You may be asked a few questions while the specification is being written. After `SPEC.md` is created, the iteration is at the `specified` stage. Review or edit `SPEC.md` however you like before moving on.

### 2. `/plan`

When `SPEC.md` is ready, run `/plan 1`. The agent will create `PLAN.md` from `SPEC.md`.

This step requires no human intervention. After `PLAN.md` is created, the iteration is at the `planned` stage.

The number `1` points to the most recently created or updated iteration. Run `spec-iter list` in your terminal to check iteration order.

### 3. `/exec`

When the first two steps are complete and you decide to implement, run `/exec 1`. The agent will execute the implementation plan.

This step also requires no human intervention and can be resumed after termination. After execution, the iteration is at the `executed` stage. Check what was implemented and whether it meets your goal.

### 4. `/post`

Run `/post 1` to complete the iteration. Today this mainly performs a document review and creates a git commit. Verification features are planned.

After this step, the iteration stage changes to `completed`.

## Requirements

- OpenCode CLI
- uv
- Python 3.9+
- Git

## License

[MIT License](LICENSE)
