Created: 2026 September 25

```yaml
change_info:
  id: "change-5bcd46ad"
  title: "Layout and terminology migration: ai/engine/, ai/governance/<name>/, ai/config.yaml; retire AEL, Ralph Loop and govwatch"
  date: "2026-09-25"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (proposal-5bcd46ad D-14); no issue document
    issue_iteration: null

source:
  type: "human_request"
  reference: "dev/proposals/proposal-5bcd46ad-ai-go-pivot.md"
  description: "Phase 1 of the AI-G&O strategic pivot: move files to the target layout and replace retired terms, without behaviour change."

scope:
  summary: >
    Move ai/ael/ to ai/engine/ and the SE governance files to
    ai/governance/software-engineering/; move project configuration to
    ai/config.yaml; flatten ai/state/ralph/ to ai/state/; replace the terms AEL
    and Ralph Loop; retire govwatch; adapt ael-mcp as engine-mcp inside this
    repository; add a one-time downstream migration script; fold in
    change-c37198be.
  affected_components:
    - name: "engine"
      file_path: "ai/ael/ → ai/engine/"
      change_type: "refactor"
    - name: "SE governance model"
      file_path: "ai/governance.md, ai/workflow.md, ai/primer.md, ai/templates/, ai/skills/, ai/doc/guide-audit-loop.md → ai/governance/software-engineering/"
      change_type: "refactor"
    - name: "seed files"
      file_path: "ai/context.md, ai/task.md → ai/governance/software-engineering/seed/; ai/ael/config.yaml → ai/engine/config.template.yaml"
      change_type: "refactor"
    - name: "engine operations guide"
      file_path: "ai/doc/guide-ael-operations.md → ai/engine/doc/guide-engine-operations.md"
      change_type: "refactor"
    - name: "govwatch"
      file_path: "ai/src/govwatch.py, ai/src/requirements-govwatch.txt, ai/doc/guide-govwatch.md, dev/design/design-govwatch.md"
      change_type: "delete"
    - name: "overwatch"
      file_path: "ai/src/overwatch.py, tests/overwatch/"
      change_type: "modify"
    - name: "engine-mcp"
      file_path: "~/Documents/GitHub/ael-mcp/server.py → ai/engine/mcp/server.py"
      change_type: "add"
    - name: "engine tests"
      file_path: "tests/ael/ → tests/engine/"
      change_type: "refactor"
    - name: "scripts"
      file_path: "bin/bootstrap.sh, bin/propagate.sh, bin/release.sh, .gitignore"
      change_type: "modify"
    - name: "downstream migration script"
      file_path: "bin/migrate-layout.sh"
      change_type: "add"
    - name: "documents"
      file_path: "README.md, CLAUDE.md, docs/, docs/claude/primer.md, ai/profiles/, ai/engine/README.md, active dev/ documents, dev/smoke/"
      change_type: "modify"
  affected_designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
      sections:
        - "paths and terms only"
    - design_ref: "dev/design/design-project-overwatch.md"
      sections:
        - "paths and terms only"
  out_of_scope:
    - "Any change to loop, gate, verdict or propagation behaviour"
    - "manifest.yaml, model-driven workspace folders, stage flow (Phase 2)"
    - "Moving the audit recipes into the SE package (Phase 2; needs recipe lookup change)"
    - "Strategic Domain / Tactical Domain terms (proposal OQ-02)"
    - "Claude Code profiles (proposal OQ-01)"
    - "Documents under closed/, dev/audit/ logs, historical Version History rows"
    - "External ael-mcp repository (operator archives it)"

rational:
  problem_statement: >
    The layout and terms tie the framework to software engineering and to a
    single engine name. The pivot (proposal-5bcd46ad) requires a layout in
    which governance models are loadable packages and the engine is generic.
  proposed_solution: >
    A mechanical migration driven by a path and term mapping, applied with
    git mv and scripted replacement, verified by tests, static checks, a
    smoke run and a residue search. Downstream projects migrate once through
    bin/migrate-layout.sh, then receive the new layout through propagate.sh.
  alternatives_considered:
    - option: "Copy the SE model to today's ai/ paths (no ai/governance/<name>/)"
      reason_rejected: "Operator decision: the subfolder is needed eventually; migrate once"
    - option: "Keep the ael/ folder name"
      reason_rejected: "Operator decision: engine is clearer for new users"
    - option: "Build engine-mcp anew now"
      reason_rejected: "Its interface changes in Phase 2; adapt now, rebuild then"
    - option: "Add layout migration logic to propagate.sh"
      reason_rejected: "One-time logic would stay in a permanent script; a separate script is removable"
  benefits:
    - "Governance models and engine are separated by folder"
    - "Propagation replaces framework-owned folders wholesale; project configuration is no longer inside a framework folder"
    - "One monitoring tool instead of two"
    - "engine-mcp is versioned with the engine; no stale separate install"
  risks:
    - risk: "Recipe prompt wording changes (RALPH LOOP → LOOP) alter model behaviour"
      mitigation: "Smoke run to SHIP in dev/smoke before closure"
    - risk: "Downstream migration damages a project"
      mitigation: "Script uses git mv, refuses a dirty working tree, never deletes; dry run on a copy first"
    - risk: "Missed path or term reference"
      mitigation: "Repository-wide residue search against the mapping"
    - risk: "Closed documents keep target_profile: ael"
      mitigation: "Readers accept ael as a legacy alias for engine"

technical_details:
  current_behavior: "Engine at ai/ael/; SE governance files at ai/ root; configuration at ai/ael/config.yaml; state at ai/state/ralph/."
  proposed_behavior: "Identical behaviour at the paths and with the names in the mapping below."
  implementation_approach: >
    Path mapping:
    ai/ael/ → ai/engine/;
    ai/ael/config.yaml → ai/engine/config.template.yaml (framework) and ai/config.yaml (project);
    ai/ael/recipes/ralph-work.yaml → ai/engine/recipes/loop-work.yaml;
    ai/ael/recipes/ralph-review.yaml → ai/engine/recipes/loop-review.yaml;
    ai/state/ralph/ → ai/state/;
    ai/{governance,workflow,primer}.md, ai/templates/, ai/skills/ → ai/governance/software-engineering/;
    ai/doc/guide-audit-loop.md → ai/governance/software-engineering/doc/;
    ai/doc/guide-ael-operations.md → ai/engine/doc/guide-engine-operations.md;
    ai/context.md, ai/task.md → ai/governance/software-engineering/seed/;
    tests/ael/ → tests/engine/.
    Term mapping:
    AEL → engine; AEL run → run; Ralph Loop → loop; RALPH LOOP (recipe prompts) → LOOP;
    RALPH-BLOCKED.md → BLOCKED.md; .ralph-complete → .complete; .ralph-timeout → .timeout;
    ael_<timestamp>.LOG → engine_<timestamp>.LOG; [ael] console prefix → [engine];
    recipe set 'ralph' → 'loop'; target_profile 'ael' → 'engine' (legacy 'ael' accepted on read);
    start_ael, ael_status, reset_ael → start_engine, engine_status, reset_engine.
    The mapping is recorded in dev/tools/mapping-5bcd46ad.yaml and applied by
    a script; the residue search uses the same file.
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "Default config path ../../config.yaml; state file and log names; recipe set name; console prefix; target_profile alias"
      functions_affected:
        - "main"
        - "setup_logging"
        - "_select_recipe_set"
        - "extract_target_profile"
      classes_affected: []
    - component: "overwatch"
      file: "ai/src/overwatch.py"
      change_summary: "State directory ai/state/; state file names; target_profile alias; AEL labels"
      functions_affected:
        - "Scanner._read_ael_state (renamed _read_engine_state)"
      classes_affected:
        - "ProjectPaths"
        - "AelState (renamed EngineState)"
    - component: "engine-mcp"
      file: "ai/engine/mcp/server.py"
      change_summary: "Port of ael-mcp: new paths and tool names; launches the orchestrator with sys.executable (the engine environment); mcp pinned via ai/engine/requirements.txt"
      functions_affected:
        - "start_engine"
        - "engine_status"
        - "reset_engine"
      classes_affected: []
    - component: "propagation"
      file: "bin/propagate.sh"
      change_summary: "Declared project files: config.yaml at ai/ root; seed ai/config.yaml, context.md, task.md if absent; governance version read from ai/governance/<name>/governance.md"
      functions_affected: []
      classes_affected: []
    - component: "downstream migration"
      file: "bin/migrate-layout.sh"
      change_summary: "One-time: git mv old layout to new in a downstream project; --dry-run; refuses a dirty tree"
      functions_affected: []
      classes_affected: []
  data_changes:
    - entity: "state directory"
      change_type: "migration"
      details: "ai/state/ralph/ contents are transient; reset before migration"
  interface_changes:
    - interface: "orchestrator CLI default --config"
      change_type: "contract"
      details: "ai/ael/config.yaml → ai/config.yaml"
      backward_compatible: "no"
    - interface: "engine-mcp tool names"
      change_type: "signature"
      details: "start_ael, ael_status, reset_ael → start_engine, engine_status, reset_engine"
      backward_compatible: "no"

dependencies:
  internal:
    - component: "change-c37198be"
      impact: "Folded in; its pending independent review is covered by this change's review"
  external:
    - library: "Claude Desktop MCP configuration"
      version_change: "ael-mcp entry → engine-mcp at ai/engine/mcp/server.py, engine environment interpreter"
      impact: "Operator edits claude_desktop_config.json"
  required_changes:
    - change_ref: "change-c37198be"
      relationship: "related"

testing_requirements:
  test_approach: "Existing tests at new paths, static checks, residue search, live smoke run, downstream dry run"
  test_cases:
    - scenario: "pytest tests/engine tests/overwatch"
      expected_result: "All pass"
    - scenario: "linter.py and protocol_checker.py on dev/"
      expected_result: "No findings beyond the pre-migration baseline"
    - scenario: "Residue search for mapped old paths and terms"
      expected_result: "None outside the exclusions in out_of_scope"
    - scenario: "bash -n on bin/*.sh"
      expected_result: "Pass"
    - scenario: "Smoke run in dev/smoke, loop mode"
      expected_result: "SHIP; state and log files carry the new names"
    - scenario: "engine-mcp start_engine, engine_status, reset_engine against dev/smoke"
      expected_result: "Run launched, status reported, state reset"
    - scenario: "migrate-layout.sh --dry-run, then live, on a copy of GTach; then propagate.sh"
      expected_result: "New layout; nothing deleted; project files intact"
  regression_scope:
    - "Loop behaviour, gates, verdict handling"
    - "Propagation relocation and seeding"
  validation_criteria:
    - "All test cases pass"
    - "Independent review accepted"

implementation:
  effort_estimate: "1–2 days"
  implementation_steps:
    - step: "1. Tag pre-5bcd46ad; record linter and protocol_checker baseline"
      owner: "Strategic Domain"
    - step: "2. Write dev/tools/mapping-5bcd46ad.yaml"
      owner: "Strategic Domain"
    - step: "3. git mv to the target layout; remove govwatch files"
      owner: "Strategic Domain"
    - step: "4. Update paths and terms in documents; governance.md → 11.0"
      owner: "Strategic Domain"
    - step: "5. Update source, recipes, tests, scripts; port engine-mcp; write migrate-layout.sh"
      owner: "Strategic Domain"
    - step: "6. Run the test cases above"
      owner: "Strategic Domain + human (smoke run, engine-mcp)"
    - step: "7. Independent review; close this change and change-c37198be"
      owner: "Independent session; human"
    - step: "8. Migrate and propagate: dev/smoke/ai, GTach, solax-modbus, e-Paper-IP-Display, pi-netconfig"
      owner: "Human"
  rollback_procedure: "Framework: git reset to tag pre-5bcd46ad. Downstream: git revert of the migration commit (git mv only)."
  deployment_notes: "One commit per implementation step. governance.md major version 11.0 requires propagate.sh --allow-major."

verification:
  implemented_date: "2026-09-25"
  implemented_by: "Strategic Domain (Claude, Cowork session), operator-approved"
  verification_date: ""
  verified_by: ""
  test_results: >
    Session checks 2026-09-25: tests/engine and tests/overwatch 62/62 pass,
    identical to the pre-migration tree, run with an offline stub harness
    (pytest, openai and rich not installable in the session; confirm with
    real pytest in the engine environment). py_compile clean for all
    modules; bash -n clean for bin/*.sh; recipes and configs parse;
    linter.py dev/ 0 errors / 93 warnings and protocol_checker.py dev/
    0 findings, both equal to baseline; no broken relative Markdown links;
    residue search clean apart from retained identifiers (see notes).
    bin/migrate-layout.sh dry run and --apply, then bin/propagate.sh
    --allow-major, verified on a synthetic project built from the
    pre-migration ai/ tree: project config and context preserved, 11
    retired paths moved to ai-local/retired-5bcd46ad/ and logged, second
    propagate run up to date; fresh-project seeding of config.yaml,
    context.md and task.md verified; propagate refuses an old-layout target
    (exit 3). Pending: operator smoke run, engine-mcp exercise,
    independent review.
  issues_found: []

traceability:
  design_updates:
    - design_ref: "dev/design/design-ael-orchestrator.md"
      sections_updated:
        - "paths and terms"
      update_date: ""
  related_changes:
    - change_ref: "change-c37198be"
      relationship: "folds in"
  related_issues: []

notes: >
  Abbreviated workflow at William Watson's instruction (2026-09-25): no T06
  issue and no T03 prompt; implementation follows approval directly; one
  independent review after all steps. ai/index.md removal and govwatch
  deletion confirmed by the operator 2026-09-25.
  Retained deliberately: requirement identifiers FR-AEL-*/NFR-AEL-* and the
  file names design-ael-orchestrator.md and requirements-1c1f4ef6-ael.md
  (traceability); historical records (dev/task.md, eb782f83 design and
  requirements, struck backlog items, closed documents, Version History
  rows); the overwatch alert-file heading text (output unchanged).
  bin/propagate.sh installs one model (MODEL=software-engineering); model
  selection is Phase 2. Recipes remain in ai/engine/recipes/ (audit recipes
  move in Phase 2).

version_history:
  - version: "0.1"
    date: "2026-09-25"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "0.2"
    date: "2026-09-25"
    author: "William Watson"
    changes:
      - "Implemented steps 1–6 (session part); verification results and retained items recorded"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
