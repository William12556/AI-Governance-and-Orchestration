Created: 2026 September 23

# Closure Check Audit — change-b170cf6a Iteration 3

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Independence and Method](<#2.0 independence and method>)
[3.0 Status of B1 to B5](<#3.0 status of b1 to b5>)
[4.0 New Routes Introduced by Iteration 3](<#4.0 new routes introduced by iteration 3>)
[5.0 T08 Record](<#5.0 t08 record>)
[6.0 Experiments](<#6.0 experiments>)
[7.0 Closure Recommendation](<#7.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** `bin/propagate.sh` at `51611db` (blob `df0c517`, unchanged at HEAD `4fc0538`); only the iteration-3 diff `1b7f068..51611db` was checked.
- **B1 to B4:** All four are resolved. Each own reproduction gave the expected result: exit 3 with the edit intact for B1 to B3, and exit 0 with the link preserved for B4.
- **B5:** Reproduced. Severity assigned: **low**. Recommendation: accept (§3.2).
- **New findings:** 0 critical, 0 high, 0 medium, 0 low, and 2 information items.
- **Recommendation (stop rule):** No finding is medium or higher, so closure of change-b170cf6a and issue-b170cf6a is recommended. The lifecycle steps are listed in §7.0 and have not been performed.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Independence and Method

- This session is not the implementing session. The `iteration_3` block (changes, test_results, behaviour_notes) was treated as a claim. None of the implementer's tests or shims were reused: the implementer's P-B2 used a `cmp` shim, and this check used a `date` shim. All cases in §6.0 were built for this check.
- **Environment:** Cowork Linux VM on the operator's machine (aarch64, GNU bash 5.1.16, rsync 3.2.7, GNU find, sort and xargs), running as a non-root user.
- **Framework copies:** A `git clone --no-local` of the repository at `4fc0538` was made in scratch space outside the repository. Iteration 2 ran from a detached worktree of that clone at `1b7f068` (blob `afc41f8`) for side-by-side comparison.
- **Targets:** Throwaway directories built from `git archive HEAD ai`, with `ai/primer.md` replaced by the older framework blob at `dd58ce0`. This makes it a planned `update` with no backup. The script was never run against a real project.
- **Prompt races:** A Python pty driver waited for `Apply changes?`, ran a mutation, and then answered. Action-time and plan-time events were injected with PATH shims for `date`, `cksum`, `sort`, `find`, `xargs`, `readlink`, `cp` and `rsync`.
- **Repository access:** Read-only, and every git command used `--no-optional-locks`. After the reads the tree is clean and `.git/index.lock` is absent. This report is the only file added.
- **Not exercised:**
  - macOS, APFS and bash 3.2. A bash 3.2.57 source download was refused by the egress proxy, so bash 3.2 compatibility was checked by static reading only (§4.2).
  - The operator's `macos_results` for iteration 3 are taken as operator evidence: (1) prompt race on a real `ai/`, (2) prompt race on a symlinked `ai/`, (3) `sort -z` supported. Check (2) records rc=3 but not the message. Because the prompt was reached, the pre-plan snapshot, including `readlink -- ai`, succeeded on macOS.
  - B2 (a post-plan edit), B3 (an injected failure), B4 and B5 have no macOS evidence.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Status of B1 to B5

### 3.1 B1 to B4

| ID | Status | Evidence |
|---|---|---|
| B1 | Resolved | P-B1: symlinked `ai/` → `real-ai/`, older `primer.md`, a line appended during the prompt. Iteration 2: exit 0, and the text is found nowhere. Iteration 3: exit 3, text intact. P-B1n (new file created in `real-ai/` during the prompt) and P-B1r (`ai` link retargeted during the prompt) → exit 3; the retarget directory was not updated. P-B1c (real `ai/`) → exit 3, intact. |
| B2 | Resolved | P-B2d: a `date` shim appends to `primer.md` on the first `date` call (`STAMP`, line 321, after plan and before the preview). Iteration 2: exit 0, edit lost. Iteration 3: exit 3, edit intact. |
| B2 (audit variant) | Acceptable | P-B2c: the audit's original `cksum` shim edits `primer.md` on the first call. That call is now inside the pre-plan baseline, so plan reads the edited file. The preview lists `backup primer.md → ai-local/primer.md (local modification)`, and the backup equals the old `primer.md` plus the edit, byte for byte. Exit 0. The file is overwritten, but the edit is not lost. The operator sees the backup in the preview before confirming. This is the same outcome as an edit made before the run started, so it is acceptable. |
| B3 | Resolved | P-B3a: `sort` rejects `-z` from the start → "cannot snapshot", exit 3 before the prompt; the target is byte-identical. P-B3b to P-B3f: `sort`, `find`, `cksum`, `xargs` or (symlinked `ai/`) `readlink` fail only after the prompt, with an edit made during the prompt → exit 3 each time, edit intact. |
| B4 | Resolved | P-B4: `context.md` → `../ctx.md` (an existing regular file). Iteration 2: exit 3. Iteration 3: exit 0, "existing project copy preserved", the link and its target unchanged, and `primer.md` updated. P-B4t: `task.md` → an absolute path, `--yes` → exit 0, link and target unchanged. The header (lines 102–104) and guide-install §3.3 match this behaviour. |

- **Residual in the reasoning (inference, high confidence):** In interactive mode, an edit to an existing file is either read into the baseline, in which case plan sees it and backs it up, or made after that file's checksum, in which case `SNAP_AFTER` differs and the run exits 3. No interval remains between baseline and prompt. The `--yes` window is unchanged and was accepted earlier.

### 3.2 B5 — Interactive refusal on unreadable content

- **Reproduced:** An interactive run exits 3 before plan, with no preview. The message is `find: './state/x': Permission denied` followed by "cannot snapshot ai/ or ai-local/ for the prompt guard". Nothing is applied. `--yes` proceeds with exit 0 in every case.

| Case | Iteration 2 (interactive) | Iteration 3 (interactive) | Iteration 3 `--yes` |
|---|---|---|---|
| Mode 000 `state/x` (F3), update pending | Prompt, exit 0 | Exit 3, nothing applied | Exit 0 |
| Mode 000 `state/x`, target up to date | "Up to date", exit 0 | **Exit 3** | Exit 0 |
| Mode 000 file `state/f` | Prompt, exit 0 | Exit 3 | Exit 0 |
| Mode 000 `workspace/y` | Prompt, exit 0 | Exit 3 | Exit 0 |
| Mode 000 `ai-local/z` | Prompt, exit 0 | Exit 3 | Exit 0 |
| Mode 000 framework file (`ai/doc/…`) | Prompt, then exit 3 | Exit 3 before the prompt | Exit 3 |

- **Scope:** B5 is broader than the directory case recorded in the change: an unreadable *file* has the same effect, because `cksum` fails. It matters only under declared paths (`workspace/`, `state/`, `logs/`) and `ai-local/`. Elsewhere in `ai/`, unreadable content already refuses in both modes (A2 enumeration, or the failed backup copy).
- **Severity: low.** Reasons:
  - The failure is in the safe direction. Nothing is applied, no content is lost, and the exit is 3 with a message naming the path.
  - It is a contract and usability defect. An interactive run on an up-to-date target now exits 3 instead of 0, and interactive and `--yes` runs disagree on the same target.
  - The trigger is uncommon: an unreadable entry that the operator's own user owns, or a root-owned file in `state/` or `logs/`. Concurrent AEL writes that delete files during the snapshot would probably produce the same message rather than "changed" (inference, not reproduced; verify by deleting a `state/` file from a `cksum` shim).
  - The refusal adds no protection. The script never writes declared directories (they are excluded from rsync and pruned from plan). A1 concerns the top-level `context.md` and `task.md`, which stay in the snapshot either way.
  - Documentation partly covers it: guide-install §3.3 says the script refuses "if a directory cannot be listed". It does not mention files or declared directories, or that only interactive runs are affected.
  - The workaround is to restore permissions. `--yes` also works but drops the prompt guard.
- **Recommendation: accept** for this change (disposition `accepted`, severity `low`). A fix is optional and can be a separate triple. The minimal form would be for `snapshot()` to record only the entry and type of `workspace`, `state` and `logs`, pruned as `list0` does. That change would also remove the P-N4 surprise (exit 3 on AEL writes) and the read cost of large `logs/` trees. It changes guard behaviour, so it would need its own check.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 New Routes Introduced by Iteration 3

### 4.1 Content loss and changes applied after a target change

- **None found.** Checked from the diff and by experiment:
  - Between `SNAP_BEFORE` (line 307) and `SNAP_AFTER` (line 468), the script writes nothing under `ai/` or `ai-local/`. `WORK` is `mktemp -d` outside the target. The up-to-date, declined and plain-apply cases behave as before.
  - B4 does not reopen A6. `NEEDS_SEED_*` uses `-f` (line 400), so a link to an existing file is never seeded. If that link becomes dangling after planning, it is still not seeded. Dangling links and links to directories refuse (A6 regression cases).
  - `snapshot()` follows only `ai/`. `ai-local/` as a symlink is recorded only, as in iteration 2.
- **Information I1, FIFO at `ai-local`:** `cksum < "${d}"` (line 282) blocks on a FIFO, so an interactive run hangs until interrupted, with nothing applied. Iteration 2 had the same line at prompt time and hung in the update case. Because the baseline now runs before plan, iteration 3 also hangs when the target is up to date. The layout is contrived and the failure is in the safe direction.
- **Information I2, version gate before the baseline:** `DST_VER` (line 93) is read before the baseline. An edit to the target `governance.md` in that interval changes only the major-version warning and gate. The edit itself is baselined and handled by plan.

### 4.2 bash 3.2 (static reading of the diff)

- Every construct is available in bash 3.2: `local d l` declared apart from the assignment, so the status of `$(readlink …)` is kept; `: >`, `printf`, `[[ -L/-d/-e/-f ]]`, `{ …; } >>`, backslash-continued `&&` chains in a subshell, `-t 0`, and `var="$(f)" && [[ … ]] || f`. `pipefail` exists since bash 3.0, so `find | sort -z` failures propagate.
- External tools on macOS: `find -print0`, `-exec readlink {} \;`, `xargs -0` and `cksum` are present in BSD userland. `sort -z` is confirmed by the operator (3), and `readlink --` is implied by operator check (2). BSD `xargs` does not run `cksum` on empty input, whereas GNU `xargs` does. Either way the output is consistent within one platform, and the before and after snapshots only need to match each other.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 T08 Record

```yaml
audit_info:
  id: "audit-b170cf6a-closure"
  title: "Closure check of change-b170cf6a iteration 3 — bin/propagate.sh B1 to B5"
  date: "2026-09-23"
  mode: "strategic"
  status: "complete"
  auditor: "Strategic Domain (Claude, Cowork; independent session — not the implementing session)"

scope:
  target: "bin/propagate.sh at 51611db (iteration-3 diff 1b7f068..51611db); change-b170cf6a iteration_3 (changes, test_results, macos_results, open_findings B5); issue-b170cf6a"
  criteria:
    - "status of audit-b170cf6a-final findings B1 to B4"
    - "severity and disposition of open finding B5"
    - "no new route to content loss or to applying changes after a target change in the iteration-3 diff"
    - "bash 3.2 compatibility of the diff (static)"
    - "regression spot checks: A1 seeding guard, A3 no-clobber, A6 dangling symlink, up to date"
  exclusions:
    - "P-N3 nested empty-directory exit 4; orphan .propagate-tmp file"
    - "Accepted residuals: C1 bytes, ai/Templates/, performance"
    - "Behaviour outside the iteration-3 diff"
    - "macOS / APFS / bash 3.2 execution (operator evidence only)"
    - "Real downstream projects (not accessed)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - location: "bin/propagate.sh:288-293 (snapshot), 303-308"
      description: >
        B5 (operator-raised; severity assigned here). An interactive run exits 3
        before plan when any directory or file under a declared path or
        ai-local/ cannot be read, including on an up-to-date target (iteration
        2: exit 0). --yes proceeds. Safe direction; nothing applied.
        Disposition: accept.
      issue_ref: "issue-b170cf6a"
  information:
    - location: "bin/propagate.sh:280-282"
      description: >
        I1. A FIFO at ai-local blocks cksum; an interactive run hangs with
        nothing applied. Pre-existing at prompt time; now also for an
        up-to-date target.
    - location: "bin/propagate.sh:93, 307"
      description: >
        I2. The target governance version is read before the baseline; only
        the major-version gate is affected.

metrics:
  items_audited: 5
  findings_total: 1
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 1

recommendations:
  - "Close change-b170cf6a and issue-b170cf6a (stop rule met: no finding medium or higher)."
  - "Record B5 as severity low, disposition accepted, in change-b170cf6a iteration_3.open_findings."
  - "Optional, separate triple: prune workspace/state/logs in snapshot() to entry and type (resolves B5, P-N4 and the read cost)."
  - "Optional, operator: on macOS, one post-plan edit case (date shim) and one B4 case (context.md -> existing file)."

traceability:
  design_refs:
    - "ai/governance.md P10.6 (10.5), P02.8, P00.14"
  issue_refs:
    - "issue-b170cf6a (coupled)"
  related_audits:
    - audit_ref: "dev/audit/audit-b170cf6a-final-2026-09-23.md"
      relationship: "follow_up"
    - audit_ref: "dev/audit/audit-b170cf6a-recheck-2026-09-23.md"
      relationship: "related"

notes: >
  B1 to B4 behave as claimed in all own reproductions. B5 fails closed and
  adds no protection; it is a low-severity contract inconsistency.

closure:
  recommended: true
  approver: "William Watson"
  approval_date: "2026-09-23"

version_history:
  - version: "1.0"
    date: "2026-09-23"
    changes:
      - "Initial closure check report"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Experiments

"it3" is `51611db`; "it2" is `1b7f068`. "Prompt" means the mutation ran while `Apply changes?` was open. Unless noted, the target has an older framework `primer.md`, planned as `update`.

| Case | Setup | it3 observed | it2 |
|---|---|---|---|
| P-B1 | Symlinked `ai/`; prompt; append to `real-ai/primer.md` | Exit 3; intact | **Exit 0; lost** |
| P-B1n | Symlinked `ai/`; prompt; create `real-ai/notes.md` | Exit 3; intact | — |
| P-B1r | Symlinked `ai/`; prompt; retarget `ai` → `other-ai` | Exit 3; `other-ai` not updated | — |
| P-B1c | Real `ai/`; prompt; append to `primer.md` | Exit 3; intact | — |
| P-B2d | `date` shim appends to `primer.md` after plan | Exit 3; intact | **Exit 0; lost** |
| P-B2c | `cksum` shim appends on its first call (audit variant) | Backed up (`local modification`) = old + edit; exit 0 | Exit 0; lost |
| P-B3a | `sort` rejects `-z` from the start | Exit 3 before the prompt; target byte-identical | — |
| P-B3b–e | `sort` / `find` / `cksum` / `xargs` fail after the prompt; prompt edit | Exit 3; intact | — |
| P-B3f | Symlinked `ai/`; `readlink` fails after the prompt; prompt edit | Exit 3; intact | — |
| P-B4 | `context.md` → `../ctx.md` (existing file) | Exit 0; link and target unchanged; applied | Exit 3 |
| P-B4t | `task.md` → absolute path; `--yes` | Exit 0; link and target unchanged | — |
| B5 (×6) | Mode 000 dir or file under `state/`, `workspace/`, `ai-local/`; framework file | See §3.2 | See §3.2 |
| A1 | `context.md` absent; prompt; create it | Exit 3; project text intact | — |
| A1s | `--yes`; `rsync` shim creates `context.md` | "Appeared during the run; not seeded"; text intact; exit 0 | — |
| A3 | Edited `workflow.md`; `cp` shim writes user file at `ai-local/workflow.md` | Exit 3; user file intact; FAILED row; `ai/workflow.md` not overwritten | — |
| A6 | `context.md` dangling; `context.md` → directory | Exit 3; nothing created; not applied | — |
| Up to date | Current `primer.md`; interactive and `--yes` | Exit 0 both | — |
| Declined / non-TTY | Answer `n`; stdin `/dev/null` without `--yes` | Exit 0 / exit 2 | — |
| I1 | FIFO at `ai-local`; up to date / update | Hangs (killed at 10 s); not applied | Up to date: exit 0 / update: hangs |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Closure Recommendation

- **Recommendation:** Close change-b170cf6a and issue-b170cf6a.
- **Reason:** B1 to B4 are resolved, with independent reproductions. B5 is low, fails closed and is recommended for acceptance. No new route to content loss or post-change application was found in the iteration-3 diff. No finding is medium or higher, so the stop rule is met.
- **Limitation:** macOS execution evidence covers B1 and the basic prompt race only (§2.0).
- **Lifecycle steps (not performed; after operator acceptance, per P00.14.4 and P02.8):**
  1. **Operator approval:** record the approver and date in this report's `closure` block.
  2. **change-b170cf6a:** set `status: "verified"`. In `iteration_3.open_findings` B5, set `severity: "low"` and `disposition: "accepted"`, with a reference to this report. Set `verification.verified_by` to this report, and fill in `verification_date` and `test_results` (summary of §6.0). Add Version History 3.3.
  3. **issue-b170cf6a:** set `status: "closed"`, and fill in `verification` (`verified_date`, `verified_by` = this report, `test_results`, `closure_notes`: "B1–B4 resolved; B5 low, accepted"). Add Version History 3.2.
  4. **Move the triple:**
     - `dev/issue/issue-b170cf6a-…` → `dev/issue/closed/`
     - `dev/change/change-b170cf6a-…` → `dev/change/closed/`
     - `dev/prompt/prompt-b170cf6a-…` → `dev/prompt/closed/`
  5. **Move the audits** to `dev/audit/closed/`: `audit-b170cf6a-recheck-2026-09-23.md`, `audit-b170cf6a-final-2026-09-23.md` and this report.
  6. **dev/backlog.md §6.0:** replace the "Blocked until the final re-check of change-b170cf6a" gate with the closure outcome (propagation unblocked).
  7. **Commit:** one git commit records the closure transition.
- **Human approval:** pending operator decision.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial closure check report |

---

Copyright (c) 2026 William Watson. MIT License.
