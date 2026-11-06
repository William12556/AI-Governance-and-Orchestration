Created: 2026 November 5

```yaml
issue_info:
  id: "issue-86c958dd"
  title: "Run record and status follow-up: recorded exit code, stale markers, FR-02-06 scope, path case, test gaps, 404 retry, manifest version; context-window resolution order"
  date: "2026-11-05"
  status: "resolved"  # change-86c958dd implemented (P03.7)
  severity: "low"
  type: "defect"
  iteration: 2
  coupled_docs:
    change_ref: "change-86c958dd"
    change_iteration: 2

source:
  origin: "code_review"  # follow-up audit audit-b8a6c445 and the change-b8a6c445 live check
  description: >
    Findings F-01 to F-05 and F-08 of
    dev/audit/audit-b8a6c445-followup-2026-11-05.md (§8.4, §8.5), with the
    operator decisions of 2026-11-05 for F-02 (a marker counts only when it is
    not older than the run's start) and F-03 (FR-02-06 only while the engine
    runs). Two observations from the change-b8a6c445 live check in dev/smoke
    on 2026-11-05 (P-01, P-02). F-06 was corrected by the planner; F-07 is
    optional and not raised.
    (CW) Iteration 2 (2026-11-06, Stage C work item 2, dev/task.md): the
    context-window resolution order, with the operator decision of
    2026-11-05 that a per-model entry in context.model_context_windows is
    used before the live oMLX query. It also closes the parked 'live oMLX
    context-window query enhancement' register item.

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py" }
    - { name: "governance manifest", file_path: "ai/governance/software-engineering/manifest.yaml" }
    - { name: "engine tests", file_path: "tests/engine/test_run_record.py" }
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py" }
    - { name: "providers", file_path: "ai/engine/src/providers.py" }  # CW: docstring only
    - { name: "config template", file_path: "ai/engine/config.template.yaml" }  # CW: comments
    - { name: "provider tests", file_path: "tests/engine/test_providers.py" }  # CW
  designs:
    - { design_ref: "design-project-overwatch §4.0 (status precedence), §5.0 (FR-02-06)" }
    - { design_ref: "design-14e05e35 §11.0 (Error Handling)" }
    - { design_ref: "design-14e05e35 §4.2 (configuration tiers); design-ael-orchestrator §7.0 (Context Window Resolution)" }  # CW
  version: "governance 12.8; engine and webui at main 90fb563 (iteration 2; line numbers re-verified)"

reproduction:
  prerequisites: "Engine and Overwatch at main 90fb563"
  steps:
    - "F-01: let _archive_audit_artifacts or _finish_run raise after rc = 0, or interrupt a run; compare run.json rc with the process exit status"
    - "F-02: end a run with SHIP, start a new run without reset that ends with rc 1 and writes no marker; scan"
    - "F-03: end a run, then open a prompt in ai/workspace/prompt/ (or open one for another executor); scan while no engine runs"
    - "F-04: on macOS, run the engine on an open prompt with --task spelled in a different letter case; scan"
    - "F-05: apply mutations A1 to A8 of audit-b8a6c445 §6.0; run tests/engine and tests/webui"
    - "F-08: make datetime.now() or os.path.abspath raise during the start record"
    - "P-01: run a loop with --reviewer-model set to a name oMLX cannot serve"
    - "P-02: start any run; read the 'governance model' line"
    - "CW: with kind omlx serving mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit (live max_context_window 393216) and context.model_context_windows giving that model 262144, start a run; read the 'context window (worker)' line"
  frequency: "always, under the stated condition"
  error_output: "P-01 (dev/smoke, 2026-11-05): 'completion error (attempt 1/3) ... Error code: 404 ... Model 'no-such-model' not found', repeated at attempt 2/3, then 'BLOCKED: completion call failed after 3 attempts'. P-02: 'governance model: software-engineering 12.2'. CW: 'context window: 393216 (tier 2: live oMLX admin query)'"

behavior:
  expected: >
    F-01: run.json rc is the run's exit code; when the end record is written
    with an exception in flight, rc is null and the record says so. F-02:
    BLOCKED.md or .complete outranks an ended run record only when the marker
    is not older than the record's start time. F-03: FR-02-06 is evaluated
    only while the engine status is running. F-04: the FR-02-06 comparison
    treats paths that name the same file as equal, whatever their letter
    case. F-05: every specified branch has a test that fails when the branch
    is removed. F-08: an exception while building the start record is
    logged as a run-record warning and does not end the run. P-01: an HTTP
    404 from the model endpoint is not retried; the run ends BLOCKED at the
    first attempt and names the status. P-02: manifest.yaml states the
    current governance.md version. CW: the resolution order is (1)
    context.context_window, (2) context.model_context_windows[model], (3)
    the provider's live query, (4) unresolved; a per-model entry is used
    whether or not the live query would return a value.
  actual: >
    F-01: early returns in main_async return the literal 1 without assigning
    rc, and an exception after rc = 0 records rc 0 while the process ends
    with status 1. F-02: precedence places blocked and ship above ended
    without reference to the record. F-03: FR-02-06 runs whenever a valid
    run record exists, including ended and stale records. F-04:
    os.path.realpath does not canonicalise letter case on APFS. F-05:
    mutations A1 to A7 survive and A8 removes one parametrised case. F-08:
    the start record is built outside the guarded write. P-01: three
    attempts with backoff before BLOCKED. P-02: manifest.yaml says 12.2;
    governance.md is at 12.8. CW: the live query precedes the per-model
    entry, so the entry applies only when the live query returns null;
    no setting gives Devstral 262144 and Magistral 40960 together except
    the global context.context_window, which applies one value to both
    roles.
  impact: "Overwatch can show SHIP or BLOCKED for a later run that ended otherwise, and can raise FR-02-06 while no engine runs; the run record can disagree with the exit status; a missing model costs two needless retries; the run log names the wrong governance version; the worker's context budget uses an unvalidated RoPE ceiling (393216) instead of the configured vendor-validated window (262144), contrary to the template comment and the operator profile."
  workaround: "Reset before each run; read the run log's last line ('engine end rc=N'). CW: none that keeps per-role windows."

environment:
  os: "macOS (Apple Silicon); F-01 to F-03, F-05, F-08, P-01 and P-02 are platform-independent"

analysis:
  root_cause: >
    Line numbers at main 90fb563 (re-verified for iteration 2; the
    orchestrator moved with change-b8c75bac, overwatch.py did not). F-01:
    orchestrator.py:2744 (rc default 1), :2773, :2811, :2852, :2860 (literal
    returns), :2977-2988 (finally). F-02: overwatch.py:530-535. F-03:
    overwatch.py:777. F-04: overwatch.py:780-782. F-05: tests/engine/
    test_run_record.py, tests/webui/test_overwatch.py (audit-b8a6c445 §6.0).
    F-08: orchestrator.py:2753-2760. P-01: _NON_RETRYABLE_STATUS =
    {400, 401, 403} (orchestrator.py:108); 404 is retried. CW:
    orchestrator.py:756-814 (resolve_context_window: tier 2 live query at
    :787-798 before tier 3 per-model entry at :800-806);
    tests/engine/test_providers.py:295 asserts the live value wins. P-02:
    manifest.yaml:7 'version: "12.2"   # tracks governance.md' was not raised
    with governance 12.3 to 12.8.
  technical_notes: >
    P-01: with kind omlx an unlisted model passes the readiness check by
    design (providers.py await_ready: "oMLX loads on first request"), so an
    unknown model is found only at the first call of its phase; in the live
    check the worker phase ran for about nine minutes before the reviewer
    call failed. The readiness behaviour is not changed by this issue. F-05
    test list: audit-b8a6c445 §8.4 F-05 recommendation. F-07 (run.json mode
    0600, orphan temporary files, no fsync) is optional and not part of this
    issue. CW documents stating the order: the resolve_context_window
    docstring and log texts, providers.py:233 (live query called 'Tier 2'),
    config.template.yaml:115-123, guide-engine-operations §3.0 (example
    comment) and §6.5, ai/engine/README.md §6.0,
    docs/guide-getting-started.md §5.1, design-14e05e35 §4.2
    ('configuration tiers 1 and 3'), design-ael-orchestrator §7.0.
    requirements-1c1f4ef6 FR-AEL-008 still describes the retired
    config.json reading; FR-04-05 and FR-04-06 of requirements-14e05e35 do
    not fix an order.

resolution:
  approach: "Implemented by change-86c958dd (848b0d7, b97c950, 6b310b4, bf18451); follow-up audit pending."
  change_ref: "change-86c958dd"

traceability:
  design_refs: ["design-project-overwatch", "design-14e05e35", "design-ael-orchestrator"]
  change_refs: ["change-86c958dd"]

notes: "Audit references: audit-b8a6c445 F-01 to F-05, F-08; operator decisions 2026-11-05 for F-02 and F-03 and for the context-window order (CW). Predecessor: issue-b8a6c445 (closed)."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-b8a6c445 and the change-b8a6c445 live check"]
  - version: "1.1"
    date: "2026-11-06"
    changes: ["Iteration 2: context-window resolution order added as CW (Stage C work item 2); line numbers re-verified at 90fb563"]
  - version: "1.2"
    date: "2026-11-06"
    changes: ["Status resolved: change-86c958dd implemented (P03.7)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
