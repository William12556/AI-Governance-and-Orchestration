Created: 2026 September 24

```yaml
issue_info:
  id: "issue-c37198be"
  title: "AEL: mcp 2.x breaks tool loading; missing --task file used as task text; filesystem-mcp 2.x write tools unrecognised; backlog §5.0 item 5 cases untested"
  date: "2026-09-24"
  reporter: "William Watson"
  status: "open"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c37198be"
    change_iteration: 1

source:
  origin: "test_result"
  test_ref: "dev/smoke live runs 2026-09-24 (ael_20260924-071040.LOG, ael_20260924-072824.LOG); dev/backlog.md §5.0 item 5"
  description: >
    Backlog §5.0 live verification on a fresh Python 3.11 environment exposed
    two defects, and §5.0 item 5 lists edge cases from closed triples
    a2f9c4d1, f5c28a04 and d1f4a83b that have never been exercised.

affected_scope:
  components:
    - name: "requirements"
      file_path: "ai/ael/requirements.txt"
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
  designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
  version: "governance 10.5; AI-G&O HEAD 2026-09-24"

reproduction:
  prerequisites: "Fresh virtual environment installed from ai/ael/requirements.txt"
  steps:
    - "D1: pip install -r ai/ael/requirements.txt resolves mcp 2.x; start AEL in loop mode"
    - "D2: run orchestrator.py --task task.md from a directory without task.md"
    - "D3: dev/smoke Run A (ael_20260924-083145.LOG): worker writes src/split.py with create{files:[...]}"
  frequency: "always"
  reproducibility_conditions: "D1 whenever pip resolves mcp>=2; D2 whenever --task names a missing file"
  preconditions: ""
  test_data: "dev/smoke harness"
  error_output: >
    D1: "[ael] Warning: failed to connect to 'filesystem': 'Tool' object has
    no attribute 'inputSchema'"; worker phase tools=0; BLOCKED on MCP error
    threshold. D2: the literal string "task.md" became the task; the worker
    invented work and wrote seven untracked files into the framework root.
    D3: "pytest gate: no deliverables — gate is no-op" in every cycle; SHIP at
    iteration 5 with both read-evidence and pytest gates vacuous.

behavior:
  expected: >
    D1: tool loading works on a fresh install. D2: a --task value that names a
    file which does not exist stops the run before any change. T: the §5.0
    item 5 cases have repeatable tests.
  actual: >
    D1: requirements.txt pins only mcp>=1.0.0; mcp 2.x removed Tool.inputSchema,
    which mcp_client.py line 70 reads. D3: @j0hanz/filesystem-mcp@latest
    (2.5.0) names its write tools create/edit/delete/move/patch/replace_text and
    batches paths in files/paths/moves lists; _WRITE_TOOLS lacks create, patch
    and replace_text and path extraction reads only top-level keys. Effects:
    create writes bypass F4 scope validation, the F21 audit-report guard and
    the post-write syntax check, and are missing from the manifest, so the
    pytest and read-evidence gates no-op; batched reads (read paths[]) are not
    counted as reviewer read evidence; mcp_client classes search_and_replace as
    read-only (^search). D2: main_async treats any --task value
    that is not an existing path as task text. T: no tests exist; the AEL test
    suite was deleted in b4df519.
  impact: >
    D1 disables all tools on any new installation. D3 lets writes escape the
    project-root scope check and turns the SHIP gates into no-ops. D2 lets a mistyped path run
    an unscoped task with write access to the project root.

analysis:
  root_cause: >
    D1: unbounded dependency. D3: MCP server pinned to @latest while tool names
    and argument shapes are hard-coded. D2: task resolution does not distinguish a path
    from task text. T: test cases recorded as unexercised at operator closure.
  technical_notes: >
    Live evidence 2026-09-24: BLOCKED exit (MCP error threshold, run 071040)
    and stall-detection BLOCK (run 072824) were both observed; tests still
    cover them for repeatability.

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5) — abbreviated workflow at operator instruction"
  target_date: "2026-09-24"
  approach: "Pin mcp<2; refuse a path-like --task that does not exist; recognise filesystem-mcp 2.x write tools and batched paths, pin the server to 2.5.0; add tests/ael/ unit tests with stub model and MCP clients."
  change_ref: "change-c37198be"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

traceability:
  design_refs:
    - "dev/design/design-ael-orchestrator.md"
  change_refs:
    - "change-c37198be"
  test_refs:
    - "tests/ael/test_orchestrator_edge_cases.py"

version_history:
  - version: "1.0"
    date: "2026-09-24"
    author: "William Watson"
    changes:
      - "Initial issue from backlog §5.0 live verification"
  - version: "1.1"
    date: "2026-09-24"
    author: "William Watson"
    changes:
      - "D3 added from dev/smoke Run A"
  - version: "1.2"
    date: "2026-09-25"
    author: "William Watson"
    changes:
      - "Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t06_issue"
```
