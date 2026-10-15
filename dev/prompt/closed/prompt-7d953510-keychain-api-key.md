Created: 2026 October 14

```yaml
prompt_info:
  id: "prompt-7d953510"
  task_type: "code_generation"
  source_ref: "change-7d953510"
  target_profile: "claude_code"  # Claude Code cloud session (operator decision 2026-10-14)
  date: "2026-10-15"
  iteration: 5
  coupled_docs:
    change_ref: "change-7d953510"
    change_iteration: 5

context:
  purpose: >
    Let a provider API key be read from the macOS login Keychain through a new
    optional provider key api_key_keychain (design-14e05e35 v1.12 §3.0 Keys,
    §11.0; requirements-14e05e35 v1.5 FR-04-07).
    Iteration 2: wrap a UnicodeDecodeError from the Keychain lookup in a
    ConfigError (FR-F; design-14e05e35 v1.13 §11.0; report-7d953510 §6.0
    item 2).
    Iteration 3: raise Keychain lookup errors after the try statement so no
    __context__ holds the raw output, and add three tests (FR-G, FR-H;
    dev/audit/audit-7d953510-strategic-2026-10-14.md L-01, L-02, L-03).
    Iteration 4: the 'key source' INFO record is lost in a real run, because
    main_async resolves the role bindings before setup_logging. Capture the
    records emitted during binding resolution and write them to the run log
    once it exists (FR-I; design-14e05e35 v1.16 §3.0; GTach engine-mcp run
    1e00fd66, engine_20261014-150813.LOG).
    Iteration 5 (test-only): add a test that runs main_async past
    setup_logging, and make T19 and T20 check level restoration from a
    level other than DEBUG (FR-J, FR-K; dev/audit/
    audit-7d953510-followup-iteration4-2026-10-15.md F-01, F-02).
  integration: >
    providers._api_key(name, pcfg, kind) is called once per provider by
    make_provider(), which build_role_bindings() calls at engine startup.
    Nothing else in the engine reads keys. A Keychain key never enters the
    process environment, so orchestrator.py subprocess scrubbing (scrub_env,
    built from api_key_env) needs no change.
  knowledge_references:
    - "dev/change/change-7d953510-keychain-api-key.md (approved scope)"
    - "dev/issue/issue-7d953510-keychain-api-key.md"
    - "dev/design/design-14e05e35-engine-generalisation.md §3.0, §11.0"
    - "dev/requirements/requirements-14e05e35-engine-generalisation.md FR-04-07, NFR-05, NFR-06"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md; ai/governance/software-engineering/primer.md"
  constraints:
    - "Iteration 5 only, test-only. Iterations 1 to 4 (FR-A to FR-I, tests T1 to T21) are implemented in commits 9b4cb23, d4c1cdb, 45a8ac0 and 050e5ec and audited. Implement FR-J and FR-K only. Do not change any file under ai/; T1 to T18 and T21 stay unchanged; T19 and T20 change only as FR-K states."
    - "Execution environment: Claude Code cloud (Linux container, repository clone). There is no macOS, no /usr/bin/security, no Keychain, no oMLX and no Mistral or Anthropic API key. Do not attempt a live run, do not start the engine or engine-mcp, and do not call any network endpoint other than package installation."
    - "Code changes are limited to tests/engine/test_providers.py."
    - "FR-08-05 must hold: a run refused before setup_logging (configuration error, manifest error, pre-run check exit 3) writes no state directory and no log file. Do not move setup_logging or archive_prior_logs."
    - "Governance changes are limited to: moving this prompt to dev/prompt/closed/, and updating the existing report named in deliverable.files (iteration 5 section)."
    - "Do not edit the issue, change, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/profiles/ or README files; the planner updates those after review."
    - "No new dependencies; standard library only (subprocess, sys)."
    - "The key value must never appear in a log record, an exception message, an exception's chained cause or context, or a test failure message."
    - "Existing behaviour and messages for api_key_env, literal api_key and kind omlx stay unchanged, except the single error message named in specification.requirements.functional."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit hash (the main commit your branch starts from) before any edit. Commit to the session branch and push it; do not merge into main, do not open a pull request, do not force-push or rewrite history."
    - "Stop condition: if the FR-J test cannot fail when the replay loop in main_async is removed, or reaching 'engine start' needs a change under ai/, do not change ai/; record it in report §5.0 and §6.0 and stop."
    - "Stop condition: if any requirement conflicts with existing code or tests, or cannot be met without touching a file outside the scope, do not improvise. Implement the unaffected parts, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: >
    Add optional provider key api_key_keychain (a Keychain generic-password
    service name). _api_key() consults sources in a fixed order and logs which
    source supplied the key.
  requirements:
    functional:
      - "FR-A Resolution order in _api_key(name, pcfg, kind): (1) api_key_env configured and os.environ[var] non-empty → return it, source label 'env:<VAR>'. (2) Else api_key_keychain configured → return _keychain_secret(name, service), source label 'keychain:<service>'. (3) Else api_key_env configured → raise the existing ConfigError 'providers.<name>: environment variable <VAR> is not set', unchanged. (4) Else the existing literal api_key and kind omlx rules, unchanged."
      - "FR-B api_key_keychain present but not a non-empty str → ConfigError 'providers.<name>.api_key_keychain: must be a non-empty string'. Validate before step 1 so a malformed value is reported even when the environment variable is set."
      - "FR-C After a successful step 1 or step 2, log once at INFO: 'providers.<name>: key source <label>'. Steps 3 and 4 log nothing new."
      - "FR-D The final fallback error for a non-omlx kind with no key source becomes: 'providers.<name>: api_key_env or api_key_keychain is required for kind <kind>'. This is the only message whose text changes; update any existing test that asserts the old text."
      - "FR-E A literal api_key together with api_key_keychain: step 2 wins, so the literal-key restriction for remote endpoints is not reached. No warning is added."
      - "FR-F (iteration 2) In _keychain_secret, a UnicodeDecodeError raised by subprocess.run (Keychain output not valid text in the locale encoding) → ConfigError 'providers.<name>.api_key_keychain: Keychain item for service <service> is not valid text' from None. Catch UnicodeDecodeError specifically, not ValueError or Exception."
      - "FR-G (iteration 3; audit L-01) In _keychain_secret, no ConfigError may carry a __context__. Each except branch (subprocess.TimeoutExpired, OSError, UnicodeDecodeError) only assigns its existing message to a local variable; after the try statement, if that variable is set, raise ConfigError(message) from None. Messages, the order of the except branches and the from None stay as they are, so __cause__ is None, __suppress_context__ is True and __context__ is None. Do not bind the exception to a name."
      - "FR-H (iteration 3; audit L-02) In the _keychain_secret docstring, replace 'macOS login Keychain' with 'the user's Keychain search list (normally the login Keychain)'. No other docstring or comment changes."
      - "FR-I (iteration 4) In orchestrator.py add a module-level class _RecordBuffer(logging.Handler) whose emit() appends each record to a list attribute 'records', and a function _resolve_bindings_capturing(config, args) that: gets logging.getLogger('engine'); saves its current level; adds a _RecordBuffer with level DEBUG; sets the logger level to DEBUG; returns (build_role_bindings(config, args), buffer.records); and in a finally block removes the buffer and restores the saved level, so the logger is unchanged whether resolution succeeds or raises. In main_async replace 'bindings = build_role_bindings(config, args)' with 'bindings, _binding_records = _resolve_bindings_capturing(config, args)' inside the existing try/except ConfigError (message and return 1 unchanged). Immediately after 'log = setup_logging(state_dir)' and before the 'engine start' log line, write the captured records with 'for _record in _binding_records: log.handle(_record)'. The buffer must be removed before setup_logging runs, because setup_logging adds its FileHandler only when the logger has no handlers. Do not change propagate, setup_logging, providers.py or any message."
      - "FR-J (iteration 5; audit F-01) Add test T22 in tests/engine/test_providers.py that runs orch.main_async to the 'engine start' log line and checks the run log. Write a config.yaml in a temporary project directory with ENV_ONLY's providers and roles plus a loop block (state_dir under the temporary directory and the loop keys main_async reads, following the existing main_async tests); set MISTRAL_API_KEY to SECRET; replace openai.AsyncOpenAI as _fake_openai does; use a free-text task (not a file under ai/workspace/). Stop the run right after 'engine start' by monkeypatching orch._select_recipe_set to raise a test-local exception and expect that exception (the audit probe's method, audit §2.0). If the manifest step stops the run first, give it a manifest the way existing tests do or monkeypatch orch.locate_manifest and orch.load_manifest; do not change ai/. Isolate the 'engine' logger as T21 does (handlers [], level and propagate restored by monkeypatch) and close its FileHandler at the end. Assert: exactly one engine_*.LOG in the state directory; it contains ENV_SOURCE_LINE; the line comes before the first line containing 'engine start'; SECRET is absent."
      - "FR-K (iteration 5; audit F-02) In T19 and T20, before the call, set the 'engine' logger level to logging.NOTSET with monkeypatch.setattr(logger, 'level', logging.NOTSET), then keep the existing before/after comparison. Nothing else in T19 or T20 changes."
      - "Mutation check (not committed): in a temporary copy or worktree, (M1) delete the two-line replay loop in main_async and (M4) delete logger.setLevel(saved_level) in _resolve_bindings_capturing; with M1 the full suite must fail in T22, with M4 it must fail in T19 or T20. Remove the temporary copy and record the results in the report."
    technical:
      language: "Python"
      version: "3.10+ (repository convention 3.11+)"
      standards:
        - "Type hints and docstrings in the existing providers.py style"
        - "Module-level constants: _SECURITY = '/usr/bin/security'; _KEYCHAIN_TIMEOUT = 10"
        - "import subprocess and sys at module top, so tests can monkeypatch P.subprocess.run and P.sys.platform"

design:
  architecture: "One private helper beside _api_key(); no new classes, no change to make_provider() or build_role_bindings()."
  components:
    - name: "_keychain_secret"
      type: "function"
      purpose: "Read one generic-password secret from the login Keychain."
      interface:
        inputs:
          - { name: "name", type: "str", description: "provider name, for messages only" }
          - { name: "service", type: "str", description: "Keychain service name" }
        outputs: { type: "str", description: "the secret, trailing newline removed" }
        raises: ["ConfigError"]
      logic:
        - "If sys.platform != 'darwin' → ConfigError 'providers.<name>.api_key_keychain: supported on macOS only; use api_key_env'. Do not call subprocess."
        - "Run subprocess.run([_SECURITY, 'find-generic-password', '-s', service, '-w'], capture_output=True, text=True, timeout=_KEYCHAIN_TIMEOUT, check=False)."
        - "OSError (includes FileNotFoundError) → ConfigError 'providers.<name>.api_key_keychain: <_SECURITY> is not available' from None."
        - "Iteration 2: UnicodeDecodeError → ConfigError per FR-F, from None. Its object attribute holds the raw output, so the cause must not be chained."
        - "Iteration 3: per FR-G, the three wrapped failures are raised after the try statement, not inside the except blocks."
        - "subprocess.TimeoutExpired → ConfigError 'providers.<name>.api_key_keychain: lookup for service <service> timed out after 10 s (Keychain locked or access dialog unanswered)' from None. TimeoutExpired carries captured output, so the cause must not be chained."
        - "returncode != 0 → ConfigError 'providers.<name>.api_key_keychain: no readable Keychain item for service <service> (security exit <code>)'. Include neither stdout nor stderr."
        - "value = stdout.rstrip('\\n'); empty → ConfigError 'providers.<name>.api_key_keychain: Keychain item for service <service> is empty'."
        - "Return value."
    - name: "_api_key"
      type: "function"
      purpose: "Resolve a provider key per FR-A to FR-E."
      interface:
        inputs:
          - { name: "name", type: "str", description: "provider name" }
          - { name: "pcfg", type: "dict", description: "provider configuration block" }
          - { name: "kind", type: "str", description: "provider kind" }
        outputs: { type: "str", description: "API key" }
        raises: ["ConfigError"]
  dependencies:
    internal: ["ConfigError", "log (module logger 'engine')"]
    external: ["subprocess", "sys"]

error_handling:
  strategy: "Every failure raises ConfigError naming providers.<name>.api_key_keychain; wrapped exceptions are raised 'from None'."
  logging:
    level: "INFO for the key source line only; no DEBUG output of command arguments or results beyond what already exists"

testing:
  unit_tests:
    - { scenario: "T1 api_key_env set and api_key_keychain configured", expected: "env value returned; subprocess.run not called; INFO record 'key source env:<VAR>'" }
    - { scenario: "T2 api_key_env configured but unset, api_key_keychain configured", expected: "Keychain value returned; INFO record 'key source keychain:<service>'" }
    - { scenario: "T3 api_key_keychain only", expected: "value returned; argv == ['/usr/bin/security','find-generic-password','-s',<service>,'-w']; timeout == 10; check False" }
    - { scenario: "T4 stdout 'secret\\n'", expected: "'secret'" }
    - { scenario: "T5 returncode 44 with stderr text", expected: "ConfigError containing 'exit 44' and the service; stderr text absent" }
    - { scenario: "T6 subprocess.TimeoutExpired raised with output containing the secret", expected: "ConfigError mentioning 'timed out'; __cause__ is None and __suppress_context__ is True; secret absent from str(error)" }
    - { scenario: "T7 empty stdout", expected: "ConfigError mentioning 'empty'" }
    - { scenario: "T8 sys.platform 'linux'", expected: "ConfigError mentioning 'macOS only'; subprocess.run not called" }
    - { scenario: "T9 subprocess.run raises FileNotFoundError", expected: "ConfigError mentioning 'not available'" }
    - { scenario: "T10 api_key_keychain '' and 123", expected: "ConfigError 'must be a non-empty string', also when api_key_env is set" }
    - { scenario: "T11 no key source for kind openai_compatible", expected: "ConfigError with the FR-D message" }
    - { scenario: "T12 literal api_key plus api_key_keychain on a remote base_url", expected: "Keychain value returned (FR-E)" }
    - { scenario: "T13 make_provider kind openai_compatible with api_key_keychain", expected: "OpenAICompatProvider built with the Keychain value as api_key (inject a stub client or monkeypatch AsyncOpenAI; no network)" }
    - { scenario: "T14 secret absence", expected: "for T2, T3 and T13, the secret string is absent from every caplog record message and argument" }
    - { scenario: "T15 (iteration 2) subprocess.run raises UnicodeDecodeError('utf-8', SECRET.encode() + b'\\xff', len(SECRET), len(SECRET) + 1, 'invalid start byte')", expected: "ConfigError mentioning 'not valid text' and the service; __cause__ is None and __suppress_context__ is True; secret absent from str(error)" }
    - { scenario: "T16 (iteration 3, L-01) parametrized over subprocess.TimeoutExpired(['/usr/bin/security'], 10, output=SECRET, stderr=SECRET), FileNotFoundError(2, 'No such file or directory') and the T15 UnicodeDecodeError", expected: "ConfigError with __context__ is None, __cause__ is None and __suppress_context__ is True; secret absent from str(error)" }
    - { scenario: "T17 (iteration 3, L-03) make_provider('anthropic', {'kind': 'anthropic', 'api_key_keychain': SERVICE}) with anthropic.AsyncAnthropic replaced by a capturing fake, following test_make_provider_passes_base_url_to_anthropic", expected: "AnthropicProvider built; the fake received api_key == SECRET; INFO record 'key source keychain:<service>'; secret absent from all records" }
    - { scenario: "T18 (iteration 3, L-03) monkeypatch.setenv('MISTRAL_API_KEY', '') (a) with api_key_env and api_key_keychain, (b) with api_key_env only", expected: "(a) Keychain value returned, source label keychain:<service>; (b) the existing ConfigError 'providers.<name>: environment variable MISTRAL_API_KEY is not set'; subprocess.run not called in (b)" }
    - { scenario: "T19 (iteration 4) _resolve_bindings_capturing with a config binding both roles to an openai_compatible provider with api_key_env: MISTRAL_API_KEY, the variable set to SECRET (monkeypatch.setenv), and openai.AsyncOpenAI replaced by a fake as in T13", expected: "returns bindings for worker and reviewer and a record list with exactly one message 'providers.<name>: key source env:MISTRAL_API_KEY'; afterwards the 'engine' logger's handlers and level equal their values before the call" }
    - { scenario: "T20 (iteration 4) _resolve_bindings_capturing with a provider whose api_key_env variable is unset and no other key source", expected: "ConfigError 'providers.<name>: environment variable MISTRAL_API_KEY is not set' propagates; the 'engine' logger's handlers and level equal their values before the call" }
    - { scenario: "T21 (iteration 4) isolate the 'engine' logger with monkeypatch.setattr(logging.getLogger('engine'), 'handlers', []) and restore its level and propagate with monkeypatch; run T19's resolution, then orch.setup_logging(<tmp state dir>), replay the records with log.handle, flush and close the FileHandler", expected: "the engine_*.LOG file in the tmp state dir contains 'providers.<name>: key source env:MISTRAL_API_KEY' and does not contain SECRET" }
    - { scenario: "T22 (iteration 5, FR-J) main_async with ENV_ONLY config, stopped after 'engine start'", expected: "one engine_*.LOG; ENV_SOURCE_LINE present and before 'engine start'; SECRET absent" }
    - { scenario: "T19, T20 (iteration 5, FR-K) logger level set to NOTSET first", expected: "level NOTSET and handlers unchanged after the call" }
  edge_cases:
    - "Tests must pass on Linux and macOS: monkeypatch P.sys.platform to 'darwin' and P.subprocess.run to a fake in every Keychain test; never invoke the real security binary."
    - "Use monkeypatch.delenv(..., raising=False) where a variable must be absent; the container environment is not assumed clean."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/overwatch -q; record passed/failed/skipped counts in the report (iteration 4 final on Linux: 330 passed, 1 skipped)."
    - "After the change: same command; no new failures; new tests pass."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; new findings caused by this work are fixed, pre-existing findings are listed, not fixed."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-7d953510-keychain-api-key.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; tests as test(engine), report and prompt move as docs(dev)"
  files:
    - { path: "tests/engine/test_providers.py", content: "modified (iteration 5)" }
    - path: "dev/reports/report-7d953510-keychain-api-key.md"
      content: >
        Iteration 5: update the existing report. Add a section '11.0 Iteration
        5' before Version History (with a table-of-contents entry and Return
        to Table of Contents link) holding: change summary, baseline and final
        test counts, mutation check results, governance check results,
        deviations (or 'None'), open points, session branch name, starting
        commit and new commit hashes. Update the status line to name
        iteration 5. Add Version History row 1.4. Leave §1.0 to §10.0
        unchanged. Iteration 1 format, kept for reference: new file. Obsidian Markdown: 'Created: <year> <month> <day>' line, table of
        contents, numbered sections, Return to Table of Contents links,
        Version History table, final line 'Copyright (c) 2026 William Watson.
        MIT License.'. Sections: 1.0 Summary; 2.0 Files changed (with
        functions); 3.0 Test results (baseline and final counts, new test
        names); 4.0 Governance checks; 5.0 Deviations from this prompt (or
        'None'); 6.0 Open points for the planner, including that the live
        validation (CLI and engine-mcp, change-7d953510) was not possible in
        the cloud environment; 7.0 Starting commit and commit hashes pushed to main.

success_criteria:
  - "T1–T18 and T21 unchanged and passing; T19 and T20 changed only per FR-K and passing; T22 present and passing"
  - "Mutation check: M1 fails T22; M4 fails T19 or T20 in a full run"
  - "Full suite: no failures beyond the recorded baseline (expected 331 passed, 1 skipped)"
  - "git diff <starting commit>..HEAD touches only test_providers.py, the report and the prompt move; nothing under ai/"
  - "No test output or failure message can carry the key value"
  - "Commits pushed to the session branch, not merged; report §11.0 lists the branch, the starting commit and the new commit hashes"

notes: "The planner reviews the session branch before the operator merges it into main fast-forward only. No follow-up audit for this test-only iteration. The live validation on macOS follows separately."
```

Copyright (c) 2026 William Watson. MIT License.
