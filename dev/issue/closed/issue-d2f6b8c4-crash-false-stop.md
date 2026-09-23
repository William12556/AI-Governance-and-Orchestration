Created: 2026 June 26

```yaml
issue_info:
  id: "issue-d2f6b8c4"
  title: "Tool-call truncation crash, substring error misclassification, and stale-signal false completion"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d2f6b8c4"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), correctness findings F3, F7,
    F11. A truncation-ordering defect can abort a phase; substring error
    classification produces false BLOCKs; a stale signal file yields a false
    immediate completion.

affected_scope:
  components:
    - name: "orchestrator (run_phase, _is_mcp_error, single-phase modes)"
      file_path: "ai/ael/src/orchestrator.py"
  version: "current"

reproduction:
  prerequisites: "AEL run reaching the relevant condition (high tool-call turn; benign matching text; leftover signal file)."
  steps:
    - "F3: a model turn issues >10 tool calls; the assistant message is appended with all tool_calls, then truncated to max_tool_calls_per_iter; tool results are appended only for retained calls; the next completions request contains orphaned tool_call ids, the API rejects it, and an unhandled exception aborts the phase"
    - "F7: a benign tool result or final summary containing 'Input validation error' or '[TOOL_CALLS]' is matched by _is_mcp_error / the malformed-final guard, inflating the error count toward a false BLOCK or flagging a valid response as malformed"
    - "F11: single --mode worker/reviewer with a leftover work-complete.txt; run_phase returns 0 on iteration 1 having done nothing; startup warns only on .ralph-complete"
  frequency: "intermittent"
  reproducibility_conditions: "F3 requires >10 calls in one turn; F7 requires matching substrings in content; F11 requires a stale work-complete.txt in single-phase mode."
  error_output: "F3: API rejection of assistant tool_call ids without matching tool messages (unhandled)."

behavior:
  expected: >
    Truncation never yields an invalid conversation; error classification uses
    structured signals; single-phase modes start from a cleared signal state.
  actual: >
    A hard crash aborts the phase (F3); benign content triggers a false BLOCK or
    false malformed flag (F7); a stale signal yields an immediate false
    completion (F11).
  impact: "Phase abort on a low-frequency path; spurious blocks; no-op runs reported complete."
  workaround: "Manually clear signal files before single-phase runs."

analysis:
  root_cause: >
    F3: truncation occurs after the assistant message carrying all tool_calls is
    built. F7: _is_mcp_error and the malformed-final guard match substrings
    anywhere in content. F11: run_loop clears work-complete.txt but single-phase
    modes do not, and startup warns only on .ralph-complete.
  technical_notes: >
    F3: truncate before building the assistant message, or append only the
    retained calls. F7: classify on structured signals (tool-result status,
    finish_reason) rather than substring scans. F11: clear phase signal files at
    the start of single-phase modes, or warn on work-complete.txt.

resolution:
  approach: >
    Truncation-ordering fix (F3); structured error classification (F7); stale
    signal clearing/warning in single-phase modes (F11). All orchestrator
    changes.

verification:
  verification_steps:
    - "A turn with >10 tool calls does not raise; the conversation remains valid"
    - "A benign result/summary containing 'Input validation error' or '[TOOL_CALLS]' is not misclassified"
    - "Single --mode worker/reviewer with a stale work-complete.txt does not return complete on iteration 1"

notes: >
  Groups proposal-f9a2c41b findings F3 (high), F7 (medium), F11 (medium). All
  source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Resolved: fix implemented and verified against source; issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
