Created: 2026 November 5

```yaml
change_info:
  id: "change-a5bd4fe1"
  title: "Scope and gate hardening (audit-caab2052 group 5)"
  date: "2026-11-05"
  status: "approved"  # operator, 2026-11-05
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a5bd4fe1"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-a5bd4fe1"
  description: "Remediate audit-caab2052 L-01, L-02, L-12 and OQ-01, and add the collection-only pass decided on 2026-11-05, with the approaches decided on 2026-11-05."

scope:
  summary: >
    (A) L-01, fail closed: a tool is a write tool unless its name matches a
    read-only pattern and contains no write verb; the read-only patterns gain
    diff and count. (B) L-02: a write path that cannot be resolved is
    refused. (C) L-12: every py_compile check writes its bytecode to a
    temporary directory removed afterwards, and the syntax gate and the
    preflight criterion check compile only files inside the project root.
    (D) OQ-01: a syntax gate FAIL overrides SHIP. (E) Collection pass: when
    the pytest gate runs and the project has a tests/ directory, the gate
    also runs a collection-only pass over tests/; a collection error fails
    the gate.
  affected_components:
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }
    - { name: "gates", file_path: "ai/engine/src/gates.py", change_type: "modify" }
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "engine tests", file_path: "tests/engine/test_scope_gate_hardening.py", change_type: "add" }
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "engine requirements", file_path: "dev/requirements/requirements-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§6.0 Gates (syntax FAIL, collection pass, bytecode)", "§7.0 Write scope (tool classification, unresolvable paths)", "§11.0 Error Handling", "Version History"] }
  out_of_scope:
    - "Per-server tool lists in ai/config.yaml (rejected 2026-11-05)"
    - "Converting the syntax gate into a declared command gate (Phase 3, audit-caab2052 OQ-01)"
    - "Bytecode written by pytest when the pytest gate imports project code"
    - "A separate 'collect' command gate (rejected 2026-11-05)"
    - "issue-86c958dd and the audit-5e8aea4f findings"

rational:
  problem_statement: "See issue-a5bd4fe1."
  proposed_solution: "Classify tools fail-closed in scope.py; refuse unresolvable paths; one shared bounded compile check with a temporary cache; syntax FAIL in the SHIP override; a collection-only step inside the pytest gate."
  alternatives_considered:
    - option: "L-01: per-server read_only_tools and write_tools lists in ai/config.yaml, unlisted tools refused"
      reason_rejected: "Operator decision 2026-11-05: a config schema change in five projects for a gap no configured server opens"
    - option: "L-01: a longer verb list only"
      reason_rejected: "Operator decision 2026-11-05: names outside the list stay unchecked"
    - option: "L-12: compile() in the engine process"
      reason_rejected: "Operator decision 2026-11-05: loses the per-file time bound of audit-caab2052 L-03"
    - option: "Collection: a separate declared command gate 'collect'"
      reason_rejected: "Operator decision 2026-11-05: more configuration for one fixed check"
  benefits:
    - "The write scope holds for any MCP server, not only for tool names with a listed verb"
    - "No engine-written bytecode beside sources, and no compile of paths outside the project"
    - "A cycle with a syntax error cannot ship"
    - "A SHIP cannot leave tests/ unimportable"
  risks:
    - risk: "A read tool of another MCP server with an unmatched name is treated as a write tool: it is not offered to the reviewer, and in the worker phase its path arguments must lie in the write scope and are recorded as deliverables"
      mitigation: "The known read tools of the configured servers are covered (issue technical notes); the refusal names the tool, and a pattern can be added"
    - risk: "The collection pass fails on a tests/ problem the worker did not cause"
      mitigation: "Accepted: SHIP with an unimportable tests/ is the defect being closed; the gate output names the module"
    - risk: "Longer pytest gate"
      mitigation: "Collection only, no test execution; same timeout as the gate"

technical_details:
  current_behavior: "See issue-a5bd4fe1 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) scope.is_write_tool(name) is true unless the name matches a
    read-only pattern and contains no write verb; is_readonly_tool(name) is
    its negation. READONLY_TOOL_PATTERNS gains '^diff' and '^count'. Every
    use of the two functions (scope check, write tracking, reviewer tool
    filter, review-phase dispatch refusal) follows the new classification
    unchanged. The tools of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep
    keep their current class, except diff and count-matches, which become
    read-only by name. (B) In scope.check, a target whose resolution raises
    gives Violation(target, "unresolvable path", "write refused: path
    '<target>' cannot be resolved"). (C) One function in gates.py runs
    'python -m py_compile <path>' with the existing timeout and with
    PYTHONPYCACHEPREFIX set to a temporary directory that is removed after
    the call; the syntax gate, the edit-failure check, the post-write check
    and the preflight criterion check use it. The syntax gate takes the
    project root and skips, with a log warning, a .py path that does not
    resolve inside it; the preflight criterion check does the same. (D) In
    run_loop's SHIP override, a syntax block with status FAIL overrides SHIP
    with the feedback "Syntax gate failed." followed by the block, before the
    command gates are evaluated. (E) When _run_pytest_gate runs (at least one
    target) and <project_root>/tests is a directory, the gate also runs
    '<gate python> -m pytest --collect-only -q <project_root>/tests' with
    the gate's cwd, timeout and scrub_env. Exit 0 or 5 (no tests collected)
    passes; any other exit fails; a step that cannot run is UNCHECKED. The
    gate status is the worst of the two steps (UNCHECKED, then FAIL, then
    PASS), and the TEST GATE block shows both outputs.
  implementation_approach: "Claude Code cloud session per a T04 prompt after approval; planner updates design, requirements and guide after review."
  code_changes:
    - component: "scope"
      file: "ai/engine/src/scope.py"
      change_summary: "A: is_write_tool, is_readonly_tool, READONLY_TOOL_PATTERNS, module docstring. B: check()"
      functions_affected: ["is_write_tool", "is_readonly_tool", "check"]
    - component: "gates"
      file: "ai/engine/src/gates.py"
      change_summary: "C: shared bounded compile function with a temporary bytecode cache; syntax_check takes the project root. E: collection-only step in the pytest gate"
      functions_affected: ["syntax_check", "run_command_gate or a pytest-specific helper", "new compile function"]
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "C: the three py_compile call sites use the shared function; D: syntax FAIL in the SHIP override; E: _run_pytest_gate passes the collection step"
      functions_affected: ["run_phase (edit-failure and post-write checks)", "preflight criterion check", "_run_syntax_gate", "_run_pytest_gate", "run_loop (SHIP override)"]
  interface_changes:
    - interface: "Tool classification"
      change_type: "contract"
      details: "Unrecognised tool names are write tools (fail closed); diff and count are read-only prefixes"
      backward_compatible: "yes for the configured servers"
    - interface: "[TEST GATE] block"
      change_type: "contract"
      details: "Adds the collection step's command and output; status rule as in proposed_behavior (E)"
      backward_compatible: "yes"
    - interface: "SHIP override"
      change_type: "contract"
      details: "A syntax FAIL now overrides SHIP (FR-03-04 v1.8)"
      backward_compatible: "no: a cycle that shipped with a syntax FAIL now returns REVISE"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library only (tempfile, os, subprocess)" }

testing_requirements:
  test_approach: "pytest, no network, no model (NFR-06), as tests/engine/test_loop_robustness.py and test_run_record.py do."
  test_cases:
    - { scenario: "S1: classification table for every tool of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep", expected: "same class as at c5d582d, except diff and count-matches read-only" }
    - { scenario: "S2: unknown tool names (copy_file, append_file, touch, frobnicate) with a path outside the project root, and without a path", expected: "is_write_tool true; scope violation; 'no recognised path argument' refusal" }
    - { scenario: "S3: reviewer tool filter with an unknown tool name", expected: "not offered" }
    - { scenario: "S4: write_file with a path containing NUL", expected: "Violation reason 'unresolvable path'" }
    - { scenario: "C1: syntax_check on a .py file in a project directory", expected: "PASS; no __pycache__ beside the file; no temporary directory left" }
    - { scenario: "C2: syntax_check with a .py path outside the project root named in work-summary.txt", expected: "not compiled; warning logged; no block entry for it" }
    - { scenario: "C3: post-write and edit-failure checks on a worker-written .py file", expected: "syntax error reported as before; no __pycache__ beside the file" }
    - { scenario: "C4: compile timeout", expected: "behaviour as at c5d582d (FAIL in the gate, skipped in the post-write check)" }
    - { scenario: "D1: run_loop with syntax FAIL and reviewer SHIP", expected: "no .complete; review-feedback.txt starts with 'Syntax gate failed.' and holds the syntax block" }
    - { scenario: "D2: syntax PASS or SKIPPED with reviewer SHIP and passing command gates", expected: "SHIP as before" }
    - { scenario: "E1: pytest gate with a passing target and a tests/ module that raises on import", expected: "[TEST GATE: FAIL]; block shows the collection output" }
    - { scenario: "E2: tests/ with no collectable tests (exit 5)", expected: "collection step passes" }
    - { scenario: "E3: collection step times out", expected: "[TEST GATE: UNCHECKED]" }
    - { scenario: "E4: no tests/ directory, or no pytest target", expected: "no collection step; behaviour as at c5d582d" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline"
    - "Live: one dev/smoke loop with task-scoped.md ends in SHIP with the collection step shown in the TEST GATE block and no __pycache__ written by the syntax gate beside src/split.py"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "3-5 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-a5bd4fe1)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §6.0, §7.0, §11.0; requirements-14e05e35 FR-03-04 (collection pass); guide-engine-operations gates and scope", owner: "planner" }
    - { step: "Live check in dev/smoke", owner: "operator" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh after verification; no configuration change."

traceability:
  related_changes:
    - { change_ref: "change-82dbf16a", relationship: "builds on (write scope, signal files, dispatch refusal)" }
    - { change_ref: "change-e58fd295", relationship: "modifies (gates)" }
    - { change_ref: "change-711a57d5", relationship: "keeps (bounded subprocesses, L-03)" }
  related_issues:
    - { issue_ref: "issue-a5bd4fe1", relationship: "source" }

notes: "Operator decisions of 2026-11-05: OQ-01 (audit-caab2052 §14.0); collection-only pass (dev/task.md group 5 row); approaches for L-01, L-12 and the collection pass."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-05"
    changes: ["Approved by the operator as drafted; implementation per prompt-a5bd4fe1"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
