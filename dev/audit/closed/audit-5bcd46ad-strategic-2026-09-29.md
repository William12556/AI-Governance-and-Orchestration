Created: 2026 September 29

# Strategic Audit — Layout Migration (5bcd46ad) and Engine Runtime Fixes (c37198be)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Independence and Method](<#2.0 independence and method>)
[3.0 Verification Results](<#3.0 verification results>)
[4.0 T08 Record](<#4.0 t08 record>)
[5.0 Experiments](<#5.0 experiments>)
[6.0 Recorded Findings (a) and (b)](<#6.0 recorded findings (a) and (b)>)
[7.0 Positive Findings](<#7.0 positive findings>)
[8.0 Closure](<#8.0 closure>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** change-5bcd46ad (commits `c6a5c64`, `7e64452`, `0b23e9c`, `88018e2`; baseline tag `pre-5bcd46ad` = `cde884a`) and change-c37198be / issue-c37198be (commit `13bb533`). Tree audited at `23030ec`.
- **Verdict:** accept with remediation.
- **Findings:** 0 critical, 1 high, 3 medium, 12 low.
- **Central result:** the migration is mechanical and behaviour-preserving. Every source change in `orchestrator.py`, `mcp_client.py`, the recipes, `overwatch.py` and `server.py` is a path, name or terminology substitution, plus the mapped items (default config path, recipe set `loop`, legacy `ael` alias, `sys.executable`). `propagate.sh` and `migrate-layout.sh` never deleted or overwrote project content in any experiment.
- **Blocking before closure:**
  - H-01: `bin/bootstrap.sh` on `main` fails against the latest release `v0.0.2`, which still has the old layout. The documented install path is broken until a release is cut.
  - M-01: the post-migration test suite has only been run with a stub harness. Real pytest remains outstanding. This audit could not run it either (§2.0).
- **Recorded findings (a) and (b):** both correctly scoped as not regressions. The cause of (a) is narrowed in §6.0.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Independence and Method

- This session did not implement either change. The change records were treated as claims, and each claim was checked against `git diff pre-5bcd46ad..HEAD`, `git show 13bb533` and the source at `23030ec`.
- The original `ael-mcp/server.py` was read from GitHub (William12556/ael-mcp, blob `7587b09`) [1] and compared line by line with `ai/engine/mcp/server.py`.
- Environments:
  - Cowork Linux VM on the operator's machine: GNU bash 5.1.16, rsync, perl, Python 3.10. No PyPI access.
  - Cloud sandbox: Python 3.11, mcp 1.27. PyPI refused by policy (HTTP 403).
- pytest, openai and rich could not be installed in either environment. **pytest result: not yet run** (the operator field in the brief was not filled). Checks run instead: `py_compile`, YAML parse, import of `server.py` with tool listing, `bash -n`, `linter.py`, `protocol_checker.py`, and script experiments (§5.0).
- macOS `/bin/bash` 3.2 and BSD `mv`/`sed` were not available. Compatibility was assessed by inspection only (§3.0 item 5).
- Scripts ran only in a VM-local clone and in throwaway targets built from `git archive pre-5bcd46ad ai`.
- **Repository side effect, disclosed:** a read-only `git status` against the repository left an empty `.git/index.lock`, because the session could not unlink it. With the operator's deletion grant, that lock file alone was removed. `git status` then reported a clean tree. No tracked file was modified. This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Verification Results

| # | Area | Result | Evidence / finding |
|---|---|---|---|
| 1 | Layout vs proposal §4.0–§5.0 | Pass | `git ls-files ai`: `engine/{src,recipes,mcp,doc}`, `config.template.yaml`, `governance/software-engineering/{templates,skills,doc,seed}`, `profiles/`, `src/overwatch.py`, `tests/engine/`. (P2) items are absent, as planned. |
| 2 | No behaviour change (orchestrator, overwatch, engine-mcp) | Pass with notes | Diff is limited to mapped names, paths and strings. `server.py` matches the ael-mcp source except for paths, names, `sys.executable` and the added `.timeout` state file. See L-04. |
| 3 | Recipe prompt wording | Pass with notes | Terminology only. Wording differs from the mapping: `WORK/REVIEW LOOP` and `work/review loop` instead of `LOOP` and `loop` (L-04). |
| 4 | `bin/propagate.sh` | Pass | Old-layout refusal exits 3. Seeding of `config.yaml`, `context.md` and `task.md` works. No deletes. The second run is up to date. `DECLARED_NESTED` is no longer needed: every declared path is now at the `ai/` top level or is a declared directory, and candidates are non-directories. |
| 5 | `bin/migrate-layout.sh` | Partial | Plan and apply are correct. It never deleted or overwrote in any experiment. The dirty-tree check refuses both tracked edits and untracked files. No bash 4 constructs are used (no `declare -A`, `mapfile`, `${x,,}` or `[[ -v ]]`). See M-02, L-01, L-03. |
| 6 | `bin/bootstrap.sh`, `bin/release.sh` | Fail / Pass | H-01. `release.sh` excludes are consistent with the new layout. |
| 7 | Residue of old paths and terms | Pass with notes | Remaining hits are retained items (change record notes), history rows, eb782f83 records and the items in L-05. |
| 8 | `governance.md` 11.0 P10.6 / P10.8 | Pass | Layout, ownership boundary, migration note, engine-mcp setup and `../../profiles/` links are accurate. The note at `governance.md:584` is pre-existing (L-12). |
| 9 | `docs/claude/primer.md` identity | Pass | `cmp` reports identical. |
| 10 | Relative links | Pass | One unresolved target: `ai/profiles/README.md` → `docs/claude/project_information.md` (gitignored, pre-existing; L-12). |
| 11 | Traceability | Pass with notes | `FR-*`/`NFR-*` ID sets are unchanged in four requirement and design documents. Backlog dispositions match proposal §6.0, except L-11. |
| 12 | change-c37198be D1–D3, `tests/engine/` | Pass with notes | D1: `ai/engine/requirements.txt` pins `mcp>=1.0.0,<2`. D2: `orchestrator.py:200-209,2397`. D3: `orchestrator.py:95-148,339-367,1425-1433`, `mcp_client.py:38-39,84`. Nine §5.0 item 5 cases are present (`test_t1`–`test_t9`) and repathed correctly. See M-03, L-07, L-09. |
| 13 | Recorded findings (a), (b) | Pass | §6.0 |
| 14 | Test execution | Open | M-01 |

- Static checks reproduced: `linter.py dev/` gives 0 errors and 93 warnings; `protocol_checker.py dev/` gives 0 findings. Both equal the recorded baseline.
- Compliance: 12 of 14 areas pass or pass with notes (86 %). One area is partial and one is open, excluding the failed bootstrap sub-area.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 T08 Record

```yaml
audit_info:
  id: "audit-5bcd46ad"
  title: "Strategic audit — change-5bcd46ad layout migration and change-c37198be engine runtime fixes, 23030ec against pre-5bcd46ad"
  date: "2026-09-29"
  mode: "strategic"
  status: "closed"
  auditor: "Strategic Domain (Claude, Cowork; independent session — not an implementing session)"

scope:
  target: "git diff pre-5bcd46ad..23030ec; commit 13bb533; ai/, bin/, tests/, docs/, dev/ change, issue, proposal, backlog and design records"
  criteria:
    - "layout conformance with proposal-5bcd46ad §4.0–§5.0"
    - "no behaviour change beyond dev/tools/mapping-5bcd46ad.yaml"
    - "script safety: never delete, never overwrite, refusal paths, bash 3.2 / BSD compatibility"
    - "document residue, governance P10.6/P10.8 accuracy, primer identity, links"
    - "traceability: requirement IDs, backlog dispositions, P03/P04 coupling"
    - "change-c37198be D1–D3 and tests after migration"
  exclusions:
    - "Real pytest execution (pytest not installable in either audit environment)"
    - "macOS /bin/bash 3.2 and BSD tool execution (inspection only)"
    - "Downstream repositories, including the solax-modbus pilot (not accessed)"
    - "Live engine or engine-mcp runs"

findings:
  critical: []
  high:
    - location: "bin/bootstrap.sh:79-81; latest release v0.0.2 (d5b0bab, 2026-07-16)"
      description: >
        H-01. The bootstrap on main copies ai/engine/config.template.yaml and
        ai/governance/software-engineering/seed/* from the latest release
        tarball. v0.0.2 has the old layout (ai/ael/, ai/governance.md), so
        cp fails under set -e. The script then exits 1 after extraction and
        leaves an old-layout ai/ and its temporary directory behind. README.md:92
        and docs/guide-install.md:42 pipe main's bootstrap.sh directly, so the
        documented new-user install fails until a new-layout release exists.
        Remediation: cut a release from the new layout (bin/release.sh
        v0.1.0, governance 11.0) before or together with closure. Optionally,
        make bootstrap.sh refuse, with a clear message, a tarball without
        ai/engine/.
      issue_ref: "proposed P03 issue"
  medium:
    - location: "dev/change/change-5bcd46ad-layout-migration.md verification.test_results; dev/todo.md Active item 1"
      description: >
        M-01. After the migration, tests/engine and tests/overwatch have run
        only under an offline stub harness (62/62). Real pytest in the
        engine environment is recorded as pending, and this audit could not
        run it (§2.0). The conftest path changes, the recipe-set rename
        (test_t6) and the EngineState rename are therefore unverified under
        the real pytest and openai/rich stack.
        Remediation: run ~/.venvs/ael/bin/python -m pytest tests/engine
        tests/overwatch -q on the Mac and record the result in both change
        records before closure.
    - location: "bin/migrate-layout.sh:56-57, 144"
      description: >
        M-02. Every retired path is moved as a whole directory and logged as
        'retired framework file', with no content check. That label is
        defined by propagate.sh as 'safe to delete'. Project-authored files
        inside ai/ael/, ai/doc/, ai/templates/ or ai/skills/ get the same
        label. Demonstrated with ai/ael/project-notes.md and
        ai/doc/project-doc.md (§5.0 A). propagate.sh avoids this through
        is_framework_version; migrate-layout.sh does not.
        Remediation: label the rows 'retired framework path (contents not
        verified)', or list per file and apply the framework-blob test before
        labelling. Before any operator cleanup of ai-local/retired-5bcd46ad/
        in solax-modbus, check that folder for non-framework files.
    - location: "dev/design/design-ael-orchestrator.md:232-233, 501; dev/change/change-c37198be-ael-runtime-verification.md traceability.design_updates"
      description: >
        M-03. change-c37198be changed the --task interface (a path-like
        value naming a missing file now exits 1) and added
        _looks_like_task_path, _select_recipe_set, _scope_targets and
        _written_targets. The design document was not updated (P04.3/P04.4):
        the §232 task precedence omits the refusal, NFR-AEL-004 still states
        that the --task interface is unchanged, and no c37198be reference
        exists. The issue lists this design in affected_scope, but
        design_updates is empty.
        Remediation: update the design (task resolution, D3 path extraction,
        write-tool set, NFR-AEL-004 note) with a c37198be version row.
        Documents only.
  low:
    - location: "bin/migrate-layout.sh:70, 151; ai/engine/mcp/server.py:32; ai/src/overwatch.py:1245"
      description: >
        L-01. The state_dir rewrite matches only the exact double-quoted
        value "ai/state/ralph". An unquoted, single-quoted or trailing-slash
        value is left unchanged, and the plan gives no warning (§5.0 C).
        engine-mcp and overwatch hard-code ai/state, while the orchestrator
        follows config. The result would be the silent status mismatch the
        solax-modbus pilot exposed. The hard-coding is inherited from ael-mcp.
        Remediation: warn when a state_dir other than "ai/state" remains
        after migration. In Phase 2, have engine-mcp read loop.state_dir from
        the project config.
    - location: "ai/engine/mcp/server.py:87-92, 130-136"
      description: >
        L-02. _pid_alive uses os.kill(pid, 0). The server never waits on its
        Popen child, so after exit the child remains a zombie and reports
        alive. It is reaped only by subprocess._cleanup() at the server's
        next Popen, for example reset_engine. This is inherited unchanged
        from ael-mcp. See §6.0.
        Remediation (Phase 2 rebuild): keep Popen handles and use poll(), or
        call os.waitpid(pid, WNOHANG) before the kill probe.
    - location: "bin/migrate-layout.sh:138; change-5bcd46ad rational.proposed_solution, risks, rollback_procedure"
      description: >
        L-03. The change record says the script uses git mv. It uses mv -n,
        so git sees deletions plus untracked files, and the operator must
        stage both sides. Rollback by reverting the committed migration
        still works.
        Remediation: correct the record, or switch to git mv inside a work
        tree.
    - location: "dev/change/change-5bcd46ad-layout-migration.md code_changes, notes"
      description: >
        L-04. The change record is incomplete or inaccurate at terminology
        level. No functional effect was found.
        (1) The mcp_client.py [ael]→[engine] prefix changes are not listed.
        (2) extract_target_profile is listed as affected but is unchanged;
        the alias is in main_async (orchestrator.py:2487).
        (3) The note says the overwatch alert file output is unchanged, but
        overwatch.py:860 changed "AEL:" to "engine:", and the embedded page
        JSON key changed from ael_state to engine_state.
        (4) Recipe wording deviates from the mapping (WORK/REVIEW LOOP).
        (5) [AEL RUNTIME CONTEXT] became [ENGINE RUNTIME CONTEXT]
        (upper case), consistently across the orchestrator and recipes.
        (6) server.py adds .timeout to _STATE_FILES.
        Remediation: amend the record.
    - location: ".gitignore:54; ai/src/overwatch.py:6-9"
      description: >
        L-05. Residue. dev/smoke/.ael/ is ignored as "engine-mcp run records",
        but engine-mcp writes to ai/state/. The overwatch docstring says code
        is carried over from ai/src/govwatch.py, which is now deleted.
        Remediation: drop or reword both.
    - location: "ai/governance/software-engineering/templates/T03-prompt.md:219-224"
      description: >
        L-06. The target_profile enum lists engine, claude_code and
        claude_omlx. Governance P13 reads the legacy value ael as engine, so
        closed prompts would fail validation against the current schema.
        Remediation: add ael to the enum as deprecated, or state that closed
        documents are exempt.
    - location: "dev/issue/issue-c37198be-ael-runtime-verification.md:9; dev/change/change-c37198be-ael-runtime-verification.md:101-102"
      description: >
        L-07. change-c37198be record hygiene. The issue status is "open"
        although the change is "implemented"; P03.7 requires "resolved". The
        change YAML has a duplicate classes_affected key. interface_changes
        and dependencies are strings rather than the T07 shape.
        Remediation: correct them at closure.
    - location: "tests/"
      description: >
        L-08. No tests cover engine-mcp (server.py), migrate-layout.sh,
        propagate.sh old-layout refusal or config seeding, the orchestrator
        default config path (../../config.yaml), or the legacy ael alias.
        The migration's new behaviour relies on live runs and one pilot.
        Remediation: add unit tests for server.py path resolution and state
        names, and a script test harness when P05 CI is authored.
    - location: "ai/engine/src/orchestrator.py:95-103, 168-169; ai/engine/src/mcp_client.py:38-39"
      description: >
        L-09. The D3 scope check applies only to names in _WRITE_TOOLS. A
        write tool with any other name is not scope-checked (fail-open),
        while mcp_client classifies by verb pattern (fail-closed). This is
        mitigated by the filesystem-mcp 2.5.0 pin in config.template.yaml.
        Existing projects keep their own ai/config.yaml, so the pin reaches
        them only by hand (dev/todo.md item 3).
        Remediation (Phase 2): derive write classification from the
        mcp_client patterns, and check downstream configs for the pin.
    - location: "Claude Desktop MCP configuration (operator device)"
      description: >
        L-10. The retired ael-mcp server is still registered: start_ael,
        ael_status and reset_ael are exposed to this session alongside
        engine-mcp. Against an unmigrated project it would launch the old
        orchestrator with a bare python3.
        Remediation: remove the entry (dev/todo.md item 4).
    - location: "dev/backlog.md:74; dev/proposals/proposal-5bcd46ad-ai-go-pivot.md:182; dev/change/change-5bcd46ad-layout-migration.md:294"
      description: >
        L-11. Record gaps.
        (1) Backlog §5.0 item 2 was to be retried in the verification run.
        The engine-mcp run went REVISE → SHIP, but its REVISE was a reviewer
        path error, not a defect fix. The item's outcome is not recorded.
        (2) Proposal OQ-01 states "a Mistral Vibe profile is added", but none
        exists in ai/profiles/.
        (3) change-5bcd46ad design_updates has an empty update_date and omits
        design-project-overwatch.md.
        Remediation: record the outcomes, or reword as planned.
    - location: "governance.md:584; ai/engine/recipes/audit-review.yaml:23; ai/profiles/README.md link"
      description: >
        L-12. Pre-existing; not regressions; recorded for the backlog.
        (1) P10.6 says the framework repository "contains only ai/, doc/, and
        templates/", which is inaccurate.
        (2) audit-review.yaml tests for ".complete containing DURATION_LIMIT",
        which the orchestrator never writes; a timeout writes .timeout
        (orchestrator.py:2113) and returns before review.
        (3) The profile README links to the gitignored
        docs/claude/project_information.md.

metrics:
  items_audited: 14
  findings_total: 16
  findings_by_severity:
    critical: 0
    high: 1
    medium: 3
    low: 12

recommendations:
  - "Before closure: cut a new-layout release (H-01) and run real pytest (M-01)."
  - "Raise P03 issues for H-01 and M-02; update the orchestrator design for c37198be (M-03, documents only)."
  - "Amend both change records (L-03, L-04, L-07, L-11) at closure."
  - "Carry L-01, L-02 and L-09 into the Phase 2 engine and engine-mcp requirements."
  - "Remove the ael-mcp registration (L-10) and inspect solax-modbus ai-local/retired-5bcd46ad/ before cleanup (M-02)."

traceability:
  design_refs:
    - "dev/design/design-ael-orchestrator.md"
    - "dev/design/design-project-overwatch.md"
  issue_refs: []
  related_audits:
    - audit_ref: "audit-c5270084"
      relationship: "related (propagate.sh safety baseline)"
    - audit_ref: "audit-b170cf6a"
      relationship: "related (propagate.sh safety baseline)"

notes: >
  Both changes used the operator-approved abbreviated workflow (proposal
  D-14; change-c37198be notes). This audit is the single independent review
  both records name. It does not close either triple; closure follows
  operator acceptance.

closure:
  date: "2026-09-29"
  approver: "William Watson"
  recorded_by: >
    The implementing session, not the auditor. This block records the closure
    decision and the disposition of findings; no finding, verdict or rationale
    above has been altered.
  remediation:
    changes: ["change-5bcd46ad (verified)", "change-c37198be (verified)"]
    issue: "issue-c37198be (closed)"
    commits: ["ce4a4ee", "dbb1da1"]
    release: "v0.1.0"
  criteria_p02_8_1:
    - criterion: "All critical findings fully resolved"
      assessment: "Met. There were none."
    - criterion: "All high-priority findings addressed or mitigated with documented acceptance"
      assessment: >
        Met. H-01 resolved by release v0.1.0 (new layout; bootstrap on main
        installs). The optional bootstrap guard is carried in dev/backlog.md
        §3.0 item 3.
    - criterion: "Completion documented in audit report"
      assessment: "Met by this block."
    - criterion: "Human approval obtained"
      assessment: "Met. Operator accepted audit and remediation on 2026-09-29."
  waiver:
    requirement: "P02.8.2 — follow-up audit after remediation"
    decision: >
      Waived by the operator. The only source change after the audit was the
      bin/migrate-layout.sh log label (M-02, P04.12); bin/bootstrap.sh was not
      changed. Recorded as a waiver rather than as satisfaction of the
      requirement.
    consequence: >
      The remediation in dbb1da1 is verified only by the implementing
      session's own checks (linter, protocol_checker, bash -n, YAML parse).
  disposition:
    fixed: ["H-01", "M-01", "M-02", "M-03", "L-05", "L-06"]
    record_corrected: ["L-03", "L-04", "L-07", "L-11"]
    carried_to_backlog: ["L-01", "L-02", "L-08", "L-09", "L-12"]
    operator_action: ["L-10"]

version_history:
  - version: "1.0"
    date: "2026-09-29"
    changes:
      - "Initial strategic audit"
  - version: "1.1"
    date: "2026-09-29"
    changes:
      - "Closure recorded (operator acceptance; follow-up audit waived)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Experiments

All targets were throwaway git repositories built from `git archive pre-5bcd46ad ai`, with a project `context.md`, a workspace issue, `ai/state/ralph/task.md`, `ai/ael/project-notes.md` and `ai/doc/project-doc.md` added. Scripts were run from a VM-local clone at `23030ec`.

| Case | Action | Result |
|---|---|---|
| A1 | `migrate-layout.sh` (dry run) | Plan listed 11 moves and the state_dir edit; tree unchanged |
| A2 | `propagate.sh --yes --allow-major` on old layout | Exit 3, refused |
| A3 | `--apply` with a tracked edit, then with an untracked file under `ai/` | Exit 3 both times, nothing applied |
| A4 | `--apply` on a clean tree | Moves done; `state_dir` became `"ai/state"`; the two project files were logged as "retired framework file" (M-02); git shows deletions plus untracked files (L-03) |
| A5 | `propagate.sh --yes` without `--allow-major` | Exit 2 (target version unknown) |
| A6 | `propagate.sh --yes --allow-major` | Framework copied; `config.yaml`, `context.md` and `task.md` preserved; no relocations |
| A7 | Second propagate run | "Target is up to date" |
| A8 | Content check | Every original file's content still exists somewhere, except framework files superseded in place (profiles, `overwatch.py`) and the state_dir edit |
| C | Unquoted `state_dir: ai/state/ralph` | No edit and no warning (L-01) |
| D | `ai/config.yaml` already present | Exit 3, refused |
| E | Empty `ai/`, `propagate.sh --yes --allow-major` | `config.yaml` (identical to the template), `context.md` and `task.md` seeded |
| Z | Python: Popen child, reference dropped, child exits | `os.kill(pid, 0)` succeeds while the child is in state `Z`; after an unrelated `subprocess.run` it raises `ProcessLookupError` (L-02, Linux) |
| S | Import `ai/engine/mcp/server.py` with mcp 1.27 | Tools `start_engine`, `engine_status`, `reset_engine` registered; invalid `project_dir` returns a JSON error |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Recorded Findings (a) and (b)

- **(a) stale `pid_alive`: correctly scoped as not a regression.**
  - `_pid_alive` and the Popen usage are byte-identical to ael-mcp [1]. The orchestrator's exit sequence (`engine end` logged, then `mcp.close()`, then `os._exit`) is unchanged by the migration.
  - The cause can be narrowed to two candidates:
    - (i) The child is a zombie. The server holds no waiting handle, so `kill(pid, 0)` succeeds until the server's next Popen reaps it (experiment Z). This fits the record: the process was "gone" only after `reset_engine`, which runs `subprocess.run`.
    - (ii) `mcp.close()` teardown runs after the `engine end` log line.
  - Confidence: moderate for (i). macOS zombie semantics for `kill(pid, 0)` were not tested here.
  - Verify with `ps -o pid,stat,etime -p <pid>` during the window: `Z` confirms (i); `S` or `R` confirms (ii).
- **(b) worker ignored the `context.md` write constraint: correctly scoped as not a regression.**
  - The same behaviour is recorded in every 2026-09-24 run before the migration (backlog §5.0 item 7).
  - Writes inside the project root are permitted by F4 by design.
  - The recipe changes do not touch the CONSTRAINTS text apart from the `BLOCKED.md` name. The Phase 2 disposition (manifest write scope) is appropriate.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Positive Findings

- The mapping file was used as the single source for both the migration and the residue search. Remaining residue is small and explained.
- The engine-mcp port is faithful. Using `sys.executable` removes the interpreter mismatch that the bare `python3` in ael-mcp allowed.
- `propagate.sh` keeps all audit-b170cf6a safeguards. The new old-layout refusal fails closed.
- Both scripts refuse unsafe states before any change and never deleted content in any experiment.
- Requirement identifiers and historical records were preserved deliberately and documented.
- The c37198be D3 fix handles nested `files`/`paths`/`moves` arguments consistently across the scope check, manifest, syntax check and F21 guard.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Closure

- Verdict: **accept with remediation**.
- Closure of change-5bcd46ad and change-c37198be (and issue-c37198be) is recommended once:
  - H-01 is resolved (new-layout release) or formally accepted with a documented workaround;
  - M-01 real pytest results are recorded;
  - M-03 design update is made (documents only).
- M-02 and the low findings may be carried as P03 issues or backlog entries.
- Follow-up audit: required for H-01 only if remediation changes `bin/bootstrap.sh`. Remediation that only cuts a release changes no source, so the operator may waive the follow-up (P02.8.2).
- Approver and closure date: William Watson, 2026-09-29. Audit and remediation accepted; follow-up audit waived (see `closure` in §4.0).

[Return to Table of Contents](<#table of contents>)

---

## References

[1] WATSON, W., 2026. *ael-mcp: server.py* [online]. GitHub repository William12556/ael-mcp, blob 7587b095. Available from: https://github.com/William12556/ael-mcp/blob/main/server.py [Accessed 29 September 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-29 | Initial strategic audit of change-5bcd46ad and change-c37198be |
| 1.1 | 2026-09-29 | Closure recorded: operator acceptance, P02.8.2 waiver, finding disposition |

---

Copyright (c) 2026 William Watson. MIT License.
