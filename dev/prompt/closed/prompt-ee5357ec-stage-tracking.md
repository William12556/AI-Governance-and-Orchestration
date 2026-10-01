Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-ee5357ec"
  task_type: "code_generation"
  source_ref: "change-ee5357ec"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-ee5357ec"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §8.0: stage tracking, approvals and the pre-run check."
  constraints:
    - "stages.py only reads files and git; it never writes"
    - "Only approvals present in git HEAD count (design §8.3)"
    - "Free-text tasks and prompt files outside ai/workspace/ are not tracked"
    - "Existing tests pass unchanged"

specification:
  requirements:
    functional:
      - "scan(project_root, manifest): one record per UUID with path, documents, approvals, current_stage, missing, anomalies; report warnings (not a git repository, uncommitted approvals ignored)"
      - "A stage with neither evidence nor approval (the loop stage) is complete when a later stage on the path is complete"
      - "prerun_missing(record, manifest): what is missing before the loop stage"
      - "approve.py <uuid> <stage>: validates stage and work item, appends to ai/approvals.yaml, commits only that file, prints the work item's status"
      - "orchestrator: exit 3 before any state change when a tracked run lacks prerequisites"
      - "propagate.sh: ai/approvals.yaml is a declared project path"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/src/stages.py"
    - path: "ai/engine/src/approve.py"
    - path: "ai/engine/src/orchestrator.py"
    - path: "bin/propagate.sh"
    - path: "tests/engine/test_stages.py"

success_criteria:
  - "Full engine and overwatch test suites pass"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
