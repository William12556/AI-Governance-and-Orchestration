Created: 2026 November 14

```yaml
change_info:
  id: "change-541f5c58"
  title: "Scripts and documents: bootstrap refuses an old-layout tarball, propagate.sh gates workspace folder creation, flow-style workspace_folders, single-quoted state_dir, duration-limit text, provider interface in the design (Stage C work item 5C)"
  date: "2026-11-14"
  status: "verified"  # approver: operator (one-time session exemption, 2026-11-14); implemented and verified 2026-11-14
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-541f5c58"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-541f5c58"
  description: "Remediate dev/task.md work item 5C: work item 5 parts (a) L-19, (b), (d), (e), with the session decisions D1 to D5 of 2026-11-14."

scope:
  summary: >
    (A, d; D1) bootstrap.sh lists the downloaded tarball and refuses it,
    before extracting anything, when it holds no ai/engine/ entry. (B, e;
    D2) propagate.sh lists the workspace folders that are absent in its
    preview; an up-to-date target with none absent exits 0 as before;
    one with absent folders continues through the plan-error check and
    the confirmation, and the folders are created only after them. (C,
    e; D3) The workspace_folders parser of bootstrap.sh and propagate.sh
    also reads a single-line flow-style list. (D, e; D4)
    migrate-layout.sh strips single quotes from loop.state_dir. (E, b;
    D5) audit-review.yaml no longer names a .complete file containing
    DURATION_LIMIT; guide-engine-operations §5.0 states .timeout and exit
    code 2; ai/profiles/README.md names the Claude Desktop project
    instructions without a link to a gitignored file. (F, a)
    design-14e05e35 §4.1 states the provider interface as built. (G)
    Tests.
  affected_components:
    - { name: "bootstrap", file_path: "bin/bootstrap.sh", change_type: "modify" }  # A, C
    - { name: "propagate", file_path: "bin/propagate.sh", change_type: "modify" }  # B, C
    - { name: "migrate-layout", file_path: "bin/migrate-layout.sh", change_type: "modify" }  # D
    - { name: "audit review recipe", file_path: "ai/governance/software-engineering/recipes/audit-review.yaml", change_type: "modify" }  # E
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # E
    - { name: "profiles index", file_path: "ai/profiles/README.md", change_type: "modify" }  # E
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # F
    - { name: "install guide", file_path: "docs/guide-install.md", change_type: "modify" }  # B, if it states the up-to-date behaviour
    - { name: "script tests", file_path: "tests/engine/test_bin_scripts.py", change_type: "create" }  # G
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["4.1 Interface"] }
  out_of_scope:
    - "Multi-line flow-style workspace_folders lists (documented as not read by the scripts)"
    - "bin/release.sh and bin/migrate-terms.py"
    - "Any change to the provider code (the design is amended, L-19)"
    - "Reviewer behaviour at a duration limit (the engine ends the run before a review)"
    - "The gitignored docs/claude/project_information.md itself"

rational:
  problem_statement: "See issue-541f5c58."
  proposed_solution: "Check the tarball listing before extraction; move folder creation behind the script's existing safeguards and show it in the preview; extend one awk program; widen one sed pattern; correct three documents and one recipe text."
  alternatives_considered:
    - option: "(A) extract to a temporary directory, verify, then move ai/ into the project"
      reason_rejected: "A listing check before extraction gives the same guarantee with one command and no move across file systems"
    - option: "(B) create the folders on the up-to-date path only with --yes"
      reason_rejected: "A second, partial rule; reusing the plan-error check and the confirmation that guard every other write is the audit recommendation (audit-14e05e35 L-10)"
    - option: "(C) document the block-list form only"
      reason_rejected: "manifest.py accepts a flow list; a manifest valid for the engine would still create no folder. The single-line form is a small extension of the awk program; the multi-line form is documented as not read"
    - option: "(E) make the engine write .complete with DURATION_LIMIT"
      reason_rejected: "A change of the state-file contract beyond the finding; .timeout and exit code 2 are tested behaviour (F10)"
  benefits:
    - "A failed bootstrap leaves the project as it was"
    - "propagate.sh writes nothing before its safeguards"
    - "Recipe, guide and design agree with the code"
  risks:
    - risk: "An up-to-date target that lacks a workspace folder now needs --yes or a terminal confirmation (exit 2 otherwise), where it exited 0 before"
      mitigation: "Intended; the message is the script's existing one. The preview names the folders"
    - risk: "The reviewer recipe text changes for audit runs"
      mitigation: "The removed condition could never be observed by the reviewer; coverage and quality criteria are unchanged. Recipe version 1.2.1"

technical_details:
  current_behavior: "See issue-541f5c58 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) bootstrap.sh, after the download: 'tar -tzf' the tarball; when no
    entry is ai/engine/ or begins with ai/engine/, print 'Error: release
    <tag> does not contain ai/engine/ (pre-5bcd46ad layout or damaged
    archive). Nothing installed.' to stderr, remove the temporary
    directory and exit 1. (B) propagate.sh: a function
    workspace_folders_of <manifest> prints the declared folders;
    MISSING_WS holds those absent below the target's ai/workspace/,
    read from the source manifest (the one the copy installs). The
    preview prints 'create       workspace/<folder>/' for each. The
    early 'Target is up to date' exit requires MISSING_WS to be empty.
    Otherwise the run continues: plan-error check (exit 3), confirmation
    rules (--yes, exit 2 without a terminal, prompt), then the existing
    apply steps, which end with create_workspace_folders. (C) The awk
    program in both scripts: a line 'workspace_folders: [a, "b", 'c']'
    yields a, b, c; block lists as before; a flow list that does not
    close on the same line yields nothing. (D) migrate-layout.sh: the
    state_dir pattern accepts a double or single quote on either side.
    (E) audit-review.yaml: the three-line DURATION_LIMIT statement is
    replaced by 'The engine ends the run itself when a duration limit is
    reached; do not relax the coverage check for it.'; 'unless duration
    limit has been reached' and '(or duration limit reached)' are
    removed; version 1.2.1. guide-engine-operations §5.0: the
    duration-limit row reads '.complete not written; .timeout holds
    TIMEOUT: iteration N; exit code 2'. ai/profiles/README.md §4.0: the
    Claude Desktop row names 'Claude Desktop project instructions (kept
    locally; not distributed)' and the planner primer
    ai/governance/software-engineering/primer.md as the tracked
    reference. (F) design-14e05e35 §4.1: complete(model, messages,
    tools, max_tokens=None) -> Completion; await_ready(model, timeout,
    interval, echo) -> None, raising ProviderError when not ready;
    live_context_window(model) -> int | None; redact(text) -> str;
    Completion.reasoning_content.
  implementation_approach: "Implemented by the autonomous session of 2026-11-14 (worker and reviewer; prompt-cf99f3f3) on the session branch. No T03 prompt (report-b3a503a2 §5.0 decision 1); the acceptance criteria are testing_requirements below."
  code_changes:
    - component: "bootstrap"
      file: "bin/bootstrap.sh"
      change_summary: "A listing check before extraction; C flow-style list"
      functions_affected: ["main script", "create_workspace_folders"]
    - component: "propagate"
      file: "bin/propagate.sh"
      change_summary: "B preview and gating of workspace folder creation; C flow-style list"
      functions_affected: ["workspace_folders_of (new)", "create_workspace_folders", "preview"]
    - component: "migrate-layout"
      file: "bin/migrate-layout.sh"
      change_summary: "D single-quoted state_dir"
      functions_affected: ["plan"]
  interface_changes:
    - interface: "bin/propagate.sh on an up-to-date target with absent workspace folders"
      change_type: "behavior"
      details: "Preview line per folder; plan-error check and confirmation apply; exit 2 without --yes and without a terminal"
      backward_compatible: "no for unattended runs without --yes in that state, which created the folders and exited 0"
    - interface: "bin/bootstrap.sh"
      change_type: "behavior"
      details: "Exit 1 before extraction for a tarball without ai/engine/"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "bash, awk, sed, tar, rsync and curl as before" }

testing_requirements:
  test_approach: "pytest running the scripts with bash in tmp_path; bootstrap.sh with a curl stand-in on PATH that serves a local tarball; propagate.sh from a copy of bin/ and ai/ in tmp_path. No network (NFR-06). Where rsync is not installed, a no-op stand-in is used: in the tested state the target is up to date and the copy has nothing to transfer."
  test_cases:
    - { scenario: "T1 (A): bootstrap.sh with a tarball that has ai/ but no ai/engine/; test_t1_bootstrap_refuses_a_tarball_without_engine", expected: "exit 1; the message names ai/engine/; the project has no ai/" }
    - { scenario: "T2 (A, C): bootstrap.sh with a new-layout tarball whose manifest uses a block list, and one with a single-line flow list; test_t2_bootstrap_installs_and_creates_workspace_folders[block|flow]", expected: "exit 0; ai/config.yaml seeded; every declared folder exists" }
    - { scenario: "T3 (B): propagate.sh on an up-to-date target with one workspace folder removed: without --yes and without a terminal; with --yes; and with nothing absent; test_t3_propagate_gates_workspace_folder_creation", expected: "exit 2 and the folder still absent, with the preview line; exit 0 and the folder created; 'Target is up to date' and exit 0" }
    - { scenario: "T4 (B): the same target with ai-local/RELOCATED.md as a directory (a plan error) and --yes; test_t4_propagate_plan_error_precedes_folder_creation", expected: "exit 3; the folder still absent" }
    - { scenario: "T5 (C): propagate.sh from a framework copy whose manifest uses a single-line flow list; test_t5_propagate_reads_a_flow_style_list", expected: "the declared folders are created" }
    - { scenario: "T6 (D): migrate-layout.sh (plan only) with state_dir: 'ai/state', 'custom/state' and \"custom/state\"; test_t6_migrate_layout_reads_single_quoted_state_dir", expected: "no warning for 'ai/state'; the warning names custom/state without quotes in both other cases" }
    - { scenario: "T7 (E): audit-review.yaml; test_t7_audit_review_recipe_has_no_duration_limit_marker", expected: "valid YAML, version 1.2.1, no 'DURATION_LIMIT'; the guide has no 'DURATION_LIMIT'" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline on Linux; macOS suite run by the operator after the session (bash 3.2 and BSD awk, sed and tar apply there)"
    - "Mutations: listing check removed (T1); early exit without the MISSING_WS condition (T3, T4); flow-style branch removed in each script (T2, T5); single quote removed from the pattern (T6)"
    - "bash -n on the three scripts"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "Follow-up audit by an independent session (P02.8.2): deferred to the operator"

implementation:
  effort_estimate: "2 hours"
  implementation_steps:
    - { step: "Failing tests, then scripts and documents", owner: "session (worker)" }
    - { step: "Independent review (prompt-cf99f3f3 §8.4)", owner: "session (fresh reviewer subagent)" }
    - { step: "macOS suite; follow-up audit (P02.8.2)", owner: "operator, after the session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "bootstrap.sh is fetched from main; the change takes effect at the merge. propagate.sh and migrate-layout.sh run from the framework repository. The recipe and the guide propagate with work item 8e."

traceability:
  related_changes:
    - { change_ref: "change-e58fd295", relationship: "follows up (workspace folder creation)" }
    - { change_ref: "change-5bcd46ad", relationship: "follows up (audit-5bcd46ad L-12, H-01 option)" }
    - { change_ref: "change-53c6f252", relationship: "follows up (provider interface; audit-caab2052 L-19)" }
  related_issues:
    - { issue_ref: "issue-541f5c58", relationship: "source" }

notes: "Session decisions 2026-11-14 under the operator's one-time exemption (prompt-cf99f3f3 §1.0 item 5): D1 listing check before extraction; D2 folder creation behind the plan-error check and the confirmation, shown in the preview; D3 single-line flow lists read, multi-line flow lists documented as not read; D4 either quote stripped; D5 the documents and the recipe follow the engine (.timeout, exit code 2), the engine is not changed."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Approved as drafted. Approver: operator (one-time session exemption, 2026-11-14)"]
  - version: "1.2"
    date: "2026-11-14"
    changes:
      - "Implemented on branch claude/blissful-keller-mn2avc from fd7f4cc: scripts and recipe 1a1b1cd, tests ff11a94 (report-541f5c58 v1.0). Status implemented"
      - "812 passed, 4 skipped at fd7f4cc; 824 passed, 4 skipped after (Linux; 12 new cases). Mutations M1 to M5 caught. bash -n passes"
      - "linter.py dev 0 errors, 113 warnings; protocol_checker.py dev 0 errors, 20 warnings"
      - "guide-engine-operations v1.35 §5.0; ai/profiles/README.md v1.16 §4.0; design-14e05e35 v1.32 §4.1 (await_ready raises TimeoutError or ProviderError); docs/guide-install.md v0.14 §3.3"
  - version: "1.3"
    date: "2026-11-14"
    changes:
      - "Review by a fresh reviewer subagent (prompt-cf99f3f3 §8.4): round 1 REVISE (a flow list was cut at the last closing bracket; baseline facts in the report), corrected in e4e7e99 (scripts), 9f35a03 (tests) and report-541f5c58 v1.1; round 2 SHIP. Not an audit"
      - "Added by the review: a flow list ends at its first closing bracket; an archive that tar cannot list is refused with the same message as one without ai/engine/"
      - "Status verified; closed with issue-541f5c58 and report-541f5c58 (P00.14.4). Approver: operator (one-time session exemption, 2026-11-14)"
      - "Linux cloud suite 858 passed, 4 skipped (with the tests of change-6d40f0dd); macOS operator suite (bash 3.2, BSD awk, sed and tar) and P02.8.2 follow-up audit deferred to after the session (report-b3a503a2 §6.0)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
