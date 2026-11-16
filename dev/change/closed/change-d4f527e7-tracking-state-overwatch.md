Created: 2026 November 14

```yaml
change_info:
  id: "change-d4f527e7"
  title: "Engine runtime hygiene: atomic writes, audit archive without overwrite, BLOCKED log order, blocked detail only when blocked, tracking by file identity, non-regular evidence documents skipped (Stage C work item 5B-2)"
  date: "2026-11-14"
  status: "verified"  # approver: operator (one-time session exemption, 2026-11-14); implemented and verified 2026-11-14
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d4f527e7"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-d4f527e7"
  description: "Remediate dev/task.md work item 5B-2: work item 5 parts (c), (i), (m), (n) with audit-caab2052 L-10 and L-14, with the session decisions D1 to D6 of 2026-11-14."

scope:
  summary: >
    (A, L-10; D1) State files, overwatch.html, ai/dashboard-alerts.md and
    ai/approvals.yaml are written to a temporary file in the target's
    directory and moved into place with os.replace. (B, L-14; D2) The
    audit archive is written below the project root passed by the run
    and never replaces an existing archive: a later archive of the same
    work item takes the suffix -2, -3, …. (C, c; D3) The unremovable
    state entries are logged before BLOCKED.md is written. (D, i; D4)
    Overwatch sets blocked_detail only when the status is blocked. (E,
    m; D5) is_tracked_task decides containment by file identity for the
    task path as given and as resolved; task_document_error refuses a
    task whose resolved path lies outside ai/workspace/. (F, n; D6)
    _documents skips a match that is not a regular file; scan reports it
    as a warning. (G) Tests.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }  # A, B, C
    - { name: "approve", file_path: "ai/engine/src/approve.py", change_type: "modify" }  # A
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "modify" }  # E, F
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py", change_type: "modify" }  # A, D
    - { name: "tracking and state tests", file_path: "tests/engine/test_tracking_state_hygiene.py", change_type: "create" }
    - { name: "stage tests", file_path: "tests/engine/test_stages.py", change_type: "modify" }  # T3, T7, T8
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py", change_type: "modify" }  # T2, T6
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # §8.4, §11.0
    - { name: "orchestrator design", file_path: "dev/design/design-ael-orchestrator.md", change_type: "modify" }  # §4.1
    - { name: "overwatch design", file_path: "dev/design/design-project-overwatch.md", change_type: "modify" }  # §4.0
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # §5.0
    - { name: "audit loop guide", file_path: "docs/guide-audit-loop.md; ai/governance/software-engineering/doc/guide-audit-loop.md", change_type: "modify" }  # archive naming, if stated there
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["8.4 Pre-run Check", "11.0 Error Handling"] }
    - { design_ref: "design-ael-orchestrator", sections: ["4.1 State Files"] }
    - { design_ref: "design-project-overwatch", sections: ["4.0 Data Model"] }
  out_of_scope:
    - "engine-mcp (ai/engine/mcp/server.py), which already refuses a task outside ai/workspace/"
    - "Reviewer and reset modes of the CLI pre-run check"
    - "The task-stage prefix other than prompt (audit-4b0a5592 F-03; transferred to design-63c98596 §10.2)"
    - "Log files, context-budget.md and the appends to BLOCKED.md and the audit report (not named by L-10)"
    - "fsync of the temporary file (durability across power loss is not part of L-10)"
    - "Confirming the letter-case behaviour on macOS (deferred to the operator)"

rational:
  problem_statement: "See issue-d4f527e7."
  proposed_solution: "One small write-then-replace helper per component; a project-root parameter and a free-name search for the archive; two statements reordered; one condition in Overwatch; samestat against the workspace for the ancestors of the task path; a regular-file test in the document scan."
  alternatives_considered:
    - option: "A shared atomic-write helper in ai/core/"
      reason_rejected: "ai/core/ is reserved and its opening belongs to design-63c98596 (L-17 transferred); three short local helpers keep the components independent"
    - option: "L-14: refuse a second archive"
      reason_rejected: "The audit run has already reached SHIP; refusing would lose the second report. A numbered name keeps both"
    - option: "(m): compare with os.path.normcase"
      reason_rejected: "normcase does not fold case on macOS; file identity handles case and symlinks together (audit-4b0a5592 F-02 recommendation)"
    - option: "(n): report a non-regular match as a work-item anomaly"
      reason_rejected: "An anomaly makes the work item's path undetermined and would refuse the approved prompt because of an unrelated entry; a scan warning reports it without blocking"
  benefits:
    - "Concurrent readers never see a partial file"
    - "No workspace task path, by any spelling or link, reaches a loop or worker run without the pre-run check, and none that resolves outside ai/workspace/ runs as a tracked task"
    - "A non-regular entry in ai/workspace/ neither hangs nor crashes the scan"
  risks:
    - risk: "A state file name that is a symlink is replaced by a regular file instead of being written through"
      mitigation: "The engine clears non-regular state entries before use (change-82dbf16a iteration 5); writing through a worker-created link was not intended behaviour"
    - risk: "An approved prompt that is itself a symlink to a file outside ai/workspace/ is now refused (exit 3)"
      mitigation: "Intended (audit-4b0a5592 F-01); the refusal names the expected location"
    - risk: "On a case-insensitive file system an approved prompt passed with different letter case is tracked and then refused, because task_document_error compares resolved path strings"
      mitigation: "Fails closed; the refusal names the expected path. Recorded in the guide; to be confirmed on macOS by the operator"

technical_details:
  current_behavior: "See issue-d4f527e7 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) orchestrator._write_atomic(path, content): write to
    '<dir>/.<name>.<pid>.tmp', os.replace onto path; on any failure
    remove the temporary file and re-raise. write_state uses it; the
    name itself is replaced, so a symlink at that name is not followed.
    (A2) overwatch._write_text_atomic(path, content), the same pattern,
    applied to the resolved path so that an output that is a symlink is
    written through as before; AlertWriter.write and HtmlRenderer.write
    use it and keep their error handling. (A3) approve._write_atomic for
    the write of ai/approvals.yaml and for writing the prior bytes back,
    on the resolved path. (B) _archive_audit_artifacts(state_dir,
    task_path, log, project_root=None): the folder is
    <project_root>/ai/workspace/audit, project_root defaulting to
    os.getcwd(); main_async passes the run's project root. The target
    names are audit-<uid>-index.md and audit-<uid>-report.md when
    neither exists; otherwise the smallest n >= 2 for which neither
    audit-<uid>-index-<n>.md nor audit-<uid>-report-<n>.md exists; a
    warning is logged when n is used. (C) In run_loop, at loop start and
    after the gates, log.error('BLOCKED: state files could not be
    removed: …') precedes write_state(…, 'BLOCKED.md', …). (D)
    _read_engine_state: blocked_detail = blocked_content when status ==
    'blocked', else None. (E1) stages._in_workspace(project_root, path):
    True when the workspace directory exists and os.path.samestat
    matches it for path or any ancestor of path. is_tracked_task: the
    path exists and _in_workspace holds for os.path.abspath(task_path)
    or os.path.realpath(task_path). (E2) task_document_error returns the
    existing refusal when the resolved task path is not _in_workspace.
    (F) _documents(project_root, manifest, skipped=None): a globbed
    match for which os.path.isfile is False is not listed; its
    project-relative path is appended to skipped when given. scan adds
    the warning '<path>: not a regular file; ignored'.
  implementation_approach: "Implemented by the autonomous session of 2026-11-14 (worker and reviewer; prompt-cf99f3f3) on the session branch. No T03 prompt (report-b3a503a2 §5.0 decision 1); the acceptance criteria are testing_requirements below."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A1 atomic state writes; B archive root and free name; C log order"
      functions_affected: ["_write_atomic (new)", "write_state", "_archive_audit_artifacts", "run_loop", "main_async"]
    - component: "approve"
      file: "ai/engine/src/approve.py"
      change_summary: "A3 atomic write and write-back"
      functions_affected: ["_write_atomic (new)", "approve"]
    - component: "stages"
      file: "ai/engine/src/stages.py"
      change_summary: "E containment by file identity; F regular files only"
      functions_affected: ["_in_workspace (new)", "is_tracked_task", "task_document_error", "_documents", "scan"]
    - component: "overwatch"
      file: "ai/webui/src/overwatch.py"
      change_summary: "A2 atomic outputs; D blocked detail"
      functions_affected: ["_write_text_atomic (new)", "AlertWriter.write", "HtmlRenderer.write", "Scanner._read_engine_state"]
  interface_changes:
    - interface: "engine CLI --task in loop and worker mode"
      change_type: "behavior"
      details: "A path in ai/workspace/ by file identity is tracked; a task that resolves outside ai/workspace/ is refused with exit 3"
      backward_compatible: "yes for approved prompts that are regular files in ai/workspace/prompt/; no for a symlink there that points outside, which ran untracked"
    - interface: "audit archive names"
      change_type: "behavior"
      details: "A second archive of a work item is audit-<uid>-index-2.md and audit-<uid>-report-2.md"
      backward_compatible: "yes for the first archive"
    - interface: "stages.py --json and work_status warnings"
      change_type: "behavior"
      details: "New warning '<path>: not a regular file; ignored'"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library, PyYAML and git only" }

testing_requirements:
  test_approach: "pytest with tmp_path projects and git repositories; no network (NFR-06). New file tests/engine/test_tracking_state_hygiene.py (T1, T4, T5); T3, T7 and T8 in tests/engine/test_stages.py, which holds the repository fixtures; T2 and T6 in tests/webui/test_overwatch.py."
  test_cases:
    - { scenario: "T1 (A1): write_state with a failing os.replace, a normal write, and a symlink at the name; test_t1_write_state_is_atomic, test_t1_write_state_replaces_a_symlink", expected: "the earlier content stays and no temporary file is left; the new content is complete; the link target is untouched" }
    - { scenario: "T2 (A2): AlertWriter.write and HtmlRenderer.write with a failing os.replace, and through a symlinked output; test_t2_overwatch_outputs_are_atomic, test_t2_overwatch_output_symlink_is_written_through", expected: "earlier content stays, the error is reported as before, no temporary file; the link stays a link and its target has the new content" }
    - { scenario: "T3 (A3): approve.py writes through os.replace and leaves no temporary file, on success and after a failed commit; test_t3_approve_writes_atomically", expected: "os.replace called for ai/approvals.yaml; directory holds no '.tmp' entry; a failed commit restores the prior bytes" }
    - { scenario: "T4 (B): two archives for one work item, and a run whose working directory is not the project root; test_t4_audit_archive_does_not_overwrite, test_t4_audit_archive_uses_the_project_root", expected: "the first pair is unchanged and the second is -2; the files are below the given root" }
    - { scenario: "T5 (C): unremovable entries at loop start and after the gates; reset_state with an unremovable entry; a real unremovable entry (read-only state directory, skipped for root); test_t5_blocked_is_logged_before_the_file[start|gates], test_t5_reset_state_returns_1, test_t5_real_unremovable_entry", expected: "the log call precedes the BLOCKED.md write; return value 1; BLOCKED naming the entry" }
    - { scenario: "T6 (D): a BLOCKED.md older than the record's start with status ended, with a live run, and a current one; test_d_blocked_detail_only_when_blocked", expected: "blocked_detail None for ended and running, the file content for blocked; the page shows no 'Blocked:' line unless blocked" }
    - { scenario: "T7 (E): is_tracked_task and a loop run for an outward symlink in ai/workspace/prompt/, the approved prompt replaced by an outward link, a file in a sibling ai/workspace-x/, a project reached through a symlinked root, and a differently cased path (case-insensitive file systems only); test_t7_tracking_by_file_identity, test_t7_outward_link_is_refused[plain|replaced], test_t7_case_variant_is_tracked", expected: "tracked: link, replaced prompt, symlinked root, case variant; not tracked: sibling; the two link runs exit 3 with nothing written to the state directory" }
    - { scenario: "T8 (F): a FIFO at ai/workspace/issues/issue-<uuid>-x.md and a directory at ai/workspace/prompt/prompt-<uuid>-zz.md beside the approved prompt; test_t8_non_regular_documents_are_skipped[fifo|directory], test_t8_prerun_passes_beside_a_non_regular_entry", expected: "scan returns within the test timeout with the warning; prerun_missing for the approved prompt returns []" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline on Linux; macOS suite run by the operator after the session, including the case-variant test"
    - "Mutations: in-place write restored in write_state, Overwatch and approve (T1 to T3); overwrite restored and os.getcwd() restored in the archive (T4); log after the write (T5); blocked_detail unconditional (T6); string comparison restored in is_tracked_task, abspath candidate removed, resolved-path refusal removed (T7); regular-file test removed (T8)"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "Follow-up audit by an independent session (P02.8.2): deferred to the operator"

implementation:
  effort_estimate: "3 hours"
  implementation_steps:
    - { step: "Failing tests, then source", owner: "session (worker)" }
    - { step: "Independent review (prompt-cf99f3f3 §8.4)", owner: "session (fresh reviewer subagent)" }
    - { step: "Design and guide updates", owner: "session" }
    - { step: "macOS suite, letter-case confirmation; follow-up audit (P02.8.2)", owner: "operator, after the session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation of work item 8e. No configuration change."

traceability:
  related_changes:
    - { change_ref: "change-4b0a5592", relationship: "follows up (audit-4b0a5592 F-01, F-02, F-04)" }
    - { change_ref: "change-86c958dd", relationship: "follows up (audit-86c958dd F-01)" }
    - { change_ref: "change-b8a6c445", relationship: "follows up (run.json atomic write pattern)" }
    - { change_ref: "change-82dbf16a", relationship: "follows up (follow-up 5 §6.0 notes 1, 3)" }
  related_issues:
    - { issue_ref: "issue-d4f527e7", relationship: "source" }

notes: "Session decisions 2026-11-14 under the operator's one-time exemption (prompt-cf99f3f3 §1.0 item 5): D1 temporary file and os.replace, three local helpers, state file names replaced and output links written through; D2 numbered archive names, project root as a parameter; D3 log first; D4 blocked detail only when blocked; D5 file identity for the given and the resolved path, and a task that resolves outside ai/workspace/ is refused; D6 non-regular matches skipped with a scan warning."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Approved as drafted. Approver: operator (one-time session exemption, 2026-11-14). Test file list amended before implementation: T3, T7 and T8 in tests/engine/test_stages.py"]
  - version: "1.2"
    date: "2026-11-14"
    changes:
      - "Implemented on branch claude/blissful-keller-mn2avc from a5a3656: source 98214f8, tests 3c3b870 (report-d4f527e7 v1.0). Status implemented"
      - "788 passed, 2 skipped at the unit baseline; 811 passed, 4 skipped after (Linux; 23 new cases, 2 new skips: root and case-sensitive file system). Mutations M1 to M17 caught"
      - "linter.py dev 0 errors, 113 warnings; protocol_checker.py dev 0 errors, 20 warnings"
      - "design-14e05e35 v1.31 §8.4, §11.0; design-ael-orchestrator v0.13 §4.1; design-project-overwatch v0.11 §4.0; guide-engine-operations v1.34 §2.0, §5.0. The guide-audit-loop copies needed no edit"
  - version: "1.3"
    date: "2026-11-14"
    changes:
      - "Review by a fresh reviewer subagent (prompt-cf99f3f3 §8.4): round 1 REVISE (the atomic helpers did not keep the mode of an existing file; approvals.yaml encoding; one count in the report), corrected in 0a3b509 (source), af46991 (tests) and report-d4f527e7 v1.1; round 2 SHIP. Not an audit"
      - "Added to proposed_behavior A by the review: an existing regular file keeps its permission bits; ai/approvals.yaml is encoded with the locale's preferred encoding, as before"
      - "Status verified; closed with issue-d4f527e7 and report-d4f527e7 (P00.14.4). Approver: operator (one-time session exemption, 2026-11-14)"
      - "Linux cloud suite 812 passed, 4 skipped; macOS operator suite (including the letter-case test and the real unremovable entry test, skipped on Linux as root) and P02.8.2 follow-up audit deferred to after the session (report-b3a503a2 §6.0)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
