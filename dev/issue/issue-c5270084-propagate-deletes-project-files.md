Created: 2026 September 23

```yaml
issue_info:
  id: "issue-c5270084"
  title: "propagate.sh --delete removes project-local files, including untracked files git cannot restore"
  date: "2026-09-23"
  reporter: "William Watson"
  status: "resolved"
  severity: "critical"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c5270084"
    change_iteration: 1

source:
  origin: "live_execution"
  test_ref: "First live run of change-07087e91: bin/propagate.sh ~/Documents/GitHub/solax-modbus, 2026-09-23 (9.11 -> 10.2)"
  description: >
    change-07087e91 introduced rsync --delete on the assumption that every file
    under a downstream ai/ outside the exclude list belongs to the framework.
    solax-modbus kept project-local files at ai/ root. The run deleted
    ai/instructions.md, ai/obsidian_markdown_guidelines.md and
    ai/ael/config.yaml.bak (tracked; restored from git HEAD the same day) and
    ai/project_information.md (gitignored, untracked; not recoverable from git)
    and the gitignored contents of ai/ael/tmp/.

affected_scope:
  components:
    - name: "propagate"
      file_path: "bin/propagate.sh"
  designs: []
  version: "governance 10.2"

behavior:
  expected: "Propagation never deletes a file that git cannot restore, and never deletes a file the project declares its own."
  actual: "Any file under the target ai/ absent from the source is deleted, tracked or not."
  impact: "Irrecoverable loss of project-local data (ai/project_information.md in solax-modbus)."

analysis:
  root_cause: >
    The exclude list encodes the framework's own knowledge of project-local
    paths; downstream projects hold files the framework does not know about.
    The VM test target in change-07087e91 contained only known paths, so the
    assumption was never tested. change-07087e91's risk entry named the
    consequence and mitigated it with the preview alone, which proved
    insufficient: the preview listed the deletion and it was not recognised as
    project data.

resolution:
  assigned_to: "Claude (Cowork, Opus 5.5) — direct implementation"
  target_date: "2026-09-23"
  approach: "Protect every untracked or gitignored target file; per-project ai/.propagate-keep for tracked project files; no deletions for a non-git target."
  change_ref: "change-c5270084"
  resolved_date: "2026-09-23"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "Protect rules for untracked files and ai/.propagate-keep under change-c5270084. solax-modbus tracked files restored from HEAD; ai/.propagate-keep written there."

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

traceability:
  design_refs: []
  change_refs:
    - "change-c5270084"
  test_refs: []

version_history:
  - version: "1.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Initial issue from the solax-modbus propagation"
  - version: "1.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Resolved under change-c5270084; awaiting audit or waiver"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
