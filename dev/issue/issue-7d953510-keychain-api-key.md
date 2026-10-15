Created: 2026 October 14

```yaml
issue_info:
  id: "issue-7d953510"
  title: "Engine cannot read a provider API key from the macOS Keychain"
  date: "2026-10-14"
  status: "open"
  severity: "medium"
  type: "enhancement"
  iteration: 4
  coupled_docs:
    change_ref: "change-7d953510"
    change_iteration: 4

source:
  origin: "user_report"
  description: >
    The engine reads remote provider keys only from the environment variable
    named in api_key_env (FR-04-07). The operator keeps the Mistral API key in
    the login Keychain (service ai-go-mistral) and must inject it per process.
    Runs started through engine-mcp (start_engine) inherit the environment of
    the engine-mcp server process, so per-process injection does not reach them
    without exporting the key globally, which overrides Mistral Vibe's own key.

affected_scope:
  components:
    - { name: "providers", file_path: "ai/engine/src/providers.py" }
  designs:
    - { design_ref: "design-14e05e35 §3.0 (Keys)" }
  version: "governance 12.2"

reproduction:
  prerequisites: "providers.mistral with kind openai_compatible and api_key_env: MISTRAL_API_KEY; key stored in the login Keychain"
  steps:
    - "Start a loop run through engine-mcp start_engine without MISTRAL_API_KEY in the engine-mcp server environment"
  frequency: "always"
  error_output: "ConfigError: providers.mistral: environment variable MISTRAL_API_KEY is not set"

behavior:
  expected: "The engine obtains the key from the configured Keychain item without the key being exported to any shell or process environment."
  actual: "The run fails at provider construction unless the key is present in the engine process environment."
  impact: "Mistral API roles cannot be used through engine-mcp without a global export of the key."
  workaround: "CLI runs only: MISTRAL_API_KEY=\"$(security find-generic-password -a \"$USER\" -s ai-go-mistral -w)\" python ai/engine/src/orchestrator.py ..."

environment:
  os: "macOS (Apple Silicon)"

analysis:
  root_cause: "providers._api_key() supports api_key_env and literal api_key only; FR-04-07 restricts key sources to environment variables."
  technical_notes: >
    Profile ai/profiles/mistral_api.md §4.0 documents Keychain service
    MISTRAL_API_KEY; the operator's item uses service ai-go-mistral. §5.0
    still states reviewer verdict parsing and tool calling are unverified for
    mistral-medium-2604, although report-14e05e35-live-verification §5.0
    records a SHIP after one cycle.
    Iteration 2: subprocess.run(..., text=True) raises UnicodeDecodeError for
    Keychain output that is not valid text; iteration 1 lets it propagate
    unwrapped, and its object attribute holds the raw output
    (report-7d953510 §6.0 item 2; NFR-05).
    Iteration 3: raise ... from None suppresses display but leaves
    __context__ bound to the TimeoutExpired or UnicodeDecodeError holding the
    raw output; tests lack kind anthropic, an empty api_key_env variable and
    a __context__ assertion (audit-7d953510 L-01, L-03).
    Iteration 4: in a real run the 'key source' INFO record is lost.
    orchestrator.main_async calls build_role_bindings before setup_logging,
    so the 'engine' logger has no handler and an effective level of WARNING
    when the record is emitted (GTach engine-mcp run 1e00fd66,
    engine_20261014-150813.LOG). Unit tests attach their own handler and
    did not show this.

resolution:
  approach: "Optional api_key_keychain provider key read through /usr/bin/security; see change-7d953510."
  change_ref: "change-7d953510"

traceability:
  design_refs: ["design-14e05e35"]
  change_refs: ["change-7d953510"]

version_history:
  - version: "1.0"
    date: "2026-10-14"
    changes: ["Initial issue"]
  - version: "1.1"
    date: "2026-10-14"
    changes: ["Iteration 2: undecodable Keychain output not wrapped (report-7d953510 §6.0 item 2); iteration 1 implemented (9b4cb23) and verified on macOS (322 passed; live CLI readiness check passed)"]
  - version: "1.2"
    date: "2026-10-14"
    changes: ["Status resolved: change-7d953510 implemented (iteration 2, d4c1cdb) (P03.7; audit-7d953510 L-04)"]
  - version: "1.3"
    date: "2026-10-14"
    changes: ["Iteration 3 from audit-7d953510 L-01, L-03; status open until iteration 3 is implemented"]
  - version: "1.4"
    date: "2026-10-14"
    changes: ["Status resolved: change-7d953510 iteration 3 implemented (45a8ac0) (P03.7)"]
  - version: "1.5"
    date: "2026-10-15"
    changes: ["Iteration 4 from the GTach live run: key source line missing from the run log; status open until iteration 4 is implemented"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
