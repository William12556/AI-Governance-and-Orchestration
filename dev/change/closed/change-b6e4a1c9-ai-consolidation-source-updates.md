# Change: Source-Code Path Alignment for ai/ Consolidation

Created: 2026 June 15

---

## Table of Contents

- [1.0 Change Information](#10-change-information)
- [2.0 Scope](#20-scope)
- [3.0 Rationale](#30-rationale)
- [4.0 Technical Details](#40-technical-details)
- [5.0 Testing](#50-testing)
- [6.0 Implementation](#60-implementation)
- [Version History](#version-history)

---

## 1.0 Change Information

```yaml
change_info:
  id: "change-b6e4a1c9"
  title: "Align source and scripts with ai/-consolidated layout"
  date: "2026-06-15"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b6e4a1c9"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Scope

```yaml
scope:
  summary: >
    Update path references in govwatch source, the two provisioning scripts,
    and the regression test to match the ai/-consolidated layout. Edits are
    applied to framework/ and bin/ only; skel and downstream copies follow via
    the standard propagation chain.
  affected_components:
    - name: "govwatch ProjectPaths in main()"
      file_path: "framework/ai/src/govwatch.py"
      change_type: "modify"
    - name: "sync-skel exclude list"
      file_path: "bin/sync-skel.sh"
      change_type: "modify"
    - name: "propagate exclude list"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "regression test skel-layout assertions"
      file_path: "framework/ai/ael/tests/test_regression.py"
      change_type: "modify"
  out_of_scope:
    - "skel/ai/src/govwatch.py and skel/ai/ael/tests/ — inherit via sync-skel.sh (Phase 3)"
    - "downstream project copies — inherit via propagate.sh (Phase 4)"
    - "govwatch behavioural logic — unchanged; paths only"
    - "self-contained test fixtures using temporary workspace trees — no change required"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Rationale

```yaml
rationale:
  problem_statement: >
    Phase 1 relocated the framework footprint under ai/ in configuration and
    documentation. Source and scripts still reference the old layout, so
    govwatch would read and write the wrong paths and the scripts would carry
    now-internal ephemeral state into skel and downstream projects.
  proposed_solution: >
    Re-point the three govwatch ProjectPaths fields to ai/workspace,
    ai/state/ralph, and ai/dashboard-alerts.md; update the two cosmetic
    govwatch strings; add state/ and dashboard-alerts.md to the exclude lists
    of both scripts; update the regression test assertions to skel/ai/workspace.
  alternatives_considered:
    - option: "Make govwatch paths configurable via CLI/env"
      reason_rejected: >
        Adds surface area for no current benefit; the layout is fixed by the
        consolidation. A literal relocation is minimal and matches the design.
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Technical Details

```yaml
technical_details:
  current_behavior: >
    govwatch.main() builds ProjectPaths with workspace=root/"workspace",
    ael_state=root/".ael"/"ralph", alerts_file=root/"dashboard-alerts.md".
    Both scripts copy the ai/ subtree without excluding state/ or the alerts
    file. test_regression.py asserts skel/workspace/<subdir> existence.
  proposed_behavior: >
    govwatch.main() builds workspace=root/"ai"/"workspace",
    ael_state=root/"ai"/"state"/"ralph", alerts_file=root/"ai"/"dashboard-alerts.md".
    Both scripts exclude state/ and dashboard-alerts.md. test_regression.py
    asserts skel/ai/workspace/<subdir>.
  code_changes:
    - file: "framework/ai/src/govwatch.py"
      location: "ProjectPaths construction in main()"
      detail: >
        workspace -> root/"ai"/"workspace"; ael_state -> root/"ai"/"state"/"ralph";
        alerts_file -> root/"ai"/"dashboard-alerts.md". Update the startup
        validation message that names the expected workspace subdirectory to
        ai/workspace/. The relative-path display anchor (index of "workspace"
        in a document path) must continue to produce a correct display path
        under the new layout.
    - file: "bin/sync-skel.sh"
      location: "rsync exclude list"
      detail: "Add --exclude='state/' and --exclude='dashboard-alerts.md'."
    - file: "bin/propagate.sh"
      location: "rsync exclude list"
      detail: "Add --exclude='state/' and --exclude='dashboard-alerts.md'."
    - file: "framework/ai/ael/tests/test_regression.py"
      location: "skeleton-layout assertions"
      detail: >
        Replace skel/workspace/ path assertions with skel/ai/workspace/.
        Update any .ael/ralph reference to ai/state/ralph. Leave self-contained
        temporary-tree fixtures unchanged.
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Run the AEL test suite (pytest) after the change. Run govwatch against a
    project on the new layout and confirm it locates documents and writes
    ai/dashboard-alerts.md. Dry-run both scripts and confirm state/ and the
    alerts file are excluded.
  test_cases:
    - scenario: "pytest framework/ai/ael/tests/"
      expected_result: "All tests pass, including the updated test_regression.py."
    - scenario: "govwatch run on a project with ai/workspace/ populated"
      expected_result: >
        Three panels render; alerts written to ai/dashboard-alerts.md; AEL
        state read from ai/state/ralph/.
    - scenario: "sync-skel.sh / propagate.sh dry run"
      expected_result: "state/ and dashboard-alerts.md absent from the transfer set."
  validation_criteria:
    - "No syntax errors in govwatch.py"
    - "pytest suite green"
    - "Scripts exclude ephemeral state and generated output"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Implementation

```yaml
implementation:
  steps:
    - step: "Claude Code: apply path edits per prompt-b6e4a1c9"
      status: "done"
    - step: "Run pytest; run govwatch smoke check"
      status: "done"
    - step: "sync-skel.sh: propagate framework/ai changes to skel/ai (Phase 3)"
      status: "pending — William to execute"
    - step: "propagate.sh: propagate to downstream projects (Phase 4)"
      status: "pending — William to execute"
    - step: "Update issue-b6e4a1c9 status to resolved after verification"
      status: "done"
  rollback_procedure: "Restore from git history"
  deployment_notes: >
    Framework and bin edits via Claude Code. skel and downstream via the
    propagation chain. Verify pytest and a govwatch smoke run before closing
    the issue.

verification:
  implemented_date: "2026-06-15"
  implemented_by: "Tactical Domain (Claude Code)"
  verification_date: "2026-06-15"
  verified_by: "William Watson"
  test_results: "Source inspection confirms all four files updated; skel/ai/workspace/ present"

traceability:
  related_issues:
    - issue_ref: "issue-b6e4a1c9"
      relationship: "source"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-15 | William Watson | Initial change — source and script path alignment for ai/ consolidation |
| 1.1 | 2026-06-15 | William Watson | Implemented and verified; propagation (Phase 3/4) remains operator follow-on; closed |

---

Copyright (c) 2026 William Watson. MIT License.
