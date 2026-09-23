Created: 2026 September 23

```yaml
issue_info:
  id: "issue-07087e91"
  title: "propagate.sh leaves renamed files behind and silently does nothing when non-interactive"
  date: "2026-09-23"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-07087e91"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/todo.md propagate.sh defects (2026-09-22); eb782f83 strategic audit F-10"
  description: >
    Found while regenerating dev/smoke/ai/ after the eb782f83 migration. Both
    defects gate the deferred propagation of governance v10.x to downstream
    projects pinned at v9.16.

affected_scope:
  components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
  designs: []
  version: "governance 10.2"

behavior:
  expected: >
    After propagation the target ai/ matches the source, apart from
    project-local files; a non-interactive run either applies or fails loudly.
  actual: >
    (1) rsync runs without --delete, so a renamed or retired source file keeps
    its old name in the target: propagating v10.x would leave fifteen template
    files where eight belong. (2) The confirmation prompt reads stdin; under
    set -euo pipefail a non-TTY stdin exits 1 after the preview and before the
    apply, reporting what it would do and then doing nothing. (3) A major
    governance version change, when renames occur, is not distinguished from a
    routine update.
  impact: "Downstream v10.x propagation (backlog §6.0) cannot proceed safely."

analysis:
  root_cause: "The script was written for additive updates under one governance major version."
  technical_notes: >
    Audit F-03 (scheme-marker gate) and F-10 (bin/ in refuse_paths) were
    remediated in 097d6ea under change-9b8f1c47; they are not reopened here.

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5) — direct implementation"
  target_date: "2026-09-23"
  approach: "rsync --delete with the exclude list as protection; --yes flag; loud non-TTY failure; major-version guard."
  change_ref: "change-07087e91"
  resolved_date: "2026-09-23"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "rsync --delete, --yes, --allow-major and non-TTY failure under change-07087e91."

verification:
  verified_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: "See change-07087e91 verification.test_results."
  closure_notes: "Closed at operator direction; audit waived and macOS not exercised, recorded in change-07087e91 operator_closure_2026_09_23."

traceability:
  design_refs: []
  change_refs:
    - "change-07087e91"
  test_refs: []

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial issue from backlog §3.0 items 2–5"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Resolved under change-07087e91; awaiting closure"
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
