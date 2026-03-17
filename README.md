# Spec Iter

Spec-driven iterative development workflow plugin for [OpenCode](https://opencode.ai).

## Overview

Spec Iter adds structured, spec-driven development commands to OpenCode. It breaks down complex features into manageable iterations with clear specifications, implementation plans, and execution tracking.

## Installation

```bash
# Install directly from git repo via uvx
uvx --from git+https://github.com/g0g5/opencode-spec-iter spec-iter /path/to/your/project/

# Or clone and run locally
git clone https://github.com/g0g5/opencode-spec-iter
cd spec-iter
python install.py /path/to/your/project/
```

Enter your project directory path when prompted. The installer will:
- Copy plugin files to `.opencode/`
- Create `.speciter/` directory for iteration management
- Initialize `iters.json` for tracking
- Update `.gitignore`

## Commands

After installation, these commands become available in OpenCode:

| Command | Description | Agent |
|---------|-------------|-------|
| `/spec <feature-idea>` | Create a specification document for your feature | build |
| `/plan <iteration-id>` | Generate implementation plan from spec | build |
| `/exec <iteration-id>` | Execute the implementation plan | plan |
| `/post <iteration-id>` | Run post-implementation tasks | build |
| `/agentsmd` | Create/update AGENTS.md project context | build |

## Full Walkthrough

This is the typical end-to-end workflow after the plugin is installed into a project.

**How commands become prompts**: OpenCode loads markdown templates from `.opencode/commands/` (installed from this package's bundled assets). Placeholders like `$1`, `$2`, `$ARGUMENTS` are replaced with your command arguments. Inline shell snippets (``!`command` ``) execute and their output is inserted into the prompt. The LLM only sees the final rendered prompt, not the template.

### 1. Create a spec with `/spec`

Example:

```text
/spec add article summarization with citations for a knowledge base app
```

**What happens to your command**:

OpenCode loads `.opencode/commands/spec.md` and replaces `$ARGUMENTS` with your feature idea. The model receives the full template with your idea filled in.

**What the model sees and does**:

- Reads your feature idea
- Pulls in any linked docs via `webfetch` if URLs are present
- Asks follow-up questions (starting with "Iteration name")
- Researches external libraries by delegating to `@explore` agents
- Creates iteration: `python ./.opencode/scripts/iter_manager.py new <iteration-name>`
- Writes spec to `.speciter/iterations/<iteration-name>/SPEC.md`
- Updates stage: `python ./.opencode/scripts/iter_manager.py update 1 specified`

### 2. Create the plan with `/plan 1`

Example:

```text
/plan 1
```

**What happens to your command**:

OpenCode loads `.opencode/commands/plan.md`, which contains ``!`python ./.opencode/scripts/prompt-plan.py $1` ``. The shell executes with `$1` = `1`, and the script's output replaces the shell snippet. The model receives only the rendered prompt from the script.

**What the model sees and does**:

The script generates a prompt like:
```
You need to create the implementation plan based on .speciter/iterations/<name>/SPEC.md

Follow this workflow strictly:
1. Create the implementation plan from the spec...
2. Save the plan as `.speciter/iterations/<name>/PLAN.md`...
```

The model writes the plan and updates stage to `planned`.

**Why id `1` works**: Iteration IDs are positional. `1` always means "most recent" (sorted by last updated). Use `/list-iters` to see the current mapping.

### 3. Execute implementation with `/exec 1`

Example:

```text
/exec 1
```

**What happens to your command**:

OpenCode loads `.opencode/commands/exec.md` with ``!`python ./.opencode/scripts/prompt-exec.py $1` ``. The script checks that `PLAN.md` exists, then outputs the execution prompt. The model receives only this generated prompt.

**What the model sees and does**:

The prompt instructs the model to:
- Read `PLAN.md` and create a todo list
- Use `task` to delegate one phase at a time to `@general` agents
- Each delegated agent receives: "Read SPEC.md and PLAN.md, complete phase N"
- After all phases, update stage to `executed`

This is controlled implementation: plan-guided, phase-by-phase, single-threaded to avoid edit conflicts.

### 4. Run post-implementation with `/post 1`

Example:

```text
/post 1
```

**What happens to your command**:

OpenCode loads `.opencode/commands/post.md` with ``!`python ./.opencode/scripts/prompt-post.py $1` ``. The script runs `git status --short` and `git diff --stat`, embedding the results in the generated prompt.

**What the model sees and does**:

The prompt includes actual git status/diff output, then instructs:
- Review the changes (already shown)
- Write `.speciter/iterations/<name>/FINISHED.md`
- Commit all changes
- Update stage to `completed`

### 5. Create project context with `/agentsmd`

Example:

```text
/agentsmd
```

**What happens to your command**:

OpenCode loads `.opencode/commands/agentsmd.md` which executes ``!`python ./.opencode/scripts/prompt-agentsmd.py` ``. The script scans for context files (`README.md`, `AGENTS.md`, etc.) and recent git commits, then outputs a prompt to generate/update project context.

**What the model sees and does**:

Receives a prompt with discovered project files and conventions, then creates/updates `AGENTS.md` with a concise project overview, structure map, and development guide.

**When to run**: After project setup, or before `/post` if the project structure changed during implementation.

### Command-to-Prompt Reference

| Command | Template File | Shell Execution | Final Prompt Source |
|---------|--------------|-----------------|---------------------|
| `/spec <idea>` | `.opencode/commands/spec.md` | None | Template with `$ARGUMENTS` replaced |
| `/plan <id>` | `.opencode/commands/plan.md` | `prompt-plan.py $1` | Script stdout |
| `/exec <id>` | `.opencode/commands/exec.md` | `prompt-exec.py $1` | Script stdout |
| `/post <id>` | `.opencode/commands/post.md` | `prompt-post.py $1` | Script stdout (includes git status) |
| `/agentsmd` | `.opencode/commands/agentsmd.md` | `prompt-agentsmd.py` | Script stdout |
| `/list-iters` | `.opencode/commands/list-iters.md` | `iter_manager.py list` | Direct script output to user |



## Project Structure

```
spec-iter/
├── spec_iter/
│   ├── cli.py                     # Installer CLI entrypoint (`spec-iter`)
│   └── bundled_src/
│       ├── commands/              # Markdown-based command templates
│       └── scripts/               # Python helper scripts for templates
├── pyproject.toml                 # Packaging and console script config
└── install.py                     # Backward-compatible wrapper (`python install.py`)
```

## Development Philosophy

- **Markdown-first**: LLM prompts are written in markdown for readability
- **Minimal Python**: Scripts handle execution, not logic
- **Concise**: Avoid long prose, focus on actionable outputs

## Requirements

- OpenCode CLI
- uv (for `uvx` installation)
- Python 3.x
- Git

## License

[MIT License](LICENSE)
