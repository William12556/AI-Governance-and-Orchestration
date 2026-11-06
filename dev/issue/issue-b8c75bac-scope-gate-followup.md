Created: 2026 November 5

```yaml
issue_info:
  id: "issue-b8c75bac"
  title: "Engine argument and config robustness: refused-call edit check, write verbs, audit-report write check, timeout extremes, config validation, read-path normalisation, test gaps"
  date: "2026-11-05"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 2
  coupled_docs:
    change_ref: "change-b8c75bac"
    change_iteration: 2

source:
  origin: "code_review"  # follow-up audits audit-a5bd4fe1 and audit-5e8aea4f; audit-14e05e35 L-08; d7f4a1c8 P08 review
  description: >
    (A) Findings F-01, F-02 and F-04 of
    dev/audit/audit-a5bd4fe1-followup-2026-11-05.md (§8.4, §11.0), with the
    operator decision of 2026-11-05 to fix F-01 and F-02 and to add the tests
    U1, U4, U5 and U10. F-03 and F-05 were documented by the planner; F-06 to
    F-08 need no action.
    (B) Findings F-01 to F-04 of
    dev/audit/audit-5e8aea4f-followup-2026-11-04.md (§8.4).
    (C) audit-14e05e35 L-08 (NFR-04 gaps in config validation).
    (D) The d7f4a1c8 P08 review note on read-path normalisation at the F28
    wall-clock-cap early return.
    (B) to (D) were added in iteration 2 (2026-11-06) as Stage C work item 1
    (dev/task.md).

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "scope", file_path: "ai/engine/src/scope.py" }
    - { name: "providers", file_path: "ai/engine/src/providers.py" }
    - { name: "mcp client", file_path: "ai/engine/src/mcp_client.py" }
    - { name: "engine tests", file_path: "tests/engine/test_scope_gate_hardening.py" }
    - { name: "engine tests", file_path: "tests/engine/test_loop_robustness.py" }
  designs:
    - { design_ref: "design-14e05e35 §3.0 (Timeouts), §7.0 (tool classification), §11.0 (Error Handling)" }
    - { design_ref: "requirements-14e05e35 NFR-04 (configuration errors)" }
  version: "governance 12.8; engine at main 7440752 (engine source unchanged since change-a5bd4fe1)"

reproduction:
  prerequisites: "Engine at main 7440752"
  steps:
    - "A F-01: the worker calls edit_file with a path that contains E_INVALID_INPUT and lies outside the project, or with such a path that also contains NUL"
    - "A F-02: offer a tool named searchAndReplace, read_and_append or list_update"
    - "A F-04: apply mutations U1, U4, U5 and U10 of audit-a5bd4fe1 §6.0"
    - "B F-01: in an audit run with a non-empty audit-report.md, call write_file {'path': ['src/x.py']}, or write audit-report.md with a non-string content"
    - "B F-02: set loop.mcp_timeout_seconds to 1e14; set loop.mcp_timeout_seconds or providers.<name>.request_timeout_seconds to an integer beyond the float range (for example a 400-digit number)"
    - "B F-03: apply mutations N2b, N5 and N12 of audit-5e8aea4f §6.0"
    - "B F-04: remove the loop.mcp_timeout_seconds validation; run tests/engine/test_loop_robustness.py"
    - "C: run the engine with no config file; with no loop: block; with no loop.state_dir; with providers.<name>.max_tokens: 'many' on an anthropic provider; with gates.<name>.timeout_seconds: -1 in ai/config.yaml"
    - "D: let a reviewer or audit phase reach the phase wall-clock cap after reading a file by a relative path; compare the returned read set with the abspath-normalised set of the other exits"
  frequency: "always, under the stated condition"
  error_output: >
    A F-01 (probe): an out-of-project file is compiled; with NUL,
    ValueError: embedded null byte ends the engine run without BLOCKED.md.
    B F-01 (audit-5e8aea4f probe A2): TypeError from os.path.basename, or
    AttributeError from .strip(), as a traceback with no BLOCKED.md.
    B F-02 (probes C1 to C3): 'Warning: failed to connect' for every MCP
    server and a run with no tools; OverflowError instead of the config
    error message. C: KeyError, ValueError or FileNotFoundError tracebacks.

behavior:
  expected: >
    A F-01: the edit-failure corrective and its compile run only for a call
    that was dispatched, and no compile error at the edit-failure or
    post-write site ends the run. A F-02: a tool name that contains a write
    verb, in any letter case, is a write tool. A F-04: the status
    combinations of the pytest gate, the preflight bytecode placement, FR-D
    on the audit path and the refused-call case each have a test.
    B F-01: the F21 audit-report check ignores non-string paths and treats a
    non-string content as empty; it never raises. B F-02: a timeout above a
    stated maximum, or one that cannot be converted to a float, is reported
    with the existing config error message, before state is created. B F-03:
    the anthropic secret wiring, the Anthropic API readiness redaction and
    the propagation of BaseException from MCPClient.close each have a test.
    B F-04: T16 and T20 isolate the engine logger. C: a missing config file,
    a missing loop: block or loop.state_dir, a non-numeric max_tokens and an
    invalid gate timeout_seconds in ai/config.yaml are each reported as a
    config error naming the file and field, with exit 1 and no traceback.
    D: every run_phase exit returns abspath-normalised read paths.
  actual: >
    A F-01: _edit_pattern_failed tests only the tool name and the result
    text; a refusal echoes the worker's path, so the marker can come from the
    path; only TimeoutExpired is caught around compile_file. A F-02: write
    verbs are a fixed lower-case list matched case-sensitively, so
    read-prefixed names with a capitalised or unlisted verb are read-only.
    A F-04: mutations U1, U4, U5 and U10 survive the suite. B F-01: the
    check takes path, file_path and files[].path without a type test and
    calls .strip() on content. B F-02: values of about 8.64e13 s or more pass
    the check and overflow timedelta in every connect; math.isfinite raises
    OverflowError for an int beyond the float range. B F-03: mutations N2b,
    N5 and N12 survive. B F-04: a regression in the guarded validation also
    fails T22. C: config['loop']['state_dir'] raises KeyError; int() on
    max_tokens raises ValueError; the config override of a gate timeout is
    not validated; load_yaml raises FileNotFoundError. D: the F28 early
    return passes the raw keys of _read_counts.
  impact: "A worker-chosen argument can make the engine compile an out-of-project file or end a run with a traceback and no BLOCKED.md; a write tool of another MCP server can bypass the scope check and be offered to the reviewer; a plausible 'no limit' timeout silently removes every MCP tool; configuration mistakes end in tracebacks instead of a named field; the read-evidence gate can misjudge reads after a wall-clock-cap exit; several specified behaviours can regress unnoticed."
  workaround: "Use the configured MCP servers; keep timeouts at ordinary values; check ai/config.yaml by hand; watch runs."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    Line numbers at main 7440752. A F-01: orchestrator.py:94-97
    (_EDIT_PATTERN_ERRORS), :1509-1537 (edit-failure check), :1605-1608
    (post-write check catches only TimeoutExpired). A F-02: scope.py:42-43
    (WRITE_NAME_PATTERNS), :67-75 (is_readonly_tool). A F-04:
    audit-a5bd4fe1 §6.0. B F-01: orchestrator.py:266-297
    (_validate_audit_report_write; path list :281-283, content :290-291),
    called at :1398. B F-02: orchestrator.py:2624-2630; providers.py:542-548;
    mcp_client.py:64 (timedelta). B F-03: tests/engine/test_loop_robustness.py
    T18 (:489), T25 (:631), T27 (:693). B F-04: T16 (:415), T20 (:516);
    fixture isolated_engine_logger (:375). C: orchestrator.py:596-598
    (load_yaml), :2546 (config['loop']['state_dir']), :2470 (gate
    timeout_seconds override); providers.py:555 (int(max_tokens)). D:
    orchestrator.py:1251.
  technical_notes: >
    A F-01 is pre-existing in kind (before change-a5bd4fe1 a NUL path was
    dispatched and the server error could carry E_INVALID_INPUT). Audit
    proposal for A F-02: match write verbs case-insensitively and add append,
    copy, truncate, save, update, upload, set, put and insert; check every
    tool of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep keeps its class
    (for example 'set' must not match an existing read tool name). Audit
    proposals for B: use scope.path_values (string-filtered) in the F21
    check; reject timeouts above timedelta.max.total_seconds() or a
    documented bound, converting with float() inside a try that maps
    OverflowError to the existing message; add the cases to T19 and T20; add
    the T18, T25 and T27 cases of audit-5e8aea4f §8.4 F-03. C: manifest.py
    :167-169 already validates the manifest's gate timeout_seconds; only the
    ai/config.yaml override is unchecked. NFR-04 requires a config error to
    name the file and field. B F-02 and C share the validation site before
    setup_logging, so FR-08-05 (no state directory on a config error) must
    hold for every new check. The Rich markup observation of audit-5e8aea4f
    §8.4 is not part of this issue.

resolution:
  approach: "To be defined in change-b8c75bac."
  change_ref: "change-b8c75bac"

traceability:
  design_refs: ["design-14e05e35", "requirements-14e05e35"]
  change_refs: ["change-b8c75bac"]

notes: "Audit references: audit-a5bd4fe1 F-01, F-02, F-04; audit-5e8aea4f F-01 to F-04; audit-14e05e35 L-08; d7f4a1c8 P08 review. Operator decisions 2026-11-05 (A) and 2026-11-06 (scope of iteration 2). Predecessors: issue-a5bd4fe1, issue-5e8aea4f (closed)."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-a5bd4fe1"]
  - version: "1.1"
    date: "2026-11-06"
    changes: ["Iteration 2: added audit-5e8aea4f F-01 to F-04, audit-14e05e35 L-08 and the F28 read-path normalisation (Stage C work item 1); line numbers verified at 7440752"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
