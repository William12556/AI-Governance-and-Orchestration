Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-e58fd295"
  task_type: "code_generation"
  source_ref: "change-e58fd295"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-e58fd295"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §5.0 and §6.0: manifest, declared gates and stage flow."
  constraints:
    - "Existing tests pass unchanged; existing monkeypatch points (_run_syntax_gate, _run_pytest_gate) remain"
    - "SE gate results identical to before (FR-03-04): same targets, same [SYNTAX GATE]/[TEST GATE] blocks"
    - "Manifest errors name file and field and stop the engine before any model call (FR-01-05, NFR-04)"
    - "Workspace folder creation never changes an existing path"

specification:
  requirements:
    functional:
      - "manifest.py: locate exactly one manifest under the engine's sibling ai/governance/; validate model, workspace_folders, writable_paths, run_types (recipe files exist), gates (command), stages (id, owner, gates, on_blocked, approval, evidence), paths"
      - "Recipes resolved from the model folder first, then ai/engine/recipes/"
      - "gates.py: syntax gate logic; pytest target mapping; command construction with {python}, {project_root}, {targets}; PASS / FAIL / UNCHECKED"
      - "run_loop: run the loop stage's gates; log 'gate=<name> type=<type> result=<result>'; any command gate FAIL overrides SHIP"
      - "After SHIP: awaiting-approval.md naming the work item and the next approval stage"
      - "On BLOCKED for a tracked work item (task file prompt-<uuid>-*.md): append 'Return to stage: <on_blocked>'"
      - "bootstrap.sh and propagate.sh create absent workspace folders from the manifest"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/src/manifest.py"
    - path: "ai/engine/src/gates.py"
    - path: "ai/engine/src/orchestrator.py"
    - path: "ai/governance/software-engineering/manifest.yaml"
    - path: "ai/governance/software-engineering/recipes/audit-work.yaml"
    - path: "ai/governance/software-engineering/recipes/audit-review.yaml"
    - path: "bin/bootstrap.sh"
    - path: "bin/propagate.sh"
    - path: "ai/engine/config.template.yaml"
    - path: "tests/engine/test_manifest_gates.py"

success_criteria:
  - "Full engine and overwatch test suites pass"
  - "An SE loop run behaves as before step 2, apart from the gate log lines and awaiting-approval.md"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
