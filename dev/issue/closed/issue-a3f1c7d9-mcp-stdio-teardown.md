Created: 2026 June 26

```yaml
issue_info:
  id: "issue-a3f1c7d9"
  title: "AEL MCP stdio teardown raises anyio cancel-scope RuntimeError at shutdown"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-a3f1c7d9"
    change_iteration: 1

source:
  origin: "code_review"
  description: >
    Observed during North-Mini-Code-1.0-6bit profile evaluation. On normal
    completion of any AEL phase that connects to MCP servers, the process emits
    two anyio RuntimeError tracebacks ("Attempted to exit cancel scope in a
    different task than it was entered in") during asyncio.run() shutdown — one
    per connected MCP server. The phase result is unaffected and the exit code
    is 0, but the tracebacks are noise that can mask genuine errors.

affected_scope:
  components:
    - name: "mcp_client"
      file_path: "ai/ael/src/mcp_client.py"
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
  version: "current"

reproduction:
  prerequisites: "oMLX reachable; MCP servers configured (filesystem, mcp-grep)."
  steps:
    - "Run: python ai/ael/src/orchestrator.py --mode worker --model <any> --task <trivial task>"
    - "Phase completes; work-complete detected"
    - "Observe two anyio cancel-scope RuntimeError tracebacks during shutdown"
  frequency: "always"
  error_output: >
    RuntimeError: Attempted to exit cancel scope in a different task than it was
    entered in (raised from mcp/client/stdio/__init__.py via anyio _asyncio.py
    during async-generator finalisation).

behavior:
  expected: "Process shuts down cleanly with no tracebacks; exit code 0."
  actual: >
    Two anyio cancel-scope RuntimeErrors print during asyncio.run() shutdown
    (one per MCP server). Exit code remains 0.
  impact: "Cosmetic; output noise obscures real diagnostics. No functional failure."
  workaround: "Ignore the tracebacks; the exit code is authoritative."

environment:
  python_version: "3.11 (Homebrew)"
  os: "macOS (Apple Silicon)"
  dependencies:
    - library: "mcp"
      version: "unknown"
    - library: "anyio"
      version: "unknown"

analysis:
  root_cause: >
    MCPClient.connect() enters the stdio_client and ClientSession async
    contexts. MCPClient.close() intentionally skips ctx.__aexit__() on the
    stdio_client contexts (commented workaround for this same RuntimeError).
    The orphaned stdio_client async generators are then finalised by the event
    loop at asyncio.run() shutdown, where their athrow/GeneratorExit path raises
    the anyio cancel-scope mismatch. The existing workaround relocates the error
    from close() to loop teardown rather than eliminating it.
  technical_notes: >
    Reproduced identically with mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-6Bit
    and North-Mini-Code-1.0-6bit; both exit 0. Defect is model-agnostic.

resolution:
  approach: >
    Decide in design/change. Option A (minimal): call os._exit(rc) before
    awaiting mcp.close(), letting the OS reap the short-lived stdio
    subprocesses; the loop never finalises the orphaned generators. Option B
    (correct): own all stdio_client and ClientSession contexts in a single
    AsyncExitStack entered and exited within the same task, so __aenter__ and
    __aexit__ run in the same task.

verification:
  verification_steps:
    - "Run --mode worker and --mode loop to completion; confirm no tracebacks at shutdown"
    - "Confirm exit code remains 0"
    - "Confirm no orphaned MCP stdio subprocesses remain after exit"

notes: "Pre-existing; surfaced during North Mini Code reviewer/worker evaluation."

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
