```yaml
# T02 Change Document
# P03 Trivial Source Change Exemption

change_info:
  id: "change-d5a8e2f4"
  title: "P03 trivial source change exemption for Strategic Domain"
  date: "2026-03-18"
  author: "William Watson"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d5a8e2f4"
    issue_iteration: 1

source:
  type: "enhancement"
  reference: "Identified during solax-modbus project development, 2026-03-18"
  description: >
    P03 §1.4.1 requires all source code changes to route through Tactical Domain
    via T04 prompt and AEL execution. No exemption exists for trivial, surgical
    fixes. In practice, Strategic Domain implements small changes directly,
    creating an undocumented protocol bypass. This change formalises a narrow
    exemption to align protocol with observed practice.

scope:
  summary: >
    Add §1.4.12 Trivial Change Exemption to P03. Define criteria permitting
    Strategic Domain to implement trivial, surgical source code changes
    directly after human approval, without raising T03/T02 documents,
    creating a T04 prompt, or invoking AEL. Git history serves as the audit
    record. Scope is deliberately narrow to preserve the standard workflow
    for all substantive changes.
  affected_components:
    - name: "governance.md"
      file_path: "framework/ai/governance.md"
      change_type: "modify"
    - name: "skel/ai/governance.md"
      file_path: "skel/ai/governance.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Changes to T02, T03, T04 templates"
    - "Workflow flowchart modifications"
    - "Any other protocol sections"

rational:
  problem_statement: >
    P03 §1.4.1 requires T03, T02, T04, and AEL execution for all source
    code changes. No threshold exists below which this workflow may be
    bypassed. For trivial, surgical fixes this overhead is disproportionate
    and discourages protocol compliance for small work.
  proposed_solution: >
    A qualifying change must satisfy two definitions simultaneously:
    Trivial: the outcome is fully predictable before implementation; no
    analysis, experimentation, or design judgement is required to determine
    the correct solution. Surgical: confined to a single, well-bounded
    location in the codebase; does not disturb surrounding logic, interfaces,
    or dependent components. A change that is trivial but not surgical, or
    surgical but not trivial, does not qualify.

    Add §1.4.12 defining a Trivial Change Exemption: when a change satisfies
    both definitions AND all five criteria below, Strategic Domain may
    implement directly after human approval — no T03, T02, T04, or AEL
    required. Git commit history is the sole audit record for exempt changes.
    (1) confined to a single function or entry point;
    (2) net line delta ≤20 lines;
    (3) no interface changes (signatures, contracts, public APIs);
    (4) unambiguous with no design decisions required;
    (5) human approval obtained before implementation.
    All conditions must hold simultaneously. If any fails, standard
    T03 → T02 → T04 → AEL workflow applies.
  alternatives_considered:
    - option: "No exemption — enforce T04/AEL for all changes"
      reason_rejected: >
        Creates disproportionate overhead for trivial fixes. AEL execution
        for a 5-line argparse addition adds no quality benefit and discourages
        protocol compliance for small work.
    - option: "Line count threshold only (no other criteria)"
      reason_rejected: >
        Line count alone is insufficient. A small change can still introduce
        interface changes or require design decisions. All five criteria
        together define the true trivial boundary.
    - option: "Increase §1.4.11 scope to cover all src/ changes"
      reason_rejected: >
        §1.4.11 covers workspace/ documents only. Merging source and document
        exemptions would undermine the fundamental domain separation model.
  benefits:
    - "Eliminates compliance gap between observed practice and documented protocol"
    - "Reduces overhead for genuinely trivial surgical fixes"
    - "Preserves Tactical Domain authority for all substantive changes"
    - "Provides audit-defensible basis for direct Strategic Domain implementation"
  risks:
    - risk: "Criteria applied too loosely, allowing non-trivial changes to bypass AEL"
      mitigation: >
        All five criteria must hold simultaneously. The conjunction is
        deliberately strict. Human approval gate remains in place regardless.
    - risk: "Ambiguity in 'no interface changes' criterion"
      mitigation: >
        Criterion clarified as: no changes to function/method signatures,
        no changes to public API contracts, no changes to module-level
        constants used as external interfaces.

technical_details:
  current_behavior: >
    P03 §1.4.1 contains no exemption for trivial source changes. All
    source code modifications require T04 prompt creation and AEL execution.
    Strategic Domain implementing directly is an undocumented protocol bypass.
  proposed_behavior: >
    P03 §1.4.12 defines trivial and surgical change definitions plus five
    jointly-necessary criteria. When all are satisfied and human approval
    is obtained, Strategic Domain may implement directly — no T03, T02,
    T04, or AEL required. Git commit history is the sole audit record for
    exempt changes.
  implementation_approach: >
    Add §1.4.12 as a new numbered section immediately after §1.4.11 in
    governance.md (both framework/ and skel/ copies). Update version
    history. No other sections modified.
  code_changes:
    - component: "governance.md"
      file: "framework/ai/governance.md"
      change_summary: "Add §1.4.12 Trivial Change Exemption after §1.4.11"
      functions_affected: []
      classes_affected: []
    - component: "skel governance.md"
      file: "skel/ai/governance.md"
      change_summary: "Add §1.4.12 Trivial Change Exemption after §1.4.11"
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Human review of drafted §1.4.12 text against criteria completeness"
  test_cases:
    - scenario: "Trivial fix meets all five criteria"
      expected_result: "Strategic Domain may implement directly after human approval"
    - scenario: "Fix meets four of five criteria (e.g. touches two functions)"
      expected_result: "Standard T04/AEL workflow applies"
    - scenario: "Fix is small but changes a public function signature"
      expected_result: "Standard T04/AEL workflow applies — criterion 3 fails"
  regression_scope:
    - "§1.4.1 through §1.4.11 unchanged"
    - "T04/AEL workflow unchanged for all non-trivial changes"
  validation_criteria:
    - "§1.4.12 text present in both governance.md copies"
    - "§1.4.12 includes explicit definitions of trivial and surgical"
    - "All five criteria explicitly enumerated"
    - "§1.4.12 explicitly states T03 and T02 documents are not required for exempt changes"
    - "Human approval gate explicitly stated"
    - "Version history updated in both files"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Add §1.4.12 to framework/ai/governance.md"
      owner: "Strategic Domain"
    - step: "Add §1.4.12 to skel/ai/governance.md"
      owner: "Strategic Domain"
    - step: "Update version history in both files"
      owner: "Strategic Domain"
  rollback_procedure: "Restore from git history"
  deployment_notes: >
    Projects already using the framework should copy updated governance.md
    from framework/ to their project ai/ directory on next governance update.

verification:
  implemented_date: "2026-03-18"
  implemented_by: "William Watson"
  verification_date: "2026-03-18"
  verified_by: "William Watson"
  test_results: "Human review confirmed §1.4.12 present in both governance.md copies with trivial/surgical definitions, all five criteria, and explicit T03/T02/T04/AEL bypass statement."
  issues_found: []

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-d5a8e2f4"
      relationship: "source"

notes: >
  Origin: solax-modbus project, issue-c3f7a2e1 (emulator --port argument
  ignored). Strategic Domain implemented directly without T04/AEL, then
  identified the protocol gap and raised this change for the framework.

version_history:
  - version: "1.2"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Status set to implemented"
      - "Verification fields completed"
  - version: "1.1"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Expanded exemption to full workflow bypass (T03/T02/T04/AEL)"
      - "Added trivial and surgical change definitions"
      - "Reframed primary driver as overhead reduction"
      - "Git history as sole audit record for exempt changes"
  - version: "1.0"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised implemented -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
