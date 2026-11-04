Created: 2026 June 10

# Issue: Implement govwatch Governance Monitoring Tool

---

## Table of Contents

- [1.0 Issue Information](#10-issue-information)
- [2.0 Source](#20-source)
- [3.0 Affected Scope](#30-affected-scope)
- [4.0 Behavior](#40-behavior)
- [5.0 Analysis](#50-analysis)
- [6.0 Resolution](#60-resolution)
- [7.0 Traceability](#70-traceability)
- [Version History](#version-history)

---

## 1.0 Issue Information

```yaml
issue_info:
  id: "issue-7c1d9e02"
  title: "Implement govwatch governance monitoring tool"
  date: "2026-06-10"
  reporter: "William Watson"
  status: "resolved"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-7c1d9e02"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Enhancement request to implement govwatch, a standalone read-only
    governance monitoring TUI for downstream projects, per approved
    requirements (requirements-govwatch.md v0.3) and component design
    (design-govwatch.md v0.1). Tactical Domain is Claude Code. Governance
    documents reside in dev/; the deliverable is framework/ai/src/govwatch.py.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "govwatch"
      file_path: "framework/ai/src/govwatch.py"   # deliverable target
  designs:
    - design_ref: "design-govwatch.md (dev/design/)"
  version: "framework/ai v9.0"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Behavior

```yaml
behavior:
  expected: >
    A read-only TUI (govwatch) exists, providing: workflow-phase inference
    from open workspace documents; two-tier compliance scanning (filename/
    structure and document content); a document registry grouped by UUID;
    and an alert summary emitted to the clipboard and to dashboard-alerts.md.
  actual: >
    No such tool exists. Workflow state and governance compliance must be
    assessed manually by reading workspace documents and AEL state files.
  impact: >
    No automated detection of issue/change/prompt coupling violations,
    UUID/iteration mismatches, malformed tactical_brief, or indicators of
    Strategic Domain protocol drift. Oversight is wholly manual.
  workaround: "Manual inspection of workspace/ and .ael/ralph/."
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Analysis

```yaml
analysis:
  root_cause: >
    New capability. Not a defect. The framework provides no situational-
    awareness tooling for downstream governance state.
  technical_notes: >
    Single-tier component: one Python module (textual + rich), no AEL
    runtime dependency. Design specifies Scanner, PhaseInference,
    ComplianceEngine, AlertWriter, and a textual App. Parsing and compliance
    logic are fully specified in design-govwatch.md §5-§9.
  related_issues: []
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Resolution

```yaml
resolution:
  assigned_to: "Claude Code (Tactical Domain)"
  target_date: ""
  approach: >
    Author framework/ai/src/govwatch.py and requirements-govwatch.txt per
    design-govwatch.md v0.1. Coupled change document (change-7c1d9e02)
    specifies build steps and the deliverable at framework/ai/src/govwatch.py.
  change_ref: "change-7c1d9e02"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Traceability

```yaml
traceability:
  design_refs:
    - "dev/design/design-govwatch.md"
  change_refs:
    - "change-7c1d9e02"   # pending creation
  test_refs: []
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-10 | William Watson | Initial enhancement issue for govwatch implementation |
| 1.1 | 2026-06-10 | William Watson | Set change coupling (change-7c1d9e02); deliverable is framework/ai/src/govwatch.py (removed dev/ staging language) |
| 1.2 | 2026-06-15 | William Watson | Resolved: govwatch.py deliverable verified present in framework/ai/src/; closed |

---

Copyright (c) 2026 William Watson. MIT License.
