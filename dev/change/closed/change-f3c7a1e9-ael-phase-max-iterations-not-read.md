Created: 2026 March 24

```yaml
# T02 Change Document
# AEL Orchestrator — phase_max_iterations not read

change_info:
  id: "change-f3c7a1e9"
  title: "AEL Orchestrator — wire phase_max_iterations to run_phase() in all projects"
  date: "2026-03-24"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f3c7a1e9"
    issue_iteration: 1

source:
  type: "defect"
  reference: "issue-f3c7a1e9, 2026-03-24"
  description: >
    orchestrator.py passed max_iterations (the outer Ralph Loop cycle limit)
    to run_phase() as its inner tool-call iteration limit. config.yaml
    phase_max_iterations was read but never forwarded to run_phase().
    The two limits were therefore identical, making independent control
    impossible. Non-trivial tasks requiring more tool calls than
    max_iterations permitted caused WORK PHASE FAILED.

scope:
  summary: >
    In each affected orchestrator.py: read phase_max_iterations from
    config.yaml in main_async(); pass it to run_phase() in all call sites
    (worker, reviewer, and loop modes). Where run_loop() does not yet
    accept phase_max_iterations as a parameter, add it and thread it
    through to both internal run_phase() calls.
  affected_components:
    - name: "framework orchestrator.py"
      file_path: "framework/ai/ael/src/orchestrator.py"
      change_type: "verify — already correct"
    - name: "skel orchestrator.py"
      file_path: "skel/ai/ael/src/orchestrator.py"
      change_type: "verify — already correct"
    - name: "GTach orchestrator.py"
      file_path: "GTach/ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "solax-modbus orchestrator.py"
      file_path: "solax-modbus/ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "config.yaml structure — no changes required"
    - "governance.md — no changes required"
    - "run_phase() internals — signature unchanged"
    - "Any other source files"

rational:
  problem_statement: >
    With loop.max_iterations set to a governance-appropriate outer cycle
    value (3-5), any non-trivial task fails immediately in the work phase
    because the inner phase tool-call budget is exhausted. The only
    workaround is to inflate max_iterations to ~20, which also inflates
    the outer loop limit unnecessarily.
  proposed_solution: >
    Read phase_max_iterations separately in main_async() and pass it to
    run_phase() at every call site. run_loop() already receives both values
    in framework/ and skel/ and forwards phase_max_iterations to run_phase()
    internally. GTach and solax-modbus require surgical corrections.
  alternatives_considered:
    - option: "Single unified iteration limit"
      reason_rejected: >
        Forces a trade-off: low value causes phase failure; high value
        allows runaway outer loops. Independent control is the correct design.
  benefits:
    - "loop.max_iterations governs outer Ralph Loop cycle count as intended"
    - "loop.phase_max_iterations governs inner tool-call budget as intended"
    - "All projects consistent with framework canonical implementation"
  risks:
    - risk: "Incorrect phase_max_iterations value in config.yaml causes phase failure"
      mitigation: >
        Fallback default in code: config["loop"].get("phase_max_iterations", max_iter).
        If key absent, behaviour is unchanged from pre-fix state.

technical_details:
  current_behavior: >
    GTach: loop mode correct; worker and reviewer single-phase modes pass
    max_iter to run_phase() instead of phase_max_iter.
    solax-modbus: phase_max_iter not read in main_async(); run_loop() does
    not accept phase_max_iterations parameter; all modes pass max_iter to
    run_phase().
  proposed_behavior: >
    All modes in all projects pass phase_max_iter to run_phase(). Outer
    loop cycle limit and inner phase tool-call budget are independently
    configurable.
  implementation_approach: >
    GTach: two-line change in main_async() — replace max_iter with
    phase_max_iter in worker and reviewer mode run_phase() calls.
    solax-modbus: (1) add phase_max_iter read in main_async();
    (2) add phase_max_iterations parameter to run_loop();
    (3) replace max_iterations with phase_max_iterations in both
    run_phase() calls inside run_loop();
    (4) replace max_iter with phase_max_iter in worker and reviewer
    mode run_phase() calls in main_async();
    (5) pass phase_max_iter to run_loop() call in main_async().
  code_changes:
    - component: "GTach orchestrator.py"
      file: "GTach/ai/ael/src/orchestrator.py"
      change_summary: >
        main_async(): worker and reviewer mode run_phase() calls:
        max_iter -> phase_max_iter (2 lines)
    - component: "solax-modbus orchestrator.py"
      file: "solax-modbus/ai/ael/src/orchestrator.py"
      change_summary: >
        main_async(): add phase_max_iter read;
        run_loop() signature: add phase_max_iterations parameter;
        run_loop() body: pass phase_max_iterations to both run_phase() calls;
        main_async(): all run_phase() and run_loop() call sites updated.
  data_changes: []
  interface_changes:
    - "solax-modbus run_loop(): new parameter phase_max_iterations added"

dependencies:
  internal:
    - "config.yaml loop.phase_max_iterations must be present in each project"
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Code inspection — verify correct parameter threading at all call sites"
  test_cases:
    - scenario: "loop.max_iterations=3, loop.phase_max_iterations=20, task requires 10 tool calls"
      expected_result: "Task completes within one outer loop iteration"
    - scenario: "phase_max_iterations absent from config.yaml"
      expected_result: "Falls back to max_iter; behaviour unchanged from pre-fix state"
  regression_scope:
    - "run_phase() internals unchanged"
    - "run_loop() outer cycle logic unchanged"
    - "All other orchestrator functionality unchanged"
  validation_criteria:
    - "phase_max_iter read from config in main_async() of all affected files"
    - "All run_phase() call sites receive phase_max_iter"
    - "run_loop() in solax-modbus accepts and forwards phase_max_iterations"

implementation:
  implementation_steps:
    - step: "Fix GTach/ai/ael/src/orchestrator.py — 2 lines in main_async()"
      owner: "Strategic Domain"
    - step: "Fix solax-modbus/ai/ael/src/orchestrator.py — run_loop() and main_async()"
      owner: "Strategic Domain"
    - step: "Update issue-f3c7a1e9 status to resolved"
      owner: "Strategic Domain"
  rollback_procedure: "Restore from git history"
  deployment_notes: ""

verification:
  implemented_date: "2026-03-24"
  implemented_by: "William Watson"
  verification_date: "2026-03-24"
  verified_by: "William Watson"
  test_results: "Code inspection confirmed correct phase_max_iter threading at all call sites in GTach and solax-modbus."
  issues_found: []

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-f3c7a1e9"
      relationship: "source"

notes: ""

version_history:
  - version: "1.1"
    date: "2026-03-24"
    author: "William Watson"
    changes:
      - "Status set to implemented; verification fields completed"
  - version: "1.0"
    date: "2026-03-24"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised implemented -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
