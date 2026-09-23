Created: 2026 July 29

```yaml
issue_info:
  id: "issue-3b9e6d72"
  title: "Reviewer verdict is lost whenever the token is not the leading word; no SHIP is reachable"
  date: "2026-07-29"
  reporter: "William Watson"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-3b9e6d72"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "run a2d10058, both cycles"
  description: >
    _normalize_verdict reads only the leading whitespace-delimited token of the
    reviewer's message. A reviewer that states its reasoning before its
    conclusion — the ordinary form for a reasoning model — has its verdict read
    as the first word of its prose and silently downgraded to REVISE.

affected_scope:
  components:
    - name: "orchestrator (_normalize_verdict, fallback feedback persistence)"
      file_path: "ai/ael/src/orchestrator.py"
  designs: []
  version: "current"

reproduction:
  prerequisites: "A reviewer model that explains before concluding. Observed with Magistral-Small-2509-MLX-8bit."
  steps:
    - "Run orchestrator.py --mode loop with a reviewer that emits reasoning followed by a trailing SHIP"
    - "Observe the loop log: verdict from reviewer final message: 'The worker has implemented the ...' -> 'REVISE'"
    - "Observe the loop never terminates on SHIP regardless of the work's quality"
  frequency: "always"
  reproducibility_conditions: >
    Whenever the verdict token is not the first word. Observed in both cycles of
    run a2d10058, in which the reviewer reasoned correctly, cited both gates
    passing, and concluded SHIP as its final token.
  preconditions: ""
  test_data: "dev/smoke"
  error_output: "verdict from reviewer final message: 'The worker has implemented the ...' -> 'REVISE'"

behavior:
  expected: >
    A reviewer that concludes SHIP terminates the loop, whatever order it placed
    its reasoning and its conclusion in.
  actual: >
    The leading token 'The' does not match SHIP, so the verdict is REVISE. The
    fallback persistence then strips that leading token and writes the remaining
    790 characters — an argument that the code is correct — into
    review-feedback.txt as REVISE feedback. The next worker receives a REVISE
    whose body says to ship.
  impact: >
    A loop-termination defect. No run in the session that produced this backlog
    reached SHIP. Every end-to-end verification path is blocked behind it: the
    successful-SHIP path, the pytest-gate SHIP override, and stall detection at
    the threshold have never been exercised. It also confounds the earlier
    reviewer-calibration evidence, since apparent false REVISEs may have been
    parsing failures rather than judgement failures.
  workaround: >
    Instruct the reviewer to emit the verdict as its opening token. Fragile —
    run fc55ecf7 demonstrates that recipe instruction does not reliably control
    model output format.

environment:
  python_version: "3.11"
  os: "macOS 14+"
  dependencies:
    - library: "openai"
      version: "current"
  domain: "domain_2"

analysis:
  root_cause: >
    The leading-token rule was chosen to prevent a verdict word occurring inside
    prose from being mistaken for a declaration. It achieves that, but at the
    cost of rejecting the position in which a reasoning model naturally states
    its conclusion. The rule constrains where the verdict may appear without any
    mechanism to enforce that placement, so the model's habits and the parser's
    expectations diverge silently — and the failure direction is REVISE, which
    looks like ordinary loop progress rather than a defect.
  technical_notes: >
    An isolated-line test discriminates on a different axis from position: a
    line that is nothing but a verdict token, once decoration is stripped, is
    unambiguously a declaration, whereas 'I considered whether to SHIP this but
    the tests fail' is not. Preferring the last such line matches the
    conclusion-at-the-end form without admitting mid-prose mentions.

    The fallback feedback extraction shares the leading-token assumption and
    must be corrected with it, or a trailing-verdict REVISE would have its first
    word removed from an otherwise intact body.
  related_issues:
    - issue_ref: "issue-f5c28a04"
      relationship: "blocks — no live three-cycle verification of that change is possible until a SHIP is reachable"
    - issue_ref: "issue-c7e9a1b3"
      relationship: "related — worker tool-call efficiency, separately confounded by never reaching a terminal SHIP"

resolution:
  assigned_to: "Claude Desktop (Opus 5) — direct implementation"
  target_date: "2026-07-29"
  approach: >
    Option 2 of the three in the remediation backlog: match an isolated
    SHIP/REVISE on its own line, preferring the last. Retain the leading-token
    rule as a second pass for the single-line 'SHIP: ...' form.
  change_ref: "change-3b9e6d72"
  resolved_date: "2026-07-29"
  resolved_by: "Claude Desktop (Opus 5)"
  fix_description: >
    _is_verdict_line and _strip_verdict added; _normalize_verdict rewritten as
    two ordered passes; fallback feedback extraction switched to _strip_verdict.

verification:
  verified_date: "2026-07-29"
  verified_by: "Claude Desktop (Opus 5) — unit-level"
  test_results: >
    Fifteen cases exercised directly against the extracted helpers, all passing:
    bare and decorated tokens; leading-token single-line form; trailing verdict
    after multi-line reasoning, including the exact string from run a2d10058;
    a verdict word occurring mid-sentence correctly not treated as a
    declaration; a message stating REVISE then later SHIP resolving to SHIP;
    empty, whitespace-only and verdict-free input all defaulting to REVISE.
  closure_notes: >
    Not verified against a live model as of implementation. Independent
    verification on 2026-07-29 confirmed the parsing logic correct on
    twenty-two cases, including live exercise of pass 2 across four review
    phases; pass 1 (isolated trailing verdict) and a run reaching an actual
    SHIP remain unexercised. Closed at William Watson's explicit instruction on
    2026-07-29 (dev/audit review); see change-3b9e6d72
    operator_closure_2026_07_29 for the basis and the items still outstanding
    at closure.

prevention:
  preventive_measures: >
    Where the orchestrator parses model output, the accepted forms should be
    enumerated against observed output rather than assumed, and a parse that
    finds no verdict at all should be distinguishable in the log from a parse
    that found REVISE.
  process_improvements: >
    The defect was visible in the loop log of every run for an extended period —
    'verdict from reviewer final message' shows the input and the output on one
    line. Log review was directed at worker behaviour and did not cover it.

verification_enhanced:
  verification_steps:
    - "Run --mode loop against dev/smoke with a task the reviewer should accept"
    - "Confirm a trailing-verdict SHIP terminates the loop and writes .ralph-complete"
    - "Confirm a trailing-verdict REVISE writes feedback with the verdict line removed and the body intact"
    - "Confirm a reviewer message containing no verdict still defaults to REVISE"
  verification_results: "Unit-level only; live run pending."

traceability:
  design_refs: []
  change_refs:
    - "change-3b9e6d72"
  test_refs:
    - "dev/smoke"

notes: >
  Remediation backlog §2.1, identified there as the highest-impact item in the
  document and sequenced before the change-a2f9c4d1 closure work for that
  reason: fixing the manifest defects without this one yields another run that
  cannot ship and therefore cannot verify anything end to end.

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 0
  failure_mode: "divergence"
  last_review_feedback: "790-character argument that the code is correct, persisted as REVISE feedback"

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial issue from run a2d10058 log analysis"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Closed at operator instruction (dev/audit review); closure_notes updated to reflect the 2026-07-29 independent verification and the operator closure decision"
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
