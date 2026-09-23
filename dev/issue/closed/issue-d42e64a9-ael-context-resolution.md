Created: 2026 July 08

```yaml
issue_info:
  id: "issue-d42e64a9"
  title: "AEL context-window resolution: duplicated resolver, non-portable model-path dependency, and stale Strategic Domain pre-flight gate"
  date: "2026-07-08"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d42e64a9"
    change_iteration: 1

source:
  origin: "code_review"
  description: >
    Analysis of ai/ael/src/orchestrator.py, ai/ael/src/budget.py,
    ai/ael/config.yaml, .gitignore, and bin/propagate.sh, cross-referenced
    against a live omlx_model_status query against the running oMLX server.
    Three findings, one shared root: context-window resolution and its
    supporting paths are computed in more than one place, some of those
    computations depend on machine-specific filesystem state, and one
    consumer of the result reads a snapshot rather than current state.

affected_scope:
  components:
    - name: "AEL orchestrator context resolver"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "Standalone budget calculator"
      file_path: "ai/ael/src/budget.py"
    - name: "AEL configuration"
      file_path: "ai/ael/config.yaml"
  designs: []
  version: ""

behavior:
  expected: >
    (1) One resolver implementation for context-window size, consulted by
    both the AEL runtime and any Strategic Domain pre-flight check. (2) A
    fresh clone of this repository on a different machine or under a
    different user account resolves all filesystem paths from the project
    root at runtime, with no committed absolute path requiring manual
    correction. (3) The Strategic Domain pre-flight gate reflects the
    model currently configured, not a snapshot that can predate a model
    change.
  actual: >
    (1) orchestrator.py::resolve_context_window() and
    budget.py::resolve_context_window() are separate implementations of
    the same logic; they have already diverged once (budget.py does not
    honor config.yaml's model_context_windows per-model override, added
    to orchestrator.py only, by change-f1c8a3e6). (2) config.yaml is
    committed to git containing absolute, machine-specific paths:
    context.models_dir ("/Users/williamwatson/ai-models"),
    mcp_servers.filesystem.args (project root path and npx binary path),
    and mcp_servers.mcp-grep.command (a venv Python interpreter path). A
    fresh clone on another installation inherits paths that do not exist
    there. (3) The Strategic Domain pre-flight gate (governance §1.10.2,
    primer §7.0) checks only that ai/state/ralph/context-budget.md
    exists, not whether it reflects the currently configured model.
  impact: >
    (1) Any future fix to context-window resolution logic (e.g.
    change-f1c8a3e6's F18 fix) must be applied twice or silently diverges
    again. (2) A fresh clone or new machine cannot run AEL or the
    filesystem/mcp-grep MCP servers without manually editing config.yaml
    paths; no error message points at this requirement. (3) A model swap
    in config.yaml between AEL runs is not reflected in the Strategic
    Domain's context-budget precondition check until budget.py or the
    orchestrator is re-run; the Strategic Domain can author a T04 prompt
    against a stale window size in the interim.
  workaround: >
    (1) None — apply resolver fixes to both files manually. (2) Manually
    edit config.yaml paths per installation. (3) Re-run
    python ai/ael/src/budget.py before authoring a T04 prompt if a model
    change is suspected.

analysis:
  root_cause: >
    (1) budget.py was introduced as a standalone pre-flight tool before
    the orchestrator's own resolver existed at startup; the two were
    never consolidated after the orchestrator gained its own resolution
    logic. (2) config.yaml carries operational settings (MCP server
    spawn arguments, model storage location) that are inherently
    per-installation, but the file is tracked in git with real paths
    rather than a portable form; bin/propagate.sh already treats
    config.yaml as project-specific and excludes it from propagation,
    confirming the framework's own design recognizes this class of value
    as non-portable, without providing a portable alternative. (3) The
    pre-flight gate was defined as a file-existence check
    (P09 §1.10.2 issue-713437bc rescoping addressed profile scope, not
    currency) because no live query mechanism was available to the
    Strategic Domain at the time; omlx_model_status (mcp_omlx) now
    provides one.
  technical_notes: >
    Live verification: omlx_model_status(params={}) against the running
    oMLX server returns settings.max_context_window = null for both
    North-Mini-Code-1.0-4bit and North-Mini-Code-1.0-6bit (the currently
    configured default model), and 393216 for the Devstral models. This
    field is populated only when explicitly set within oMLX's own admin
    panel per model — it is not an automatic readout of the model's
    inherent max_position_embeddings. oMLX's own is_default flag is set
    on mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit, not on
    North-Mini-Code — any live query must address a model by explicit id
    from config.yaml, never rely on oMLX's own default flag.
    _archive_audit_artifacts() in orchestrator.py already assumes
    os.getcwd() is the project root (os.path.join(os.getcwd(), "ai",
    "workspace", "audit")) — precedent for project-root-relative path
    computation already exists in this file.
  related_issues:
    - issue_ref: "issue-f1c8a3e6"
      relationship: "related"

resolution:
  approach: >
    Retire budget.py; orchestrator.py becomes the sole resolver. Tiered
    resolution: (1) config.yaml explicit global override, (2) live query
    to oMLX's admin endpoint for the configured model id, (3) config.yaml
    per-model override (existing model_context_windows), (4) unknown —
    warn. Remove context.models_dir and the config.json filesystem glob
    entirely. Compute project root at runtime (os.getcwd(), consistent
    with existing _archive_audit_artifacts precedent) and substitute it
    into MCP server spawn arguments rather than committing literal paths
    in config.yaml. Replace the Strategic Domain's file-existence
    precondition with a direct omlx_model_status call at T04-authoring
    time.
  change_ref: "change-d42e64a9"

traceability:
  design_refs: []
  change_refs:
    - "change-d42e64a9"

notes: >
  The govwatch.py question (its dependency on context-budget.md's
  presence as its only signal, absent MCP access) is explicitly paused
  pending resolution of this issue, per human direction. Not addressed
  here.

closure:
  verified_by: "William Watson"
  verified_date: "2026-07-09"
  verification_result: >
    Stream A (orchestrator.py tiered resolver, PROJECT_ROOT substitution,
    config.yaml portability) and Stream B (governance.md, primer.md,
    docs/claude/primer.md, workflow.md, ael-requirements.md wording;
    budget.py retired to deprecated/) both implemented. Test cases 1, 3, and
    5 (tmp/validate-context-resolution.py) executed and passed against
    solax-modbus (downstream project) after propagation via bin/propagate.sh.
    Test case 2 (live oMLX admin-panel value taking tier-2 precedence)
    confirmed by direct log evidence during an actual --mode worker run
    ("context window: 262144 (tier 1: config global override)", correctly
    demonstrating tier 1 > tier 2 precedence with live=393216 present) rather
    than an isolated null-override run. Test case 4 (fresh clone, different
    path) accepted with waiver — not executed; no second clone available at
    verification time. PROJECT_ROOT substitution and models_dir removal
    verified by inspection of solax-modbus/ai/ael/config.yaml (no committed
    absolute project-root path; {PROJECT_ROOT} placeholder present).
  waivers:
    - test_case: "Fresh clone on a machine with a different project path"
      reason: "No second clone environment available at verification time; tier-1/tier-3 path-portability logic verified by code inspection and config.yaml inspection instead"
      accepted_by: "William Watson"
      accepted_date: "2026-07-09"

version_history:
  - version: "1.0"
    date: "2026-07-08"
    changes:
      - "Initial issue document; bundles resolver duplication, config.yaml path non-portability, and Strategic Domain staleness gate under one shared root"
  - version: "1.1"
    date: "2026-07-09"
    changes:
      - "Closed: status resolved; verification recorded; test case 4 accepted with waiver"
  - version: "1.2"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Status normalised resolved -> closed: terminal value required for documents in closed/ (protocol_checker lifecycle rule). Closure-time record correction."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
