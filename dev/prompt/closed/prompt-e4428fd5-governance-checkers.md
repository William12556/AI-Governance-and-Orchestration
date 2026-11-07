Created: 2026 November 7

```yaml
prompt_info:
  id: "prompt-e4428fd5"
  task_type: "debug"
  source_ref: "change-e4428fd5"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-07"
  iteration: 1
  coupled_docs:
    change_ref: "change-e4428fd5"
    change_iteration: 1

context:
  purpose: >
    Make the governance checkers validate every governance document by
    its class: schema_type uses class words, numbered values of both
    schemes are aliases, an absent schema_type is inferred from a unique
    root key, an unknown value is warned. Report malformed YAML values as
    findings instead of raising. Treat the self-containment check of
    closed prompts as a warning. Add the terminal test status superseded.
    Add test modules for both checkers. Remediates issue-e4428fd5
    (audit-caab2052 M-03, L-11 and group 3 tests; audit-eb782f83 F-04)
    with the operator decisions of 2026-11-05 and 2026-11-07.
    AMENDMENT 1 (2026-11-07): FR-A1 to FR-E are implemented and merged
    (44e3e04, be4cbbb, bc4563b, 7c1907a; report-e4428fd5 v1.0). The first
    implementation stopped because root-key inference validated closed
    documents without schema_type for the first time (6 linter and 16
    protocol errors on dev/). This amendment implements FR-A4 only:
    inference is limited to documents outside closed/ whose file name
    class matches the root key (operator decision 2026-11-07, option V3;
    change-e4428fd5 v1.2).
  integration: >
    ai/engine/src/linter.py validates document structure, YAML fields
    (check_yaml), coupling (check_coupling) and links, keyed on
    metadata.schema_type through the tables _ENUMS, _ID_FIELDS,
    _ITER_FIELDS and _COUPLING (linter.py:46-111 at 12222b3).
    ai/engine/src/protocol_checker.py imports Finding, _extract_yaml, _get
    and the name patterns from linter, loads documents in load_workspace
    (:111-142) and runs the protocol checks, keyed through
    _TERMINAL_STATUS, _STATUS_FIELD, _ID_FIELD, _COUPLING_PAIRS and
    MANDATORY_BACK (:33-80, :188). Both are run as 'python3
    ai/engine/src/<checker>.py <workspace dir>'. ai/engine/src/manifest.py
    validates the governance model manifest (stage gates at :184-189).
    Templates live in ai/governance/software-engineering/templates/.
    Line numbers are at main 12222b3; locate code by the quoted text if
    lines have moved.
  knowledge_references:
    - "dev/change/change-e4428fd5-governance-checkers.md (approved scope, v1.1)"
    - "dev/issue/issue-e4428fd5-governance-checkers.md"
    - "dev/audit/audit-caab2052-static-code-2026-10-27.md M-03, L-11, §10.0, §14.0 (fixture description in §2.0)"
    - "ai/governance/software-engineering/governance.md P00.14.3, Appendix A.5"
    - "CLAUDE.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No network other than package installation."
    - "Code changes are limited to ai/engine/src/linter.py, ai/engine/src/protocol_checker.py, ai/engine/src/manifest.py, the templates T01-requirements.md, T02-design.md and T04-test.md to T08-audit.md in ai/governance/software-engineering/templates/, the new tests/engine/test_linter.py and tests/engine/test_protocol_checker.py, and tests/engine/test_manifest_gates.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit any document in dev/ other than the report and this prompt's move, any closed/ directory, governance.md, manifest.yaml, T03-prompt.md, ai/engine/doc/, README files or dev/task.md; the planner updates governance.md and manifest.yaml after review."
    - "No new dependencies. Standard library and PyYAML only."
    - "Keep every existing finding message unchanged except where an FR states new text."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."
    - "Amendment 1 scope: code changes are limited to ai/engine/src/linter.py, ai/engine/src/protocol_checker.py, tests/engine/test_linter.py and tests/engine/test_protocol_checker.py. Governance changes are limited to updating dev/reports/report-e4428fd5-governance-checkers.md (new version, Amendment 1 results) and moving this prompt to dev/prompt/closed/. FR-A1 to FR-E are already implemented; do not change them except as FR-A4 states."

specification:
  description: "Five changes, FR-A1 to FR-E, with the tests listed under testing.unit_tests."
  requirements:
    functional:
      - "FR-A1 (class resolver) In linter.py add CLASS_WORDS = ('requirements', 'design', 'prompt', 'test', 'result', 'issue', 'change', 'audit'), ROOT_KEYS = {'prompt_info': 'prompt', 'test_info': 'test', 'result_info': 'result', 'issue_info': 'issue', 'change_info': 'change', 'audit_info': 'audit'} and resolve_class(data: dict) -> tuple[str | None, str | None] returning (class, message). With metadata.schema_type present: a str that is a class word gives that class; a str matching ^t0[1-8]_(requirements|design|prompt|test|result|issue|change|audit)$ gives the captured class word; any other str gives (None, \"unknown schema_type '<value>'\"); a non-str gives (None, 'metadata.schema_type must be a string'). With schema_type absent: the class of the first top-level key of data that is in ROOT_KEYS, or (None, 'YAML block present but metadata.schema_type is missing') when none is. Comment: change-e4428fd5 (audit-caab2052 M-03; operator decisions 2026-11-05, 2026-11-07)."
      - "FR-A2 (tables by class word) Re-key _ENUMS, _ID_FIELDS, _ITER_FIELDS and _COUPLING in linter.py, and _TERMINAL_STATUS, _STATUS_FIELD, _ID_FIELD, _COUPLING_PAIRS, MANDATORY_BACK and the class tests in check_status_consistency and check_prompt_self_contained in protocol_checker.py, by class word (t02_change -> change, t03_issue -> issue, t04_prompt -> prompt, t05_test -> test, t06_result -> result). check_yaml uses resolve_class: a message from it is a WARN finding (the missing-schema_type message keeps its text) and the function returns (findings, data, None); a resolved class is returned in place of the raw value. The missing metadata.template_version warning is given only when metadata.schema_type is present (a prompt whose class was inferred gets no template_version warning). A resolved class without rules (requirements, design, audit) gives no finding. run() and the coupling pass use the resolved class. protocol_checker imports resolve_class from linter; load_workspace uses it and skips a document whose class is None, without a finding (linter reports it); WorkspaceDoc.schema_type holds the class word. Comments: change-e4428fd5 (audit-caab2052 M-03)."
      - "FR-A3 (templates) In T01-requirements.md, T02-design.md, T04-test.md, T05-result.md, T06-issue.md, T07-change.md and T08-audit.md: the template's metadata.schema_type value becomes the class word (requirements, design, test, result, issue, change, audit), and the schema_type enum in the template's schema section lists the class word only. Add a version-history row to each template ('change-e4428fd5: schema_type class word'). T03-prompt.md is not changed."
      - "FR-B (closed prompts) In check_prompt_self_contained, when doc.in_closed the three findings are WARN instead of ERROR and their messages end with ' (closed record)'. No other check changes severity. Comment: change-e4428fd5 (operator decision 2026-11-07)."
      - "FR-C (audit-caab2052 L-11; type checks) No check in linter.py, protocol_checker.py or manifest.py raises for any YAML value shape. In detail: (1) a YAML block whose top level is not a mapping gives the linter ERROR 'YAML block top level must be a mapping' and is skipped by protocol_checker; (2) check_yaml: an id that is not a str gives ERROR \"'<id path>' must be a string\"; an enum field whose value is not a str gives ERROR \"'<field path>' value must be a string\" (in place of the membership test); (3) check_coupling: a reference that is not a str gives ERROR \"'<ref path>' must be a string\"; (4) protocol_checker: load_workspace skips a document whose id is not a str; _uuid_from_id returns None for a non-str; every coupling check and check_status_consistency skip a reference or status that is not a str (linter reports it); (5) manifest.py: a stage gates entry that is not a str raises ManifestError for '<stage>.gates' with 'entries must be strings', before the membership test. Comments: change-e4428fd5 (audit-caab2052 L-11)."
      - "FR-D (superseded) The test status enum gains 'superseded': linter _ENUMS['test']['test_info.status'], protocol_checker _TERMINAL_STATUS['test'] = frozenset({'passed', 'superseded'}), T04-test.md (the status comment on the template's status line and the schema enum for test_info.status). Comment: change-e4428fd5 (GTach observation 2026-10-08)."
      - "FR-E (tests) New tests/engine/test_linter.py and tests/engine/test_protocol_checker.py as listed under testing; one case in tests/engine/test_manifest_gates.py for FR-C (5)."
      - "FR-A4 (Amendment 1; operator decision 2026-11-07, option V3) resolve_class gains an optional parameter path: str | None = None. When schema_type is absent and path is given, the root-key class is used only when (1) no component of the path is 'closed' and (2) the file name's prefix before the first '-' equals that class (prompt-<...>.md with prompt_info gives prompt; proposal-<...>.md with change_info gives no class). Otherwise the result is (None, MISSING_SCHEMA_TYPE), as before the change. With path None (direct calls, for example from tests) the root-key rule applies without the two conditions. check_yaml passes its path; protocol_checker.load_workspace passes its path. Documents with schema_type present are unaffected. The corpus test test_checkers_complete_on_dev_corpus asserts that each checker reports 0 errors on dev/. Comment: change-e4428fd5 amendment 1 (operator decision 2026-11-07)."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-e4428fd5 and the finding ID at each change site"

design:
  architecture: "No new modules in ai/. One shared resolver in linter.py used by protocol_checker.py."
  components:
    - name: "linter.resolve_class"
      type: "function"
      purpose: "Resolve a governance document's class from schema_type or its root key"
      interface:
        inputs: [{ name: "data", type: "dict", description: "parsed first YAML block" }]
        outputs: { type: "tuple[str | None, str | None]", description: "(class word, message); message set when class is None" }
        raises: []
      logic: ["class word", "numbered alias ^t0[1-8]_<class>$", "unknown or non-str value", "absent: first top-level key in ROOT_KEYS"]
  dependencies:
    internal: ["linter", "protocol_checker", "manifest"]
    external: ["re", "yaml"]

error_handling:
  strategy: "Every malformed value becomes a finding (checkers) or a ManifestError (manifest loader); no TypeError escapes."
  logging:
    level: "Not applicable (findings are printed by the checkers)"

testing:
  unit_tests:
    - { scenario: "A1 (test_linter.py): resolve_class for the 8 class words, the 15 numbered values (t01_design, t02_change, t03_issue, t04_prompt, t05_test, t06_result, t07_requirements, t08_audit, t01_requirements, t02_design, t03_prompt, t04_test, t05_result, t06_issue, t07_change), 't09_change', 'Change', 'change ', 'foo', a list; absent schema_type with each ROOT_KEYS key, with project_info and with no known key", expected: "class word for the 23 accepted spellings and the six root keys; None with the stated message otherwise" }
    - { scenario: "A2a: a change document with four defects (invalid status, invalid priority, id not matching the pattern, iteration 0) as t02_change, t07_change and change", expected: "the same four ERROR findings for each spelling" }
    - { scenario: "A2b: one valid and one defective issue, test and result document in each accepted spelling", expected: "same findings per spelling" }
    - { scenario: "A2c: a design, a requirements and an audit document with valid schema_type", expected: "no finding about schema_type" }
    - { scenario: "A2d: a prompt with prompt_info and no metadata", expected: "no missing-schema_type and no template_version warning; prompt coupling and protocol prompt checks applied" }
    - { scenario: "A2e: a document with schema_type 'foo'", expected: "WARN with the message unknown schema_type 'foo'; no field checks" }
    - { scenario: "A3: every template file", expected: "T01, T02, T04 to T08 metadata.schema_type is a class word and the schema enum lists only that word; T03 has no schema_type and resolve_class gives prompt" }
    - { scenario: "B (test_protocol_checker.py): a prompt with empty specification.description and empty design.components in prompt/ and in prompt/closed/", expected: "ERROR active; WARN ending '(closed record)' closed" }
    - { scenario: "B2: a closed change with status 'closed' (invalid enum) and an issue in issue/closed/ with status 'open'", expected: "linter ERROR and protocol lifecycle finding with unchanged severity" }
    - { scenario: "C: schema_type, id, an enum field, a coupling reference and a status each as a list, a mapping and an int; a YAML block that is a list; a manifest stage gates list holding a mapping (test_manifest_gates.py)", expected: "findings with the stated texts or ManifestError naming the field; no exception from either checker or the manifest loader" }
    - { scenario: "D: a test document with status superseded in test/closed/; with status executed in test/closed/; with superseded in test/", expected: "closed superseded: no finding; closed executed: lifecycle finding as today; active superseded: the existing terminal-status-in-active-folder finding" }
    - { scenario: "E (one test per check, each with a minimal defective fixture and a valid one): linter naming, structure (table of contents, version history), yaml, coupling (missing, not found, iteration mismatch), links; protocol uuid_chain, bidirectional (mandatory and optional back-reference), one_to_one, status_consistency, lifecycle_placement, prompt_self_contained", expected: "each check fires on its defective fixture and is silent on the valid one" }
    - { scenario: "Corpus: run both checkers on dev/ (subprocess, as an operator would)", expected: "0 errors from each; record warning counts before and after in the report" }
    - { scenario: "AM1 (Amendment 1): resolve_class with prompt_info and no schema_type for path prompt/prompt-x.md, prompt/closed/prompt-x.md, and None", expected: "prompt; (None, missing-schema_type message); prompt" }
    - { scenario: "AM2: a proposal file proposals/proposal-x.md containing a change_info block without schema_type, through check_yaml and load_workspace", expected: "no change rules applied; the missing-schema_type warning from linter; skipped by protocol_checker" }
    - { scenario: "AM3: a closed change without schema_type and with status 'closed' (as change-3b9e6d72)", expected: "no enum, lifecycle or status_consistency error; the missing-schema_type warning as before the change" }
    - { scenario: "AM4: an active prompt without metadata and with an empty specification.description", expected: "prompt checks applied: self-containment ERROR" }
  edge_cases:
    - "Use tmp_path workspaces; no network."
    - "Name fixtures with the document naming patterns the checkers accept (MASTER_RE, NORMAL_RE)."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; python3 ai/engine/src/linter.py dev; python3 ai/engine/src/protocol_checker.py dev; record counts and findings per check."
    - "After the change: the same commands; no new test failures; all new tests pass; both checkers report 0 errors on dev/."
    - "Mutation check (not committed), each on a temporary copy: (M1) remove the numbered-alias rule: A2a fails; (M2) remove root-key inference: A2d fails; (M3) give the template_version warning for inferred classes: A2d fails; (M4) remove the closed downgrade in check_prompt_self_contained: B fails; (M5) apply the downgrade to every protocol check: B2 fails; (M6) remove the enum type check: C fails; (M7) remove the manifest gates type check: C fails; (M8) remove superseded from _TERMINAL_STATUS: D fails; (M9) key one linter table back to t02_change: A2a fails. Record results."
    - "Amendment 1 mutations (not committed): (M10) drop the closed/ condition: AM1 and the corpus test fail; (M11) drop the file-name condition: AM2 fails; (M12) check_yaml stops passing its path: AM1 through check_yaml or AM3 fails. Record results in the updated report."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-e4428fd5-governance-checkers.md dev/prompt/closed/; leave the issue and change documents active"
    - "Amendment 1: update the existing report to version 1.1 with a new section '8.0 Amendment 1' (files and functions changed, baseline and final test counts, new tests, mutations M10 to M12, both checkers on dev/ with counts per check before and after) and a Version History row; keep sections 1.0 to 7.0 unchanged except a one-line pointer to §8.0 in §1.0"
    - "Commits: Conventional Commits; checker and manifest source as fix(engine), templates as fix(governance), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/linter.py", content: "modified (FR-A1, FR-A2, FR-C, FR-D)" }
    - { path: "ai/engine/src/protocol_checker.py", content: "modified (FR-A2, FR-B, FR-C, FR-D)" }
    - { path: "ai/engine/src/manifest.py", content: "modified (FR-C)" }
    - { path: "ai/governance/software-engineering/templates/T01-requirements.md, T02-design.md, T04-test.md, T05-result.md, T06-issue.md, T07-change.md, T08-audit.md", content: "modified (FR-A3; FR-D in T04)" }
    - { path: "tests/engine/test_linter.py", content: "new (FR-E)" }
    - { path: "tests/engine/test_protocol_checker.py", content: "new (FR-E)" }
    - { path: "tests/engine/test_manifest_gates.py", content: "modified (FR-C (5))" }
    - path: "dev/reports/report-e4428fd5-governance-checkers.md"
      content: >
        New file in Obsidian-compatible GitHub Flavored Markdown, laid out as
        README.md: unnumbered H1 title followed by the line 'Created: <year>
        <month> <day>'; unnumbered '## Table of Contents' as a bulleted list
        of the H2 sections linked by GitHub heading slugs (for example
        [1.0 Summary](#10-summary)); numbered sections; '---' between
        sections; '[Return to Table of Contents](#table-of-contents)' at the
        end of each section except Version History; Version History table;
        final '---' and the line 'Copyright (c) 2026 William Watson. MIT
        License.'. Sections: 1.0 Summary; 2.0 Files changed (with
        functions); 3.0 Test results (baseline and final counts, new test
        names, mutation results); 4.0 Governance checks (both checkers on
        dev/ before and after, counts per check and the new findings
        listed); 5.0 Deviations from this prompt (or 'None'); 6.0 Open
        points for the planner; 7.0 Session branch, starting commit and
        commit hashes.

success_criteria:
  - "FR-A1 to FR-E implemented as specified; all new tests present and passing"
  - "Mutations M1 to M9 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "Both checkers report 0 errors on dev/"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates governance.md P00.14.3 and Appendix A.5 and the governance version to 12.9 in governance.md and manifest.yaml after review."
```

Copyright (c) 2026 William Watson. MIT License.
