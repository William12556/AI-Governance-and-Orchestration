Created: 2026 November 7

```yaml
change_info:
  id: "change-4b0a5592"
  title: "Approval and tracking: track workspace tasks by location, restore approvals after a failed commit, read approvals in a nested project (Stage C work item 4)"
  date: "2026-11-07"
  status: "approved"  # operator approval 2026-11-07
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-4b0a5592"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-4b0a5592"
  description: "Remediate audit-caab2052 L-04, L-05, L-06 and audit-14e05e35 follow-up 5 F5-01 with the operator decisions of 2026-11-07 (D1 to D3)."

scope:
  summary: >
    (A, L-04 and F5-01; D1) A --task path whose resolved location is
    ai/workspace/ or lies inside it is tracked whatever its name or file
    type. In loop and worker mode a tracked task runs only when it is the
    approved prompt of its work item; otherwise the run is refused with
    exit 3 before any state change, by the existing pre-run rules. (B,
    L-05; D2) When git add or git commit fails, approve.py restores
    ai/approvals.yaml to its content before the call (or removes it if the
    call created it), resets its index entry to HEAD, and reports git's
    output or the exit code. (C, L-06; D3) committed_approvals reads
    HEAD:./ai/approvals.yaml, which resolves from the project directory.
    (D) Tests.
  affected_components:
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "modify" }  # A, C
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }  # A
    - { name: "approve", file_path: "ai/engine/src/approve.py", change_type: "modify" }  # B
    - { name: "stage tests", file_path: "tests/engine/test_stages.py", change_type: "modify" }  # D
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner: §8.3, §8.4
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner: §5.0
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["8.3 Protection", "8.4 Pre-run Check"] }
  out_of_scope:
    - "engine-mcp (ai/engine/mcp/server.py), which already refuses every case"
    - "reviewer and reset modes"
    - "Restoring an index entry the operator had staged for ai/approvals.yaml before the call (the entry is reset to HEAD)"
    - "Overwatch"

rational:
  problem_statement: "See issue-4b0a5592."
  proposed_solution: "Track by resolved location only and let the existing pre-run rules refuse what is not the approved prompt; make approve.py leave no state behind on a git failure; resolve the approvals path from the project directory."
  alternatives_considered:
    - option: "Track by name and location together (current behaviour), adding a type check only"
      reason_rejected: "Operator decision D1 2026-11-07: design-14e05e35 §8.4 tracks by location; a workspace prompt with another name would still run unchecked"
    - option: "Write the approval to a temporary index or commit before writing the working file"
      reason_rejected: "More moving parts for a low finding; restoring the file and the index entry is sufficient (D2)"
    - option: "Run git show from the repository root with the project's prefix"
      reason_rejected: "HEAD:./<path> gives the same result with one character (D3)"
  benefits:
    - "No workspace task reaches a loop or worker run without the pre-run check"
    - "A failed approval leaves the repository as it was and says why"
    - "Approvals work in a project nested in a larger repository"
  risks:
    - risk: "A non-prompt file in ai/workspace/ passed as --task in loop or worker mode is now refused (exit 3)"
      mitigation: "Intended by design-14e05e35 §8.4; the refusal names the expected prompt path"
    - risk: "An index entry the operator staged for ai/approvals.yaml before a failed approve.py is reset to HEAD"
      mitigation: "The working file keeps its content before the call; recorded in the guide"

technical_details:
  current_behavior: "See issue-4b0a5592 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) stages.is_tracked_task(project_root, task_path) is True when
    task_path is non-empty, os.path.exists(task_path) is True (any file
    type), and its resolved path equals the resolved ai/workspace/ or
    starts with it followed by a separator; symlinks stay resolved (L-01).
    (A2) orchestrator.main_async: _tracked = ST.is_tracked_task(cwd,
    args.task), independent of work_item. In loop and worker mode a
    tracked task goes through ST.prerun_missing as today; with no
    work-item UUID in its name the refusal header names the task path
    instead of the work item. Exit 3 before any state change. The task
    file is still read only when os.path.isfile is True, so a FIFO is
    never opened. The 'outside ai/workspace/ — not tracked' warning is
    unchanged and now appears only for a path outside ai/workspace/. (B)
    approve.approve: before writing, record whether ai/approvals.yaml
    exists and its bytes. When git add or git commit returns non-zero,
    write the bytes back (or remove the file if it did not exist), then
    run git reset -q -- ai/approvals.yaml, falling back to git rm -q
    --cached --ignore-unmatch -- ai/approvals.yaml when HEAD does not
    exist. Return 1 with 'git failed (<add|commit>): <stderr or stdout,
    stripped>' or, when both are empty, 'git failed (<add|commit>): exit
    code <n>'; if the restoration fails, append '; ai/approvals.yaml could
    not be restored: <detail>'. (C) stages.committed_approvals: git show
    HEAD:./ai/approvals.yaml. (D) Tests in tests/engine/test_stages.py.
  implementation_approach: "Claude Code cloud session per prompt-4b0a5592 after approval, on a session branch. The planner updates design-14e05e35 §8.3 and §8.4 and guide-engine-operations §5.0 after review."
  code_changes:
    - component: "stages"
      file: "ai/engine/src/stages.py"
      change_summary: "A1 tracking by location, any type; C HEAD:./ path"
      functions_affected: ["is_tracked_task", "committed_approvals"]
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A2 tracked independent of the UUID name; refusal header without a UUID"
      functions_affected: ["main_async"]
    - component: "approve"
      file: "ai/engine/src/approve.py"
      change_summary: "B restore file and index entry after a failed git step; non-empty detail"
      functions_affected: ["approve"]
  interface_changes:
    - interface: "engine CLI --task in loop and worker mode"
      change_type: "behavior"
      details: "Any existing path in ai/workspace/ is tracked; one that is not the approved prompt is refused with exit 3"
      backward_compatible: "yes for approved prompts named prompt-<uuid>-<name>.md; no for other workspace paths, which ran untracked"
    - interface: "approve.py exit 1 on a git failure"
      change_type: "behavior"
      details: "File and index entry restored; detail never empty"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library, PyYAML and git only" }

testing_requirements:
  test_approach: "pytest with tmp_path git repositories; no network (NFR-06)."
  test_cases:
    - { scenario: "A1: is_tracked_task for a regular file, a directory and a FIFO inside ai/workspace/, ai/workspace/ itself, a missing path, a path outside, free text, a symlink into ai/workspace/", expected: "True for the first four and the symlink; False otherwise" }
    - { scenario: "A2: loop and worker runs with ai/workspace/prompt/my-task.md and with ai/workspace/notes.md", expected: "exit 3; the refusal names the task path; no state written" }
    - { scenario: "A2: a directory and a FIFO at ai/workspace/prompt/prompt-<uuid>-x.md; ai/workspace/ itself", expected: "exit 3; no state written; the FIFO case returns without blocking" }
    - { scenario: "A2: prompt-<uuid>-x.md outside ai/workspace/", expected: "the existing not-tracked warning; no exit 3" }
    - { scenario: "B: approve.py with a pre-commit hook that prints to stderr and exits 1, with ai/approvals.yaml committed and with no ai/approvals.yaml; then the hook removed and approve.py run again", expected: "exit 1 with the hook output in the message; file bytes as before (or absent); git status --porcelain for the file empty; the retry gives exit 0 and one entry for the pair" }
    - { scenario: "B: a hook that exits 1 silently", expected: "message ends 'exit code 1'" }
    - { scenario: "C: a project in a subdirectory of a git repository: approve.py, committed_approvals, prerun_missing for the approved prompt", expected: "the entry is found; prerun_missing returns []" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline; macOS suite run by the operator"
    - "Mutations: the isfile test restored, the work_item condition restored, the file restore removed, the index reset removed, the './' removed, the workspace-equality case removed: each fails a named test"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "2-3 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-4b0a5592)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §8.3, §8.4; guide-engine-operations §5.0", owner: "planner" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation after Stage C work item 6. No configuration change. No live engine check is needed: the change affects the pre-run check, which tests cover offline."

traceability:
  related_changes:
    - { change_ref: "change-ee5357ec", relationship: "follows up (stage tracking and approvals)" }
    - { change_ref: "change-82dbf16a", relationship: "follows up (task read once; F4-02)" }
  related_issues:
    - { issue_ref: "issue-4b0a5592", relationship: "source" }

notes: "Operator decisions 2026-11-07: D1 track every existing path in ai/workspace/ whatever its name or type, refused unless it is the approved prompt; D2 restore the file and reset its index entry after a failed git step, with a non-empty detail; D3 HEAD:./ai/approvals.yaml."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Approved by the operator as drafted; implementation per prompt-4b0a5592"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
