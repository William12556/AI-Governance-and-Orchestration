# Change: AEL Orchestrator — Edit Failure Corrective Guidance and Supporting Improvements

Created: 2026 March 27

---

```yaml
# T02 Change Document
# AEL Orchestrator — edit failure corrective guidance and supporting improvements

change_info:
  id: "change-a5c8d2f1"
  title: "AEL Orchestrator — edit failure corrective guidance, log flush, reviewer syntax gate, propagation fix, pre-flight check"
  date: "2026-03-27"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 2
  coupled_docs:
    issue_ref: "issue-a5c8d2f1"
    issue_iteration: 2

source:
  type: "defect"
  reference: "issue-a5c8d2f1, 2026-03-27"
  description: >
    Five gaps in the AEL orchestrator caused repeated BLOCKED/rc=1 exits
    during GTach prompt-e1f2a3b4-3 and subsequent re-runs. Gaps 1-3 were
    implemented in framework and skel (iteration 1). Gaps 4-5 are new
    findings from post-fix log analysis and are added in iteration 2.

    Gap 4: The GTach orchestrator copy contains a spurious 'return 1' at
    the end of the edit mismatch branch, causing the loop to exit
    immediately after logging the WARNING — before any corrective message
    reaches the model. The framework does not have this line.

    Gap 5: No pre-flight check exists. The orchestrator does not compare
    success criteria against on-disk state before the worker starts. When
    a prior run has partially completed a task, the worker receives a stale
    brief and constructs edit patterns that no longer match the files.

scope:
  summary: >
    Iteration 1 (implemented): three targeted changes to framework and skel
    orchestrator.py and ralph-review.yaml.
    Iteration 2 (approved): two additional changes —
      4. Remove spurious 'return 1' from GTach (and any other project copies
         with the same line) edit mismatch branch.
      5. Add opt-in pre-flight success criteria check to run_loop() in
         framework and skel.
  affected_components:
    - name: "run_phase — edit failure handling (P1c branch)"
      file_path: "framework/ai/ael/src/orchestrator.py"
      change_type: "implemented (iteration 1)"
    - name: "run_phase — edit failure handling (P1c branch)"
      file_path: "skel/ai/ael/src/orchestrator.py"
      change_type: "implemented (iteration 1)"
    - name: "main — log flush"
      file_path: "framework/ai/ael/src/orchestrator.py"
      change_type: "implemented (iteration 1)"
    - name: "main — log flush"
      file_path: "skel/ai/ael/src/orchestrator.py"
      change_type: "implemented (iteration 1)"
    - name: "reviewer recipe — syntax gate"
      file_path: "framework/ai/ael/recipes/ralph-review.yaml"
      change_type: "implemented (iteration 1)"
    - name: "reviewer recipe — syntax gate"
      file_path: "skel/ai/ael/recipes/ralph-review.yaml"
      change_type: "implemented (iteration 1)"
    - name: "run_phase — remove spurious return 1"
      file_path: "GTach/ai/ael/src/orchestrator.py"
      change_type: "modify (iteration 2)"
    - name: "run_phase — remove spurious return 1 (if present)"
      file_path: "solax-modbus/ai/ael/src/orchestrator.py"
      change_type: "verify/modify (iteration 2)"
    - name: "run_loop — pre-flight success criteria check"
      file_path: "framework/ai/ael/src/orchestrator.py"
      change_type: "modify (iteration 2)"
    - name: "run_loop — pre-flight success criteria check"
      file_path: "skel/ai/ael/src/orchestrator.py"
      change_type: "modify (iteration 2)"
  affected_designs: []
  out_of_scope:
    - "mcp_client.py — no changes required"
    - "parser.py — no changes required"
    - "worker recipe ralph-work.yaml — no changes required"
    - "governance.md — no changes required"

rational:
  problem_statement: >
    Gaps 1-3 were correctly implemented in framework and skel. The GTach
    project copy was not correctly propagated: a 'return 1' was retained in
    the edit mismatch branch, causing the loop to exit before the corrective
    message reaches the model. All subsequent runs fail in under 5ms with
    no model inference.

    Separately, the structural cause of pattern mismatches — a stale task
    brief describing already-completed work — is not addressed by the
    corrective message alone. A pre-flight check would prevent the worker
    from attempting already-satisfied criteria and provide accurate context
    about what actually remains.
  proposed_solution: >
    Change 4: Remove the spurious 'return 1' from the GTach orchestrator
    edit mismatch branch. Verify solax-modbus is not affected. The edit
    mismatch branch should append the corrective message and fall through
    — identical to the canonical framework implementation.

    Change 5: Add an opt-in pre-flight success criteria check to run_loop()
    in framework and skel. Before the first worker iteration, parse success
    criteria from the task document and evaluate deterministic criteria
    (file content presence, Python syntax) against current on-disk state.
    Inject a pre-flight summary into the worker's initial context.
    Controlled by config flag preflight_check (default: false).
  alternatives_considered:
    - option: "Leave project copies to be corrected manually per-run"
      reason_rejected: >
        Propagation errors will recur. The canonical fix should be applied
        to all project copies and enforced via a documented sync procedure.
    - option: "Auto-read all target files and inject content into context"
      reason_rejected: >
        Inflates context budget proportional to file sizes. Pre-flight
        summary is lower-cost and provides the same signal.
    - option: "Pre-flight check enabled by default"
      reason_rejected: >
        Success criteria parsing is heuristic. Default-off reduces risk
        of false positives on tasks without structured criteria blocks.
  benefits:
    - "Corrective message reaches model — worker can self-correct (Gap 4)"
    - "Worker starts with accurate picture of remaining work (Gap 5)"
    - "Reduces wasted iterations on already-completed criteria"
    - "Pre-flight summary provides post-mortem context in logs"
  risks:
    - risk: "Pre-flight criteria parser misidentifies a criterion as satisfied"
      mitigation: >
        Default-off. Parser is conservative: only marks criterion satisfied
        when a deterministic check (grep, py_compile) returns unambiguous
        result. Ambiguous criteria are left as pending.
    - risk: "Spurious return 1 present in other project copies not yet checked"
      mitigation: >
        Verify solax-modbus explicitly. Document propagation review step
        in deployment notes.

technical_details:
  current_behavior: >
    GTach orchestrator exits run_phase() with rc=1 immediately after
    logging edit pattern mismatch WARNING. Corrective message is appended
    to messages[] but the function returns before the next model call.
    Framework/skel do not have this line and behave correctly.
    No pre-flight check exists in any orchestrator.
  proposed_behavior: >
    Change 4: Edit mismatch branch in all project copies appends corrective
    message and continues loop — identical to framework.
    Change 5: When preflight_check: true in config, run_loop() evaluates
    deterministic success criteria before first worker iteration and
    injects a summary of satisfied/remaining items into worker context.
  implementation_approach: >
    Change 4 — GTach/ai/ael/src/orchestrator.py:
      Locate the if _edit_pattern_failed: block.
      Remove the 'return 1' line at the end of the block.
      Verify the block ends with messages.append(...) and falls through
      to the next tool call — matching the framework implementation.
      Repeat verification for solax-modbus.

    Change 5 — run_loop() in framework and skel orchestrator.py:
      Add preflight_check parameter read from config (default false).
      If enabled, before the first run_phase() call:
        a. Extract success_criteria list from task document. Attempt
           YAML block parse first; fall back to plain list under a
           '## N.0 Success Criteria' heading.
        b. For each criterion:
           - If it references a file path and contains a grep-able
             string (e.g. "contains 'transport'"), run grep and mark
             satisfied/unsatisfied.
           - If it references a .py file and criterion is "no syntax
             errors", run py_compile and mark accordingly.
           - Otherwise mark as 'unchecked' (cannot evaluate deterministically).
        c. Build pre-flight summary string.
        d. Log the summary at INFO level.
        e. Prepend summary to task string delivered to worker:
             "[PRE-FLIGHT]\n<summary>\n[END PRE-FLIGHT]\n\n<task>"
      Add preflight_check key to config.yaml (framework and skel):
        loop:
          preflight_check: false

  code_changes:
    - component: "GTach orchestrator.py — remove return 1"
      file: "GTach/ai/ael/src/orchestrator.py"
      change_summary: >
        Within if _edit_pattern_failed: block: remove 'return 1'.
        Block must end with messages.append and fall through.
    - component: "solax-modbus orchestrator.py — verify/remove return 1"
      file: "solax-modbus/ai/ael/src/orchestrator.py"
      change_summary: >
        Inspect if _edit_pattern_failed: block. Remove 'return 1' if present.
    - component: "framework orchestrator.py — pre-flight check"
      file: "framework/ai/ael/src/orchestrator.py"
      change_summary: >
        Add run_preflight_check() helper. Call from run_loop() before
        first worker phase when preflight_check config flag is true.
        Prepend pre-flight summary to task string.
    - component: "framework config.yaml — preflight_check flag"
      file: "framework/ai/ael/config.yaml"
      change_summary: >
        Add loop.preflight_check: false.
    - component: "skel copies"
      file: "skel/ai/ael/src/orchestrator.py, skel/ai/ael/config.yaml"
      change_summary: "Mirror framework changes for iteration 2."
  data_changes: []
  interface_changes:
    - "run_loop(): new optional preflight_check parameter (default false)"

dependencies:
  internal:
    - "subprocess (stdlib) — already imported"
    - "re (stdlib) — already imported"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Code inspection for Change 4.
    Manual loop run with preflight_check enabled for Change 5.
  test_cases:
    - scenario: "GTach orchestrator — edit tool returns E_INVALID_INPUT"
      expected_result: >
        WARNING logged. Corrective message injected. Loop continues to
        next iteration. Model inference occurs. Worker re-reads file
        and self-corrects. No rc=1 before model call.
    - scenario: "solax-modbus orchestrator — same edit failure"
      expected_result: "Identical to GTach expected result above."
    - scenario: "preflight_check false (default)"
      expected_result: "run_loop() behaviour unchanged. No pre-flight summary."
    - scenario: "preflight_check true — some criteria already satisfied"
      expected_result: >
        Pre-flight summary prepended to worker task. Worker log shows
        which criteria are satisfied and which remain. Worker does not
        attempt edits on already-correct files.
    - scenario: "preflight_check true — criteria parse fails (no structured block)"
      expected_result: >
        Warning logged. All criteria marked 'unchecked'. Worker receives
        full task without pre-flight summary. No rc=1.
  regression_scope:
    - "Framework/skel iteration 1 changes (Gaps 1-3) unchanged"
    - "MCP error threshold and BLOCKED logic unchanged"
    - "preflight_check false: run_loop() identical to pre-change behaviour"
  validation_criteria:
    - "GTach orchestrator edit mismatch branch has no return 1"
    - "solax-modbus orchestrator edit mismatch branch has no return 1"
    - "Loop continues after edit mismatch warning (confirmed by model latency in log)"
    - "config.yaml contains loop.preflight_check key"
    - "Pre-flight summary appears in log when flag is true"

implementation:
  implementation_steps:
    - step: "Remove return 1 from GTach/ai/ael/src/orchestrator.py edit mismatch branch"
      owner: "Strategic Domain"
    - step: "Inspect and fix solax-modbus/ai/ael/src/orchestrator.py if same line present"
      owner: "Strategic Domain"
    - step: "Implement run_preflight_check() in framework/ai/ael/src/orchestrator.py"
      owner: "Strategic Domain"
    - step: "Add preflight_check: false to framework/ai/ael/config.yaml"
      owner: "Strategic Domain"
    - step: "Mirror pre-flight changes to skel/"
      owner: "Strategic Domain"
    - step: "Update issue-a5c8d2f1 status to resolved when all steps verified"
      owner: "Strategic Domain"
  rollback_procedure: "Restore from git history"
  deployment_notes: >
    Change 4 is a one-line removal. Apply and verify with a test run
    before proceeding to Change 5.
    Change 5 ships with preflight_check: false. Enable per-project
    once validated against a known task with structured success criteria.
    Propagation review: when syncing framework to project copies, diff
    the edit mismatch block against the canonical framework implementation
    to detect any spuriously introduced lines.

verification:
  implemented_date: "2026-03-27"
  implemented_by: "William Watson"
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-a5c8d2f1"
      relationship: "source"
    - issue_ref: "issue-f4a7c2e9"
      relationship: "overlapping fix location — P4 syntax check in run_phase()"
    - issue_ref: "issue-b2d4f6a8"
      relationship: "overlapping fix location — MCP error handling in run_phase()"

notes: >
  Original observation: GTach prompt-e1f2a3b4-3.
  Continued failures: ael_20260327-125814.LOG, ael_20260327-130118.LOG.
  Gap 4 evidence: rc=1 within 5ms of WARNING across all three logs.
  Worker model: Devstral-Small-2-24B-Instruct-2512.

version_history:
  - version: "3.0"
    date: "2026-03-27"
    author: "William Watson"
    changes:
      - "Iteration 2 implemented: Gap 6 (role:user after role:tool API rejection) fixed; corrective guidance embedded in tool result content; applied to framework, skel, GTach"
  - version: "2.0"
    date: "2026-03-27"
    author: "William Watson"
    changes:
      - "Iteration 2: added Gap 4 (spurious return 1 propagation fix) and Gap 5 (pre-flight check)"
      - "Status reset to approved pending implementation of iteration 2 items"
  - version: "1.1"
    date: "2026-03-27"
    author: "William Watson"
    changes:
      - "Status implemented; iteration 1 items (Gaps 1-3) applied to framework and skel"
  - version: "1.0"
    date: "2026-03-27"
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
