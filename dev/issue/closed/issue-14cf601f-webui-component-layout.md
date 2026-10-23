Created: 2026 October 23

```yaml
issue_info:
  id: "issue-14cf601f"
  title: "Framework source layout: ai/src/ is a bare source folder at the ai/ root"
  date: "2026-10-23"
  status: "closed"
  severity: "low"
  type: "requirement_change"
  iteration: 1
  coupled_docs:
    change_ref: "change-14cf601f"
    change_iteration: 1

source:
  origin: "requirement_change"
  description: >
    The operator intends to fold all framework functionality into a future
    central web UI (scope not yet decided). Source organisation must be
    coherent and support that direction with an open and flexible
    architecture. ai/src/ holds only overwatch.py and its requirements file
    since govwatch was retired (change-5bcd46ad). A bare src/ at the ai/
    root is not a component and does not fit the component layout used by
    ai/engine/.

affected_scope:
  components:
    - { name: "overwatch", file_path: "ai/src/overwatch.py, ai/src/requirements-overwatch.txt" }
    - { name: "overwatch tests", file_path: "tests/overwatch/test_overwatch.py, tests/engine/test_engine_mcp.py" }
    - { name: "scripts", file_path: "bin/migrate-terms.py" }
  designs:
    - { design_ref: "dev/design/design-project-overwatch.md (paths only)" }
  version: "governance 12.4"

behavior:
  expected: >
    Framework source is organised by component. Each component sits at the
    same level under ai/ with the same internal shape (src/, optional doc/,
    requirements.txt, tests/<component>/). A component for the future
    central UI exists, with Overwatch as its current module, and a shared
    core component is reserved for code shared between components.
  actual: "Overwatch sits in a bare ai/src/ folder with no component of its own."
  impact: "Layout does not express component boundaries; a later UI would have no defined home."
  workaround: "None needed; no behavioural fault."

analysis:
  root_cause: >
    ai/src/ was created as a general-purpose tools folder for govwatch
    (requirements-govwatch §2.0, closed). After govwatch's retirement the
    rationale no longer holds.
  technical_notes: >
    overwatch.py imports only the standard library and yaml; it has no
    dependency on ai/engine/src/ and does not resolve paths from __file__.
    bin/propagate.sh relocates target files absent from the source to
    ai-local/ with the label 'retired framework file', so a downstream
    ai/src/ is handled without script change.

resolution:
  approach: "Move Overwatch into a new ai/webui/ component; reserve ai/core/; see change-14cf601f."
  change_ref: "change-14cf601f"

traceability:
  design_refs: ["dev/design/design-project-overwatch.md", "dev/proposals/proposal-5bcd46ad-ai-go-pivot.md §4.0–5.0"]
  change_refs: ["change-14cf601f"]

version_history:
  - version: "1.0"
    date: "2026-10-23"
    changes: ["Initial issue (abbreviated triple, operator instruction 2026-10-23)"]
  - version: "1.1"
    date: "2026-10-23"
    changes: ["Closed: resolved by change-14cf601f (merged at 1a76d51); audit waived at operator direction"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
