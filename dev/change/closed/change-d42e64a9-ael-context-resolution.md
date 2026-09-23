Created: 2026 July 08

```yaml
change_info:
  id: "change-d42e64a9"
  title: "Retire budget.py; tiered live/config context-window resolution in orchestrator.py; project-root-relative paths; live-query Strategic Domain gate"
  date: "2026-07-08"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d42e64a9"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-d42e64a9"
  description: >
    Resolve resolver duplication, config.yaml path non-portability, and
    the Strategic Domain staleness gate identified in issue-d42e64a9.

scope:
  summary: >
    Two work streams, following the split precedent in change-713437bc.
    Stream A (source code): ai/ael/src/orchestrator.py gains a tiered
    context-window resolver and runtime project-root computation;
    ai/ael/config.yaml drops context.models_dir and replaces literal
    absolute paths with a {PROJECT_ROOT} placeholder; ai/ael/src/budget.py
    is retired (git mv to deprecated/). Requires T04 + Tactical Domain
    (target_profile: ael), since it is a source-code refactor. Stream B
    (documents): ai/governance.md §1.10.2, ai/primer.md §7.0,
    docs/claude/primer.md, ai/workflow.md, and
    dev/requirements/ael-requirements.md rewording — the Strategic
    Domain's precondition changes from a file-existence check to a direct
    omlx_model_status call. Direct Strategic Domain edit, no triple,
    consistent with repo precedent for governance/primer/template
    document edits.
  affected_components:
    - name: "AEL orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "AEL configuration"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
    - name: "Standalone budget calculator"
      file_path: "ai/ael/src/budget.py"
      change_type: "delete"
  affected_designs: []
  out_of_scope:
    - "govwatch.py — paused per human direction pending this change's completion"
    - "Setting max_context_window inside oMLX's own admin panel for installed models — an operator action in an external system, not a framework change"
    - "Retrofitting config.yaml in downstream projects (GTach, solax-modbus, e-Paper-IP-Display) — config.yaml remains project-specific and excluded from bin/propagate.sh; each project's config.yaml is corrected independently at the operator's discretion"
    - "A new CLI entry point replacing budget.py's standalone invocation — the Strategic Domain gate now queries oMLX directly rather than reading a file budget.py would have produced"

rational:
  problem_statement: >
    Context-window resolution is implemented twice and has already
    diverged once (issue-d42e64a9, finding 1). config.yaml commits
    machine-specific absolute paths that break on any other installation
    (finding 2). The Strategic Domain's context-budget precondition
    checks file existence, not currency, and can pass against a stale
    model configuration (finding 3).
  proposed_solution: >
    Consolidate resolution into orchestrator.py alone, ordered:
    (1) config.yaml context.context_window explicit override, (2) live
    query to oMLX's admin endpoint (settings.max_context_window) for the
    configured model id, (3) config.yaml
    context.model_context_windows per-model override, (4) unknown — warn
    and instruct. Retire budget.py and context.models_dir entirely.
    Compute project root at runtime via os.getcwd() — consistent with
    the existing _archive_audit_artifacts() precedent already in
    orchestrator.py — and substitute a {PROJECT_ROOT} placeholder into
    MCP server spawn arguments in config.yaml, removing all committed
    absolute paths. Replace the Strategic Domain's file-existence check
    with a direct omlx_model_status call before authoring any
    AEL-targeted T04 prompt.
  alternatives_considered:
    - option: "Live query only, no config.yaml fallback tiers"
      reason_rejected: >
        omlx_model_status currently returns settings.max_context_window
        = null for North-Mini-Code-1.0-4bit and -6bit (the configured
        default). A live-query-only design leaves context window
        permanently unresolved until the operator sets it in oMLX's own
        admin panel, with no interim fallback.
    - option: "Keep budget.py as a separate standalone pre-flight tool, just fix its glob bug"
      reason_rejected: >
        This is the second occasion the two resolvers have diverged
        (change-f1c8a3e6's per-model override fix reached
        orchestrator.py only). A single resolver removes the recurring
        class of defect rather than patching one more instance of it.
    - option: "Derive PROJECT_ROOT from Path(__file__).resolve().parents[3] instead of os.getcwd()"
      reason_rejected: >
        os.getcwd() is already the project-root assumption used
        elsewhere in this file (_archive_audit_artifacts); introducing a
        second, different assumption in the same module is inconsistent
        and gives no practical benefit under the documented invocation
        pattern.
  benefits:
    - "Single source of truth for context-window resolution; eliminates the divergence-prone duplication class of defect"
    - "Fresh clone or new-machine installation requires no manual path correction for AEL's own MCP server spawning"
    - "Strategic Domain gate reflects the model actually configured at authoring time, not a stale snapshot"
    - "No new external dependency — live query uses the stdlib HTTP client, consistent with minimal-dependency preference"
  risks:
    - risk: "settings.max_context_window is null in oMLX for most currently installed models, including the configured default"
      mitigation: >
        Tier 3 (config.yaml model_context_windows) remains the practical
        primary source until the operator configures oMLX directly;
        behavior for North-Mini-Code-1.0-6bit is unchanged from today
        (262144, from existing config.yaml override).
    - risk: "os.getcwd()-based PROJECT_ROOT assumes AEL is invoked from the repository root"
      mitigation: >
        Matches the existing, already-shipped assumption in
        _archive_audit_artifacts(); no new invocation constraint
        introduced.
    - risk: "Removing context.models_dir is a breaking config.yaml schema change"
      mitigation: >
        config.yaml is excluded from propagation and is per-installation
        by design; this repository's own config.yaml is updated as part
        of this change, and downstream projects are corrected
        independently at the operator's discretion.

technical_details:
  current_behavior: >
    orchestrator.py::resolve_context_window() and
    budget.py::resolve_context_window() independently implement
    filesystem-glob-based config.json discovery under
    context.models_dir, with divergent handling of
    context.model_context_windows. config.yaml commits absolute paths
    for context.models_dir, mcp_servers.filesystem.args (npx binary and
    project root), and mcp_servers.mcp-grep.command (venv Python
    interpreter). The Strategic Domain's precondition (governance
    §1.10.2, primer §7.0) requires only that
    ai/state/ralph/context-budget.md exist.
  proposed_behavior: >
    orchestrator.py is the sole resolver, implementing the four-tier
    chain in rational.proposed_solution. config.yaml no longer contains
    context.models_dir or literal absolute paths; MCP server args use a
    {PROJECT_ROOT} placeholder substituted at connect time. budget.py no
    longer exists at ai/ael/src/budget.py. The Strategic Domain calls
    omlx_model_status directly before authoring an AEL-targeted T04
    prompt, in place of checking for context-budget.md.
  implementation_approach: >
    Stream A (Tactical Domain, target_profile: ael, via T04 + AEL):
    rewrite resolve_context_window() to the four-tier chain, adding an
    async helper that performs a single stdlib HTTP GET against
    {omlx.base_url with /v1 stripped}/admin/api/models?model_id=
    {omlx.default_model}, parsing settings.max_context_window, and
    degrading to the next tier on any network error, timeout, or null
    value (logged at WARNING, never raised). Remove the config.json glob
    branch and context.models_dir from both code and config.yaml. Add a
    module-level PROJECT_ROOT = os.getcwd() constant; before passing
    mcp_servers to MCPClient, substitute the literal string
    "{PROJECT_ROOT}" in any arg or command value. Update config.yaml
    accordingly.
    Stream B (Strategic Domain, direct edit — no triple): governance.md
    §1.10.2 and primer.md §7.0 — "context-budget.md must exist" becomes
    "call omlx_model_status for the configured model before authoring
    the prompt; treat a null or missing result as unresolved and warn
    the operator, same as today's unknown-window behavior." Mirror in
    docs/claude/primer.md. workflow.md's P01 flowchart node referencing
    "run budget.py" updated to reflect its retirement.
    dev/requirements/ael-requirements.md FR-AEL-005 and FR-AEL-012
    reworded to the four-tier chain and the retained
    context-budget.md write (still produced at AEL runtime for
    human/govwatch visibility; only the Strategic Domain's precondition
    changes).
    Retirement of budget.py itself (git mv to deprecated/) is a
    Strategic Domain filesystem action, performed directly via the
    Filesystem MCP server and a supplied git command, not part of the
    Tactical Domain deliverable.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        Replace resolve_context_window() with the four-tier chain
        including a new live-query helper; add PROJECT_ROOT constant and
        {PROJECT_ROOT} substitution before MCP server connection.
      functions_affected:
        - "resolve_context_window"
        - "write_context_report"
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "config.yaml context and mcp_servers schema"
      change_type: "schema"
      details: >
        Remove context.models_dir. Retain context.context_window and
        context.model_context_windows unchanged. mcp_servers.*.args and
        mcp_servers.*.command accept a {PROJECT_ROOT} placeholder token,
        substituted at runtime.
      backward_compatible: "no"

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Manual verification against the running oMLX server and repository,
    per repo precedent (no automated pytest suite for orchestrator.py).
  test_cases:
    - scenario: "North-Mini-Code-1.0-6bit configured; oMLX settings.max_context_window is null"
      expected_result: "Resolver falls to tier 3; reports 262144 (unchanged from current config.yaml override)"
    - scenario: "Operator sets max_context_window for a model in oMLX's admin panel; that model configured as default"
      expected_result: "Resolver reports the live value at tier 2, no config.yaml override needed"
    - scenario: "oMLX server unreachable at orchestrator startup"
      expected_result: "Tier 2 query fails gracefully, logged at WARNING; resolver falls to tier 3 or tier 4"
    - scenario: "Fresh clone on a machine with a different project path"
      expected_result: "AEL connects to filesystem and mcp-grep MCP servers with no manual config.yaml path edit"
    - scenario: "Strategic Domain authors an AEL-targeted T04 prompt"
      expected_result: "Precondition satisfied by a direct omlx_model_status call; context-budget.md is no longer read for this purpose"
  regression_scope:
    - "context-budget.md is still written by the orchestrator at AEL runtime (unchanged) — only the Strategic Domain's precondition source changes"
    - "Existing model_context_windows override for North-Mini-Code-1.0-6bit continues to resolve to 262144"
  validation_criteria:
    - "ai/ael/src/orchestrator.py has no syntax errors after edit"
    - "config.yaml remains valid YAML; no literal absolute path remains"
    - "budget.py absent from ai/ael/src/; present under deprecated/"

implementation:
  implementation_steps:
    - step: "Stream B: Strategic Domain edits governance.md, primer.md, docs/claude/primer.md, workflow.md, ael-requirements.md directly"
      owner: "Claude Desktop"
    - step: "Strategic Domain retires budget.py via git mv to deprecated/"
      owner: "Claude Desktop"
    - step: "Stream A: Strategic Domain authors T04 prompt (prompt-d42e64a9); Tactical Domain (AEL) implements"
      owner: "ael"
  rollback_procedure: "git revert; restore budget.py from deprecated/ or git history"
  deployment_notes: >
    No propagation action required. config.yaml remains project-specific
    and excluded from bin/propagate.sh.

traceability:
  related_issues:
    - issue_ref: "issue-d42e64a9"
      relationship: "resolves"

notes: >
  Stream split follows repo precedent (change-7c1d9a4e, change-713437bc):
  governance/primer/template document edits handled directly by the
  Strategic Domain, no triple; only the source-code stream requires the
  full T03/T02/T04 workflow. govwatch.py is explicitly out of scope,
  paused per human direction.

closure:
  verified_by: "William Watson"
  verified_date: "2026-07-09"
  verification_result: >
    Both streams complete: Stream A (orchestrator.py four-tier resolver,
    PROJECT_ROOT substitution, config.yaml models_dir removal) shipped
    prior to this closure session; Stream B (governance.md §1.2.8/§1.10.2,
    primer.md, docs/claude/primer.md, workflow.md, ael-requirements.md
    FR-AEL-005/012) completed and budget.py retired to deprecated/.
    testing_requirements.test_cases 1, 2, 3, 5 verified (1/3/5 scripted via
    tmp/validate-context-resolution.py against solax-modbus post-propagation;
    2 confirmed via live orchestrator log during --mode worker run). Test
    case 4 (fresh clone) accepted with waiver — see waivers below.
  waivers:
    - test_case: "Fresh clone on a machine with a different project path"
      reason: "No second clone environment available at verification time; PROJECT_ROOT substitution logic verified by code inspection (os.getcwd()-derived, consistent with _archive_audit_artifacts precedent) and by absence of committed absolute project-root paths in solax-modbus/ai/ael/config.yaml"
      accepted_by: "William Watson"
      accepted_date: "2026-07-09"

version_history:
  - version: "1.0"
    date: "2026-07-08"
    changes:
      - "Initial change document; two-stream resolution (orchestrator.py/config.yaml/budget.py via T04/Tactical Domain, governance/primer/workflow documents via direct Strategic Domain edit)"
  - version: "1.1"
    date: "2026-07-09"
    changes:
      - "Closed: status implemented; verification recorded; test case 4 accepted with waiver"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised implemented -> verified: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction; asserts no verification beyond what this document already records."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
