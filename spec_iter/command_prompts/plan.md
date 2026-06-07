You need to create the implementation plan based on {{spec_path}}

Follow this workflow strictly:

0. Read `.speciter/templates/PLAN.md` and treat it as the required template for all following steps.

1. Create the implementation plan from the spec.
   - Fill every template section with concise but actionable content from `{{spec_path}}`.
   - Keep sections that are not applicable and write `N/A` with a brief reason instead of deleting them.
   - Structure the plan as numbered phases.
   - Use the template phase blocks as a pattern; create as many phases as needed and do not leave placeholder phase headings or `...` in the saved plan.
   - Every phase must include `Status`, a concise plain-text description covering goal, scope, implementation steps, and verification, plus `Completion Log`.
   - Keep every step concrete enough that another agent can perform it without inferring hidden requirements.
   - Set initial phase statuses to `pending`.
   - Set initial completion logs to `N/A`.
   - Do not include time schedules, dates, deadlines, or milestones.

2. Save the plan document.
   - Save the plan as `{{plan_path}}`.
   - Run command `spec-iter update {{iter_id}} planned`
