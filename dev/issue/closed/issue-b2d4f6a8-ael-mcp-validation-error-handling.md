# Issue: AEL Orchestrator — MCP Validation Error Not Handled With Explicit Retry Guidance

Created: 2026 March 24

---

## Table of Contents

- [1.0 Issue Information](#10-issue-information)
- [2.0 Source](#20-source)
- [3.0 Affected Scope](#30-affected-scope)
- [4.0 Reproduction](#40-reproduction)
- [5.0 Behavior](#50-behavior)
- [6.0 Environment](#60-environment)
- [7.0 Analysis](#70-analysis)
- [8.0 Resolution](#80-resolution)
- [Version History](#version-history)

---

## 1.0 Issue Information

```yaml
issue_info:
  id: "issue-b2d4f6a8"
  title: "AEL Orchestrator — MCP -32602 validation error not handled with explicit retry guidance"
  date: "2026-03-24"
  reporter: "William Watson"
  status: "resolved"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "user_report"
  test_ref: ""
  description: >
    Worker model emitted a malformed MCP tool call with missing required
    arguments (path and edits undefined). MCP server returned -32602
    Input validation error. Orchestrator injected the raw error string
    as a tool result but provided no explicit retry instruction to the
    model. Model failed to self-correct and produced a text-only response,
    terminating the phase with the error written to work-summary.txt.
    Loop appeared to complete normally (rc=0 from run_phase) despite
    zero useful work having been performed.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "run_phase"
      file_path: "framework/ai/ael/src/orchestrator.py"
    - name: "run_phase"
      file_path: "skel/ai/ael/src/orchestrator.py"
  designs:
    - design_ref: ""
  version: "AEL orchestrator as of 2026-03-24"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Reproduction

```yaml
reproduction:
  prerequisites: >
    Worker model configured. MCP filesystem server connected with edit tool
    requiring path and edits arguments.
  steps:
    - "Issue a Ralph Loop task requiring MCP filesystem edits"
    - "Worker model produces malformed tool call: edit() with no path or edits arguments"
    - "Observe work-summary.txt contains raw MCP -32602 error string"
    - "Observe review-result.txt absent or REVISE (loop accomplished nothing)"
  frequency: "intermittent"
  reproducibility_conditions: >
    Occurs when worker model generates a tool invocation with missing required
    parameters. More likely under high context pressure or with smaller/weaker
    models that do not reliably format tool arguments.
  error_output: >
    work-summary.txt content:
    [TOOL_CALLS]MCP error -32602: Input validation error: Invalid arguments
    for tool edit: [{"expected": "string", "code": "invalid_type", "path": ["path"],
    "message": "Invalid input: expected string, received undefined"}, {"expected":
    "array", "code": "invalid_type", "path": ["edits"], "message": "Invalid input:
    expected array, received undefined"}]
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Behavior

```yaml
behavior:
  expected: >
    When a tool call returns an MCP -32602 validation error, the orchestrator
    injects explicit corrective guidance as a user-role message, prompting the
    model to re-examine the tool schema and reissue the call with correct
    arguments. After a configurable number of consecutive MCP errors,
    the orchestrator writes RALPH-BLOCKED.md and exits cleanly.
  actual: >
    Raw MCP error string injected as tool result only. No additional guidance
    provided. Model failed to self-correct. Phase returned rc=0 (apparent
    success) with error content in work-summary.txt. No BLOCKED state written.
  impact: >
    Loop iteration consumed without useful output. Error surfaced only on
    manual inspection of work-summary.txt. Reviewer either writes REVISE
    (loop wastes further iterations) or the issue is missed entirely.
  workaround: "Reset state and re-run. Inspect work-summary.txt after each run."
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Environment

```yaml
environment:
  python_version: "3.x"
  os: "macOS"
  dependencies:
    - library: "openai"
      version: ""
    - library: "mcp"
      version: ""
  domain: "domain_1"
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Analysis

```yaml
analysis:
  root_cause: >
    run_phase() in orchestrator.py dispatches tool calls and injects results
    uniformly regardless of whether the result represents a successful tool
    response or an MCP protocol error. The raw error string (e.g.
    'Error calling edit: -32602: Input validation error...') is injected as
    a tool role message. This is necessary but insufficient: smaller or
    context-pressured models may not recognise this as a signal to retry
    with corrected arguments.

    Two gaps:
    1. No explicit retry instruction injected when MCP error detected.
    2. No consecutive error counter; loop can run to max_iterations
       performing no useful work and exiting with apparent success (rc=0).

  technical_notes: >
    Detection: result string returned by mcp_client.call_tool() begins with
    'Error calling' when an exception is caught. MCP -32602 specifically
    indicates argument validation failure.

    Fix location: run_phase() in orchestrator.py, within the tool dispatch
    loop after result is obtained.

    Proposed changes (confined to run_phase(), no interface changes):

    1. Detect MCP error in result. When detected:
       a. Print prominent warning to terminal (RED).
       b. Log at WARNING level with tool name and error detail.
       c. Append additional user-role message:
          "The previous tool call failed with a validation error. Review
          the required parameters for the tool and reissue the call with
          all required arguments correctly specified."
       d. Increment per-phase mcp_error_count.

    2. After mcp_error_count reaches configurable threshold (default 3):
       a. Write RALPH-BLOCKED.md with error detail.
       b. Return 1 from run_phase().

    Both changes are backward-compatible and confined to run_phase().
    mcp_client.py does not require modification.

  related_issues:
    - issue_ref: ""
      relationship: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  target_date: "2026-03-25"
  approach: >
    1. Add MCP error detection in run_phase() tool dispatch loop.
    2. Inject explicit retry user message on MCP error detection.
    3. Track consecutive MCP errors; write RALPH-BLOCKED.md at threshold.
    4. Apply fix to framework/ai/ael/src/orchestrator.py and
       skel/ai/ael/src/orchestrator.py. Propagate to project copies.
  change_ref: ""
  resolved_date: "2026-03-25"
  resolved_by: "William Watson"
  fix_description: >
    Added MCP error detection in run_phase() tool dispatch loop.
    Explicit retry user message injected on each MCP error.
    Per-phase mcp_error_count counter resets on successful tool call.
    At mcp_error_threshold consecutive errors, RALPH-BLOCKED.md is written
    and run_phase() returns 1. Threshold configurable via config.yaml
    loop.mcp_error_threshold (default 3). Changes applied to framework and
    skel orchestrator.py and config.yaml.

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: "Pending verification run."

prevention:
  preventive_measures: >
    Explicit MCP error handling prevents silent loop failure on malformed
    tool calls. Consecutive error threshold prevents wasted iterations and
    provides a clean BLOCKED state for Strategic Domain review.
  process_improvements: >
    Consider adding a recipe instruction to worker prompts reminding the
    model to verify required tool arguments before invocation.

traceability:
  design_refs:
    - ""
  change_refs:
    - ""
  test_refs:
    - ""

notes: >
  Observed during GTach project prompt-e1f2a3b4-2 execution.
  Worker model: Devstral-Small-2-24B-Instruct-2512.
  Loop state directory: GTach/.ael/ralph/

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 1
  failure_mode: "critical_error"
  last_review_feedback: "N/A — review phase did not complete"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-24 | William Watson | Initial issue |
| 1.1 | 2026-03-25 | William Watson | Resolved: MCP error handling implemented in orchestrator.py and config.yaml (framework and skel) |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
