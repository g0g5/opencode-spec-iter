Create a iter-manager.py script. The script manages all iterations in the project's .speciter/ folder.

Interaction: CLI parameters

1. `python iter-manager new [iteration-name]`: Create a new managed iteration.
    - If .speciter/iters.json not exists, create it.
    - transform the input iteration-name to lowerbound kebab-case
    - create .speciter/iterations/[iteration-name]/ directory
    - add the new iteration with iteration name into "iterations : [...]", with following example.
    - sort the iterations by timestamp, most recent is at top; later it is, more behind it puts.

    - Example:
```json
{
    "time": <timestamp of create or modification>,
    "name": "iteration-name",
    "stage": "new", 
}
```
    

2. `python iter-manager list [optional: n]`: list all or top n iterations by ranking, print the names and their stages.

3. `python iter-manager [id] spec`: verify if SPEC.md exists and print the SPEC.md path of iteration by id. Example: ".speciter/iterations/[iteration-name]/SPEC.md" or "Error: SPEC.md not found of [iteration-name]."


4. `python iter-manager [id] plan`: verify if SPEC.md exists and print the PLAN.md path of iteration by id. Example: ".speciter/iterations/[iteration-name]/PLAN.md" or "Error: PLAN.md not found of [iteration-name]."

5. `python iter-manager [id] update [spec|plan|execute|post|completed]`: update iteration stage.