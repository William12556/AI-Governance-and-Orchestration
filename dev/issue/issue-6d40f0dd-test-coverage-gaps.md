Created: 2026 November 14

```yaml
issue_info:
  id: "issue-6d40f0dd"
  title: "Test coverage gaps: surviving mutations of the follow-up audits, the repo fixture's signing configuration, and the re-measurement of audit-caab2052 §8.0"
  date: "2026-11-14"
  status: "resolved"  # change-6d40f0dd implemented 2026-11-14 (P03.7)
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-6d40f0dd"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 §8.0; audit-b8c75bac F-03; audit-86c958dd F-03; audit-4b0a5592 F-07, F-10; report-4b0a5592 §6.0 item 2
  description: >
    Stage C work item 6 (dev/task.md row 6d40f0dd), parts (a), (b), (c),
    (e) and (f). Part (d) closed with change-9377f9b9. Raised by the
    autonomous session of 2026-11-14 (prompt-cf99f3f3, report-b3a503a2)
    under the operator's one-time exemption.

affected_scope:
  components:
    - { name: "loop robustness tests", file_path: "tests/engine/test_loop_robustness.py" }
    - { name: "configuration tests", file_path: "tests/engine/test_config_validation.py" }
    - { name: "stage tests", file_path: "tests/engine/test_stages.py" }
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py" }
  designs:
    - { design_ref: "requirements-14e05e35 NFR-06 (offline tests)" }
  version: "main 9b75595, with change-bae631c7, change-d4f527e7 and change-541f5c58 of the session"

reproduction:
  prerequisites: "the session branch at 51d0f26"
  steps:
    - "(b) apply mutations X05, X16 and X17 of audit-b8c75bac §6.0 and run the suite: no test fails"
    - "(c) apply mutations X05, X09 and M7 of audit-86c958dd §6.0 on Linux and run the suite: no test fails"
    - "(e) run the suite offline on a machine with global commit.gpgsign=true and a signer that needs the network: tests using the repo fixture fail"
    - "(f) apply mutations X07, X10, X12, X13, X14, X17 and X18 of audit-4b0a5592 §6.0: no test fails"
    - "(a) search tests/ for each public name listed in audit-caab2052 §8.0"
  frequency: "always"
  error_output: "(e) 47 errors in tests that use the repo fixture (audit-4b0a5592 F-10)."

behavior:
  expected: >
    Each behaviour named by the audits has a test that fails when the
    behaviour is removed. The repo fixture commits without depending on
    the machine's signing configuration. The state of the §8.0 gaps is
    known after the changes of work items 1 to 5.
  actual: >
    The named mutations survive. The repo fixture in
    tests/engine/test_stages.py sets the author and committer identity
    but not commit.gpgsign. audit-caab2052 §8.0 was measured at 24b2dfc
    (331 tests) and not since.
  impact: "A regression in one of the named behaviours would not be detected. The offline suite depends on the machine."
  workaround: "(e) git config --global commit.gpgsign false on the test machine."

environment:
  os: "platform-independent; the hard-link case needs a file system with hard links"

analysis:
  root_cause: >
    The follow-up audits record the surviving mutations in their §6.0
    tables; the registered subsets are those of dev/task.md work item 6
    (b), (c) and (f). (e): tests/engine/test_stages.py repo fixture.
  technical_notes: >
    X13 and X17 of audit-4b0a5592 concern a failed restoration in
    approve.py; since change-d4f527e7 the write-back goes through
    approve._write_atomic, which a test can make fail. X02 and X04 were
    covered by change-d4f527e7. The optional mutations (audit-b8c75bac
    X03, X06, X09; audit-86c958dd X03, X06) are taken where one short
    case covers them.

resolution:
  approach: "To be defined in change-6d40f0dd."
  change_ref: "change-6d40f0dd"

traceability:
  design_refs: ["requirements-14e05e35 NFR-06"]
  change_refs: ["change-6d40f0dd"]

notes: "Audit references: audit-caab2052 §8.0 and §14.0 (decided 2026-11-14 by the session under the one-time exemption); audit-b8c75bac F-03; audit-86c958dd F-03; audit-4b0a5592 F-07, F-10; report-4b0a5592 §6.0 item 2 (dev/reports/closed/)."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial issue for Stage C work item 6"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Status resolved: change-6d40f0dd implemented (P03.7)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
