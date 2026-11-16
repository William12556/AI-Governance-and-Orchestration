Created: 2026 November 7

```yaml
issue_info:
  id: "issue-9377f9b9"
  title: "Checker hygiene: unparsable and deeply nested YAML, closed test on the full path, boolean iteration, checker test gaps"
  date: "2026-11-07"
  status: "closed"  # change-9377f9b9 verified 2026-11-14
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-9377f9b9"
    change_iteration: 1

source:
  origin: "code_review"  # audit-e4428fd5 F-01 to F-04, F-08; report-e4428fd5 §8.6 item 2
  description: >
    Stage C work item 5A (dev/task.md work item 5 parts (g) for the
    checkers and the manifest loader, (j), (k), (l)), with work item 6 (d)
    folded in, and the operator decisions of 2026-11-07 (D1 to D5, see
    change-9377f9b9).

affected_scope:
  components:
    - { name: "linter", file_path: "ai/engine/src/linter.py" }
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py" }
    - { name: "manifest loader", file_path: "ai/engine/src/manifest.py" }
  designs:
    - { design_ref: "governance.md Appendix A.5 (class resolution, closed records)" }
    - { design_ref: "requirements-14e05e35 NFR-04 (file and field reported)" }
  version: "main 0a79ff0; governance 12.9"

reproduction:
  prerequisites: "main 0a79ff0"
  steps:
    - "(g) a governance document whose first YAML block nests 5,000 levels; run linter.py and protocol_checker.py on its workspace; a manifest.yaml nested the same way passed to load_manifest"
    - "(k) a change document whose first YAML block is 'change_info: ['; run both checkers"
    - "(k) run both checkers on dev/: prompt/closed/prompt-5e8aea4f-loop-robustness-followup.md and prompt/closed/prompt-711a57d5-loop-robustness.md have YAML blocks that do not parse and are reported by neither"
    - "(j) place a workspace below a directory named closed; an active prompt without metadata and with an empty specification.description gets no finding from protocol_checker"
    - "(l) a change document with iteration: true"
  frequency: "always, under the stated condition"
  error_output: "(g) RecursionError: maximum recursion depth exceeded, with a traceback, from both checkers and from load_manifest"

behavior:
  expected: >
    (g) deeply nested YAML gives a finding naming the file from the
    linter, is skipped by protocol_checker, and gives a ManifestError
    from load_manifest. (k) a YAML block that does not parse is reported.
    (j) whether a document is closed is decided below the workspace
    directory. (l) a boolean iteration is rejected.
  actual: >
    (g) _extract_yaml (linter.py) and load_manifest (manifest.py) catch
    only yaml.YAMLError; RecursionError ends the run. (k) _extract_yaml
    returns None on a parse error, check_yaml returns no finding and
    load_workspace skips the document. (j) check_yaml and load_workspace
    pass the full path to resolve_class, which tests every component for
    'closed'. (l) isinstance(iter_val, int) accepts True.
  impact: "A malformed or hostile document ends a check run without naming the file; a governance document with broken YAML is never validated and nothing says so; a workspace stored below a directory named closed loses class inference; a boolean iteration passes."
  workaround: "Inspect documents by hand; keep projects out of directories named closed."

environment:
  os: "platform-independent"

analysis:
  root_cause: >
    Line numbers at main 0a79ff0. (g) linter.py:166-174 (_extract_yaml
    catches yaml.YAMLError only), used by protocol_checker.py
    load_workspace (:124-160); manifest.py:120-127 (OSError and
    yaml.YAMLError only). (k) linter.py:172-174 and check_yaml
    (:307-320, returns when data is None). (j) linter.py resolve_class
    (:206-245, 'closed' in every component of the given path), called
    with the full path from check_yaml (:329) and load_workspace (:152).
    (l) linter.py:372.
  technical_notes: >
    Measured at 0a79ff0 (planner): two governance documents in dev/ have
    a first YAML block that does not parse, both in prompt/closed/
    (5e8aea4f 'while parsing a block mapping', 711a57d5 'while scanning
    a quoted scalar'). A third, proposals/closed/proposal-claude-code-
    2.1.0-governance-enhancements.md, is not a governance document by
    name and is not checked. Closed documents are frozen
    (requirements-eb782f83 CON-04), so an ERROR for them would fail the
    corpus test. protocol_checker already computes in_closed relative to
    the workspace (load_workspace :140). Work item 6 (d) lists the
    checker mutations that survived audit-e4428fd5 (X01, X06, X11, X18,
    X19, X25).

resolution:
  approach: "To be defined in change-9377f9b9."
  change_ref: "change-9377f9b9"

traceability:
  design_refs: ["governance.md Appendix A.5", "requirements-14e05e35 NFR-04"]
  change_refs: ["change-9377f9b9"]

notes: "References: audit-e4428fd5 F-01, F-02, F-03, F-04, F-08 (dev/audit/audit-e4428fd5-followup-2026-11-07.md); report-e4428fd5 §8.6 item 2; dev/task.md work items 5 (g), (j), (k), (l) and 6 (d). Operator decisions 2026-11-07: D1 ERROR active, WARN closed; D2 workspace-relative path; D3 ManifestError; D4 boolean iteration rejected; D5 work item 6 (d) folded in."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial issue for Stage C work item 5A"]
  - version: "1.1"
    date: "2026-11-07"
    changes: ["Status resolved: change-9377f9b9 implemented (P03.7)"]
  - version: "1.2"
    date: "2026-11-14"
    changes: ["Status closed: change-9377f9b9 verified. Approver: operator (one-time session exemption, 2026-11-14). Linux cloud suite 766 passed, 2 skipped; macOS operator suite and P02.8.2 follow-up audit deferred to after the session"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
