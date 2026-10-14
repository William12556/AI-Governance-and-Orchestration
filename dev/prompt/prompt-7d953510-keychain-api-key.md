Created: 2026 October 14

```yaml
prompt_info:
  id: "prompt-7d953510"
  task_type: "code_generation"
  source_ref: "change-7d953510"
  target_profile: "claude_code"
  date: "2026-10-14"
  iteration: 1
  coupled_docs:
    change_ref: "change-7d953510"
    change_iteration: 1

context:
  purpose: "Allow a provider API key to be loaded from the macOS login Keychain."
  integration: "providers._api_key() is called by make_provider() for every provider in ai/config.yaml."
  constraints:
    - "Modify only ai/engine/src/providers.py and tests/engine/test_providers.py"
    - "No new dependencies"
    - "The key must never appear in log records, exception messages or return values other than _api_key()'s"
    - "Existing api_key_env and literal api_key behaviour and messages unchanged"

specification:
  description: "Add optional provider key api_key_keychain (Keychain service name, non-empty string)."
  requirements:
    functional:
      - "Resolution order in _api_key(name, pcfg, kind): (1) if api_key_env is configured and os.environ has a non-empty value → return it, source 'env:<VAR>'; (2) elif api_key_keychain is configured → return _keychain_secret(name, service), source 'keychain:<service>'; (3) elif api_key_env is configured → raise the existing 'environment variable <VAR> is not set' ConfigError; (4) existing literal api_key and omlx rules unchanged"
      - "When api_key_keychain is present but not a non-empty str → ConfigError 'providers.<name>.api_key_keychain: must be a non-empty string'"
      - "On success from steps 1 or 2, log at INFO: 'providers.<name>: key source <label>'"
      - "When neither api_key_env nor api_key_keychain nor api_key is given for a non-omlx kind, the error message names both api_key_env and api_key_keychain"
    technical:
      language: "Python"
      version: "3.10+"
      standards:
        - "Type hints and docstrings in the module's existing style"
        - "Module-level constants: _SECURITY = '/usr/bin/security', _KEYCHAIN_TIMEOUT = 10"

design:
  architecture: "One private helper; no new classes."
  components:
    - name: "_keychain_secret"
      type: "function"
      purpose: "Read a generic-password secret from the login Keychain."
      interface:
        inputs:
          - { name: "name", type: "str", description: "provider name, for messages" }
          - { name: "service", type: "str", description: "Keychain service" }
        outputs: { type: "str", description: "secret with trailing newline removed" }
        raises: ["ConfigError"]
      logic:
        - "If sys.platform != 'darwin': ConfigError 'providers.<name>.api_key_keychain: supported on macOS only; use api_key_env'"
        - "subprocess.run([_SECURITY, 'find-generic-password', '-s', service, '-w'], capture_output=True, text=True, timeout=_KEYCHAIN_TIMEOUT, check=False)"
        - "FileNotFoundError/OSError → ConfigError '<_SECURITY> not available'"
        - "subprocess.TimeoutExpired → ConfigError 'Keychain lookup for service <service> timed out after 10 s (Keychain locked or access dialog unanswered)'"
        - "returncode != 0 → ConfigError 'no readable Keychain item for service <service> (security exit <code>)'; do not include stdout or stderr"
        - "value = stdout.rstrip('\\n'); empty → ConfigError 'Keychain item for service <service> is empty'"
  dependencies:
    internal: ["ConfigError", "log"]
    external: ["subprocess", "sys (stdlib)"]

error_handling:
  strategy: "All failures raise ConfigError naming the config key; never chain exceptions that carry stdout ('raise ... from None' for CalledProcess-like paths)."
  logging:
    level: "INFO for key source; no DEBUG output of command results"

testing:
  unit_tests:
    - { scenario: "env set + keychain configured", expected: "env value; subprocess.run not called; log 'key source env:MISTRAL_API_KEY'" }
    - { scenario: "env configured but unset + keychain configured", expected: "keychain value" }
    - { scenario: "keychain only", expected: "value; exact argv and timeout=10 asserted" }
    - { scenario: "stdout 'secret\\n'", expected: "'secret'" }
    - { scenario: "returncode 44", expected: "ConfigError containing 'exit 44' and service; not containing stderr text" }
    - { scenario: "TimeoutExpired", expected: "ConfigError mentioning timeout" }
    - { scenario: "empty stdout", expected: "ConfigError" }
    - { scenario: "sys.platform 'linux'", expected: "ConfigError; subprocess.run not called" }
    - { scenario: "FileNotFoundError", expected: "ConfigError" }
    - { scenario: "api_key_keychain '' or 123", expected: "ConfigError" }
    - { scenario: "caplog over successful keychain lookup", expected: "secret absent from every record and from str() of any raised error in failure tests" }
    - { scenario: "make_provider with openai_compatible + api_key_keychain", expected: "OpenAICompatProvider built (client stubbed)" }
  edge_cases:
    - "Literal api_key plus api_key_keychain on a remote base_url: keychain wins (step 2 precedes step 4)"
  validation:
    - "pytest tests/engine/ passes offline"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - { path: "ai/engine/src/providers.py", content: "modified" }
    - { path: "tests/engine/test_providers.py", content: "modified" }

success_criteria:
  - "All listed unit tests present and passing"
  - "Full test suite passes"
  - "No change to files outside the two deliverables"
  - "git diff shows no secret-bearing log or exception text"

notes: "Documents listed in change-7d953510 implementation_steps are updated by the planner, not in this prompt."
```

Copyright (c) 2026 William Watson. MIT License.
