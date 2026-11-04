# Issue: AEL Orchestrator — Python Syntax Errors Not Detected After File Write

Created: 2026 March 27

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
  id: "issue-f4a7c2e9"
  title: "AEL Orchestrator — Python syntax errors not detected after file write"
  date: "2026-03-27"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e1f2a3b4"
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
    Worker model wrote a syntactically invalid Python file during
    prompt-e1f2a3b4-3 execution. The set literal in watchdog.py was
    written with a missing closing brace:
      self.critical_threads = {'display', 'transport', 'main'
    The orchestrator wrote the file, reported success, and continued.
    The reviewer did not catch the error before producing a malformed
    final response (RALPH-BLOCKED). The syntax error was discovered
    only on manual inspection of the written file.
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
  version: "AEL orchestrator as of 2026-03-27"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Reproduction

```yaml
reproduction:
  prerequisites: >
    Worker model configured. MCP filesystem server connected.
    Task requires writing or editing one or more .py files.
  steps:
    - "Issue a Ralph Loop task requiring MCP filesystem writes to .py files"
    - "Worker model produces syntactically invalid Python in a write or edit call"
    - "Orchestrator reports successful write; no validation performed"
    - "Reviewer phase runs but does not detect or correct the syntax error"
    - "Loop completes (SHIP or BLOCKED) with invalid Python on disk"
    - "Syntax error discovered on manual inspection or at import time"
  frequency: "intermittent"
  reproducibility_conditions: >
    Occurs when the worker model generates truncated or malformed Python
    in a write or edit call. Observed with Devstral-Small-2-24B-Instruct-2512.
    More likely under context pressure or when the model emits partial content
    before the closing delimiter of a set, dict, or list literal.
  error_output: >
    watchdog.py line 91:
      self.critical_threads = {'display', 'transport', 'main'
    SyntaxError: '(' was never closed  (or equivalent at import time)
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Behavior

```yaml
behavior:
  expected: >
    After any write or edit tool call targeting a .py file, the orchestrator
    runs python -m py_compile on the written file. If a SyntaxError is
    detected, the error output is injected as a user-role message instructing
    the model to correct the file before continuing. The model must fix the
    file and re-verify before the phase can proceed.
  actual: >
    No syntax validation is performed after file writes. The MCP server
    reports success for any write operation regardless of file content.
    Syntax errors survive the loop undetected and require manual correction.
  impact: >
    Written source files may be syntactically invalid. Errors surface only
    at import time or on manual inspection, not during the loop. The
    correction burden falls on the human operator. In the observed case,
    watchdog.py would cause an ImportError on application startup.
  workaround: >
    Manually run python -m py_compile on all written .py files after each
    loop run. Correct errors in place using Filesystem MCP tools.
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
  domain: "framework/ai/ael"
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Analysis

```yaml
analysis:
  root_cause: >
    run_phase() in orchestrator.py dispatches write and edit tool calls
    and injects the MCP success result into message history. No post-write
    validation step exists. The MCP filesystem server returns success for
    any syntactically valid write operation at the file I/O level; Python
    syntax correctness is outside its scope.

    The reviewer phase is also unreliable as a syntax check. The reviewer
    uses the same model (Devstral-Small-2-24B-Instruct-2512), which may
    hallucinate a SHIP verdict or produce a malformed response before
    completing its verification pass.

  technical_notes: >
    Fix location: run_phase() in orchestrator.py, within the tool dispatch
    loop after the MCP result is obtained and confirmed non-error.

    Proposed change:
      After a successful write, edit, write_file, or create_file call
      targeting a path ending in .py, run:
        proc = subprocess.run(
            ["python", "-m", "py_compile", path],
            capture_output=True, text=True
        )
      If proc.returncode != 0:
        - Log a WARNING with the stderr output.
        - Inject a user-role message:
            f"Syntax error in {path}:\n\n{proc.stderr.strip()}\n\n
              Correct the file before continuing."
        - Do not increment mcp_error_count (this is not an MCP error).

    The model then issues a corrective write or edit in the next iteration.
    The check runs again after the correction. No loop limit change required.

    python -m py_compile is available in the standard library and requires
    no additional dependencies. The path must be absolute; the orchestrator
    already operates with absolute paths via the MCP server configuration.

  related_issues:
    - issue_ref: "issue-b2d4f6a8"
      relationship: "same fix location (run_phase tool dispatch loop)"
```

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Resolution

```yaml
resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    Add a post-write syntax check in run_phase() tool dispatch loop.
    After any successful write, edit, write_file, or create_file call
    on a .py file, run python -m py_compile. Inject corrective user
    message on failure. Apply to framework and skel orchestrator.py.
  change_ref: ""
  resolved_date: "2026-03-27"
  resolved_by: "William Watson"
  fix_description: >
    Added import subprocess. Added P4 post-write syntax check in run_phase()
    tool dispatch loop (else branch after mcp_error_count = 0). After any
    successful write, edit, write_file, or create_file call on a .py path,
    runs python -m py_compile. On failure: logs WARNING, prints red console
    line, injects corrective user-role message. Applied to framework, skel,
    GTach, solax-modbus. e-Paper-IP-Display skipped (orchestrator predates
    MCP error handling — requires wholesale replacement before this patch).

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: "Fix applied. e-Paper-IP-Display excluded — version too far behind."

prevention:
  preventive_measures: >
    Post-write syntax validation closes the gap between MCP write success
    and Python import correctness. The model receives immediate, actionable
    feedback and can self-correct within the same loop run.
  process_improvements: >
    Consider extending validation to other languages if non-Python targets
    are added (e.g. pyproject.toml TOML validity via tomllib.loads).

traceability:
  design_refs:
    - ""
  change_refs:
    - ""
  test_refs:
    - ""

notes: >
  Observed during GTach project prompt-e1f2a3b4-3 execution.
  Worker model: Devstral-Small-2-24B-Instruct-2512.
  Affected file: src/gtach/core/watchdog.py
  Loop state directory: GTach/.ael/ralph/
  Log: ael_20260327-103951.LOG

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 1
  failure_mode: "reviewer_malformed_response"
  last_review_feedback: "N/A — reviewer phase did not produce SHIP/REVISE"

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
| 1.0 | 2026-03-27 | William Watson | Initial issue |
| 1.1 | 2026-03-27 | William Watson | Resolved: P4 post-write Python syntax check added to run_phase() in framework, skel, GTach, solax-modbus |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
