Created: 2026 October 01

```yaml
change_info:
  id: "change-793992ae"
  title: "Phase 2 step 5: engine-mcp work_status, tracked runs only, configured state_dir, child reaping"
  date: "2026-10-01"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0); no issue document
    issue_iteration: null

source:
  type: "design"
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.3, §9.0"
  description: "Step 5 of the Phase 2 implementation plan: engine-mcp (FR-06, FR-08-06; audit-5bcd46ad L-01, L-02, L-08)."

scope:
  summary: >
    Refactor ai/engine/mcp/server.py in place. Add the read-only tool
    work_status(project_dir), which runs the project's own stages.py --json.
    start_engine in loop and worker mode accepts only a T03 prompt file inside
    the project's ai/workspace/, so a planner cannot bypass the pre-run check
    with a free-text task. The state directory is read from loop.state_dir in
    ai/config.yaml. The server keeps each child's Popen handle and reaps a
    finished child before the liveness probe. bin/migrate-layout.sh warns on a
    non-standard state_dir. Tests for server.py (backlog §2.0-9).
  affected_components:
    - { name: "engine-mcp", file_path: "ai/engine/mcp/server.py", change_type: "modify" }
    - { name: "stages CLI", file_path: "ai/engine/src/stages.py", change_type: "modify" }
    - { name: "migration script", file_path: "bin/migrate-layout.sh", change_type: "modify" }
    - { name: "overwatch", file_path: "ai/src/overwatch.py (configured state_dir, L-01)", change_type: "modify" }
    - { name: "documents", file_path: "governance.md 11.3, primer.md (both copies), docs/guide-orchestration.md", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_engine_mcp.py", change_type: "add" }
    - { name: "documents", file_path: "ai/engine/README.md, ai/engine/doc/guide-engine-operations.md, design-14e05e35 §9.0", change_type: "modify" }
  deviations:
    - "Design §9.0 limits start_engine to prompt tasks in loop mode; worker mode is limited too, because the pre-run check covers both modes and a free-text worker run would bypass it. Reviewer mode is read-only and unchanged."

rational:
  problem_statement: >
    engine-mcp hard-coded ai/state (L-01), reported pid_alive for a finished
    but unreaped child (L-02), had no tests (L-08) and accepted free-text loop
    tasks that the pre-run check does not cover.
  proposed_solution: "Configured state_dir, reaping, a prompt-only rule for writing modes, a read-only status tool."
  risks:
    - "A planner can no longer start a free-text loop or worker run through engine-mcp; the operator can still do so from the command line"

testing_requirements:
  validation_criteria:
    - "Configured state_dir used; free-text and outside-workspace tasks refused in loop and worker mode; reviewer mode unchanged; pid_alive false after a child exits; work_status returns the report and writes nothing"

implementation:
  rollback_procedure: "Revert the commit; restart engine-mcp in Claude Desktop."

traceability:
  requirements: ["FR-06-01", "FR-06-02", "FR-06-03", "FR-08-06", "NFR-06"]
  design: "design-14e05e35 §9.0"
  prompt: "dev/prompt/closed/prompt-793992ae-engine-mcp.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-01"
    changes: ["Verified: operator test 195 passed; commit f1eb673; closed"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
