Created: 2026 November 4

```yaml
prompt_info:
  id: "prompt-5e8aea4f"
  task_type: "debug"
  source_ref: "change-5e8aea4f"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-04"
  iteration: 1
  coupled_docs:
    change_ref: "change-5e8aea4f"
    change_iteration: 1

context:
  purpose: >
    Close the residual findings of the change-711a57d5 follow-up audit:
    a crash from non-string read paths (F-01), an exception from MCP close
    after a timeout (F-02), non-finite timeouts (F-03), four untested
    behaviours (F-04), and API keys in error text from echoing endpoints
    (F-05; operator decision: redact the resolved key).
  integration: >
    run_phase (orchestrator.py) dispatches tool calls and tracks read paths
    for the review phase. _completion_with_retry wraps every model call and
    writes BLOCKED.md on failure. Providers (providers.py) are built by
    make_provider, which resolves the key through _api_key; await_ready polls
    the endpoint before the run. main_async validates loop settings before
    setup_logging, constructs MCPClient (mcp_client.py) and closes it in one
    finally. Line numbers below are at ba7e082; locate code by the quoted
    text if lines have moved.
  knowledge_references:
    - "dev/change/change-5e8aea4f-loop-robustness-followup.md (approved scope)"
    - "dev/issue/issue-5e8aea4f-loop-robustness-followup.md"
    - "dev/audit/audit-711a57d5-followup-2026-10-29.md §5.0, §6.0, §8.0"
    - "dev/design/design-14e05e35-engine-generalisation.md §3.0, §11.0"
    - "dev/prompt/closed/prompt-711a57d5-loop-robustness.md (FR-A to FR-G, T1 to T16)"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/orchestrator.py, ai/engine/src/providers.py, ai/engine/src/mcp_client.py and tests/engine/test_loop_robustness.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/profiles/, README files or dev/task.md; the planner updates those after review."
    - "No new dependencies. Standard library plus the existing openai, anthropic and mcp packages."
    - "Keep every existing message, log line and BLOCKED.md text unchanged except where an FR states new text or the redaction of FR-D replaces a key inside it."
    - "FR-08-05 must hold: a run refused before setup_logging writes no state directory and no log file."
    - "NFR-05: no API key may appear in a log record, console line, exception message, BLOCKED.md or test failure message. Tests use fake secrets only."
    - "_api_key keeps its signature and return value; existing tests of it must pass unchanged."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Five independent changes, FR-A to FR-E; FR-A to FR-D each with tests in tests/engine/test_loop_robustness.py, FR-E adds tests only."
  requirements:
    functional:
      - "FR-A (F-01) In run_phase's read tracking (orchestrator.py:1380-1391, '# P3: duplicate read tracking'), replace the construction of _rpaths so that: the value of 'path' is included only when isinstance(value, str); the value of 'paths' is iterated only when isinstance(value, list), keeping the existing isinstance(p, str) filter on its entries. Any other value contributes nothing. The existing 'if not _path: continue', counting and warning are unchanged. In the edit-pattern branch (orchestrator.py:1461-1462, '_ep_path = tc["arguments"].get("path", "")'), treat a non-str value as "" so the later '_ep_path.endswith(".py")' cannot raise. Nothing else in run_phase changes; the call is still dispatched and its result handled as before. Comment: change-5e8aea4f (audit-711a57d5 F-01)."
      - "FR-B (F-02) In MCPClient.close (mcp_client.py:125-133), wrap 'await self._stack.aclose()' in try/except Exception as e: print(f\"[engine] Warning: error while closing MCP connections: {e}\"); clear self._sessions in a finally so it runs in every case. BaseException subclasses that are not Exception (for example asyncio.CancelledError, KeyboardInterrupt) still propagate. Update the docstring. Comment: change-5e8aea4f (audit-711a57d5 F-02)."
      - "FR-C (F-03) Import math in providers.py and orchestrator.py. In make_provider (providers.py:500-504) and in main_async's loop.mcp_timeout_seconds check (orchestrator.py:2552-2557), add 'or not math.isfinite(value)' to the rejection condition after the type test (so math.isfinite never receives a non-number). Messages unchanged. Comment: change-5e8aea4f (audit-711a57d5 F-03)."
      - "FR-D (F-05) Key redaction. (1) providers.py: module constant REDACTED = \"API-KEY-REDACTED\". (2) New function _resolve_api_key(name, pcfg, kind) -> tuple[str, bool] containing the current body of _api_key, returning (value, True) on the api_key_env and api_key_keychain branches and (value, False) on the literal api_key and default 'local' branches; error behaviour and the 'key source' log lines unchanged. _api_key(name, pcfg, kind) becomes 'return _resolve_api_key(name, pcfg, kind)[0]' with its docstring kept. (3) OpenAICompatProvider.__init__ and AnthropicProvider.__init__ take secret: str = \"\" and store it as self._secret; add method redact(self, text: str) -> str returning text.replace(self._secret, REDACTED) when self._secret is non-empty, otherwise text unchanged. The secret is never logged, printed or included in repr. (4) make_provider calls _resolve_api_key and passes secret=key to the provider constructor when the second element is True, otherwise secret=\"\". (5) In both await_ready methods (providers.py:196-201, 368-372, 382-388) compute err = self.redact(str(e)) and use err in place of e in every echo(...) and TimeoutError(...) text; exception chaining (from e) unchanged. (6) orchestrator.py: helper _redact(provider, text: str) -> str returning provider.redact(text) when provider has a callable redact attribute, otherwise text. In _completion_with_retry (orchestrator.py:454-532), at the start of the except branch compute err_text = _redact(provider, str(e)). Use err_text in place of e (or last_error) in: the 'completion call failed (attempt ...)' warning, the console retry line, the FR-E log/BLOCKED.md 'Last error:' line and RuntimeError message, and the persistent-failure BLOCKED.md 'Last error:' line and RuntimeError message. Pass every traceback.format_exc() result through _redact before it is logged or written. Message wording, order and the 'from e' / 'from last_error' chaining are unchanged. Comments: change-5e8aea4f (audit-711a57d5 F-05; NFR-05)."
      - "FR-E (F-04) Tests only: see testing.unit_tests T21 to T24. No source change."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-5e8aea4f and the finding ID at each change site, as existing code does"

design:
  architecture: "No new modules; one constant, one helper per module, one method per provider class."
  components:
    - name: "provider.redact"
      type: "method"
      purpose: "Replace the provider's own secret key in text"
      interface:
        inputs:
          - { name: "text", type: "str", description: "error text or traceback" }
        outputs: { type: "str", description: "text with every occurrence of the secret replaced by API-KEY-REDACTED" }
        raises: []
      logic:
        - "Identity when the provider was built without a secret (literal key, injected client)"
    - name: "_resolve_api_key"
      type: "function"
      purpose: "Return the key and whether it is a secret (api_key_env or api_key_keychain)"
      interface:
        inputs:
          - { name: "name, pcfg, kind", type: "str, dict, str", description: "as _api_key" }
        outputs: { type: "tuple[str, bool]", description: "(key, secret)" }
        raises: ["ConfigError"]
      logic: ["Body moved from _api_key; each return also states its source class"]
    - name: "MCPClient.close"
      type: "method"
      purpose: "Teardown that never raises an Exception"
      interface:
        inputs: []
        outputs: { type: "None", description: "unchanged" }
        raises: []
      logic: ["try aclose; except Exception print warning; finally clear sessions"]
  dependencies:
    internal: ["providers.ConfigError"]
    external: ["math"]

error_handling:
  strategy: "Malformed read arguments are ignored by tracking; close errors become a warning; non-finite timeouts stop before any state is written; key text is replaced before it leaves the provider or the retry wrapper."
  logging:
    level: "Existing levels; no new log record except the close warning printed to the console"

testing:
  unit_tests:
    - { scenario: "T17 (FR-A) run_phase (is_worker_phase True) with a fake provider returning read_file {\"path\": [\"a\"]}, then read {\"paths\": 5}, then a final text response; then run_phase as a review phase with read_file {\"path\": [\"a\"]}, read_file {\"path\": 5}, then a final response", expected: "no exception; both phases return rc 0; each call reached the fake MCP call_tool; the review phase's returned read set contains only str entries" }
    - { scenario: "T17b (FR-A) run_phase with an edit_file call {\"path\": [\"a.py\"]} whose fake MCP result contains an _EDIT_PATTERN_ERRORS string, then a final response", expected: "no exception; phase returns rc 0; corrective text names 'the target file'" }
    - { scenario: "T18 (FR-B) MCPClient.close where self._stack.aclose is replaced by an async function raising ExceptionGroup('x', [RuntimeError('late answer')]); sessions dict pre-filled", expected: "no exception; captured stdout contains 'Warning: error while closing MCP connections'; _sessions empty" }
    - { scenario: "T19 (FR-C) make_provider with request_timeout_seconds float('nan') and float('inf') (follow T6)", expected: "ConfigError containing 'request_timeout_seconds: must be a positive number'" }
    - { scenario: "T20 (FR-C) main_async with loop.mcp_timeout_seconds float('nan') and float('inf') written by yaml.safe_dump (follow T16, with readiness stubbed as in T24)", expected: "returns 1; no state directory; the existing error text printed" }
    - { scenario: "T21 (FR-E, M4/M5) run_phase with subprocess.run replaced by a recording fake: (a) an edit_file call whose result contains an _EDIT_PATTERN_ERRORS string on a .py path; (b) a successful write_file to a .py path that exists on disk (create it in the test; the fake MCP does not write)", expected: "py_compile argv recorded at both sites with timeout=30; with the fake raising subprocess.TimeoutExpired, no exception and the phase continues" }
    - { scenario: "T22 (FR-E, M6) main_async with a legacy config, readiness stubbed, orch.MCPClient replaced by a fake class recording construction kwargs and counting awaited close calls, and no task (args.task None, no task.md) so main_async returns after MCP construction", expected: "returns 1; close awaited exactly once; last log line contains 'engine end rc=1'" }
    - { scenario: "T23 (FR-E, M15) as T22 with loop.mcp_timeout_seconds: 7", expected: "fake MCPClient received timeout_seconds == 7" }
    - { scenario: "T24 (FR-E) T16 with OpenAICompatProvider.await_ready replaced by an async function that raises TimeoutError at once", expected: "T16 assertions unchanged; with the mcp_timeout_seconds validation removed (mutation), the test fails in under 5 s instead of after the readiness wait" }
    - { scenario: "T25 (FR-D) make_provider for openai_compatible with api_key_env set to a fake secret (monkeypatch.setenv), and for omlx with a literal api_key 'local-test-key'", expected: "first provider's redact replaces the secret with API-KEY-REDACTED; second provider's redact returns text unchanged" }
    - { scenario: "T26 (FR-D) _completion_with_retry with a fake provider that has redact for secret 'sk-test-SECRET' and raises an exception with status_code 401 whose str contains the secret; then an exception without status_code (initial_backoff 0)", expected: "BLOCKED.md, recorded log lines and the RuntimeError message contain API-KEY-REDACTED and never 'sk-test-SECRET', for both the FR-E and the persistent-failure path" }
    - { scenario: "T27 (FR-D) OpenAICompatProvider and AnthropicProvider (base_url set) built with secret 'sk-test-SECRET' and a fake client whose models.list raises an exception containing the secret; await_ready with timeout 0", expected: "TimeoutError text and every echoed line contain API-KEY-REDACTED and not the secret" }
    - { scenario: "T28 (FR-D) _resolve_api_key for env, keychain (fake security subprocess as in test_providers.py), literal and default omlx", expected: "secret flags True, True, False, False; _api_key returns the same values as before" }
  edge_cases:
    - "Use monkeypatch for every SDK, subprocess and MCP fake; no network."
    - "Restore the 'engine' logger as the existing isolated_engine_logger fixture does."
    - "A provider object without redact (existing fakes such as _Script) must keep working in _completion_with_retry."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts (expected on Linux as root: 361 passed, 1 skipped)."
    - "After the change: same command; no new failures; T17 to T28 pass."
    - "Mutation check (not committed), each on a temporary copy: audit-711a57d5 M4 (no timeout at orchestrator.py:1557), M5 (no timeout at :1482), M6 (no close in the finally), M15 (MCPClient built without timeout_seconds); plus N1 (FR-A str test removed), N2 (FR-B except removed), N3 (isfinite removed from make_provider), N4 (_redact returns text unchanged). Each must fail at least one test; record which."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-5e8aea4f-loop-robustness-followup.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as fix(engine), tests as test(engine), report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-A, FR-C, FR-D)" }
    - { path: "ai/engine/src/providers.py", content: "modified (FR-C, FR-D)" }
    - { path: "ai/engine/src/mcp_client.py", content: "modified (FR-B)" }
    - { path: "tests/engine/test_loop_robustness.py", content: "modified (T16 readiness stub per T24; new T17 to T28)" }
    - path: "dev/reports/report-5e8aea4f-loop-robustness-followup.md"
      content: >
        New file in Obsidian-compatible GitHub Flavored Markdown, laid out as
        README.md: unnumbered H1 title followed by the line 'Created: <year>
        <month> <day>'; unnumbered '## Table of Contents' as a bulleted list
        of the H2 sections linked by GitHub heading slugs (for example
        [1.0 Summary](#10-summary)); numbered sections; '---' between
        sections; '[Return to Table of Contents](#table-of-contents)' at the
        end of each section except Version History; Version History table;
        final '---' and the line 'Copyright (c) 2026 William Watson. MIT
        License.'. Sections: 1.0 Summary; 2.0 Files changed (with functions);
        3.0 Test results (baseline and final counts, new test names, mutation
        results); 4.0 Governance checks; 5.0 Deviations from this prompt (or
        'None'); 6.0 Open points for the planner, including that no live run
        was possible; 7.0 Session branch, starting commit and commit hashes.

success_criteria:
  - "FR-A to FR-D implemented as specified; T17 to T28 present and passing; T16 changed only by the readiness stub"
  - "Mutations M4, M5, M6, M15 and N1 to N4 each fail at least one test"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move"
  - "No existing message changed except the FR-B warning and the key replacement of FR-D"
  - "No fake secret appears in any captured log, console output or BLOCKED.md in the tests"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35 §3.0 and §11.0 and the operations guide after review."
```

Copyright (c) 2026 William Watson. MIT License.
