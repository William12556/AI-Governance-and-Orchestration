Created: 2026 June 26

```yaml
issue_info:
  id: "issue-b9d2f4a7"
  title: "Reviewer syntax gate unexecutable, budget undercount, and interpreter/tool assumptions"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-b9d2f4a7"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), accuracy/portability findings
    F6, F8, F9. The reviewer syntax gate cannot run, the token budget is
    undercounted, and interpreter/tool invocations assume an environment.

affected_scope:
  components:
    - name: "orchestrator (estimate_tokens, main_async, py_compile, run_preflight_check)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
  version: "current"

reproduction:
  prerequisites: "AEL run reaching the relevant condition."
  steps:
    - "F6: ralph-review.yaml instructs the reviewer to run 'python -m py_compile', but the reviewer's tools are filesystem and grep only (no shell); the gate cannot be executed and is skipped or fabricated"
    - "F8: estimate_tokens sums message content only; the tools JSON schema array (18 schemas) is never counted and main_async zeroes the system prompt; the abort threshold can be passed without warning"
    - "F9: py_compile runs as ['python','-m',...] using PATH rather than sys.executable; grep in run_preflight_check is assumed present"
  frequency: "always"
  reproducibility_conditions: "F6 every review phase; F8 every request (magnitude grows with tool count); F9 under venv/PATH variance or absent grep."

behavior:
  expected: >
    The syntax gate is executed by the orchestrator on modified .py files and the
    result injected; the budget estimate includes the tool schema and rendered
    system prompt; interpreter and external-tool invocations are
    environment-safe.
  actual: >
    The reviewer cannot run the gate and may fabricate it (F6); the budget
    undercounts and can overflow before warning (F8); the interpreter/tool
    assumptions misbehave across environments (F9).
  impact: "False syntax assurance; context overflow without warning; check misbehaviour across environments."
  workaround: "None reliable."

analysis:
  root_cause: >
    F6: the recipe instructs a shell action the reviewer cannot perform. F8:
    estimate_tokens omits the serialized tool schema and the system prompt; the
    docstring's 'overestimates, safe direction' claim is incorrect. F9: PATH
    'python' may differ from the running interpreter; grep presence is assumed.
  technical_notes: >
    F6: have the orchestrator run py_compile on modified .py files at review time
    and inject the result, rather than instructing the model. F8: include
    serialized tool-schema length and the rendered system prompt in the estimate.
    F9: use sys.executable; guard external tools (grep).

resolution:
  approach: >
    Move the syntax gate into the orchestrator and remove the reviewer-run
    instruction from ralph-review.yaml (F6); correct estimate_tokens (F8); use
    sys.executable and guard grep (F9). Source changes.

verification:
  verification_steps:
    - "Syntax of modified .py is verified by the orchestrator and the result injected into the reviewer context"
    - "The budget estimate includes the tool schema and system prompt; the abort threshold accounts for them"
    - "py_compile uses the running interpreter; a missing grep is handled without an unhandled error"

notes: >
  Groups proposal-f9a2c41b findings F6 (medium), F8 (medium), F9 (medium). F6
  touches ralph-review.yaml (remove the reviewer-run gate) and orchestrator (run
  the gate); F8 and F9 are orchestrator. All source changes.

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
