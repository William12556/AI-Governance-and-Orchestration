Created: 2026 July 29

```yaml
issue_info:
  id: "issue-f5c28a04"
  title: "work-summary.txt is never cleared per cycle; exhaustion exit trusts file existence; move/rename deliverables recorded at the source path"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-f5c28a04"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/audit/audit-p08-2026-07-29-orchestrator-changes.md (findings F1, F2, F3); run a2d10058"
  description: >
    Three coupled defects in the work-summary manifest lifetime introduced by
    change-a2f9c4d1, identified by the P08 strategic audit and confirmed against
    a live run. Consolidated for remediation with two adjacent low-severity items
    from the same backlog: reset returning failure for an absent state directory,
    and run logs not surviving between sessions.

affected_scope:
  components:
    - name: "orchestrator (run_phase exhaustion exit, write-target recording, run_loop per-cycle state)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "orchestrator (reset_state)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "AEL canonical configuration"
      file_path: "ai/ael/config.yaml"
  designs: []
  version: "post change-a2f9c4d1"

reproduction:
  prerequisites: "A Ralph Loop run of two or more cycles in which the worker writes deliverables in cycle 1 and nothing in cycle 2."
  steps:
    - "Run orchestrator.py --mode loop against dev/smoke"
    - "Observe cycle 1: worker writes deliverables; work-summary.txt is produced"
    - "Observe cycle 2: worker issues no write calls and exhausts its iteration budget"
    - "Observe the phase returns rc=0 and the gates adjudicate cycle 1's deliverables a second time"
  frequency: "always"
  reproducibility_conditions: "Any run of two or more cycles. Confirmed in run a2d10058, which contains exactly one write call, in cycle 1."
  preconditions: ""
  test_data: "dev/smoke"
  error_output: ""

behavior:
  expected: >
    Each cycle is adjudicated on its own output. A worker phase that produced
    nothing returns rc=1 regardless of what earlier cycles produced. A
    deliverable created by move_file or rename_file appears in the manifest at
    the path where it now exists.
  actual: >
    work-summary.txt is cleared once, at loop start. The exhaustion exit tests
    os.path.exists, which cannot distinguish a manifest produced this cycle from
    one left by a prior cycle, so an unproductive cycle returns rc=0. The
    wall-clock and work-complete exits decline to overwrite the stale manifest
    for the same reason. Deliverables moved or renamed are recorded at their
    pre-move path, fail the isfile filter at synthesis, and are dropped.
  impact: >
    The read-evidence, syntax and pytest gates re-adjudicate a previous cycle's
    deliverables as though they were this cycle's, which is the same vacuous-pass
    condition change-a2f9c4d1 set out to close. Blocks closure of
    change-a2f9c4d1 and therefore downstream propagation.
  workaround: "None. Inspect work-summary.txt manually against the run log's write calls."

environment:
  python_version: "3.11"
  os: "macOS 14+"
  dependencies:
    - library: "openai"
      version: "current"
  domain: "domain_2"

analysis:
  root_cause: >
    F1/F2: change-a2f9c4d1 attached synthesis to phase exit but left the
    manifest's lifetime at run scope. Synthesis is deliberately conservative and
    never overwrites an existing summary, so a manifest that outlives its cycle
    suppresses the very mechanism intended to replace it. The exhaustion exit
    then derives its return code from that same file's presence.

    F3: the expression `path or file_path or destination` was copied from
    _validate_write_scope, where the source path is the correct subject for
    scope enforcement. For manifest construction the destination is what
    matters — the two helpers share an argument shape but not an intent.

    2.3: reset_state treated an absent state directory as an error rather than
    as the requested end state already obtaining.

    3.1: run logs are written only into state_dir, which is transient by design.
    The .gitignore '*.log' pattern additionally matches 'ael_*.LOG' on a
    case-insensitive filesystem, so version control does not recover them.
  technical_notes: >
    The per-cycle clear belongs before the work phase, not before the review
    phase as the remediation backlog suggested. review-feedback.txt is cleared
    before the review phase because the worker has already consumed it;
    work-summary.txt is the reviewer's and the gates' input, so clearing it at
    that point would remove what they exist to check.

    Conditioning the exhaustion return code on a boolean tracked during the
    phase, rather than re-testing the file, keeps the fix correct independently
    of the clearing change. Either alone would close the defect; together they
    are robust to a future caller that clears differently.
  related_issues:
    - issue_ref: "issue-a2f9c4d1"
      relationship: "related — this issue completes the manifest lifecycle that change introduced"
    - issue_ref: "issue-e4b1a7c3"
      relationship: "related — a propagated stale ai/state/ was one route by which a manifest outlived its cycle"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: >
    Clear work-summary.txt at the top of each loop cycle; track manifest
    production within the phase and use that, not file existence, for the
    exhaustion return code; prefer the destination argument for move/rename when
    recording write targets; return 0 from reset_state when the state directory
    is absent; add an opt-in log_archive_dir that copies prior run logs out of
    state_dir before each run.
  change_ref: "change-f5c28a04"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5)"
  fix_description: >
    Five edits to ai/ael/src/orchestrator.py and two to ai/ael/config.yaml. See
    change-f5c28a04 technical_details.

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude Desktop (Opus 5) — static verification only"
  test_results: >
    ai/ael/src/orchestrator.py parses without error. archive_prior_logs
    exercised directly against a scratch directory: no-op when unconfigured,
    copies .LOG and .log, idempotent on re-run, ignores non-log files, safe when
    state_dir is absent.
  closure_notes: >
    Not verified end-to-end as of implementation. Independent verification on
    2026-07-29 confirmed the per-cycle clear and corrected exhaustion return
    code live, twice (see change-f5c28a04 independent_verification_2026_07_29).
    Three of seven test cases remain unexercised. Closed at William Watson's
    explicit instruction on 2026-07-29 (dev/audit review); see
    change-f5c28a04 operator_closure_2026_07_29 for the basis and the items
    still outstanding at closure.

prevention:
  preventive_measures: >
    When a helper's argument-extraction expression is copied between functions,
    confirm the two share an intent and not merely an argument shape. When a
    state file's producer and consumer sit in different phases, its lifetime
    should be stated explicitly rather than inherited from the run.
  process_improvements: >
    change-a2f9c4d1 was accepted on inline source review without an end-to-end
    run. The defects it left were all visible in a two-cycle execution.

verification_enhanced:
  verification_steps:
    - "Run --mode loop against dev/smoke for at least three cycles"
    - "Confirm work-summary.txt content differs per cycle and never carries forward"
    - "Confirm a cycle in which the worker writes nothing returns rc=1"
    - "Confirm a deliverable produced via move_file appears in the manifest at its destination"
    - "Confirm ai/logs/ accumulates run logs across successive runs"
  verification_results: "Pending — requires live execution."

traceability:
  design_refs: []
  change_refs:
    - "change-f5c28a04"
  test_refs:
    - "dev/smoke"

notes: >
  Consolidates remediation backlog items §1.1 (F1), §1.2 (F2), §1.3 (F3), §2.3
  (reset idempotency), §3.1 (log preservation) and §4.2 (stale reviewer model in
  canonical config). §1.5, the correction of change-a2f9c4d1's overstated
  claims, is delivered by the same change.

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial issue consolidating P08 audit findings F1/F2/F3 with adjacent backlog items 2.3, 3.1 and 4.2"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Closed at operator instruction (dev/audit review); closure_notes updated to reflect the 2026-07-29 independent live verification and the operator closure decision"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
