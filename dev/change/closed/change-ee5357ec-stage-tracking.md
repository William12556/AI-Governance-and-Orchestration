Created: 2026 October 01

```yaml
change_info:
  id: "change-ee5357ec"
  title: "Phase 2 step 4: work-item stage tracking, committed approvals and pre-run check"
  date: "2026-10-01"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0); no issue document
    issue_iteration: null

source:
  type: "design"
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.2, §8.0"
  description: "Step 4 of the Phase 2 implementation plan: stage tracking and approvals (FR-08, requirements OQ-01 and OQ-04)."

scope:
  summary: >
    Add ai/engine/src/stages.py: derive each work item's stage from the
    documents in ai/workspace/ using the manifest's stage evidence and paths;
    read approvals from the committed ai/approvals.yaml (git HEAD only); report
    missing evidence, awaited approvals and anomalies. Add
    ai/engine/src/approve.py, the operator command that records one approval
    and commits ai/approvals.yaml. Before a loop or worker run on a T03 prompt
    inside ai/workspace/, the engine refuses to start (exit 3) when an earlier
    stage lacks evidence or approval. Declare ai/approvals.yaml as a project
    file (propagate.sh, governance P10.6, proposal §4.2).
  affected_components:
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "add" }
    - { name: "approve command", file_path: "ai/engine/src/approve.py", change_type: "add" }
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "propagation", file_path: "bin/propagate.sh", change_type: "modify" }
    - { name: "documents", file_path: "governance.md P10.6, manifest.yaml version, proposal-5bcd46ad §4.2, design §14.0 DI-02, engine guide", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_stages.py", change_type: "add" }
  out_of_scope:
    - "engine-mcp work_status tool (step 5); stages.status_report() provides its content"

rational:
  problem_statement: "Open-weight planners may lose track of the workflow; nothing stops a loop run on an unapproved prompt (requirements OQ-01)."
  proposed_solution: "Derive stages from documents, count only committed operator approvals, check prerequisites before a run."
  risks:
    - "Existing work items need their approvals recorded with approve.py before their next tracked engine run"
    - "A planner with git or shell access can still commit an approval (design DI-03, accepted)"

testing_requirements:
  validation_criteria:
    - "All existing tests pass unchanged"
    - "Stage derivation for each SE path, closed documents and anomalies; committed versus uncommitted approvals; non-git project; pre-run refusal; approve.py records and commits; propagate.sh keeps ai/approvals.yaml"

implementation:
  rollback_procedure: "Revert the commit; ai/approvals.yaml in downstream projects can stay (it is ignored by the previous engine)."

traceability:
  requirements: ["FR-08-01", "FR-08-02", "FR-08-03", "FR-08-04", "FR-08-05", "FR-08-07", "NFR-06"]
  design: "design-14e05e35 §8.0"
  prompt: "dev/prompt/closed/prompt-ee5357ec-stage-tracking.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-01"
    changes: ["Verified: operator test 179 passed; commit e846562; closed"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
