Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-bdc6820f"
  task_type: "code_generation"
  source_ref: "change-bdc6820f"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-bdc6820f"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §7.0: write scope and reviewer deliverables block."
  constraints:
    - "Existing tests pass unchanged; _validate_write_scope, _written_targets and MCPClient._is_readonly_tool keep their signatures"
    - "Free-text tasks and non-prompt task files keep project-root containment (NFR-02)"

specification:
  requirements:
    functional:
      - "scope.py: WRITE_TOOLS, write verb patterns, read-only patterns, is_write_tool (fail-closed), is_readonly_tool, path extraction, written_targets"
      - "extract_deliverable_paths(raw): None when the task is not a T03 prompt (no prompt_info), else deliverable.files paths"
      - "WriteScope: exact deliverable files, writable_paths prefixes, state directory; directory creation allowed for ancestors of allowed paths"
      - "Rejected write: tool error 'write outside the declared scope: <path>; allowed: <list>' and log 'write rejected tool=<t> path=<p> reason=<r>'"
      - "Reviewer task: [DELIVERABLES] block with absolute paths from work-summary.txt"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/src/scope.py"
    - path: "ai/engine/src/orchestrator.py"
    - path: "ai/engine/src/mcp_client.py"
    - path: "tests/engine/test_write_scope.py"

success_criteria:
  - "Full engine and overwatch test suites pass"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
