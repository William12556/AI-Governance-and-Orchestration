Created: 2026 June 26

```yaml
issue_info:
  id: "issue-c8b3e9a1"
  title: "Tactical Domain has no write containment and the reviewer is not read-only"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c8b3e9a1"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), scope-containment findings
    F4, F5. Ordinary Ralph Loop runs have no write-target enforcement, and the
    reviewer receives the full mutating toolset.

affected_scope:
  components:
    - name: "orchestrator (tool dispatch, phase tool exposure)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "mcp_client (tool exposure)"
      file_path: "ai/ael/src/mcp_client.py"
    - name: "AEL config (allowed dirs)"
      file_path: "ai/ael/config.yaml"
  version: "current"

reproduction:
  prerequisites: "AEL run with filesystem MCP allowed dirs spanning the GitHub/ClaudeProjects tree."
  steps:
    - "F4: worker calls write/edit/delete on a path outside the project root; the orchestrator dispatches without validation; only audit runs (_check_audit_scope) enforce any scope"
    - "F5: review phase receives mcp.get_openai_tools() (full toolset); reviewer calls write/edit/move/delete and mutates source"
  frequency: "always"
  reproducibility_conditions: "Any non-audit run; any review phase."
  error_output: "None; silent out-of-scope mutation."

behavior:
  expected: >
    Writes are constrained to the project root; the reviewer operates with a
    read-only tool subset and cannot mutate source.
  actual: >
    Any reachable file in the allowed-dirs tree can be modified or deleted on a
    non-audit run (F4); the reviewer can mutate source (F5).
  impact: "Silent cross-repository scope drift; worker/reviewer separation violated."
  workaround: "Manually narrow MCP allowed dirs per run."

analysis:
  root_cause: >
    The orchestrator dispatches any model-called tool with no write-target
    validation; scope enforcement exists only for audit runs keyed on
    audit-index.md (F4). Both phases receive the full tool schema (F5).
  technical_notes: >
    F4: narrow MCP allowed dirs to the project root in config.yaml; optionally
    validate each write path against the project root / task-derived allowlist
    and REVISE on out-of-scope writes. F5: pass a read-only tool subset
    (read/list/grep) to the review phase.

resolution:
  approach: >
    Read-only reviewer tool subset (F5, source change); project-root allowed-dirs
    in config.yaml (F4, configuration); optional write-path validation in the
    orchestrator (F4, source change).

verification:
  verification_steps:
    - "A worker write targeting a path outside the project root is rejected or REVISEd"
    - "The reviewer cannot call write/edit/move/delete (no mutating tools exposed)"
    - "Audit-run scope enforcement is unchanged"

notes: >
  Groups proposal-f9a2c41b findings F4 (high) and F5 (high). The F4 allowed-dirs
  narrowing is configuration; F4 path validation and F5 reviewer tool subset are
  source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Resolved: fix implemented and verified against source; issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
