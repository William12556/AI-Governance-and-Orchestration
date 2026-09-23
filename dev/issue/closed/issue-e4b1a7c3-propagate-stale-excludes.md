Created: 2026 July 29

```yaml
issue_info:
  id: "issue-e4b1a7c3"
  title: "propagate.sh excludes a stale state path and does not protect project-specific ai/context.md"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e4b1a7c3"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "dev/smoke provisioning, 2026-07-29"
  description: >
    Two exclude-list defects in bin/propagate.sh, both observed directly while
    provisioning and re-provisioning the dev/smoke harness.

    (1) Stale state path. The exclude list carries --exclude='ael/state/',
    which was correct before the 2026-06-16 restructure. AEL runtime state now
    resides at ai/state/ (config loop.state_dir defaults to ai/state/ralph),
    which no pattern matches. Every propagation therefore copies the source
    repository's live Ralph state — task.md, work-summary.txt, iteration.txt,
    review-feedback.txt, RALPH-BLOCKED.md and logs — into the target project.

    (2) ai/context.md unprotected. context.md holds project conventions and
    technology stack and is project-specific by nature, in the same class as
    config.yaml. It is not excluded, so propagation overwrites any downstream
    project's filled-in copy with the framework's unfilled placeholder
    template.

affected_scope:
  components:
    - name: "propagate.sh (EXCLUDES array)"
      file_path: "bin/propagate.sh"
  designs: []
  version: "current"

reproduction:
  prerequisites: "LLM-G&O repository with a populated ai/state/ralph/, and a downstream project with a filled-in ai/context.md."
  steps:
    - "Run bin/propagate.sh <project-root>"
    - "Observe ai/state/ralph/ appears in the target containing the source repository's runtime state"
    - "Observe the target's ai/context.md is replaced by the placeholder template"
  frequency: "always"
  reproducibility_conditions: "Independent of target project. Observed twice against dev/smoke."
  preconditions: ""
  test_data: "dev/smoke"
  error_output: ""

behavior:
  expected: >
    Propagation carries framework source only. Runtime state is never
    transferred, and project-specific configuration files are never
    overwritten. A newly provisioned project still receives the context.md
    template so it has something to fill in.
  actual: >
    Source runtime state is copied into every target, and any filled-in
    downstream context.md is silently replaced by the template.
  impact: >
    A propagated ai/state/ralph/ can carry a stale work-summary.txt, which
    suppresses the change-a2f9c4d1 synthesis path, and a stale audit-index.md
    would silently switch recipe selection to the audit pair (orchestrator
    line ~2009). RALPH-BLOCKED.md and iteration.txt corrupt the next run's
    starting state. Loss of a downstream context.md is silent and only
    discoverable by reading the file.
  workaround: "Delete <project>/ai/state and restore context.md manually after every propagation."

environment:
  python_version: ""
  os: "macOS 14+"
  dependencies:
    - "rsync"
  domain: "provisioning"

analysis:
  root_cause: >
    (1) The exclude pattern was not updated when framework/ai/ and skel/ai/
    were consolidated to a single ai/ at repository root (2026-06-16), moving
    state from ai/ael/state/ to ai/state/.
    (2) context.md was added as a propagated artefact (ralph-work.yaml v1.3.0,
    PROCEDURE step 1) without being classified alongside config.yaml as
    project-specific.
  technical_notes: >
    Simply excluding context.md would regress new-project provisioning, since
    the target would never receive the template at all. A second rsync pass
    with --ignore-existing seeds it only when absent, giving new projects the
    template and leaving filled-in copies untouched. config.yaml is handled by
    plain exclusion with documented manual migration; aligning it to the same
    seeding pattern is deliberately out of scope.
  related_issues:
    - issue_ref: "issue-b6e4a1c9"
      relationship: "related — ai/ consolidation that moved the state path"
    - issue_ref: "issue-a2f9c4d1"
      relationship: "related — a propagated stale work-summary.txt suppresses its synthesis path"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: "Correct the state exclude to the post-restructure path; exclude context.md from the main pass and seed it with a second --ignore-existing pass"
  change_ref: "change-e4b1a7c3"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5), completed by change-8c1a4f5e"
  fix_description: >
    change-e4b1a7c3 replaced the dead 'ael/state/' exclude with an anchored
    '/state/', excluded '/context.md' from the main transfer so a downstream
    copy is never overwritten, and added a seeding pass for targets lacking the
    file. change-8c1a4f5e completed the fix by evaluating the seed condition
    before the preview's early exit, which is what made the seeding pass
    reachable in its own use case (audit finding F4).

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude (Cowork remediation session, Opus 5) — independent of the implementing session"
  test_results: >
    All three validation criteria re-derived live, against a synthetic source
    tree carrying a populated ai/state/ and every other exclude category.

    "No ai/state/ in target after propagation": the same source and target pair
    run against the pre-e4b1a7c3 script transferred state/leak.txt into the
    target; run against the current script it is excluded. Corroborated in the
    framework's own use — propagation to dev/smoke listed only
    ai/ael/src/orchestrator.py and created no ai/state in the target.

    "Filled-in target context.md survives propagation": a target whose
    context.md contained downstream content retained it byte-for-byte, and the
    script reported "context.md: existing project copy preserved."

    "Target without ai/context.md receives the template": satisfied, including
    the narrow case audit finding F4 identified as failing — see
    issue-8c1a4f5e, whose fix supplies it.

    bash -n clean; set -euo pipefail present; preview and confirmation flow
    unchanged, with declining at the prompt producing no transfer and no seed.
  closure_notes: >
    Closed. The partial criterion recorded by the P08 audit (F4) is resolved by
    change-8c1a4f5e, which is itself closed on independent live evidence. The
    style findings F5 and F6 were also carried by that change. No finding
    against change-e4b1a7c3 remains open.

prevention:
  preventive_measures: >
    Path-bearing constants in provisioning scripts should be reviewed whenever
    the repository layout changes. The 2026-06-16 restructure updated
    .gitignore and propagate.sh's source path but not its exclude list.
  process_improvements: ""

verification_enhanced:
  verification_steps: []
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-e4b1a7c3"
  test_refs:
    - "dev/smoke"

notes: >
  Downstream projects GTach, solax-modbus and e-Paper-IP-Display should be
  checked for a template-overwritten ai/context.md and a propagated
  ai/state/ before the next propagation.

  Update (2026-07-29, P08 audit audit-p08-20260729): change-e4b1a7c3 corrected
  the state exclude and protected context.md, both verified. It also
  introduced a defect the audit designated F4: the seeding pass's precondition
  was computed using the same EXCLUDES that hide context.md from the diff, so
  a target differing from source only by a missing context.md reported "up to
  date" and exited before the seeding pass ever ran — unreachable in the one
  case it existed to serve. Two low-severity style findings (F5, F6) were
  logged in the same review. All three are addressed by change-8c1a4f5e, which
  evaluates the seed condition before the preview's early exit and anchors the
  remaining path-specific excludes. This issue remains open pending
  independent audit of change-8c1a4f5e, which has self-verification only.

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
      - "Initial issue from dev/smoke provisioning"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "P08 audit audit-p08-20260729 verified the state-exclude and context.md-protection fixes but found the seeding pass unreachable in its own use case (F4), plus two style findings (F5, F6); corrective change-8c1a4f5e implemented; issue remains open pending independent audit of that change"
  - version: "1.2"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "change-8c1a4f5e independently verified live in the Cowork remediation session, closing F4; all three validation criteria of change-e4b1a7c3 re-derived live, including a pre-change/post-change comparison demonstrating the state leak the exclude correction prevents; issue closed"
  - version: "1.3"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
