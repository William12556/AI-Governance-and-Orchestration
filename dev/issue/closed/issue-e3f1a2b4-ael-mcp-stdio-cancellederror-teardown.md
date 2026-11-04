# Issue: AEL Orchestrator — MCP stdio Transport CancelledError on Teardown Prevents File Writes

Created: 2026 April 29

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
  id: "issue-e3f1a2b4"
  title: "AEL Orchestrator — MCP stdio transport CancelledError on teardown prevents file writes"
  date: "2026-04-29"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e3f1a2b4"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "user_report"
  test_ref: "experiment: claude-omlx-comparison"
  description: >
    Observed during claude-omlx-comparison experiment. All AEL runs (both
    full T04 and brief prompt) failed consistently with asyncio CancelledError
    during MCP stdio client teardown. The error occurs after model inference
    completes and before (or during) the write_file tool call execution.
    No deliverable file was written in any AEL run across multiple retry attempts.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "MCPClient / run_phase"
      file_path: "framework/ai/ael/src/mcp_client.py"
    - name: "run_phase"
      file_path: "framework/ai/ael/src/orchestrator.py"
  designs:
    - design_ref: ""
  version: "AEL orchestrator as of 2026-04-29"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Reproduction

```yaml
reproduction:
  prerequisites: >
    oMLX running with Devstral-Small-2-24B-Instruct-2512 (Q8 or 6bit).
    Framework AEL orchestrator launched via ael-mcp start_ael.
  steps:
    - "Start AEL loop run against any prompt requiring a write_file tool call"
    - "Observe model inference completes (worker iteration 1-3)"
    - "Observe CancelledError raised in anyio stdio transport during MCP teardown"
    - "Confirm no output file written"
    - "Retry — error repeats consistently"
  frequency: "consistent — 100% reproduction rate across 4 attempts"
  reproducibility_conditions: >
    Observed on M4 Mac Mini, macOS, Python 3.11 (Homebrew), anyio via
    Homebrew mcp package. Occurs on every run regardless of prompt size
    (full T04 ~400 tokens or brief ~200 tokens).
  error_output: |
    asyncio.exceptions.CancelledError: Cancelled by cancel scope 1093bcb10

    Full traceback (from mcp-*.log):
      File ".../mcp_client.py", line 94, in close
        await ctx.__aexit__(None, None, None)
      File ".../mcp/client/stdio/__init__.py", line 182, in stdio_client
        async with (
      File ".../anyio/_backends/_asyncio.py", line 776, in __aexit__
        raise exc_val
      File ".../anyio/abc/_resources.py", line 29, in __aexit__
        await self.aclose()
      File ".../anyio/_backends/_asyncio.py", line 1074, in aclose
        await self.wait()
      File ".../anyio/_backends/_asyncio.py", line 1082, in wait
        return await self._process.wait()
      File ".../asyncio/subprocess.py", line 137, in wait
        return await self._transport._wait()
      File ".../asyncio/base_subprocess.py", line 230, in _wait
        return await waiter
    asyncio.exceptions.CancelledError: Cancelled by cancel scope ...
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Behavior

```yaml
behavior:
  expected: >
    MCP client connects, model inference completes, write_file tool call
    executes successfully, deliverable file is written, orchestrator
    proceeds to reviewer phase or SHIPs.
  actual: >
    MCP client crashes with CancelledError during stdio transport teardown.
    No write_file call reaches the MCP server. Orchestrator exits rc=1.
    No deliverable file is written.
  impact: >
    AEL loop is non-functional for any task requiring filesystem writes.
    All experiment runs failed. Issue blocks the ralph loop entirely.
  workaround: "None identified. Retry does not resolve."
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Environment

```yaml
environment:
  hardware: "M4 Mac Mini, 64GB unified memory"
  python_version: "3.11 (Homebrew Cellar/python@3.11/3.11.14_1)"
  os: "macOS (Sequoia)"
  dependencies:
    - library: "anyio"
      version: "Homebrew-managed (via mcp package)"
    - library: "mcp"
      version: "Homebrew-managed"
    - library: "asyncio"
      version: "stdlib 3.11"
  inference_server: "oMLX, Devstral-Small-2-24B-Instruct-2512 Q8 / 6bit"
  domain: "framework (project_dir: framework/)"
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Analysis

```yaml
analysis:
  root_cause: >
    The CancelledError originates in the anyio asyncio backend's subprocess
    transport during MCP stdio client teardown (mcp_client.py close()).
    The cancel scope that owns the stdio_client context manager is cancelled
    before the subprocess wait() can complete cleanly.

    This is a race condition between the asyncio event loop's cancellation
    propagation and the MCP stdio subprocess lifecycle. When the orchestrator's
    top-level task is cancelled or times out, the cancel scope propagates into
    the stdio_client context manager before the subprocess has exited, causing
    the CancelledError to bubble up through mcp_client.close().

    The crash occurs consistently at the same call site
    (mcp/client/stdio/__init__.py line 182), suggesting the anyio version
    installed via Homebrew has a known incompatibility with Python 3.11's
    asyncio subprocess transport under cancel scope propagation.

  possible_causes:
    - "anyio version mismatch with Python 3.11 asyncio subprocess transport"
    - "MCP client close() called within a cancel scope that fires prematurely"
    - "orchestrator timeout or cancellation signal triggering before MCP teardown completes"

  technical_notes: >
    The fix should either:
    1. Shield mcp_client.close() from cancellation using asyncio.shield() or
       anyio's CancelScope(shield=True), allowing subprocess teardown to
       complete before the cancel propagates.
    2. Upgrade or pin anyio to a version that handles subprocess transport
       teardown correctly under Python 3.11.
    3. Wrap mcp_client.close() in a try/except CancelledError to suppress
       the teardown error and allow the orchestrator to exit cleanly.

    Option 1 is the most robust. Option 3 is the minimal fix.

  related_issues:
    - issue_ref: "issue-b2d4f6a8"
      relationship: "same MCP client code path; different failure mode"
```

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    Investigate mcp_client.py close() — apply asyncio.shield() or
    anyio CancelScope(shield=True) around subprocess teardown, or
    suppress CancelledError in close() as a minimal fix.
    Alternatively, pin/upgrade anyio to a compatible version.
  change_ref: ""
  resolved_date: "2026-04-29"
  resolved_by: "William Watson"
  fix_description: >-
    Changed except Exception to except BaseException in MCPClient.close()
    stdio context teardown loop in framework and skel mcp_client.py.
    CancelledError (BaseException subclass in Python 3.8+) is now suppressed
    during shutdown. Orchestrator exits cleanly; write_file calls complete.

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: >
    Add integration test that verifies write_file tool call completes
    successfully in a loop run before declaring a release stable.
  process_improvements: ""

traceability:
  design_refs:
    - ""
  change_refs:
    - ""
  test_refs:
    - "experiment: claude-omlx-comparison (2026-04-29)"

notes: >
  Discovered during claude-omlx-comparison experiment.
  All four AEL loop runs (full T04 and brief, multiple retries) failed
  with this error. Claude-omlx runs (Runs 3 and 4) completed successfully.
  The MCP client instability is the primary differentiator between AEL
  and claude-omlx in the experiment context.

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 1
  failure_mode: "critical_error"
  last_review_feedback: "N/A — worker phase did not complete write"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-04-29 | Initial issue |
| 1.1 | 2026-04-29 | Resolved: BaseException handler applied to framework and skel mcp_client.py; change-e3f1a2b4 created |

---

Copyright (c) 2026 William Watson. MIT License.
