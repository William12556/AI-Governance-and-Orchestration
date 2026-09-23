Created: 2026 June 28

```yaml
issue_info:
  id: "issue-c5e1b9d4"
  title: "Reviewer REVISE feedback not persisted when reviewer is read-only — worker starved, stall detection inert"
  date: "2026-06-28"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c5e1b9d4"
    change_iteration: 1

source:
  origin: "code_review"
  description: >
    Post-implementation review of proposal-f9a2c41b remediations. The read-only
    reviewer (change-c8b3e9a1, F5) has no write tool, so it cannot write
    review-feedback.txt. The verdict fallback (change-a1d4f7e2, F1/F2) captures
    only the leading SHIP/REVISE token from the reviewer final message, not the
    feedback body. On REVISE the feedback body is therefore lost.

affected_scope:
  components:
    - name: "orchestrator (run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
  version: "current (post proposal-f9a2c41b implementation)"

reproduction:
  prerequisites: "Ralph Loop (--mode loop); reviewer running with the read-only tool subset."
  steps:
    - "Run a loop task that the reviewer will REVISE (incomplete or iterative)"
    - "Reviewer emits 'REVISE <reasons>' as its final message (it cannot write files)"
    - "run_loop derives verdict REVISE from the final message; review-feedback.txt remains empty"
    - "Next work phase: worker reads STATE_DIR/review-feedback.txt (work recipe step 4), finds it empty"
    - "Worker repeats the same output; reviewer repeats REVISE; loop runs to max_iterations"
  frequency: "always"
  reproducibility_conditions: >
    Any REVISE cycle while the reviewer toolset is read-only. The SHIP path is
    unaffected (verdict token alone suffices to ship).
  error_output: "review-feedback.txt empty after a REVISE verdict; worker receives no corrective guidance."

behavior:
  expected: >
    On REVISE, the reviewer's feedback reaches the worker via review-feedback.txt
    so the worker can target its revision; stall detection observes feedback
    content and can BLOCK on repetition.
  actual: >
    review-feedback.txt is never written (reviewer has no write tool) and the
    orchestrator captures only the verdict token. Feedback is lost, the worker
    repeats unchanged, and F12 stall detection — which hashes review-feedback.txt
    — sees an empty string every cycle and never fires.
  impact: >
    The REVISE -> fix -> SHIP cycle is broken: the loop cannot converge on any
    task requiring more than one iteration, and burns all iterations without the
    stall guard engaging. The SHIP path (first-pass-correct) still works.
  workaround: "None within the loop."

environment:
  python_version: "3.11 (Homebrew)"
  os: "macOS (Apple Silicon)"

analysis:
  root_cause: >
    Interaction of two accepted remediations with an unreconciled recipe.
    change-c8b3e9a1 removed the reviewer's write tools; change-a1d4f7e2 added a
    verdict-only fallback parser. ralph-review.yaml still instructs the reviewer
    to "use write tool" for review-result.txt and review-feedback.txt, which it
    can no longer do. No path persists the feedback body, so the worker's
    feedback channel (work recipe step 4) and F12 stall detection (hashes
    review-feedback.txt) are both starved.
  technical_notes: >
    F12 stall detection: _hash_feedback("") returns "" and the stall branch is
    guarded by `if _current_hash and ...`, so an always-empty feedback never
    increments the stall counter.
  related_issues:
    - issue_ref: "issue-c8b3e9a1 (closed)"
      relationship: "blocked_by"
    - issue_ref: "issue-a1d4f7e2 (closed)"
      relationship: "related"

resolution:
  approach: >
    In run_loop, when the verdict is derived from the reviewer final message
    (review-result.txt absent) and resolves to REVISE, persist the reviewer
    message body (text after the leading verdict token) to review-feedback.txt,
    unless the reviewer already wrote a non-empty review-feedback.txt. Reconcile
    ralph-review.yaml OUTPUT guidance with the read-only toolset: instruct the
    reviewer to emit the verdict as the leading token followed by the feedback
    body in the final message, and remove the "use write tool" instruction.

verification:
  verification_steps:
    - "Loop REVISE cycle: review-feedback.txt is non-empty and contains the reviewer reasoning"
    - "Worker next iteration receives the feedback (work recipe step 4)"
    - "Identical feedback across stall_threshold cycles triggers the F12 stall BLOCK"
    - "First-pass-correct task still SHIPs (no regression)"
    - "A reviewer-written review-feedback.txt, if present, is not overwritten"

notes: >
  Out of scope (track separately): F8 per-iteration runtime budget check still
  excludes the tool-schema payload (only the report was corrected); single
  --mode reviewer does not surface the parsed verdict. Neither affects loop
  convergence.

closure:
  verified_by: "William Watson"
  verified_date: "2026-07-09"
  verification_result: >
    Code implemented in orchestrator.py (fallback REVISE feedback persistence)
    and ralph-review.yaml (v1.8.0, OUTPUT/VERDICT FORMAT reconciled with
    read-only reviewer toolset). Verification steps from resolution.verification_steps
    confirmed via review of shipped orchestrator.py logic; no regression
    observed in prior AEL runs against this codebase.

version_history:
  - version: "1.0"
    date: "2026-06-28"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-07-09"
    changes:
      - "Closed: status resolved; verification recorded"
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
