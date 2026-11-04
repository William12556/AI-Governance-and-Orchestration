# Issue: AEL Orchestrator — Edit Pattern Mismatch Yields No Corrective Guidance

Created: 2026 March 27

---

## Table of Contents

- [1.0 Issue Information](#10-issue-information)
- [2.0 Source](#20-source)
- [3.0 Affected Scope](#30-affected-scope)
- [4.0 Reproduction](#40-reproduction)
- [5.0 Behavior](#50-behavior)
- [6.0 Environment](#60-environment)
- [7.0 Analysis](#70-analysis)
- [8.0 Resolution](#80-resolution)
- [Version History](#version-history)

---

## 1.0 Issue Information

```yaml
issue_info:
  id: "issue-a5c8d2f1"
  title: "AEL Orchestrator — edit pattern mismatch yields no corrective guidance; loop exits rc=1"
  date: "2026-03-27"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 3
  coupled_docs:
    change_ref: "change-a5c8d2f1"
    change_iteration: 2
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "user_report"
  test_ref: ""
  description: >
    During GTach prompt-e1f2a3b4-3 execution the worker attempted to edit
    watchdog.py using a pattern derived from the task brief. A prior partial
    run had already applied a different version of the edit, leaving the
    file in a mutated state the worker was unaware of. The edit tool
    returned E_INVALID_INPUT (pattern not found). The orchestrator classified
    this as an MCP error and injected a generic retry message. The worker
    retried the same failing edit. After three consecutive failures the loop
    wrote RALPH-BLOCKED.md and exited rc=1.

    Subsequent runs (ael_20260327-125814.LOG, ael_20260327-130118.LOG)
    continued to fail after framework fixes were partially propagated to
    the GTach copy. The edit mismatch branch in the GTach orchestrator
    contains a spurious 'return 1' that exits run_phase() immediately after
    logging the WARNING — before any corrective message is delivered to the
    model. The framework orchestrator does not have this line.

    Five contributing gaps have been identified:
      1. Edit failure message generic — does not instruct worker to re-read
         file before retrying. (Framework fix implemented.)
      2. Log handlers not flushed before os._exit(rc). (Framework fix implemented.)
      3. Reviewer recipe has no syntax gate. (Framework fix implemented.)
      4. GTach orchestrator copy contains spurious 'return 1' in edit mismatch
         branch — corrective message never delivered; loop exits immediately.
      5. No pre-flight check — orchestrator does not verify success criteria
         before the worker starts, allowing the worker to attempt work already
         completed by a prior run.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "run_phase — edit failure handling"
      file_path: "framework/ai/ael/src/orchestrator.py"
      note: "Framework correct. Gaps 1-3 implemented."
    - name: "run_phase — edit failure handling"
      file_path: "skel/ai/ael/src/orchestrator.py"
      note: "Skel correct. Gaps 1-3 implemented."
    - name: "run_phase — spurious return 1"
      file_path: "GTach/ai/ael/src/orchestrator.py"
      note: "Gap 4 — return 1 must be removed from edit mismatch branch."
    - name: "main — log flush"
      file_path: "framework/ai/ael/src/orchestrator.py"
    - name: "main — log flush"
      file_path: "skel/ai/ael/src/orchestrator.py"
    - name: "reviewer recipe — syntax gate"
      file_path: "framework/ai/ael/recipes/ralph-review.yaml"
    - name: "reviewer recipe — syntax gate"
      file_path: "skel/ai/ael/recipes/ralph-review.yaml"
    - name: "run_loop — pre-flight check"
      file_path: "framework/ai/ael/src/orchestrator.py"
      note: "Gap 5 — new enhancement."
    - name: "run_loop — pre-flight check"
      file_path: "skel/ai/ael/src/orchestrator.py"
      note: "Gap 5 — new enhancement."
  designs:
    - design_ref: ""
  version: "AEL orchestrator as of 2026-03-27"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Reproduction

```yaml
reproduction:
  prerequisites: >
    Worker model configured. MCP filesystem server connected.
    Target .py file partially modified by a prior run — worker's task
    brief describes original file state, not current on-disk state.
  steps:
    - "Issue a Ralph Loop task requiring an edit to a .py file"
    - "Ensure the file has been partially mutated by a prior run"
    - "Worker constructs edit pattern from task brief (stale)"
    - "Edit tool returns E_INVALID_INPUT: pattern not found"
    - "GTach orchestrator logs WARNING and returns rc=1 immediately"
    - "Loop exits — corrective message never delivered to model"
  frequency: "consistent — every run against partially-mutated files"
  reproducibility_conditions: >
    Occurs when a prior partial run has left a file in an intermediate
    state. Confirmed across runs ael_20260327-120831.LOG,
    ael_20260327-125814.LOG, ael_20260327-130118.LOG. All three show
    the same sequence: WARNING logged, next iteration budget-ok logged,
    then rc=1 within 5ms — well below model inference latency.
  error_output: >
    WARNING  edit pattern mismatch tool=edit path=<file>
    DEBUG    iteration N/50 phase=WORKER
    DEBUG    context budget ok: X / 393216 tokens (Y%)
    INFO     AEL end rc=1
    (5ms elapsed — no model call made)
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Behavior

```yaml
behavior:
  expected: >
    When an edit tool call fails with a pattern-not-found error, the
    orchestrator injects a corrective message instructing the worker to
    read the file first. The loop continues; the worker re-reads and
    self-corrects. The loop does not exit until mcp_error_threshold is
    reached or the worker completes its task.

    Additionally:
    - Log handlers flushed before os._exit(rc).
    - Reviewer verifies Python syntax before issuing SHIP.
    - Before the worker starts, the orchestrator checks which success
      criteria are already met and informs the worker, preventing
      redundant work on already-completed items.
  actual: >
    GTach orchestrator returns rc=1 immediately after logging the edit
    mismatch WARNING. No corrective message is injected. No model
    inference occurs. The loop exits in under 5ms with no useful work
    performed. This repeats on every re-run while the stale brief and
    mutated file remain divergent.
  impact: >
    Every run against a partially-mutated file fails immediately. The
    human operator must manually correct the divergent file before
    re-running. The framework fix (corrective message + continue) is
    never reached because the project copy exits first.
  workaround: >
    Manually correct the divergent file to match the current expected
    state. For the immediate GTach case: fix watchdog.py syntax error
    (add missing '}' on line 91) and re-run.
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Environment

```yaml
environment:
  python_version: "3.x"
  os: "macOS"
  dependencies:
    - library: "openai"
      version: ""
    - library: "mcp"
      version: ""
  domain: "framework/ai/ael"
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Analysis

```yaml
analysis:
  root_cause: >
    Five gaps converge. Gaps 1-3 are fixed in framework and skel.
    Gaps 4-5 are new findings from post-fix log analysis.

    GAP 1 — Edit failure message (primary, framework fixed):
      E_INVALID_INPUT detected by _is_mcp_error(). Generic retry message
      does not instruct worker to re-read file. Fixed in framework by
      adding P1c branch with targeted read instruction before P1a.

    GAP 2 — Log flush before os._exit (secondary, framework fixed):
      os._exit() does not flush FileHandler buffers. Terminal log records
      silently dropped. Fixed in framework by flushing ael logger handlers
      before os._exit(rc).

    GAP 3 — Reviewer recipe syntax gate (secondary, framework fixed):
      Reviewer recipe has no py_compile instruction. Fixed in framework
      by adding syntax verification requirement to reviewer checklist.

    GAP 4 — Spurious return 1 in GTach orchestrator (blocking, unfixed):
      The GTach copy of orchestrator.py has 'return 1' at the end of the
      if _edit_pattern_failed: block. This exits run_phase() immediately
      after the WARNING is logged — before the corrective message appended
      to messages[] is delivered to the model. The framework orchestrator
      does not have this line; it was introduced during imprecise propagation.
      Evidence: all three failing logs show rc=1 within 5ms of the WARNING,
      with no subsequent model inference latency.

    GAP 5 — No pre-flight success criteria check (structural, unimplemented):
      The orchestrator has no mechanism to compare the task's success
      criteria against the current on-disk state before the worker starts.
      When a prior partial run has already satisfied some criteria, the
      worker's task brief still describes all items as pending. The worker
      constructs edit patterns based on the brief's FROM: descriptions,
      which no longer match the file. A pre-flight check that reads target
      files and marks already-met criteria would prevent the worker from
      attempting work that is already done and provide accurate context
      about what remains.

  technical_notes: >
    GAP 4 fix: In GTach/ai/ael/src/orchestrator.py, within the
    if _edit_pattern_failed: block, remove the 'return 1' line.
    The block should append the corrective message and fall through
    to the next tool call in the loop — identical to the framework.

    GAP 5 design (see change-a5c8d2f1 §technical_details for full spec):
      run_loop() pre-flight phase before the first worker iteration:
        - Parse success_criteria from the task document (YAML block or
          plain list under '## N.0 Success Criteria').
        - For each criterion that references a file path, read the file
          and evaluate the criterion deterministically where possible
          (grep for string presence/absence, py_compile for syntax).
        - Inject a pre-flight summary into the worker's initial context:
            "Pre-flight check: criteria 2, 3, 4 already satisfied.
             Remaining: criteria 1 (watchdog.py syntax error)."
        - Worker acts only on unsatisfied criteria.
      Scope: opt-in via config (preflight_check: true). Default off
      until validated. Applies to framework and skel only; project
      copies inherit via standard sync.

  related_issues:
    - issue_ref: "issue-f4a7c2e9"
      relationship: "overlapping fix location (P4 post-write syntax check)"
    - issue_ref: "issue-b2d4f6a8"
      relationship: "overlapping fix location (MCP error handling in run_phase)"
```

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    See change-a5c8d2f1 iteration 2 for full specification.
    Four remaining actions:
      4. Remove spurious 'return 1' from GTach orchestrator edit mismatch branch.
      5. Design and implement pre-flight success criteria check in framework
         and skel run_loop() (opt-in, default off).
      Propagate Gap 4 fix to any other project copies (solax-modbus) that
      may have the same spurious line.
  change_ref: "change-a5c8d2f1"
  resolved_date: "2026-03-27"
  resolved_by: "William Watson"
  fix_description: >-
    Gap 6: corrective guidance from P1a, P1c, and P4 was injected as a
    standalone role:user message after role:tool. The Mistral/oMLX API
    rejects this structure with an unhandled exception (rc=1 in <10ms, no
    model call). Fixed by embedding guidance in the tool result content.
    Applies to framework, skel, and GTach.

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: >
    Targeted edit-failure guidance (Gaps 1-3) prevents generic retry loops.
    Removing the spurious return 1 (Gap 4) allows the corrective message to
    reach the model. Pre-flight check (Gap 5) prevents the worker from
    constructing stale patterns when prior runs have partially completed work.
  process_improvements: >
    Propagation from framework to project copies should include a diff
    review step to detect lines introduced during propagation that are
    not present in the canonical framework source.

traceability:
  design_refs:
    - ""
  change_refs:
    - "change-a5c8d2f1"
  test_refs:
    - ""

notes: >
  Original observation: GTach prompt-e1f2a3b4-3.
  Log: GTach/.ael/ralph/ael_20260327-120831.LOG
  Continued failures: ael_20260327-125814.LOG, ael_20260327-130118.LOG
  Worker model: Devstral-Small-2-24B-Instruct-2512.
  GAP 4 evidence: rc=1 within 5ms of WARNING in all three logs.

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 1
  failure_mode: "spurious_return_1_in_edit_mismatch_branch"
  last_review_feedback: "N/A — loop exits before reviewer phase"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3 | 2026-03-27 | William Watson | Resolved: Gap 6 (role:user after role:tool rejected by API) fixed; corrective guidance embedded in tool result content across framework, skel, GTach |
| 1.2 | 2026-03-27 | William Watson | Reopened; added GAP 4 (spurious return 1 in GTach copy) and GAP 5 (pre-flight check); updated reproduction, behavior, analysis, resolution |
| 1.1 | 2026-03-27 | William Watson | Status resolved; fix_description populated (premature — framework only) |
| 1.0 | 2026-03-27 | William Watson | Initial issue |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
