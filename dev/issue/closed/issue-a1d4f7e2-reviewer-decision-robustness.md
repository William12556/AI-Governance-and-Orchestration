Created: 2026 June 26

```yaml
issue_info:
  id: "issue-a1d4f7e2"
  title: "Ralph Loop reviewer decision handling is brittle and clobbers work-summary.txt"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-a1d4f7e2"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), reviewer-decision findings
    F1, F2, F13. The reviewer SHIP/REVISE verdict can be lost or misread,
    producing unbounded REVISE, and the shared terminal-write path corrupts the
    artifact under review.

affected_scope:
  components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
  version: "current"

reproduction:
  prerequisites: "Ralph Loop (--mode loop) with a reviewer that may emit its verdict in prose."
  steps:
    - "F1: reviewer states SHIP/REVISE in its final message instead of writing review-result.txt; run_loop reads review-result.txt empty, treats as not-SHIP, REVISEs, loops"
    - "F2: reviewer writes 'SHIP.' / '**SHIP**' / 'ship'; exact-string compare result == 'SHIP' fails and falls through to REVISE"
    - "F13: reviewer final message (no tool calls) overwrites work-summary.txt via the shared terminal-write path, corrupting the worker record"
  frequency: "intermittent"
  reproducibility_conditions: "Depends on reviewer output form (prose verdict, decorated/case-variant SHIP, or terminal message without tool calls)."
  error_output: "Bare REVISE printed each cycle with no review-result.txt; corrupted work-summary.txt on the subsequent cycle."

behavior:
  expected: >
    The reviewer decision is recognised whether written to review-result.txt or
    stated in the final message, tolerant of casing and decoration; the review
    phase does not write or overwrite work-summary.txt.
  actual: >
    A prose verdict yields no result file (F1); a decorated/case-variant SHIP
    fails the exact-string test (F2); a reviewer terminal message overwrites
    work-summary.txt (F13). All three drive non-converging REVISE.
  impact: "Effective approvals loop indefinitely; the worker artifact under review is corrupted."
  workaround: "None reliable."

analysis:
  root_cause: >
    run_phase is shared by both phases; its terminal branch writes the model
    text to work-summary.txt and returns regardless of phase (F1, F13). SHIP
    detection uses result == 'SHIP' after strip(), with no normalisation (F2).
  technical_notes: >
    F1: parse SHIP/REVISE from the reviewer final message as a fallback when
    review-result.txt is absent. F2: normalise — uppercase, strip
    non-alphanumerics, test the leading token. F13: make the terminal-write
    target phase-specific or suppress it during review.
  related_issues:
    - issue_ref: "issue-e2b8046c"
      relationship: "related"

resolution:
  approach: >
    Review-phase final-message fallback parsing (F1); normalised SHIP comparison
    (F2); phase-specific terminal-write target so review does not write
    work-summary.txt (F13). Orchestrator change; F2 normalisation may also touch
    ralph-review.yaml.

verification:
  verification_steps:
    - "Reviewer prose verdict (no review-result.txt) is honoured: SHIP ships, REVISE revises"
    - "Decorated/case-variant SHIP ('SHIP.', '**SHIP**', 'ship') resolves to SHIP"
    - "After a review phase, work-summary.txt retains the worker content unmodified"
    - "A genuinely incomplete task still REVISEs (no SHIP-gate regression)"

notes: >
  Groups proposal-f9a2c41b findings F1 (high), F2 (high), F13 (medium). Distinct
  from issue-e2b8046c, which is an observed symptom of the same over-looping
  class; these are the structural causes for prose/decorated verdicts and the
  shared write path. All three are source changes.

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
