Created: 2026 November 7

```yaml
change_info:
  id: "change-9377f9b9"
  title: "Checker hygiene: report unparsable and deeply nested YAML, closed test below the workspace, reject boolean iteration, checker tests (Stage C work item 5A)"
  date: "2026-11-07"
  status: "approved"  # operator approval 2026-11-07
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-9377f9b9"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-9377f9b9"
  description: "Remediate dev/task.md work item 5 parts (g) for the checkers and manifest loader, (j), (k), (l), and work item 6 (d), with the operator decisions of 2026-11-07 (D1 to D5)."

scope:
  summary: >
    (A, k and g; D1) When a governance document's first fenced YAML block
    does not parse, or nests too deeply (RecursionError), linter
    check_yaml reports 'YAML block does not parse: <problem>': ERROR for a
    document outside closed/, WARN ending ' (closed record)' for one
    inside closed/ (closed measured below the workspace directory).
    protocol_checker skips the document as today and no longer raises.
    (B, j; D2) Both checkers pass resolve_class the document's path
    relative to the workspace directory. (C, g; D3) load_manifest maps
    RecursionError to ManifestError '<path>: invalid YAML: nesting too
    deep'. (D, l; D4) A boolean iteration gives the existing iteration
    error. (E; D5) Tests, including the work item 6 (d) gaps.
  affected_components:
    - { name: "linter", file_path: "ai/engine/src/linter.py", change_type: "modify" }  # A, B, D
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py", change_type: "modify" }  # B
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py", change_type: "modify" }  # C
    - { name: "linter tests", file_path: "tests/engine/test_linter.py", change_type: "modify" }
    - { name: "protocol checker tests", file_path: "tests/engine/test_protocol_checker.py", change_type: "modify" }
    - { name: "manifest tests", file_path: "tests/engine/test_manifest_gates.py", change_type: "modify" }
    - { name: "governance", file_path: "ai/governance/software-engineering/governance.md", change_type: "modify" }  # planner: Appendix A.5 sentence, version 12.10
    - { name: "governance manifest", file_path: "ai/governance/software-engineering/manifest.yaml", change_type: "modify" }  # planner: version 12.10
  affected_designs:
    - { design_ref: "governance.md", sections: ["Appendix A.5", "Version History"] }
  out_of_scope:
    - "Editing any closed/ document"
    - "_load_config in orchestrator.py (work item 5 (g), change 5B)"
    - "stages.py document scan (work item 5 (n), change 5B)"
    - "YAML blocks after the first one in a document"
    - "Non-governance documents (names not matching MASTER_RE or NORMAL_RE)"

rational:
  problem_statement: "See issue-9377f9b9."
  proposed_solution: "One parse helper in linter.py that returns the data or a problem text; check_yaml reports the problem with a severity by location; _extract_yaml keeps its contract for protocol_checker; workspace-relative paths for class inference; one added type check; one added exception mapping."
  alternatives_considered:
    - option: "ERROR for every unparsable block"
      reason_rejected: "Two closed prompts in dev/ would fail the corpus test; closed records are frozen (CON-04); operator decision D1"
    - option: "WARN for every unparsable block"
      reason_rejected: "An active document with broken YAML is a defect to fix before use; operator decision D1"
    - option: "Raise the recursion limit"
      reason_rejected: "Moves the threshold without removing the traceback"
  benefits:
    - "No governance document with broken YAML is silently skipped"
    - "No YAML shape ends a check run or the manifest load with a traceback"
    - "Class inference works for a project below a directory named closed"
  risks:
    - risk: "A downstream active document with broken YAML now fails linter.py"
      mitigation: "Intended; the pre-propagation checker run of work item 8e finds it"
    - risk: "dev/ gains two linter warnings (the two closed prompts)"
      mitigation: "Measured; a warning does not fail a check run"

technical_details:
  current_behavior: "See issue-9377f9b9 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) linter.py gains _parse_yaml_block(content) -> tuple[data, problem]:
    no fenced block gives (None, None); a block that loads gives (data,
    None); yaml.YAMLError gives (None, e.problem if set, else the first
    line of str(e)); RecursionError gives (None, 'nesting too deep').
    _extract_yaml(content) returns the data element, so it never raises
    and protocol_checker.load_workspace skips such a document as today.
    (A2) check_yaml(path, content, workspace_dir=None): with a problem, one
    finding 'YAML block does not parse: <problem>'; severity WARN with the
    suffix ' (closed record)' when a component of the path relative to
    workspace_dir (or of path when workspace_dir is None) is 'closed',
    otherwise ERROR; returns (findings, None, None). run passes its
    workspace_dir. (B) check_yaml passes resolve_class the path relative to
    workspace_dir when given; load_workspace passes os.path.relpath(path,
    workspace_dir). resolve_class is unchanged. (C) load_manifest: except
    RecursionError raises ManifestError(f'{path}: invalid YAML: nesting
    too deep'). (D) check_yaml iteration: a bool value gives the existing
    ERROR "iteration must be integer ≥ 1, got '<value>'". (E) Tests.
  implementation_approach: "Claude Code cloud session per prompt-9377f9b9 after approval, on a session branch. The planner updates governance.md Appendix A.5 and the version (12.10) in governance.md and manifest.yaml after review."
  code_changes:
    - component: "linter"
      file: "ai/engine/src/linter.py"
      change_summary: "A _parse_yaml_block, check_yaml parse finding by location; B workspace-relative inference path; D boolean iteration"
      functions_affected: ["_parse_yaml_block (new)", "_extract_yaml", "check_yaml", "run"]
    - component: "protocol checker"
      file: "ai/engine/src/protocol_checker.py"
      change_summary: "B workspace-relative inference path"
      functions_affected: ["load_workspace"]
    - component: "manifest loader"
      file: "ai/engine/src/manifest.py"
      change_summary: "C RecursionError as ManifestError"
      functions_affected: ["load_manifest"]
  interface_changes:
    - interface: "linter.check_yaml"
      change_type: "signature"
      details: "Optional workspace_dir parameter; existing calls unchanged"
      backward_compatible: "yes"
    - interface: "linter findings"
      change_type: "behavior"
      details: "New finding 'YAML block does not parse: <problem>' (ERROR active, WARN closed)"
      backward_compatible: "no for active documents with broken YAML, which were skipped"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library and PyYAML only" }

testing_requirements:
  test_approach: "pytest with tmp_path workspaces; no network (NFR-06)."
  test_cases:
    - { scenario: "A: a change document with 'change_info: [' in change/ and in change/closed/", expected: "ERROR active; WARN ending '(closed record)' closed; protocol_checker gives no finding and does not raise" }
    - { scenario: "A, g: a 5,000-level nested first YAML block, active and closed", expected: "'YAML block does not parse: nesting too deep' with the same severities; both checkers' run() return normally" }
    - { scenario: "A: a document without a YAML block", expected: "no parse finding" }
    - { scenario: "B: a workspace below a directory named closed: an active prompt without metadata and with an empty description; an active change without schema_type", expected: "class inferred; the prompt self-containment ERROR; the linter treats the change as active" }
    - { scenario: "C: load_manifest on a 5,000-level nested manifest.yaml", expected: "ManifestError naming the path with 'invalid YAML: nesting too deep'" }
    - { scenario: "D: iteration true and false", expected: "the iteration ERROR" }
    - { scenario: "E (work item 6 (d)): t02_changes; a path component or file name containing 'closed' as a substring; a str change status with a non-str issue status and the reverse in check_status_consistency; an empty deliverable.files in the closed self-containment fixture; [] and 0 as an id", expected: "unknown schema_type; inference applied; no status_consistency finding and no exception; the deliverable.files finding as WARN (closed record); the 'must be a string' ERROR" }
    - { scenario: "Corpus: both checkers on dev/", expected: "0 errors; the linter reports the two closed prompts as WARN" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline; macOS suite run by the operator"
    - "Mutations: RecursionError not caught; parse problem ignored; closed severity ERROR; active severity WARN; full path passed to resolve_class; bool iteration accepted; manifest RecursionError not mapped; each fails a named test"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "2-3 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-9377f9b9)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "governance.md Appendix A.5 and version 12.10; manifest.yaml 12.10", owner: "planner" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation after Stage C work item 6. The checkers run offline; no live engine check is needed."

traceability:
  related_changes:
    - { change_ref: "change-e4428fd5", relationship: "follows up (audit-e4428fd5 F-01 to F-04, F-08)" }
  related_issues:
    - { issue_ref: "issue-9377f9b9", relationship: "source" }

notes: "Operator decisions 2026-11-07: D1 unparsable YAML is ERROR outside closed/ and WARN (closed record) inside; D2 workspace-relative path for class inference; D3 RecursionError in load_manifest as ManifestError; D4 boolean iteration rejected; D5 work item 6 (d) folded into this change."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Approved by the operator as drafted; implementation per prompt-9377f9b9"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
