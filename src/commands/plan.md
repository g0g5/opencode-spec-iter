---
description: Create the implementation plan based on the spec document.
agent: build
---

You need to create the implementation plan based on .agent/iterations/$ARGUMENTS/spec.md.

Follow this workflow strictly:

1. Verify `.agent/iterations/$ARGUMENTS/spec.md` exists.
   - If `spec.md` is not found, stop immediately and report that the plan cannot be created because the spec file is missing.

2. Create the implementation plan from the spec.
   - Produce a clear and concise implementation plan.
   - Structure the plan as phases with step-by-step actions under each phase.
   - Do not include time schedules, dates, deadlines, or milestones.

3. Save the plan document.
   - Save the plan as `.agent/iterations/$ARGUMENTS/plan.md`.
