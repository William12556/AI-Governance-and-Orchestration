Created: 2026 September 22

```yaml
issue_info:
  id: "issue-e36a35d3"
  title: "Five Python modules under ai/ cite the retired protocol numbering scheme"
  date: "2026-09-22"
  reporter: "William Watson"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-e36a35d3"
    change_iteration: 1

source:
  origin: "planned_change"
  description: >
    The eb782f83 migration renumbers every protocol and template identifier and
    replaces positional citations of the form §1.x.y with protocol-relative
    citations of the form Pnn.a.b. Five Python modules under ai/ carry protocol
    citations in module docstrings and inline comments. On completion of the
    migration these citations will reference a numbering scheme that no longer
    exists, and will in several cases resolve to a different protocol than the
    one intended.

affected_scope:
  components:
    - name: "protocol_checker (module docstring, six check-section banners)"
      file_path: "ai/ael/src/protocol_checker.py"
    - name: "linter (module docstring, check-section banners, enum comment)"
      file_path: "ai/ael/src/linter.py"
    - name: "orchestrator (tactical_brief guidance strings, extraction docstrings)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "govwatch (tactical brief detection comment)"
      file_path: "ai/src/govwatch.py"
    - name: "overwatch (tactical brief detection comment)"
      file_path: "ai/src/overwatch.py"
  version: "current"

reproduction:
  prerequisites: "eb782f83 migration applied to the live corpus."
  steps:
    - "Apply the eb782f83 migration"
    - "Read the module docstring of ai/ael/src/protocol_checker.py"
    - "Observe citations of the form 'UUID chain integrity (P09 §1.10.2)'"
    - "Resolve P09 against the migrated governance.md: P09 is a reserved, contentless identifier"
    - "Resolve §1.10.2: the positional citation scheme no longer exists"
  frequency: "deterministic"
  reproducibility_conditions: "Any state of the corpus after migration and before this change."
  error_output: "None. The defect is silent: no tool reports it and no execution path is affected."

behavior:
  expected: >
    Citations in these modules name the protocol that governs the check they
    annotate, in the migrated scheme. For example, the UUID chain integrity
    check cites P13.2, the prompt protocol.
  actual: >
    Citations name the retired scheme. Several are actively misleading rather
    than merely stale: P03 and P04 exchanged identifiers in the migration, so a
    comment reading "One-to-one constraint (P03 §1.4.2)" cites the identifier
    that now belongs to Change while §1.4 was Change under the old scheme —
    correct by accident in that instance, and wrong in the coupling comments
    that pair P03 with P04.
  impact: >
    Documentation only. No control flow depends on protocol or template
    identifiers; document classes are keyed by name, never by template number.
    The harm is to a maintainer reading these modules, and to the framework's
    own claim that the corpus is internally consistent after migration.
  workaround: "Consult the alias appendix in governance.md to translate."

analysis:
  root_cause: >
    Protocol citations were embedded in source comments as documentation of
    which governance clause each check implements. That is good practice and is
    not itself the defect. The defect arises because the citations are written
    in a scheme that the migration retires.
  contributing_factors:
    - "Positional citations couple a reference to a protocol's ordinal position, which is the root defect eb782f83 exists to remove"
    - "No tooling validates citations embedded in source comments; linter.py and protocol_checker.py validate documents, not their own docstrings"
  scope_note: >
    Raised as an issue rather than folded into eb782f83 because these are
    modifications to existing source. Under the framework's own rule, the full
    issue-change-prompt workflow applies to src/ changes, whereas eb782f83's
    new tooling is initial implementation from an approved design and is exempt.

resolution_criteria:
  - "All protocol and template citations in the five modules use the migrated scheme"
  - "No positional §1.x.y citation remains in any of the five modules"
  - "All five modules import without error"
  - "linter.py and protocol_checker.py execute and report identically to their pre-change behaviour on the same inputs"
  - "govwatch.py and overwatch.py each complete one scan cycle"
  - "No executable line is altered; the diff contains only comments and docstrings"

traceability:
  related_documents:
    - "dev/proposals/proposal-eb782f83-protocol-template-reordering.md"
    - "dev/requirements/requirements-eb782f83-protocol-template-reordering.md"
    - "dev/design/design-eb782f83-protocol-template-reordering.md"
  related_requirements:
    - "CON-09 — Python modules under ai/ are governed as source code"
    - "FR-04-06 — conversion applies to comments and docstrings"
    - "NFR-07 — no behavioural change to any executable component"
    - "V-15 — the five modules import and execute unchanged"

version_history:
  - version: "1.0"
    date: "2026-09-22"
    author: "William Watson"
    changes:
      - "Initial issue document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
