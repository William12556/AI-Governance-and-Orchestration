Created: 2026 November 7

```yaml
change_info:
  id: "change-e4428fd5"
  title: "Governance checkers: class-word schema_type, aliases, type checks, superseded tests, checker tests (Stage C work item 3)"
  date: "2026-11-07"
  status: "approved"  # operator approval 2026-11-07
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e4428fd5"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-e4428fd5"
  description: "Remediate audit-caab2052 M-03 and L-11, add tests for both checkers, and add a terminal status for superseded test documents, with the operator decisions of 2026-11-05 (audit-caab2052 §14.0) and 2026-11-07."

scope:
  summary: >
    (A) schema_type uses class words: requirements, design, prompt, test,
    result, issue, change, audit. Both checkers resolve a document's class
    from its schema_type: a class word, or a numbered value of either
    scheme (t01_ to t08_ followed by a class word) as an alias. Without a
    schema_type, the class is inferred from a unique root key
    (prompt_info, test_info, result_info, issue_info, change_info,
    audit_info). An unrecognised value gives a warning. Rule tables are
    keyed by class word. Templates T01, T02 and T04 to T08 emit the class
    word; T03 stays without metadata. (B) In protocol_checker, the prompt
    self-containment check reports WARN instead of ERROR for a prompt in a
    closed/ directory; every other check keeps its severity. (C, L-11)
    Type checks before membership tests and pattern matches in both
    checkers and manifest.py; a malformed value gives a finding or a
    ManifestError naming the file and field. (D) Test documents gain the
    status superseded, which is terminal. (E) Test modules for both
    checkers.
  affected_components:
    - { name: "linter", file_path: "ai/engine/src/linter.py", change_type: "modify" }
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py", change_type: "modify" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "modify" }  # C
    - { name: "templates", file_path: "ai/governance/software-engineering/templates/T01, T02, T04-T08", change_type: "modify" }  # A, D
    - { name: "linter tests", file_path: "tests/engine/test_linter.py", change_type: "add" }
    - { name: "protocol checker tests", file_path: "tests/engine/test_protocol_checker.py", change_type: "add" }
    - { name: "manifest tests", file_path: "tests/engine/test_manifest_gates.py", change_type: "modify" }  # C
    - { name: "governance", file_path: "ai/governance/software-engineering/governance.md", change_type: "modify" }  # planner: P00.14.3, Appendix A.5, version 12.9
    - { name: "governance manifest", file_path: "ai/governance/software-engineering/manifest.yaml", change_type: "modify" }  # planner: version 12.9
  affected_designs:
    - { design_ref: "governance.md", sections: ["P00.14.3 Closure Criteria (Test)", "Appendix A.5 schema_type", "Version History"] }
  out_of_scope:
    - "Editing any closed/ document"
    - "Metadata for the prompt template T03 (its v1.6 design keeps prompts free of governance metadata)"
    - "A terminal status for result documents (T05)"
    - "Changing the severity of any check other than prompt self-containment for closed/ documents"
    - "The protocol citation check (dropped from the register 2026-11-06)"

rational:
  problem_statement: "See issue-e4428fd5."
  proposed_solution: "One class resolver shared by both checkers; rule tables keyed by class word; type checks at every lookup on document values; one added status value; tests."
  alternatives_considered:
    - option: "Migrate every document to one numbered scheme"
      reason_rejected: "Requires editing closed/ documents (requirements-eb782f83 CON-04); operator decision 2026-11-05 retires the numeric prefix instead"
    - option: "Add metadata.schema_type 'prompt' to T03"
      reason_rejected: "Operator decision 2026-11-07: T03 v1.6 removed governance metadata from prompts; the class is inferred from prompt_info"
    - option: "All findings for closed/ documents as WARN"
      reason_rejected: "Operator decision 2026-11-07: validity errors in closed/ documents stay errors (an invalid status in a closed change was caught this way on 2026-11-06)"
    - option: "Check active documents only"
      reason_rejected: "Drops checks that closed documents pass today"
  benefits:
    - "Every governance document is validated by its class rules; an unrecognised schema_type is reported"
    - "Prompts no longer give the missing-schema_type warning"
    - "Malformed YAML values are reported with file and field instead of a traceback"
    - "A test document for removed code can be closed truthfully"
    - "Regressions in either checker are caught by tests"
  risks:
    - risk: "Documents previously skipped are now validated: linter.py dev gains about 8 warnings (closed changes without issue_ref) and protocol_checker.py dev about 7 warnings and 13 self-containment findings, the latter now warnings (issue technical notes)"
      mitigation: "Measured before the change; the report records the before and after counts per check"
    - risk: "A downstream document with a mistyped schema_type that was silently skipped now gives a warning"
      mitigation: "Intended (M-03); a warning does not fail a check run"

technical_details:
  current_behavior: "See issue-e4428fd5 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) linter.py defines CLASS_WORDS = ('requirements', 'design',
    'prompt', 'test', 'result', 'issue', 'change', 'audit'), ROOT_KEYS =
    {'prompt_info': 'prompt', 'test_info': 'test', 'result_info':
    'result', 'issue_info': 'issue', 'change_info': 'change',
    'audit_info': 'audit'} and resolve_class(data) -> tuple[class | None,
    message | None]. A str value that is a class word gives that class; a
    str matching ^t0[1-8]_(<class word>)$ gives the class word; any other
    str gives None and the message "unknown schema_type '<value>'"; a
    non-str value gives None and "metadata.schema_type must be a string".
    An absent schema_type gives the class of the single top-level key of
    the data found in ROOT_KEYS, or None with the existing message
    "YAML block present but metadata.schema_type is missing" when none
    matches. (A2) _ENUMS, _ID_FIELDS, _ITER_FIELDS and _COUPLING in
    linter.py, and _TERMINAL_STATUS, _STATUS_FIELD, _ID_FIELD,
    _COUPLING_PAIRS, MANDATORY_BACK and the 'prompt' checks in
    protocol_checker.py, are keyed by class word. protocol_checker imports
    resolve_class from linter. A message from resolve_class is a WARN
    finding in check_yaml; protocol_checker.load_workspace skips such a
    document without a finding (linter reports it). A known class without
    rules (requirements, design, audit) is not a finding. (A3) Templates
    T01, T02, T04, T05, T06, T07 and T08: metadata.schema_type becomes the
    class word, and the schema section's enum for schema_type lists the
    class word only. T03 is unchanged. (B) check_prompt_self_contained
    reports WARN instead of ERROR when doc.in_closed; the message gains
    ' (closed record)'. (C) Before each membership test, dictionary lookup
    or re operation on a document or manifest value, the value's type is
    checked: linter check_yaml (enum fields: a non-str or unhashable value
    is an ERROR '<field>: invalid value'; id: a non-str id is an ERROR
    '<id field> must be a string'; iteration: as today), check_coupling (a
    non-str reference is an ERROR '<ref field> must be a string');
    protocol_checker load_workspace (a non-str id: the document is skipped
    and linter reports it), _uuid_from_id and every coupling check (a
    non-str reference is skipped by protocol_checker and reported by
    linter); manifest.py stage gates (a non-str entry raises ManifestError
    for '<stage>.gates': 'entries must be strings'). No check raises for
    any YAML value shape. (D) The test status enum gains superseded:
    templates/T04-test.md status comment and schema enum, linter _ENUMS
    test, protocol_checker _TERMINAL_STATUS test = {passed, superseded}.
    (E) New tests/engine/test_linter.py and test_protocol_checker.py.
  implementation_approach: "Claude Code cloud session per a T04 prompt after approval, on a session branch. The planner updates governance.md (P00.14.3, Appendix A.5, version 12.9) and manifest.yaml (version 12.9) after review."
  code_changes:
    - component: "linter"
      file: "ai/engine/src/linter.py"
      change_summary: "A1 resolve_class; A2 tables by class word; C type checks; D superseded"
      functions_affected: ["resolve_class (new)", "check_yaml", "check_coupling", "run", "rule tables"]
    - component: "protocol checker"
      file: "ai/engine/src/protocol_checker.py"
      change_summary: "A2 tables by class word, resolve_class; B closed-prompt WARN; C type checks; D terminal status"
      functions_affected: ["load_workspace", "_uuid_from_id", "check_uuid_chain", "check_bidirectional", "check_one_to_one", "check_status_consistency", "check_lifecycle_placement", "check_prompt_self_contained", "rule tables"]
    - component: "manifest loader"
      file: "ai/engine/src/manifest.py"
      change_summary: "C gate entries must be strings"
      functions_affected: ["stage validation in load_manifest"]
    - component: "templates"
      file: "ai/governance/software-engineering/templates/T01, T02, T04-T08"
      change_summary: "A3 class word; D superseded in T04"
      functions_affected: []
  interface_changes:
    - interface: "metadata.schema_type"
      change_type: "contract"
      details: "Class words; numbered values of both schemes accepted as aliases; absent value inferred from a unique root key; unknown value warned"
      backward_compatible: "yes: every value in use is accepted"
    - interface: "Test status"
      change_type: "contract"
      details: "superseded added; terminal"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library and PyYAML only" }

testing_requirements:
  test_approach: "pytest with tmp_path workspaces; no network (NFR-06)."
  test_cases:
    - { scenario: "A1: resolve_class for each class word, each of the 15 numbered values, 't09_change', 'change ', 'Change', 'foo', a list, and an absent value with each root key and with project_info", expected: "class word for the 23 accepted spellings and the six root keys; None with the stated message otherwise" }
    - { scenario: "A2: the audit-caab2052 fixture (a change with four defects) as t02_change, t07_change and change", expected: "the same four findings for each" }
    - { scenario: "A2: an issue, a prompt, a test and a result document in each spelling", expected: "same findings per spelling" }
    - { scenario: "A2: a design, requirements and audit document", expected: "no unknown-type finding" }
    - { scenario: "A2: a prompt without metadata", expected: "no missing-schema_type warning; prompt rules applied" }
    - { scenario: "A3: every template under ai/governance/software-engineering/templates", expected: "T01, T02, T04-T08 metadata.schema_type is a class word; T03 has none and resolves to prompt" }
    - { scenario: "B: a prompt with empty specification.description in prompt/ and in prompt/closed/", expected: "ERROR active; WARN with '(closed record)' closed" }
    - { scenario: "B: a closed change with an invalid status", expected: "ERROR (severity unchanged)" }
    - { scenario: "C: schema_type, id, an enum field and a coupling reference each as a list, a mapping and an int; a manifest stage gates list holding a mapping", expected: "findings or ManifestError naming file and field; no exception" }
    - { scenario: "D: a test document with status superseded in test/closed/; with status executed in test/closed/", expected: "superseded: no finding; executed: lifecycle finding as today" }
    - { scenario: "E: one test per existing check of both checkers (naming, structure, yaml, coupling, links; uuid chain, bidirectional, one-to-one, status consistency, lifecycle placement, prompt self-containment)", expected: "each check fires on a minimal defective fixture and is silent on a valid one" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline; macOS suite run by the operator"
    - "Mutations: removing the alias rule, the root-key inference, the closed-prompt downgrade, a type check and the superseded value each fail a named test"
    - "linter.py dev and protocol_checker.py dev: 0 errors; the report lists the warning counts before and after, per check"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "4-6 hours"
  implementation_steps:
    - { step: "Source, templates and tests (prompt-e4428fd5)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "governance.md P00.14.3, Appendix A.5, version 12.9; manifest.yaml 12.9", owner: "planner" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation after Stage C work item 6. No downstream document needs editing: every value in use is accepted. No live engine check is needed; the checkers run offline."

traceability:
  related_changes:
    - { change_ref: "change-eb782f83", relationship: "follows up (protocol and template reordering; audit-eb782f83 F-04)" }
  related_issues:
    - { issue_ref: "issue-e4428fd5", relationship: "source" }

notes: "Operator decisions: 2026-11-05 (audit-caab2052 §14.0, M-03 approach); 2026-11-07 (closed-prompt self-containment as WARN only; superseded for test documents only; L-11 with type checks; class of a prompt inferred from prompt_info, T03 unchanged). Count: 15 distinct numbered values (t08_audit is the same in both schemes), not 14 as in the earlier register wording."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Approved by the operator as drafted; implementation per prompt-e4428fd5"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
