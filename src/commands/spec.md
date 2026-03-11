---
description: Create the specification document based on user's idea.
agent: build
---

In this iteration, the user wants to build: 

$ARGUMENTS

Follow this workflow strictly:

1. If any web page link exist in user ideas, use `webfetch` to fetch and read all the links for context.

2. Gather requirements with the `question` tool.
   - The first question must be: `Iteration name`.
   - Suggest a kebab-case default iteration name derived from the user idea.
   - Keep asking follow-up questions until you have enough information to write a complete SPEC.

3. Identify external library dependencies needed for this iteration.
   - List the key libraries that are likely required.
   - Delegate research to `@explore` agents, one agent per library.
   - Each delegated agent must focus on only one library and return:
     - highly concise code examples directly related to the iteration goal,
     - implementation-focused outputs that show how to use the library,
     - minimal prose (focus on "how", not "why").
   - Use this exact delegation prompt template:
     - `Do web search to find out latest documentation of <library name>, about <related topics to iteration's goal>, return highly concise code examples of how to use the library with minimal prose.`

4. Create the SPEC document.
   - Run command `python ./.opencode/scripts/iter_manager.py new <interation-name>`, where `<iteration-name>` is the confirmed iteration name from step 2.
   - Write a concise but actionable SPEC using the gathered answers and library research.
   - Save it to: `.speciter/iterations/<iteration-name>/SPEC.md`, 
   - Run command `python ./.opencode/scripts/iter_manager.py 1 update specified`