---
description: Create the specification document based on user's idea.
agent: build
---

In this iteration, the user wants to build:

$ARGUMENTS

Follow this workflow strictly:

1. If any web link or file exist in user ideas, read them for the context.

2. Gather requirements with the `question` tool.
   - The first question must be: `Iteration name`.
   - Suggest a kebab-case default iteration name derived from the user idea.
   - Keep asking follow-up questions until you have enough information to write a complete SPEC.

3. Run command `spec-iter new <iteration-name>`, where `<iteration-name>` is the confirmed iteration name from step 2.

4. Identify external library dependencies needed for this iteration.
   - List the key libraries that are likely required.
   - Delegate research to `@general` agents, one agent per library.
   - Use this exact delegation prompt template:
     - `Do web search to find out latest documentation of <library name>, about <related topics to iteration's goal>, return highly concise code examples of how to use the library with minimal prose. Save a report as ./docs/<topic>.md`
   - Read the research reports in docs/

5. Create the SPEC document.
   - Write a concise but actionable SPEC using the gathered answers and library research. Avoid long prose, use researched code examples.
   - Save it to: `.speciter/iterations/<iteration-name>/SPEC.md`,
   - Run command `spec-iter update 1 specified`
