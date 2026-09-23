Created: 2026 July 17

```yaml
issue_info:
  id: "issue-5bdc2d9b"
  title: "AEL orchestrator SHIP gate does not verify pytest results for modified/added tests"
  date: "2026-07-17"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-5bdc2d9b"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: ""
  description: >
    Review of T04 prompt-authoring instructions and the AEL orchestrator's
    existing SHIP-gate family (read-evidence gate, audit coverage/scope gate)
    found no gate that executes pytest and inspects the result before accepting
    a reviewer's SHIP verdict in the non-audit (ralph) loop. T04 v1.11 now
    instructs deliverable.format_requirements to request pytest execution, and
    governance P06 §1.7.15 now mandates a Claude-Code-side PostToolUse pytest
    hook (ai/skills/validation/run-tests.md), but neither mechanism is
    orchestrator-enforced: a reviewer can still emit SHIP without pytest having
    been run, or after a failing run, for AEL-executed tasks (target_profile:
    ael), since the tactical_brief path used for AEL does not carry
    deliverable.format_requirements.

affected_scope:
  components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
  designs: []
  version: "current"

reproduction:
  prerequisites: "Ralph Loop (--mode loop, ael target profile), reviewer that emits SHIP without running or despite a failing pytest suite."
  steps:
    - "T04 prompt with target_profile: ael and coupled test files under tests/ is issued to AEL"
    - "Worker completes; work-summary.txt lists deliverable files including modified tests/ paths"
    - "Reviewer final message begins with SHIP without having run pytest, or despite pytest failing"
    - "run_loop accepts SHIP; no gate cross-checks test execution or result"
  frequency: "always"
  reproducibility_conditions: "Applies to every ael-profile task touching tests/; independent of reviewer model."
  preconditions: ""
  test_data: ""
  error_output: ""

behavior:
  expected: >
    SHIP is accepted for tasks touching tests/ only when pytest has been run
    against the affected test paths and exits 0. A SHIP issued without a
    passing run is overridden to REVISE, mirroring the existing read-evidence
    and audit coverage gates.
  actual: >
    SHIP acceptance depends only on the reviewer's final-message token
    (_normalize_verdict); pytest execution and result are not checked.
  impact: "AEL-shipped code with modified/added tests/ can ship without the test suite having actually passed."
  workaround: "Manual post-SHIP pytest run by Strategic Domain before T06 acceptance."

environment:
  python_version: ""
  os: ""
  dependencies: []
  domain: ""

analysis:
  root_cause: >
    No SHIP-gate function inspects test execution state; existing gates
    (read-evidence, audit coverage/scope) check reviewer read behaviour and
    checklist state, not command execution results.
  technical_notes: >
    Precedent: the read-evidence SHIP gate (issue-d7f4a1c8/change-d7f4a1c8)
    established the pattern — deterministic, orchestrator-side gate that
    overrides SHIP to REVISE with feedback naming the deficiency. A pytest
    SHIP gate would follow the same shape: on SHIP verdict, if the deliverable
    set (from work-summary.txt) includes any path under tests/ or src/,
    require evidence that pytest was executed and passed (e.g. exit-code
    capture from a tool call, or a required worker-reported test-result
    block) before accepting; otherwise override to REVISE naming the missing
    or failing evidence. Exact evidence-capture mechanism (parse worker tool
    calls vs. require a structured result field) is a design decision for the
    T02 change document.
  related_issues:
    - issue_ref: "issue-d7f4a1c8"
      relationship: "related"

resolution:
  assigned_to: "Claude Code (Opus 4.5)"
  target_date: "2026-07-17"
  approach: "Orchestrator-native pytest gate with SHIP override"
  change_ref: "change-5bdc2d9b"
  resolved_date: "2026-07-17"
  resolved_by: "Claude Code (Opus 4.5)"
  fix_description: >
    Added _run_pytest_gate(state_dir, log, project_root) to orchestrator.py:
    resolves test targets from deliverables (tests/ direct; src/<component>/
    maps to tests/<component>/ if exists), runs pytest via subprocess, injects
    [TEST GATE: PASS|FAIL|UNCHECKED] block into reviewer context. SHIP override
    in run_loop converts SHIP to REVISE when gate reports FAIL. Commit a9173f2.

verification:
  verified_date: "2026-07-17"
  verified_by: "Claude Desktop (P08 strategic audit)"
  test_results: "Independently confirmed against source (see change-5bdc2d9b verification.test_results for the full item-by-item audit); Claude Code's implementation and self-check hold up under independent review"
  closure_notes: "Implemented via change-5bdc2d9b, commit a9173f2; independently verified by Claude Desktop (P08 strategic audit), 2026-07-17. AEL now has a deterministic pytest SHIP gate matching claude_code/claude_omlx coverage."

prevention:
  preventive_measures: ""
  process_improvements: ""

verification_enhanced:
  verification_steps: []
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-5bdc2d9b"
  test_refs: []

notes: >
  Companion to T04 v1.11 (deliverable.format_requirements pytest instruction)
  and governance 9.12 (P06 §1.7.15 mandatory PostToolUse pytest hook,
  ai/skills/validation/run-tests.md). Those two changes address claude_code
  and claude_omlx target profiles; this issue addresses the remaining ael
  target profile gap via orchestrator-side enforcement.

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Coupled to change-5bdc2d9b (proposed); status open → investigating"
  - version: "1.2"
    date: "2026-07-17"
    author: "Claude Code (Opus 4.5)"
    changes:
      - "Resolved via change-5bdc2d9b (commit a9173f2); status investigating → resolved"
  - version: "1.3"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Independently verified against source (Claude Desktop, P08 strategic audit); verified_by corrected to reflect Strategic Domain audit rather than implementer self-attestation; issue closed"
  - version: "1.4"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
