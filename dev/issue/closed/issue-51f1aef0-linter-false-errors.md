Created: 2026 September 23

```yaml
issue_info:
  id: "issue-51f1aef0"
  title: "linter.py reports false errors on valid dev/ documents"
  date: "2026-09-23"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-51f1aef0"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "python3 ai/ael/src/linter.py dev — 99 errors after protocol_checker reached 0 on 2026-09-23"
  description: >
    linter.py rejects documents that conform to the current templates and
    conventions. Five independent defects account for 95 of the 99 dev/
    errors; the remaining 4 are gitignored eval probes outside governance.

affected_scope:
  components:
    - name: "linter"
      file_path: "ai/ael/src/linter.py"
  designs: []
  version: "governance 10.2"

behavior:
  expected: "A document conforming to its T0x template and the P00 naming convention produces no ERROR."
  actual: >
    (1) check_structure requires a markdown 'Version History' heading; YAML-schema
    documents carry a version_history: key instead (T06, T07 and others define it).
    (2) VALID_CLASSES omits 'proposal' and 'report', both established dev/ classes.
    (3) The t03_issue type enum omits 'enhancement' and 'requirement_change',
    which the T06 template lists as valid.
    (4) Coupling resolution indexes only YAML-bearing documents, so a change whose
    coupled issue is a prose document (issue-a5c8d2f1, issue-f3c7a1e9) is reported
    as referencing a missing document.
    (5) Prompt documents are required to carry version history, but the T03
    template defines no version_history field; prompts are single-use and
    versioned by their iteration field and git.
  impact: "The linter cannot serve as a CI gate (backlog §2.4) while valid documents fail it."

analysis:
  root_cause: "Linter rules predate the current template set and the prose-document convention (governance P11.7)."
  technical_notes: "Simulated fix reduces dev/ errors from 99 to 4; ai/workspace unchanged at 0."

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5) — direct implementation"
  target_date: "2026-09-23"
  approach: "Correct the five rules in linter.py; no document changes."
  change_ref: "change-51f1aef0"
  resolved_date: "2026-09-23"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "Five rule corrections in linter.py under change-51f1aef0."

verification:
  verified_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: "See change-51f1aef0 verification.test_results."
  closure_notes: "Closed at operator direction; independent audit waived, recorded in change-51f1aef0 operator_closure_2026_09_23."

traceability:
  design_refs: []
  change_refs:
    - "change-51f1aef0"
  test_refs: []

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial issue from dev/ linter baseline (backlog §3.1–3.2)"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Resolved under change-51f1aef0; awaiting verification and closure"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed at operator direction; status resolved -> closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
