Created: 2026 October 01

```yaml
change_info:
  id: "change-82dbf16a"
  title: "Audit-14e05e35 remediation: verdict source, content-bound approvals, dispatch allowlist, gates and documents"
  date: "2026-10-01"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 5
  coupled_docs:
    issue_ref: "issue-82dbf16a"
    issue_iteration: 5

source:
  type: "issue"
  reference: "dev/issue/issue-82dbf16a-audit-14e05e35-remediation.md"
  description: "Remediation of audit-14e05e35 findings approved by the operator 2026-10-01 (recommendations 1–4)."

scope:
  summary: >
    H-01: review-result.txt is cleared before each review phase; the worker
    may not write the engine signal files (review-result.txt,
    review-feedback.txt, .complete, .timeout, awaiting-approval.md,
    mcp-run.json, iteration.txt, task.md, context-budget.md) in any task.
    H-03: run_phase dispatches only tools offered to the phase and no write
    tool in a review phase. H-02: approve.py records the git blob hash of each
    evidence document of the stage; the pre-run check and the stage scan at
    the loop stage report an approval whose documents changed, were added or
    removed, or that records no hashes; re-running approve.py re-approves.
    M-01: a write call with no recognised path argument is refused. M-02: an
    UNCHECKED command gate ends the run BLOCKED naming the gate; SKIPPED gates
    are listed in awaiting-approval.md. M-03: two-domain wording replaced in
    the primer (both copies), governance, overwatch, guides and profiles;
    V-08 widened to bare forms. M-04: git runs with --no-optional-locks in
    stages.py. M-05: api_key_env variables are removed from the gate
    environment. Low: L-01 and L-02 symlink resolution; L-03 writable_paths
    validated; L-05 compounds; L-06 and L-07 guide and CLAUDE.md; L-12 return
    stage in worker mode; L-13 declared deliverables in the [DELIVERABLES]
    block; L-14 UUIDs must be quoted strings; L-15 approve.py in governance;
    L-16 live report. The audit-review recipe states the verdict in the final
    response, matching the read-only review phase.
    Iteration 2 (follow-up audit F-01 to F-06): the verdict comes from the
    reviewer's final message only and REVISE feedback always from it (F-01);
    a tracked task must be an active evidence document of the stage before
    the loop stage, in the engine pre-run check and in engine-mcp through
    stages.py --task-check (F-02); blobs are keyed by path relative to
    ai/workspace/ (F-03); a write whose target is or contains a signal file
    is refused (F-04), compared case-insensitively (F-05); documents and the
    pytest gate docstring corrected, governance 12.2, design 1.7 with DI-06
    (F-06).
    Iteration 3 (second follow-up F2-01 to F2-04): the task check requires
    the resolved task path to equal one of the scanned active prompt documents
    of the work item named by the task as given; document and engine-mcp
    names are matched in full (F2-01, F2-02). review-result.txt,
    review-feedback.txt, .complete and awaiting-approval.md are cleared after
    the gates, immediately before the review phase (F2-03, F2-04).
    loop-review.yaml 1.10.0 step 5 wording; engine guide §5.0; design 1.8.
    Iteration 4 (third follow-up F3-01, F3-02): the post-gate clear runs
    before the UNCHECKED check (F3-01); main_async reads the task bytes once
    before the pre-run check, prerun_missing compares their blob hash with
    the approved hash of the matched document, and the run uses those bytes
    for the task text and the write scope (F3-02). Engine guide §5.0; design 1.9.
    Iteration 5 (fourth follow-up F4-01, F4-02): clear_state and reset_state
    remove files, symlinks and directories; an entry that cannot be removed
    ends the run BLOCKED (reset returns 1); engine_status reports shipped only
    for a regular .complete (F4-01). prerun_missing refuses a task path given
    without bytes (F4-02). Engine guide §5.0; design 1.10.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "modify" }
    - { name: "approve command", file_path: "ai/engine/src/approve.py", change_type: "modify" }
    - { name: "gates", file_path: "ai/engine/src/gates.py", change_type: "modify" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "modify" }
    - { name: "engine-mcp", file_path: "ai/engine/mcp/server.py", change_type: "modify" }  # iterations 2, 3
    - { name: "loop review recipe", file_path: "ai/engine/recipes/loop-review.yaml", change_type: "modify" }  # iteration 3
    - { name: "overwatch", file_path: "ai/src/overwatch.py", change_type: "modify" }
    - { name: "audit review recipe", file_path: "ai/governance/software-engineering/recipes/audit-review.yaml", change_type: "modify" }
    - { name: "governance", file_path: "ai/governance/software-engineering/governance.md (12.1), manifest.yaml, primer.md (both copies), templates/T03-prompt.md", change_type: "modify" }
    - { name: "documents", file_path: "guide-engine-operations.md, ai/engine/README.md, CLAUDE.md, docs guides, profile, skill, requirements v1.3, design v1.6, backlog, live report", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_audit_remediation.py (add); test_stages.py, test_manifest_gates.py, test_migrate_terms.py, tests/overwatch/test_overwatch.py (modify)", change_type: "modify" }
  out_of_scope:
    - "L-08, L-09, L-10, L-11 and the L-14 accept remainder (backlog §3.0 items 6–10)"
    - "Requiring evidence documents to be committed before approval (the working copy is compared)"

rational:
  problem_statement: "The audit showed that the loop's verdict, the approval gate and the read-only reviewer can each be bypassed."
  proposed_solution: "Engine-owned signal files, content-bound approvals and a dispatch allowlist, each with tests; the medium and in-scope low findings with them."
  risks:
    - "Existing approvals without blobs no longer open the loop; operators re-run approve.py once per tracked work item"
    - "Iteration 2: approvals recorded by iteration 1 are keyed by file name and must be re-recorded once"
    - "Iteration 2: a tracked run must name the prompt in ai/workspace/prompt/ itself"
    - "Gate code written by the worker still runs with operator permissions (design DI-06); a detached process started by a gate can still write state files after the clear"
    - "An edit to a change or prompt after approval (including a status edit) needs re-approval"
    - "A misconfigured gate now blocks a run that previously shipped"
    - "Write tools of other MCP servers that take no recognised path argument are refused"

testing_requirements:
  validation_criteria:
    - "All existing tests pass (two fixtures updated to bound approvals; iteration 2: blob keys in fixtures, FakePopen lets the task check run)"
    - "Iteration 2: gate-written review-result.txt and review-feedback.txt ignored; task in a prompt subfolder, other workspace folder, workspace root, closed/ or with .MD refused by the engine (exit 3) and engine-mcp; active and closed copies bound separately; directory targets holding signal files refused; case variants refused"
    - "Iteration 3: newline-terminated task name and a symlink named for another work item refused by the pre-run check, main_async (exit 3) and engine-mcp; gate-written .complete, awaiting-approval.md, review-result.txt and review-feedback.txt absent during review and after REVISE, for bare, bold and empty REVISE messages"
    - "Iteration 4: gate-written files cleared when the gate times out or a later gate cannot run; task bytes differing from the approved content refused; an in-place edit or symlink re-point after the pre-run check does not reach the run (main_async with stubbed providers and MCP)"
    - "Iteration 5: symlinked, dangling and directory .complete removed by clear_state and reset_state; gate-created symlink and directory .complete absent at review and after; unremovable entry BLOCKs; engine_status shipped false for a symlink or directory; tracked task absent at the read refused (exit 3)"
    - "Forged review-result.txt does not override REVISE; reviewer and unoffered calls are refused and not dispatched; signal files refused; no-path writes refused; symlink target checked; UNCHECKED blocks naming the gate; SKIPPED listed; gate environment scrubbed; worker-mode return stage; declared deliverables in block; writable_paths validated; edited, added and unbound approvals reported; re-approval; unquoted UUID skipped; scan leaves .git/index unchanged; symlinked prompt tracked; bare-term scan"

implementation:
  rollback_procedure: "Revert the commit. ai/approvals.yaml entries with blobs remain readable by the previous engine."

traceability:
  requirements: ["FR-02-03", "FR-03-02", "FR-05-01", "FR-05-03", "FR-07-01", "FR-08-05", "FR-08-06", "NFR-05"]
  design: "design-14e05e35 v1.10 §6.0, §7.0, §8.0, §9.0, §10.0, §14.0 DI-06"
  audit: "dev/audit/audit-14e05e35-phase2-2026-10-01.md; follow-ups dev/audit/audit-14e05e35-followup-2026-10-01.md, dev/audit/audit-14e05e35-followup2-2026-10-01.md, dev/audit/audit-14e05e35-followup3-2026-10-01.md, dev/audit/audit-14e05e35-followup4-2026-10-01.md"
  prompt: "dev/prompt/closed/prompt-82dbf16a-audit-14e05e35-remediation.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record; implemented 2026-10-01 (258 passed, offline shim); commit 9f692dc"]
  - version: "2.0"
    date: "2026-10-01"
    changes: ["Iteration 2 from the follow-up audit (F-01 to F-06); implemented 2026-10-01 (279 passed, offline shim); commit 5ada0b6"]
  - version: "3.0"
    date: "2026-10-01"
    changes: ["Iteration 3 from the second follow-up audit (F2-01 to F2-04); implemented 2026-10-01 (287 passed, offline shim); commit 736af62"]
  - version: "4.0"
    date: "2026-10-01"
    changes: ["Iteration 4 from the third follow-up audit (F3-01, F3-02); implemented 2026-10-01 (292 passed, offline shim); commit da21811"]
  - version: "5.0"
    date: "2026-10-01"
    changes: ["Iteration 5 from the fourth follow-up audit (F4-01, F4-02); implemented 2026-10-01 (303 passed, offline shim)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
