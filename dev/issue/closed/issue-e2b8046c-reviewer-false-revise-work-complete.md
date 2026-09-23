Created: 2026 June 26

```yaml
issue_info:
  id: "issue-e2b8046c"
  title: "Ralph Loop reviewer issues false REVISE for the orchestrator-cleared work-complete.txt"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e2b8046c"
    change_iteration: 1

source:
  origin: "test_result"
  test_ref: "T4 manual Ralph Loop, North-Mini-Code-1.0-6bit, 2026-06-26"
  description: >
    During a full Ralph Loop test, the reviewer issued REVISE every iteration
    citing a missing work-complete.txt, despite the worker's deliverable being
    correct. The loop could not converge to SHIP and exhausted max_iterations.

affected_scope:
  components:
    - name: "orchestrator (run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
    - name: "ralph-work recipe"
      file_path: "ai/ael/recipes/ralph-work.yaml"
  version: "current"

reproduction:
  prerequisites: >
    Ralph Loop (--mode loop) on a task the worker can complete in one pass,
    where the worker writes work-complete.txt and names it in work-summary.txt.
  steps:
    - "Run --mode loop with a trivial, fully-specified task"
    - "Worker writes the deliverable plus work-complete.txt, and lists work-complete.txt in work-summary.txt"
    - "run_loop calls clear_state(state_dir, 'work-complete.txt') before the review phase"
    - "Reviewer reads work-summary.txt, attempts to verify each named file, finds work-complete.txt absent, writes REVISE"
    - "Loop repeats; never SHIPs; exhausts max_iterations"
  frequency: "intermittent"
  reproducibility_conditions: >
    Triggers whenever the worker's work-summary.txt references work-complete.txt
    (or any orchestrator-managed signal file). North Mini Code does so reliably
    because its summaries are literal and complete.
  error_output: >
    review-feedback.txt: "Missing required file: work-complete.txt. The task
    requires creating this file containing the word 'done'. Additionally, verify
    hello.py syntax."

behavior:
  expected: >
    The reviewer evaluates task deliverables only. Orchestrator-managed signal
    files (work-complete.txt, review-*.txt, .ralph-complete) are excluded from
    reviewer verification. The loop converges to SHIP when deliverables are correct.
  actual: >
    The reviewer treats the cleared work-complete.txt as a missing deliverable
    and issues REVISE each cycle. The loop fails to converge and exhausts
    max_iterations.
  impact: >
    Ralph Loop cannot SHIP for any task whose worker summary names the signal
    file. Wasted iterations and inference cost; loop is effectively non-functional
    in this case.
  workaround: "None reliable; the worker cannot be guaranteed to omit work-complete.txt from its summary."

environment:
  python_version: "3.11 (Homebrew)"
  os: "macOS (Apple Silicon)"

analysis:
  root_cause: >
    Two-part interaction. (1) run_loop deletes work-complete.txt before the
    review phase ("clear worker signal before reviewer starts"). (2)
    ralph-review.yaml instructs the reviewer to verify every output file
    mentioned in work-summary.txt, and ralph-work.yaml's worker reports
    work-complete.txt creation in that summary. The reviewer therefore attempts
    to verify a file the orchestrator has deliberately removed and fails.
  technical_notes: >
    Worker deliverable (hello.py) was correct, minimal, and syntactically valid.
    Mechanism is model-agnostic; exposed by the worker naming the signal file.

resolution:
  approach: >
    Decide in design/change. Option A (prompt-level, preferred): ralph-review.yaml
    instructs the reviewer to ignore orchestrator-managed signal files and verify
    only task deliverables. Option B: ralph-work.yaml instructs the worker to
    exclude state/signal files from the work-summary deliverable list. Option C
    (code): defer clearing work-complete.txt until after the reviewer reads it, or
    never expose it to the reviewer. A + B require no source change.

verification:
  verification_steps:
    - "Run a one-pass-completable loop task; confirm SHIP within 1-2 iterations"
    - "Confirm reviewer feedback no longer references work-complete.txt"
    - "Confirm a genuinely incomplete task still REVISEs correctly (no regression of the SHIP gate)"

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 3
  failure_mode: "divergence"
  last_review_feedback: "Missing required file: work-complete.txt..."

notes: >
  Observed during North-Mini-Code-1.0-6bit reviewer-role evaluation. The
  reviewer SHIP/REVISE sentinel mechanism itself functions correctly; this
  defect concerns convergence, not sentinel emission.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Resolved: Option B fix implemented (ralph-work.yaml v1.4.0) and verified against source; change/prompt pair authored; issue closed"
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
