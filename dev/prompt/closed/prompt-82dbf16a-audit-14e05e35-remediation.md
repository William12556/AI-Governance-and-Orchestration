Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-82dbf16a"
  task_type: "code_generation"
  source_ref: "change-82dbf16a"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 5
  coupled_docs:
    change_ref: "change-82dbf16a"
    change_iteration: 5

context:
  purpose: "Remediate audit-14e05e35 H-01 to H-03, M-01 to M-05 and the in-scope low findings; iteration 2: the follow-up audit residuals F-01 to F-06; iteration 3: the second follow-up F2-01 to F2-04; iteration 4: the third follow-up F3-01, F3-02; iteration 5: the fourth follow-up F4-01, F4-02."
  constraints:
    - "The worker keeps write access to work-summary.txt, work-complete.txt and BLOCKED.md"
    - "Approvals are compared with the working copy of each evidence document"
    - "The stage scan and pre-run check write nothing, including the git index"
    - "Existing tests pass; fixtures change only where approvals must now carry hashes"

specification:
  requirements:
    functional:
      - "H-01: clear review-result.txt before the review phase; scope.check refuses writes to the engine signal files for the worker in every task"
      - "H-03: run_phase refuses a call whose tool was not offered to the phase and any write tool in a review phase; the call is not dispatched and is logged"
      - "H-02: approve.py records blobs {document name: git blob hash} for the stage's evidence documents; prerun_missing and scan (at the loop stage) report changed, added or removed documents and entries without blobs; re-running approve.py replaces the entry"
      - "M-01: a write-classified call with no recognised path argument is refused"
      - "M-02: an UNCHECKED command gate writes BLOCKED.md naming the gate and returns 1 before the review phase; SKIPPED gates are listed in awaiting-approval.md"
      - "M-04: stages.py runs git with --no-optional-locks"
      - "M-05: gate specs carry scrub_env from providers.*.api_key_env; run_command_gate removes those variables"
      - "L-01, L-02: realpath in is_tracked_task and the scope check; L-03: writable_paths must be relative paths below the root; L-12: return stage in worker mode; L-13: declared deliverables in the [DELIVERABLES] block; L-14: approval UUIDs must be quoted 8-hex strings"
      - "Iteration 2, F-01: the verdict and the REVISE feedback come from the reviewer final message only; review-result.txt is not read"
      - "Iteration 2, F-02: prerun_missing(task_path) and stages.py --task-check refuse a task that is not an active evidence document of the stage before the loop stage (resolved path); engine-mcp runs the check before starting"
      - "Iteration 2, F-03: blobs keyed by path relative to ai/workspace/"
      - "Iteration 2, F-04, F-05: refuse a write whose target is or contains a signal file; compare case-folded paths"
      - "Iteration 3, F2-01, F2-02: task_document_error requires realpath(task) to equal the realpath of an active task-stage document of the UUID taken from the task name as given; fullmatch for document and engine-mcp names"
      - "Iteration 3, F2-03, F2-04: clear review-result.txt, review-feedback.txt, .complete and awaiting-approval.md after the gates, before the review phase"
      - "Iteration 4, F3-01: run that clear before the UNCHECKED check"
      - "Iteration 4, F3-02: read the task bytes once before the pre-run check; prerun_missing(task_bytes) requires their blob hash to equal the approved hash of the matched document; use the bytes for the task text and the write scope"
      - "Iteration 5, F4-01: clear_state and reset_state remove files, symlinks and directories; an unremovable entry ends the run BLOCKED and reset returns 1; engine_status shipped requires a regular, non-symlink .complete"
      - "Iteration 5, F4-02: prerun_missing refuses a task path given without bytes"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/src/orchestrator.py"
    - path: "ai/engine/src/scope.py"
    - path: "ai/engine/src/stages.py"
    - path: "ai/engine/src/approve.py"
    - path: "ai/engine/src/gates.py"
    - path: "ai/engine/src/manifest.py"
    - path: "ai/engine/mcp/server.py"
    - path: "ai/engine/recipes/loop-review.yaml"
    - path: "tests/engine/test_audit_remediation.py"
    - path: "tests/engine/test_stages.py"
    - path: "tests/engine/test_manifest_gates.py"
    - path: "tests/engine/test_migrate_terms.py"
    - path: "tests/engine/test_engine_mcp.py"

success_criteria:
  - "Full engine and overwatch test suites pass"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.15"
  schema_type: "t03_prompt"
```
