Created: 2026 September 23

# Final Re-check Audit — change-b170cf6a Iteration 2

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Independence and Method](<#2.0 independence and method>)
[3.0 Status of A1 to A7](<#3.0 status of a1 to a7>)
[4.0 New Routes Introduced by Iteration 2](<#4.0 new routes introduced by iteration 2>)
[5.0 T08 Record](<#5.0 t08 record>)
[6.0 Experiments](<#6.0 experiments>)
[7.0 Closure Recommendation](<#7.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** `bin/propagate.sh` at `45ac716` (blob `afc41f8`, unchanged at HEAD `e04c43c`); the iteration-2 diff against `b39d01f` only.
- **A1 to A7:** 7 resolved. For A7, the case-variant framework directory residual is accepted as documented.
- **New findings:** 0 critical, 0 high, 1 medium, 3 low.
- **Medium (B1):** The new snapshot does not descend into `ai/` when `ai/` is a symlink. An edit made during the prompt is then overwritten without a backup, and the run exits 0. Iteration 1 refused the same case with exit 3, so this is a regression introduced by iteration 2.
- **Recommendation (stop rule):** A finding is medium, so change-b170cf6a should not be closed. The fix is small and local (§7.0).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Independence and Method

- The `iteration_2` block of the change document was treated as a claim. None of the implementer's tests were reused. The cases in §6.0 were built for this check.
- **Environment:** Cowork Linux VM on the operator's machine (aarch64, GNU bash 5.1.16, rsync 3.2.7, GNU userland). The framework was a `git clone --no-local` of the repository at `e04c43c`. A worktree at `b48bd40` (iteration 1) was used for comparison. Targets were throwaway directories built from `git archive HEAD ai` (10.5) or `git archive pre-eb782f83 ai` (9.16). The script was not run against any real project.
- **Prompt races:** A Python pty driver waited for `Apply changes?`, ran a mutation in the target, and then answered `y`. Action-time races were injected with PATH shims for `cp`, `rsync`, `cksum` and `sort`.
- **Not exercised:** macOS, APFS and bash 3.2. The operator's `macos_results` (6 checks at `45ac716`) are taken as operator evidence. `/tmp/macos-check.out` is on the Mac and not reachable from the VM, so it was not read. None of the six operator checks covers the confirmation prompt, so the snapshot guard is unverified on macOS (see B3).
- **Repository side effects:** An early read-only `git status` refreshed `.git/index` (stat data only), and a later one left an empty `.git/index.lock` because the mount did not allow the unlink. With the operator's approval, the lock was removed and the tree was confirmed clean. This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Status of A1 to A7

| ID | Status | Evidence |
|---|---|---|
| A1 | Resolved | P-A1, P-A1b: `context.md` or `task.md` created during the prompt → exit 3, project text intact. S-A1: `context.md` created after the prompt (rsync shim, `--yes`) → "appeared during the run; not seeded", project text intact, exit 0. There are two independent layers. |
| A2 | Resolved | F2 (mode 300 `templates/` with an edit) and F1 (mode 000 project directory) → exit 3 before any change, edit intact. F3: unlistable `state/x` is pruned and the run proceeds. F4 (mode 600 directory: listable, not searchable) → `mv` fails, FAILED row, exit 3 before the copy. |
| A3 | Resolved | P-A3 (file at `ai-local/primer.md` during the prompt) and P-A3g (`ai-local` symlink during the prompt) → exit 3; nothing written outside. S-A3 and S-A3s (file or symlink placed at the destination just before `mv -n`) → exit 3; user file and outside file intact. Residual: an orphan `.propagate-tmp.*` is left in `ai-local/` (information). |
| A4 | Resolved | P-A4: retired 9.16 template edited during the prompt → exit 3, nothing applied. The pre-prompt window is not covered (B2); only labels are affected there. |
| A5 | Resolved | R16 repeated: a blob only on a non-default framework branch → `local modification` backup containing the text. Line 184 uses `git log HEAD`. |
| A6 | Resolved | A dangling symlink at `context.md` or `task.md` → exit 3 before any change; nothing created at the link target. The refusal is broader than needed (B4). |
| A7 | Resolved; residual accepted as documented | Linux: `Context.md`, `TASK.md`, `Workspace/`, `AEL/config.yaml`, `Dashboard-Alerts.md`, `Logs/`, `State/` and an `AEL` symlink each refused with "differs … only by letter case". Operator macOS (5): `ai/Context.md` → exit 3, intact. The `ai/Templates/` residual is observed by the operator (6) and documented in guide-install §3.3. |

- **N-08 residual (C1 bytes):** recorded in the change document as accepted. It is outside A1–A7 and was not re-tested.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 New Routes Introduced by Iteration 2

### 4.1 Content loss and changes applied after a target change

- **B1 (medium), symlinked `ai/` is not snapshotted:** `snapshot()` (lines 264–278) prints only `link <target>` for any `-L` root, and that includes `PROJECT_AI`. Every other step follows the link: the `-d` guard (line 68), `list0` (`cd`), and `rsync … "${PROJECT_AI}/"`. P-B1: `ai` → `real-ai`; `primer.md` holds an older framework version (planned as `update`, no backup); a line is appended during the prompt. Iteration 2 exits 0, and the text is found nowhere. Iteration 1 (`b48bd40`) exits 3 with the text intact. The seed-time guard (A1) and the no-clobber backup (A3) still protect their own cases, so the loss is limited to edits to planned `update` files and to files not planned at all. The severity matches A2 in the previous audit: an uncommon layout, a plausible operator action, and silent loss with exit 0.
- **B2 (low), baseline taken after the plan:** `SNAP_BEFORE` (line 431) is taken after `plan`, after the preview and after the snapshot has run. An edit made after a file has been planned and before the snapshot completes becomes part of the baseline. P-B2 (a `cksum` shim edits `primer.md` on the first snapshot call) → exit 0, edit lost. Iteration 1's re-plan after the prompt covered this interval. The window is bounded: it lasts as long as the plan, the preview and the snapshot, which is seconds for large trees, and the prompt has not yet been shown. It is comparable to the `--yes` window accepted earlier.
- **B3 (low), snapshot fails open:** All errors inside `snapshot()` are discarded (`2>/dev/null`, `|| true`), and the output is never validated. P-B3: with `sort -z` rejected (shim), an edit made during the prompt was applied with exit 0 and lost. The operator's macOS run did not exercise the prompt path, so the support of `/usr/bin/sort -z` on macOS is not evidenced. As far as I know, both the older GNU-derived sort and the current BSD-derived sort on macOS accept `-z` (confidence moderate). It can be verified with `printf 'b\0a\0' | LC_ALL=C /usr/bin/sort -z | od -c`.

### 4.2 Other effects

- **B4 (low), A6 refusal over-broad:** Lines 358–362 refuse any symlink at `context.md` or `task.md`, including a valid symlink to an existing file. Iteration 1 preserved such a link, with exit 0 (P-B4). No seeding was due in that case. This contradicts the header comment at line 101 ("a symlink at a declared path is protected too"), and guide-install §3.3 does not list this refusal. The effect is in the safe direction.
- **Information:**
  - `snapshot()` reads declared directories, so AEL or govwatch writes during the prompt cause exit 3 (P-N4). This is safe and may surprise the operator. The iteration-2 note "declared directories are … never read" applies to `list0` only.
  - The cleanup `find` was changed from `-depth` to `-prune … | sort -rz`. Behaviour is unchanged against iteration 1. A directory at a framework file path whose relocated content leaves empty directories two or more levels deep gives exit 4 in both iterations (P-N3). This is pre-existing and was not re-audited.
  - bash 3.2 (static reading): the new constructs are 3.2-compatible. The operator's macOS check (2) exercised the new no-clobber backup path under bash 3.2 with rc=0.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 T08 Record

```yaml
audit_info:
  id: "audit-b170cf6a-final"
  title: "Final re-check of change-b170cf6a iteration 2 — bin/propagate.sh A1 to A7"
  date: "2026-09-23"
  mode: "strategic"
  status: "complete"
  auditor: "Strategic Domain (Claude, Cowork; independent session — not the implementing session)"

scope:
  target: "bin/propagate.sh at 45ac716 (iteration-2 diff vs b39d01f); change-b170cf6a iteration_2 and macos_results blocks"
  criteria:
    - "status of audit-b170cf6a findings A1 to A7"
    - "no new route to content loss introduced by iteration 2"
    - "no new route to applying changes after a target change during the prompt"
  exclusions:
    - "Behaviour outside the iteration-2 changes"
    - "macOS / APFS / bash 3.2 execution (operator evidence only)"
    - "Real downstream projects (not accessed)"

findings:
  critical: []
  high: []
  medium:
    - location: "bin/propagate.sh:264-278 (snapshot), 431-441"
      description: >
        B1. snapshot() records only the link target when ai/ is a symlink,
        while the rest of the script follows the link. An edit made during
        the prompt to a planned 'update' file is overwritten without backup,
        exit 0 (P-B1). Iteration 1 refused this with exit 3. Regression.
      issue_ref: ""
  low:
    - location: "bin/propagate.sh:282, 431"
      description: >
        B2. SNAP_BEFORE is taken after plan and preview; an edit between a
        file's planning and the snapshot is baselined and overwritten without
        backup (P-B2). Window bounded to plan+preview+snapshot duration.
    - location: "bin/propagate.sh:264-278"
      description: >
        B3. snapshot() suppresses all errors and is not validated; a failing
        sort -z or find silently disables the prompt guard (P-B3). macOS
        prompt path not exercised.
    - location: "bin/propagate.sh:358-362; 101; docs/guide-install.md §3.3"
      description: >
        B4. Any symlink at context.md or task.md is refused, including a valid
        one that iteration 1 preserved (P-B4). Contradicts line 101; refusal
        not listed in guide-install.

metrics:
  items_audited: 7
  findings_total: 4
  findings_by_severity:
    critical: 0
    high: 0
    medium: 1
    low: 3

recommendations:
  - "Keep change-b170cf6a open (stop rule: B1 is medium). Iteration 3, limited to snapshot():"
  - "B1: snapshot PROJECT_AI through the link (apply the -L branch to ai-local only), or refuse a symlinked ai/ with exit 3."
  - "B2: take SNAP_BEFORE before plan (interactive mode)."
  - "B3: fail closed — check the snapshot pipeline status and exit 3 on error."
  - "B4: refuse only when seeding would follow the link (not a regular file behind it), or document the refusal in the header and guide-install."
  - "Operator: run one prompt-race case on macOS (edit a file during the prompt → expect exit 3)."

traceability:
  design_refs:
    - "ai/governance.md P10.6 (10.5), P02.8"
  issue_refs:
    - "issue-b170cf6a (coupled); B1 to B4 not yet raised"
  related_audits:
    - audit_ref: "dev/audit/audit-b170cf6a-recheck-2026-09-23.md"
      relationship: "follow_up"

notes: >
  A1 to A7 behave as claimed in all tested cases. The single medium finding is
  a regression in the new snapshot mechanism for one layout; the fix is local.

version_history:
  - version: "1.0"
    date: "2026-09-23"
    changes:
      - "Initial final re-check report"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Experiments

"it2" is `45ac716`; "it1" is `b48bd40`. "Prompt" means the mutation ran while `Apply changes?` was open.

| Case | Setup | it2 observed | it1 |
|---|---|---|---|
| P-A1, P-A1b | Prompt; create `context.md` / `task.md` | Exit 3; text intact | — |
| S-A1 | `--yes`; rsync shim creates `context.md` | Not seeded; text intact; exit 0 | — |
| F1, F2 | Mode 000 `proj/`; mode 300 `templates/` with edit | Exit 3 before change; edit intact | — |
| F3, F4 | Mode 000 `state/x`; mode 600 `proj/` | Proceeds, exit 0; FAILED row, exit 3 | — |
| P-A3, P-A3g | Prompt; file at `ai-local/primer.md`; `ai-local` symlink | Exit 3; nothing written outside | — |
| S-A3, S-A3s | `cp` shim places file / symlink at the backup destination | Exit 3; user file and outside file intact; orphan tmp | — |
| P-A4 | 9.16; prompt; edit retired `T01-design.md` | Exit 3 | — |
| A5 | `primer.md` = blob on a non-default framework branch | Backed up | — |
| A6 | Dangling symlink at `context.md` / `task.md` | Exit 3; nothing created | — |
| A7 | 7 case variants + `AEL` symlink | All refused, exit 3 | — |
| P-B1 | Symlinked `ai/`; older framework `primer.md`; prompt edit | **Exit 0; edit lost** | Exit 3; intact |
| P-B1c | As P-B1 with a real `ai/` directory | Exit 3; intact | — |
| P-B2 | `cksum` shim edits `primer.md` before the baseline | **Exit 0; edit lost** | (covered by re-plan) |
| P-B3 | `sort` shim rejects `-z`; prompt edit | **Exit 0; edit lost** | — |
| P-B4 | Valid symlink `context.md` → existing file | Exit 3 | Exit 0; preserved |
| P-N3 | `workflow.md/a/b/n.md` + `__pycache__` | Exit 4 | Exit 4 |
| P-N4 | Prompt; write `state/ralph.json` | Exit 3 | — |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Closure Recommendation

- **Recommendation:** Do not close change-b170cf6a or issue-b170cf6a yet.
- **Reason:** A1 to A7 are resolved. However, iteration 2 replaced a guard that covered symlinked `ai/` (the iteration-1 re-plan) with one that does not. The result is silent content loss with exit 0 (B1, medium). Under the operator's stop rule, one medium finding blocks closure.
- **Path:**
  - Iteration 3, limited to `snapshot()` and its call site: B1 required; B2 and B3 are recommended because they touch the same few lines; B4 is either fixed or documented.
  - Closure check limited to P-B1, P-B2 and P-B3 plus one macOS prompt-race case. If these pass and nothing is medium or higher, close.
- **Human approval:** pending operator decision.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial final re-check report |

---

Copyright (c) 2026 William Watson. MIT License.
