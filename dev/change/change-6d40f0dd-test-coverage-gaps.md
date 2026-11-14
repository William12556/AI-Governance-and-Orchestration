Created: 2026 November 14

```yaml
change_info:
  id: "change-6d40f0dd"
  title: "Test coverage gaps: tests for the surviving mutations of the follow-up audits, repo fixture without commit signing, re-measured audit-caab2052 §8.0 with tests for pure helpers (Stage C work item 6)"
  date: "2026-11-14"
  status: "approved"  # approver: operator (one-time session exemption, 2026-11-14)
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-6d40f0dd"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-6d40f0dd"
  description: "Remediate dev/task.md work item 6 parts (a), (b), (c), (e) and (f), with the session decisions D1 to D3 of 2026-11-14. Tests only; no file under ai/ or bin/ changes."

scope:
  summary: >
    (B) audit-b8c75bac F-03: tests for X05 and X06 (file_path key in the
    F21 check, top level and in a files item), X16 (infinite gate
    timeout) and X17 (empty gate timeout_seconds). (C) audit-86c958dd
    F-03: tests for X05 (marker mtime equal to started), X09 (absent or
    non-string started) and a hard-link case in the B3 test. (E) The
    repo fixture of tests/engine/test_stages.py sets commit.gpgsign=false
    in the test repository. (F) audit-4b0a5592 F-07: tests for X07, X10,
    X12, X13 and X17, X14 and X18. (A) audit-caab2052 §8.0 is
    re-measured; tests are added for the pure helper functions among the
    remaining gaps; the gaps that remain are registered in dev/task.md.
  affected_components:
    - { name: "coverage gap tests", file_path: "tests/engine/test_coverage_gaps.py", change_type: "create" }  # A, B
    - { name: "stage tests", file_path: "tests/engine/test_stages.py", change_type: "modify" }  # E, F
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py", change_type: "modify" }  # C
    - { name: "task register", file_path: "dev/task.md", change_type: "modify" }  # A: remaining gaps
  affected_designs: []
  out_of_scope:
    - "Any change to ai/engine/, ai/webui/ or bin/"
    - "audit-b8c75bac X03 and X09, audit-86c958dd X03 and X06 (optional in the dispositions; each needs fault injection into a narrow except clause)"
    - "Tests for the §8.0 gaps that need a running loop, a provider or an MCP server stand-in beyond the existing fixtures (registered as remaining)"
    - "A coverage tool (no dependency is added); the re-measurement is by test name and public name, as in the audit"

rational:
  problem_statement: "See issue-6d40f0dd."
  proposed_solution: "One short test per surviving mutation, placed with the fixtures it needs; one line in the repo fixture; a re-measurement table in the report; characterisation tests for pure helpers."
  alternatives_considered:
    - option: "Set commit.gpgsign through GIT_CONFIG_* environment variables in the fixture"
      reason_rejected: "The other fixtures and tests of the file use 'git config commit.gpgsign false' in the test repository; the same form keeps one pattern"
    - option: "Leave (a) as a table only"
      reason_rejected: "Several remaining gaps are pure functions that a few lines cover; the prompt asks for the tasks to be completed as far as possible"
  benefits:
    - "The named mutations no longer survive"
    - "The suite does not depend on the machine's signing configuration"
  risks:
    - risk: "Characterisation tests fix current behaviour, including behaviour nobody specified"
      mitigation: "Only documented behaviour (docstrings, design) is asserted; the report lists the functions"

technical_details:
  current_behavior: "See issue-6d40f0dd behavior.actual."
  proposed_behavior: "Tests only; see testing_requirements. The repo fixture runs 'git config commit.gpgsign false' after 'git init'."
  implementation_approach: "Implemented by the autonomous session of 2026-11-14 (worker and reviewer; prompt-cf99f3f3) on the session branch. No T03 prompt (report-b3a503a2 §5.0 decision 1). Each new test is shown to fail under its mutation on a temporary copy."
  code_changes:
    - component: "tests"
      file: "tests/engine/test_coverage_gaps.py; tests/engine/test_stages.py; tests/webui/test_overwatch.py"
      change_summary: "New tests; repo fixture"
      functions_affected: ["repo (fixture)"]
  interface_changes: []

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "pytest and git as before" }

testing_requirements:
  test_approach: "pytest; no network (NFR-06). Each mutation is applied to a temporary copy and the named test must fail."
  test_cases:
    - { scenario: "B X05, X06: an overwrite of audit-report.md given by file_path, at the top level and in a files item; test_b_f21_file_path_key[top|files]", expected: "the write is refused with the F21 message" }
    - { scenario: "B X16: gates.pytest.timeout_seconds .inf and -.inf; test_b_infinite_gate_timeout_is_refused", expected: "configuration error; no state written" }
    - { scenario: "B X17: an empty gates.pytest.timeout_seconds key; test_b_empty_gate_timeout_is_refused", expected: "configuration error; no state written" }
    - { scenario: "C X05: BLOCKED.md and .complete with mtime equal to the record's started second; test_c_marker_at_the_start_second_counts", expected: "status blocked and ship" }
    - { scenario: "C X09: a record without started, and with a non-string started; test_c_absent_or_non_string_started_keeps_the_precedence", expected: "status blocked for an old BLOCKED.md" }
    - { scenario: "C M7: the run's task file is a hard link to the open prompt; test_c_fr_02_06_hard_link_is_the_same_file", expected: "no FR-02-06 alert" }
    - { scenario: "E: the repo fixture; test_e_repo_fixture_disables_commit_signing", expected: "git config commit.gpgsign is false in the fixture repository, also with GIT_CONFIG_GLOBAL setting it true" }
    - { scenario: "F X07: a free-text task in loop mode; test_f_free_text_task_prints_no_tracking_warning", expected: "no 'not tracked' line and no 'work item None'" }
    - { scenario: "F X10: git add fails (ai/approvals.yaml ignored); test_f_failed_git_add_restores_the_file", expected: "exit 1 naming 'add'; the file is absent again; nothing staged" }
    - { scenario: "F X12: a hook that writes to both streams; test_f_failure_detail_prefers_stderr", expected: "the detail is the stderr text" }
    - { scenario: "F X13, X17: the write-back fails; test_f_restoration_failure_is_reported", expected: "the message ends with 'could not be restored: <reason>'" }
    - { scenario: "F X14: another file staged before a failed call; test_f_failed_call_leaves_other_staged_files", expected: "the other file is still staged" }
    - { scenario: "F X18: a nested project without approvals below a project with them; test_f_nested_project_does_not_read_the_outer_approvals", expected: "committed_approvals of the nested project is empty" }
    - { scenario: "A: check_context_budget, _strip_verdict, _truncate_tool_result, extract_reasoning, format_tool_signatures, _substitute_project_root, _parse_audit_items, gates.pytest_targets, parser.parse_tool_calls; test_a_* in test_coverage_gaps.py", expected: "the documented results" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline on Linux; macOS suite run by the operator after the session"
    - "Each of the mutations X05, X06, X16, X17 (audit-b8c75bac), X05, X09, M7 (audit-86c958dd), X07, X10, X12, X13, X14, X18 (audit-4b0a5592) fails its named test; the fixture line removed fails test_e under a signing configuration"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "No file under ai/ or bin/ in the unit's diff"

implementation:
  effort_estimate: "2 hours"
  implementation_steps:
    - { step: "Tests and mutation runs", owner: "session (worker)" }
    - { step: "Independent review (prompt-cf99f3f3 §8.4)", owner: "session (fresh reviewer subagent)" }
    - { step: "macOS suite", owner: "operator, after the session" }
  rollback_procedure: "Revert the test commits."
  deployment_notes: "tests/ is not propagated. No follow-up audit is required for a change that touches tests only (P02.8.2 applies to remediation that changed source code); the operator may waive it in the audits' closure blocks."

traceability:
  related_changes:
    - { change_ref: "change-b8c75bac", relationship: "tests for audit-b8c75bac F-03" }
    - { change_ref: "change-86c958dd", relationship: "tests for audit-86c958dd F-03" }
    - { change_ref: "change-4b0a5592", relationship: "tests for audit-4b0a5592 F-07, F-10" }
    - { change_ref: "change-d4f527e7", relationship: "follows (approve._write_atomic used by the X13 test)" }
  related_issues:
    - { issue_ref: "issue-6d40f0dd", relationship: "source" }

notes: "Session decisions 2026-11-14 under the operator's one-time exemption (prompt-cf99f3f3 §1.0 item 5): D1 the optional mutation X06 of audit-b8c75bac is taken, X03 and X09 there and X03 and X06 of audit-86c958dd are not; D2 part (a) is a re-measurement by name plus tests for pure helpers; D3 the remaining §8.0 gaps are registered in dev/task.md as one row."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Approved as drafted. Approver: operator (one-time session exemption, 2026-11-14)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
