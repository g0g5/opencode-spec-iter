# Spec Iter

## Project Overview

Spec Iter is a Python companion CLI for OpenCode that installs bundled slash-command templates into projects and manages a spec-driven iteration workflow under `.speciter/`.

## Structure Map

```text
spec-iter/
|- spec_iter/                  # Runtime package for the installed `spec-iter` CLI
|  |- cli.py                   # argparse entrypoint and command dispatch
|  |- init.py                  # Project initialization, managed command install, legacy cleanup
|  |- iterations.py            # Iteration metadata, id resolution, stage updates, path helpers
|  |- project.py               # Upward project-root discovery and display-path helpers
|  |- prompts.py               # Prompt generation for command and delegated subagent flows
|  |- command_prompts/         # Markdown prompt templates rendered for top-level command flows
|  |- subagent_prompts/        # Markdown prompt templates rendered for delegated subagent tasks
|  \- commands/               # Markdown templates copied into `.opencode/commands/`
|- docs/                       # Design notes and implementation planning docs
|- pyproject.toml              # Packaging metadata and console script entrypoint
|- README.md                   # User-facing install and workflow documentation
|- AGENTS.md                   # Project guidance for coding agents
|- install.py                  # Backward-compatible wrapper for `spec-iter init`
\- clify.spec.md              # Current CLI companion refactor spec
```

## Development Guide

- Primary workflow: update package code in `spec_iter/` and bundled command templates in `spec_iter/commands/` together.
- Installation model: prefer `uv tool install .` for local validation; end-user workflow is `spec-iter init`, then `spec-iter ...` inside initialized projects.
- Verification: run `python -m compileall spec_iter` after Python changes; manually validate `spec-iter init`, `spec-iter new`, `spec-iter list`, `spec-iter update`, and `spec-iter prompt ...` in a temp project when behavior changes.
- Prompt templates: keep markdown concise; command prompts live in `spec_iter/command_prompts/`, delegated-agent prompts live in `spec_iter/subagent_prompts/`, and OpenCode expands `$` placeholders plus inline shell snippets before sending the final prompt to the model.
- Scope: managed runtime behavior now lives in package modules, not copied `.opencode/scripts/` helpers; preserve backward-compatible init migration behavior when changing project setup.
