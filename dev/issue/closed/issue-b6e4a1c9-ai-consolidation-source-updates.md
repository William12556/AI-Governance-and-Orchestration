# Issue: Source-Code Path References for ai/ Consolidation

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
  id: "issue-b6e4a1c9"
  title: "Source-code and script path references for ai/ consolidation"
  date: "2026-06-15"
  reporter: "William Watson"
  status: "resolved"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-b6e4a1c9"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Source

```yaml
source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Phase 1 of the ai/ consolidation relocated the framework footprint under
    ai/ in configuration and documentation: workspace/ to ai/workspace/, loop
    state .ael/ralph/ to ai/state/ralph/, and govwatch output to
    ai/dashboard-alerts.md. Source code and provisioning scripts still
    reference the pre-consolidation layout and must be updated so the
    framework operates against the new structure. See
    change-plan-ai-consolidation v0.2 §4.4, §4.6 and §7.0 Phase 2.
```

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Affected Scope

```yaml
affected_scope:
  components:
    - name: "govwatch ProjectPaths construction"
      file_path: "framework/ai/src/govwatch.py"
    - name: "skeleton sync excludes"
      file_path: "bin/sync-skel.sh"
    - name: "downstream propagation excludes"
      file_path: "bin/propagate.sh"
    - name: "regression test skeleton-layout assertions"
      file_path: "framework/ai/ael/tests/test_regression.py"
  designs:
    - design_ref: "dev/design/design-govwatch.md (govwatch paths)"
  version: "framework as of 2026-06-15, post Phase 1 consolidation"
```

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Behavior

```yaml
behavior:
  expected: >
    govwatch reads ai/workspace/, ai/state/ralph/, and writes
    ai/dashboard-alerts.md. The sync and propagation scripts do not carry the
    ephemeral ai/state/ directory or the generated ai/dashboard-alerts.md into
    skel or downstream projects. The regression test asserts the skel layout
    at skel/ai/workspace/.
  actual: >
    govwatch.py constructs workspace = root/"workspace", ael_state =
    root/".ael"/"ralph", alerts_file = root/"dashboard-alerts.md". The scripts
    have no exclude for state/ or dashboard-alerts.md. test_regression.py
    asserts the pre-consolidation skel/workspace/ layout.
  impact: >
    govwatch would not locate documents or state under the new layout and
    would write the alerts file to the wrong location. With state now inside
    the propagated ai/ subtree, the scripts would carry ephemeral state into
    skel and downstream projects. The regression test would fail against the
    new skel layout.
  workaround: "None. Source must match the relocated structure."
```

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Analysis

```yaml
analysis:
  root_cause: >
    Path references in source and scripts were authored against the
    pre-consolidation layout. The Phase 1 change relocated those paths in
    configuration and documentation only; the corresponding source and script
    references were deferred to Phase 2 because they require the issue/change/
    prompt protocol.
  technical_notes: >
    govwatch.py centralises all three paths in ProjectPaths within main(), so
    the change is three constructor lines plus two cosmetic strings (the
    startup validation message and the relative-path display anchor). The
    scripts already operate only on the ai/ subtree; the sole required change
    is adding excludes so the now-internal ai/state/ and ai/dashboard-alerts.md
    are not propagated. Test fixtures that build self-contained temporary
    trees are unaffected; only assertions against the real skel layout change.
  related_issues:
    - issue_ref: "issue-7c1d9e02"
      relationship: "same component (govwatch); original implementation"
```

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Resolution

```yaml
resolution:
  assigned_to: "Tactical Domain (Claude Code)"
  target_date: ""
  approach: >
    Implement via change-b6e4a1c9 and prompt-b6e4a1c9. Claude Code edits
    framework/ and bin/ directly. skel/ai mirrors update via Phase 3
    sync-skel.sh; downstream projects update via propagate.sh.
  change_ref: "change-b6e4a1c9"
  resolved_date: "2026-06-15"
  resolved_by: "William Watson"
  fix_description: >-
    All four edits implemented and verified by source inspection: govwatch.py
    ProjectPaths (ai/workspace, ai/state/ralph, ai/dashboard-alerts.md) plus
    validation message and display anchor; bin/sync-skel.sh and bin/propagate.sh
    exclude state/ and dashboard-alerts.md; test_regression.py asserts
    skel/ai/workspace/.

verification:
  verified_date: "2026-06-15"
  verified_by: "William Watson"
  test_results: "Source inspection 2026-06-15; skel/ai/workspace/ present, regression assertion satisfied"
  closure_notes: "Framework-side consolidation source updates complete; skel/downstream follow via propagation"

traceability:
  design_refs:
    - "dev/design/design-govwatch.md"
  change_refs:
    - "change-b6e4a1c9"
  test_refs:
    - "framework/ai/ael/tests/test_regression.py"

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
| 1.0 | 2026-06-15 | Initial issue — source and script path alignment for ai/ consolidation |
| 1.1 | 2026-06-15 | Resolved: all edits implemented and verified by source inspection; closed |

---

Copyright (c) 2026 William Watson. MIT License.
