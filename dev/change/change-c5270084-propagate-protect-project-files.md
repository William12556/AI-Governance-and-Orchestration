Created: 2026 September 23

```yaml
change_info:
  id: "change-c5270084"
  title: "propagate.sh: protect untracked target files and ai/.propagate-keep entries from --delete"
  date: "2026-09-23"
  author: "William Watson"
  status: "implemented"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c5270084"
    issue_iteration: 1
    prompt_ref: "prompt-c5270084"

source:
  type: "issue"
  reference: "issue-c5270084"
  description: "Restrict --delete to files git can restore and the project has not declared its own."

scope:
  summary: "bin/propagate.sh protect rules; two guides updated."
  affected_components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "user guides"
      file_path: "docs/guide-install.md, docs/guide-getting-started.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Recovery of solax-modbus ai/project_information.md (operator: Time Machine or Claude project knowledge)"
    - "Keep lists for other downstream projects — to be written before each first v10.x propagation"

rational:
  problem_statement: "See issue-c5270084."
  proposed_solution: >
    Before preview and apply, pass every file reported by git ls-files --others
    in the target ai/ (untracked, including gitignored) to rsync as a protect
    ('P') rule, and every path in <project>/ai/.propagate-keep likewise. List
    protected files that are absent from the source in the preview. If the
    target is not a git repository, protect everything.
  alternatives_considered:
    - option: "Revert to additive rsync plus a retired-path list"
      reason_rejected: "Operator chose protect rules 2026-09-23; renames still propagate automatically."
    - option: "Protect only via .propagate-keep"
      reason_rejected: "Relies on foresight; an unlisted untracked file would still be lost irrecoverably."
  benefits:
    - "No file git cannot restore is ever deleted"
    - "Projects can declare tracked local files explicitly"
  risks:
    - risk: "A tracked project file not in .propagate-keep is still deleted"
      mitigation: "Recoverable with git checkout; listed as '*deleting' in the preview"
    - risk: "An untracked retired framework file survives in the target"
      mitigation: "Shown as 'protect' in the preview for manual removal"

technical_details:
  current_behavior: "rsync --delete removes every target file absent from the source, excluded paths apart."
  proposed_behavior: "As proposed_solution."
  implementation_approach: "Protect section before the preview; PROTECT array added to both rsync calls; .propagate-keep excluded from transfer."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "Protect section, .propagate-keep support, preview listing"
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - "New optional file <project>/ai/.propagate-keep"

dependencies:
  internal:
    - component: "change-07087e91"
      impact: "Corrects its deletion scope"
  external:
    - "git (target repository)"
  required_changes: []

testing_requirements:
  test_approach: "Scratch git targets in the Cowork VM; re-run against solax-modbus after restoring its tracked files."
  test_cases:
    - scenario: "Target with tracked retired template, untracked gitignored file, untracked file with a space, gitignored tmp dir"
      expected_result: "Tracked retired files deleted; all untracked files preserved and listed as 'protect'"
    - scenario: "Tracked project file listed in .propagate-keep"
      expected_result: "Preserved; listed as protected; .propagate-keep itself not overwritten"
    - scenario: "Target not a git repository"
      expected_result: "No deletions"
    - scenario: "solax-modbus after restore, with its .propagate-keep"
      expected_result: "Up to date; nothing deleted"
  regression_scope:
    - "change-07087e91 behaviour: --yes, non-TTY exit 2, major-version guard, seeding"
  validation_criteria:
    - "All test cases pass"
    - "bash -n passes"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "Write ai/.propagate-keep in each downstream project before its first v10.x propagation."

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    bash -n passes. Scratch git targets (Cowork Linux VM): tracked retired
    files deleted; gitignored project_information.md, gitignored tmp file and
    an untracked file with a space preserved and listed; a tracked file in
    .propagate-keep preserved; non-git target deleted nothing. solax-modbus
    after restore with its keep file: up to date, nothing deleted.
    change-07087e91 regression (git target): non-TTY exit 2; 9.16 target
    under --yes exit 2; --allow-major applied and seeded; up to date exit 0;
    unknown option exit 1. Not exercised under macOS bash 3.2 or macOS rsync.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-07087e91"
      relationship: "corrects"
  related_issues:
    - issue_ref: "issue-c5270084"
      relationship: "resolves"

notes: >
  Lesson: change-07087e91 was closed with its audit waived; the defect was a
  premise error that an independent review is designed to catch. A P02.8.2
  follow-up audit or a recorded waiver is required before closure.

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial change document — approved for direct implementation"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Implemented; verification by implementing session recorded"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
