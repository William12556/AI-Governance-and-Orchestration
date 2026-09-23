Created: 2026 July 29

```yaml
change_info:
  id: "change-a2f9c4d1"
  title: "Work-summary synthesis at all non-blocked worker exits; productive iteration exhaustion reclassified as non-fatal"
  date: "2026-07-29"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a2f9c4d1"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-a2f9c4d1"
  description: >
    Attach work-summary.txt persistence to worker-phase termination rather than
    to a single exit path, and stop treating a productive worker phase that
    exhausted its tool-call budget as a fatal error.

scope:
  summary: >
    Two coupled edits to orchestrator.py. (1) Track successful write-tool
    targets during a phase and, at the wall-clock, work-complete and
    iteration-exhaustion exits, synthesise work-summary.txt from those
    observations when the worker did not write one. (2) At the iteration
    exhaustion exit, return 0 instead of 1 when the phase produced
    deliverables, so run_loop proceeds to the review phase and the reviewer
    adjudicates the work.
  affected_components:
    - name: "orchestrator (_synthesize_work_summary new function, run_phase)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "The BLOCKED exit (unparsed tool markers) — deliberately excluded; a malformed phase must not present a manifest"
    - "ralph-work.yaml wording — the recipe already specifies the obligation three times over; the defect is non-compliance, not under-specification"
    - "Worker tool-call efficiency (one call per iteration, no batching despite TOOL DISCIPLINE guidance) — separate pre-existing concern, see issue-c7e9a1b3"
    - "Granting the worker an execution tool so it can run tests itself — rejected on containment grounds by change-5bdc2d9b; unchanged here"
    - "bin/propagate.sh exclude-list defects and the stale deployed ael-mcp build — logged in issue-a2f9c4d1 notes, separate triples required"

rational:
  problem_statement: >
    work-summary.txt is the sole input to _extract_deliverables, which in turn
    feeds the read-evidence, syntax and pytest gates. Three of run_phase's four
    exits never write it, so those gates pass vacuously whenever a phase
    terminates by wall-clock cap or work-complete detection. On iteration
    exhaustion the run aborts outright, discarding correct work.
  proposed_solution: >
    Follow the established precedent (read-evidence gate, pytest gate): handle
    it deterministically in the orchestrator rather than instructing the model
    harder. Record write-tool targets as they succeed, and reconstruct a
    manifest at phase exit when the worker did not supply one. Reclassify
    exhaustion-with-deliverables as a budget boundary rather than a failure,
    consistent with the architecture's premise that the reviewer is the
    arbiter of completeness.
  alternatives_considered:
    - option: "Strengthen ralph-work.yaml wording around PROCEDURE step 6"
      reason_rejected: >
        Run fc55ecf7 issued an explicit REVISE naming the missing file; the
        worker then ran a further twelve iterations without writing it. The
        recipe already states the obligation in PROCEDURE, in a dedicated WORK
        SUMMARY section, and by implication in CONSTRAINTS. More instruction is
        not the remedy.
    - option: "Inject a budget warning near exhaustion telling the worker to write the summary now"
      reason_rejected: >
        Still model-discretionary, and consumes an iteration to deliver. Does
        not address the wall-clock or work-complete exits at all.
    - option: "Raise phase_max_iterations as the operational fix"
      reason_rejected: >
        Treats a symptom. Run fc55ecf7 had twelve spare iterations. Also
        increases the cost of genuinely stuck phases.
    - option: "Return 0 on iteration exhaustion unconditionally"
      reason_rejected: >
        A phase that produced nothing would then reach review with an empty
        manifest every cycle, consuming the full outer max_iterations budget
        for no work. Gating on observed deliverables preserves fail-fast for
        unproductive phases.
  benefits:
    # Correction (2026-07-29, change-f5c28a04): the original wording here read
    # "Closes a silent gate-bypass affecting three of four worker exits". The
    # code as implemented did not support that claim. Synthesis declines to
    # overwrite an existing work-summary.txt, and the file was cleared only once
    # per run rather than once per cycle, so from cycle 2 onward a manifest left
    # by the previous cycle suppressed synthesis and was re-presented to the
    # gates. The bypass was narrowed, not closed. Closing it required the
    # per-cycle clear added by change-f5c28a04.
    - "Narrows a silent gate-bypass at three of four worker exits, for the first cycle of a run; fully closed by change-f5c28a04's per-cycle manifest clear"
    - "Deterministic — independent of worker recipe compliance"
    - "Restores the reviewer as arbiter of completeness on budget exhaustion"
    - "No new model-controlled capability or attack surface"
  risks:
    - risk: "Synthesised manifest is mistaken for the worker's own account"
      mitigation: "Body is explicitly headed ORCHESTRATOR-GENERATED SUMMARY and states it records what was written, not why"
    - risk: "Synthesis masks a genuinely failed phase"
      # Correction (2026-07-29, change-f5c28a04): the original mitigation ended
      # "rc remains 1 when no deliverables were produced". As implemented, the
      # exhaustion exit tested os.path.exists(work-summary.txt), which is
      # satisfied by a manifest from any prior cycle. A worker that produced
      # nothing in cycle 2+ therefore returned rc=0. Verified in run a2d10058,
      # which contains exactly one write call, in cycle 1. change-f5c28a04
      # replaces the existence test with this phase's own synthesis outcome.
      mitigation: "Writes nothing when no successful non-state writes were observed; never overwrites an existing summary. The intended 'rc remains 1 when no deliverables were produced' guarantee did not hold as implemented and is delivered by change-f5c28a04"
    - risk: "A worker producing useless output each cycle now consumes all outer max_iterations rather than aborting after one"
      mitigation: "Bounded by max_iterations; F12 stall detection covers repeated identical REVISE feedback. Accepted."
    - risk: "Write-target tracking records paths from calls that appeared to succeed but did not"
      mitigation: "Recorded only when the call produced no scope error, no audit-report error, and no MCP error; additionally filtered by os.path.isfile at synthesis time"

technical_details:
  current_behavior: >
    run_phase writes work-summary.txt only on the final-response exit (F13,
    line ~1069). The wall-clock cap exit (~952), work-complete exit (~1267)
    and iteration exhaustion exit (~1272) return without writing it.
    Exhaustion returns rc=1; run_loop aborts on any non-zero work-phase rc
    (~1765).
  proposed_behavior: >
    A phase-scoped _written_paths set records successful write-tool targets.
    At each of the three non-blocked exits, if the phase is a worker phase and
    work-summary.txt is absent, _synthesize_work_summary reconstructs it from
    _written_paths, excluding state-directory paths and non-files. The
    exhaustion exit returns 0 when synthesis found deliverables (or a summary
    already existed), else 1.
  implementation_approach: >
    1. Add _synthesize_work_summary(state_dir, written_paths, reason, log) ->
    bool near the write-scope helpers. Returns False without writing if
    work-summary.txt exists, if written_paths is empty, or if no path survives
    the state-dir and isfile filters.
    2. Initialise _written_paths: set[str] alongside _read_counts in run_phase.
    3. In the tool dispatch loop, after the P3 duplicate-read tracking block,
    record os.path.abspath of the target of any _WRITE_TOOLS call that
    produced no _scope_err, no _report_err and no MCP error.
    4. Call the helper at the wall-clock, work-complete and exhaustion exits,
    guarded by is_worker_phase.
    5. At the exhaustion exit, compute rc from whether a manifest is present
    after synthesis.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        New _synthesize_work_summary helper; _written_paths tracking in
        run_phase; synthesis calls at three exits; exhaustion return code
        conditioned on deliverable presence.
      functions_affected:
        - "_synthesize_work_summary (new)"
        - "run_phase"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "_WRITE_TOOLS"
      impact: "Reused as-is for write-call identification; no change"
    - component: "write_state"
      impact: "Reused as-is"
    - component: "_extract_deliverables"
      impact: "Unchanged; becomes reliably non-empty on the affected exits"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Live Ralph Loop execution against dev/smoke, which reproduced both defects
    deterministically across two runs. Inline source review in addition.
  test_cases:
    - scenario: "Worker writes deliverables then exhausts the iteration budget"
      expected_result: "work-summary.txt synthesised listing the deliverables; phase returns 0; review phase runs"
    - scenario: "Worker writes nothing and exhausts the iteration budget"
      expected_result: "No summary written; phase returns 1; run aborts as before"
    - scenario: "Worker writes work-summary.txt itself, then exhausts the budget"
      expected_result: "Existing summary preserved verbatim; phase returns 0"
    - scenario: "Worker reaches a normal final response"
      expected_result: "F13 path unchanged; summary is the worker's own final message"
    - scenario: "Worker writes only state signal files"
      expected_result: "No summary synthesised; treated as no deliverables"
    - scenario: "Phase exits on the BLOCKED path"
      expected_result: "No synthesis; rc=1 unchanged"
    - scenario: "Review phase"
      expected_result: "Unaffected — synthesis guarded by is_worker_phase"
  regression_scope:
    - "F13 final-response summary write unchanged"
    - "Read-evidence, syntax, pytest and audit gates unchanged (they now receive a populated deliverable set where previously empty)"
    - "Review-phase behaviour unchanged"
  validation_criteria:
    - "No change to review-phase behaviour"
    - "No change to the BLOCKED path"
    - "ai/ael/src/orchestrator.py has no syntax errors"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via Filesystem MCP (no Claude Code, no AEL) per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert ai/ael/src/orchestrator.py to prior version"
  deployment_notes: >
    Downstream propagation via bin/propagate.sh once verified. Note the
    propagate exclude-list defects logged in issue-a2f9c4d1 notes are not
    addressed by this change and remain a propagation hazard.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-09-23"
  verified_by: "Claude (Cowork, Opus 5.5) — static verification only"
  test_results: >
    orchestrator.py compiles; all five implementation steps present in the
    form corrected by change-f5c28a04 and change-d1f4a83b. Test cases not
    exercised live in this verification.
  issues_found: []

operator_closure_2026_09_23:
  closed_by: "William Watson"
  basis: >
    Closed at William Watson's direction on 2026-09-23 to bring dev/ to a
    stable state. The P08 audit was performed (audit-p08-2026-07-29) and its
    findings were remediated by change-f5c28a04 and change-d1f4a83b, both
    closed at operator instruction on 2026-07-29. No live SHIP has been
    observed and the live test cases in testing_requirements remain
    unexercised; they are carried in dev/backlog.md. This is an operator
    closure decision, not a claim that every success criterion was
    independently re-derived.

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-d7f4a1c8"
      relationship: "precedent (deterministic orchestrator-side enforcement)"
    - change_ref: "change-5bdc2d9b"
      relationship: "precedent (deliverable-set consumer)"
    - change_ref: "change-f5c28a04"
      relationship: "corrective successor — completes the manifest lifecycle this change left partial (F1/F2/F3) and corrects this document's overstated claims"
  related_issues:
    - issue_ref: "issue-a2f9c4d1"
      relationship: "resolves"

notes: >
  Implemented directly by the Strategic Domain rather than delegated, at
  William Watson's instruction. P08 strategic audit by an independent session
  remains outstanding and is required before closure.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — approved for direct implementation (option 1: both parts)"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Corrected two claims the implemented code did not support, per P08 audit and dev/remediation-2026-07-29.md §1.5: the gate-bypass benefit (narrowed, not closed) and the rc=1 mitigation (did not hold across cycles). Both are delivered by change-f5c28a04."
      - "Added change-f5c28a04 to traceability.related_changes as the corrective successor"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed at operator direction after static verification; status approved -> verified (terminal status per protocol_checker; verification static only); verification and operator_closure_2026_09_23 recorded"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
