Created: 2026 June 27

```yaml
change_info:
  id: "change-a3f1c7d9"
  title: "Own MCP stdio/session contexts in a single AsyncExitStack (a3f1c7d9 Option B)"
  date: "2026-06-27"
  author: "William Watson"
  status: "verified"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a3f1c7d9"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-a3f1c7d9"
  description: >
    Remediate issue-a3f1c7d9 via Option B (correct fix): own all stdio_client and
    ClientSession contexts in a single AsyncExitStack entered and exited within
    the same task, eliminating the anyio cancel-scope RuntimeError raised when
    orphaned stdio generators are finalised at loop teardown.

scope:
  summary: >
    Refactor MCPClient.connect and MCPClient.close to enter every stdio_client
    and ClientSession context through one instance-owned AsyncExitStack, and tear
    them down via stack.aclose() in the same task. Remove the ctx.__aexit__ skip
    workaround.
  affected_components:
    - name: "mcp_client (MCPClient.connect, MCPClient.close)"
      file_path: "ai/ael/src/mcp_client.py"
      change_type: "refactor"
  affected_designs: []
  out_of_scope:
    - "orchestrator main() os._exit(rc) and log flush (retained; harmless)"
    - "issue-e3f1a2b4 CancelledError handling (separate, already closed)"
    - "Tool catalogue, get_openai_tools, call_tool behavior (unchanged)"

rational:
  problem_statement: >
    connect() enters stdio_client and ClientSession contexts; close() skips
    ctx.__aexit__() to avoid an anyio cancel-scope RuntimeError, which only
    relocates the error to loop teardown where the orphaned async generators are
    finalised and raise "Attempted to exit cancel scope in a different task".
  proposed_solution: >
    Enter each stdio_client and ClientSession via a single instance-owned
    AsyncExitStack in connect(); call stack.aclose() in close(). Because both run
    in the same task (main_async), each context's __aenter__ and __aexit__ execute
    in the same task and the cancel scope unwinds cleanly.
  alternatives_considered:
    - option: "Option A — os._exit(rc) before mcp.close()"
      reason_rejected: "Suppresses the symptom by skipping clean async teardown; leaves the workaround in place. Option B removes the root cause."
  benefits:
    - "Clean shutdown with no tracebacks; output noise removed"
    - "close() performs real teardown rather than a skip workaround"
    - "No orphaned stdio subprocesses left to OS reaping"
  risks:
    - risk: "connect() and close() not awaited in the same task in some caller"
      mitigation: "Current sole caller (main_async) awaits both in one task; document the requirement in close()"
    - risk: "Partial connect failure leaves some contexts entered"
      mitigation: "Retain per-server try/except; only successfully entered contexts are pushed onto the stack and are cleanly closed by aclose()"

technical_details:
  current_behavior: >
    self._contexts holds stdio_client contexts; close() awaits session.__aexit__
    only and intentionally skips ctx.__aexit__(); orphaned generators raise at
    asyncio.run() shutdown.
  proposed_behavior: >
    A single AsyncExitStack owns all stdio_client and ClientSession contexts;
    close() calls stack.aclose() in the same task, unwinding all contexts in LIFO
    order without a cancel-scope mismatch.
  implementation_approach: >
    Add `from contextlib import AsyncExitStack`. Create the stack in connect();
    enter each stdio_client and ClientSession via stack.enter_async_context();
    retain per-server try/except and session.initialize(). Replace close() body
    with stack.aclose(); remove the _contexts list and the skip-workaround
    comment. Exact structure decided in implementation.
  code_changes:
    - component: "mcp_client"
      file: "ai/ael/src/mcp_client.py"
      change_summary: "Refactor connect/close to a single AsyncExitStack; remove ctx.__aexit__ skip workaround"
      functions_affected:
        - "MCPClient.__init__"
        - "MCPClient.connect"
        - "MCPClient.close"
      classes_affected:
        - "MCPClient"
  interface_changes:
    - interface: "MCPClient.connect / MCPClient.close"
      change_type: "contract"
      details: "connect() and close() must be awaited in the same task (cancel-scope requirement)"
      backward_compatible: "yes"

dependencies:
  internal:
    - component: "orchestrator main_async"
      impact: "Awaits connect() and close() in the same task — requirement satisfied"
  external:
    - library: "contextlib (stdlib)"
      version_change: "none"
      impact: "AsyncExitStack"

testing_requirements:
  test_approach: "Manual run of --mode worker and --mode loop to completion"
  test_cases:
    - scenario: "Run --mode worker to completion"
      expected_result: "No anyio cancel-scope tracebacks at shutdown; exit code 0"
    - scenario: "Run --mode loop to completion"
      expected_result: "No tracebacks; exit code 0"
    - scenario: "After exit"
      expected_result: "No orphaned MCP stdio subprocesses remain"
    - scenario: "One MCP server fails to connect"
      expected_result: "Warning logged; other servers connect; clean teardown"
  regression_scope:
    - "Tool catalogue construction and dispatch unchanged"
  validation_criteria:
    - "ai/ael/src/mcp_client.py has no syntax errors"

implementation:
  effort_estimate: "hours"
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-a3f1c7d9; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert mcp_client.py to prior version"

notes: >
  Execution path: Claude Code. Source refactor (mcp_client.py). Issue remains open
  until implemented and verified; this change is proposed, not yet implemented.

version_history:
  - version: "1.0"
    date: "2026-06-27"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised implemented -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
