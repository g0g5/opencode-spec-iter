---
description: Create or update the AGENTS.md for Spec Iter
agent: build
---

Create or update AGENTS.md to help agents understand the project.

**Process:**
1. If AGENTS.md exists, read it first for context
2. Inspect workspace to understand: tech stack (WHAT), purpose (WHY), and key commands (HOW - build/test/typecheck only)
3. Write concise AGENTS.md following this structure:

```markdown
## Project Overview
<One sentence: what this project does and its core stack.>

## Structure Map
<Bullet list of agent-facing directories/files (exclude dot-prefixed internals).
In monorepos, list each app/package with one-line description.>

## Development Guide
<Minimal workflow: how to build, test, and verify changes.>
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information