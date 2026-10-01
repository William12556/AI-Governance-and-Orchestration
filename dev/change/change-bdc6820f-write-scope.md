Created: 2026 October 01

```yaml
change_info:
  id: "change-bdc6820f"
  title: "Phase 2 step 3: worker write scope and reviewer deliverables block"
  date: "2026-10-01"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0); no issue document
    issue_iteration: null

source:
  type: "design"
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.2, §7.0"
  description: "Step 3 of the Phase 2 implementation plan: write scope (FR-05); backlog §5.0-7 and §5.0-8; audit-5bcd46ad L-09."

scope:
  summary: >
    Add ai/engine/src/scope.py as the single source of write-tool
    classification (used by the scope check, the loop and mcp_client) and of
    the write scope. For a T03 prompt task the worker may write only the
    prompt's deliverable.files, the manifest's writable_paths and the state
    directory; other writes return a tool error and are logged. Free-text and
    other non-prompt tasks keep project-root containment. The reviewer task
    receives a [DELIVERABLES] block with absolute paths.
  affected_components:
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "add" }
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "MCP client", file_path: "ai/engine/src/mcp_client.py", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_write_scope.py", change_type: "add" }
    - { name: "documents", file_path: "ai/engine/doc/guide-engine-operations.md, ai/engine/README.md", change_type: "modify" }
  out_of_scope:
    - "Run-type-specific writable paths (not needed: audit runs write only the state directory)"

rational:
  problem_statement: >
    Workers wrote unrequested files (backlog §5.0-7); the reviewer resolved a
    relative deliverable path against the state directory (§5.0-8); write
    classification was duplicated and fail-open in the scope check (L-09).
  proposed_solution: "Deliverable-based allowlist, absolute deliverable paths for the reviewer, one fail-closed classification."
  risks:
    - "A prompt whose deliverable.files omits a file the worker must write now gets a tool error for that write; the operator adds the file to the prompt or to writable_paths"
    - "Tools whose names contain a write verb are now scope-checked (fail-closed), which can reject a tool that only reads"

testing_requirements:
  validation_criteria:
    - "All existing tests pass unchanged"
    - "Deliverable, writable-path and state-directory writes allowed; others rejected and logged; directory creation for a deliverable's parent allowed; move checks source and destination; free-text tasks keep root containment; [DELIVERABLES] block holds absolute paths"

implementation:
  rollback_procedure: "Revert the commit."

traceability:
  requirements: ["FR-05-01", "FR-05-02", "FR-05-03", "FR-05-04", "NFR-02", "NFR-06"]
  design: "design-14e05e35 §7.0"
  prompt: "dev/prompt/closed/prompt-bdc6820f-write-scope.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
