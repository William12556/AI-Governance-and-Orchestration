Created: 2026 November 14

```yaml
issue_info:
  id: "issue-541f5c58"
  title: "Scripts and documents: bootstrap with an old-layout tarball, propagate.sh workspace folders before confirmation, flow-style workspace_folders, single-quoted state_dir, DURATION_LIMIT text, provider interface drift"
  date: "2026-11-14"
  status: "open"
  severity: "low"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-541f5c58"
    change_iteration: 1

source:
  origin: "code_review"  # audit-caab2052 L-19; audit-5bcd46ad L-12, H-01 option; audit-14e05e35 L-10
  description: >
    Stage C work item 5C (dev/task.md row 541f5c58): work item 5 parts
    (a) L-19, (b), (d) and (e). Raised by the autonomous session of
    2026-11-14 (prompt-cf99f3f3, report-b3a503a2) under the operator's
    one-time exemption.

affected_scope:
  components:
    - { name: "bootstrap", file_path: "bin/bootstrap.sh" }  # (d), (e)
    - { name: "propagate", file_path: "bin/propagate.sh" }  # (e)
    - { name: "migrate-layout", file_path: "bin/migrate-layout.sh" }  # (e)
    - { name: "audit review recipe", file_path: "ai/governance/software-engineering/recipes/audit-review.yaml" }  # (b)
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md" }  # (b)
    - { name: "profiles index", file_path: "ai/profiles/README.md" }  # (b)
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md" }  # (a)
  designs:
    - { design_ref: "design-14e05e35 §4.1 Interface" }
    - { design_ref: "requirements-14e05e35 FR-01-04" }
  version: "main 9b75595"

reproduction:
  prerequisites: "main 9b75595"
  steps:
    - "(d) run bin/bootstrap.sh against a release tarball in the pre-5bcd46ad layout (no ai/engine/)"
    - "(e) run bin/propagate.sh without --yes and with stdin not a terminal on an up-to-date target that lacks a workspace folder; run it on a target with a plan error"
    - "(e) declare 'workspace_folders: [issues, change]' in a model manifest and run bootstrap.sh or propagate.sh"
    - "(e) set state_dir: 'ai/state' (single quotes) in ai/config.yaml and run bin/migrate-layout.sh"
    - "(b) read audit-review.yaml, guide-engine-operations §5.0 and ai/profiles/README.md §4.0 against orchestrator.py and the tracked files"
    - "(a) compare design-14e05e35 §4.1 with providers.py"
  frequency: "always, under the stated condition"
  error_output: "(d) 'cp: cannot stat .../ai/engine/config.template.yaml' after ai/ was extracted. (e) migrate-layout.sh: warn … loop.state_dir is \"'ai/state'\" (standard: \"ai/state\")."

behavior:
  expected: >
    (d) bootstrap.sh refuses a tarball without ai/engine/ with a clear
    message and leaves the project unchanged. (e) propagate.sh creates
    workspace folders only after the plan-error check and the
    confirmation that guard its other writes; both scripts read a
    single-line flow-style workspace_folders list, which manifest.py
    accepts; migrate-layout.sh reads a single-quoted state_dir without a
    false warning. (b) The audit review recipe and the operations guide
    describe the duration-limit exit as the engine implements it; the
    profiles index names no link target that is absent from the
    repository. (a) design-14e05e35 §4.1 states the provider interface as
    built.
  actual: >
    (d) bootstrap.sh extracts the tarball and then fails in cp with set
    -e, leaving a partial ai/. (e) propagate.sh calls
    create_workspace_folders on the up-to-date path and exits 0 before
    the plan-error check and without confirmation; the awk parser in
    both scripts reads block lists only, so a flow-style list creates no
    folder and says nothing; migrate-layout.sh strips double quotes
    only. (b) audit-review.yaml tells the reviewer that a .complete file
    containing DURATION_LIMIT marks a duration-limit exit, and the guide
    lists that .complete content; the orchestrator writes .timeout with
    'TIMEOUT: iteration N' and exits with code 2 before any further
    review. ai/profiles/README.md links to
    docs/claude/project_information.md, which is gitignored. (a) design
    §4.1 names context_window(model) and await_ready(model, timeout,
    poll) -> bool; providers.py has live_context_window(model) and
    await_ready(model, timeout, interval, echo) -> None, raising
    ProviderError.
  impact: "(d) a failed install leaves a partial ai/ that blocks a re-run. (e) a write without the script's own safeguards; missing workspace folders for a flow-style manifest; a false warning. (b), (a) documents that do not match the code."
  workaround: "(d) remove the partial ai/ by hand. (e) write workspace_folders as a block list; use double quotes."

environment:
  os: "macOS and Linux (bash, awk, sed, tar)"

analysis:
  root_cause: >
    Line numbers at main 9b75595. (d) bin/bootstrap.sh:72-81. (e)
    bin/propagate.sh:452-459 (up-to-date path), :491-497 (plan-error
    check), :503-523 (confirmation), :125 and bin/bootstrap.sh:97 (awk
    parser); bin/migrate-layout.sh:98 (sed pattern with '"?'). (b)
    ai/governance/software-engineering/recipes/audit-review.yaml:21-25,
    :36; ai/engine/doc/guide-engine-operations.md:191;
    ai/profiles/README.md:51; orchestrator.py:2146-2151. (a)
    dev/design/design-14e05e35-engine-generalisation.md:142-147;
    providers.py:157, 200, 232, 372, 384, 424.
  technical_notes: >
    The duration limit is checked at the top of each loop iteration; the
    engine writes .timeout and returns 2, so no review phase follows and
    the reviewer cannot observe it. .timeout is cleared at the next loop
    start. The release tarball holds ai/ only (bin/release.sh).
    manifest.py loads the manifest with yaml.safe_load, so any YAML list
    form is accepted there; the shell scripts parse it with awk.

resolution:
  approach: "To be defined in change-541f5c58."
  change_ref: "change-541f5c58"

traceability:
  design_refs: ["design-14e05e35 §4.1", "requirements-14e05e35 FR-01-04"]
  change_refs: ["change-541f5c58"]

notes: "Audit references: audit-caab2052 L-19 (§14.0, decided 2026-11-14 by the session under the one-time exemption); audit-5bcd46ad L-12 and the H-01 option (dev/audit/closed/); audit-14e05e35 L-10 (dev/audit/closed/audit-14e05e35-phase2-2026-10-01.md). The guide §5.0 row was found by the session on 2026-11-14 (report-b3a503a2 §3.7 DD-02)."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial issue for Stage C work item 5C"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "issue"
```

Copyright (c) 2026 William Watson. MIT License.
