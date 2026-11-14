Created: 2026 November 14

```yaml
issue_info:
  id: "issue-d4f527e7"
  title: "Engine runtime hygiene: non-atomic writes, audit archive overwrite, BLOCKED log order, stale blocked detail in Overwatch, tracking by path string, non-regular evidence documents"
  date: "2026-11-14"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d4f527e7"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 L-10, L-14; audit-14e05e35 follow-up 5 §6.0 notes 1, 3; audit-86c958dd F-01; audit-4b0a5592 F-01, F-02, F-04
  description: >
    Stage C work item 5B-2 (dev/task.md row d4f527e7): work item 5 parts
    (c), (i), (m) and (n), with audit-caab2052 L-10 and L-14. Raised by
    the autonomous session of 2026-11-14 (prompt-cf99f3f3,
    report-b3a503a2) under the operator's one-time exemption.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }  # L-10, L-14, (c)
    - { name: "approve", file_path: "ai/engine/src/approve.py" }  # L-10
    - { name: "stages", file_path: "ai/engine/src/stages.py" }  # (m), (n)
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py" }  # L-10, (i)
  designs:
    - { design_ref: "design-14e05e35 §8.3 Protection, §8.4 Pre-run Check" }
    - { design_ref: "design-project-overwatch §4.0 Data Model, §7.1" }
    - { design_ref: "design-ael-orchestrator §4.1 State Files" }
  version: "main 9b75595"

reproduction:
  prerequisites: "main 9b75595; for (m) and (n) a project that is a git repository with the software-engineering governance model"
  steps:
    - "L-10: read ai/state/*.txt, overwatch.html, ai/dashboard-alerts.md or ai/approvals.yaml while the engine, Overwatch or approve.py rewrites it"
    - "L-14: run two audit loops for the same work item to SHIP; run one from a directory other than the project root"
    - "(c) make a state entry unremovable at loop start and read the engine log"
    - "(i) leave a BLOCKED.md from an earlier run in the state directory and start a later run that ends without a marker, or is running"
    - "(m) place a symlink at ai/workspace/prompt/prompt-<uuid>-x.md that points outside ai/workspace/ and run the engine in loop mode with it as --task; on a case-insensitive file system, pass AI/Workspace/prompt/<name>"
    - "(n) create a FIFO at ai/workspace/issues/issue-<uuid>-x.md, or a directory at ai/workspace/prompt/prompt-<uuid>-zz.md beside the approved prompt, and run the engine with the approved prompt"
  frequency: "always, under the stated condition (L-10: inferred, medium confidence that partial reads occur in practice)"
  error_output: "(n) directory: IsADirectoryError traceback from blob_hash; FIFO: the pre-run check blocks in open()."

behavior:
  expected: >
    L-10: a reader of a state file, overwatch.html,
    ai/dashboard-alerts.md or ai/approvals.yaml sees the previous content
    or the new content, never a partial file. L-14: an audit archive is
    written below the run's project root and never replaces an earlier
    archive. (c) The log records the unremovable entries before
    BLOCKED.md is written. (i) Overwatch shows the content of BLOCKED.md
    as blocked detail only when the status is blocked. (m) A task path
    that lies in ai/workspace/ by file identity, either as given or
    resolved, is tracked; one that resolves outside ai/workspace/ is
    refused by the pre-run check. (n) An evidence document match that is
    not a regular file is skipped and reported; the scan neither blocks
    nor raises.
  actual: >
    L-10: write_state, AlertWriter.write, HtmlRenderer.write and
    approve.py truncate and rewrite in place. L-14:
    _archive_audit_artifacts copies with shutil.copy2 without an
    existence check and resolves the folder from os.getcwd(). (c)
    run_loop writes BLOCKED.md and then calls log.error at both sites.
    (i) _read_engine_state sets blocked_detail from BLOCKED.md whatever
    the status. (m) is_tracked_task compares resolved path strings, so
    an outward symlink and, on a case-insensitive file system, a
    differently cased path are untracked and start without the pre-run
    check. (n) _documents globs by name; _status opens every match and
    blob_hash reads it.
  impact: "L-10: a concurrent reader can see a partial file. L-14: the first archive of a work item is lost. (c) the log order differs from the file order. (i) the page shows ENDED or RUNNING with the failure text of an earlier run. (m) a tracked prompt replaced by an outward link runs without the pre-run check. (n) a run hangs or ends with a traceback."
  workaround: "(m), (n) keep only regular files in ai/workspace/. L-14: copy the archive before a second audit run."

environment:
  os: "platform-independent; (m) letter case: case-insensitive file systems (macOS default); FIFO cases: POSIX"

analysis:
  root_cause: >
    Line numbers at main 9b75595. L-10: orchestrator.py:689-692
    (write_state); overwatch.py:1006, :1187; approve.py:82-83, :103-104.
    L-14: orchestrator.py:590-597. (c) orchestrator.py:2120-2124,
    :2273-2277. (i) overwatch.py:599. (m) stages.py:333-340. (n)
    stages.py:194-213 (_documents), :171-175 (_status), :78-81
    (blob_hash).
  technical_notes: >
    task_document_error compares the resolved task path with the resolved
    paths of the work item's documents. A symlink inside ai/workspace/
    is itself globbed as a document, so both sides resolve to the same
    outside file and the comparison passes; tracking the link is
    therefore not sufficient, and the resolved task path must also be
    tested against the workspace. os.path.samestat on the workspace
    directory decides containment for both letter case and symlinks.
    os.path.isfile uses stat and does not open a FIFO. The run record
    run.json is already written atomically (change-b8a6c445). A state
    entry cannot be made unremovable for the root user, so the test with
    a real entry runs only for another user.

resolution:
  approach: "To be defined in change-d4f527e7."
  change_ref: "change-d4f527e7"

traceability:
  design_refs: ["design-14e05e35 §8.3", "design-14e05e35 §8.4", "design-project-overwatch §4.0", "design-ael-orchestrator §4.1"]
  change_refs: ["change-d4f527e7"]

notes: "Audit references: audit-caab2052 L-10, L-14 (§14.0, decided 2026-11-14 by the session under the one-time exemption); audit-14e05e35 follow-up 5 §6.0 notes 1 and 3 (dev/audit/closed/audit-14e05e35-followup5-2026-10-01.md); audit-86c958dd F-01; audit-4b0a5592 F-01, F-02, F-04, and X02, X04 of F-07."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial issue for Stage C work item 5B-2"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
