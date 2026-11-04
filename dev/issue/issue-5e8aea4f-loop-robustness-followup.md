Created: 2026 November 4

```yaml
issue_info:
  id: "issue-5e8aea4f"
  title: "Engine loop robustness follow-up: non-string read paths, MCP close race, non-finite timeouts, test gaps, API key in error text"
  date: "2026-11-04"
  status: "open"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-5e8aea4f"
    change_iteration: 1

source:
  origin: "code_review"  # strategic follow-up audit audit-711a57d5
  description: >
    Findings F-01 to F-05 of dev/audit/audit-711a57d5-followup-2026-10-29.md
    (§8.0, §11.0). F-06 (guide wording) was corrected in
    guide-engine-operations v1.21 (8e9b6c8) and is not part of this issue.
    Operator decision for F-05 (2026-11-04): redact the resolved API key from
    error text. Findings re-checked by the planner against ba7e082.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "providers", file_path: "ai/engine/src/providers.py" }
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py" }
    - { name: "tests", file_path: "tests/engine/test_loop_robustness.py" }
  designs:
    - { design_ref: "design-14e05e35 §3.0 (Configuration, Timeouts), §11.0 (Error Handling)" }
    - { design_ref: "requirements-14e05e35 NFR-05" }
  version: "governance 12.7; engine at ba7e082"

reproduction:
  prerequisites: "Engine at ba7e082; probes as described in audit-711a57d5 §2.0 (p_repro.py P2b, pc_close_race.py, pm6_model_timeout.py, pi_nan_mcp.py, pd_keys.py, mutate.py)"
  steps:
    - "F-01: a provider returns a read tool call whose arguments are {\"path\": [\"a\"]} (any phase) or {\"path\": 5} (review phase)"
    - "F-01 (planner re-check): a read tool call whose 'paths' value is a number, for example {\"paths\": 5}"
    - "F-02: an MCP call times out, the server answers late, and the engine closes the client while the answer arrives"
    - "F-03: request_timeout_seconds or loop.mcp_timeout_seconds is .nan or .inf in ai/config.yaml"
    - "F-04: mutations M4, M5, M6 and M15 of audit-711a57d5 §6.0 applied to the source"
    - "F-05: a completion call fails and the endpoint echoes the Authorization header in the response body"
  frequency: "always, under the stated condition"
  error_output: "F-01: TypeError traceback from run_phase (unhashable type: 'list'; 'int' object is not iterable); no BLOCKED.md. F-02: ExceptionGroup[BrokenResourceError] from MCPClient.close after 'engine end rc=N'"

behavior:
  expected: >
    A malformed read argument is ignored by read tracking and the phase
    continues. Closing the MCP client never raises. A non-finite timeout is a
    configuration error. Every behaviour specified by change-711a57d5 has a
    test that fails when the behaviour is removed. No API key from an
    environment variable or the Keychain appears in a log record, console
    line, BLOCKED.md or exception message (NFR-05), whatever the endpoint
    returns.
  actual: >
    F-01: read tracking takes 'path' without a type test and iterates 'paths'
    without a list test; a list path raises TypeError when used as a dict key,
    a numeric path raises TypeError in os.path.abspath at the end of a review
    phase, and a numeric 'paths' raises TypeError on iteration. The run ends
    with a traceback, no BLOCKED.md and no return stage. F-02: a late MCP
    answer during close makes mcp.close() raise in main_async's finally; main()
    exits with a traceback and status 1 instead of rc. F-03: NaN and infinity
    pass both timeout checks; model calls are unbounded, and every MCP server
    fails to connect, so the run continues with no tools. F-04: the two
    run_phase py_compile timeouts, the single close in the finally and the
    loop.mcp_timeout_seconds wiring have no test; T16 detects removed
    validation only after a 61 s readiness wait per case. F-05: the SDK error
    text is written verbatim to the run log, the console, BLOCKED.md and the
    RuntimeError; the readiness check echoes it likewise.
  impact: "Unattended runs can crash without a BLOCKED record, end with a misleading exit status, run without bound or without tools, and expose an API key through an echoing endpoint, proxy or gateway."
  workaround: "Use finite timeouts; avoid endpoints that echo credentials; watch runs."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    F-01: orchestrator.py:1383-1384 build _rpaths from tc["arguments"].get("path")
    without isinstance(str) and from .get("paths") without isinstance(list);
    the values reach _read_counts (dict keys, :1388) and os.path.abspath
    (:1317, :1588, :1593). The edit-pattern branch calls .endswith on
    .get("path") (:1462, :1474). FR-A of change-711a57d5 guards the arguments
    object only. F-02: MCPClient.close (mcp_client.py:125-133) awaits
    self._stack.aclose() unguarded; mcp 1.30 sends no cancellation on a read
    timeout, so a late answer can race the stdio teardown. F-03:
    providers.py:503 and orchestrator.py:2555 test type and sign only.
    F-04: tests/engine/test_loop_robustness.py covers the preflight and gate
    timeout sites (T12 to T14) but not orchestrator.py:1482 and :1557; T15
    constructs no MCP client; no test inspects MCPClient's timeout_seconds
    argument. F-05: _completion_with_retry (orchestrator.py:485-528) formats
    str(e) and traceback.format_exc() unfiltered; await_ready
    (providers.py:196-201, 368-372, 382-388) formats str(e) unfiltered. The anthropic
    SDK puts the whole response body into str(e), openai puts error.message.
  technical_notes: >
    The 'paths' crash and the edit-pattern .endswith crash were found by the
    planner during re-check; same class as F-01. The F28 wall-clock-cap early return (orchestrator.py:1205) returns
    unnormalised read paths; that is a separate deferred row in dev/task.md
    and is not changed here. F-05 is pre-existing at 7c4e390; change-711a57d5
    added no channel (audit-711a57d5 §5.0). A literal api_key (kind omlx or a
    local base_url) is not a secret and must not be redacted, because short
    literals such as 'local' would corrupt unrelated text.

resolution:
  approach: "See change-5e8aea4f."
  change_ref: "change-5e8aea4f"

traceability:
  design_refs: ["design-14e05e35", "requirements-14e05e35"]
  change_refs: ["change-5e8aea4f"]

notes: "Audit references: audit-711a57d5 F-01 to F-05; F-05 operator decision 2026-11-04 (redact). Predecessor: issue-711a57d5 (closed)."

version_history:
  - version: "1.0"
    date: "2026-11-04"
    changes: ["Initial issue from audit-711a57d5 F-01 to F-05"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
