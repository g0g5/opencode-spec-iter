- Write concise AGENTS.md following this structure:

```markdown
## Project Overview
[One sentence: what this project does and its core stack.]

## Structure Map
[Generate a module-level tree view with one-line descriptions after `#`. Show only folders and single-file modules; do not list files inside folder modules. Exclude dot-prefixed internals. In monorepos, include each app/package as top-level modules.]

Example:

my-ts-service/
|- src/                    # Runtime application modules for the service
|  |- server.ts            # Boots HTTP server and initializes app startup flow
|  |- config.ts            # Loads and validates environment/app configuration
|  |- auth/                # Authentication and authorization module
|  |- users/               # User domain logic and related operations
|  \- common/              # Shared utilities, types, and cross-cutting helpers
|- docs/                   # Project documentation for developers and maintainers
|  |- api/                 # API contracts, endpoint behavior, and examples
|  \- architecture/        # System design, decisions, and module boundaries
\- tests/                  # Automated test modules
   |- unit/                # Fast tests for isolated module behavior
   \- integration/         # Tests for module interactions and external boundaries

## Development Guide
[Minimal workflow: how to build, test, and verify changes.]
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information
