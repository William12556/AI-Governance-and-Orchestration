Created: 2026 July 02

```yaml
issue_info:
  id: "issue-713437bc"
  title: "T04/P09/govwatch hard-code AEL as sole Tactical Domain and change-document lineage as sole prompt origin"
  date: "2026-07-02"
  status: "closed"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-713437bc"
    change_iteration: 1

source:
  origin: "code_review"
  description: >
    Analysis of dev/reports/report-p09-t04-contradictions-2026-07-01.md,
    cross-referenced against ai/governance.md P03 §1.4.1 and P09 §1.10,
    ai/templates/T04-prompt.md (template and schema), ai/profiles/claude.md,
    and ai/src/govwatch.py. Confirms the report's nine findings (F1-F9,
    two root causes) and identifies two additional unconditional govwatch
    compliance checks that independently enforce the same two incorrect
    assumptions, outside the report's stated scope.

affected_scope:
  components:
    - name: "P09 Prompt protocol"
      file_path: "ai/governance.md"
    - name: "P03 Change protocol"
      file_path: "ai/governance.md"
    - name: "Strategic Domain Primer"
      file_path: "ai/primer.md"
    - name: "T04 Prompt template and schema"
      file_path: "ai/templates/T04-prompt.md"
    - name: "govwatch compliance engine"
      file_path: "ai/src/govwatch.py"

behavior:
  expected: >
    A T04 prompt document is valid under governance and govwatch regardless
    of which Tactical Domain profile executes it (AEL automated loop vs.
    Claude Code / claude-omlx manual single pass) and regardless of whether
    it derives from a design document (P03 §1.4.1 initial-implementation
    exception) or a change document (standard P03/P04 cycle).
  actual: >
    Root A: T04 schema requires tactical_brief (minLength 1) for every
    prompt. The field's sole consumer is the AEL orchestrator
    (extract_tactical_brief). Claude Code reads the full document and
    extracts nothing (profiles/claude.md §5.0, "implement <prompt-path>").
    govwatch FR-02-10 flags any prompt lacking tactical_brief as a
    VIOLATION unconditionally on cls == "prompt", with no profile check.
    Root B: T04 schema requires prompt_info.coupled_docs.change_ref
    (pattern ^change-[0-9a-f]{8}$) for every prompt. Governance P03 §1.4.1
    permits design-sourced initial-implementation prompts with no change
    document. govwatch FR-02-03 flags any prompt with no coupled change
    sharing UUID as a VIOLATION unconditionally, with no source-lineage
    check. T04's own source_ref field comment ("design-<uuid> or
    change-<uuid>") already anticipates the design-sourced case that
    coupled_docs then forbids (F4).
  impact: >
    A governance-compliant T04 prompt (manual profile, or design-sourced,
    or both) cannot satisfy the T04 schema, and is permanently flagged as
    a compliance violation by govwatch regardless of schema outcome. The
    author must violate a stated directive to proceed. Confirmed against a
    live Claude Code / design-sourced session in solax-modbus.

analysis:
  root_cause: >
    Root A: tactical_brief and the context-budget precondition (P09
    §1.10.2, primer §3.0/§7.0) assume AEL is the sole Tactical Domain
    consumer of T04 prompts. Written when AEL was the only implementation;
    never reconciled after the Claude Code / claude-omlx profiles were
    added. Root B: coupled_docs and the P09 prompt-creation clause assume
    every prompt derives from a change document. Never reconciled after
    the §1.4.1 initial-implementation exception was added (governance
    v9.8). No field in prompt_info declares target Tactical Domain profile
    or lets source_ref's existing design/change discrimination drive
    schema requirements.
  technical_notes: >
    Full finding detail in
    dev/reports/report-p09-t04-contradictions-2026-07-01.md (F1-F9).
    govwatch FR-02-03 and FR-02-10 (ai/src/govwatch.py,
    ComplianceEngine._tier2) verified independently as unconditional. The
    report scoped govwatch out, but both checks are load-bearing for a
    complete fix: a governance/T04-only fix leaves these two checks
    producing false violations on every manual-profile or design-sourced
    prompt.

resolution:
  approach: >
    Root A: add prompt_info.target_profile (enum: ael, claude_code,
    claude_omlx). T04 schema: tactical_brief required only when
    target_profile == ael (if/then). P09 §1.10.2 and primer §3.0/§7.0:
    scope tactical_brief and context-budget directives to target_profile
    == ael. govwatch FR-02-10: read target_profile, suppress when != ael.
    Resolves F1, F6.
    Root B: no new field — reuse existing source_ref prefix. T04 schema:
    coupled_docs required only when source_ref matches ^change- (if/then);
    omitted when source_ref matches ^design-. P09 §1.10.2 creation clause:
    "from design documents (initial implementation, §1.4.1) or from
    change documents (corrective/enhancement cycle)". govwatch FR-02-03:
    read source_ref, suppress the coupled-change check for design-sourced
    prompts (requires adding source_ref extraction to parse_document,
    currently absent). Resolves F2, F3, F4.
    Hygiene (F5, F7, F8, F9): reword the tactical_brief field comment
    (F5); remove output_format / deliverable.documentation from the T04
    schema or restore to the template body, whichever matches intent
    (F7); update or remove stale embedded version labels (F8); fold F9
    into the Root A fix — tactical_brief size guidance scoped to
    target_profile == ael, single source of truth (budget.py computed
    figure) rather than two static numbers.
  change_ref: "change-713437bc"

traceability:
  design_refs: []
  change_refs:
    - "change-713437bc"

notes: >
  Both roots and the govwatch extension bundled in one issue per human
  direction — overlapping prompt_info schema region, overlapping
  govwatch.py file. Change document to follow, coupling all four affected
  files (governance.md, primer.md, T04-prompt.md, govwatch.py) under one
  change_ref.

verification:
  verified_date: "2026-07-08"
  test_results: >
    Verified against source. Stream A (govwatch.py): DocumentRecord carries
    target_profile and is_design_sourced; parse_document populates both;
    FR-02-03 (_tier1) guarded on is_design_sourced; FR-02-10 (_tier2)
    guarded on target_profile. Stream B: T04-prompt.md v1.10 adds
    prompt_info.target_profile and both if/then schema blocks; governance.md
    v9.10 rewords P09 §1.10.2 and P03 §1.4.1 cross-reference.
  closure_notes: "Both streams confirmed implemented against source; issue closed."

version_history:
  - version: "1.0"
    date: "2026-07-02"
    changes:
      - "Initial issue document; bundles Root A and Root B from report-p09-t04-contradictions-2026-07-01.md plus independently verified govwatch FR-02-03/FR-02-10 unconditional violations"
  - version: "1.1"
    date: "2026-07-08"
    changes:
      - "Verified against source; issue closed"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised verified -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
