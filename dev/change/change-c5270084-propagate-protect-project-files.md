Created: 2026 September 23

```yaml
change_info:
  id: "change-c5270084"
  title: "propagate.sh: delete only unmodified framework files; relocate project content to ai-local/"
  date: "2026-09-23"
  author: "William Watson"
  status: "implemented"
  priority: "critical"
  iteration: 2
  coupled_docs:
    issue_ref: "issue-c5270084"
    issue_iteration: 2
    prompt_ref: "prompt-c5270084"

source:
  type: "issue"
  reference: "issue-c5270084"
  description: "Restrict --delete to files git can restore and the project has not declared its own."

scope:
  summary: "bin/propagate.sh classify-and-relocate; governance 10.3 P10.6 rule; two guides updated."
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
    - "Recovery of solax-modbus ai/project_information.md (operator: Time Machine or Claude project knowledge)"
    - "Moving governance-declared project files (context.md, task.md, ael/config.yaml, workspace/, state/) out of ai/ — operator decision 2026-09-23; backlog"

rational:
  problem_statement: "See issue-c5270084."
  proposed_solution: >
    Operator direction 2026-09-23: project files do not belong in ai/. For each
    target file that rsync --delete would remove, compute its git blob hash; if
    that blob exists in the framework repository it is an unmodified framework
    file and is deleted. Otherwise it is project content, tracked or not, and is
    moved to <project-root>/ai-local/<same path> before the rsync apply, never
    overwriting (timestamp suffix on collision), and logged in
    ai-local/RELOCATED.md. A relocated file that was gitignored in ai/ and is
    not ignored at its new path is flagged. Governance P10.6 states the rule.
  alternatives_considered:
    - option: "Iteration 1: protect untracked files; ai/.propagate-keep for tracked project files"
      reason_rejected: "Leaves legacy project files in ai/ and relies on per-project keep lists; superseded by operator direction."
    - option: "Classify by path presence in framework history"
      reason_rejected: "solax-modbus ai/instructions.md shares a historic framework path but holds project-edited content; path alone would delete it."
  benefits:
    - "No file is lost: every deletion is restorable from framework history, every other file is moved"
    - "Enforces the P10.6 layout; retires .propagate-keep"
  risks:
    - risk: "A relocated file that was gitignored becomes committable"
      mitigation: "Warning at run time and in RELOCATED.md"
    - risk: "An edited framework file (e.g. a locally patched template) is relocated rather than deleted"
      mitigation: "Intended: edits are project content; listed as 'relocate' in the preview"
    - risk: "Relocation succeeds but the rsync apply fails"
      mitigation: "Files are moved, not lost; RELOCATED.md records each move"

technical_details:
  current_behavior: "Iteration 1: untracked files and .propagate-keep entries protected via rsync P rules."
  proposed_behavior: "As proposed_solution. P rules and .propagate-keep removed."
  implementation_approach: "Classify section (rsync --delete dry run, '*deleting' paths expanded to files, git hash-object / cat-file -e); Relocate section before apply."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "Classify and Relocate sections; preview lines delete/relocate; protect rules removed"
      functions_affected:
        - "is_framework_blob (new)"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "New directory <project-root>/ai-local/ with RELOCATED.md; exit 3 if a relocation fails"
    - "ai/.propagate-keep retired (iteration 1 only)"

dependencies:
  internal:
    - component: "change-07087e91"
      impact: "Corrects its deletion scope"
  external:
    - "git (target repository)"
  required_changes: []

testing_requirements:
  test_approach: "Scratch targets in the Cowork VM; dry run against solax-modbus."
  test_cases:
    - scenario: "Historic unmodified framework template in target"
      expected_result: "Deleted"
    - scenario: "Tracked project-edited file at a historic framework path; gitignored file; untracked file with a space; gitignored tmp dir"
      expected_result: "All relocated to ai-local/ with paths preserved and logged"
    - scenario: "Destination already exists in ai-local/"
      expected_result: "Timestamp suffix; existing file untouched"
    - scenario: "File ignored by an ai/-anchored pattern"
      expected_result: "Relocated; WARNING printed and recorded"
    - scenario: "Declared project files (context.md, ael/config.yaml, workspace/, state/)"
      expected_result: "Untouched"
    - scenario: "Target not a git repository"
      expected_result: "Classification still applies; project files relocated"
  regression_scope:
    - "change-07087e91: --yes, non-TTY exit 2, major-version guard, seeding, up-to-date, unknown option"
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
    Iteration 2. bash -n passes. All six test cases pass on scratch targets
    (Cowork Linux VM, GNU bash, rsync 3.2.7); all change-07087e91 regression
    cases pass. Dry run against solax-modbus classifies instructions.md,
    obsidian_markdown_guidelines.md, ael/config.yaml.bak and .propagate-keep
    as project content to relocate, and nothing to delete. Not exercised under
    macOS bash 3.2 or macOS rsync.
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
  - version: "2.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 2 at operator direction: protect rules and .propagate-keep replaced by content classification and relocation to ai-local/; governance 10.3 P10.6 rule"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
