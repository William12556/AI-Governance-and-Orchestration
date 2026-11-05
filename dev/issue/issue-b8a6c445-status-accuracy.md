Created: 2026 November 5

```yaml
issue_info:
  id: "issue-b8a6c445"
  title: "Status accuracy: engine runs shown as running after they end; prompt match always fails; duplicated results; closed-path filter; stale alert heading"
  date: "2026-11-05"
  status: "open"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-b8a6c445"
    change_iteration: 1

source:
  origin: "code_review"  # strategic audit audit-caab2052
  description: >
    Remediation group 2 of dev/audit/audit-caab2052-static-code-2026-10-27.md
    (§10.0, §14.0): M-04, M-05, L-07, L-08 and L-15, with the OQ-02 citation
    correction at overwatch.py:828. Operator decision 2026-11-05 (§14.0): the
    engine writes one run record, run.json, which Overwatch reads for the
    engine status and the FR-02-06 prompt match. Findings re-checked by the
    planner against 695ad06.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "scope", file_path: "ai/engine/src/scope.py" }
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py" }
  designs:
    - { design_ref: "design-project-overwatch §4.0 (Data Model), §5.0 (Components), §7.1 (Monitoring Panel), §8.4" }
    - { design_ref: "design-14e05e35 §7.0 (signal files), §11.0 (Error Handling)" }
  version: "governance 12.7; engine and webui at 695ad06"

reproduction:
  prerequisites: "A project with ai/state/; Overwatch run with --project <root>"
  steps:
    - "M-04: run the engine to any exit that writes neither BLOCKED.md nor .complete (context-budget abort, declined continuation after max iterations, review-phase failure, --duration limit, an early return after setup_logging), then scan with Overwatch"
    - "M-05: open a prompt in ai/workspace/prompt/ and run the engine on it; scan with Overwatch"
    - "L-07: place one result document in ai/workspace/test/result/; scan"
    - "L-08: place the project under a directory named closed/; scan"
    - "L-15: open ai/dashboard-alerts.md after a scan"
  frequency: "always, under the stated condition"
  error_output: "M-04: engine status RUNNING with no engine process. M-05: WARNING FR-02-06 'engine task.md does not reference any open prompt document' while the engine runs that prompt"

behavior:
  expected: >
    Overwatch shows RUNNING only while an engine process runs, and shows
    that a run has ended, with its exit code, when it ended without SHIP or
    BLOCKED. FR-02-06 is raised only when the engine's task is not an open
    prompt. Each document appears once. Only closed/ folders inside the
    workspace hide documents. The alert file names the current tool.
  actual: >
    M-04: status is RUNNING whenever task.md exists and neither BLOCKED.md
    nor .complete does; the engine writes task.md at every start and only
    reset removes it, and five exit paths write neither marker. M-05: the
    match uses the first non-empty line of task.md, which is always the
    runtime header '[ENGINE RUNTIME CONTEXT]', so it never succeeds while a
    prompt is open. L-07: result documents are scanned under both test/ and
    test/result/. L-08: 'closed' is tested against the absolute path. L-15:
    the alert file is headed '# govwatch alerts'. OQ-02: the AlertWriter
    docstring cites CON-07 for the write permission; the basis is CON-01 and
    NFR-01 (requirements-0c6aedee v0.6).
  impact: "The operator cannot tell from Overwatch whether a run needs attention; a false warning appears on every prompt run; document counts and the FR-02-05 count are doubled for results."
  workaround: "Read the run log's last line ('engine end rc=N') or engine-mcp engine_status."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    M-04: Overwatch infers 'running' from the presence of task.md
    (overwatch.py:466-473); the engine records no run end. engine-mcp avoids
    the defect with a pid check on mcp-run.json, which only engine-mcp runs
    write. M-05: task_ref is the first line of task.md (overwatch.py:483-489);
    the runtime header is prepended at orchestrator.py:2729-2736 before the
    write at :2739. L-07: CLASS_DIRS maps test to test/ and result to
    test/result/ (overwatch.py:52-53) and the scan uses rglob (:403). L-08:
    "closed" in filepath.parts (overwatch.py:405). L-15: overwatch.py:856.
    OQ-02: overwatch.py:828.
  technical_notes: >
    Line numbers at 695ad06. requirements-0c6aedee FR-01-01 and FR-01-02 and
    design-project-overwatch §4.0, §5.0 state that the state-reading logic
    and ComplianceEngine were ported from govwatch unmodified; that was the
    FR-01 port constraint, and this issue changes both. The planner amends
    those statements after review. A stale BLOCKED.md left by an earlier run
    is not cleared at loop start (orchestrator.py:2026-2029); this issue does
    not change that.

resolution:
  approach: "See change-b8a6c445."
  change_ref: "change-b8a6c445"

traceability:
  design_refs: ["design-project-overwatch", "design-14e05e35"]
  change_refs: ["change-b8a6c445"]

notes: "Audit references: audit-caab2052 M-04, M-05, L-07, L-08, L-15, OQ-02 (§14.0 operator decisions, 2026-11-05)."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-caab2052 remediation group 2"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
