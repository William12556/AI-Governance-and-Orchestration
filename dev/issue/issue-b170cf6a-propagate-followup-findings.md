Created: 2026 September 23

```yaml
issue_info:
  id: "issue-b170cf6a"
  title: "propagate.sh residual findings N-01 to N-08 from the c5270084 follow-up audit"
  date: "2026-09-23"
  reporter: "William Watson"
  status: "resolved"
  severity: "medium"
  type: "defect"
  iteration: 2
  coupled_docs:
    change_ref: "change-b170cf6a"
    change_iteration: 2

source:
  origin: "code_review"
  test_ref: "dev/audit/closed/audit-c5270084-followup-2026-09-23.md (N-01 to N-08)"
  description: >
    The P02.8.2 follow-up audit of change-c5270084 iteration 3 confirmed the
    no-delete design for files absent from the source and recorded eight new
    findings: three medium, five low.

affected_scope:
  components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
  designs: []
  version: "governance 10.4"

behavior:
  expected: "No project content is lost by propagation; the preview and exit codes are accurate."
  actual: >
    N-01 local edits to framework files overwritten without a copy, including
    files created at framework paths during the prompt. N-02 (inferred, macOS)
    case-insensitive name equivalence lets a project file be overwritten.
    N-03 preview and up-to-date gate depend on rsync itemize text. N-04
    dirname without '--'. N-05 exit-contract gaps (RELOCATED.md candidate,
    unchecked suffix, log path as directory, excluded-only directory blocking
    the copy). N-06 stash-only blobs labelled 'retired framework file'. N-07
    symlinked parent of a declared path relocated whole; relative symlinks.
    N-08 FIFO unlinked by rsync; raw control characters echoed; files created
    during the prompt not relocated; interrupt between move and log.
  impact: "N-01 is the remaining content-loss path; the others affect accuracy or block runs."

analysis:
  root_cause: "Iteration 3 protected only entries absent from the source and still parsed rsync output for the preview."

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5) — direct implementation"
  target_date: "2026-09-23"
  approach: "Back up local modifications; exact-name comparison; self-computed preview; re-plan after the prompt; exit-contract fixes."
  change_ref: "change-b170cf6a"
  resolved_date: "2026-09-23"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "See change-b170cf6a technical_details."

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

traceability:
  design_refs:
    - "ai/governance.md P10.6"
  change_refs:
    - "change-b170cf6a"
  test_refs: []

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial issue from the c5270084 follow-up audit; resolved under change-b170cf6a, awaiting independent re-check"
  - version: "2.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 2: re-check audit-b170cf6a found A1-A7 (2 medium, 5 low); remediated under change-b170cf6a iteration 2; final re-check pending"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
