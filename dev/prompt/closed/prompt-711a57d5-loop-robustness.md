Created: 2026 October 29

```yaml
prompt_info:
  id: "prompt-711a57d5"
  task_type: "debug"
  source_ref: "change-711a57d5"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-10-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-711a57d5"
    change_iteration: 1

context:
  purpose: >
    Make the engine loop robust against malformed tool arguments, unbounded
    model and MCP calls, retries that cannot succeed, option-like preflight
    patterns, and exits that skip the 'engine end' log line. Remediates
    audit-caab2052 M-01, M-02, M-06, L-03, L-09 and audit-14e05e35 L-09
    with the operator's dispositions (audit-caab2052 §14.0).
  integration: >
    run_phase (orchestrator.py) dispatches tool calls normalised by the
    providers (providers.py) to MCP servers through MCPClient
    (mcp_client.py). _completion_with_retry wraps every model call.
    main_async builds providers (build_role_bindings), reads the loop
    settings, creates the run log (setup_logging), connects MCP and runs the
    loop inside a try/finally. gates.syntax_check runs py_compile on
    deliverables. Line numbers below are at 24b2dfc; locate code by the
    quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-711a57d5-loop-robustness.md (approved scope)"
    - "dev/issue/issue-711a57d5-loop-robustness.md"
    - "dev/audit/audit-caab2052-static-code-2026-10-27.md §5.1, §5.2, §5.5, §6.0, §14.0"
    - "dev/design/design-14e05e35-engine-generalisation.md §3.0, §11.0"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md; ai/governance/software-engineering/primer.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/orchestrator.py, ai/engine/src/providers.py, ai/engine/src/mcp_client.py, ai/engine/src/gates.py and the new tests/engine/test_loop_robustness.py. Existing test files may change only where an assertion depends on the old behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/profiles/, README files or dev/task.md; the planner updates those after review."
    - "No new dependencies. Standard library plus the existing openai, anthropic and mcp packages."
    - "Keep every existing message, log line and BLOCKED.md text unchanged except where an FR states new text."
    - "FR-08-05 must hold: a run refused before setup_logging writes no state directory and no log file. Do not move setup_logging, archive_prior_logs or the binding-record replay."
    - "NFR-05: no API key may appear in a log record, exception message, BLOCKED.md or test failure message."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if the installed mcp package's ClientSession does not accept read_timeout_seconds, implement FR-A to FR-C and FR-E to FR-G, leave FR-D unimplemented, record the installed version and the constructor signature in report §5.0 and §6.0, and stop."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Seven independent changes, FR-A to FR-G, each with tests in tests/engine/test_loop_robustness.py."
  requirements:
    functional:
      - "FR-A (M-01) In run_phase's dispatch loop ('for tc in tool_calls:', orchestrator.py:1291), immediately after the two existing 'call →' console and debug lines and before '_refusal = _dispatch_refusal(...)', test isinstance(tc['arguments'], dict). When false: build msg = f\"arguments for tool '{tc['name']}' must be a JSON object of named arguments, got {type(tc['arguments']).__name__}\"; log.warning('malformed tool arguments tool=%s type=%s', name, type name); print one red console line '[engine] malformed tool arguments: <name>'; set result = f'Error: {msg}'; set _scope_err = msg and _report_err = None; do not call _dispatch_refusal, S.check, _validate_audit_report_write or mcp.call_tool. Read tracking (orchestrator.py:1336-1346) and the edit-pattern branch (orchestrator.py:1409-1438) must not run for such a call: guard each with isinstance(tc['arguments'], dict). All later handling (truncation, F27 failed-call tracking, corrective text, tool message append under tc['id']) runs unchanged. The check lives only in run_phase; providers.py and parser.py are not changed for M-01."
      - "FR-B (M-02) In estimate_tokens (orchestrator.py:711), for each message add len(tc['function']['arguments']) // 4 for every entry of m.get('tool_calls') or [] whose function.arguments is a str; ignore malformed entries. Keep the existing content and tools handling. In run_phase replace 'estimated = estimate_tokens(messages)' (orchestrator.py:1179) with 'estimated = estimate_tokens(messages, tools)'."
      - "FR-C (M-06 model calls) Add module constant DEFAULT_REQUEST_TIMEOUT_SECONDS = 300.0 in providers.py. OpenAICompatProvider.__init__ and AnthropicProvider.__init__ take timeout: float = DEFAULT_REQUEST_TIMEOUT_SECONDS; when they build the SDK client they pass timeout=timeout and max_retries=0 (AsyncOpenAI(base_url=..., api_key=..., timeout=..., max_retries=0); AsyncAnthropic(**kwargs) with the two keys added). An injected client is used unchanged. make_provider reads pcfg.get('request_timeout_seconds'); absent or None means the default; otherwise it must be an int or float, not bool, and > 0, else ConfigError(f'providers.{name}.request_timeout_seconds: must be a positive number'). Validate before _api_key so the message appears whatever the key source. Pass the value to both provider kinds. In build_role_bindings, the legacy provider built from the omlx: block also copies omlx.request_timeout_seconds when present."
      - "FR-D (M-06 MCP) MCPClient.__init__(self, servers, timeout_seconds: float = 120.0) stores the value. In connect, build ClientSession(read, write, read_timeout_seconds=timedelta(seconds=self._timeout_seconds)) (from datetime import timedelta); nothing else in connect or call_tool changes, so a timeout surfaces through the existing except branches ('Warning: failed to connect' in connect, 'Error calling' in call_tool). In main_async, read loop.mcp_timeout_seconds next to the other loop settings (orchestrator.py:2477-2484): absent or None means 120.0; otherwise an int or float, not bool, > 0, else print '[engine] config error: loop.mcp_timeout_seconds: must be a positive number' in red and return 1 (this is before setup_logging, so no state is written). Pass it as MCPClient(config.get('mcp_servers', {}), timeout_seconds=<value>) at orchestrator.py:2574."
      - "FR-E (audit-14e05e35 L-09) Add module constant _NON_RETRYABLE_STATUS = frozenset({400, 401, 403}) in orchestrator.py. In _completion_with_retry's except branch, after last_error = e and the existing warning, if getattr(e, 'status_code', None) in _NON_RETRYABLE_STATUS: log.error('completion call failed with HTTP %d (not retried)', code); write BLOCKED.md as '# BLOCKED\\n\\nCompletion call failed with HTTP <code> (not retried).\\n\\nLast error: <e>\\n\\nTraceback:\\n```\\n<tb>\\n```\\n'; print '[engine] BLOCKED: completion call failed with HTTP <code> (not retried)' in red; raise RuntimeError(f'Completion call failed: {e}') from e. Other errors keep the current retry, backoff and messages."
      - "FR-F (L-03) Add module constant _SUBPROCESS_TIMEOUT_SECONDS = 30 in orchestrator.py and SYNTAX_TIMEOUT_SECONDS = 30 in gates.py. (1) Preflight grep (orchestrator.py:1644-1647): argv ['grep', '-qF', '--', pattern, path] and timeout=_SUBPROCESS_TIMEOUT_SECONDS; the existing except Exception branch handles a timeout. (2) The three py_compile calls in orchestrator.py (edit-pattern corrective :1428, post-write check :1497, preflight :1623) get timeout=_SUBPROCESS_TIMEOUT_SECONDS. On subprocess.TimeoutExpired: at :1428 skip the syntax addition; at :1497 treat the file as not checked and append no syntax message; at :1623 the existing except branch applies. (3) gates.syntax_check (gates.py:67) gets timeout=SYNTAX_TIMEOUT_SECONDS; on TimeoutExpired append the result line f'  ✗ {py_path}: syntax check timed out after {SYNTAX_TIMEOUT_SECONDS} s' and count it as a failure the same way a non-zero exit is counted."
      - "FR-G (L-09) In main_async, move 'rc = 1' (orchestrator.py:2656) to just before a new 'try:' placed immediately after the log-archive line (orchestrator.py:2511-2512), and set 'mcp = None' before that try. The block from 'recipe_set = _select_recipe_set(state_dir)' to the end of the current try body moves inside the new try; '_run_started' stays where it is. Remove the current 'try:' at orchestrator.py:2658 so one try/finally remains; its body keeps its existing statements in order. The finally logs 'engine end rc=%d' and then 'if mcp is not None: await mcp.close()'. Remove the explicit 'await mcp.close()' at orchestrator.py:2599 and :2608. Early returns inside the try keep 'return 1'; rc is 1 for them, so the logged value matches. Nothing before setup_logging changes."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-711a57d5 and the finding ID at each change site, as existing code does"

design:
  architecture: "No new modules in ai/; constructor parameters and module constants only."
  components:
    - name: "run_phase"
      type: "function"
      purpose: "FR-A argument-type check; FR-B estimate with tools"
      interface:
        inputs: []
        outputs: { type: "unchanged", description: "unchanged" }
        raises: []
      logic:
        - "Check precedes every other dispatch check, so a malformed call cannot reach code that indexes its arguments"
    - name: "make_provider / provider constructors"
      type: "function"
      purpose: "FR-C timeout and max_retries=0"
      interface:
        inputs:
          - { name: "pcfg.request_timeout_seconds", type: "int | float | None", description: "seconds; default 300" }
        outputs: { type: "provider", description: "unchanged" }
        raises: ["ConfigError"]
      logic: ["Validate, then build the SDK client with timeout and max_retries=0"]
    - name: "MCPClient"
      type: "class"
      purpose: "FR-D session read timeout"
      interface:
        inputs:
          - { name: "timeout_seconds", type: "float", description: "default 120.0" }
        outputs: { type: "unchanged", description: "unchanged" }
        raises: []
      logic: ["ClientSession(read, write, read_timeout_seconds=timedelta(seconds=timeout_seconds))"]
  dependencies:
    internal: ["providers.ConfigError", "scope", "gates"]
    external: ["datetime.timedelta", "subprocess"]

error_handling:
  strategy: "Malformed calls and MCP timeouts become tool errors; non-retryable model errors end BLOCKED at once; configuration errors stop before any state is written."
  logging:
    level: "WARNING for malformed arguments; ERROR for non-retryable completion failure; existing levels elsewhere"

testing:
  unit_tests:
    - { scenario: "T1 (FR-A) run_phase with a fake provider returning write_file arguments [1, 2], then read_file arguments '\"{\\\"path\\\": \\\"a\\\"}\"' (a str), then a final text response; fake MCP client records calls", expected: "no exception; two tool messages whose tool_call_id equals the calls' ids and whose content starts 'Error: arguments for tool'; fake call_tool never invoked; phase return code 0" }
    - { scenario: "T2 (FR-A) four identical malformed calls in successive iterations", expected: "BLOCKED.md written by the existing F27 path; phase return code 1" }
    - { scenario: "T3 (FR-B) estimate_tokens on one assistant message with tool_calls[0].function.arguments of 40,000 characters and empty content", expected: ">= 10,000" }
    - { scenario: "T4 (FR-B) run_phase with a context window set and estimate_tokens wrapped by a spy", expected: "spy receives the tools list passed to run_phase" }
    - { scenario: "T5 (FR-C) make_provider for kinds openai_compatible and anthropic with openai.AsyncOpenAI and anthropic.AsyncAnthropic replaced by capturing fakes (follow test_providers.py fakes), without and with request_timeout_seconds: 45", expected: "timeout 300.0 then 45; max_retries 0 in both" }
    - { scenario: "T6 (FR-C) request_timeout_seconds 0, -1, 'x', True", expected: "ConfigError containing 'providers.<name>.request_timeout_seconds: must be a positive number'" }
    - { scenario: "T7 (FR-C) build_role_bindings with only an omlx: block containing request_timeout_seconds: 90", expected: "fake AsyncOpenAI receives timeout 90" }
    - { scenario: "T8 (FR-D) MCPClient.connect with stdio_client and ClientSession replaced by fakes, default and timeout_seconds=7", expected: "ClientSession received read_timeout_seconds == timedelta(seconds=120) and timedelta(seconds=7)" }
    - { scenario: "T9 (FR-D) call_tool where the fake session raises an exception with message 'Timed out'", expected: "returns a string starting \"Error calling '\"" }
    - { scenario: "T10 (FR-E) _completion_with_retry with a provider raising an exception that has status_code = 401", expected: "provider called once; BLOCKED.md contains 'HTTP 401' and 'not retried'; RuntimeError raised" }
    - { scenario: "T11 (FR-E) status_code 500, and an exception without status_code; initial_backoff 0", expected: "provider called max_retries times; BLOCKED.md contains 'after 3 attempts'" }
    - { scenario: "T12 (FR-F) run_preflight_check on a task whose criterion says a temporary file contains '--version' while the file does not contain it", expected: "criterion not reported SATISFIED" }
    - { scenario: "T13 (FR-F) subprocess.run replaced by a recording fake for the preflight grep and for gates.syntax_check", expected: "grep argv has '--' immediately before the pattern; timeout=30 on grep and py_compile" }
    - { scenario: "T14 (FR-F) gates.syntax_check where subprocess.run raises subprocess.TimeoutExpired", expected: "no exception; gate block contains 'timed out after 30 s' for the file" }
    - { scenario: "T15 (FR-G) main_async run to setup_logging with a valid config and a manifest whose recipe_paths raises ManifestError (monkeypatch), 'engine' logger isolated as in test_providers.py T21/T22", expected: "returns 1; the run log's last line contains 'engine end rc=1'; no MCP client was constructed" }
    - { scenario: "T16 (FR-D) main_async with loop.mcp_timeout_seconds: 0", expected: "returns 1; no state directory created" }
  edge_cases:
    - "Use monkeypatch for every SDK, subprocess and MCP fake; no network."
    - "Restore the 'engine' logger's handlers, level and propagate after tests that call setup_logging, as test_providers.py does."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts (expected on Linux as root: 331 passed, 1 skipped)."
    - "After the change: same command; no new failures; T1 to T16 pass."
    - "Mutation check (not committed), in a temporary copy: (M1) remove the FR-A isinstance check: T1 must fail; (M2) revert FR-E: T10 must fail; (M3) revert FR-G's try placement: T15 must fail. Record results."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-711a57d5-loop-robustness.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as fix(engine), tests as test(engine), report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-A, FR-B, FR-D wiring, FR-E, FR-F, FR-G)" }
    - { path: "ai/engine/src/providers.py", content: "modified (FR-C)" }
    - { path: "ai/engine/src/mcp_client.py", content: "modified (FR-D)" }
    - { path: "ai/engine/src/gates.py", content: "modified (FR-F)" }
    - { path: "tests/engine/test_loop_robustness.py", content: "new (T1 to T16)" }
    - path: "dev/reports/report-711a57d5-loop-robustness.md"
      content: >
        New file. Obsidian Markdown: 'Created: <year> <month> <day>' line,
        table of contents, numbered sections, Return to Table of Contents
        links, Version History table, final line 'Copyright (c) 2026
        William Watson. MIT License.'. Sections: 1.0 Summary; 2.0 Files
        changed (with functions); 3.0 Test results (baseline and final
        counts, new test names, mutation results); 4.0 Governance checks;
        5.0 Deviations from this prompt (or 'None'); 6.0 Open points for the
        planner, including the installed mcp version and that no live run
        was possible; 7.0 Session branch, starting commit and commit hashes.

success_criteria:
  - "FR-A to FR-G implemented as specified; T1 to T16 present and passing"
  - "Mutation checks M1 to M3 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move"
  - "No existing message changed except those FR-A, FR-D, FR-E and FR-F define"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35 §3.0 and §11.0, config.template.yaml and the operations guide after review."
```

Copyright (c) 2026 William Watson. MIT License.
