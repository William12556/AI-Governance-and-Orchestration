Created: 2026 October 29

```yaml
issue_info:
  id: "issue-711a57d5"
  title: "Engine loop robustness: malformed tool arguments, budget estimate, unbounded calls, retried client errors"
  date: "2026-10-29"
  status: "open"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-711a57d5"
    change_iteration: 1

source:
  origin: "code_review"  # strategic audit audit-caab2052
  description: >
    Remediation group 1 of dev/audit/audit-caab2052-static-code-2026-10-27.md
    (§10.0, §14.0): M-01, M-02, M-06, L-03 and L-09, together with
    audit-14e05e35 L-09 (deferred in dev/task.md). Each defect affects
    unattended runs or the reliability of BLOCKED signalling. Findings
    re-checked by the planner against 24b2dfc (65087f9 changes no source).

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "providers", file_path: "ai/engine/src/providers.py" }
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py" }
    - { name: "gates", file_path: "ai/engine/src/gates.py" }
  designs:
    - { design_ref: "design-14e05e35 §3.0 (Configuration), §11.0 (Error Handling)" }
    - { design_ref: "design-ael-orchestrator §5.1 (budget estimate includes the tool schema)" }
  version: "governance 12.x; engine at 24b2dfc"

reproduction:
  prerequisites: "Engine at 24b2dfc; probes as described in audit-caab2052 §2.0 (P1, P2, P4)"
  steps:
    - "M-01: a provider returns a tool call whose arguments are a list, a number or a double-encoded string"
    - "M-02: a worker issues a write_file call with 40,000 characters of content"
    - "M-06: the model endpoint or an MCP server accepts a request and never answers"
    - "audit-14e05e35 L-09: the provider answers HTTP 400, 401 or 403"
    - "L-03: a preflight success criterion names a pattern that starts with '-'"
    - "L-09: the run stops on a manifest error, a readiness failure, the strict tactical brief or a missing task, after setup_logging"
  frequency: "always, under the stated condition"
  error_output: "M-01: AttributeError traceback from run_phase; no BLOCKED.md"

behavior:
  expected: >
    A malformed call gets a tool error and the phase continues. The budget
    estimate counts tool-call arguments and the tool schema. Every model
    call and MCP request is bounded in time. Client errors that cannot
    succeed on retry stop at once. Subprocesses cannot be fooled by option-
    like patterns or block indefinitely. Every exit after setup_logging logs
    'engine end rc=N' and closes the MCP client.
  actual: >
    M-01: AttributeError ends the run with a traceback; no BLOCKED.md and no
    return stage. M-02: tool-call arguments in assistant messages count 0
    tokens and run_phase omits the schema, so large writes reach the
    provider's context limit without a budget abort. M-06: SDK defaults
    (600 s read timeout, 2 retries) multiplied by the engine's 3 attempts
    allow up to 9 x 600 s per completion; MCP initialize and call_tool have
    no timeout; the phase cap and --duration are checked only between
    iterations. audit-14e05e35 L-09: HTTP 400/401/403 are retried 3 times.
    L-03: grep treats a pattern starting with '-' as an option, so a
    criterion is reported SATISFIED falsely; grep and py_compile have no
    timeout. L-09: four returns after setup_logging skip 'engine end' and,
    where the client exists, mcp.close() is called by hand.
  impact: "Unattended runs can crash without a BLOCKED record, stall for hours, overrun the context window, or report false preflight results."
  workaround: "None in the engine; the operator watches runs and resets by hand."

environment:
  os: "macOS (Apple Silicon) and Linux; behaviour is platform-independent"

analysis:
  root_cause: >
    M-01: providers.py:150 and parser.py:93, 96, 110-117 pass any JSON value
    as arguments; run_phase calls .get on it (scope.py:64, 70 via
    orchestrator.py:1302; orchestrator.py:275, 1338, 1415).
    M-02: estimate_tokens counts message content only
    (orchestrator.py:720-728); the call at orchestrator.py:1179 passes no
    tools.
    M-06: AsyncOpenAI and AsyncAnthropic are built with SDK defaults
    (providers.py:124, 321); MCPClient builds ClientSession without a read
    timeout (mcp_client.py:51-53, 101).
    audit-14e05e35 L-09: _completion_with_retry retries every exception
    (orchestrator.py:475-505).
    L-03: ["grep", "-qF", pattern, path] without '--' or timeout
    (orchestrator.py:1644-1647); py_compile calls without timeout
    (orchestrator.py:1428, 1497, 1623; gates.py:67).
    L-09: the try/finally that logs 'engine end' starts at
    orchestrator.py:2658, after returns at 2520, 2558, 2600 and 2609.
  technical_notes: >
    The audit's gates.py line citations were 104 lines too high; corrected
    in audit-caab2052 v1.1. Line numbers above are at 24b2dfc.
    Design §11.0 already states that a strict-mode schema rejection stops at
    the first call, so the audit-14e05e35 L-09 fix brings the code into line
    with the design.

resolution:
  approach: "See change-711a57d5."
  change_ref: "change-711a57d5"

traceability:
  design_refs: ["design-14e05e35", "design-ael-orchestrator"]
  change_refs: ["change-711a57d5"]

notes: "Audit references: audit-caab2052 M-01, M-02, M-06, L-03, L-09 (§14.0 operator decisions, 2026-10-29); audit-14e05e35 L-09."

version_history:
  - version: "1.0"
    date: "2026-10-29"
    changes: ["Initial issue from audit-caab2052 remediation group 1 and audit-14e05e35 L-09"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
