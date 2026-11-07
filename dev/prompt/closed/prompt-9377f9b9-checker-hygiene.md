Created: 2026 November 7

```yaml
prompt_info:
  id: "prompt-9377f9b9"
  task_type: "debug"
  source_ref: "change-9377f9b9"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-07"
  iteration: 1
  coupled_docs:
    change_ref: "change-9377f9b9"
    change_iteration: 1

context:
  purpose: >
    Make the governance checkers report a first YAML block that does not
    parse or nests too deeply, instead of skipping it or raising; decide
    'closed' below the workspace directory for class inference; reject a
    boolean iteration; map deeply nested YAML in the manifest loader to a
    ManifestError; and close the checker test gaps left by
    audit-e4428fd5. Remediates issue-9377f9b9 (dev/task.md work item 5
    parts (g), (j), (k), (l) and work item 6 (d)) with the operator
    decisions of 2026-11-07 (D1 to D5).
  integration: >
    ai/engine/src/linter.py: _extract_yaml (:166-174) parses the first
    fenced YAML block and returns None on yaml.YAMLError; resolve_class
    (:206-245) tests every component of the given path for 'closed';
    check_yaml(path, content) (:307-376) returns when data is None,
    passes the full path to resolve_class (:329) and checks iteration
    with isinstance(iter_val, int) (:372); run(workspace_dir) (:467-508)
    calls check_yaml(path, content) for each governance document.
    ai/engine/src/protocol_checker.py imports _extract_yaml and
    resolve_class from linter; load_workspace (:124-160) computes
    in_closed relative to the workspace (:140), skips a document whose
    data is not a dict, and passes the full path to resolve_class
    (:152). ai/engine/src/manifest.py load_manifest (:120-127) catches
    OSError and yaml.YAMLError. Line numbers are at main 0a79ff0; locate
    code by the quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-9377f9b9-checker-hygiene.md (scope and proposed behaviour)"
    - "dev/issue/issue-9377f9b9-checker-hygiene.md"
    - "dev/audit/audit-e4428fd5-followup-2026-11-07.md F-01 to F-04, F-08, §6.0 (X01, X06, X11, X18, X19, X25)"
    - "ai/governance/software-engineering/governance.md Appendix A.5"
    - "CLAUDE.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No network other than package installation."
    - "Code changes are limited to ai/engine/src/linter.py, ai/engine/src/protocol_checker.py, ai/engine/src/manifest.py, tests/engine/test_linter.py, tests/engine/test_protocol_checker.py and tests/engine/test_manifest_gates.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit any other document in dev/, any closed/ directory, governance.md, manifest.yaml, the templates, ai/engine/doc/, README files or dev/task.md; the planner updates governance.md and manifest.yaml after review."
    - "No new dependencies. Standard library and PyYAML only."
    - "Keep every existing finding message unchanged except where an FR states new text."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."
    - "Stop condition: if either checker reports an error on dev/ after the change, do not edit dev/; record the findings in report §4.0 and §6.0 and stop."

specification:
  description: "Five changes, FR-01 to FR-05, with the tests listed under testing.unit_tests."
  requirements:
    functional:
      - "FR-01 (work item 5 (k), (g); D1) In linter.py add _parse_yaml_block(content: str) -> tuple[object | None, str | None]: no fenced YAML block gives (None, None); a block that loads gives (data, None); yaml.YAMLError e gives (None, problem) with problem = e.problem when it is a non-empty str, else the first line of str(e); RecursionError gives (None, 'nesting too deep'). _extract_yaml(content) returns the first element of _parse_yaml_block(content), so it never raises; protocol_checker.load_workspace keeps skipping a document whose data is not a dict. Comment: change-9377f9b9 (audit-e4428fd5 F-01, F-02)."
      - "FR-02 (work item 5 (k); D1) check_yaml(path, content, workspace_dir: str | None = None) uses _parse_yaml_block. With a problem it returns ([finding], None, None), the finding having check 'yaml' and the message 'YAML block does not parse: <problem>'. Severity: WARN with the message suffix ' (closed record)' when any component of the location path is 'closed', otherwise ERROR. The location path is os.path.relpath(path, workspace_dir) when workspace_dir is given, else path; split components on both '/' and '\\\\'. run(workspace_dir) passes workspace_dir to check_yaml. Without a problem, check_yaml behaves as today except FR-03 and FR-04."
      - "FR-03 (work item 5 (j); D2) check_yaml passes resolve_class the location path of FR-02 instead of path. protocol_checker.load_workspace passes os.path.relpath(path, workspace_dir) to resolve_class. resolve_class is unchanged. Comment: change-9377f9b9 (report-e4428fd5 §8.6 item 2)."
      - "FR-04 (work item 5 (l); D4) In check_yaml the iteration check rejects a bool value: 'isinstance(iter_val, bool) or not isinstance(iter_val, int) or iter_val < 1' gives the existing ERROR text \"iteration must be integer ≥ 1, got '<value>'\". Comment: change-9377f9b9 (audit-e4428fd5 F-08)."
      - "FR-05 (work item 5 (g); D3) manifest.load_manifest: 'except RecursionError' raises ManifestError(f'{path}: invalid YAML: nesting too deep') from the exception. Comment: change-9377f9b9 (audit-e4428fd5 F-01)."
      - "FR-06 (tests; D5) Add the cases under testing.unit_tests to tests/engine/test_linter.py, tests/engine/test_protocol_checker.py and tests/engine/test_manifest_gates.py."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on new or changed signatures; docstrings in the existing module style"
        - "Comments referencing change-9377f9b9 and the finding ID at each change site"

design:
  architecture: "No new modules. One new helper in linter.py; small changes in three existing functions and one manifest exception handler."
  components:
    - name: "linter._parse_yaml_block"
      type: "function"
      purpose: "Parse the first fenced YAML block and report why it does not parse"
      interface:
        inputs: [{ name: "content", type: "str", description: "markdown document text" }]
        outputs: { type: "tuple[object | None, str | None]", description: "(data, problem); problem set when a block is present and does not parse" }
        raises: []
      logic: ["no block: (None, None)", "yaml.safe_load", "YAMLError: problem text", "RecursionError: 'nesting too deep'"]
    - name: "linter.check_yaml"
      type: "function"
      purpose: "Validate the first YAML block; report a parse problem by location"
      interface:
        inputs: [{ name: "path, content, workspace_dir", type: "str, str, str | None", description: "workspace_dir optional" }]
        outputs: { type: "tuple[list[Finding], dict | None, str | None]", description: "unchanged" }
        raises: []
      logic: ["location path relative to workspace_dir", "parse problem: ERROR, or WARN (closed record) under closed", "resolve_class with the location path", "bool iteration rejected"]
  dependencies:
    internal: ["linter", "protocol_checker", "manifest"]
    external: ["os", "re", "yaml"]

testing:
  unit_tests:
    - { scenario: "T1 (FR-01, FR-02): a change document whose first YAML block is 'change_info: [' at change/change-<uuid>-x.md and at change/closed/change-<uuid>-x.md, through linter.run and protocol_checker.run", expected: "linter: one 'yaml' finding starting 'YAML block does not parse: ', ERROR active, WARN ending ' (closed record)' closed; protocol_checker: no finding for the document and no exception" }
    - { scenario: "T2 (FR-01, FR-02): the same with a first YAML block nested 5,000 levels (for example 'a:' followed by 5,000 nested '[' or mapping levels)", expected: "message 'YAML block does not parse: nesting too deep' with the same severities; both run() calls return normally" }
    - { scenario: "T3 (FR-01): _parse_yaml_block on text without a fenced block, with a valid block, with an invalid block", expected: "(None, None); (data, None); (None, non-empty problem)" }
    - { scenario: "T4 (FR-03): a workspace at <tmp>/closed/ws: an active prompt prompt/prompt-<uuid>-x.md without metadata and with an empty specification.description; an active change change/change-<uuid>-x.md without schema_type", expected: "protocol_checker: the self-containment ERROR for the prompt; linter: change rules applied to the change (for example an invalid status gives the enum ERROR)" }
    - { scenario: "T5 (FR-04): a change document with iteration true and with iteration false", expected: "the iteration ERROR for each" }
    - { scenario: "T6 (FR-05, test_manifest_gates.py): load_manifest on a manifest.yaml nested 5,000 levels", expected: "ManifestError whose text contains the path and 'invalid YAML: nesting too deep'" }
    - { scenario: "T7 (6 (d), X01): resolve_class with schema_type 't02_changes'", expected: "None and \"unknown schema_type 't02_changes'\"" }
    - { scenario: "T8 (6 (d), X06): resolve_class with prompt_info and no schema_type for prompt/enclosed/prompt-x.md and prompt/prompt-1a2b3c4d-closed-loop.md", expected: "prompt for both" }
    - { scenario: "T9 (6 (d), X18, X19): check_status_consistency with change 'implemented' and issue status ['resolved']; with change status ['implemented'] and issue 'open'", expected: "no status_consistency finding and no exception for either" }
    - { scenario: "T10 (6 (d), X25): the closed self-containment fixture with deliverable.files empty as well", expected: "the deliverable.files finding as WARN ending ' (closed record)'" }
    - { scenario: "T11 (6 (d), X11): a change id of [] and of 0", expected: "\"'change_info.id' must be a string\" ERROR for each" }
    - { scenario: "Corpus: both checkers on dev/ (the existing corpus tests)", expected: "0 errors; linter WARN 'YAML block does not parse' for prompt/closed/prompt-5e8aea4f-loop-robustness-followup.md and prompt/closed/prompt-711a57d5-loop-robustness.md" }
  edge_cases:
    - "Use tmp_path workspaces; no network."
    - "Name fixtures with the document naming patterns the checkers accept (MASTER_RE, NORMAL_RE)."
    - "Build deeply nested YAML in the test (for example '[' * 5000 + ']' * 5000) rather than storing it in a file in the repository."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; python3 ai/engine/src/linter.py dev; python3 ai/engine/src/protocol_checker.py dev; record counts."
    - "After the change: the same commands; no new test failures; all new tests pass; both checkers report 0 errors on dev/; list the linter warnings added and removed."
    - "Mutation check (not committed), each on a temporary copy: (M1) _parse_yaml_block does not catch RecursionError: T2 fails; (M2) check_yaml ignores the problem: T1 fails; (M3) closed severity ERROR: T1 or the corpus test fails; (M4) active severity WARN: T1 fails; (M5) check_yaml passes the full path to resolve_class: T4 fails; (M6) load_workspace passes the full path: T4 fails; (M7) bool iteration accepted: T5 fails; (M8) load_manifest does not map RecursionError: T6 fails. Record results."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-9377f9b9-checker-hygiene.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; checker and manifest source as fix(engine), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/linter.py", content: "modified (FR-01 to FR-04)" }
    - { path: "ai/engine/src/protocol_checker.py", content: "modified (FR-03)" }
    - { path: "ai/engine/src/manifest.py", content: "modified (FR-05)" }
    - { path: "tests/engine/test_linter.py", content: "modified (FR-06)" }
    - { path: "tests/engine/test_protocol_checker.py", content: "modified (FR-06)" }
    - { path: "tests/engine/test_manifest_gates.py", content: "modified (FR-06)" }
    - path: "dev/reports/report-9377f9b9-checker-hygiene.md"
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
        dev/ before and after, warnings added and removed); 5.0 Deviations
        from this prompt (or 'None'); 6.0 Open points for the planner; 7.0
        Session branch, starting commit and commit hashes.

success_criteria:
  - "FR-01 to FR-06 implemented as specified; all new tests present and passing"
  - "Mutations M1 to M8 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "Both checkers report 0 errors on dev/"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates governance.md Appendix A.5 and the governance version to 12.10 in governance.md and manifest.yaml after review."
```

Copyright (c) 2026 William Watson. MIT License.
