Created: 2026 October 01

```yaml
change_info:
  id: "change-155cc014"
  title: "Phase 2 step 6: Strategic Domain / Tactical Domain replaced by the agent roles planner, worker and reviewer"
  date: "2026-10-01"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0); no issue document
    issue_iteration: null

source:
  type: "design"
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.4, §10.0"
  description: "Step 6 of the Phase 2 implementation plan: terminology (FR-07; proposal-5bcd46ad OQ-02)."

scope:
  summary: >
    Add bin/migrate-terms.py (plan by default, --apply, --scan for downstream
    project-owned files). Apply it to the framework-owned documents, templates,
    profiles, docs/ and CLAUDE.md: about 450 lines in 27 files. Fix the few
    sentences the rules leave awkward by hand. Add a Version History row to
    each changed document; governance.md and the SE manifest take version 12.0.
  affected_components:
    - { name: "terminology script", file_path: "bin/migrate-terms.py", change_type: "add" }
    - { name: "governance model", file_path: "ai/governance/software-engineering/ (governance.md, workflow.md, primer.md, templates T03/T08, skills, doc)", change_type: "modify" }
    - { name: "engine documents and comments", file_path: "ai/engine/README.md, ai/engine/doc/, ai/engine/src/orchestrator.py (comments and messages only)", change_type: "modify" }
    - { name: "profiles", file_path: "ai/profiles/", change_type: "modify" }
    - { name: "repository documents", file_path: "docs/, docs/claude/, CLAUDE.md", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_migrate_terms.py", change_type: "add" }
  out_of_scope:
    - "dev/ records, closed/ documents, Version History rows (FR-07-02)"
    - "Template field names such as tactical_brief (FR-07-03)"
    - "Downstream project-owned files: reported by --scan, edited by the operator"

rational:
  problem_statement: "The domain terms predate agent roles (D-07, D-09) and suggest fixed tools rather than roles bound to any model."
  proposed_solution: "Planner for the Strategic Domain; worker and reviewer (worker/reviewer before a noun) for the Tactical Domain."
  risks:
    - "Major governance version: downstream propagation needs --allow-major"

testing_requirements:
  validation_criteria:
    - "No term remains in the live corpus outside version histories, closed documents and dev/ (V-08)"
    - "Script rules tested (capitalisation, compounds, anchors, exclusions); full suite passes"

implementation:
  rollback_procedure: "Revert the commit."

traceability:
  requirements: ["FR-07-01", "FR-07-02", "FR-07-03", "FR-07-04", "FR-07-05"]
  design: "design-14e05e35 §10.0"
  prompt: "dev/prompt/closed/prompt-155cc014-terminology.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record; plan presented to the operator before apply"]
  - version: "1.1"
    date: "2026-10-01"
    changes: ["Applied after operator approval: 450 lines in 27 files, six hand fixes, table-of-contents link capitalisation, Version History rows; governance.md and manifest 12.0"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
