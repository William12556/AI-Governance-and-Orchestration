Created: 2026 July 29

```yaml
issue_info:
  id: "issue-8c1a4f5e"
  title: "propagate.sh context.md seeding pass is unreachable in its own use case; exclude anchoring inconsistent"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-8c1a4f5e"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/audit/audit-p08-2026-07-29-orchestrator-changes.md (findings F4, F5, F6), reproduced live by the auditor"
  description: >
    change-e4b1a7c3 added a context.md seeding pass for new projects and, in the
    same edit, excluded context.md from the transfer. The exclusion makes the
    file invisible to the preview's change detection, so the early exit fires
    before the seeding pass in precisely the case the pass exists to serve.

affected_scope:
  components:
    - name: "propagate.sh (preview early exit, EXCLUDES array, seeding pass)"
      file_path: "bin/propagate.sh"
  designs: []
  version: "post change-e4b1a7c3"

reproduction:
  prerequisites: "A target project whose ai/ matches the framework in every respect except that ai/context.md is absent."
  steps:
    - "Run bin/propagate.sh <project-root>"
    - "Observe 'Target is up to date. No changes to apply.' and exit 0"
    - "Observe ai/context.md is still absent in the target"
  frequency: "always"
  reproducibility_conditions: "Whenever context.md is the only difference — the state a project reaches after any prior successful propagation that failed to seed it."
  preconditions: ""
  test_data: "A scratch target constructed by rsyncing ai/ with context.md excluded"
  error_output: ""

behavior:
  expected: >
    A target lacking ai/context.md receives the template, whether or not any
    other framework file differs.
  actual: >
    CHANGES is computed with EXCLUDES, which now contains /context.md. A target
    differing only by a missing context.md therefore reports no changes and
    exits before reaching the seeding pass.
  impact: >
    New projects silently fail to receive the context.md template once their
    framework files are otherwise current. Downstream, ai/context.md is the
    AEL profile's tactical context file, so its absence or emptiness degrades
    every subsequent run there.
  workaround: "Copy ai/context.md into the target manually."

environment:
  python_version: ""
  os: "macOS 14+"
  dependencies:
    - library: "rsync"
      version: "system"
  domain: "provisioning"

analysis:
  root_cause: >
    The seeding pass and the exclusion that necessitates it were added in the
    same change, and the interaction between the exclusion and the preview's
    early exit was not considered. The exclusion is correct — it protects a
    filled-in downstream copy — but it also removes the file from the only
    signal the script uses to decide whether there is work to do.
  technical_notes: >
    Two adjacent minor findings from the same audit are folded in here. F5: the
    seeding rsync carries --ignore-existing inside a branch already guarded by
    a file-absence test, so the flag can never affect the outcome. F6: three
    excludes — config.yaml, workspace/ and dashboard-alerts.md — are unanchored
    while /state/ and /context.md are anchored, so the first three match at any
    depth beneath ai/ and would exclude same-named files the framework does
    intend to propagate. Neither has been observed to cause loss; both are
    latent.
  related_issues:
    - issue_ref: "issue-e4b1a7c3"
      relationship: "related — introduced the exclusion and the seeding pass whose interaction is defective here"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: >
    Evaluate the seed condition before the early exit and admit it as work to be
    done; drop the redundant flag; anchor the three path-specific excludes.
  change_ref: "change-8c1a4f5e"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5)"
  fix_description: >
    NEEDS_SEED computed before CHANGES; early exit conditioned on both; preview
    reports the pending seed; seeding branch keyed on NEEDS_SEED without
    --ignore-existing; config.yaml, workspace/ and dashboard-alerts.md anchored.

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude (Cowork remediation session, Opus 5) — independent of the implementing session"
  test_results: >
    Re-derived independently rather than accepted from the implementing
    session's record. bash -n clean and set -euo pipefail present, both
    re-checked. Executed against a synthetic source tree carrying every exclude
    category and five scratch targets: (a) current except context.md absent,
    with timestamps preserved so CHANGES is genuinely empty — the exact F4
    precondition — reports "(no framework files differ)" plus the pending seed
    and writes a byte-identical context.md on confirmation; (a-regression) the
    same case against a reconstructed e4b1a7c3-only script reports "Target is up
    to date. No changes to apply." and never seeds, so the defect and its
    correction are both demonstrated on the same input; (b) fully current —
    up to date, exit 0; (c) empty target — full file list plus seed line, both
    applied; (d) re-run after seeding — up to date; (e) declining at the prompt
    — "Aborted.", neither transfer nor seed occurs.

    The anchoring gap recorded at implementation is now closed. The synthetic
    source contained ai/doc/config.yaml and ai/doc/workspace/note.md alongside
    ai/ael/config.yaml and ai/workspace/gov.md. Case (c) transferred the two
    nested files and excluded the two anchored ones, which is the behavioural
    difference anchoring was introduced to produce and which no earlier test
    target could show. ai/state/ and ai/dashboard-alerts.md were excluded in the
    same run.
  closure_notes: >
    Closed. Every success criterion in change-8c1a4f5e is satisfied by evidence
    gathered in an independent session, including the one criterion its own
    verification block recorded as inspection-only. No findings were raised
    against this change during that verification.

prevention:
  preventive_measures: >
    When a file is excluded from a transfer and handled by a separate pass, the
    condition governing that pass must be evaluated independently of the
    transfer's own change detection.
  process_improvements: >
    change-e4b1a7c3 was verified against a target that differed in many files,
    where the early exit never fired. A single-difference target would have
    exposed this immediately.

verification_enhanced:
  verification_steps:
    - "Construct a target current in all respects except a missing ai/context.md"
    - "Confirm the preview reports a pending seed rather than 'up to date'"
    - "Confirm the seed writes a file identical to ai/context.md"
    - "Confirm a fully current target still reports up to date"
    - "Confirm a re-run after seeding reports up to date"
  verification_results: "All five confirmed 2026-07-29."

traceability:
  design_refs: []
  change_refs:
    - "change-8c1a4f5e"
  test_refs:
    - "Scratch targets under /tmp, constructed and discarded during verification"

notes: >
  Remediation backlog §1.4 (F4), §4.3 (F5) and §4.4 (F6). F5 and F6 are
  cosmetic and latent respectively; they are folded in here because they touch
  the same twenty lines and would otherwise require a second pass over the same
  file.

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
      - "Initial issue consolidating P08 audit findings F4, F5 and F6"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Independently verified live in the Cowork remediation session, including the F4 precondition against a reconstructed pre-change script and the anchoring case the implementing session could not demonstrate; no findings; issue closed"
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
