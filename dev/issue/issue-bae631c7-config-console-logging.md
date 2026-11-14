Created: 2026 November 14

```yaml
issue_info:
  id: "issue-bae631c7"
  title: "Engine runtime hygiene: console prefix consumed by Rich, RecursionError in _load_config, unvalidated model_context_windows, MCP catalogue reporting, dead code"
  date: "2026-11-14"
  status: "resolved"  # change-bae631c7 implemented 2026-11-14 (P03.7)
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-bae631c7"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 L-13, L-16; audit-b8c75bac F-05; audit-86c958dd F-02; report-86c958dd §6.0; report-b8c75bac §6.0 item 5
  description: >
    Stage C work item 5B-1 (dev/task.md row bae631c7): work item 5 parts
    (f), (g) for _load_config and (h), with audit-caab2052 L-13 and L-16.
    Raised by the autonomous session of 2026-11-14 (prompt-cf99f3f3,
    report-b3a503a2) under the operator's one-time exemption.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }  # (f), (g), (h), L-16
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py" }  # L-13, L-16
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py" }  # L-16
    - { name: "providers", file_path: "ai/engine/src/providers.py" }  # L-16
    - { name: "stages", file_path: "ai/engine/src/stages.py" }  # L-16
  designs:
    - { design_ref: "design-14e05e35 §3.0 Configuration, §11.0 Error Handling" }
    - { design_ref: "requirements-14e05e35 NFR-04" }
  version: "main 9b75595"

reproduction:
  prerequisites: "main 9b75595"
  steps:
    - "(f) run the engine with an unreadable configuration: the console shows ' configuration error (...)' without the '[engine]' prefix that the source writes"
    - "(g) run the engine with an ai/config.yaml holding 20,000 nested '[': the run ends with a RecursionError traceback"
    - "(h) set context.model_context_windows: null, or an entry of null, 0, -1, true or a string, and run the engine with that model"
    - "L-13: configure two MCP servers that both offer a tool named read_file; configure one server whose command does not exist"
    - "L-16: ruff check --isolated --select F ai/engine/src; mypy stages.py"
  frequency: "always, under the stated condition"
  error_output: "(g) RecursionError traceback. (h) TypeError: argument of type 'NoneType' is not iterable (null mapping); TypeError from int(None) after the start record (null entry); a logging traceback for a string entry."

behavior:
  expected: >
    (f) Console lines keep their '[engine]' prefix. (g) Deeply nested
    configuration YAML is reported as a configuration error naming the
    file, with no traceback and no state written (NFR-04; design §11.0).
    (h) A null model_context_windows mapping is treated as empty; an
    entry that is not a positive integer is refused before any state is
    written, naming file and field. L-13: a tool name offered by two
    servers and a server that fails to connect are reported in the engine
    log as well as on the console. L-16: no unused import or variable, no
    f-string without placeholders, and the approvals fallback has the
    declared type.
  actual: >
    (f) Rich reads '[engine]' after a style tag as markup and drops it;
    75 console.print sites in orchestrator.py are affected. (g)
    _load_config catches OSError and yaml.YAMLError only. (h)
    resolve_context_window tests 'model_name in model_overrides' on None
    and calls int() on any entry; an entry of 0 or a negative number
    replaces a valid live value, and 0 disables budget tracking. The
    comment in _completion_with_retry names HTTP 400/401/403 although 404
    is not retried either. L-13: mcp_client.connect overwrites a
    duplicate tool name silently and only prints a connection failure.
    L-16: mcp_client.py:11 (uuid), orchestrator.py:74 (Rule), :1303
    (pct_str), :1454 and providers.py:646 (f-strings without
    placeholders), protocol_checker.py:180 (by_id), stages.py:298
    (approvals = set() where a dict is declared).
  impact: "(f) console lines lose their source marker. (g), (h) a run ends with a traceback, in two cases after the start record was written. L-13: a run with fewer tools than configured leaves no trace in the engine log. L-16: none at run time."
  workaround: "(g), (h) correct the configuration by hand. L-13: read the console output of the run."

environment:
  os: "platform-independent"

analysis:
  root_cause: >
    Line numbers at main 9b75595. (f) orchestrator.py: every
    console.print of the form '[<style>][engine] …' (75 sites). (g)
    orchestrator.py:623-633. (h) orchestrator.py:523-524 (comment),
    :792-796 (tier 2), main_async :2693-2725 (configuration checks do not
    cover context.model_context_windows). L-13: mcp_client.py:68-77.
    L-16: as listed under behavior.actual.
  technical_notes: >
    Rich renders '\[' as a literal '['. In a Python string literal the
    escape is written '\\[engine]'. gates.DEFAULT_PYTEST_COMMAND (L-16:
    'unreachable through the engine') is used by a direct call of
    run_command_gate with an empty spec, which
    tests/engine/test_scope_gate_hardening.py exercises; it is not dead
    code. The stale docstring test paths named in L-16 exist since
    change-e4428fd5. The annotation-style and remaining mypy items of
    L-16 have no behavioural effect.

resolution:
  approach: "To be defined in change-bae631c7."
  change_ref: "change-bae631c7"

traceability:
  design_refs: ["design-14e05e35 §3.0", "design-14e05e35 §11.0", "requirements-14e05e35 NFR-04"]
  change_refs: ["change-bae631c7"]

notes: "Audit references: audit-caab2052 L-13, L-16 (§14.0, decided 2026-11-14 by the session under the one-time exemption); audit-b8c75bac F-05; audit-86c958dd F-02; report-86c958dd §6.0; report-b8c75bac §6.0 item 5."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial issue for Stage C work item 5B-1"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Status resolved: change-bae631c7 implemented (P03.7)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
