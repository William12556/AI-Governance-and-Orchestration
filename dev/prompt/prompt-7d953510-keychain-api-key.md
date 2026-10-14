Created: 2026 October 14

```yaml
prompt_info:
  id: "prompt-7d953510"
  task_type: "code_generation"
  source_ref: "change-7d953510"
  target_profile: "claude_code"  # Claude Code cloud session (operator decision 2026-10-14)
  date: "2026-10-14"
  iteration: 1
  coupled_docs:
    change_ref: "change-7d953510"
    change_iteration: 1

context:
  purpose: >
    Let a provider API key be read from the macOS login Keychain through a new
    optional provider key api_key_keychain (design-14e05e35 v1.12 §3.0 Keys,
    §11.0; requirements-14e05e35 v1.5 FR-04-07).
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
    - "Execution environment: Claude Code cloud (Linux container, repository clone). There is no macOS, no /usr/bin/security, no Keychain, no oMLX and no Mistral or Anthropic API key. Do not attempt a live run, do not start the engine or engine-mcp, and do not call any network endpoint other than package installation."
    - "Source changes are limited to ai/engine/src/providers.py and tests/engine/test_providers.py."
    - "Governance changes are limited to: moving this prompt to dev/prompt/closed/, and creating the report named in deliverable.files. Do not edit the issue, change, requirements or design documents, ai/config.yaml, ai/engine/config.template.yaml, ai/engine/doc/, ai/profiles/ or README files; the planner updates those after review."
    - "No new dependencies; standard library only (subprocess, sys)."
    - "The key value must never appear in a log record, an exception message, an exception's chained cause or context, or a test failure message."
    - "Existing behaviour and messages for api_key_env, literal api_key and kind omlx stay unchanged, except the single error message named in specification.requirements.functional."
    - "Work directly on main (CLAUDE.md §4.0). Record the starting commit hash before any edit. Commit to main and push; do not create branches, force-push or rewrite history."
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
  edge_cases:
    - "Tests must pass on Linux and macOS: monkeypatch P.sys.platform to 'darwin' and P.subprocess.run to a fake in every Keychain test; never invoke the real security binary."
    - "Use monkeypatch.delenv(..., raising=False) where a variable must be absent; the container environment is not assumed clean."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/overwatch -q; record passed/failed/skipped counts in the report."
    - "After the change: same command; no new failures; new tests pass."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; record results; new findings caused by this work are fixed, pre-existing findings are listed, not fixed."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-7d953510-keychain-api-key.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; source as feat(engine), report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/providers.py", content: "modified" }
    - { path: "tests/engine/test_providers.py", content: "modified" }
    - path: "dev/reports/report-7d953510-keychain-api-key.md"
      content: >
        New. Obsidian Markdown: 'Created: <year> <month> <day>' line, table of
        contents, numbered sections, Return to Table of Contents links,
        Version History table, final line 'Copyright (c) 2026 William Watson.
        MIT License.'. Sections: 1.0 Summary; 2.0 Files changed (with
        functions); 3.0 Test results (baseline and final counts, new test
        names); 4.0 Governance checks; 5.0 Deviations from this prompt (or
        'None'); 6.0 Open points for the planner, including that the live
        validation (CLI and engine-mcp, change-7d953510) was not possible in
        the cloud environment; 7.0 Starting commit and commit hashes pushed to main.

success_criteria:
  - "T1–T14 present and passing"
  - "Full suite: no failures beyond the recorded baseline"
  - "git diff <starting commit>..HEAD touches only providers.py, test_providers.py, the report and the prompt move"
  - "No log or exception path in the diff can carry the key value"
  - "Commits pushed to main; report §7.0 lists the starting commit and the new commit hashes"

notes: "The planner verifies the pushed commits by direct source review and runs the live validation on macOS before closing the issue and change."
```

Copyright (c) 2026 William Watson. MIT License.
