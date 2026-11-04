# Prompt: Correct ael-mcp State Directory to ai/state/ralph

Created: 2026 June 15

---

## Table of Contents

- [1.0 Prompt Information](#10-prompt-information)
- [2.0 Context](#20-context)
- [3.0 Specification](#30-specification)
- [4.0 Deliverable](#40-deliverable)
- [5.0 Testing](#50-testing)
- [6.0 Tactical Brief](#60-tactical-brief)
- [7.0 Success Criteria](#70-success-criteria)
- [Version History](#version-history)

---

## 1.0 Prompt Information

```yaml
prompt_info:
  id: "prompt-c4a9f2e1"
  task_type: "code_modification"
  source_ref: "change-c4a9f2e1"
  date: "2026-06-15"
  iteration: 1
  coupled_docs:
    change_ref: "change-c4a9f2e1"
    change_iteration: 1
```

Tactical Domain: Claude Code, operating in the ael-mcp repository
(William12556/ael-mcp), not the framework repository. Read each target file
before editing and apply only the changes specified.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Context

```yaml
context:
  purpose: >
    Align ael-mcp with the ai/-consolidated layout. The orchestrator now writes
    loop state to ai/state/ralph/; ael-mcp/server.py still hardcodes .ael/ralph.
    Correct the constant and the documentation references.
  integration: >
    Standalone repository; no framework propagation. server.py is the only
    source file. requirements.txt is unchanged (mcp only).
  knowledge_references: []
  constraints:
    - "Literal path correction only; do not add a YAML parser or new dependency"
    - "Do not alter _STATE_FILES, tool signatures, or process logic"
    - "Read each file before editing; preserve formatting and alignment"
    - "Operate in the ael-mcp repository, not the framework repository"
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Specification

```yaml
specification:
  description: >
    Change one constant and one docstring line in server.py; replace the
    .ael/ralph references in README.md and DESIGN.md.
  edits:
    - file: "server.py"
      changes:
        - "Constant (~line 26): _STATE_REL = \".ael/ralph\"  ->  _STATE_REL = \"ai/state/ralph\" (preserve existing column alignment)"
        - "Module docstring (~line 6): 'report current run state from .ael/ralph/' -> 'report current run state from ai/state/ralph/'"
    - file: "README.md"
      changes:
        - "Replace both .ael/ralph/ references with ai/state/ralph/ (tool table row and the 'Reads ...' line)"
    - file: "DESIGN.md"
      changes:
        - "Replace all .ael/ralph/ references with ai/state/ralph/ (5 occurrences: run-state location, subprocess log note, run-record note, state_files note, log_path example)"
  technical:
    language: "Python and Markdown"
    version: "Python 3.11"
    standards:
      - "No behavioural change; path string and documentation only"
      - "mcp remains the only dependency"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Deliverable

```yaml
deliverable:
  format_requirements:
    - "Apply edits in place to the existing files in the ael-mcp repository"
  files:
    - path: "server.py"
    - path: "README.md"
    - path: "DESIGN.md"
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Testing

```yaml
testing:
  approach: >
    Import-check server.py for syntax. Optionally run a smoke check of
    start_ael / ael_status / reset_ael against a project migrated to the ai/
    layout and confirm state is read and written under ai/state/ralph/.
  validation:
    - "server.py imports without error"
    - "grep finds no remaining .ael/ralph in server.py, README.md, DESIGN.md"
    - "start_ael writes the run record to ai/state/ralph/ (if smoke-tested)"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Tactical Brief

```yaml
tactical_brief: |
  Operate in the ael-mcp repository (William12556/ael-mcp). Apply path-only
  edits; read each file first; change nothing else.
  1. server.py — change the module constant
        _STATE_REL        = ".ael/ralph"
     to
        _STATE_REL        = "ai/state/ralph"
     keeping the existing column alignment. In the module docstring near the
     top, change the ael_status line "report current run state from .ael/ralph/"
     to "... from ai/state/ralph/". Do not touch _STATE_FILES, tool signatures,
     subprocess handling, or imports. Do not add a YAML parser.
  2. README.md — replace both ".ael/ralph/" references with "ai/state/ralph/"
     (the tool-table row for ael_status and the "Reads ... state files" line).
  3. DESIGN.md — replace all five ".ael/ralph/" references with
     "ai/state/ralph/" (run-state location, subprocess log note, run-record
     note, state_files note, and the log_path example).
  Verify: grep for ".ael/ralph" returns nothing across the three files; server.py
  imports cleanly.
```

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Success Criteria

```yaml
success_criteria:
  - "server.py _STATE_REL equals \"ai/state/ralph\" with alignment preserved"
  - "server.py docstring ael_status line names ai/state/ralph/"
  - "No .ael/ralph reference remains in server.py, README.md, or DESIGN.md"
  - "server.py imports without error; mcp remains the only dependency"
  - "No change to _STATE_FILES, tool signatures, or process logic"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-15 | William Watson | Initial prompt — ael-mcp state directory correction, coupled to change-c4a9f2e1 |

---

Copyright (c) 2026 William Watson. MIT License.
