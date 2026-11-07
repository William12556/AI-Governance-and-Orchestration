Created: 2026 November 7

```yaml
issue_info:
  id: "issue-e4428fd5"
  title: "Governance checkers: schema_type namespace, silent skips, TypeError on malformed values, terminal status for superseded tests, missing checker tests"
  date: "2026-11-07"
  status: "closed"  # change-e4428fd5 verified 2026-11-07
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e4428fd5"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 group 3; audit-eb782f83 F-04; GTach observation 2026-10-08
  description: >
    Stage C work item 3 (dev/task.md): audit-caab2052 M-03 and L-11 and the
    missing tests for linter.py and protocol_checker.py (§10.0 group 3),
    with the operator decision of 2026-11-05 recorded in audit-caab2052
    §14.0 (retire the numeric schema_type prefix; templates emit the class
    word; checkers accept the class word and the numbered values as
    aliases; an unknown value is a warning; governance Appendix A.5
    updated). This also closes audit-eb782f83 F-04. Added: the terminal
    status for a test document whose target was removed (found in GTach,
    2026-10-08).

affected_scope:
  components:
    - { name: "linter", file_path: "ai/engine/src/linter.py" }
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py" }  # L-11
    - { name: "templates", file_path: "ai/governance/software-engineering/templates/T01-T08" }
    - { name: "governance", file_path: "ai/governance/software-engineering/governance.md" }  # P00.14.3, Appendix A.5
  designs:
    - { design_ref: "governance.md Appendix A.5 (Unmigrated Namespace), P00.14.3 (Closure Criteria)" }
    - { design_ref: "requirements-14e05e35 NFR-04 (file and field reported)" }
  version: "governance 12.8; checkers at main 12222b3"

reproduction:
  prerequisites: "main 12222b3"
  steps:
    - "M-03: run python3 ai/engine/src/linter.py dev and protocol_checker.py dev; 23 documents in dev/ carry schema_type t07_change, t06_issue or t03_prompt (the template numbering) and are skipped by both checkers without a message"
    - "M-03: a t07_change document with four defects gives 0 findings; the same document as t02_change gives 4 (audit-caab2052 fixture)"
    - "M-03: documents with t01_design, t07_requirements or t08_audit pass check_yaml without any field check and without a message"
    - "L-11: a document whose metadata.schema_type is a list, or whose coupling reference or id is a list or mapping; a manifest stage whose gates list holds a mapping"
    - "Terminal status: in a project, remove the code a T04 test document covers; the test cannot reach a terminal status other than passed"
    - "Tests: no test module covers linter.py or protocol_checker.py"
  frequency: "always, under the stated condition"
  error_output: "L-11: TypeError (unhashable type: 'list' or 'dict'; expected string or bytes-like object) with a traceback instead of a finding"

behavior:
  expected: >
    M-03: every governance document is validated by the rules of its
    class, whichever accepted schema_type spelling it carries; a
    schema_type that names no known class gives a warning naming the file
    and the value. L-11: a malformed value gives a finding naming the file
    and field; neither checker nor the manifest loader raises. Terminal
    status: a test document whose target was removed can be closed with a
    recorded terminal status. Tests: each check of both checkers has a
    test.
  actual: >
    M-03: rules are keyed on the five retired-scheme strings t02_change to
    t06_result; any other value returns before any field check
    (linter.py check_yaml, the coupling pass in run, and
    protocol_checker.load_workspace) and nothing is reported. Templates
    emit the retired values (T02-design t01_design ... T08-audit
    t08_audit); T03-prompt emits no schema_type, so every prompt gives the
    warning 'metadata.schema_type is missing'. L-11: membership tests and
    re.search on unchecked values raise TypeError. Terminal status: the
    test status enum is planned, in_progress, executed, passed, failed,
    blocked; protocol_checker accepts only passed as terminal. Tests: none.
  impact: "Documents in the template numbering are never validated, so defects in them go unreported; malformed YAML ends a check run with a traceback; a test document for removed code cannot be closed without a false 'passed'; a regression in either checker goes unnoticed."
  workaround: "Write documents with the retired values; inspect templated documents by hand."

environment:
  os: "platform-independent"

analysis:
  root_cause: >
    Line numbers at main 12222b3. M-03: linter.py:46-111 (_ENUMS,
    _ID_FIELDS, _ITER_FIELDS, _COUPLING keyed on t02_change to
    t06_result), :251-262 (check_yaml returns before field checks for an
    unlisted value), :403 (coupling pass); protocol_checker.py:33-80
    (tables), :131-133 (load_workspace drops unlisted values); governance
    Appendix A.5 records the namespace as unmigrated. L-11:
    manifest.py:188 ('g not in gates' with g a mapping); linter.py
    check_yaml (schema_type membership test on a list) and check_coupling
    (reference lookup with a list); protocol_checker.py _uuid_from_id
    (:84-87, re.search on a non-string id) and the coupling checks
    (:160-168). Terminal status: templates/T04-test.md:26 (status enum),
    linter.py _ENUMS t05_test, protocol_checker.py _TERMINAL_STATUS
    t05_test, governance P00.14.3 (Test: executed with passing results).
  technical_notes: >
    Measured impact of aliasing (planner simulation at 12222b3, aliases
    t07_change, t06_issue, t03_prompt, t04_test, t05_result mapped to the
    rule sets): linter.py dev goes from 0 errors and 93 warnings to 0
    errors and 101 warnings (8 closed changes without issue_ref);
    protocol_checker.py dev goes from 0 errors and 0 warnings to 13
    errors and 7 warnings, all in 7 closed short prompts (155cc014, 53c6f252, 793992ae, 82dbf16a,
    bdc6820f, e58fd295, ee5357ec: empty specification.description or
    design.components) and their changes (no prompt_ref back-reference).
    They are short prompts for Phase 2 changes that Claude implemented in
    the planning session (operator decision 2026-10-01, recorded in each
    prompt's target_profile comment), and they lie in closed/
    directories, which requirements-eb782f83 CON-04 treats as frozen. The numbered values in use: retired scheme
    t01_design to t08_audit (templates and 118 occurrences in dev/),
    template scheme t01_requirements to t08_audit (23 documents in dev/); t08_audit is
    the same in both. No engine, Overwatch or test code outside the two
    checkers reads schema_type (repository search).

resolution:
  approach: "To be defined in change-e4428fd5."
  change_ref: "change-e4428fd5"

traceability:
  design_refs: ["governance.md Appendix A.5", "governance.md P00.14.3", "requirements-14e05e35"]
  change_refs: ["change-e4428fd5"]

notes: "Audit references: audit-caab2052 M-03, L-11, §10.0 group 3, §14.0; audit-eb782f83 F-04. Operator decision 2026-11-05 (M-03 approach). Operator decisions 2026-11-07: findings for the closed short prompts reported as warnings, not errors; terminal status superseded for test documents only; L-11 fixed with type checks; prompt template schema_type (see change-e4428fd5)."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial issue for Stage C work item 3 (audit-caab2052 group 3)"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Status resolved: change-e4428fd5 implemented with Amendment 1 (P03.7)"]
  - version: "1.2"
    date: "2026-11-07"
    changes: ["Status closed: change-e4428fd5 verified (macOS suite 734 passed; follow-up audit audit-e4428fd5-followup-2026-11-07)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
