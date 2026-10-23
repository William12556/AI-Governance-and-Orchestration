Created: 2026 October 23

```yaml
prompt_info:
  id: "prompt-14cf601f"
  task_type: "refactor"
  source_ref: "change-14cf601f"
  target_profile: "claude_code"  # Claude Code cloud session
  date: "2026-10-23"
  iteration: 1
  coupled_docs:
    change_ref: "change-14cf601f"
    change_iteration: 1

context:
  purpose: >
    Organise framework source by component. Move Overwatch from the bare
    ai/src/ folder into a new ai/webui/ component (the home of a future
    central UI; Overwatch is its current module), rename its tests to
    tests/webui/, and update every active reference. Mechanical move: no
    behaviour change.
  integration: >
    overwatch.py imports only the standard library and yaml and does not
    resolve paths from __file__; it runs from a project root. Two tests load
    it by path: tests/overwatch/test_overwatch.py (_SRC) and
    tests/engine/test_engine_mcp.py (test_overwatch_reads_configured_state_dir,
    sys.path insert). ai/core/ already exists with a README.md written by
    the planner; leave it unchanged.
  knowledge_references:
    - "dev/change/change-14cf601f-webui-component-layout.md (approved scope)"
    - "dev/issue/issue-14cf601f-webui-component-layout.md"
    - "CLAUDE.md; ai/governance/software-engineering/governance.md; ai/governance/software-engineering/primer.md"
  constraints:
    - "Use git mv for every move so history follows the files."
    - "No change to Overwatch behaviour, output, CLI options or dependencies. The only edit inside overwatch.py is the path in its module docstring usage line."
    - "Do not modify ai/core/README.md, bin/propagate.sh, bin/migrate-layout.sh, anything under dev/tools/, dev/audit/, any closed/ folder, Version History rows other than the one added below, or dev/requirements/."
    - "Do not edit the issue or change documents; the planner updates them after review."
    - "ai/governance/software-engineering/primer.md and docs/claude/primer.md must remain byte-identical."
    - "Git (CLAUDE.md §4.0): work on your session branch. Record the starting commit hash before any edit. Commit and push the session branch; do not merge into main, do not open a pull request, do not force-push."
    - "Stop condition: if any step needs a change outside the listed files, or a test fails after the move that passed in the baseline, do not improvise. Record it in the report §5.0 and §6.0 and stop."

specification:
  description: "Component layout per change-14cf601f."
  requirements:
    functional:
      - "FR-A git mv ai/src/overwatch.py ai/webui/src/overwatch.py; git mv ai/src/requirements-overwatch.txt ai/webui/requirements.txt. ai/src/ must no longer exist."
      - "FR-B git mv tests/overwatch tests/webui. In tests/webui/test_overwatch.py change _SRC to parents[2] / 'ai' / 'webui' / 'src' / 'overwatch.py' and the module docstring path to ai/webui/src/overwatch.py."
      - "FR-C tests/engine/test_engine_mcp.py: the sys.path insert in test_overwatch_reads_configured_state_dir becomes os.path.join(REPO, 'ai', 'webui', 'src')."
      - "FR-D ai/webui/src/overwatch.py: module docstring usage line becomes 'python ai/webui/src/overwatch.py [--project PATH] [--interval N]'."
      - "FR-E bin/migrate-terms.py scan(): the framework folder tuple becomes ('engine', 'governance', 'profiles', 'core', 'webui')."
      - "FR-F CLAUDE.md: replace ai/src/ with ai/webui/ in the target-platform line, the scope line and the source-change line; install row becomes 'pip install -r ai/webui/requirements.txt'; test row becomes 'python3 -m pytest tests/engine tests/webui -v'; docstring example becomes ai/webui/src/overwatch.py; layout row lists 'ai/engine/', 'ai/core/', 'ai/webui/', 'ai/governance/<model>/', 'ai/profiles/'."
      - "FR-G governance.md P10.6: framework-owned folders become 'ai/engine/, ai/core/, ai/webui/, ai/governance/<model>/, ai/profiles/'. In the layout tree replace the src/ line with two lines: 'core/  # Framework-owned: shared code (reserved)' and 'webui/  # Framework-owned: central UI component (current module: overwatch)', aligned with the existing comments. Add Version History row '| 12.5 | 2026-10-23 | P10.6: framework source organised by component; ai/src/ replaced by ai/webui/ (Overwatch) and ai/core/ (reserved) (change-14cf601f). Non-breaking. |'."
      - "FR-H Both primer.md copies and docs/guide-orchestration.md: the overwatch command becomes 'python ai/webui/src/overwatch.py [--project PATH] [--interval N]'. If either primer.md has a Version History table, add one row in both, identically."
      - "FR-I dev/design/design-project-overwatch.md: replace ai/src/overwatch.py with ai/webui/src/overwatch.py, ai/src/requirements-overwatch.txt with ai/webui/requirements.txt, and the ai/src/ tree with ai/webui/ containing src/overwatch.py and requirements.txt. Leave historical statements about govwatch coexistence unchanged in meaning. Add one Version History row citing change-14cf601f."
    technical:
      language: "Python, Markdown, YAML"
      version: "Python 3.10+ (repository convention 3.11+)"

testing:
  validation:
    - "Baseline before any edit: python3 -m pytest tests/engine tests/overwatch -q; record counts (last recorded: 331 passed, 1 skipped on Linux)."
    - "After the change: python3 -m pytest tests/engine tests/webui -q; counts equal the baseline."
    - "python3 -m py_compile ai/webui/src/overwatch.py bin/migrate-terms.py"
    - "From the repository root: python3 ai/webui/src/overwatch.py --project dev/smoke --interval 1, stopped after one cycle; no traceback; remove any generated files that are not ignored by git."
    - "python3 ai/engine/src/linter.py dev and python3 ai/engine/src/protocol_checker.py dev; findings equal the baseline."
    - "Residue search: grep -rn -e 'ai/src' -e 'tests/overwatch' -e 'requirements-overwatch' excluding .git, closed/, dev/audit/, dev/tools/, dev/reports/, dev/requirements/, dev/issue/, dev/change/, dev/prompt/ and bin/migrate-layout.sh; expected no matches. List every remaining match in the report with the reason it is retained."
    - "cmp ai/governance/software-engineering/primer.md docs/claude/primer.md"

deliverable:
  format_requirements:
    - "Setup if needed: pip install -r ai/engine/requirements.txt -r ai/src/requirements-overwatch.txt pytest (before the move; pip may need --break-system-packages)"
    - "Commits: Conventional Commits; moves and code as refactor(webui), documents as docs, report as docs(dev)"
    - "Close this prompt with git mv dev/prompt/prompt-14cf601f-webui-component-layout.md dev/prompt/closed/"
  files:
    - { path: "ai/webui/src/overwatch.py", content: "moved; docstring path (FR-D)" }
    - { path: "ai/webui/requirements.txt", content: "moved, unchanged" }
    - { path: "tests/webui/test_overwatch.py", content: "moved; FR-B" }
    - { path: "tests/engine/test_engine_mcp.py", content: "FR-C" }
    - { path: "bin/migrate-terms.py", content: "FR-E" }
    - { path: "CLAUDE.md", content: "FR-F" }
    - { path: "ai/governance/software-engineering/governance.md", content: "FR-G" }
    - { path: "ai/governance/software-engineering/primer.md, docs/claude/primer.md, docs/guide-orchestration.md", content: "FR-H" }
    - { path: "dev/design/design-project-overwatch.md", content: "FR-I" }
    - path: "dev/reports/report-14cf601f-webui-component-layout.md"
      content: >
        New file. Obsidian Markdown: 'Created: <year> <month> <day>' line,
        table of contents, numbered sections, Return to Table of Contents
        links, Version History table, final line 'Copyright (c) 2026 William
        Watson. MIT License.'. Sections: 1.0 Summary; 2.0 Files changed;
        3.0 Test results (baseline and final counts); 4.0 Governance checks
        and residue search; 5.0 Deviations (or 'None'); 6.0 Open points for
        the planner, including downstream propagation not performed;
        7.0 Session branch, starting commit and commit hashes.

success_criteria:
  - "ai/src/ and tests/overwatch/ no longer exist; ai/webui/src/overwatch.py, ai/webui/requirements.txt and tests/webui/test_overwatch.py exist and git log --follow shows their history"
  - "Test counts equal the baseline"
  - "Residue search clean apart from listed, justified retentions"
  - "Both primer.md copies identical"
  - "ai/core/README.md unchanged"
  - "Commits pushed to the session branch, not merged; report §7.0 lists branch, starting commit and commit hashes"

notes: "The planner reviews the session branch before the operator merges it fast-forward only. Downstream propagation (solax-modbus first) is a separate human step."
```

Copyright (c) 2026 William Watson. MIT License.
