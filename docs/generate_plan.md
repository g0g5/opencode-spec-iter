Create a Python script to dynammically generate LLM agent prompt for creating plan based on SPEC.md. The script import IterManager for iterations related functionalities. The workflow:

1. try to get the iteration spec path by id (directly pass `$ARGUMENTS` as id).
2. generate the prompt based on result

- If SPEC.md not exists:
    prompt: "SPEC.md not found. Tell the user to run `/spec` to create the SPEC.md first."
- If SPEC.md exists:
    prompt:

"""
You need to create the implementation plan based on [SPEC.md path]

Follow this workflow strictly:

1. Create the implementation plan from the spec.
   - Produce a clear and concise implementation plan.
   - Structure the plan as phases with step-by-step actions under each phase.
   - Do not include time schedules, dates, deadlines, or milestones.

2. Save the plan document.
   - Save the plan as `[iteration path]/PLAN.md`.
"""