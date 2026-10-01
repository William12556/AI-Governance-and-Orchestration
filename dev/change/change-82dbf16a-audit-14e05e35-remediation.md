Created: 2026 October 01

```yaml
change_info:
  id: "change-82dbf16a"
  title: "Audit-14e05e35 remediation: verdict source, content-bound approvals, dispatch allowlist, gates and documents"
  date: "2026-10-01"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-82dbf16a"
    issue_iteration: 1

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
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "modify" }
    - { name: "approve command", file_path: "ai/engine/src/approve.py", change_type: "modify" }
    - { name: "gates", file_path: "ai/engine/src/gates.py", change_type: "modify" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "modify" }
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
    - "An edit to a change or prompt after approval (including a status edit) needs re-approval"
    - "A misconfigured gate now blocks a run that previously shipped"
    - "Write tools of other MCP servers that take no recognised path argument are refused"

testing_requirements:
  validation_criteria:
    - "All existing tests pass (two fixtures updated to bound approvals)"
    - "Forged review-result.txt does not override REVISE; reviewer and unoffered calls are refused and not dispatched; signal files refused; no-path writes refused; symlink target checked; UNCHECKED blocks naming the gate; SKIPPED listed; gate environment scrubbed; worker-mode return stage; declared deliverables in block; writable_paths validated; edited, added and unbound approvals reported; re-approval; unquoted UUID skipped; scan leaves .git/index unchanged; symlinked prompt tracked; bare-term scan"

implementation:
  rollback_procedure: "Revert the commit. ai/approvals.yaml entries with blobs remain readable by the previous engine."

traceability:
  requirements: ["FR-02-03", "FR-03-02", "FR-05-01", "FR-05-03", "FR-07-01", "FR-08-05", "FR-08-06", "NFR-05"]
  design: "design-14e05e35 v1.6 §6.0, §7.0, §8.0, §10.0"
  audit: "dev/audit/audit-14e05e35-phase2-2026-10-01.md"
  prompt: "dev/prompt/closed/prompt-82dbf16a-audit-14e05e35-remediation.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record; implemented 2026-10-01 (258 passed, offline shim)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
