# Change: AEL MCP Client — CancelledError on stdio Teardown

Created: 2026 April 29

---

## Table of Contents

- [1.0 Change Information](#10-change-information)
- [2.0 Scope](#20-scope)
- [3.0 Rationale](#30-rationale)
- [4.0 Technical Details](#40-technical-details)
- [5.0 Testing](#50-testing)
- [6.0 Implementation](#60-implementation)
- [Version History](#version-history)

---

## 1.0 Change Information

```yaml
change_info:
  id: "change-e3f1a2b4"
  title: "AEL MCP Client — suppress CancelledError on stdio transport teardown"
  date: "2026-04-29"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e3f1a2b4"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Scope

```yaml
scope:
  summary: >
    Single-line change to MCPClient.close() in framework and skel.
    Broadens exception handler for stdio context teardown from Exception
    to BaseException, suppressing CancelledError during shutdown.
  affected_components:
    - name: "MCPClient.close() — stdio context teardown"
      file_path: "framework/ai/ael/src/mcp_client.py"
      change_type: "modify"
    - name: "MCPClient.close() — stdio context teardown"
      file_path: "skel/ai/ael/src/mcp_client.py"
      change_type: "modify"
  out_of_scope:
    - "orchestrator.py — no changes required"
    - "session teardown loop — Exception handler is sufficient (sessions do not raise CancelledError)"
    - "downstream project copies — inherit via standard propagation"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Rationale

```yaml
rationale:
  problem_statement: >
    asyncio.CancelledError inherits from BaseException, not Exception, in
    Python 3.8+. The existing except Exception handler in the stdio context
    teardown loop did not catch CancelledError. The error propagated out of
    close(), crashing the orchestrator before any write_file tool call
    could complete. The AEL loop was non-functional for all filesystem
    write tasks. Reproduction rate: 100%.
  proposed_solution: >
    Change except Exception to except BaseException in the stdio context
    teardown loop only. close() is called exclusively during shutdown;
    any teardown error at this point is non-recoverable. Suppressing
    BaseException here is safe and targeted.
  alternatives_considered:
    - option: "asyncio.shield() around ctx.__aexit__"
      reason_rejected: >
        More complex; requires restructuring close() as a coroutine with
        explicit shield scope. Minimal fix is sufficient.
    - option: "Pin/upgrade anyio to compatible version"
      reason_rejected: >
        Environment-level change; does not address the underlying handler
        gap. The code fix is more portable.
    - option: "except (Exception, asyncio.CancelledError)"
      reason_rejected: >
        Verbose; BaseException is cleaner and catches all shutdown-phase
        interrupts uniformly.
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Technical Details

```yaml
technical_details:
  current_behavior: >
    MCPClient.close() iterates over self._contexts and calls
    ctx.__aexit__(None, None, None) inside except Exception. When anyio's
    stdio transport raises CancelledError during subprocess wait(), the
    handler does not catch it. CancelledError propagates, crashing the
    orchestrator before write_file executes.
  proposed_behavior: >
    except BaseException suppresses CancelledError (and any other
    BaseException subclass) during stdio teardown. Orchestrator exits
    cleanly. write_file tool calls complete before close() is reached.
  code_changes:
    - file: "framework/ai/ael/src/mcp_client.py"
      location: "MCPClient.close() — stdio context teardown loop"
      old: "except Exception:"
      new: |
        except BaseException:
            # CancelledError inherits BaseException (not Exception) in Python 3.8+.
            # Suppress teardown errors — close() is shutdown-only; errors are non-recoverable.
    - file: "skel/ai/ael/src/mcp_client.py"
      location: "MCPClient.close() — stdio context teardown loop"
      old: "except Exception:"
      new: "except BaseException: (same comment as framework)"
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Manual AEL loop run against a task requiring at least one write_file
    tool call. Confirm deliverable file written and orchestrator exits rc=0.
  test_cases:
    - scenario: "AEL loop run requiring write_file"
      expected_result: >
        No CancelledError in logs. Deliverable file written.
        Orchestrator exits rc=0 or rc=SHIP. MCP teardown completes silently.
    - scenario: "AEL loop run requiring edit tool call"
      expected_result: "Same as above — no regression."
  regression_scope:
    - "MCPClient.connect() — unchanged"
    - "MCPClient.call_tool() — unchanged"
    - "session teardown loop in close() — unchanged (Exception handler retained)"
  validation_criteria:
    - "No asyncio.CancelledError in AEL log"
    - "Deliverable file present on disk after run"
    - "Orchestrator exits with rc=0 or SHIP state"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Implementation

```yaml
implementation:
  steps:
    - step: "Edit framework/ai/ael/src/mcp_client.py — change Exception to BaseException in ctx teardown"
      status: "done"
    - step: "Edit skel/ai/ael/src/mcp_client.py — same change"
      status: "done"
    - step: "Propagate to downstream projects via bin/propagate.sh"
      status: "pending — William to execute"
    - step: "Update issue-e3f1a2b4 status to resolved after verification run"
      status: "pending"
  rollback_procedure: "Restore from git history"
  deployment_notes: >
    Propagate to GTach, solax-modbus, e-Paper-IP-Display via bin/propagate.sh.
    Verify with a live AEL loop run before closing the issue.

verification:
  implemented_date: "2026-04-29"
  implemented_by: "William Watson"
  verification_date: ""
  verified_by: ""
  test_results: ""

traceability:
  related_issues:
    - issue_ref: "issue-e3f1a2b4"
      relationship: "source"
    - issue_ref: "issue-b2d4f6a8"
      relationship: "same MCP client code path; different failure mode"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-29 | William Watson | Initial change — BaseException handler applied to framework and skel |

---

Copyright (c) 2026 William Watson. MIT License.
