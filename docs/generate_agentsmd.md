
1. Scan the project folder (script's runtime CWD), to find existing agent instruction files:
    - CLAUDE.md
    - AGENTS.md
    - other possible files, configurable in a list

2. Get the recent git commits (`git log --oneline -10`), if git local repo exists.

3. Concat the strings of prompt based on results:

Beginning of prompt:

if exists AGENTS.md:
    - "You are now facing an established project with AGENTS.md. The AGENTS.md may need update. Create a TODO list and follow the workflow strictly:"
else if AGENTS.md does not exist:
    - "You are now facing an project without AGENTS.md. You need to create AGENTS.md. Create a TODO list and follow the workflow strictly:"

First steps:

if exists any instruction file:
    - "- Read the found instruction files for context: [list all found instruction files]"

if exists git repo, show recent commits:
    - "- Read the following recent commit messages: [insert recent git commits here]"

Main steps:

if exists AGENTS.md:
    - "- Inspect workspace, focusing on project structure changes which may conflict existing AGENTS.md"
else if AGENTS.md does not exist:
    - "- Inspect workspace to understand: 
    - WHAT — Describe the tech stack, project structure, and purpose of each major directory/package. In monorepos, explicitly list every app and shared package with a one-line description of what it does.
    - WHY — State the project's purpose and the role of each major component.
    - HOW — Specify only the most universally-needed commands: how to build, run tests, run typechecks, and verify changes. Do not list every possible command—only the ones used in nearly every task."

Final generation instruction (in all conditions):
"- Write concise AGENTS.md following this structure:

```markdown
## Project Overview
[One sentence: what this project does and its core stack.]

## Structure Map
[Bullet list of agent-facing directories/files (exclude dot-prefixed internals).
In monorepos, list each app/package with one-line description.]

## Development Guide
[Minimal workflow: how to build, test, and verify changes.]
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information
"