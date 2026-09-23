Created: 2026 September 23

```yaml
change_info:
  id: "change-b170cf6a"
  title: "propagate.sh: back up local modifications; exact names; self-computed preview; re-plan after prompt; exit-contract fixes"
  date: "2026-09-23"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b170cf6a"
    issue_iteration: 1
    prompt_ref: "prompt-b170cf6a"

source:
  type: "issue"
  reference: "issue-b170cf6a"
  description: "Remediate follow-up audit findings N-01 to N-08."

scope:
  summary: "bin/propagate.sh; governance 10.5 P10.6; two guides."
  affected_components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "governance"
      file_path: "ai/governance.md"
      change_type: "modify"
    - name: "user guides"
      file_path: "docs/guide-install.md, docs/guide-getting-started.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "A directory at a declared file name (ai/context.md/) is emptied into ai-local/ and then seeded (N-07 part); no content lost; unchanged"
    - "Interrupt between log row and action: row is now written first, so an interrupted action leaves a row without a move (safe direction)"

rational:
  problem_statement: "See issue-b170cf6a."
  proposed_solution: >
    N-01: before the copy, copy each regular target file at a framework path
    whose content differs from the source and is not a framework version at
    that path to ai-local/ as 'local modification'. After an interactive
    confirmation, re-plan and refuse (exit 3) if the plan changed while the
    prompt was open. N-02: path existence is decided by exact byte comparison
    of directory entries, component by component. N-03: the preview and the
    up-to-date gate are computed with find and cmp; rsync output is not parsed.
    N-04: dirname -- throughout. N-05: RELOCATED.md reserved; suffix loops with
    timestamp, index and counter until free; a non-regular log path refuses
    before any change; droppings inside a type-conflict directory are relocated
    and empty blocking directories removed; a failed copy exits 4 with a
    message. N-06: labels use branches, tags, remotes and HEAD only. N-07: a
    candidate symlink that holds a declared path (ai/ael) refuses before any
    change; relative symlinks are noted in the log. N-08: every non-directory
    entry type is enumerated, so a FIFO at a framework path is relocated;
    control characters are replaced in displayed paths.
  alternatives_considered:
    - option: "Record N-01 as accepted behaviour"
      reason_rejected: "Operator decision 2026-09-23: back up edits."
  benefits:
    - "No project content lost, including local edits to framework files"
    - "No dependence on rsync output text"
  risks:
    - risk: "Backups of intentionally discarded edits accumulate in ai-local/"
      mitigation: "Labelled 'local modification'; deleted by the human after review"

technical_details:
  current_behavior: "Iteration 3 of change-c5270084."
  proposed_behavior: "As proposed_solution."
  implementation_approach: "plan() computes cands, backups and updates as NUL lists; records carry kind, path, destination, label, ignore flag and note."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "N-01 to N-08"
      functions_affected:
        - "plan, fingerprint, exact_exists, ancestor_conflict, dest_for, add_rec, disp (new); same_type, is_framework_version"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "Preview lines 'add', 'update', 'relocate', 'backup'"
    - "Exit 3 when the target changes during the prompt or ai/ael is a symlink; exit 4 when the copy fails"
    - "RELOCATED.md label 'local modification'"

dependencies:
  internal:
    - component: "change-c5270084"
      impact: "Extends iteration 3"
  external:
    - "git, rsync, find, cmp"
  required_changes: []

testing_requirements:
  test_approach: "Follow-up audit experiments X1-X13 re-run on throwaway targets in the Cowork Linux VM."
  test_cases:
    - scenario: "X1 9.16 target with special names and a type conflict, LC_ALL=C"
      expected_result: "7 retired and 9 project entries relocated; T01-T08 present; exit 0"
    - scenario: "X2 local edit to primer.md; X2b older framework primer.md"
      expected_result: "Edit backed up then overwritten; older version not backed up"
    - scenario: "X3 file created at a framework path or a new path during the prompt"
      expected_result: "Exit 3, nothing applied, created files intact"
    - scenario: "X4 FIFO at workflow.md; X5 directory holding notes and droppings at workflow.md"
      expected_result: "Relocated; framework workflow.md in place; exit 0"
    - scenario: "X6 declared symlinks and logs/; X6b symlinked ai/ael holding config.yaml"
      expected_result: "Untouched; exit 3 before any change"
    - scenario: "X7 relocated .gitignore; X8 stash-only blob"
      expected_result: "Three warnings; label 'project content'"
    - scenario: "X9c RELOCATED.md candidate; X9d log path is a directory; X9e suffix exists"
      expected_result: "Suffixed; exit 3 before any change; next free suffix"
    - scenario: "X10 guards and empty ai/; X11 rsync output shim; X13 '-x.md' and '--'"
      expected_result: "Exit 2 / initialize; update applied; relocated, exit 0"
  regression_scope:
    - "change-07087e91 and change-c5270084 behaviour"
  validation_criteria:
    - "All test cases pass; bash -n passes"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "Independent re-check and macOS procedure (follow-up audit §8.0) before the next downstream propagation."

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    bash -n passes. All test cases pass in the Cowork Linux VM (GNU bash 5.1,
    rsync 3.2.7). N-02 cannot be exercised on this file system (case
    sensitive); follow-up §8.0 step 3 on macOS remains the test. bash 3.2 not
    re-run for this change.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-c5270084"
      relationship: "extends"
  related_issues:
    - issue_ref: "issue-b170cf6a"
      relationship: "resolves"

notes: >
  Implemented by the Strategic Domain at operator instruction. Independent
  re-check required before closure (operator decision 2026-09-23).

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial change document; implemented"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
