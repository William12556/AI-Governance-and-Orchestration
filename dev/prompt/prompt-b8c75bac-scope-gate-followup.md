Created: 2026 November 6

```yaml
prompt_info:
  id: "prompt-b8c75bac"
  task_type: "debug"
  source_ref: "change-b8c75bac"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-06"
  iteration: 1
  coupled_docs:
    change_ref: "change-b8c75bac"
    change_iteration: 1

context:
  purpose: >
    Make the engine robust against worker-chosen tool arguments and against
    configuration mistakes: the edit-failure check runs only for dispatched
    calls and survives compile errors; write verbs are matched in any letter
    case; the F21 audit-report check accepts any argument shape; both
    timeout settings share one validation with a maximum of 86400 s;
    configuration errors in ai/config.yaml name the file and field instead
    of ending in a traceback; the F28 early return normalises read paths;
    and several specified behaviours gain tests. Remediates issue-b8c75bac
    parts A to D (audit-a5bd4fe1 F-01, F-02, F-04; audit-5e8aea4f F-01 to
    F-04; audit-14e05e35 L-08; the F28 read-path note), with the operator
    decisions of 2026-11-05 and 2026-11-06.
  integration: >
    orchestrator.py: run_phase dispatches worker tool calls. Before
    dispatch it sets _scope_err (scope violation or review-phase refusal)
    and _report_err (_validate_audit_report_write, the F21 check); after
    dispatch it runs the edit-failure check (_edit_pattern_failed) and the
    post-write syntax check, both through gates.compile_file. main_async
    loads ai/config.yaml with load_yaml, resolves role bindings
    (providers.make_provider, which raises ConfigError), resolves gate specs
    (_resolve_gate_specs, which raises ConfigError) and validates
    loop.mcp_timeout_seconds before archive_prior_logs and setup_logging, so
    a refused run writes no state (FR-08-05). ConfigError is printed as
    '[engine] configuration error (<config path>): <message>' and the run
    returns 1. scope.py classifies tools fail-closed (is_readonly_tool,
    WRITE_NAME_PATTERNS). The engine runs with the project root as its
    working directory. Line numbers below are at main 7440752; locate code
    by the quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-b8c75bac-scope-gate-followup.md (approved scope, v1.1)"
    - "dev/issue/issue-b8c75bac-scope-gate-followup.md (iteration 2)"
    - "dev/audit/audit-a5bd4fe1-followup-2026-11-05.md §6.0 (U1, U4, U5, U10), §8.4 (F-01, F-02, F-04)"
    - "dev/audit/audit-5e8aea4f-followup-2026-11-04.md §6.0 (N2b, N5, N12), §8.4 (F-01 to F-04)"
    - "dev/audit/closed/audit-14e05e35-phase2-2026-10-01.md L-08"
    - "dev/requirements/requirements-14e05e35-engine-generalisation.md NFR-04, FR-08-05"
    - "dev/design/design-14e05e35-engine-generalisation.md §3.0 (Timeouts, v1.23), §7.0, §11.0"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No oMLX, no model, no API key, no MCP server binaries. Do not start the engine against a real endpoint, do not start engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to ai/engine/src/orchestrator.py, ai/engine/src/scope.py, ai/engine/src/providers.py, the comments in ai/engine/config.template.yaml, tests/engine/test_scope_gate_hardening.py, tests/engine/test_loop_robustness.py and the new tests/engine/test_config_validation.py. Other existing test files may change only where an assertion depends on behaviour or message text changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit the issue, change, audit, requirements or design documents, ai/config.yaml, ai/engine/doc/, ai/engine/mcp/, ai/engine/src/mcp_client.py, ai/engine/src/gates.py, ai/governance/, ai/profiles/, ai/webui/, README files, dev/smoke/ or dev/task.md; the planner updates documents after review."
    - "No new dependencies. Standard library and PyYAML only."
    - "Keep every existing message, log line, state file and BLOCKED.md text unchanged except where an FR states new text."
    - "Keep every subprocess bounded as change-711a57d5 made it; compile_file keeps its timeout and the TimeoutExpired handling at each call site."
    - "Every new configuration check runs before archive_prior_logs and setup_logging: a refused run creates or changes nothing in the state directory (FR-08-05)."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the A2b classification table (S1) shows a changed class for any tool of filesystem-mcp 2.5.0, mcp-ripgrep or mcp-grep, do not adjust the verb list to hide it; record it in report §6.0 and continue with the other FRs."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Nine changes, FR-A1 to FR-D, with the tests listed under testing.unit_tests."
  requirements:
    functional:
      - "FR-A1 (audit-a5bd4fe1 F-01; edit-failure check) In run_phase: (1) the _edit_pattern_failed condition (orchestrator.py:1509-1513) additionally requires 'not _scope_err and not _report_err', so the check and its compile run only for a dispatched call. (2) At the edit-failure compile site (:1534-1537) and the post-write compile site (:1605-1608), keep the 'except subprocess.TimeoutExpired' branch unchanged and add 'except Exception as exc:' that logs log.warning('%s check: compile of %s failed (%s); not checked', <'edit-failure' or 'post-write'>, path, type(exc).__name__) and treats the result as no syntax error (the same outcome as a timeout at that site). Comment: change-b8c75bac (audit-a5bd4fe1 F-01)."
      - "FR-A2 (audit-a5bd4fe1 F-02; write verbs) In scope.py: WRITE_NAME_PATTERNS gains r'append', r'copy', r'truncate', r'save', r'update', r'upload', r'set', r'put', r'insert', and every match against WRITE_NAME_PATTERNS uses re.IGNORECASE. WRITE_TOOLS, READONLY_TOOL_PATTERNS and the fail-closed rule of change-a5bd4fe1 are unchanged. Update the module docstring and the is_readonly_tool docstring. Comment: change-b8c75bac (audit-a5bd4fe1 F-02)."
      - "FR-A3 (audit-a5bd4fe1 F-04) Tests only: U1, U4, U5, U10 as listed under testing."
      - "FR-B1 (audit-5e8aea4f F-01; F21 arguments) In _validate_audit_report_write (orchestrator.py:266-297): build the list of (path, content) pairs with scope.path_values(arguments, ('path', 'file_path')) for the top-level call and scope.path_values(f, ('path', 'file_path')) for each dict f in arguments.get('files') when that value is a list; ignore any other 'files' value. A content that is not a str is treated as ''. The function never raises for any argument shape; its return values and message are unchanged. Comment: change-b8c75bac (audit-5e8aea4f F-01)."
      - "FR-B2 (audit-5e8aea4f F-02; timeout maximum) In providers.py add MAX_TIMEOUT_SECONDS = 86400 and validate_timeout(value: Any, field: str) -> float. It raises ConfigError(f'{field}: must be a positive number') for a bool, a value that is not int or float, a value float() cannot convert (catch OverflowError), NaN, infinity or a value <= 0, and ConfigError(f'{field}: must not exceed {MAX_TIMEOUT_SECONDS} seconds') for a larger value; otherwise it returns float(value). make_provider uses it for request_timeout_seconds with field f'providers.{name}.request_timeout_seconds' (replacing providers.py:542-548; the legacy omlx: value copied at :588-589 passes through the same check). main_async uses it for loop.mcp_timeout_seconds with field 'loop.mcp_timeout_seconds' when the key is set (replacing orchestrator.py:2624-2631; the default stays 120.0) and prints a ConfigError as '[red][engine] configuration error ({escape(args.config)}): {escape(str(e))}[/red]', returning 1. This replaces the message '[engine] config error: loop.mcp_timeout_seconds: must be a positive number'. Update the two comments in ai/engine/config.template.yaml (:32, :88) to state 'maximum 86400'. Comments: change-b8c75bac (audit-5e8aea4f F-02; operator decision 2026-11-06)."
      - "FR-B3 (audit-5e8aea4f F-03) Tests only, as listed under testing."
      - "FR-B4 (audit-5e8aea4f F-04) Add the isolated_engine_logger fixture to test_t16_invalid_mcp_timeout_stops_before_state and test_t20_non_finite_mcp_timeout_stops_before_state; no other change to those tests except assertions on the message text changed by FR-B2."
      - "FR-C (audit-14e05e35 L-08; configuration errors) (1) Add _load_config(path: str) -> dict to orchestrator.py. It raises ConfigError: 'cannot read file: <strerror>' for OSError; 'invalid YAML: <problem> at line <n>' for yaml.MarkedYAMLError (problem and problem_mark.line + 1), 'invalid YAML' for any other yaml.YAMLError; 'top level must be a mapping' when the loaded value is not a dict. load_yaml stays unchanged for recipe files. (2) main_async loads the config with _load_config in place of load_yaml(args.config). Before the reset branch it requires config['loop'] to be a dict ('loop: required and must be a mapping') and config['loop']['state_dir'] to be a non-empty str ('loop.state_dir: required and must be a non-empty string'). (3) Before archive_prior_logs, when args.max_iterations is not given, loop.max_iterations must be an int (not bool) greater than 0 ('loop.max_iterations: required as a positive integer unless --max-iterations is given'). (4) In make_provider (providers.py:555), max_tokens: absent or None uses _ANTHROPIC_DEFAULT_MAX_TOKENS; a bool, a value int() cannot convert, or a converted value <= 0 raises ConfigError(f'providers.{name}.max_tokens: must be a positive integer'). (5) In _resolve_gate_specs, when the ai/config.yaml override for a gate contains timeout_seconds, it must be an int or float (not bool), finite and > 0, else ConfigError(f'gates.{name}.timeout_seconds: must be a positive number'); manifest values keep their own check in manifest.py. (6) Every ConfigError from (1) to (5) is printed in the form '[red][engine] configuration error ({escape(args.config)}): {escape(str(e))}[/red]' and main_async returns 1. Comments: change-b8c75bac (audit-14e05e35 L-08; NFR-04)."
      - "FR-D (F28 read paths) The wall-clock-cap return in run_phase (orchestrator.py:1251) returns {os.path.abspath(p) for p in _read_counts.keys()} for review phases and set() for worker phases, as the other exits do. Comment: change-b8c75bac (d7f4a1c8 P08 review)."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-b8c75bac and the finding ID at each change site"

design:
  architecture: "No new modules in ai/. One new function in providers.py (validate_timeout) and one in orchestrator.py (_load_config)."
  components:
    - name: "providers.validate_timeout"
      type: "function"
      purpose: "Single validation for timeout settings with a maximum"
      interface:
        inputs:
          - { name: "value", type: "Any", description: "value read from the configuration" }
          - { name: "field", type: "str", description: "dotted field name used in the message" }
        outputs: { type: "float", description: "validated timeout in seconds" }
        raises: ["ConfigError"]
      logic: ["type test excluding bool", "float() inside try for OverflowError", "isfinite and > 0", "<= MAX_TIMEOUT_SECONDS"]
    - name: "orchestrator._load_config"
      type: "function"
      purpose: "Load ai/config.yaml and report file errors as ConfigError"
      interface:
        inputs: [{ name: "path", type: "str", description: "config file path" }]
        outputs: { type: "dict", description: "parsed configuration" }
        raises: ["ConfigError"]
      logic: ["open and yaml.safe_load", "map OSError and YAMLError", "require a mapping"]
  dependencies:
    internal: ["providers", "scope"]
    external: ["math", "os", "re", "yaml"]

error_handling:
  strategy: "Configuration errors end the run with exit 1 and a message naming the file and field, before any state is written. Worker-argument problems at the F21, edit-failure and post-write sites never end the run."
  logging:
    level: "WARNING for a compile exception at the edit-failure or post-write site; no log record for configuration errors (they occur before setup_logging)"

testing:
  unit_tests:
    - { scenario: "A1a / U10 (test_scope_gate_hardening.py) run_phase worker phase with a fake MCP: edit_file with path '../E_INVALID_INPUT.py' (outside the project root)", expected: "refusal returned to the worker as before; G.compile_file not called (spy)" }
    - { scenario: "A1b: edit_file with path 'src/x\\x00E_INVALID_INPUT.py'", expected: "no exception; refusal with reason 'unresolvable path'; G.compile_file not called; phase continues" }
    - { scenario: "A1c: dispatched edit_file whose result contains 'edits failed to match', with G.compile_file raising ValueError; and a dispatched write_file of a .py file with G.compile_file raising ValueError at the post-write site", expected: "warning 'compile of ... failed (ValueError); not checked' for each site; phase continues" }
    - { scenario: "A2a: is_write_tool for searchAndReplace, listAndDelete, read_and_append, search_and_copy, find_and_truncate, cat_save, list_update, head_upload, grep_set, read_and_put, find_insert, ReadAndWrite", expected: "True for each" }
    - { scenario: "A2b: the existing S1 table (filesystem-mcp 2.5.0, mcp-ripgrep, mcp-grep)", expected: "unchanged: write create, delete, edit, move, patch, replace_text; read-only all others" }
    - { scenario: "A3 / U1: add_collection_pass status combinations: target FAIL with collection PASS; target UNCHECKED with collection FAIL", expected: "FAIL; UNCHECKED" }
    - { scenario: "A3 / U4: run_preflight_check 'no syntax' criterion on an in-project .py file (real compile)", expected: "no __pycache__ beside the file" }
    - { scenario: "A3 / U5: run_loop on the audit path (audit-index.md present) with a syntax block '[SYNTAX GATE: FAIL]' and an audit SHIP that passes the audit SHIP gate", expected: "behaviour of the audit path at 7440752 (the FR-D override of change-a5bd4fe1 applies only on the loop path); the test fails if the override is moved above 'if _audit_original_count is None'" }
    - { scenario: "B1 (test_loop_robustness.py) _validate_audit_report_write with a non-empty audit-report.md and: write_file {'path': ['src/x.py']}; {'path': 5, 'file_path': 'src/x.py'}; create {'files': [{'path': 3}, 'x', {'path': 'audit-report.md', 'content': 7}]}; create {'files': 'x'}; write_file audit-report.md with content None", expected: "no exception for any; non-report writes return None; a report write that drops the existing content returns the existing error message" }
    - { scenario: "B1 through run_phase (as audit-5e8aea4f probe A2): worker phase with non-empty audit-report.md and write_file {'path': ['src/x.py']}", expected: "no traceback; run_phase continues" }
    - { scenario: "B2 (extend T19 and T20): request_timeout_seconds and loop.mcp_timeout_seconds at 86400, 86400.5, 1e14, 10**400, True, '60', 0, -1, .nan, .inf", expected: "86400 accepted; 86400.5 and 1e14 'must not exceed 86400 seconds'; the others 'must be a positive number'; through main_async exit 1 with the 'configuration error (<config path>)' message and no state directory" }
    - { scenario: "B3a (T25): make_provider with kind anthropic and api_key_env set", expected: "provider stores the key as its secret; redact replaces it" }
    - { scenario: "B3b (T27): AnthropicProvider without base_url whose models.retrieve raises an error echoing the key, through await_ready", expected: "echo lines and TimeoutError text contain API-KEY-REDACTED and not the key" }
    - { scenario: "B3c (T18): MCPClient.close with a session whose aclose raises asyncio.CancelledError", expected: "CancelledError propagates; sessions cleared" }
    - { scenario: "B4: T16 and T20 with isolated_engine_logger", expected: "pass; with the loop.mcp_timeout_seconds validation removed (mutation), T16 and T20 fail and T22 passes" }
    - { scenario: "C1 (test_config_validation.py) main_async with --config naming a missing file; a file containing 'loop: [' ; a file containing '- a'", expected: "exit 1; message 'configuration error (<path>): cannot read file: ...', 'invalid YAML: ... at line ...', 'top level must be a mapping'; no traceback" }
    - { scenario: "C2: config without loop:; loop as a list; loop without state_dir; state_dir ''", expected: "exit 1; message names 'loop' or 'loop.state_dir'" }
    - { scenario: "C3: --mode reset with a config without loop:", expected: "exit 1 with the loop message; reset_state not called" }
    - { scenario: "C4: loop.max_iterations missing, 0, True, 'x' without --max-iterations; missing with --max-iterations 2", expected: "exit 1 naming loop.max_iterations; with --max-iterations validation passes (stop the run after validation with a stub, as the existing main_async tests do)" }
    - { scenario: "C5: anthropic provider with max_tokens 'many', 0, True, and with '4096' and 4096", expected: "the first three refused naming providers.<name>.max_tokens; '4096' and 4096 accepted" }
    - { scenario: "C6: gates.pytest.timeout_seconds -1, 'x', True, .nan in ai/config.yaml; and 600", expected: "the first four refused naming gates.pytest.timeout_seconds; 600 accepted" }
    - { scenario: "C7: every refusal in B2 and C1 to C6", expected: "the state directory does not exist afterwards (or is unchanged when created by the test fixture beforehand)" }
    - { scenario: "D1: review-phase run_phase that reads 'src/a.py' by a relative path and then reaches the phase wall-clock cap (monkeypatched time.monotonic)", expected: "returned read set equals {os.path.abspath('src/a.py')}" }
  edge_cases:
    - "Use tmp_path and monkeypatch only; no network, no real engine run."
    - "Restore the 'engine' logger after tests that call setup_logging (isolated_engine_logger)."
    - "Existing classification tests (test_write_scope.py, test_orchestrator_edge_cases.py, test_scope_gate_hardening.py S1 to S4) and compile argv and timeout tests (test_loop_robustness.py T13, T14, T21) must keep passing unchanged."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; record counts."
    - "After the change: same command; no new failures; all new tests pass."
    - "Mutation check (not committed), each on a temporary copy: (M1) remove 'not _scope_err and not _report_err' from the edit-failure condition: A1a fails; (M2) remove the new except branch at the post-write site: A1c fails; (M3) drop re.IGNORECASE: A2a fails; (M4) remove one added verb (update): A2a fails; (M5) restore the untyped path list in _validate_audit_report_write: B1 fails; (M6) remove the maximum check in validate_timeout: B2 fails; (M7) remove the OverflowError handling: B2 fails; (M8) restore load_yaml(args.config): C1 fails; (M9) move the loop.state_dir check after the reset branch: C3 fails; (M10) remove the max_tokens check: C5 fails; (M11) remove the gate timeout check: C6 fails; (M12) restore the raw read set at the F28 return: D1 fails; plus N2b, N5 and N12 of audit-5e8aea4f §6.0: B3 fails. Record results."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; fix new findings caused by this work only."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-b8c75bac-scope-gate-followup.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as fix(engine), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-A1, FR-B1, FR-B2, FR-C, FR-D)" }
    - { path: "ai/engine/src/scope.py", content: "modified (FR-A2)" }
    - { path: "ai/engine/src/providers.py", content: "modified (FR-B2, FR-C)" }
    - { path: "ai/engine/config.template.yaml", content: "modified, comments only (FR-B2)" }
    - { path: "tests/engine/test_scope_gate_hardening.py", content: "modified (A1, A2, A3)" }
    - { path: "tests/engine/test_loop_robustness.py", content: "modified (B1 to B4)" }
    - { path: "tests/engine/test_config_validation.py", content: "new (C1 to C7, D1)" }
    - path: "dev/reports/report-b8c75bac-scope-gate-followup.md"
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
        was possible and the A2b classification result; 7.0 Session branch,
        starting commit and commit hashes.

success_criteria:
  - "FR-A1 to FR-D implemented as specified; all new tests present and passing"
  - "Mutations M1 to M12, N2b, N5 and N12 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "No existing message changed except the loop.mcp_timeout_seconds message (FR-B2) and the new texts stated in FR-A1, FR-B2 and FR-C"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35 §7.0 and §11.0 and the operations guide after review; the timeout maximum is already in design v1.23 and guide v1.26."
```

Copyright (c) 2026 William Watson. MIT License.
