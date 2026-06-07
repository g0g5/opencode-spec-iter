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

In this process the agent would:
    - Starting with ask you questions for clarifying specification details
    - Run command `spec-iter new <iteration-name>`, which creates a new iteration
    - Inspect and understand the current workspace situation using an `@explore` subagent
    - Identify external library dependencies, do parallel web research with subagents
    - Create the `SPEC.md` document.

After `SPEC.md` is created, the iteration is at the `specified` stage. Review or edit `SPEC.md` however you like before moving on.

### 2. `/plan`

When `SPEC.md` is ready, run `/plan 1`. The agent will create `PLAN.md` from `SPEC.md`.

In this process the agent would:
    - Read `SPEC.md` and create a phased implementation plan
    - Save the plan as `PLAN.md`
    - Run command `spec-iter update {{iter_id}} planned`

This step requires no human intervention. After `PLAN.md` is created, the iteration is at the `planned` stage.

The number `1` points to the most recently created or updated iteration. Run `spec-iter list` in your terminal to check iteration order.

### 3. `/exec`

When the first two steps are complete and you decide to implement, run `/exec 1`. The agent will execute the implementation plan.

In this process the agent would:
    - main agent would create a todo list reflecting PLAN.md
    - delegate each phase implementation to one subagent, one-by-one
    - make sure they completed
    - Run command `spec-iter update {{iter_id}} executed`

This step also requires no human intervention and can be resumed after termination. After execution, the iteration is at the `executed` stage. Check what was implemented and whether it meets your goal.

After the first iteration has executed, it is usually a good time to create a proper `AGENTS.md` for the project so future agent work has clear project-specific guidance.

### 4. `/iter`

`/iter` is an experimental command that combines planning and execution into one workflow. When `SPEC.md` is ready, run `/iter 1` to have the agent create `PLAN.md` and then execute it phase by phase.

In this process the agent would:
    - delegate PLAN.md creation to one `@plan-creator` subagent
    - delegate each phase implementation to one `@phase-executor` subagent, one-by-one
    - Run command `spec-iter update {{iter_id}} executed`

This command is intended for lower-friction iteration, but `/plan` and `/exec` remain the recommended stable workflow when you want to review the plan before implementation.

### 5. `/post`

Run `/post 1` to complete the iteration. Today this mainly performs a document review and creates a git commit. Verification features are planned.

After this step, the iteration stage changes to `completed`.

## Requirements

- OpenCode CLI
- uv
- Python 3.9+
- Git

Recommended extensions:

- [agents-md-skill](https://github.com/g0g5/agents-md-skill) for creating and maintaining project `AGENTS.md` guidance. The previous `/agentsmd` workflow has moved to this separate agent skill project.
- [opencode-websearch](https://github.com/emilsvennesson/opencode-websearch), an OpenCode-native web search plugin that uses your provider's internal web search tool. It supports providers such as OpenAI via API or ChatGPT subscription, Moonshot.ai via Kimi API or coding plan, GitHub Copilot, and others. Otherwise, configure at least one valid web search method, such as DuckDuckGo MCP, Tavily, or another provider.

## License

[MIT License](LICENSE)
