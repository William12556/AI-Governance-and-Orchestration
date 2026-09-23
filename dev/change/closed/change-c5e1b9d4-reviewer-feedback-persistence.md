Created: 2026 June 28

```yaml
change_info:
  id: "change-c5e1b9d4"
  title: "Persist reviewer REVISE feedback from the final message; reconcile read-only reviewer recipe"
  date: "2026-06-28"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c5e1b9d4"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-c5e1b9d4"
  description: >
    Remediate the feedback-persistence defect arising from the F5 read-only
    reviewer (change-c8b3e9a1) interacting with the F1/F2 verdict fallback
    (change-a1d4f7e2): on REVISE, the reviewer feedback body is never persisted,
    starving the worker and disabling F12 stall detection.

scope:
  summary: >
    In run_loop, persist the reviewer final-message body as review-feedback.txt
    on a fallback REVISE verdict; align ralph-review.yaml OUTPUT guidance with
    the read-only toolset.
  affected_components:
    - name: "orchestrator (run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
      change_type: "modify"
  out_of_scope:
    - "Reviewer tool scope — reviewer remains read-only (change-c8b3e9a1)"
    - "Worker-phase behaviour"
    - "F8 per-iteration runtime budget check (tracked separately)"
    - "Single --mode reviewer verdict surfacing (tracked separately)"

rational:
  problem_statement: >
    The read-only reviewer cannot write review-feedback.txt, and the verdict
    fallback captures only the leading SHIP/REVISE token. On REVISE the feedback
    body is lost: the worker (work recipe step 4) receives nothing and repeats,
    and F12 stall detection — which hashes review-feedback.txt — never fires on
    an always-empty file. The loop cannot converge beyond one iteration.
  proposed_solution: >
    When run_loop derives the verdict from the reviewer final message
    (review-result.txt absent) and it resolves to REVISE, write the message body
    (text after the leading verdict token) to review-feedback.txt, unless a
    non-empty review-feedback.txt already exists. Update ralph-review.yaml OUTPUT
    to instruct the reviewer to emit the verdict as the leading token followed by
    the feedback body in the final message, and remove the "use write tool"
    instruction it can no longer satisfy.
  benefits:
    - "Worker receives targeted feedback; REVISE -> fix -> SHIP can converge"
    - "F12 stall detection becomes effective (non-empty, comparable feedback)"
    - "Recipe matches the reviewer's actual (read-only) capability"
  risks:
    - risk: "Leading-token stripping removes part of legitimate feedback"
      mitigation: "Strip only the first whitespace-delimited token when it normalises to SHIP/REVISE; retain the remainder verbatim"
    - risk: "Overwriting a reviewer-written feedback file"
      mitigation: "Synthesise feedback only when review-feedback.txt is absent or empty"

technical_details:
  current_behavior: >
    run_loop reads review-result.txt (precedence) then falls back to
    _normalize_verdict(reviewer_final_msg) for the verdict only. review-feedback.txt
    is read but never written on the fallback path; the reviewer cannot write it.
  proposed_behavior: >
    On a fallback REVISE verdict with no non-empty review-feedback.txt, run_loop
    writes the reviewer message body (post leading token) to review-feedback.txt
    before the REVISE panel, feedback read, and stall-detection steps.
  implementation_approach: >
    Confine changes to the review-result handling block of run_loop and the
    OUTPUT/VERDICT FORMAT guidance of ralph-review.yaml. Exact token-stripping
    decided in implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "On fallback REVISE, persist reviewer_final_msg body to review-feedback.txt when absent/empty; place before feedback read and stall detection"
      functions_affected:
        - "run_loop"
    - component: "ralph-review recipe"
      file: "ai/ael/recipes/ralph-review.yaml"
      change_summary: "Reconcile OUTPUT with read-only toolset: verdict as leading token plus feedback body in the final message; remove 'use write tool' output block"

testing_requirements:
  test_cases:
    - scenario: "Loop REVISE cycle, reviewer read-only"
      expected_result: "review-feedback.txt non-empty with reviewer reasoning; worker receives it next iteration"
    - scenario: "Identical REVISE feedback across stall_threshold cycles"
      expected_result: "F12 stall BLOCK fires (RALPH-BLOCKED.md written)"
    - scenario: "First-pass-correct task"
      expected_result: "Loop SHIPs (no regression)"
    - scenario: "review-feedback.txt already non-empty"
      expected_result: "Existing feedback preserved, not overwritten"
  validation_criteria:
    - "Leading SHIP/REVISE token not duplicated into the feedback body"
    - "review-result.txt precedence unchanged"
    - "Reviewer remains read-only"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-c5e1b9d4; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py and ralph-review.yaml to prior version"

notes: >
  Execution path: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Defect is an integration consequence of
  change-c8b3e9a1 (F5) and change-a1d4f7e2 (F1/F2); reviewer remains read-only by
  design.

closure:
  verified_by: "William Watson"
  verified_date: "2026-07-09"
  verification_result: >
    orchestrator.py persists fallback REVISE feedback body to review-feedback.txt
    (confirmed present in shipped code); ralph-review.yaml v1.8.0 reconciles
    OUTPUT/VERDICT FORMAT with read-only reviewer toolset. Testing per
    testing_requirements.test_cases confirmed via code review; no regression
    to review-result.txt precedence or SHIP path observed.

version_history:
  - version: "1.0"
    date: "2026-06-28"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-07-09"
    changes:
      - "Closed: status implemented; verification recorded"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised implemented -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
