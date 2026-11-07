Created: 2026 November 7

```yaml
prompt_info:
  id: "prompt-4b0a5592"
  task_type: "debug"
  source_ref: "change-4b0a5592"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-11-07"
  iteration: 1
  coupled_docs:
    change_ref: "change-4b0a5592"
    change_iteration: 1

context:
  purpose: >
    Track every engine CLI task path that lies in ai/workspace/ by its
    resolved location, whatever its name or file type, so the pre-run
    check refuses anything that is not the approved prompt. Make
    approve.py leave ai/approvals.yaml and its index entry as they were
    when git add or git commit fails, with a non-empty reason. Read
    committed approvals from the project directory when the project is a
    subdirectory of a repository. Remediates issue-4b0a5592
    (audit-caab2052 L-04, L-05, L-06; audit-14e05e35 follow-up 5 F5-01)
    with the operator decisions of 2026-11-07 (D1 to D3).
  integration: >
    ai/engine/src/orchestrator.py main_async derives work_item from the
    task name (_work_item_uuid, :2541-2549), reads the task file once when
    os.path.isfile is true (:2668-2671), sets '_tracked = bool(work_item)
    and ST.is_tracked_task(os.getcwd(), args.task)' (:2672), runs
    ST.prerun_missing in loop and worker mode and exits 3 when anything is
    missing (:2673-2684), and otherwise warns that the prompt is outside
    ai/workspace/ (:2685-2687). ai/engine/src/stages.py is_tracked_task
    (:323-329) requires a regular file; prerun_missing (:365) first calls
    task_document_error, which refuses any task that is not an active
    prompt document of its work item, then refuses a task whose bytes were
    not read; committed_approvals (:124-129) runs git show
    HEAD:ai/approvals.yaml through _git (git --no-optional-locks -C
    <project_root>). ai/engine/src/approve.py approve (:62-85) writes
    ai/approvals.yaml, then runs git add and git commit and returns on the
    first failure. Line numbers are at main 1f02370; locate code by the
    quoted text if lines have moved.
  knowledge_references:
    - "dev/change/change-4b0a5592-approval-tracking.md (scope and proposed behaviour)"
    - "dev/issue/issue-4b0a5592-approval-tracking.md"
    - "dev/audit/audit-caab2052-static-code-2026-10-27.md L-04, L-05, L-06"
    - "dev/audit/closed/audit-14e05e35-followup5-2026-10-01.md F5-01 (cases E-3h, E-3i)"
    - "dev/design/design-14e05e35-engine-generalisation.md §8.3, §8.4"
    - "CLAUDE.md"
  constraints:
    - "Execution environment: Claude Code cloud (Linux container, repository clone). No network other than package installation."
    - "Code changes are limited to ai/engine/src/stages.py, ai/engine/src/orchestrator.py, ai/engine/src/approve.py and tests/engine/test_stages.py. Other existing test files may change only where an assertion depends on behaviour changed by an FR below; record each such change in the report."
    - "Governance changes are limited to: creating the report named in deliverable.files, and moving this prompt to dev/prompt/closed/."
    - "Do not edit any other document in dev/, any closed/ directory, ai/engine/mcp/, ai/webui/, ai/governance/, ai/engine/doc/, README files or dev/task.md; the planner updates design-14e05e35 and guide-engine-operations after review."
    - "No new dependencies. Standard library, PyYAML and the git command only."
    - "Keep every existing console and refusal message unchanged except where an FR states new text."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit before any edit. Commit to the session branch and push it; do not merge into main, open a pull request, force-push or rewrite history."
    - "Stop condition: if any FR conflicts with existing code or tests, or needs a file outside the scope, implement the unaffected FRs, record the conflict in report §5.0 and §6.0, and stop."
    - "Stop condition: if the baseline suite has failures, do not fix them; record them and judge the final run against the baseline."

specification:
  description: "Four changes, FR-01 to FR-04, with the tests listed under testing.unit_tests (FR-05)."
  requirements:
    functional:
      - "FR-01 (L-04, F5-01; D1) stages.is_tracked_task(project_root, task_path) returns True when task_path is non-empty, os.path.exists(task_path) is True (regular file, directory, FIFO or any other type), and os.path.realpath(task_path) equals the resolved ai/workspace/ directory or starts with it followed by os.sep. Symlinks stay resolved (L-01). Otherwise False. Update the docstring: a path inside ai/workspace/ is tracked whatever its name or type. Comment: change-4b0a5592 (audit-caab2052 L-04; audit-14e05e35 F5-01)."
      - "FR-02 (L-04; D1) orchestrator.main_async: '_tracked = ST.is_tracked_task(os.getcwd(), args.task)', independent of work_item. In loop and worker mode a tracked task goes through ST.prerun_missing(os.getcwd(), manifest, work_item or '', args.task, _task_bytes) as today; any missing item exits 3 before any state change. When work_item is None the refusal header is '[engine] task <args.task> is not ready for '<loop stage id>'; missing:' (escaped as the existing header is); with a work item the existing header is unchanged. Keep reading the task file only when os.path.isfile(args.task) is True, so a FIFO is never opened. Keep the 'outside ai/workspace/ — not tracked' warning branch as 'elif work_item and not _tracked'. Comment: change-4b0a5592 (audit-caab2052 L-04)."
      - "FR-03 (L-05; D2) approve.approve: before writing ai/approvals.yaml, record whether it exists and its bytes. When git add or git commit returns non-zero: write the recorded bytes back, or remove the file if it did not exist; then run git -C <project_root> reset -q -- ai/approvals.yaml, and if that returns non-zero (no HEAD), git -C <project_root> rm -q --cached --ignore-unmatch -- ai/approvals.yaml. Return (1, message) with message 'git failed (<add|commit>): <detail>' where detail is the stripped stderr, else the stripped stdout, else 'exit code <n>'. If writing back, removing or the index reset fails, append '; ai/approvals.yaml could not be restored: <reason>'. Keep the existing 'git failed (' prefix and the step name as today ('add --' or 'commit -q' from cmd[3:5]); only the detail fallback and the restoration are new. Comment: change-4b0a5592 (audit-caab2052 L-05)."
      - "FR-04 (L-06; D3) stages.committed_approvals: run git show with f'HEAD:./{APPROVALS_FILE}' so git resolves the path relative to the -C directory. Comment: change-4b0a5592 (audit-caab2052 L-06)."
      - "FR-05 (tests) Add the cases under testing.unit_tests to tests/engine/test_stages.py, reusing its fixtures (project, repo, se, orch) and helpers."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "PEP 8; type hints on changed signatures; docstrings in the existing module style"
        - "Comments referencing change-4b0a5592 and the finding ID at each change site"

design:
  architecture: "No new modules. Changes inside the three existing functions and one branch of main_async."
  components:
    - name: "stages.is_tracked_task"
      type: "function"
      purpose: "Decide whether a CLI task is a tracked work item by its resolved location"
      interface:
        inputs: [{ name: "project_root", type: "str", description: "project directory" }, { name: "task_path", type: "str | None", description: "--task value" }]
        outputs: { type: "bool", description: "True for an existing path at or below ai/workspace/" }
        raises: []
      logic: ["empty or missing path: False", "resolve symlinks", "equal to or below the resolved workspace: True"]
    - name: "approve.approve"
      type: "function"
      purpose: "Record and commit an approval; leave no state behind on a git failure"
      interface:
        inputs: [{ name: "project_root, uuid, stage, manifest, now", type: "as today", description: "unchanged" }]
        outputs: { type: "tuple[int, str]", description: "unchanged codes; failure detail never empty" }
        raises: []
      logic: ["record prior bytes", "write", "git add, git commit", "on failure: restore bytes or remove, reset the index entry, report"]
  dependencies:
    internal: ["stages", "orchestrator", "approve"]
    external: ["os", "subprocess", "git"]

testing:
  unit_tests:
    - { scenario: "T1 (FR-01): is_tracked_task for a regular file, a directory and a FIFO (os.mkfifo) inside ai/workspace/, ai/workspace/ itself, a missing path inside ai/workspace/, a regular file outside, the text 'implement x', and a symlink outside pointing into ai/workspace/", expected: "True for the regular file, directory, FIFO, ai/workspace/ and the symlink; False for the missing path, the outside file and the text" }
    - { scenario: "T2 (FR-02): loop mode and worker mode with --task ai/workspace/prompt/my-task.md (a regular T03 prompt)", expected: "exit 3; the header names the task path; the task_document_error refusal is listed; nothing written to the state directory" }
    - { scenario: "T3 (FR-02): loop mode with --task ai/workspace/notes.md", expected: "exit 3; nothing written to the state directory" }
    - { scenario: "T4 (FR-01, FR-02): loop mode with a directory at ai/workspace/prompt/prompt-<uuid>-x.md, with a FIFO at the same path, and with ai/workspace/ itself as --task", expected: "exit 3 for each; nothing written to the state directory; the FIFO case completes within a test timeout (FIFO not opened)" }
    - { scenario: "T5 (FR-02): loop mode with prompt-<uuid>-x.md outside ai/workspace/", expected: "the existing 'outside ai/workspace/ — not tracked' warning; no exit 3 from the pre-run check" }
    - { scenario: "T6 (FR-03): approve.py with a pre-commit hook that prints 'hook says no' to stderr and exits 1, once with ai/approvals.yaml already committed and once with no ai/approvals.yaml; then the hook removed and approve.py run again", expected: "exit 1 and 'hook says no' in the message; the file bytes equal those before the call, or the file is absent; git status --porcelain -- ai/approvals.yaml is empty; the retry exits 0 and the file holds exactly one entry for the pair" }
    - { scenario: "T7 (FR-03): a pre-commit hook that exits 1 without output", expected: "the message ends 'exit code 1'" }
    - { scenario: "T8 (FR-04): a git repository whose project lies in a subdirectory (repo/sub with ai/ under sub); approve.py run from sub; committed_approvals(sub); prerun_missing for the approved prompt", expected: "the entry is returned; prerun_missing returns []" }
  edge_cases:
    - "Use tmp_path repositories; no network. Configure user.name, user.email and commit.gpgsign=false in each test repository, as the existing fixtures do."
    - "Skip the FIFO cases where os.mkfifo is not available."
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/webui -q; python3 ai/engine/src/linter.py dev; python3 ai/engine/src/protocol_checker.py dev; record counts."
    - "After the change: the same commands; no new test failures; all new tests pass; both checkers report 0 errors on dev/."
    - "Mutation check (not committed), each on a temporary copy: (M1) restore the os.path.isfile requirement in is_tracked_task: T1 or T4 fails; (M2) restore 'bool(work_item) and' in _tracked: T2 fails; (M3) skip writing back the file in approve: T6 fails; (M4) skip the index reset: T6 fails; (M5) drop './' in committed_approvals: T8 fails; (M6) drop the workspace-equality case in is_tracked_task: T1 or T4 fails. Record results."

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest (pip may need --break-system-packages)"
    - "Close this prompt with git mv dev/prompt/prompt-4b0a5592-approval-tracking.md dev/prompt/closed/; leave the issue and change documents active"
    - "Commits: Conventional Commits; engine source as fix(engine), tests as test, report and prompt move as docs(dev)"
  files:
    - { path: "ai/engine/src/stages.py", content: "modified (FR-01, FR-04)" }
    - { path: "ai/engine/src/orchestrator.py", content: "modified (FR-02)" }
    - { path: "ai/engine/src/approve.py", content: "modified (FR-03)" }
    - { path: "tests/engine/test_stages.py", content: "modified (FR-05)" }
    - path: "dev/reports/report-4b0a5592-approval-tracking.md"
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
        dev/ before and after); 5.0 Deviations from this prompt (or
        'None'); 6.0 Open points for the planner; 7.0 Session branch,
        starting commit and commit hashes.

success_criteria:
  - "FR-01 to FR-05 implemented as specified; all new tests present and passing"
  - "Mutations M1 to M6 fail their named tests"
  - "Full suite: no failures beyond the recorded baseline"
  - "Both checkers report 0 errors on dev/"
  - "git diff <starting commit>..HEAD touches only the files in deliverable.files and the prompt move, plus recorded assertion updates"
  - "Commits pushed to the session branch, not merged; report §7.0 lists the branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward into main. A follow-up audit by an independent session is required before closure (P02.8.2). The planner updates design-14e05e35 §8.3 and §8.4 and guide-engine-operations §5.0 after review."
```

Copyright (c) 2026 William Watson. MIT License.
