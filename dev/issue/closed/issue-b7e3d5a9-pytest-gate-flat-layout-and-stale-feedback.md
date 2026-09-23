Created: 2026 July 29

```yaml
issue_info:
  id: "issue-b7e3d5a9"
  title: "Pytest gate resolves no targets for flat src/ layouts; review-feedback.txt is never refreshed across loop iterations"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-b7e3d5a9"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "dev/smoke run 531e5e76 (2026-07-29 08:25)"
  description: >
    Two independent defects observed in the first Ralph Loop run to complete a
    full worker/review cycle.

    (1) Pytest gate target resolution. _run_pytest_gate maps a deliverable
    src/<component>/... to the directory tests/<component>/ by taking
    parts[1] of the relative path. For a flat layout the deliverable is
    src/<name>.py, so parts[1] is "<name>.py" and the gate tests
    os.path.isdir("tests/<name>.py"), which can never be true. No targets
    resolve, the gate returns empty, and no [TEST GATE] block is injected. A
    project laid out as src/split.py + tests/test_split.py receives no test
    enforcement whatsoever, and the SHIP override cannot fire.

    (2) Stale reviewer feedback. review-feedback.txt is cleared once by
    clear_state at loop start, outside the iteration loop. The fallback
    persistence in run_loop is guarded by `if not existing_feedback:` and so
    writes only on the first REVISE. Every subsequent worker phase therefore
    reads cycle 1's feedback regardless of what later reviewers said. Because
    the file content is literally unchanged, F12 stall detection compares it
    to itself and increments on every cycle, guaranteeing a false BLOCK on any
    loop that reaches stall_threshold iterations.

affected_scope:
  components:
    - name: "orchestrator (_run_pytest_gate, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
  designs: []
  version: "current"

reproduction:
  prerequisites: "Ralph Loop, project with a flat src/<name>.py + tests/test_<name>.py layout, at least two loop iterations."
  steps:
    - "Run --mode loop against dev/smoke (src/split.py, tests/test_split.py)"
    - "Observe reviewer task contains [SYNTAX GATE: PASS] but no [TEST GATE] block"
    - "Observe log: 'pytest gate: no test-relevant targets resolved — gate is no-op'"
    - "Allow the loop to run a second cycle"
    - "Observe the logged 'review feedback:' body in cycle 2 is cycle 1's text, not cycle 2's verdict body"
    - "Observe 'stall detection: identical feedback (count=1/3)'"
  frequency: "always"
  reproducibility_conditions: "Defect 1 requires a flat src/ layout. Defect 2 is layout-independent and affects every multi-iteration loop."
  preconditions: ""
  test_data: "dev/smoke"
  error_output: |
    2026-07-29 08:29:12 INFO phase start phase=REVIEWER ... task=[SYNTAX GATE: PASS]
    2026-07-29 08:32:41 DEBUG stall detection: identical feedback (count=1/3)

behavior:
  expected: >
    (1) A deliverable src/<name>.py resolves to tests/test_<name>.py when that
    file exists, so the pytest gate runs and can enforce.
    (2) Each review phase replaces the prior cycle's feedback, so the worker
    receives current feedback and stall detection measures genuine repetition
    by the reviewer rather than orchestrator staleness.
  actual: >
    (1) No targets resolve for flat layouts; the gate silently no-ops.
    (2) Feedback is frozen at cycle 1 for the life of the run.
  impact: >
    (1) The pytest SHIP gate introduced by change-5bdc2d9b provides no
    protection for flat-layout projects, while appearing to be active.
    (2) Reviewer feedback after cycle 1 is discarded, so the loop cannot
    converge on later reviewer guidance, and F12 stall detection produces a
    false BLOCK on any run reaching three iterations.
  workaround: "(1) Restructure to src/<component>/ + tests/<component>/. (2) None."

environment:
  python_version: "3.11"
  os: "macOS 14+ / Apple Silicon"
  dependencies: []
  domain: "tactical"

analysis:
  root_cause: >
    (1) The component-directory heuristic assumes parts[1] names a package
    directory; it does not handle parts[1] naming a module file.
    (2) The `if not existing_feedback:` guard from change-c5e1b9d4 was intended
    to avoid clobbering feedback written by the reviewer itself. Since F5 made
    the reviewer read-only, the orchestrator is the only writer, so the guard
    now protects nothing but stale data. The per-cycle clear at the review
    phase (clear_state work-complete.txt) omits review-feedback.txt.
  technical_notes: >
    Defect 1 is the limitation recorded in change-5bdc2d9b out_of_scope
    ("Test target resolution beyond the tests/<component>/ layout
    convention"), now confirmed empirically rather than assumed. The remedy
    stays targeted rather than falling back to a whole-suite run, preserving
    that change's file-scoped design decision.

    Defect 2's stall-detection consequence was not anticipated when
    change-c5e1b9d4 was written; the interaction only becomes observable in a
    live multi-iteration run.
  related_issues:
    - issue_ref: "issue-5bdc2d9b"
      relationship: "related — introduced the pytest gate whose resolution is incomplete"
    - issue_ref: "issue-c5e1b9d4"
      relationship: "related — introduced the non-overwrite guard now causing staleness"
    - issue_ref: "issue-a2f9c4d1"
      relationship: "related — its fix enabled the run that surfaced both defects"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: "Flat-layout fallback in pytest target resolution; add review-feedback.txt to the per-cycle clear"
  change_ref: "change-b7e3d5a9"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5)"
  fix_description: >
    Added a flat-module fallback to _run_pytest_gate's src/ target-resolution
    branch: when the tests/<component>/ directory mapping does not resolve,
    tests test_<stem>.py then <stem>_test.py where stem is the deliverable's
    basename. Added review-feedback.txt to the per-cycle clear_state call
    immediately before the review phase, alongside work-complete.txt.

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude Desktop (independent P08 audit session) — audit-p08-20260729"
  test_results: >
    Verified live and independently. Run a2d10058 (both cycles): reviewer task
    contains '[TEST GATE: PASS]' with 'pytest gate: running pytest on 1
    target(s)' naming tests/test_split.py — the flat-layout fallback resolving
    and executing where it previously no-opped. Cycle 1 and cycle 2 persisted
    fallback feedback bodies of differing length (684 vs 790 chars), confirming
    distinct content rather than a repeat of cycle 1. The worker was separately
    confirmed to read the prior cycle's feedback before the per-cycle clear
    removes it. No findings against this change; audit status "verified".
  closure_notes: >
    Closed per audit-p08-2026-07-29-orchestrator-changes.md, the only one of
    the three audited changes to receive a clean "verified" status with no
    findings. The stall-BLOCK threshold path and the pytest-FAIL/SHIP-override
    path remain unexercised in all available evidence — disclosed as pre-
    existing weak points, not defects of this fix, and not required for its
    own two success criteria.

prevention:
  preventive_measures: >
    Both defects were invisible to inline source review across prior audits and
    surfaced on the first live multi-cycle run. Gate-related changes should not
    close on source review alone.
  process_improvements: ""

verification_enhanced:
  verification_steps: []
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-b7e3d5a9"
  test_refs:
    - "dev/smoke"

notes: >
  A third observation from the same run is not treated as a defect: the
  reviewer issued REVISE on a correct implementation, objecting to a harmless
  defensive guard. The delivered code satisfies all fifteen oracle assertions.
  This is recipe calibration under "Err toward REVISE when uncertain", not a
  code defect, and is being addressed separately as a prompt-engineering
  question.

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 2
  failure_mode: "max iterations 2 reached without SHIP on a correct implementation"
  last_review_feedback: "stale cycle-1 body (defect 2)"

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial issue from live dev/smoke run 531e5e76"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Resolved via change-b7e3d5a9; independently verified by P08 audit audit-p08-20260729 (status: verified, no findings); issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
