Created: 2026 June 26

```yaml
issue_info:
  id: "issue-f1c8a3e6"
  title: "Minor orchestrator defects: continue off-by-one, reviewer framing, audit counting, context window resolution"
  date: "2026-06-26"
  reporter: "William Watson"
  status: "closed"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-f1c8a3e6"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/proposals/proposal-f9a2c41b-orchestrator-review.md"
  description: >
    From orchestrator.py review (proposal-f9a2c41b), lower-severity findings F15,
    F16, F17, F18: a continue-prompt off-by-one, inconsistent reviewer framing,
    inconsistent audit item counting, and arbitrary context-window resolution.

affected_scope:
  components:
    - name: "orchestrator (continue prompt, review_task, audit counting, resolve_context_window)"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
    - name: "AEL config (context override)"
      file_path: "ai/ael/config.yaml"
  version: "current"

reproduction:
  prerequisites: "AEL run reaching the relevant condition."
  steps:
    - "F15: after the user answers 'y' to the continue prompt, '_extra += max_iterations; continue' re-enters the while and increments i, skipping one iteration number; the loop delivers one fewer cycle than the 'another N' promised"
    - "F16: review_task in run_loop lacks the [AEL RUNTIME CONTEXT] header the review recipe references; single --mode reviewer is handed the worker task text rather than a review instruction"
    - "F17: audit snapshot/scope checks count line.strip().startswith('- ['); the unchecked-item gate counts substring '- [ ]'; differing indentation/format makes the two disagree"
    - "F18: resolve_context_window returns glob(...)[0] (an arbitrary match when multiple variant dirs match); the config.json max_position_embeddings (e.g. 500000) overstates the vendor-supported window (256K)"
  frequency: "intermittent"
  reproducibility_conditions: "F15 on continue; F16 every review/single-mode; F17 on varied item formatting; F18 on multi-match globs or overstated config window."

behavior:
  expected: >
    The continue prompt delivers the promised cycle count; reviewer framing is
    consistent across modes with the runtime header; one shared parser counts
    audit items; the context window resolves to the exact model directory with a
    supported-context override.
  actual: >
    One fewer cycle than promised (F15); inconsistent reviewer framing (F16);
    divergent audit counts (F17); overstated context window (F18).
  impact: "Minor; narrow-condition."
  workaround: "None required."

analysis:
  root_cause: >
    F15: the post-'y' compensation increments past one iteration number. F16:
    review_task omits the runtime header and single-mode reuses the worker task
    text. F17: two different item-counting expressions. F18: glob(...)[0] is an
    arbitrary match and config.json overstates the usable window.
  technical_notes: >
    F15: fix the bound-check/compensation. F16: prepend the runtime header to
    review_task and use a consistent review instruction across modes. F17: use a
    single shared parser for audit-index items. F18: match the exact model
    directory; allow a per-model supported-context override in config.yaml.

resolution:
  approach: >
    Continue-prompt fix (F15); consistent reviewer framing with the runtime
    header (F16, orchestrator + ralph-review.yaml); shared audit item parser
    (F17); exact-directory context resolution with a config override (F18,
    orchestrator + config.yaml). Addressed opportunistically per the proposal.

verification:
  verification_steps:
    - "After 'y', the loop delivers exactly the promised additional cycles"
    - "Reviewer framing includes the runtime header in both loop and single-mode"
    - "Audit snapshot/scope and the unchecked-item gate count identically for varied formatting"
    - "The context window resolves to the exact model directory; a supported-context override is honoured"

notes: >
  Groups proposal-f9a2c41b findings F15 (low), F16 (low), F17 (low), F18 (low).
  The F18 supported-context override is configuration; F18 exact-directory
  match, F15, F16, and F17 are source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Resolved: fix implemented and verified against source; issue closed"
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
