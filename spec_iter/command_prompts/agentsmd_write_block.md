- Write concise AGENTS.md following this structure:

```markdown
## Project Overview
[One sentence: what this project does and its core stack.]

## Structure Map
[Generate a structure tree with one-line descriptions after `#`. Always include the meaningful directory hierarchy, including deeper nested directories when they clarify module boundaries. For files, be selective: include only architecturally important files, such as entrypoints, shared foundations, registries, orchestration files, and files that other project code depends on. Omit leaf implementation files and repetitive sibling files that are mostly interchangeable or isolated variants (for example per-provider configs, individual NPC definitions, or one-off adapters), unless one is the canonical entrypoint or shared base. Exclude dot-prefixed internals and generated/build/cache/vendor directories unless they are part of the core source layout. In monorepos, include each app/package as a top-level module.]

Example:

my-ts-service/
|- src/                        # Runtime application modules for the service
|  |- server.ts                # Boots the HTTP server and application startup flow
|  |- config.ts                # Loads and validates environment and service config
|  |- auth/                    # Authentication and authorization module
|  |  |- routes.ts             # Registers auth HTTP routes
|  |  |- service.ts            # Coordinates login, token, and session logic
|  |  \- providers/           # External auth provider integrations
|  |     \- ...               # Folded provider implementations such as google.ts and github.ts
|  |- users/                   # User domain logic and related operations
|  |  |- repository.ts         # Shared persistence interface for user data access
|  |  \- profiles/            # Profile-related user flows
|  |     |- controller.ts      # Handles profile HTTP endpoints
|  |     \- service.ts         # Orchestrates profile read/write operations
|  \- common/                  # Shared utilities, types, and cross-cutting helpers
|     |- errors.ts             # Common application error types
|     \- ...                   # Folded helpers such as logging.ts and metrics.ts
|- docs/                       # Project documentation for developers and maintainers
|  |- api/                     # API contracts, endpoint behavior, and examples
|  \- architecture/           # System design, decisions, and module boundaries
\- tests/                      # Automated test modules
   |- unit/                    # Fast tests for isolated module behavior
   |  \- ...                   # Folded unit suites for auth, users, and common helpers
   \- integration/             # Tests for module interactions and external boundaries

## Development Guide
[Minimal workflow: how to build, test, and verify changes.]
```

**Rules:**
- Be concise: no long prose, no unnecessary details
- Focus on what agents need to know to be productive
- Exclude obvious or rarely-used information
