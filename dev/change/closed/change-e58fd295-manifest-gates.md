Created: 2026 October 01

```yaml
change_info:
  id: "change-e58fd295"
  title: "Phase 2 step 2: governance model manifest, declared gates and stage flow"
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
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.1, §5.0 and §6.0"
  description: "Step 2 of the Phase 2 implementation plan: manifest, gates and stage flow (FR-01, FR-02, FR-03)."

scope:
  summary: >
    Add ai/engine/src/manifest.py (locate, load and validate the installed
    governance model's manifest.yaml) and ai/engine/src/gates.py (syntax gate
    and command gates). Add ai/governance/software-engineering/manifest.yaml
    and move the audit recipes into that package. The engine selects recipes
    through the manifest's run types, runs the loop stage's declared gates
    (command gates configurable per project), logs every gate result, lets any
    failing command gate override SHIP, writes awaiting-approval.md after SHIP
    and appends the return stage to BLOCKED.md for tracked work items.
    bootstrap.sh and propagate.sh create absent workspace folders listed in the
    manifest.
  affected_components:
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "add" }
    - { name: "gates", file_path: "ai/engine/src/gates.py", change_type: "add" }
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "SE manifest", file_path: "ai/governance/software-engineering/manifest.yaml", change_type: "add" }
    - { name: "audit recipes", file_path: "ai/engine/recipes/audit-*.yaml → ai/governance/software-engineering/recipes/", change_type: "move" }
    - { name: "scripts", file_path: "bin/bootstrap.sh, bin/propagate.sh", change_type: "modify" }
    - { name: "configuration template and documents", file_path: "ai/engine/config.template.yaml, ai/engine/README.md, ai/engine/doc/guide-engine-operations.md, governance.md P10 recipe location", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_manifest_gates.py", change_type: "add" }
  out_of_scope:
    - "Write scope enforcement using writable_paths (step 3)"
    - "Stage derivation from documents, approvals file, pre-run check (step 4)"

rational:
  problem_statement: >
    Recipes, gates and stages are fixed in orchestrator.py, so only the SE
    workflow can run and the pytest gate's interpreter cannot be set per
    project (backlog §2.0-10).
  proposed_solution: "Read them from the installed model's manifest, with per-project gate overrides in ai/config.yaml."
  risks:
    - "A missing or invalid manifest now stops the engine (FR-01-05); downstream projects receive the manifest with the next propagation"

technical_details:
  proposed_behavior: >
    The engine locates exactly one ai/governance/<name>/manifest.yaml next to
    its own ai/engine/ folder. The SE manifest reproduces the current flow:
    run types loop and audit; loop stage gates syntax, pytest, reviewer; the
    pytest command '{python} -m pytest -q {targets}' with a 300 s timeout.
    gates.python in ai/config.yaml selects the interpreter for {python}.
  interface_changes:
    - "config: gates.python; gates.<name>.{command, timeout_seconds}"
    - "run_loop: keyword arguments gates, gate_specs"
    - "state files: awaiting-approval.md (after SHIP)"

testing_requirements:
  validation_criteria:
    - "All existing tests pass unchanged"
    - "Manifest validation, gate command construction and outcomes, SHIP override by a failing command gate, awaiting-approval.md, BLOCKED return stage and workspace folder creation are tested"

implementation:
  rollback_procedure: "Revert the commit; the audit recipes return to ai/engine/recipes/."

traceability:
  requirements: ["FR-01-01", "FR-01-02", "FR-01-03", "FR-01-04", "FR-01-05", "FR-01-06", "FR-01-07", "FR-02-01", "FR-02-02", "FR-02-03", "FR-03-01", "FR-03-02", "FR-03-03", "FR-03-04", "FR-03-05", "FR-03-06", "NFR-01", "NFR-04"]
  design: "design-14e05e35 §5.0, §6.0"
  prompt: "dev/prompt/closed/prompt-e58fd295-manifest-gates.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-01"
    changes: ["Verified: operator test 130 passed; commit 89e8947; closed"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
