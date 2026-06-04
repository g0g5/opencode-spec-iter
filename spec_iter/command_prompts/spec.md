Based on above user idea, follow this workflow strictly:

1. Gather requirements with the `question` tool.
   - The first question must be: `Iteration name`.
   - Suggest a kebab-case default iteration name derived from the user idea.
   - Keep asking follow-up questions until you have enough information to write a complete SPEC.

2. Run command `spec-iter new <iteration-name>`, where `<iteration-name>` is the confirmed iteration name from step 1.

3. Inspect and understand the current workspace situation.
   - Delegate the exploration to one `@explore` agent.
   - Focusing on goal related parts.

4. Identify external library dependencies needed for this iteration.
   - List the key libraries that are likely required.
   - Review these existing docs in .speciter/docs/ first to understand what has already been researched. 
   - Focus new research only on libraries, APIs, or patterns not yet covered.
   - Delegate research to `@general` agents, one agent per library.
   - Use this exact delegation prompt template:
     - `{{research_prompt}}`
   - Read the research reports in .speciter/docs/

5. Create the SPEC document.
   - Read `.speciter/templates/SPEC.md` and use it as the required template.
   - Fill every template section with concise but actionable content based on the gathered QAs, workspace exploration, and research reports.
   - Keep sections that are not applicable and write `N/A` with a brief reason instead of deleting them.
   - Save it to: `.speciter/iterations/<iteration-name>/SPEC.md`,
   - Run command `spec-iter update 1 specified`
{{agentsmd_step}}
