Created: 2026 October 01

# Follow-up Audit — Remediation of audit-14e05e35 (change-82dbf16a)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Scope and Method](<#2.0 scope and method>)
[3.0 Verification Status](<#3.0 verification status>)
[4.0 Findings](<#4.0 findings>)
[5.0 Experiments](<#5.0 experiments>)
[6.0 Observations](<#6.0 observations>)
[7.0 T08 Record](<#7.0 t08 record>)
[8.0 Closure Recommendation](<#8.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** remediation commit `9f692dc` (change-82dbf16a, issue-82dbf16a) of [audit-14e05e35](<audit-14e05e35-phase2-2026-10-01.md>). Targeted follow-up per P02.8.2.
- **Verdict:** remediation incomplete. Do not close issue-82dbf16a or change-82dbf16a yet.
- **Verified closed:** H-03, M-01, M-02, M-03, M-04, M-05. FR-03-02 v1.3 matches the code.
- **Partially remediated:** H-01 and H-02. The fixes work for the cases tested by the change, but each has a bypass that reproduces the original consequence:
  - F-01 (high): a command gate runs after `review-result.txt` is cleared and before it is read. Worker-written test code forges `SHIP` against a `REVISE` reviewer (E-1b).
  - F-02 (high): the pre-run check binds the *evidence documents*, not the *task file*. A tracked prompt outside the evidence folder runs under another document's approval (E-2b).
- **Additional findings:** 2 medium (F-03, F-04), 2 low (F-05, F-06).
- **Tests:** 257 passed, 1 skipped (root), consistent with the change record's 258 passed (§2.0).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope and Method

- **In scope:** H-01 to H-03, M-01 to M-05, FR-03-02 v1.3, as stated in change-82dbf16a.
- **Out of scope:** backlog §3.0 items 6–10 (L-08 to L-11, L-14 accept remainder), other low findings, and findings not listed in audit-14e05e35.
- **Independence:** this session implemented no part of change-82dbf16a. The change record and test names were treated as claims.
- **Method:**
  - Read `git diff 4cdfbe4 9f692dc` for `scope.py`, `orchestrator.py`, `stages.py`, `approve.py`, `gates.py`, `manifest.py`, and the new tests.
  - Repeated E-1 to E-5 of the original audit and added variants for path forms, symlinks, tool-name variants and `approvals.yaml` forms (§5.0).
  - Ran `pytest -q tests/engine tests/overwatch`.
  - Checked the tool schemas of the pinned `@j0hanz/filesystem-mcp` 2.5.0 (tag `v2.5.0`, GitHub source) for write tools that take directory paths.
- **Environments:**
  - Cowork Linux VM on the operator's machine (repository mounted). Used for reading and git only, always with `git --no-optional-locks`. The working tree was clean at `9f692dc` (= `origin/main`). No `.git/*.lock` file existed before or after.
  - Cloud sandbox: fresh clone of `origin/main` at `9f692dc`, Python 3.11.15. PyPI and apt were refused (HTTP 403). `pytest`, `pluggy`, `iniconfig`, `packaging` and `rich` (with `markdown-it-py`, `mdurl`, `pygments`) were loaded from their GitHub sources on `PYTHONPATH`. `openai` was replaced by a minimal stand-in (`AsyncOpenAI` only), as in the original audit. The result is indicative; the authoritative run remains the operator's.
- **Test result (cloud clone):** `257 passed, 1 skipped`. The skip is `tests/overwatch/test_overwatch.py` "root ignores directory permissions" (sandbox runs as root). `tests/engine/test_audit_remediation.py` and `tests/engine/test_stages.py`: 56 passed.
- **Governance checks:** `linter.py dev` 0 errors (94 warnings, not assessed); `protocol_checker.py dev` 0 errors.
- **Side effects:** none in the repository. Probes ran only in the cloud clone and were deleted. This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Verification Status

| Item | Status | Evidence |
|---|---|---|
| H-01 | Partial | Direct worker forgery refused and cleared (E-1 repeat, E-1c, E-1d, E-1e). Gate bypass F-01; directory-write bypass F-04; case variants F-05 |
| H-02 | Partial | Edited, added, removed and unbound approvals block (E-2, E-2e, E-2f); `approve.py` re-approval works (existing test, E-2 removed). Task-file bypass F-02; basename collision F-03 |
| H-03 | Closed | All seven dispatch variants refused, none dispatched (E-3). `mcp.call_tool` has one call site (`orchestrator.py:1267`), behind `_dispatch_refusal` (`:1009`, `:1240`) |
| M-01 | Closed | Nine argument forms without a usable path refused (E-4) |
| M-02 | Closed | UNCHECKED command gate ends BLOCKED naming the gate; SKIPPED listed in `awaiting-approval.md` (existing tests; code at `orchestrator.py:2026-2039`, `_finish_run`) |
| M-03 | Closed | Primer §2.0 (both copies identical), `governance.md` P00, `overwatch.py` labels updated; bare-term scan `test_live_corpus_has_no_bare_domain_terms` passes; remaining matches are version rows, audit mode names and `tactical_brief` |
| M-04 | Closed | Scan leaves `.git/index` unchanged; plain `git status` still changes it (E-5) |
| M-05 | Closed | `scrub_env` built from every configured `api_key_env` and applied in `gates.run_command_gate` (existing test). Cloud kinds require `api_key_env` (`providers.py:413`) |
| FR-03-02 v1.3 | Consistent | Every applicable gate must pass (FAIL overrides SHIP); UNCHECKED blocks and is named; empty gates are SKIPPED and listed at approval. See §6.0 note 1 |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Findings

### 4.1 High

**F-01 Gate processes can still supply the verdict (H-01 residual).**
- Evidence: `review-result.txt` is cleared at `orchestrator.py:2002`. The syntax and command gates then run (`:2006-2024`), the reviewer runs, and the verdict is read from `review-result.txt` first (`:2080-2084`). The pytest gate executes project test code, and `tests/` is worker-writable (`writable_paths: [tests/]`).
- Experiment E-1b: the worker writes `tests/conftest.py` that writes `SHIP` into the state directory, plus a passing test; the reviewer reads the deliverables and answers `REVISE`. Result: `rc 0`, `.complete` present, log `verdict from review-result.txt: 'SHIP'`.
- Consequence: the stated guarantee "only this cycle's review phase can supply a verdict file" (change scope, code comment `:2000`) does not hold. A rejecting reviewer is overridden, as in the original H-01.
- Inference: no legitimate writer of `review-result.txt` remains. The review phase refuses write tools (H-03), and `audit-review.yaml` 1.2.0 states the verdict in the final response.
- Recommendation: take the verdict from the reviewer's final message only, and drop `review-result.txt` as a verdict source. Keep clearing it for compatibility. Add a test with a gate that writes the file.

**F-02 The task file is not bound to the approval (H-02 residual).**
- Evidence: `is_tracked_task` (`stages.py:310`) accepts any file under `ai/workspace/`; the work item UUID comes from the file name (`orchestrator.py:2268`). `prerun_missing` (`stages.py:319`) checks the documents found by `_documents` (`:180`), which globs only `<evidence folder>/<prefix>-*.md` and its `closed/`. The task file itself is never compared with them. engine-mcp `_tracked_task_error` (`server.py:96`) applies the same rule.
- Experiment E-2b: with an approved, unchanged `prompt/prompt-<uuid>-work.md`, a new `prompt-<uuid>-evil.md` placed in `ai/workspace/prompt/sub/`, `ai/workspace/scratch/`, `ai/workspace/change/` or `ai/workspace/` is tracked, `prerun_missing` returns `[]`, and engine-mcp accepts it. E-2c: `ai/workspace/prompt/prompt-<uuid>-evil.MD` gives the same result (the glob is case-sensitive; the UUID pattern ignores the extension).
- Consequence: a planner with filesystem access only can run unapproved content, the case H-02 was raised for.
- Recommendation: in the pre-run check, require the resolved task path to be one of the evidence documents of the stage before the loop stage (realpath comparison), and refuse otherwise with exit 3. Apply the same rule in engine-mcp. Add tests for a subfolder, another workspace folder and an extension variant.

[Return to Table of Contents](<#table of contents>)

### 4.2 Medium

**F-03 Blob map keyed by basename (H-02).**
- Evidence: `stage_blobs` (`stages.py:124`) keys hashes by `os.path.basename`. A document present in both the active and the `closed/` folder collapses to one key; the closed copy, scanned last, wins.
- Experiment E-2d: with both copies present, `approve.py` recorded one hash; editing the active copy afterwards left `prerun_missing` at `[]`. The scan reports the anomaly "documents in both the active and the closed folder", but the anomaly does not block the run.
- Recommendation: key blobs by path relative to `ai/workspace/`, or make that anomaly block the pre-run check.

**F-04 Directory-scoped write tools reach signal files (H-01).**
- Evidence: `scope.check` compares each target path with the protected set by equality (`scope.py:214`). filesystem-mcp 2.5.0 `replace_text` takes `path` as "file to rewrite, or directory to rewrite under" with an optional glob. A call with `path: ai/state` is inside the declared scope (state directory prefix) and is not a signal file.
- Experiment E-1f: `replace_text` with `path: ai/state` (with and without `pattern: mcp-run.json`) is allowed, with and without a write scope.
- Consequence: the worker can rewrite existing signal files, for example `task.md` (read back by a later run without `--task`, `orchestrator.py:2516`) and `mcp-run.json`. The verdict is not affected, because `review-result.txt` does not exist during the worker phase.
- Recommendation: refuse a write call when any protected path lies under a target (`_within(p, resolved)`), not only when it equals the target.

[Return to Table of Contents](<#table of contents>)

### 4.3 Low

| ID | Location | Finding | Recommendation |
|---|---|---|---|
| F-05 | `scope.py:130-137, 214` | Protected paths are compared case-sensitively. `ai/state/REVIEW-RESULT.TXT` and `ai/state/.Complete` pass the check (E-1c). On a case-insensitive APFS volume (macOS is the target platform) these name the protected files. Inference: not executed on APFS. Verdict forgery is prevented by the clear at `:2002`, which removes the same file. | Compare case-folded names under the state directory, or use `os.path.samefile` when the file exists. |
| F-06 | `governance.md:139`; `docs/guide-orchestration.md:44`; `docs/setup-apple-silicon-mlx-magistral.md:160`; `ai/profiles/mlx_devstral_magistral_heterogeneous.md:120`; `orchestrator.py:1641-1642`; `guide-engine-operations.md:43` | Documents still say the reviewer writes `review-result.txt`. The engine guide says the verdict is the final response, while the code still reads the file first (F-01). The `_run_pytest_gate` docstring still says "Only FAIL overrides SHIP". | Correct with F-01. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Experiments

All in the cloud clone at `9f692dc`, as temporary pytest probes, deleted afterwards.

| ID | Experiment | Result |
|---|---|---|
| E-1 (repeat) | Fake `run_phase`: worker writes `review-result.txt = SHIP`; reviewer reads the deliverables and returns `REVISE` | `rc 1`, no `.complete`; verdict from final message |
| E-1b | As E-1, but the worker writes `tests/conftest.py` that writes `SHIP` into the state directory; pytest gate configured | `rc 0`, `.complete` present; verdict from `review-result.txt` (F-01) |
| E-1c | `scope.check` with signal-file path forms: `//`, `/./`, `x/../`, `./`, trailing space, upper case | Normalised forms refused; upper-case forms allowed (F-05); trailing space is a different file |
| E-1d | Symlink `tests/r` → `ai/state/review-result.txt`, write to `tests/r` | Refused (engine signal file) |
| E-1e | `move_file` and `edit_file` to `review-result.txt`; `copy_file` | Write tools refused; `copy_file` not classified as write (not a filesystem-mcp 2.5.0 tool; §6.0 note 3) |
| E-1f | `replace_text` with `path: ai/state` | Allowed (F-04) |
| E-2 (repeat) | Committed bound approval; edit prompt and add `prompt-<uuid>-second.md` | `[]` before; `changed` and `added` reported after |
| E-2 removed | Approve with two prompts, remove one | `removed` reported |
| E-2b | Approved prompt unchanged; tracked `prompt-<uuid>-evil.md` in four other workspace locations | Tracked, `prerun_missing` `[]`, engine-mcp accepts (F-02) |
| E-2c | `prompt-<uuid>-evil.MD` in the prompt folder | Tracked, `[]` (F-02) |
| E-2d | Same basename in active and `closed/`; approve; edit active copy | `[]`; anomaly reported, not blocking (F-03) |
| E-2e | Nine `approvals.yaml` forms: `blobs` empty, null, list, foreign key, `./` key, upper-case hash, unquoted keys, bound-then-unbound, unbound-then-bound | All block except a correct bound entry (quoted or unquoted keys). Last entry for a pair wins; an unbound later entry blocks |
| E-2f | CRLF rewrite of an approved prompt | `changed` reported |
| E-3 (repeat) | Reviewer calls: unoffered `write_file`, `Write_File`, `" read_file"`, `filesystem__write_file`; offered `edit_file` and `move_file` under labels `REVIEW` and `Reviewer phase` | None dispatched |
| E-4 (repeat) | `write_file` with `filename`, `file`, `directory`, `uri`, empty, `None`, list, empty `paths`, `edits` without path; symlink `tests/link` → `src` | All refused; symlink target checked |
| E-5 (repeat) | Stat-dirty file; `scan` and `prerun_missing`; then plain `git status` | Index unchanged by the scan; changed by plain `git status` |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Observations

No finding is raised for the following.

1. **FR-03-02 and pytest applicability.** The pytest gate's targets come from the worker's `work-summary.txt`. A worker that names no test-relevant deliverable makes the gate SKIPPED. FR-03-02 v1.3 permits this, and the gate is listed in `awaiting-approval.md`. L-13 merged the declared deliverables into the reviewer block only, not into the gate targets.
2. **Read-after-check window.** The pre-run check hashes the prompt (`orchestrator.py:2381`), and the prompt is read later (`~:2490`). The window is short, and the worker cannot write `ai/workspace/`.
3. **Write-verb classification.** Names such as `copy_file` or `append_file` are not classified as writes. filesystem-mcp 2.5.0 exposes none of them (`create`, `delete`, `diff`, `edit`, `find_files`, `list`, `list_roots`, `move`, `patch`, `read`, `replace_text`, `search_text`, `stat`). A project that adds another MCP server is exposed. This predates the change.
4. **M-05 scope.** Only configured `api_key_env` variables are removed. Other key variables in the operator's shell reach gate processes.
5. **`approve.py`** runs `git add` and `git commit` without `--no-optional-locks`. That is correct, because it writes the index.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 T08 Record

```yaml
audit_info:
  id: "audit-14e05e35"
  title: "Follow-up audit — remediation of audit-14e05e35 (change-82dbf16a, 9f692dc)"
  date: "2026-10-01"
  mode: "strategic"
  status: "complete"
  auditor: "planner (Claude, Cowork; independent session — not the implementing session)"

scope:
  target: "git diff 4cdfbe4..9f692dc: ai/engine/src/{scope,orchestrator,stages,approve,gates,manifest}.py, ai/engine/mcp/server.py (unchanged, checked), tests/engine, requirements FR-03-02 v1.3"
  criteria:
    - "H-01, H-02, H-03 remediation and bypasses (path forms, symlinks, tool-name variants, approvals.yaml forms)"
    - "M-01 to M-05 as stated in change-82dbf16a"
    - "FR-03-02 v1.3 against the code"
    - "repeat of experiments E-1 to E-5"
  exclusions:
    - "backlog §3.0 items 6-10 (L-08 to L-11, L-14 accept remainder)"
    - "findings not listed in the follow-up scope"
    - "live engine runs; macOS APFS case behaviour (F-05 by inference)"

findings:
  critical: []
  high:
    - location: "ai/engine/src/orchestrator.py:2002, 2006-2024, 2080-2084"
      description: "F-01. Gate processes run after review-result.txt is cleared; worker-written test code forges SHIP against REVISE (E-1b). H-01 residual."
      issue_ref: "issue-82dbf16a"
    - location: "ai/engine/src/stages.py:180, 310, 319; ai/engine/mcp/server.py:96"
      description: "F-02. Tracked task file outside the evidence folder (or .MD) runs under another document's approval (E-2b, E-2c). H-02 residual."
      issue_ref: "issue-82dbf16a"
  medium:
    - location: "ai/engine/src/stages.py:124"
      description: "F-03. Blob map keyed by basename; active copy unbound when a closed copy has the same name (E-2d)."
    - location: "ai/engine/src/scope.py:214"
      description: "F-04. Directory-scoped write tools (replace_text) reach signal files; protection compares by equality (E-1f)."
  low:
    - location: "ai/engine/src/scope.py:130-137, 214"
      description: "F-05. Case-sensitive comparison of protected paths (E-1c); case-insensitive APFS by inference."
    - location: "governance.md:139; docs/guide-orchestration.md:44; docs/setup-apple-silicon-mlx-magistral.md:160; ai/profiles/mlx_devstral_magistral_heterogeneous.md:120; orchestrator.py:1641-1642"
      description: "F-06. Documents and a docstring describe review-result.txt and gate precedence as before the change."

metrics:
  items_audited: 9  # H-01..H-03, M-01..M-05, FR-03-02
  findings_total: 6
  findings_by_severity:
    critical: 0
    high: 2
    medium: 2
    low: 2

recommendations:
  - "F-01: take the verdict from the reviewer's final message only; add a gate-writes-file test."
  - "F-02: require the resolved task path to be an evidence document of the stage before the loop stage (engine and engine-mcp); add tests."
  - "F-03: key blobs by workspace-relative path, or block on the active/closed anomaly."
  - "F-04: refuse writes whose target contains a protected path."
  - "F-05, F-06: fix with F-01 and F-04."

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md v1.6"
    - "dev/requirements/requirements-14e05e35-engine-generalisation.md v1.3"
  issue_refs:
    - "issue-82dbf16a"
  related_audits:
    - audit_ref: "audit-14e05e35 (dev/audit/audit-14e05e35-phase2-2026-10-01.md)"
      relationship: "follow_up"

notes: "Indicative test run (pytest and rich from GitHub sources, openai stubbed): 257 passed, 1 skipped (root). No repository side effects."

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes:
      - "Initial follow-up audit of change-82dbf16a"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Closure Recommendation

- **issue-82dbf16a:** do not close. Keep the status `resolved` with `verification.verified_date` empty. Record this audit in `verification.closure_notes` as "follow-up found F-01 to F-06".
- **change-82dbf16a:** do not close. Open iteration 2 of the same issue and change for F-01 to F-04, with tests. F-05 and F-06 may be included or carried as backlog entries.
- **Already verified, no further work:** H-03, M-01 to M-05, FR-03-02 v1.3.
- **P02.8.1:** the high-priority criterion is not met while F-01 and F-02 are open. They may be accepted only by the operator as documented mitigations.
- **Next follow-up:** limited to F-01 to F-04 and their tests, because iteration 2 changes source (P02.8.2).
- **Interim operating note:** until F-02 is fixed, run tracked prompts only from the prompt evidence folder (`ai/workspace/prompt/prompt-<uuid>-*.md`). Until F-01 is fixed, do not treat a SHIP as reviewed when the cycle changed `tests/conftest.py` or other test infrastructure.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-01 | Initial follow-up audit of change-82dbf16a (audit-14e05e35 remediation) |

---

Copyright (c) 2026 William Watson. MIT License.
