Created: 2026 June 26

```yaml
issue_info:
  id: "issue-e7a1c3d5"
  title: "Loop hygiene: no stall detection, timeout reported as success, no completion-call error handling"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e7a1c3d5"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), loop-hygiene findings F12,
    F10, F14. The loop cannot detect a stall, reports a timeout as success, and
    aborts on a transient completion error.

affected_scope:
  components:
    - name: "orchestrator (run_loop, duration-limit branch, completions call)"
      file_path: "ai/ael/src/orchestrator.py"
  version: "current"

reproduction:
  prerequisites: "Ralph Loop (--mode loop) reaching the relevant condition."
  steps:
    - "F12: the reviewer emits identical REVISE feedback each cycle; no stall mechanism exists; the loop consumes every iteration without BLOCK"
    - "F10: the duration limit is reached; the branch writes .ralph-complete and returns 0; main_async archives and exits 0; a caller (including ael-mcp) cannot distinguish a timed-out run from a SHIP"
    - "F14: client.chat.completions.create raises on a transient oMLX error; with no surrounding try/except the exception aborts the loop with no retry"
  frequency: "intermittent"
  reproducibility_conditions: "F12 on repeated identical feedback; F10 on duration-limit exit; F14 on a transient endpoint error."

behavior:
  expected: >
    Repeated no-progress feedback triggers a clean BLOCK; a timeout returns a
    distinct non-zero code and sentinel; a transient completion error retries
    with backoff and BLOCKs cleanly on persistent failure.
  actual: >
    A stall burns all iterations without BLOCK (F12); a timeout writes
    .ralph-complete and returns 0 (F10); a transient error aborts the loop
    (F14).
  impact: "Wasted iterations and inference cost; timeout indistinguishable from SHIP; loop fragility under transient endpoint errors."
  workaround: "None reliable."

analysis:
  root_cause: >
    No stall-detection mechanism (F12); the duration-limit branch returns rc=0
    with .ralph-complete (F10); the completions call is unguarded (F14).
  technical_notes: >
    F12: hash review-feedback.txt per cycle; if unchanged for N consecutive
    cycles, write RALPH-BLOCKED.md and stop. F10: return a distinct non-zero
    code and a different sentinel (e.g. .ralph-timeout). F14: wrap with bounded
    retry/backoff; on persistent failure, BLOCK cleanly.
  related_issues:
    - issue_ref: "issue-e2b8046c"
      relationship: "related"

resolution:
  approach: >
    Stall detection (F12); distinct timeout exit code and sentinel (F10);
    bounded retry/backoff around the completions call (F14). All orchestrator
    changes.

verification:
  verification_steps:
    - "N consecutive identical REVISE feedbacks produce RALPH-BLOCKED.md and stop the loop"
    - "A duration-limit exit returns a non-zero code and a timeout sentinel, not .ralph-complete"
    - "A transient completion error retries; a persistent one BLOCKs without an uncaught exception"

notes: >
  Groups proposal-f9a2c41b findings F12 (medium), F10 (medium), F14 (medium). All
  source changes. F12 stall detection relates to the over-looping class observed
  in issue-e2b8046c.

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: "divergence"
  last_review_feedback: ""

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
