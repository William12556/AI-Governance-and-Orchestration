Created: 2026 September 23

```yaml
change_info:
  id: "change-c5270084"
  title: "propagate.sh: never delete; relocate all non-framework and retired files to ai-local/ with labels"
  date: "2026-09-23"
  author: "William Watson"
  status: "implemented"
  priority: "critical"
  iteration: 3
  coupled_docs:
    issue_ref: "issue-c5270084"
    issue_iteration: 3
    prompt_ref: "prompt-c5270084"

source:
  type: "issue"
  reference: "issue-c5270084"
  description: "Restrict --delete to files git can restore and the project has not declared its own."

scope:
  summary: "bin/propagate.sh rewritten to a no-delete design; governance 10.4 P10.6; two guides updated. Remediates audit-c5270084 findings F-01 to F-12."
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
    - "Recovery of solax-modbus ai/project_information.md"
    - "Moving governance-declared project files out of ai/ (backlog §2.0 item 7)"
    - "Local edits to files that exist in the framework source are overwritten by the copy, as before 07087e91 — unchanged behaviour, not addressed by the audit"

rational:
  problem_statement: >
    Strategic audit dev/audit/audit-c5270084-strategic-2026-09-23.md refuted
    C1, C2, C4, C5, C6 and C9 for iteration 2: apply-time rsync --delete was not
    bounded by the classification (F-01, critical), the blob test accepted
    unreachable and path-independent objects (F-02), and change-07087e91's
    version check made new-project initialization exit silently (F-03,
    regression in a closed change).
  proposed_solution: >
    Operator decision 2026-09-23: the script never deletes. rsync runs without
    --delete. Target entries are enumerated with find -print0 and compared with
    the source directly; every entry that is absent from the source or of a
    different type is relocated to ai-local/ before the copy. RELOCATED.md
    labels each: 'retired framework file' when its non-empty content is a blob
    at the same path in history reachable from the framework's refs, otherwise
    'project content'. The human deletes after review.
  alternatives_considered:
    - option: "Fail-closed automatic deletion (audit ISS-A)"
      reason_rejected: "Operator chose no deletion: less code and no data-loss path at all."
  benefits:
    - "No code path deletes a file; the label is advisory only"
    - "Safety does not depend on rsync output text (C8 reduces to bash 3.2 compatibility)"
  risks:
    - risk: "Retired framework files accumulate in ai-local/"
      mitigation: "Labelled 'retired framework file'; one manual rm per major version"
    - risk: "A file created while the prompt is open is not relocated"
      mitigation: "It is left in ai/; nothing is lost"

technical_details:
  current_behavior: "Iteration 2: classification from rsync '*deleting' output, apply-time rsync --delete."
  proposed_behavior: "As proposed_solution. Per finding: F-01 no --delete, independent enumeration incl. type conflicts; F-02 reachable, path-specific, non-empty blobs, label only; F-03 absent/unparseable version reported as 'unknown' and treated as major, x.y.z accepted, empty ai/ initializes; F-04 ignore status recorded before any move, checked after all, warning when a .gitignore is relocated; F-05 logs/ declared; F-06 excludes without trailing slash; F-07 NUL-delimited paths, destinations pre-checked, every relocation failure exits 3 before the copy; F-08 preview shows actual destination and label; F-09 shallow clone noted; F-10 destination chain checked for files and symlinks; F-11 executable bit; F-12 documents corrected."
  implementation_approach: "Script rewritten section by section; interface unchanged apart from exit 3 on unsafe ai-local/ destinations."
  code_changes:
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "No-delete rewrite"
      functions_affected:
        - "gov_version, is_declared, same_type, label_of, check_dir_chain"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "ai-local/RELOCATED.md gains a Label column"
    - "Exit 3 when an ai-local/ destination path is unsafe (before any change)"
    - "Unknown target version requires --allow-major with --yes"

dependencies:
  internal:
    - component: "change-07087e91"
      impact: "Corrects its deletion scope"
  external:
    - "git (target repository)"
  required_changes: []

testing_requirements:
  test_approach: "The audit's experiments E2-E17 re-run against iteration 3 on throwaway targets (Cowork VM), plus a dry run against solax-modbus."
  test_cases:
    - scenario: "E2 9.16 target with project files and nested dotfile paths"
      expected_result: "Seven retired templates relocated and labelled retired; project files relocated with paths; T01-T08 present"
    - scenario: "E3 file where the source has a directory; E4 leading-space name; E5 newline and non-ASCII names under LC_ALL=C"
      expected_result: "All relocated intact; framework files correct; exit 0"
    - scenario: "E7 rsync output rewritten by a shim"
      expected_result: "Project file relocated; nothing deleted"
    - scenario: "E8 shallow clone; E9 unreachable blob; E12 empty files; E17 CRLF copy"
      expected_result: "Relocated; shallow note shown; labels 'project content' for E9, E12, E17"
    - scenario: "E10 symlinked state/ and workspace/, logs/ directory; E14 declared files"
      expected_result: "Untouched; no ai-local/"
    - scenario: "E11 relocated .gitignore and root-anchored ignore"
      expected_result: "Warnings for .gitignore relocation and for both newly unignored files"
    - scenario: "E13 ai-local/ component is a file or a symlink"
      expected_result: "Exit 3 before any change; nothing written outside ai-local/"
    - scenario: "E15 guards; E16 empty ai/ and x.y.z version rows"
      expected_result: "Exit 2 with tree unchanged; empty ai/ initializes with --allow-major; x.y.z parsed"
  regression_scope:
    - "change-07087e91 --yes, non-TTY, major guard, seeding, up-to-date, unknown option"
  validation_criteria:
    - "All test cases pass"
    - "bash -n passes; no code path deletes a file"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "After each propagation, review ai-local/RELOCATED.md in the project and delete what is not needed. ai/.propagate-keep (iteration 1) is obsolete."

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    Iteration 3. bash -n passes. All listed cases pass on throwaway targets in
    the Cowork Linux VM (GNU bash 5.1, rsync 3.2.7). E6 (race) not re-run: a
    file created during the prompt is outside the plan and there is no
    deletion step. Dry run against solax-modbus relocates .propagate-keep,
    ael/config.yaml.bak, obsidian_markdown_guidelines.md and instructions.md
    as project content. Operator live run against solax-modbus on macOS
    (bash 3.2, openrsync — 'Transfer starting' output), 2026-09-23: four files
    relocated byte-identical to HEAD, framework files updated, no deletion.
    That run did not cover labelling of retired files or the major-version
    guard on macOS; audit §8.0 step 2 remains outstanding. RELOCATED.md Note
    column printed the raw flag 'false'; corrected to a readable note.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-07087e91"
      relationship: "corrects — including audit F-03, a regression introduced by 07087e91 after its closure (new-project initialization exited silently)"
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
  - version: "3.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 3 after audit-c5270084: no-delete design at operator direction; findings F-01 to F-12 remediated; governance 10.4 (logs/ declared)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
