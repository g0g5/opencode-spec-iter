---
description: Execute the implementation plan of iteration.
agent: plan
---

You orchestrate execution of `.agent/iterations/$ARGUMENTS/plan.md`.
Your role is coordination and oversight only. Do not write or edit any files yourself.

Follow this workflow strictly:

1. Verify `.agent/iterations/$ARGUMENTS/plan.md` exists.
   - If missing, stop immediately and tell the user execution cannot continue because the plan is missing.
   - If present, use `todowrite` to create and maintain a todo list for all plan steps.
2. Delegate exactly one implementation step at a time to one `@general` agent.
   - Never run multiple implementation agents in parallel; this avoids edit conflicts.
3. For each delegated step, send this exact instruction to the `@general` agent:
   - `Read spec.md and plan.md in .agent/iterations/$ARGUMENTS/, complete <step number>.`
4. When a step is finished, delegate the next step to a new `@general` agent.
5. After all steps are complete, report what was done to the user.
