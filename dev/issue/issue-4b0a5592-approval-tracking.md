Created: 2026 November 7

```yaml
issue_info:
  id: "issue-4b0a5592"
  title: "Approval and tracking: CLI tracks by name, non-regular workspace paths untracked, approve.py leaves state after a failed commit, approvals unreadable in a nested project"
  date: "2026-11-07"
  status: "resolved"  # change-4b0a5592 implemented 2026-11-07 (P03.7)
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-4b0a5592"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 group 4; audit-14e05e35 follow-up 5 F5-01
  description: >
    Stage C work item 4 (dev/task.md): audit-caab2052 L-04, L-05 and L-06
    (§10.0 group 4) and audit-14e05e35 follow-up 5 F5-01, with the
    operator decisions of 2026-11-07 (D1 to D3, see change-4b0a5592).

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }  # L-04
    - { name: "stages", file_path: "ai/engine/src/stages.py" }  # L-04, F5-01, L-06
    - { name: "approve", file_path: "ai/engine/src/approve.py" }  # L-05
  designs:
    - { design_ref: "design-14e05e35 §8.3 Protection, §8.4 Pre-run Check" }
    - { design_ref: "requirements-14e05e35 FR-08-05" }
  version: "main 1f02370"

reproduction:
  prerequisites: "main 1f02370; a project that is a git repository with the software-engineering governance model"
  steps:
    - "L-04: run the engine in loop mode with --task ai/workspace/prompt/my-task.md (a regular T03 prompt whose name does not match prompt-<uuid>-); the run starts without the pre-run check"
    - "F5-01: create a directory or a FIFO at ai/workspace/prompt/prompt-<uuid>-x.md and run the engine in loop mode with it as --task; the run starts with the path string as task text and no write scope, and the console says the prompt is outside ai/workspace/"
    - "L-05: install a pre-commit hook that exits 1 and run approve.py <uuid> prompt; then remove the hook and run it again"
    - "L-06: place the project in a subdirectory of a git repository, approve a stage with approve.py and run the engine with the approved prompt"
  frequency: "always, under the stated condition"
  error_output: "L-05: 'git failed (commit -q): ' with an empty detail when the hook prints nothing. L-06: every tracked run refused as unapproved (exit 3)."

behavior:
  expected: >
    L-04, F5-01: a task path whose resolved location is in ai/workspace/
    is tracked whatever its name or type (design-14e05e35 §8.4); in loop
    and worker mode it runs only when it is the approved prompt of its
    work item, otherwise it is refused with exit 3 before any state
    change. L-05: a failed git add or commit leaves ai/approvals.yaml and
    its index entry as they were, and the message reports git's output.
    L-06: approvals are read from the project's own ai/approvals.yaml in
    HEAD wherever the project lies in the repository.
  actual: >
    L-04: the CLI tracks only names matching ^prompt-[0-9a-f]{8}-
    (orchestrator.py _work_item_uuid, and '_tracked = bool(work_item) and
    ...'). F5-01: stages.is_tracked_task returns False for any path that
    is not a regular file. L-05: approve.py writes and stages the file
    before the commit and returns on a failure without restoring it; a
    retry appends a second entry (parse_approvals takes the last, so the
    result stays correct); the detail can be empty. L-06:
    committed_approvals runs 'git show HEAD:ai/approvals.yaml', which git
    resolves from the repository root, so it returns {} in a nested
    project.
  impact: "L-04, F5-01: a workspace prompt can run without the pre-run check and, for a non-regular path, without a write scope. L-05: a staged file and a duplicate entry are left behind; the operator gets no reason. L-06: approvals in a nested project are never seen; runs are refused (fails closed)."
  workaround: "Name prompts prompt-<uuid>-<name>.md and pass only regular files; restore ai/approvals.yaml by hand after a failed approve.py; keep projects at a repository root."

environment:
  os: "platform-independent (FIFO case: POSIX)"

analysis:
  root_cause: >
    Line numbers at main 1f02370. L-04: orchestrator.py:2541-2549
    (_PROMPT_UUID_RE, _work_item_uuid), :2660 (work_item), :2672 (_tracked
    requires work_item). F5-01: stages.py:323-329 (is_tracked_task
    returns False unless os.path.isfile); the warning at
    orchestrator.py:2685-2687 then names the wrong reason. L-05:
    approve.py:77-85 (write, add, commit; return on failure without
    restoring; detail is stderr or stdout, both empty when the hook
    prints nothing). L-06: stages.py:128 (f"HEAD:{APPROVALS_FILE}");
    'HEAD:./<path>' resolves relative to the -C directory.
  technical_notes: >
    engine-mcp already refuses each case (ai/engine/mcp/server.py:96-112
    _tracked_task_error: not a regular file, outside ai/workspace/, or a
    name other than prompt-<uuid>-<name>.md), so only direct CLI runs are
    affected by L-04 and F5-01. The task file is read only when
    os.path.isfile is true (orchestrator.py:2669-2671), so a FIFO is never
    opened. stages.py has one HEAD:<path> reference; its other git calls
    use pathspecs, which git resolves relative to -C. design-14e05e35
    §8.3 names 'git show HEAD:ai/approvals.yaml' and needs the new form.

resolution:
  approach: "To be defined in change-4b0a5592."
  change_ref: "change-4b0a5592"

traceability:
  design_refs: ["design-14e05e35 §8.3", "design-14e05e35 §8.4", "requirements-14e05e35 FR-08-05"]
  change_refs: ["change-4b0a5592"]

notes: "Audit references: audit-caab2052 L-04, L-05, L-06, §10.0 group 4; audit-14e05e35 follow-up 5 F5-01 (dev/audit/closed/audit-14e05e35-followup5-2026-10-01.md). Operator decisions 2026-11-07: D1 track by location whatever the type, D2 restore the file and index entry after a failed commit, D3 HEAD:./ path."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial issue for Stage C work item 4 (audit-caab2052 group 4)"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Status resolved: change-4b0a5592 implemented (P03.7)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
