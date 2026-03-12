# Spec Iter

Spec Iter is a OpenCode project-level plugin that contains LLM agent commands for spec-driven iterative development workflow.

## What is OpenCode

OpenCode is an open-source coding agent that operates across terminal, desktop, and IDE environments with configurable sub-agents and multi-provider LLM support. A coding agent product is a host runtime for an LLM-based programmer: a managed environment that supplies the model with workspace access, tools, memory/state, guardrails, and orchestration, so the model can perform multi-step engineering work instead of only answering prompts.

## Project Structure

/src -> the plugin's "source code". to be installed to elsewhere as ".opencode" folder.

## Development

- Markdown-based LLM prompting + minimal Python scripting.
- OpenCode loads markdown files in `src/commands/` as prompt templates.
- When a user runs a command such as `/command params`, OpenCode fills `$` placeholders in the template with the command arguments, similar to f-string interpolation.
- If the template contains inline shell snippets like ``!`shell command` ``, OpenCode executes them while building the prompt.
- The model API receives only the fully rendered final prompt, not the original command template or inline shell commands.
- Keep everything (prompts, scripts) concise and minimalist, avoid long prose.
