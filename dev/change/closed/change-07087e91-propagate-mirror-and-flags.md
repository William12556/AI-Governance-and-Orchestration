Created: 2026 September 23

```yaml
change_info:
  id: "change-07087e91"
  title: "propagate.sh: mirror with --delete; --yes and --allow-major; fail loudly without a TTY"
  date: "2026-09-23"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-07087e91"
    issue_iteration: 1
    prompt_ref: "prompt-07087e91"

source:
  type: "issue"
  reference: "issue-07087e91"
  description: "Make propagation carry renames and run safely without a terminal."

scope:
  summary: "Edits to bin/propagate.sh; two user guides updated to match."
  affected_components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
      change_type: "modify"
    - name: "user guides"
      file_path: "docs/guide-install.md, docs/guide-getting-started.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Running propagation against any downstream project (backlog §6.0)"
    - "Audit F-03 and F-10 — already remediated in 097d6ea"
    - "bin/propagate.sh git file mode (100644, not executable) — pre-existing"

rational:
  problem_statement: "See issue-07087e91."
  proposed_solution: >
    Mirror the target with rsync --delete, relying on rsync's default that
    excluded paths are neither transferred nor deleted. Add --yes; without it
    a non-TTY stdin exits 2 with a message before anything is applied. Read
    the governance version from the last Version History row of each
    governance.md; on a major difference print a warning, and under --yes
    require --allow-major.
  alternatives_considered:
    - option: "Explicit retired-path list"
      reason_rejected: "Operator decision 2026-09-23: every future rename would need manual recording."
    - option: "Refuse outright on a major version difference"
      reason_rejected: "Blocks the intended v9.16 -> v10.x propagation; a warning plus explicit flag suffices."
  benefits:
    - "Renames and retirements propagate"
    - "Non-interactive runs either apply or fail with exit 2"
    - "Major-version propagation is never silent"
  risks:
    - risk: "Files a downstream project added under ai/ outside the exclude list are deleted"
      mitigation: "Preview lists every '*deleting' line before confirmation; interactive default is No"
    - risk: "Version not detectable (no governance.md or no table)"
      mitigation: "Reported as 'unknown'; guard does not trigger; preview still lists deletions"

technical_details:
  current_behavior: "rsync -av without --delete; unconditional read -p prompt."
  proposed_behavior: "As proposed_solution."
  implementation_approach: "Argument loop; gov_version helper; --delete in preview and apply; confirmation branch on --yes / TTY."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "Options, version guard, --delete, confirmation logic"
      functions_affected:
        - "gov_version (new)"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "New options --yes and --allow-major; exit 2 when a run is refused"

dependencies:
  internal: []
  external:
    - "rsync (existing)"
  required_changes: []

testing_requirements:
  test_approach: "Scratch target built from the current ai/ plus project-local files and one retired template; bash -n."
  test_cases:
    - scenario: "Non-TTY stdin without --yes"
      expected_result: "Preview shown incl. '*deleting'; exit 2; nothing applied"
    - scenario: "--yes, same major version"
      expected_result: "Retired file deleted; config.yaml, context.md, task.md, workspace/, state/ preserved; exit 0"
    - scenario: "--yes, target 9.16, source 10.2"
      expected_result: "Warning; exit 2; nothing applied"
    - scenario: "--yes --allow-major, target 9.16"
      expected_result: "Applied; target mirrors source apart from excludes; exit 0"
    - scenario: "Target already up to date"
      expected_result: "'up to date'; exit 0"
    - scenario: "Unknown option"
      expected_result: "Error; exit 1"
    - scenario: "context.md and task.md absent"
      expected_result: "Both seeded from source"
  regression_scope:
    - "Seeding of context.md and task.md"
    - "Exclude list unchanged"
  validation_criteria:
    - "All test cases pass"
    - "bash -n passes"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "bin/ is not propagated; takes effect for the next downstream propagation."

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    bash -n passes. All seven test cases pass against a scratch target in the
    Cowork Linux VM (rsync, GNU bash): non-TTY without --yes exit 2 with
    nothing applied; --yes deletes the retired template and preserves every
    excluded path; 9.16 -> 10.2 under --yes alone exit 2; with --allow-major
    applied and the target mirrors the source apart from excludes; up-to-date
    exit 0; unknown option exit 1; context.md and task.md seeded. Not
    exercised under macOS bash 3.2 or macOS rsync.
  issues_found: []

operator_closure_2026_09_23:
  closed_by: "William Watson"
  basis: >
    Closed at William Watson's direction on 2026-09-23. The P02.8.2 follow-up
    audit is waived and recorded here as a waiver, not as satisfaction of the
    requirement. Verified only by the implementing session, in a Linux VM;
    not exercised under macOS bash 3.2 or macOS rsync. The first live
    downstream propagation (backlog §6.0) is the first macOS exercise.

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-9b8f1c47"
      relationship: "related — remediated audit F-03 and F-10"
  related_issues:
    - issue_ref: "issue-07087e91"
      relationship: "resolves"

notes: >
  Implemented by the Strategic Domain at operator instruction. A P02.8.2
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
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed at operator direction; audit waived and macOS not exercised (operator_closure_2026_09_23); status implemented -> verified"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
