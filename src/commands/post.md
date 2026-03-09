---
description: Execute post implementation affairs.
agent: build
---

You execute post-implementation tasks for iteration `$ARGUMENTS`.

Follow this workflow strictly:

1. Inspect local changes.
   - Run `git status`.
   - Run `git diff`.

2. Create the iteration completion report at:
   - `.speciter/iterations/$ARGUMENTS/FINISHED.md`
   - Keep it concise and implementation-focused.

3. Commit all post-implementation changes.
   - Include updated `AGENTS.md` and `.speciter/iterations/$ARGUMENTS/FINISHED.md`.
   - Use a concise commit message describing completion of post-implementation tasks.
