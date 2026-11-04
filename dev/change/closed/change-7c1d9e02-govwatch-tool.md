Created: 2026 June 10

# Change: Implement govwatch Governance Monitoring Tool

---

## Table of Contents

- [1.0 Change Information](#10-change-information)
- [2.0 Scope](#20-scope)
- [3.0 Rationale](#30-rationale)
- [4.0 Technical Details](#40-technical-details)
- [5.0 Testing](#50-testing)
- [6.0 Implementation](#60-implementation)
- [7.0 Traceability](#70-traceability)
- [Version History](#version-history)

---

## 1.0 Change Information

```yaml
change_info:
  id: "change-7c1d9e02"
  title: "Implement govwatch governance monitoring tool"
  date: "2026-06-10"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-7c1d9e02"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Scope

```yaml
scope:
  summary: >
    Add govwatch, a single-module read-only governance monitoring TUI, and
    its dependency manifest. Implementation follows design-govwatch.md v0.1.
  affected_components:
    - name: "govwatch module"
      file_path: "framework/ai/src/govwatch.py"
      change_type: "add"
    - name: "govwatch dependency manifest"
      file_path: "framework/ai/src/requirements-govwatch.txt"
      change_type: "add"
  affected_designs:
    - design_ref: "dev/design/design-govwatch.md"
      sections: ["all"]
  out_of_scope:
    - "Modification of sync-skel.sh / propagate.sh — ai/src/ already in rsync scope (OQ-05)"
    - "Downstream .gitignore edit for dashboard-alerts.md (OQ-04) — deferred, requires separate human decision"
    - "Tests directory — no automated tests this iteration; validation is manual TUI run"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Rationale

```yaml
rationale:
  problem_statement: >
    No tooling provides situational awareness of downstream governance state.
    Workflow phase, document coupling integrity, tactical_brief validity, and
    AEL status must be assessed manually (issue-7c1d9e02).
  proposed_solution: >
    Implement govwatch per design-govwatch.md: a polling textual/rich TUI with
    a Scanner producing an immutable snapshot, PhaseInference, a two-tier
    ComplianceEngine, and an AlertWriter emitting to the clipboard and to
    dashboard-alerts.md (the sole write target).
  alternatives_considered:
    - option: "Web dashboard"
      reason_rejected: "Requires a server process and browser dependency; rejected in requirements §9.1."
    - option: "Extend AEL orchestrator with monitoring"
      reason_rejected: "Couples a read-only observer to the execution loop; violates separation and read-only constraint."
  benefits:
    - "Automated detection of coupling and tactical_brief violations"
    - "Clipboard payload pasteable into Claude Desktop for Strategic Domain review"
    - "No runtime dependency on AEL modules"
  risks:
    - risk: "Document parsing assumptions diverge from future template changes"
      mitigation: "Parsing mirrors orchestrator strategy and schema required-lists; design §9 records the contract."
    - risk: "AEL 'running' status inferred from state files may be stale"
      mitigation: "Documented limitation; status derived without process inspection per NFR-03."
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Technical Details

```yaml
technical_details:
  current_behavior: "No govwatch tool exists."
  proposed_behavior: >
    python ai/src/govwatch.py launches a TUI from a downstream project root,
    polling at a configurable interval, rendering Workflow State, Compliance
    Alerts, and Document Registry panels, and writing dashboard-alerts.md.
  implementation_approach: >
    Tactical Domain (Claude Code) authors the single module per
    design-govwatch.md §5-§12. Elements per design §12.0 Element Registry.
  code_changes:
    - component: "govwatch module"
      file: "framework/ai/src/govwatch.py"
      change_summary: >
        Implement ProjectPaths, DocumentRecord, AelState, BudgetState, Alert,
        Snapshot dataclasses; Scanner, PhaseInference, ComplianceEngine,
        AlertWriter; GovwatchApp (textual.App); validate_project,
        parse_filename, parse_document, main. CLASS_DIRS maps class to
        workspace subdirectory (issue -> issues/).
      classes_affected:
        - "ProjectPaths, DocumentRecord, AelState, BudgetState, Alert, Snapshot"
        - "Scanner, PhaseInference, ComplianceEngine, AlertWriter, GovwatchApp"
      functions_affected:
        - "validate_project, parse_filename, parse_document, main"
    - component: "dependency manifest"
      file: "framework/ai/src/requirements-govwatch.txt"
      change_summary: "List textual and rich."
  interface_changes: []
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Manual validation run from a downstream project root that contains
    workspace/ and (optionally) .ael/ralph/. No automated tests this iteration.
  test_cases:
    - scenario: "Run against a project with a coupled issue+change pair"
      expected_result: "Registry groups the pair by UUID; no coupling violation."
    - scenario: "Run against a project with a T02 lacking its T03"
      expected_result: "VIOLATION alert FR-02-01; red in Compliance panel."
    - scenario: "Run against a T04 with empty/placeholder tactical_brief"
      expected_result: "VIOLATION alert FR-02-10."
    - scenario: "Absent .ael/ralph/"
      expected_result: "AEL status Idle; no exception (NFR-05)."
    - scenario: "Press C, R, Q"
      expected_result: "Clipboard payload copied; immediate refresh; clean quit."
    - scenario: "Each scan"
      expected_result: "dashboard-alerts.md overwritten with current state only (FR-04-04)."
  validation_criteria:
    - "TUI renders three panels without error"
    - "Phase inference matches design §6.0 precedence"
    - "No write occurs outside dashboard-alerts.md (NFR-01)"
    - "Malformed document yields WARNING, not unhandled exception (NFR-04)"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Implementation

```yaml
implementation:
  steps:
    - step: "Claude Code: author framework/ai/src/govwatch.py per design-govwatch.md and prompt-7c1d9e02"
      status: "pending"
    - step: "Claude Code: create framework/ai/src/requirements-govwatch.txt (textual, rich)"
      status: "pending"
    - step: "William: manual validation run from a downstream project root"
      status: "pending"
    - step: "William: propagate via bin/sync-skel.sh then bin/propagate.sh <project>"
      status: "pending"
    - step: "William: set issue-7c1d9e02 status to resolved after verification"
      status: "pending"
  rollback_procedure: "Remove framework/ai/src/govwatch.py and requirements-govwatch.txt; restore from git history."
  deployment_notes: >
    govwatch propagates automatically — ai/src/ is within the recursive rsync
    scope of both scripts; no script modification required (OQ-05).
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Traceability

```yaml
traceability:
  design_updates:
    - design_ref: "dev/design/design-govwatch.md"
      sections_updated: []
      update_date: ""
  related_issues:
    - issue_ref: "issue-7c1d9e02"
      relationship: "source"
  related_prompts:
    - prompt_ref: "prompt-7c1d9e02"
      relationship: "implements"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-10 | William Watson | Initial change — govwatch implementation, coupled to issue-7c1d9e02 |
| 1.1 | 2026-06-15 | William Watson | Implemented: govwatch.py present in framework/ai/src/ and path-aligned to ai/ layout (change-b6e4a1c9); closed |

---

Copyright (c) 2026 William Watson. MIT License.
