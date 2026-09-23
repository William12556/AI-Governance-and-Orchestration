Created: 2026 June 28

```yaml
issue_info:
  id: "issue-7c1d9a4e"
  title: "Orchestrator hard-codes Ralph recipe pair; tactical-audit mode unreachable"
  date: "2026-06-28"
  status: "closed"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-7c1d9a4e"
    change_iteration: 1

source:
  origin: "code_review"
  description: >
    main_async loads the recipe pair from fixed filenames ralph-work.yaml and
    ralph-review.yaml. No mechanism selects audit-work.yaml / audit-review.yaml.
    The audit recipes and the orchestrator's audit gates already exist, but the
    tactical-audit mode cannot be launched without manually editing source.

affected_scope:
  components:
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"

behavior:
  expected: >
    The orchestrator selects the audit recipe pair when an audit run is
    indicated, and the standard Ralph pair otherwise — without source edits.
  actual: >
    ralph-work.yaml / ralph-review.yaml are loaded unconditionally. Running a
    tactical audit requires a manual two-line edit before launch and a revert
    afterward.
  impact: >
    Tactical-audit mode is effectively unreachable in normal operation. The
    manual edit is a regression risk and the only manual step in an otherwise
    state-detected audit path.

analysis:
  root_cause: >
    Recipe loading predates audit support. The audit scope-lock, SHIP gate, and
    artifact-archive logic all key on the presence of audit-index.md in the
    state directory, but recipe selection was never parameterised on that signal.
  technical_notes: >
    audit-index.md is a documented pre-launch precondition (guide-audit-loop.md
    §2.2), so it is a reliable selection signal already present before launch.

resolution:
  approach: >
    Select the recipe pair on presence of audit-index.md in the state directory:
    present -> audit-*.yaml, absent -> ralph-*.yaml. Print and log the selected
    recipe set at startup. No new CLI flag or config key.
  change_ref: "change-7c1d9a4e"
  resolved_date: "2026-06-28"
  fix_description: >
    orchestrator.py main_async (lines 1508-1521): recipe load branched on
    os.path.exists(state_dir/audit-index.md); recipe_set label printed and
    logged at startup. recipe_dir line and rev_recipe name retained.

verification:
  verified_date: "2026-06-28"
  test_results: >
    Verified against source: branch present, audit/ralph pairs correct,
    startup print and log lines present, no regression to standard path.
  closure_notes: "Implemented via Claude Code; verified against source."

traceability:
  change_refs:
    - "change-7c1d9a4e"

notes: >
  Scope limited to recipe selection. Governance (P08 two-mode model), primer
  triggers, guide cleanup, and the audit template are handled separately as
  document changes (no triple required).

version_history:
  - version: "1.0"
    date: "2026-06-28"
    changes:
      - "Initial issue document"
  - version: "1.1"
    date: "2026-06-28"
    changes:
      - "Implemented and verified against source; issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised verified -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
