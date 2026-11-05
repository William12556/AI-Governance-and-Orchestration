Created: 2026 November 5

```yaml
issue_info:
  id: "issue-86c958dd"
  title: "Run record and status follow-up: recorded exit code, stale markers, FR-02-06 scope, path case, test gaps, 404 retry, manifest version"
  date: "2026-11-05"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-86c958dd"
    change_iteration: 1

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

affected_scope:
  components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py" }
    - { name: "overwatch", file_path: "ai/webui/src/overwatch.py" }
    - { name: "governance manifest", file_path: "ai/governance/software-engineering/manifest.yaml" }
    - { name: "engine tests", file_path: "tests/engine/test_run_record.py" }
    - { name: "overwatch tests", file_path: "tests/webui/test_overwatch.py" }
  designs:
    - { design_ref: "design-project-overwatch §4.0 (status precedence), §5.0 (FR-02-06)" }
    - { design_ref: "design-14e05e35 §11.0 (Error Handling)" }
  version: "governance 12.8; engine and webui at 505869e"

reproduction:
  prerequisites: "Engine and Overwatch at 505869e"
  steps:
    - "F-01: let _archive_audit_artifacts or _finish_run raise after rc = 0, or interrupt a run; compare run.json rc with the process exit status"
    - "F-02: end a run with SHIP, start a new run without reset that ends with rc 1 and writes no marker; scan"
    - "F-03: end a run, then open a prompt in ai/workspace/prompt/ (or open one for another executor); scan while no engine runs"
    - "F-04: on macOS, run the engine on an open prompt with --task spelled in a different letter case; scan"
    - "F-05: apply mutations A1 to A8 of audit-b8a6c445 §6.0; run tests/engine and tests/webui"
    - "F-08: make datetime.now() or os.path.abspath raise during the start record"
    - "P-01: run a loop with --reviewer-model set to a name oMLX cannot serve"
    - "P-02: start any run; read the 'governance model' line"
  frequency: "always, under the stated condition"
  error_output: "P-01 (dev/smoke, 2026-11-05): 'completion error (attempt 1/3) ... Error code: 404 ... Model 'no-such-model' not found', repeated at attempt 2/3, then 'BLOCKED: completion call failed after 3 attempts'. P-02: 'governance model: software-engineering 12.2'"

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
    current governance.md version.
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
    governance.md is at 12.8.
  impact: "Overwatch can show SHIP or BLOCKED for a later run that ended otherwise, and can raise FR-02-06 while no engine runs; the run record can disagree with the exit status; a missing model costs two needless retries; the run log names the wrong governance version."
  workaround: "Reset before each run; read the run log's last line ('engine end rc=N')."

environment:
  os: "macOS (Apple Silicon); F-01 to F-03, F-05, F-08, P-01 and P-02 are platform-independent"

analysis:
  root_cause: >
    Line numbers at 505869e (audit-b8a6c445 §8.4). F-01:
    orchestrator.py:2646 (rc default 1), :2675, :2713, :2754, :2762 (literal
    returns), :2876-2884 (finally). F-02: overwatch.py:530-535. F-03:
    overwatch.py:777. F-04: overwatch.py:780-782. F-05: tests/engine/
    test_run_record.py, tests/webui/test_overwatch.py (audit-b8a6c445 §6.0).
    F-08: orchestrator.py:2655-2662. P-01: _NON_RETRYABLE_STATUS =
    {400, 401, 403} (orchestrator.py:107); 404 is retried. P-02:
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
    issue.

resolution:
  approach: "To be defined in change-86c958dd."
  change_ref: "change-86c958dd"

traceability:
  design_refs: ["design-project-overwatch", "design-14e05e35"]
  change_refs: ["change-86c958dd"]

notes: "Audit references: audit-b8a6c445 F-01 to F-05, F-08; operator decisions 2026-11-05 for F-02 and F-03. Predecessor: issue-b8a6c445 (closed)."

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial issue from audit-b8a6c445 and the change-b8a6c445 live check"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

Copyright (c) 2026 William Watson. MIT License.
