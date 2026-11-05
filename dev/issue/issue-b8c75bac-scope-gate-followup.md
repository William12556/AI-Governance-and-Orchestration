Created: 2026 November 5

```yaml
issue_info:
  id: "issue-b8c75bac"
  title: "Scope and gate follow-up: edit-failure check on refused calls, case-sensitive write verbs, test gaps"
  date: "2026-11-05"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-b8c75bac"
    change_iteration: 1

source:
  origin: "code_review"  # follow-up audit audit-a5bd4fe1
  description: >
    Findings F-01, F-02 and F-04 of
    dev/audit/audit-a5bd4fe1-followup-2026-11-05.md (§8.4, §11.0), with the
    operator decision of 2026-11-05 to fix F-01 and F-02 and to add the tests
    U1, U4, U5 and U10. F-03 and F-05 were documented by the planner; F-06 to
    F-08 need no action.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "scope", file_path: "ai/engine/src/scope.py" }
    - { name: "engine tests", file_path: "tests/engine/test_scope_gate_hardening.py" }
  designs:
    - { design_ref: "design-14e05e35 §7.0 (tool classification), §11.0 (Error Handling)" }
  version: "governance 12.8; engine at main after change-a5bd4fe1"

reproduction:
  prerequisites: "Engine after change-a5bd4fe1"
  steps:
    - "F-01: the worker calls edit_file with a path that contains E_INVALID_INPUT and lies outside the project, or with such a path that also contains NUL"
    - "F-02: offer a tool named searchAndReplace, read_and_append or list_update"
    - "F-04: apply mutations U1, U4, U5 and U10 of audit-a5bd4fe1 §6.0"
  frequency: "always, under the stated condition"
  error_output: "F-01 (probe): an out-of-project file is compiled; with NUL, ValueError: embedded null byte ends the engine run without BLOCKED.md"

behavior:
  expected: >
    F-01: the edit-failure corrective and its compile run only for a call
    that was dispatched, and no compile error at the edit-failure or
    post-write site ends the run. F-02: a tool name that contains a write
    verb, in any letter case, is a write tool. F-04: the status combinations
    of the pytest gate, the preflight bytecode placement, FR-D on the audit
    path and the refused-call case each have a test.
  actual: >
    F-01: _edit_pattern_failed tests only the tool name and the result text;
    a refusal echoes the worker's path, so the marker can come from the path;
    only TimeoutExpired is caught around compile_file. F-02: write verbs are
    a fixed lower-case list matched case-sensitively, so read-prefixed names
    with a capitalised or unlisted verb are read-only. F-04: mutations U1,
    U4, U5 and U10 survive the suite.
  impact: "A worker-chosen path can make the engine compile an out-of-project file or end the run with a traceback; a write tool of another MCP server can bypass the scope check and be offered to the reviewer; four specified behaviours can regress unnoticed."
  workaround: "Use the configured MCP servers; watch runs."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    F-01: orchestrator.py:94-97 (_EDIT_PATTERN_ERRORS), :1509-1537
    (edit-failure check), :1605-1608 (post-write check catches only
    TimeoutExpired). F-02: scope.py:42-43 (WRITE_NAME_PATTERNS), :67-75
    (is_readonly_tool). F-04: audit-a5bd4fe1 §6.0. Line numbers at aace3f6.
  technical_notes: >
    F-01 is pre-existing in kind (before change-a5bd4fe1 a NUL path was
    dispatched and the server error could carry E_INVALID_INPUT). Audit
    proposal for F-02: match write verbs case-insensitively and add append,
    copy, truncate, save, update, upload, set, put and insert; check every
    tool of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep keeps its class
    (for example 'set' must not match an existing read tool name).

resolution:
  approach: "To be defined in change-b8c75bac."
  change_ref: "change-b8c75bac"

traceability:
  design_refs: ["design-14e05e35"]
  change_refs: ["change-b8c75bac"]

notes: "Audit references: audit-a5bd4fe1 F-01, F-02, F-04; operator decisions 2026-11-05. Predecessor: issue-a5bd4fe1 (closed)."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-a5bd4fe1"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
