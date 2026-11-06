Created: 2026 November 6

```yaml
change_info:
  id: "change-86c958dd"
  title: "Run record, status and context-window order (Stage C work item 2)"
  date: "2026-11-06"
  status: "approved"  # operator approval 2026-11-06
  priority: "low"
  iteration: 2
  coupled_docs:
    issue_ref: "issue-86c958dd"
    issue_iteration: 2

source:
  type: "issue"
  reference: "issue-86c958dd"
  description: "Remediate issue-86c958dd iteration 2: audit-b8a6c445 F-01 to F-05 and F-08, live-check observations P-01 and P-02, and the context-window resolution order (CW), with the operator decisions of 2026-11-05 for F-02, F-03 and CW."

scope:
  summary: >
    Engine: (A1, F-01) run.json records the run's exit code: every early
    return inside the run's try assigns rc, and an exception in flight
    records rc null with the exception type. (A2, F-08) the start record
    is built inside its guarded write. (A3, P-01) HTTP 404 is not retried.
    (A4, P-02) manifest.yaml states governance 12.8. (D, CW) the context
    window resolves global override, then per-model entry, then live
    query, then unresolved. Overwatch: (B1, F-02) BLOCKED.md or .complete
    outranks an ended run record only when the marker is not older than
    the record's start. (B2, F-03) FR-02-06 is evaluated only while the
    status is running. (B3, F-04) the FR-02-06 path comparison uses
    os.path.samefile. Tests: (C, F-05) the audit-b8a6c445 F-05 list, plus
    tests for A1 to A3, B1 to B3 and D.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }  # D: docstring only
    - { name: "config template", file_path: "ai/engine/config.template.yaml", change_type: "modify" }  # D: comments only
    - { name: "governance manifest", file_path: "ai/governance/software-engineering/manifest.yaml", change_type: "modify" }  # A4
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py", change_type: "modify" }
    - { name: "engine tests", file_path: "tests/engine/test_run_record.py", change_type: "modify" }
    - { name: "provider tests", file_path: "tests/engine/test_providers.py", change_type: "modify" }
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py", change_type: "modify" }
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "ael design", file_path: "dev/design/design-ael-orchestrator.md", change_type: "modify" }  # planner
    - { name: "overwatch design", file_path: "dev/design/design-project-overwatch.md", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
    - { name: "engine README", file_path: "ai/engine/README.md", change_type: "modify" }  # planner
    - { name: "getting started guide", file_path: "docs/guide-getting-started.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§4.2 (configuration tiers)", "§7.0 (run.json fields)", "§11.0 (HTTP 404; run record with an exception)", "Version History"] }
    - { design_ref: "design-ael-orchestrator", sections: ["§7.0 Context Window Resolution", "Version History"] }
    - { design_ref: "design-project-overwatch", sections: ["§4.0 status precedence", "§5.0 FR-02-06", "Version History"] }
  out_of_scope:
    - "audit-b8a6c445 F-07 (run.json mode, orphan temporary files, fsync)"
    - "The 'engine end rc=N' log line: unchanged (governance P00.11 and existing tests rely on it)"
    - "Readiness behaviour for a model oMLX does not list (issue technical notes)"
    - "engine-mcp"
    - "Clearing a stale BLOCKED.md or .complete at loop start"
    - "requirements-1c1f4ef6 FR-AEL-008 wording (see notes)"

rational:
  problem_statement: "See issue-86c958dd."
  proposed_solution: "Assign rc at every early return and record an in-flight exception as rc null with its type; move the start record into its guarded write; add 404 to the non-retryable statuses; correct the manifest version; reorder the context-window tiers; make Overwatch's precedence and FR-02-06 depend on the run record's start time and status, and compare paths by file identity."
  alternatives_considered:
    - option: "F-01: document that rc is main_async's return value and excludes uncaught exceptions"
      reason_rejected: "The issue's expected behaviour (iteration 1) requires the record to match the exit status"
    - option: "F-02: extend the accepted risk to .complete"
      reason_rejected: "Operator decision 2026-11-05: marker counts only when not older than the run's start"
    - option: "F-04: case-fold both resolved paths on Darwin"
      reason_rejected: "os.path.samefile compares file identity on every platform and needs no platform branch"
    - option: "CW: keep the order and document that per-model entries apply only when the live query returns null"
      reason_rejected: "Operator decision 2026-11-05: the per-model entry is used before the live query"
  benefits:
    - "Overwatch shows the outcome of the latest run, not of an earlier one"
    - "FR-02-06 warns only about a running engine"
    - "run.json agrees with the process exit status"
    - "A missing model fails at the first attempt"
    - "Per-role context windows from the configuration apply as the template and profiles state"
  risks:
    - risk: "D: a project whose model_context_windows entry was written as a fallback for a model that now reports a larger live window gets the smaller configured value"
      mitigation: "The configured value is the operator's statement; downstream entries are checked before propagation (deployment notes)"
    - risk: "B1: a marker written within the same second as the run's start but before it compares as not older (started has one-second resolution)"
      mitigation: "Accepted: a marker from the same run is the intended case; a marker from an earlier run in the same second is improbable"
    - risk: "A3: a provider that returns 404 for a transient routing error is no longer retried"
      mitigation: "The BLOCKED.md text names the status; the operator reruns"

technical_details:
  current_behavior: "See issue-86c958dd behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) In main_async, every 'return 1' inside the try that follows
    setup_logging (orchestrator.py:2773, :2811, :2852, :2860 at 90fb563)
    becomes 'rc = 1' followed by 'return rc'. An 'except BaseException as
    exc:' clause before the finally stores the exception and re-raises it.
    When an exception was stored, the end record has rc null and an added
    field "error" holding type(exc).__name__; otherwise "error" is absent
    and rc is the value returned. The log line 'engine end rc=N' is
    unchanged. (A2) The start record dict is built inside the try that
    guards its _write_run_record call; an exception there is logged as
    'run record not written: <exc>' and the run continues without a run
    record, as a write failure does today. (A3) _NON_RETRYABLE_STATUS gains
    404. (A4) manifest.yaml version '12.8'. (B1) In
    Overwatch._read_engine_state, when a valid record exists and is not
    live, BLOCKED.md (then .complete) gives 'blocked' (then 'ship') only
    when the marker file's mtime is not earlier than the record's started
    time (datetime.fromisoformat; seconds resolution); otherwise the status
    is 'ended'. When started cannot be parsed, or no valid record exists,
    precedence is unchanged. (B2) The FR-02-06 check runs only when the
    engine status is 'running'. (B3) The FR-02-06 comparison uses
    os.path.samefile(task_file, doc.path) inside a try; an OSError or
    ValueError compares as not the same file. (D) resolve_context_window:
    tier 1 context.context_window; tier 2
    context.model_context_windows[model_name]; tier 3 the live query; tier
    4 unresolved. Log texts and tiers_tried strings follow the new numbers
    ('tier 2: config per-model override', 'tier 3: live oMLX admin query').
    The docstring, providers.py:233 and the config.template.yaml comments
    state the new order.
  implementation_approach: "Claude Code cloud session per a T04 prompt after approval, on a session branch. The planner updates design-14e05e35, design-ael-orchestrator, design-project-overwatch, the operations guide, ai/engine/README.md and docs/guide-getting-started.md after review."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A1 rc at early returns and exception record; A2 start record in its guarded write; A3 404; D tier order"
      functions_affected: ["main_async", "resolve_context_window", "_NON_RETRYABLE_STATUS"]
    - component: "providers"
      file: "ai/engine/src/providers.py"
      change_summary: "D docstring of the live query ('tier 3')"
      functions_affected: ["live_context_window docstring"]
    - component: "config template"
      file: "ai/engine/config.template.yaml"
      change_summary: "D comments on context_window and model_context_windows"
      functions_affected: []
    - component: "manifest"
      file: "ai/governance/software-engineering/manifest.yaml"
      change_summary: "A4 version 12.8"
      functions_affected: []
    - component: "overwatch"
      file: "ai/webui/src/overwatch.py"
      change_summary: "B1 marker age; B2 FR-02-06 only while running; B3 samefile"
      functions_affected: ["_read_engine_state", "FR-02-06 check"]
  interface_changes:
    - interface: "run.json"
      change_type: "contract"
      details: "rc may be null with an added 'error' field when the run ends with an exception"
      backward_compatible: "yes: Overwatch already treats a non-int rc as unknown"
    - interface: "Context window resolution"
      change_type: "contract"
      details: "Per-model entry before the live query; log text tier numbers change"
      backward_compatible: "no for a configuration that relied on the live value overriding its entry"
    - interface: "Overwatch status"
      change_type: "contract"
      details: "A marker older than the run record's start no longer outranks 'ended'; FR-02-06 only while running"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library only" }

testing_requirements:
  test_approach: "pytest, no network, no model (NFR-06), as test_run_record.py, test_providers.py and test_overwatch.py do."
  test_cases:
    - { scenario: "A1a: run_loop stubbed to return 0 and 2", expected: "run.json rc 0 and 2; no 'error' field" }
    - { scenario: "A1b: each of the four early returns after setup_logging", expected: "rc 1 in run.json, returned 1" }
    - { scenario: "A1c: _finish_run raises RuntimeError after rc = 0; and KeyboardInterrupt", expected: "exception propagates; run.json rc null, error 'RuntimeError' / 'KeyboardInterrupt'; log 'engine end rc=' line present" }
    - { scenario: "A2: datetime.now raising during the start record", expected: "warning 'run record not written'; run continues; no run.json" }
    - { scenario: "A2b (F-05): only the second _write_run_record call fails", expected: "rc unchanged; warning logged; start record left in place" }
    - { scenario: "A3: completion raising an error with status 404", expected: "one attempt; BLOCKED.md names 404" }
    - { scenario: "A4: manifest version equals the latest governance.md version-history entry", expected: "equal (test reads both files)" }
    - { scenario: "B1: ended record; BLOCKED.md and .complete each older and not older than started; unparsable started", expected: "older: ended; not older: blocked / ship; unparsable: blocked / ship" }
    - { scenario: "B2: ended record whose task_file is not an open prompt", expected: "no FR-02-06 alert; with a live record: alert" }
    - { scenario: "B3: live record whose task_file differs in letter case from the open prompt on a case-insensitive file system (skip where the tmp file system is case-sensitive); task_file missing", expected: "same file: no alert; missing: alert" }
    - { scenario: "C (F-05, audit-b8a6c445 §8.4): O1 cases for pid as bool and string, ended as a number, rc as bool, an invalid record with BLOCKED.md, a live record with .complete; _pid_alive for 0, -1 and PermissionError; task_ref assertions; FR-02-06 silent with an invalid record; O3 with one document directly in test/; 'run.json' in SIGNAL_FILES", expected: "as specified in audit-b8a6c445 §8.4 F-05" }
    - { scenario: "D1: per-model entry 40960 and live query returning 1000", expected: "40960; log names tier 2" }
    - { scenario: "D2: no per-model entry, live query 1000", expected: "1000; log names tier 3" }
    - { scenario: "D3: global override set", expected: "global value whatever the other tiers give" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline; full macOS suite including tests/engine/test_engine_mcp.py run by the operator"
    - "Mutations: removing each new branch fails at least one named test"
    - "Live: one dev/smoke loop with task-scoped.md and --config config-mistral.reference.yaml ends in SHIP; its log shows the worker context window from model_context_windows (tier 2); run.json rc 0. One run with --reviewer-model no-such-model ends BLOCKED at the first attempt naming 404"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "4-6 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-86c958dd)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "Planner documents (affected_components marked planner)", owner: "planner" }
    - { step: "Live check in dev/smoke", owner: "operator" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation after Stage C work item 6. Before propagating, check each downstream ai/config.yaml model_context_windows entry: it now takes precedence over the live oMLX value."

traceability:
  related_changes:
    - { change_ref: "change-b8a6c445", relationship: "follows up (run.json, Overwatch status)" }
    - { change_ref: "change-711a57d5", relationship: "modifies (non-retryable statuses)" }
    - { change_ref: "change-53c6f252", relationship: "modifies (per-role context window resolution)" }
  related_issues:
    - { issue_ref: "issue-86c958dd", relationship: "source" }

notes: "Operator decisions 2026-11-05: F-02, F-03 and CW. Proposed by the planner for approval: the 'error' field for A1; os.path.samefile for B3; 404 added to the non-retryable set without other statuses. The planner also proposes to amend requirements-1c1f4ef6 FR-AEL-008, which still describes the retired config.json reading, to the four-tier order, as a document-only correction with this change's planner updates."

version_history:
  - version: "1.0"
    date: "2026-11-06"
    changes: ["Initial change record (iteration 2, matching issue-86c958dd iteration 2)"]
  - version: "1.1"
    date: "2026-11-06"
    changes: ["Approved by the operator as drafted, including the planner's proposals: the 'error' field (A1), os.path.samefile (B3), 404 only (A3) and the FR-AEL-008 document correction; implementation per prompt-86c958dd"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
