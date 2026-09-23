Created: 2026 September 23

```yaml
change_info:
  id: "change-51f1aef0"
  title: "linter.py: accept YAML version_history, proposal/report classes, full issue-type enum, prose-issue coupling; exempt prompts from version history"
  date: "2026-09-23"
  author: "William Watson"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-51f1aef0"
    issue_iteration: 1
    prompt_ref: "prompt-51f1aef0"

source:
  type: "issue"
  reference: "issue-51f1aef0"
  description: "Correct five linter rules that reject valid documents."

scope:
  summary: "Five rule corrections in ai/ael/src/linter.py. No document changes, no new checks."
  affected_components:
    - name: "linter (VALID_CLASSES, _ENUMS, check_structure, run)"
      file_path: "ai/ael/src/linter.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "dev/eval/results/probe-*.md — gitignored, not governance documents"
    - "WARN-level findings (missing Created:, template_version, anchors)"
    - "Citation checking in source comments (backlog §3.3)"

rational:
  problem_statement: "See issue-51f1aef0: 95 false errors in dev/ prevent use of the linter as a CI gate."
  proposed_solution: "Align each rule with the current templates and conventions."
  alternatives_considered:
    - option: "Add markdown Version History sections to every YAML document"
      reason_rejected: "Retrofits 80+ closed documents to satisfy a rule the templates contradict."
    - option: "Add version_history to the T03 prompt template"
      reason_rejected: "Operator decision 2026-09-23: prompts are exempt; iteration field and git record changes."
  benefits:
    - "dev/ linter errors 99 -> 4 (the 4 being out-of-governance probes)"
    - "Prerequisite for CI (backlog §2.4)"
  risks:
    - risk: "Relaxed structure rule hides a genuinely missing history"
      mitigation: "Accepts only a line-anchored version_history: key or the markdown heading; prompts are the only exemption"
    - risk: "Filename-based coupling index accepts a document with a malformed YAML id"
      mitigation: "ID pattern check on YAML documents is unchanged and still reports malformed ids"

technical_details:
  current_behavior: "See issue-51f1aef0 behavior.actual (1)–(5)."
  proposed_behavior: >
    (1) check_structure passes when the markdown heading or a line-anchored
    version_history: key is present. (2) VALID_CLASSES adds proposal and report.
    (3) t03_issue type enum adds enhancement and requirement_change. (4) run()
    indexes every NORMAL_RE governance filename as <class>-<uuid> before coupling.
    (5) check_structure skips the version-history check for prompt-class files.
  implementation_approach: "Direct edits to the four locations; check_structure gains the filename to identify prompts."
  code_changes:
    - component: "linter"
      file: "ai/ael/src/linter.py"
      change_summary: "Five rule corrections as listed"
      functions_affected:
        - "check_structure"
        - "run"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Run linter.py against dev/, ai/workspace and a scratch fixture set; compare with the pre-change baseline."
  test_cases:
    - scenario: "YAML document with version_history: key and no markdown heading"
      expected_result: "No structure ERROR"
    - scenario: "Document with neither heading nor key (non-prompt)"
      expected_result: "Structure ERROR still reported"
    - scenario: "Prompt document without version history"
      expected_result: "No structure ERROR"
    - scenario: "proposal-<uuid>-x.md and report-<uuid>-x.md"
      expected_result: "No naming ERROR"
    - scenario: "Unknown class foo-<uuid>-x.md"
      expected_result: "Naming ERROR still reported"
    - scenario: "Issue with type enhancement; issue with type bogus"
      expected_result: "No ERROR; ERROR respectively"
    - scenario: "Change coupled to a prose-format issue that exists; change coupled to a nonexistent issue"
      expected_result: "No ERROR; coupling ERROR respectively"
  regression_scope:
    - "ai/workspace: 0 errors before and after"
    - "Iteration-mismatch coupling check unchanged for YAML documents"
  validation_criteria:
    - "dev/ ERROR count equals the 4 probe files' errors"
    - "All test cases pass"
    - "linter.py compiles"

implementation:
  effort_estimate: "small"
  implementation_steps:
    - step: "Claude (Cowork) implements directly at William Watson's instruction, 2026-09-23"
      owner: "Claude (Cowork, Opus 5.5)"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "Propagates with ai/ via bin/propagate.sh; no configuration change."

verification:
  implemented_date: "2026-09-23"
  implemented_by: "Claude (Cowork, Opus 5.5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — implementing session"
  test_results: >
    linter.py compiles. dev/: 99 -> 8 errors, all on the 4 gitignored
    dev/eval/results probe files (out of scope). ai/workspace: 0 -> 0.
    protocol_checker dev/: 0. Scratch fixture set: all seven test cases
    behave as specified. Additional effect: the version-history check now
    matches a heading or key rather than any occurrence of the phrase, so a
    document that only mentions "version history" in prose is now reported;
    no dev/ document is affected.
  issues_found: []

operator_closure_2026_09_23:
  closed_by: "William Watson"
  basis: >
    Closed at William Watson's direction on 2026-09-23. The P02.8.2 follow-up
    audit (required for source remediation under governance 10.2) is waived
    and recorded here as a waiver, not as satisfaction of the requirement:
    linter.py has been verified only by the implementing session.

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-51f1aef0"
      relationship: "resolves"

notes: >
  Implemented by the Strategic Domain at operator instruction. Per P02.8.2 as
  amended in governance 10.2, a follow-up audit applies to source remediation;
  independent review or a recorded waiver is required before closure.

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
      - "Implemented; verification by implementing session recorded; version-history check anchored to heading or key"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed at operator direction; independent audit waived (operator_closure_2026_09_23); status implemented -> verified"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
