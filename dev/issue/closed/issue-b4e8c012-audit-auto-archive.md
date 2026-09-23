Created: 2026 June 17

```yaml
issue_info:
  id: "issue-b4e8c012"
  title: "AEL audit loop does not auto-archive output artifacts on SHIP"
  date: "2026-06-17"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-b4e8c012"
    change_iteration: 1

source:
  origin: "requirement_change"
  description: >
    After an audit loop SHIPs, audit-index.md and audit-report.md remain in
    ai/state/ralph/ and must be manually copied to ai/workspace/audit/ with
    canonical naming. This is an error-prone manual step that should be
    automated.

affected_scope:
  components:
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
  version: "current"

reproduction:
  prerequisites: "Audit loop run to SHIP completion."
  steps:
    - "Launch audit loop with --mode loop --task <uuid>-audit.md"
    - "Loop SHIPs successfully"
    - "Observe: audit-report.md remains in ai/state/ralph/ with no archive copy"
  frequency: "always"

behavior:
  expected: >
    On SHIP, audit-index.md and audit-report.md are automatically copied to
    ai/workspace/audit/ as audit-<uuid>-index.md and audit-<uuid>-report.md.
    UUID is derived from the --task filename.
  actual: >
    Files remain in ai/state/ralph/. Archiving requires manual cp command
    per ai/doc/guide-audit-loop.md §7.3.
  impact: "Manual step; risk of missed archiving or incorrect naming."
  workaround: "Manual cp per guide-audit-loop.md §7.3."

resolution:
  approach: >
    Add _archive_audit_artifacts() to orchestrator.py. Call from main_async
    after run_loop returns rc=0 in loop mode. Add audit-index.md and
    audit-report.md to _RESET_FILES.

verification:
  verification_steps:
    - "Run audit loop to SHIP; confirm both files appear in ai/workspace/audit/ with correct names"
    - "Run --mode reset; confirm audit-index.md and audit-report.md are cleared from state"
    - "Run standard Ralph Loop (non-audit); confirm no archive attempt is made"

notes: "UUID is extracted from --task basename via re.search(r'[0-9a-f]{8}', ...). Fallback: yyyymmdd timestamp."

version_history:
  - version: "1.0"
    date: "2026-06-17"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Resolved: auto-archive implemented and verified against source; issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
