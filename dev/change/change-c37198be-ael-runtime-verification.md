Created: 2026 September 24

```yaml
change_info:
  id: "change-c37198be"
  title: "AEL: pin mcp<2; refuse a missing --task file; filesystem-mcp 2.x write tools; tests for backlog §5.0 item 5 cases"
  date: "2026-09-24"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c37198be"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-c37198be"
  description: "Defects D1 and D2 from the 2026-09-24 live runs; test coverage T for backlog §5.0 item 5."

scope:
  summary: "ai/ael/requirements.txt; ai/ael/src/orchestrator.py (task resolution, recipe selection helper); new tests/ael/."
  affected_components:
    - name: "requirements"
      file_path: "ai/ael/requirements.txt"
      change_type: "modify"
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "MCP client"
      file_path: "ai/ael/src/mcp_client.py"
      change_type: "modify"
    - name: "AEL configuration and docs"
      file_path: "ai/ael/config.yaml, ai/ael/README.md, ai/doc/guide-ael-operations.md, dev/smoke/config.reference.yaml"
      change_type: "modify"
    - name: "AEL unit tests"
      file_path: "tests/ael/"
      change_type: "add"
  affected_designs: []
  out_of_scope:
    - "Porting mcp_client.py to mcp 2.x"
    - "Any change to loop, gate or verdict behaviour"
    - "ael-mcp (backlog §8.0 item 2)"

rational:
  problem_statement: "See issue-c37198be."
  proposed_solution: >
    D1: constrain mcp to >=1.0.0,<2 in requirements.txt. D2: in main_async,
    after reset mode and before any state change, refuse (exit 1) a --task
    value that looks like a file path (no whitespace; ends in .md, .yaml,
    .yml or .txt, or contains a path separator) when no such file exists.
    Free-text tasks are unchanged. D3: add create, patch, replace_text and
    search_and_replace to _WRITE_TOOLS; read paths from nested files/paths/
    moves/edits entries (_scope_targets for F4, _written_targets for the
    manifest and the post-write syntax check, destinations for moves); extend
    F21 to create files[]; count read paths[] as reviewer read evidence;
    mcp_client never classes a name containing a write verb as read-only; pin
    @j0hanz/filesystem-mcp to 2.5.0 in the framework config, docs and smoke
    reference config. T: add tests/ael/ covering the nine §5.0
    item 5 cases with stub model and MCP clients; extract the inline recipe
    choice into _select_recipe_set(state_dir) so it can be tested.
  alternatives_considered:
    - option: "Adapt mcp_client.py to read either inputSchema or input_schema"
      reason_rejected: "mcp 2.x changes are not otherwise assessed; a version bound is the smaller, verifiable fix"
  benefits:
    - "Fresh installations load tools"
    - "A mistyped task path cannot start an unscoped run"
    - "Nine previously unexercised behaviours become repeatable tests"
    - "Writes through filesystem-mcp 2.x tools are scope-checked and reach the SHIP gates"
  risks:
    - risk: "A free-text task that happens to end in .md is refused"
      mitigation: "Only single-token values are treated as paths; any whitespace makes it text"

technical_details:
  current_behavior: "See issue-c37198be behavior.actual."
  proposed_behavior: "As proposed_solution."
  implementation_approach: >
    Tests import orchestrator.py directly, replace run_phase and the gates where
    a loop-level behaviour is under test, and drive run_phase with a scripted
    fake completion client and fake MCP client where a phase-level behaviour is
    under test. No network, oMLX or MCP server is required.
  code_changes:
    - component: "requirements"
      file: "ai/ael/requirements.txt"
      change_summary: "mcp>=1.0.0,<2"
      functions_affected: []
      classes_affected: []
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "_looks_like_task_path, _select_recipe_set, _path_values, _scope_targets, _written_targets (new); main_async task check; _WRITE_TOOLS; _validate_write_scope; _validate_audit_report_write; run_phase read tracking, write recording, post-write syntax check"
      functions_affected:
        - "main_async"
        - "_validate_write_scope"
        - "_validate_audit_report_write"
        - "run_phase"
    - component: "MCP client"
      file: "ai/ael/src/mcp_client.py"
      change_summary: "_WRITE_NAME_PATTERNS; _is_readonly_tool excludes write verbs"
      functions_affected:
        - "MCPClient._is_readonly_tool"
      classes_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - "orchestrator.py exits 1 with an error when --task names a missing file"

dependencies:
  internal: []
  external:
    - "mcp>=1.0.0,<2"
  required_changes: []

testing_requirements:
  test_approach: "pytest tests/ael/ on the operator's Mac (~/.venvs/ael); live evidence from dev/smoke runs A and B."
  test_cases:
    - scenario: "T1 worker writes work-summary.txt itself, then exhausts its iteration budget"
      expected_result: "Worker's summary kept unchanged; phase rc=0"
    - scenario: "T2 move_file as the only write"
      expected_result: "Synthesized manifest records the destination, not the source"
    - scenario: "T3 log_archive_dir unset"
      expected_result: "archive_prior_logs returns 0 and creates nothing"
    - scenario: "T4 _normalize_verdict pass 1"
      expected_result: "Last isolated verdict line wins, including decorated forms"
    - scenario: "T5 RALPH-BLOCKED.md after the work phase"
      expected_result: "run_loop returns 1 without a review phase"
    - scenario: "T6 audit-index.md present / absent"
      expected_result: "Recipe set 'audit' / 'ralph'; all four recipe files load"
    - scenario: "T7 failing test target"
      expected_result: "_run_pytest_gate returns [TEST GATE: FAIL]"
    - scenario: "T8 reviewer SHIP with pytest gate FAIL"
      expected_result: "SHIP overridden; feedback holds the gate output; no .ralph-complete"
    - scenario: "T9 identical REVISE feedback on consecutive cycles"
      expected_result: "Stall BLOCK written; run_loop returns 1"
    - scenario: "D1 requirements.txt"
      expected_result: "mcp bounded below 2"
    - scenario: "D2 --task names a missing file / free text / existing file"
      expected_result: "Refused / accepted / accepted"
    - scenario: "D3 create files[], delete paths[], move moves[], edit files[] outside project root"
      expected_result: "Scope violation"
    - scenario: "D3 create as the only write; move moves[]; reviewer read paths[]; create over audit-report.md; tool-name classes"
      expected_result: "Manifest records created file; destination recorded; both reads counted; blocked; write verbs never read-only"
    - scenario: "Live: dev/smoke Run A2 (clean) and Run B (defective fixture) after D3"
      expected_result: "Pytest gate runs on src/split.py; SHIP only with [TEST GATE: PASS]"
  regression_scope:
    - "Free-text --task and existing task files behave as before"
    - "Recipe choice unchanged"
  validation_criteria:
    - "pytest tests/ael/ passes; py_compile passes"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly; abbreviated workflow at operator instruction 2026-09-24 (issue/change, then implementation; review after all changes)"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "Propagate to downstream projects after verification."

verification:
  implemented_date: "2026-09-24"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-24"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session; independent review pending"
  test_results: >
    pytest tests/ael/ on the operator's Mac (~/.venvs/ael, Python 3.11.14,
    mcp 1.30.0): 43 passed. Live dev/smoke runs: Run A2 (ael_20260924-141914)
    pytest gate PASS on tests/test_split.py, SHIP at iteration 3 (D1-D3
    confirmed live). Run B2 (ael_20260924-154002) pytest gate FAIL fed to the
    reviewer; no convergence (worker model), stall BLOCK. Live also: BLOCKED
    exit on MCP error threshold (071040), stall BLOCK (072824, 144119, 154002).
    filesystem-mcp 2.5.0 moves[] keys confirmed as source/destination.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-a2f9c4d1"
      relationship: "tests"
    - change_ref: "change-f5c28a04"
      relationship: "tests"
    - change_ref: "change-d1f4a83b"
      relationship: "tests"
  related_issues:
    - issue_ref: "issue-c37198be"
      relationship: "resolves"

notes: >
  Abbreviated workflow at William Watson's instruction (2026-09-24): no T03
  prompt; implementation follows directly; review after all changes.

version_history:
  - version: "1.0"
    date: "2026-09-24"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-09-24"
    author: "William Watson"
    changes:
      - "D3 (filesystem-mcp 2.x write tools) added to scope"
  - version: "1.2"
    date: "2026-09-24"
    author: "William Watson"
    changes:
      - "Implemented; test and live-run results recorded"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
