Created: 2026 October 01

```yaml
issue_info:
  id: "issue-82dbf16a"
  title: "Audit-14e05e35: forged verdict, unbound approvals, reviewer write dispatch, and medium and low findings"
  date: "2026-10-01"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-82dbf16a"
    change_iteration: 1

source:
  origin: "audit"
  test_ref: "dev/audit/audit-14e05e35-phase2-2026-10-01.md (experiments E-1 to E-6)"
  description: >
    The independent audit of Phase 2 (requirements V-14) found three high,
    five medium and sixteen low findings. The operator approved remediation
    of H-01 to H-03, M-01 to M-05 and the low findings L-01 to L-07, L-12,
    L-13, L-14 (UUID parsing), L-15 and L-16; L-08 to L-11 and the L-14
    accept remainder go to the backlog.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "scope", file_path: "ai/engine/src/scope.py" }
    - { name: "stages", file_path: "ai/engine/src/stages.py" }
    - { name: "approve command", file_path: "ai/engine/src/approve.py" }
    - { name: "gates", file_path: "ai/engine/src/gates.py" }
    - { name: "manifest", file_path: "ai/engine/src/manifest.py" }
  designs:
    - design_ref: "dev/design/design-14e05e35-engine-generalisation.md"
  version: "governance 12.0; AI-G&O HEAD 4cdfbe4"

reproduction:
  prerequisites: "AI-G&O at 4cdfbe4"
  steps:
    - "H-01 (E-1): a worker writes SHIP into review-result.txt; the reviewer answers REVISE; the loop ends rc 0 with .complete"
    - "H-02 (E-2): after a committed prompt approval, the prompt is edited and a second prompt-<uuid>-*.md added; prerun_missing returns []"
    - "H-03 (E-3): a reviewer call to write_file src/x.py is dispatched"
    - "M-01 (E-4): write calls with filename, file, directory or uri arguments pass the scope check"
    - "M-04 (E-5): git status in the stage scan changes .git/index"
  frequency: "always"
  reproducibility_conditions: "As stated per finding"
  preconditions: ""
  test_data: "Audit experiments E-1 to E-6"
  error_output: "See audit §5.0 and §6.0"

behavior:
  expected: >
    Only the reviewer of the current cycle supplies a verdict; an approval
    covers only the document content it was given for; the review phase
    writes nothing; a write call with no recognised path is refused; a gate
    that cannot run blocks; the stage scan writes nothing; gate processes do
    not receive provider keys.
  actual: "As listed under reproduction; M-02, M-03, M-05 and the low findings per audit §5.0."
  impact: >
    H-01 lets the worker override a rejecting reviewer. H-02 lets a planner
    with filesystem access only run unapproved content. H-03 lets a
    hallucinated reviewer call write anywhere in the project.

analysis:
  root_cause: >
    H-01: the state directory is in the worker's scope and review-result.txt
    takes precedence over the reviewer's final message. H-02: approvals are
    (uuid, stage) pairs. H-03: dispatch does not compare calls with the
    offered tool list. M-01: the scope check is fail-open when no target is
    extracted. M-02: only FAIL overrides SHIP. M-04: git status takes the
    optional index lock. M-05: subprocess.run inherits the environment.
  technical_notes: "M-02 decided by the operator 2026-10-01: UNCHECKED blocks; gates with nothing to check are listed in awaiting-approval.md; FR-03-02 amended."

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5)"
  target_date: "2026-10-01"
  approach: "See change-82dbf16a."
  change_ref: "change-82dbf16a"
  resolved_date: "2026-10-01"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "Signal files protected and review-result.txt cleared before review; approvals record blob hashes and the pre-run check compares them; dispatch limited to offered tools, no writes in review; no-path writes refused; UNCHECKED blocks; git without optional locks; provider keys scrubbed from gates; document corrections."

verification:
  verified_date: ""
  verified_by: "Targeted follow-up audit (P02.8.2), pending"
  test_results: "258 passed 2026-10-01 (offline shim, tests/engine and tests/overwatch); operator pytest run pending."
  closure_notes: ""

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md v1.6"
  change_refs:
    - "change-82dbf16a"
  test_refs:
    - "tests/engine/test_audit_remediation.py"
    - "tests/engine/test_stages.py"
    - "tests/engine/test_manifest_gates.py"
    - "tests/engine/test_migrate_terms.py"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    author: "William Watson"
    changes:
      - "Initial issue from audit-14e05e35; status resolved after implementation"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t06_issue"
```
