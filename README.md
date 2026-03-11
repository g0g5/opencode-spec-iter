# Spec Iter

Spec-driven iterative development workflow plugin for [OpenCode](https://opencode.ai).

## Overview

Spec Iter adds structured, spec-driven development commands to OpenCode. It breaks down complex features into manageable iterations with clear specifications, implementation plans, and execution tracking.

## Installation

```bash
# Clone the repository
git clone https://github.com/g0g5/opencode-spec-iter
cd spec-iter

# Install to your project
python install.py
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

## Workflow

1. **Spec** - Define what to build with requirements and dependencies
2. **Plan** - Break down into actionable implementation steps
3. **Exec** - Execute the plan step by step
4. **Post** - Handle cleanup, tests, documentation

## Project Structure

```
spec-iter/
├── src/
│   ├── commands/       # Markdown-based LLM prompts
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── exec.md
│   │   ├── post.md
│   │   └── agentsmd.md
│   └── scripts/        # Python execution scripts
│       ├── iter_manager.py
│       ├── prompt-plan.py
│       ├── prompt-exec.py
│       └── prompt-post.py
└── install.py          # Installation script
```

## Development Philosophy

- **Markdown-first**: LLM prompts are written in markdown for readability
- **Minimal Python**: Scripts handle execution, not logic
- **Concise**: Avoid long prose, focus on actionable outputs

## Requirements

- OpenCode CLI
- Python 3.x
- Git

## License

[MIT License](LICENSE)
