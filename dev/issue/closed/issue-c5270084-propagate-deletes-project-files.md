Created: 2026 September 23

```yaml
issue_info:
  id: "issue-c5270084"
  title: "propagate.sh --delete removes project-local files, including untracked files git cannot restore"
  date: "2026-09-23"
  reporter: "William Watson"
  status: "closed"
  severity: "critical"
  type: "defect"
  iteration: 3
  coupled_docs:
    change_ref: "change-c5270084"
    change_iteration: 3

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
  approach: "Iteration 3: never delete; relocate every non-declared target file absent from the source to ai-local/ with an advisory label (governance P10.6)."
  change_ref: "change-c5270084"
  resolved_date: "2026-09-23"
  resolved_by: "Claude (Cowork, Opus 5.5)"
  fix_description: "Iteration 1: protect rules and ai/.propagate-keep. Iteration 2: content classification and relocation to ai-local/. solax-modbus tracked files restored from HEAD."

verification:
  verified_date: "2026-09-23"
  verified_by: "Independent follow-up audit (dev/audit/closed/audit-c5270084-followup-2026-09-23.md)"
  test_results: "F-01 to F-11 resolved, F-12 partially resolved; no project content absent from the source lost in any case."
  closure_notes: "Closed at operator direction. Residual findings N-01 to N-08 continue under issue-b170cf6a."

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
  - version: "2.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 2: resolution approach changed at operator direction (relocate project files to ai-local/)"
  - version: "3.0"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Iteration 3 after audit-c5270084 refuted iteration 2: no-delete design"
  - version: "3.1"
    date: "2026-09-23"
    author: "William Watson"
    changes:
      - "Closed after independent follow-up audit; status resolved -> closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.3"
  schema_type: "t03_issue"
```
