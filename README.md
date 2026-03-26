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
- create `.speciter/iters.json` if missing
- install or update managed files in `.opencode/commands/`
- add `.speciter/` and `.opencode/commands/` to `.gitignore`
- run `git init` when the project is not already a git repo
- remove legacy managed helper scripts from `.opencode/scripts/` when safe

## CLI Commands

These commands work from the project root or any subdirectory inside an initialized project.

```bash
spec-iter new add-search
spec-iter list
spec-iter update 1 specified
spec-iter prompt 1 plan
spec-iter prompt 1 exec
spec-iter prompt 1 post
spec-iter prompt agentsmd
```

## OpenCode Commands

After `spec-iter init`, OpenCode can load these bundled templates from `.opencode/commands/`:

| Command | Description |
|---------|-------------|
| `/spec <feature-idea>` | Create a specification document for a new iteration |
| `/plan <iteration-id>` | Generate an implementation plan from `SPEC.md` |
| `/exec <iteration-id>` | Execute the implementation plan from `PLAN.md` |
| `/post <iteration-id>` | Run post-implementation tasks and completion flow |
| `/agentsmd` | Create or update `AGENTS.md` project context |
| `/list-iters` | Show iteration ids and stages |

The bundled markdown templates now shell out to `spec-iter`, not project-local Python helper scripts.

## Workflow

1. Run `/spec <idea>` and the agent creates an iteration with `spec-iter new <iteration-name>`.
2. The agent writes `.speciter/iterations/<iteration-name>/SPEC.md` and updates the stage with `spec-iter update 1 specified`.
3. Run `/plan 1` and the template inserts `spec-iter prompt 1 plan` output.
4. Run `/exec 1` and the template inserts `spec-iter prompt 1 exec` output.
5. Run `/post 1` and the template inserts `spec-iter prompt 1 post` output.
6. Run `/agentsmd` when you want the helper prompt for `AGENTS.md`.

Iteration ids are positional and 1-based. `1` always means the most recently updated iteration.

## Project Structure

```text
spec-iter/
|- spec_iter/
|  |- cli.py                  # argparse entrypoint and command dispatch
|  |- init.py                 # project initialization and managed file installation
|  |- iterations.py           # iteration CRUD-style logic and path helpers
|  |- project.py              # project-root discovery and path formatting
|  |- prompts.py              # prompt generation for plan/exec/post/agentsmd
|  \- commands/               # Markdown command templates copied to projects
|- pyproject.toml             # packaging and console script config
\- install.py                # backward-compatible wrapper for `spec-iter init`
```

## Requirements

- OpenCode CLI
- uv
- Python 3.9+
- Git

## License

[MIT License](LICENSE)
