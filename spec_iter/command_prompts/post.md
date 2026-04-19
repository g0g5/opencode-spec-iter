You execute post-implementation tasks for iteration `{{iter_id}}`.

Follow this workflow strictly:

1. Review local changes (already provided below):

Git Status:
```
{{git_status}}
```

Git Diff (stats):
```
{{git_diff}}
```

2. Create the iteration completion report at:
   - `{{finished_path}}`
   - Keep it concise and implementation-focused.

3. Run command `spec-iter update {{iter_id}} completed`

4. Commit all changes, regardless created by this iteration or not.