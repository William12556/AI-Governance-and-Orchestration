Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-793992ae"
  task_type: "code_generation"
  source_ref: "change-793992ae"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-793992ae"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §9.0: engine-mcp refactor."
  constraints:
    - "start_engine, engine_status and reset_engine keep their names and arguments"
    - "work_status writes nothing"
    - "The project's own engine and manifest are used (subprocess with the server's interpreter)"

specification:
  requirements:
    functional:
      - "state_dir from ai/config.yaml loop.state_dir, default ai/state"
      - "start_engine loop/worker: task must be an existing prompt-<uuid>-*.md inside <project>/ai/workspace/ (relative paths resolve against the project)"
      - "Popen handle kept per project; poll() before the probe; without a handle os.waitpid(pid, WNOHANG), ChildProcessError -> os.kill(pid, 0)"
      - "work_status(project_dir): JSON from 'stages.py --json' run in the project"
      - "stages.py: command-line entry with --json"
      - "migrate-layout.sh: warn when loop.state_dir is not ai/state"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/mcp/server.py"
    - path: "ai/engine/src/stages.py"
    - path: "bin/migrate-layout.sh"
    - path: "tests/engine/test_engine_mcp.py"

success_criteria:
  - "Full engine and overwatch test suites pass"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
