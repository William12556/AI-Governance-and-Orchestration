Created: 2026 October 23

```yaml
change_info:
  id: "change-14cf601f"
  title: "Component layout: move Overwatch to ai/webui/, reserve ai/core/, retire ai/src/"
  date: "2026-10-23"
  author: "William Watson"
  status: "proposed"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-14cf601f"
    issue_iteration: 1

source:
  type: "issue"
  reference: "dev/issue/issue-14cf601f-webui-component-layout.md"
  description: "Organise framework source by component in preparation for a future central web UI."

scope:
  summary: >
    Mechanical move with no behaviour change. ai/src/ becomes ai/webui/src/;
    the Overwatch requirements file becomes the component's requirements.txt;
    tests/overwatch/ becomes tests/webui/. ai/core/ is reserved (README only)
    for code shared between components. All active references are updated.
  affected_components:
    - { name: "overwatch", file_path: "ai/src/overwatch.py → ai/webui/src/overwatch.py", change_type: "refactor" }
    - { name: "webui requirements", file_path: "ai/src/requirements-overwatch.txt → ai/webui/requirements.txt", change_type: "refactor" }
    - { name: "core placeholder", file_path: "ai/core/README.md", change_type: "add" }
    - { name: "webui tests", file_path: "tests/overwatch/ → tests/webui/", change_type: "refactor" }
    - { name: "engine-mcp test", file_path: "tests/engine/test_engine_mcp.py (overwatch import path)", change_type: "modify" }
    - { name: "scan script", file_path: "bin/migrate-terms.py (framework folder set)", change_type: "modify" }
    - { name: "documents", file_path: "CLAUDE.md, ai/governance/software-engineering/governance.md (P10.6, version 12.5), ai/governance/software-engineering/primer.md, docs/claude/primer.md, docs/guide-orchestration.md, dev/design/design-project-overwatch.md", change_type: "modify" }
  affected_designs:
    - design_ref: "dev/design/design-project-overwatch.md"
      sections: ["paths only"]
  out_of_scope:
    - "Any change to Overwatch behaviour, output, CLI or dependencies"
    - "Extraction of shared code into ai/core/ (only when shared code exists)"
    - "Web UI scope, deployment model, server process (not decided)"
    - "bin/propagate.sh and bin/migrate-layout.sh (no change needed; migrate-layout.sh comments are historical)"
    - "dev/tools/ migration scripts and mappings (historical)"
    - "Documents under closed/, dev/audit/ logs, Version History rows, requirements-0c6aedee (historical statement)"

rational:
  problem_statement: "A bare ai/src/ folder does not express component boundaries and gives a future central UI no defined home."
  proposed_solution: >
    Organise ai/ by component with a common shape (src/, optional doc/,
    requirements.txt, tests/<component>/). Dependency direction: webui may
    use engine and core; engine may use core; core uses nothing internal;
    nothing imports webui. governance/ and profiles/ remain data only.
  alternatives_considered:
    - option: "ai/engine/src/overwatch.py"
      reason_rejected: "Couples a read-only observer to the engine it observes; the future UI covers more than the engine"
    - option: "Component named ai/overwatch/"
      reason_rejected: "Names today's module rather than the component; a second rename would follow"
    - option: "Central installable package (src/aigo/)"
      reason_rejected: "Depends on deployment decisions outside this change's scope"
  benefits:
    - "Every source component has the same shape and its own dependency file"
    - "The future UI has a component; Overwatch becomes its first module"
    - "ai/ root no longer holds a bare src/"
  risks:
    - risk: "Missed path reference"
      mitigation: "Repository-wide residue search for ai/src and tests/overwatch outside the exclusions"
    - risk: "Downstream projects keep a stale ai/src/"
      mitigation: "bin/propagate.sh relocates it to ai-local/ as 'retired framework file'; verify on solax-modbus before other projects"

technical_details:
  current_behavior: "Overwatch at ai/src/overwatch.py; tests at tests/overwatch/."
  proposed_behavior: "Identical behaviour from ai/webui/src/overwatch.py; tests at tests/webui/."
  implementation_approach: "git mv for all moves, then path substitution in the files listed; ai/core/README.md added."
  interface_changes:
    - interface: "Overwatch invocation"
      change_type: "contract"
      details: "python ai/src/overwatch.py → python ai/webui/src/overwatch.py"
      backward_compatible: "no"
    - interface: "Overwatch dependency file"
      change_type: "contract"
      details: "ai/src/requirements-overwatch.txt → ai/webui/requirements.txt"
      backward_compatible: "no"

testing_requirements:
  test_approach: "Existing tests at new paths, static checks, residue search"
  test_cases:
    - { scenario: "python3 -m pytest tests/engine tests/webui -q", expected_result: "Same counts as the baseline run of tests/engine tests/overwatch" }
    - { scenario: "py_compile ai/webui/src/overwatch.py; bin/migrate-terms.py --scan on a fixture", expected_result: "Pass" }
    - { scenario: "One overwatch scan cycle from the repository root", expected_result: "overwatch.html and dashboard-alerts.md written; no traceback" }
    - { scenario: "linter.py dev and protocol_checker.py dev", expected_result: "No findings beyond baseline" }
    - { scenario: "Residue search for ai/src, tests/overwatch and requirements-overwatch", expected_result: "None outside the out_of_scope exclusions" }
    - { scenario: "diff of ai/governance/software-engineering/primer.md and docs/claude/primer.md", expected_result: "Identical" }
    - { scenario: "propagate.sh to solax-modbus (human)", expected_result: "ai/webui/ and ai/core/ installed; ai/src/ relocated to ai-local/ and logged" }
  validation_criteria:
    - "All test cases pass"
    - "Independent review accepted"

implementation:
  effort_estimate: "1–2 hours"
  implementation_steps:
    - { step: "1. Implement prompt-14cf601f", owner: "Claude Code (cloud session branch)" }
    - { step: "2. Planner review of session branch; operator fast-forward merge", owner: "Planner; human" }
    - { step: "3. Propagate to solax-modbus; then remaining downstream projects", owner: "Human" }
  rollback_procedure: "git revert of the implementation commits; downstream: restore ai/src/ from ai-local/."
  deployment_notes: "Governance 12.5 is a minor version; propagate.sh needs no --allow-major."

verification:
  implemented_date: null
  implemented_by: null
  verification_date: null
  verified_by: null
  test_results: null
  issues_found: []

traceability:
  design_updates:
    - design_ref: "dev/design/design-project-overwatch.md"
      sections_updated: ["paths"]
      update_date: null
  related_changes:
    - { change_ref: "change-5bcd46ad", relationship: "follows (layout migration)" }
  related_issues: ["issue-14cf601f"]

notes: >
  Abbreviated triple at the operator's instruction (2026-10-23), following the
  change-5bcd46ad precedent. ai/webui/ is the component for the future central
  UI, whose scope is not yet decided; Overwatch is its current module and keeps
  its name. ai/core/ was created by the planner on 2026-10-23 with a README
  only, at the operator's instruction.

version_history:
  - version: "0.1"
    date: "2026-10-23"
    author: "William Watson"
    changes: ["Initial change document"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```

Copyright (c) 2026 William Watson. MIT License.
