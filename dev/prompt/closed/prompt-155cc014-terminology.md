Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-155cc014"
  task_type: "refactor"
  source_ref: "change-155cc014"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-155cc014"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §10.0: terminology migration."
  constraints:
    - "Apply only after the operator has reviewed the plan"
    - "Version History rows, closed/ and dev/ unchanged; field names unchanged"
    - "docs/claude/primer.md stays identical to ai/governance/software-engineering/primer.md"

specification:
  requirements:
    functional:
      - "bin/migrate-terms.py: plan, --apply, --scan"
      - "Manual fixes for sentences the rules leave awkward"
      - "Version History row in each changed document; governance.md and manifest 12.0"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "bin/migrate-terms.py"
    - path: "tests/engine/test_migrate_terms.py"

success_criteria:
  - "Corpus scan finds no term outside the exclusions; full suite passes"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
