# Issue: ael-mcp — Hardcoded State Directory Misaligned with ai/ Consolidation

Created: 2026 June 15

---

## Table of Contents

- [1.0 Issue Information](#10-issue-information)
- [2.0 Source](#20-source)
- [3.0 Affected Scope](#30-affected-scope)
- [4.0 Behavior](#40-behavior)
- [5.0 Analysis](#50-analysis)
- [6.0 Resolution](#60-resolution)
- [Version History](#version-history)

---

## 1.0 Issue Information

```yaml
issue_info:
  id: "issue-c4a9f2e1"
  title: "ael-mcp hardcoded state directory misaligned with ai/ consolidation"
  date: "2026-06-15"
  reporter: "William Watson"
  status: "resolved"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c4a9f2e1"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "user_report"
  test_ref: ""
  description: >
    Surfaced during verification of the ai/ consolidation. ael-mcp/server.py
    hardcodes the loop state directory as _STATE_REL = ".ael/ralph". The
    consolidation relocated loop state to ai/state/ralph/ (orchestrator reads
    loop.state_dir from config.yaml). server.py was not updated and now points
    at the pre-consolidation location.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "_STATE_REL constant and dependent state operations"
      file_path: "server.py"
    - name: "ael_status docstring reference"
      file_path: "server.py"
    - name: "state directory references (documentation)"
      file_path: "README.md"
    - name: "state directory references (documentation)"
      file_path: "DESIGN.md"
  designs:
    - design_ref: "ael-mcp/DESIGN.md"
  version: "ael-mcp as of 2026-06-15 (repository: William12556/ael-mcp)"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Behavior

```yaml
behavior:
  expected: >
    ael_status reports state from ai/state/ralph/; start_ael seeds the run
    record there; reset_ael clears it there. The server and the orchestrator
    agree on the state location.
  actual: >
    server.py derives state_dir = root / ".ael/ralph". start_ael writes the
    run record and log to .ael/ralph/ while the orchestrator writes loop state
    to ai/state/ralph/. ael_status reads .ael/ralph/ and reports idle or stale
    state. The server and orchestrator disagree.
  impact: >
    AEL launched via the Claude Desktop ael-mcp tools misreports state against
    any project migrated to the ai/ layout. start_ael seeds state in the wrong
    directory; ael_status cannot observe the orchestrator's actual progress.
    AEL launched directly from the terminal is unaffected (the orchestrator
    reads loop.state_dir from config.yaml correctly).
  workaround: "Launch AEL from the terminal rather than via ael-mcp tools."
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Analysis

```yaml
analysis:
  root_cause: >
    server.py defines the state path as a hardcoded module constant
    (_STATE_REL = ".ael/ralph") rather than reading loop.state_dir from the
    project's config.yaml. The ai/ consolidation changed the canonical state
    location to ai/state/ralph; the hardcoded constant was not updated.
  technical_notes: >
    _validate_project() already resolves the path to config.yaml but does not
    parse it; state_dir is computed solely from the constant. The minimal,
    reliable fix is to correct the constant to "ai/state/ralph". A
    config-driven alternative (parse loop.state_dir from config.yaml) was
    considered but rejected: it adds a YAML-parser dependency to a server whose
    only current dependency is mcp, for marginal benefit, since state_dir is
    fixed by convention.
  related_issues:
    - issue_ref: "issue-b6e4a1c9"
      relationship: "same consolidation effort; framework-side source updates"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Resolution

```yaml
resolution:
  assigned_to: "Tactical Domain (Claude Code)"
  target_date: ""
  approach: >
    Implement via change-c4a9f2e1 and prompt-c4a9f2e1. Correct _STATE_REL to
    "ai/state/ralph", update the ael_status docstring, and align the .ael/ralph
    references in README.md and DESIGN.md.
  change_ref: "change-c4a9f2e1"
  resolved_date: "2026-06-15"
  resolved_by: "William Watson"
  fix_description: >-
    Implemented and verified by source inspection in the ael-mcp repository:
    server.py _STATE_REL is now "ai/state/ralph" and the ael_status docstring
    updated; README.md and DESIGN.md references all read ai/state/ralph/.

verification:
  verified_date: "2026-06-15"
  verified_by: "William Watson"
  test_results: "Source inspection 2026-06-15: no .ael/ralph reference remains in server.py, README.md, or DESIGN.md"
  closure_notes: "ael-mcp aligned with ai/-consolidated state location"

traceability:
  design_refs:
    - "ael-mcp/DESIGN.md"
  change_refs:
    - "change-c4a9f2e1"
  test_refs:
    - ""

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-06-15 | Initial issue — ael-mcp state directory alignment for ai/ consolidation |
| 1.1 | 2026-06-15 | Resolved: server.py, README.md, DESIGN.md verified on ai/state/ralph/; closed |

---

Copyright (c) 2026 William Watson. MIT License.
