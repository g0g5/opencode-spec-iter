---
description: Execute post implementation affairs.
agent: build
---

You execute post-implementation tasks for iteration `$ARGUMENTS`.

Follow this workflow strictly:

1. Inspect local changes.
   - Run `git status`.
   - Run `git diff`.

2. Update `AGENTS.md` to exactly match this required template and section names:

```
## Project Overview

Describe what the project does and the core stack in one or two sentences.

Example:

`<project-name>` is `<something for one-sentence purpose>`. Built with `<language/framework>`, using `<data/storage>`, and tested with `<testing tool>`.

## Structure Map

List agent-facing modules at folder level (include single-file modules but ignore internal files).
Exclude all dot-prefixed folders/files (e.g., `.agent/`, `.cache/`).

### Development Guide

Provide the minimal local workflow in one or two sentences, including how to run, verify, and build.
```

3. Create the iteration completion report at:
   - `.agent/iterations/$ARGUMENTS/FINISHED.md`
   - Keep it concise and implementation-focused.

4. Commit all post-implementation changes.
   - Include updated `AGENTS.md` and `.agent/iterations/$ARGUMENTS/FINISHED.md`.
   - Use a concise commit message describing completion of post-implementation tasks.
