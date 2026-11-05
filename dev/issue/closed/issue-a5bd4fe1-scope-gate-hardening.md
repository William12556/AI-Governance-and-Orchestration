Created: 2026 November 5

```yaml
issue_info:
  id: "issue-a5bd4fe1"
  title: "Scope and gate hardening: unclassified tools unchecked, unresolvable paths allowed, py_compile writes beside sources, syntax FAIL does not block SHIP, import-breaking helper files pass the pytest gate"
  date: "2026-11-05"
  status: "closed"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-a5bd4fe1"
    change_iteration: 1

source:
  origin: "code_review"  # strategic audit audit-caab2052, group 5
  description: >
    Remediation group 5 of dev/audit/audit-caab2052-static-code-2026-10-27.md
    (§10.0, §14.0): L-01, L-02 and L-12; the OQ-01 decision (a syntax FAIL
    blocks SHIP; requirements-14e05e35 FR-03-04 v1.8); and the operator
    decision of 2026-11-05 to add a collection-only pass over tests/ to the
    pytest gate (GTach work item 72f95f73, run 1e00fd66). Approach decisions
    of 2026-11-05: L-01 fail closed; L-12 temporary bytecode cache and project
    paths only; collection pass inside the pytest gate. Findings re-checked by
    the planner against c5d582d.

affected_scope:
  components:
    - { name: "scope", file_path: "ai/engine/src/scope.py" }
    - { name: "gates", file_path: "ai/engine/src/gates.py" }
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
  designs:
    - { design_ref: "design-14e05e35 §6.0 (Gates), §7.0 (Write scope), §11.0 (Error Handling)" }
    - { design_ref: "requirements-14e05e35 FR-03-02, FR-03-04, FR-05-01" }
  version: "governance 12.8; engine at c5d582d"

reproduction:
  prerequisites: "Engine at c5d582d"
  steps:
    - "L-01: offer the worker an MCP tool whose name has no listed write verb (for example copy_file or append_file) and call it with a path outside the project root"
    - "L-02: call write_file with a path that contains a NUL character"
    - "L-12: run a loop whose work-summary.txt names a .py file; list __pycache__/ beside that file; repeat with a .py path outside the project"
    - "OQ-01: a cycle in which the syntax gate reports FAIL and the reviewer answers SHIP"
    - "Collection: the worker writes tests/__init__.py or a tests/ module that fails on import, beside a passing target"
  frequency: "always, under the stated condition"
  error_output: "L-01, L-02: no scope violation. OQ-01: SHIPPED with [SYNTAX GATE: FAIL]. Collection (GTach 72f95f73): pytest gate PASS; full suite passed only after three worker helper files were removed from tests/"

behavior:
  expected: >
    L-01: a tool that is not recognised as read-only is checked as a write
    tool. L-02: a write path that cannot be resolved is refused. L-12: syntax
    checks write no bytecode beside the checked files and compile only files
    inside the project. OQ-01: a syntax FAIL overrides SHIP as a command gate
    FAIL does. Collection: a tests/ module that cannot be imported fails the
    pytest gate.
  actual: >
    L-01: scope.check returns before any path test when is_write_tool is
    false, and is_write_tool matches ten verbs; the docstring's
    "fail-closed" holds only for names that contain one of them. L-02:
    scope.check continues past a path whose resolution raises. L-12: four
    sites run 'python -m py_compile', which writes __pycache__/*.pyc beside
    the source; the syntax gate compiles every existing .py path named in
    work-summary.txt, including paths outside the project, and that file is
    worker-written. OQ-01: the SHIP override loop checks command gates only.
    Collection: the pytest gate runs only the targets derived from the
    deliverables, so a tests/ file that breaks the import of other test
    modules is not seen.
  impact: "With another MCP server or version, a write tool could bypass the write scope; a malformed path passes the scope check; the engine writes bytecode outside the write scope and, through work-summary.txt, outside the project; a cycle with a syntax error can ship; a SHIP can leave the project's full test suite broken."
  workaround: "Use the pinned filesystem MCP server; run the full suite before accepting a SHIP."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    Line numbers at c5d582d. L-01: scope.py:38-60 (verb and read-only
    patterns, is_write_tool, is_readonly_tool), :201 (early return in
    check). L-02: scope.py:210-213. L-12: gates.py:43-95 (syntax_check:
    paths from work-summary.txt, existence test only, py_compile at :69);
    orchestrator.py:1535 (edit-failure check), :1610 (post-write check),
    :1740 (preflight criterion check). OQ-01: orchestrator.py:2363-2386
    iterate _command_results only; the syntax block is not in that list
    (:2184-2186). Collection: _run_pytest_gate (orchestrator.py:1810-1839)
    passes only gates.pytest_targets(deliverables) to the command.
  technical_notes: >
    Tools of the configured servers (filesystem-mcp 2.5.0: create, delete,
    diff, edit, find_files, list, list_roots, move, patch, read,
    replace_text, search_text, stat; mcp-ripgrep: search, count-matches,
    list-files, list-file-types; mcp-grep: grep). Under a fail-closed rule,
    diff and count-matches are read tools that match no read-only pattern
    today. is_readonly_tool also decides which tools the reviewer is offered
    (mcp_client.py:79-93). Bytecode written by pytest itself when the gate
    imports project code is not part of L-12. GTach 72f95f73: the helper
    files were tests/__init__.py, tests/run_test_sim.py and
    tests/test_changes.py (change-72f95f73 test_results).

resolution:
  approach: "See change-a5bd4fe1."
  change_ref: "change-a5bd4fe1"

traceability:
  design_refs: ["design-14e05e35", "requirements-14e05e35"]
  change_refs: ["change-a5bd4fe1"]

notes: "Audit references: audit-caab2052 L-01, L-02, L-12, OQ-01 (§14.0); operator decisions 2026-11-05."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-caab2052 remediation group 5"]
  - version: "1.1"
    date: "2026-11-05"
    changes: ["Status resolved: change-a5bd4fe1 implemented (0fabfa6) (P03.7)"]
  - version: "1.2"
    date: "2026-11-05"
    changes: ["Verified: macOS suite 446 passed, follow-up audit-a5bd4fe1 and the live check in dev/smoke; change-a5bd4fe1 verified on operator approval"]
  - version: "1.3"
    date: "2026-11-05"
    changes: ["Closed on operator acceptance (P00.14.4); moved to dev/issue/closed/. Residual findings of audit-a5bd4fe1 continue in issue-b8c75bac"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
