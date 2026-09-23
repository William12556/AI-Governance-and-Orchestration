Created: 2026 September 23

# Re-check Audit — change-b170cf6a (propagate.sh follow-up fixes)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Independence and Method](<#2.0 independence and method>)
[3.0 Status of N-01 to N-08](<#3.0 status of n-01 to n-08>)
[4.0 Attack on the Claims](<#4.0 attack on the claims>)
[5.0 T08 Record](<#5.0 t08 record>)
[6.0 Experiments](<#6.0 experiments>)
[7.0 Closure Recommendation](<#7.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** `bin/propagate.sh` at `b48bd40` (blob `e0188366`, mode 100755), change-b170cf6a iteration 1.
- **N-01 to N-08:** 5 resolved (N-01, N-03, N-04, N-05, N-07); 2 partially resolved (N-02, N-08); 0 not resolved.
- **Claim "no project content is lost, including local edits":** Holds for the cases N-01 described. It is refuted in three other ways. A declared file created during the prompt is overwritten by seeding (A1). A local edit in a directory that `find` cannot list is overwritten without a backup, and the run exits 0 (A2). A file in `ai-local/` created during the prompt is overwritten by the backup `cp`, or the `cp` writes through a symlink outside the project (A3).
- **Claim "nothing is applied if the target changes during the prompt":** Holds only for changes to the path lists outside declared paths and outside `ai-local/`. It is false for declared files (A1), for `ai-local/` (A3) and for content changes to planned entries (A4).
- **New findings:** 0 critical, 0 high, 2 medium, 5 low.
- **Recommendation:** Do not close change-b170cf6a yet. Fix A1 and A2 (medium) in iteration 2, with a follow-up re-check. The low findings may be fixed in the same iteration or accepted in writing. The macOS procedure is still outstanding.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Independence and Method

- The change document was read as a claim. None of the implementer's tests (X1–X13 re-runs) or results were reused. The cases in §6.0 were built for this re-check.
- **Environment:** Cowork Linux VM on the operator's machine (aarch64, GNU bash 5.1.16, rsync 3.2.7, GNU coreutils). The framework was a `git clone --no-local` of the repository at `b48bd40`, placed in a throwaway directory. Targets were throwaway directories made from `git archive HEAD ai` (10.5) or `git archive pre-eb782f83 ai` (9.16) and then `git init`-ed. The script was not run against any real project.
- **Oracle:** Each target (`ai/` and `ai-local/`) was snapshotted before and after a run as a set of git blob hashes. Content counts as lost when a non-empty pre-run blob is absent after the run and is not an object in the framework clone. Content introduced during a prompt was checked directly with `grep`.
- **Prompt races:** A Python pty driver waited for `Apply changes?`, ran a mutation in the target, and then answered `y`.
- **Not exercised:** macOS (APFS case-insensitivity, BSD userland, `/usr/bin/rsync` as openrsync) and bash 3.2. In the cloud container, loop mounts worked, but the kernel has no ext4 casefold support and no FUSE library was available. The egress policy blocked the bash 3.2 source (ftp.gnu.org and GitHub). N-02 and the macOS items below therefore rest on static reading.
- **Repository side effects:** Read-only commands only (`git log`, `git show`, `git status`). No `.git/index.lock` remained (checked). This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Status of N-01 to N-08

| ID | Status | Evidence |
|---|---|---|
| N-01 | Resolved | R1a: local edits to `primer.md` and to the uncommitted `templates/T02-design.md` were backed up with the label `local modification`, the framework copy was applied, 0 lost, exit 0. R1b: an older framework `primer.md` was updated without a backup, and its content remains in framework history. R2a and R2b: a framework file edited during the prompt, or a new file created during it, gave exit 3 with nothing applied. Adjacent loss paths that N-01 did not describe are recorded as A1–A3. |
| N-02 | Partially resolved | Static reading: `exact_exists` (lines 140–154) compares directory entries byte for byte, so `Primer.md` is not treated as the source's `primer.md`; it becomes a candidate and is relocated. Not exercised (§2.0). Adjacent case-variant effects are inferred in A7. |
| N-03 | Resolved | No rsync output is parsed (no `--itemize-changes`, no dry run). N03a: a stale `workflow.md` was applied, not reported as up to date. N03b: an rsync shim returning 23 gave exit 4 with a message after the relocations were logged. |
| N-04 | Resolved | `dirname --` at lines 34, 290 and 423. N04: `ai/-x.md` and `ai/--` were relocated, exit 0. |
| N-05 | Resolved | (a) N05a: a `RELOCATED.md` candidate got a suffix on the first run, exit 0. (b) N05b: an existing suffix `-1-1` led to `-1-2`. (c) N05c: `ai-local/RELOCATED.md` as a directory gave exit 3, nothing applied. (d) N05d: `.DS_Store`, `__pycache__/m.pyc` and `notes.txt` in `ai/workflow.md/` were relocated, the directory was removed and the framework file placed, exit 0. Copy failure → exit 4 (N03b). A new exit-contract gap in seeding is recorded as A6. |
| N-06 | Resolved | N06: a stash-only blob was labelled `project content`. Line 183 uses `--branches --tags --remotes HEAD`. The residual reliance on non-default refs is recorded as A5. |
| N-07 | Resolved | N07a: a symlinked `ai/ael` holding `config.yaml` gave exit 3 before any change; the link was intact and `ai-local/` was not created. N07b: a relative symlink was relocated and its log row carries the note. A directory at a declared file name remains unchanged, as scoped out by the change (no content lost). |
| N-08 | Partially resolved | N08a: a FIFO at `workflow.md` was relocated intact. ESC was masked in the preview under `C.UTF-8` and `C` (N08b). Re-plan: files created at new paths gave exit 3 (R2b). The log row is written before its action (lines 421–431). Residual: the C1 CSI byte is not masked. The raw byte `0x9B` is passed through in both locales, and `U+009B` is passed through under `LC_ALL=C` (N08b). Whether a terminal interprets it depends on the terminal; the risk is low. |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Attack on the Claims

### 4.1 "No project content is lost, including local edits to framework files"

- **A1 (medium), declared file created during the prompt:** `NEEDS_SEED_*` is fixed before the prompt (lines 322–323). The re-plan skips declared paths (line 210), so creating `ai/context.md` or `ai/task.md` during the prompt leaves the fingerprint unchanged. Seeding then runs `cp` over the new file (lines 472–488). R2c and R2c2: the project text was found nowhere afterwards, exit 0. This is a plausible sequence: the preview says `seed context.md (absent in target)`, and the operator copies the real file in before answering.
- **A2 (medium), enumeration errors ignored:** Both `find` calls run in process substitutions (lines 223, 237). A `find` failure does not stop the script under `set -e`. F2: `ai/templates` with mode 300 (writable, not listable) holding an edited `T02-design.md` was not planned, not backed up, and was overwritten by rsync. The edit was lost, with exit 0 and "This script deleted nothing". F1: an unreadable project directory was neither relocated nor reported, and the result was "Target is up to date", exit 0. The trigger is uncommon, but the failure is silent.
- **A3 (low), `ai-local/` not re-validated after the prompt:** `dest_for` and `check_dir_chain` run only at plan time. The backup uses `cp -p` without no-clobber (line 429). R2e: a user file created at `ai-local/primer.md` during the prompt was overwritten and lost. R2f: a symlink created there led `cp` to overwrite a file outside the project. R2g: an `ai-local` symlink created during the prompt sent the backup and the log outside the project. Moves use `mv -n` and are not affected in this way.
- **A5 (low), trust in any ref of the framework clone:** Backup and label decisions accept a blob from any branch, tag or remote-tracking ref (line 183). R16: target content equal to a blob on a non-default framework branch was overwritten without a backup. After `branch -D` and `gc --prune=now`, the content existed nowhere.
- **Holds:** unreadable edited file (E: `cp` failed, exit 3 with a FAILED row, edit intact); idempotent second run (R1c); 9.16 → 10.5 migration with 7 retired templates relocated and 0 spurious backups (P1); empty directory at a file path replaced (ED).

### 4.2 "Nothing is applied if the target changes during the prompt"

- The fingerprint (line 240) covers only the path lists `cands`, `backups` and `updates`. It omits declared paths (A1), `ai-local/` (A3), the seeding state (A1), and the content and labels of planned entries.
- **A4 (low), stale labels:** R2d: a retired 9.16 template edited during the prompt kept the list unchanged. It was moved with the label `retired framework file` ("safe to delete") and carried the project note. No content was lost; the label invites deletion.
- The three lists are concatenated before the checksum, so a path that moves from the end of `cands` to the start of `backups` gives the same fingerprint. By reading, every such case either moves the file or fails. None loses content. This is noted only.
- `--yes` has no prompt window. The plan-to-copy interval is sub-second and was not attacked.

### 4.3 Further observations

- **A6 (low), seeding exit contract:** `-f` and `cp` follow symlinks. S: with a dangling symlink at `ai/context.md`, GNU `cp` refused and the script exited 1 ("usage") after the copy had been applied, with no summary. By reading of BSD `cp`, macOS would instead create the file at the link target, possibly outside `ai/` (inference; untested).
- **A7 (low, inference, macOS only), case-variant names:** `is_declared` and the rsync excludes are case-sensitive, while APFS is not. `ai/Context.md`, `ai/Workspace/` or `ai/AEL/config.yaml` would be relocated to `ai-local/`. The project's live file then leaves `ai/` while the summary says "existing project copy preserved". A case-variant framework directory (`ai/Templates/`) would have its framework files relocated as `project content` on every run, because rsync writes back into the same directory. No content lost.
- **Performance (information):** 1,500 files in one non-declared directory took 7.1 s under bash 5.1 (`exact_exists` is quadratic per directory). This is acceptable. bash 3.2 on macOS is expected to be slower.
- **Unverified on macOS (information):** BSD `awk -F'\t'` (label table; failure would produce spurious `local modification` backups, which is the safe direction), BSD `tr -cd '\0'`, BSD `cp` on symlinks, and bash 3.2 execution. The change document itself records that bash 3.2 was not re-run.
- **Documentation:** guide-install §3.3 says declared files "are never touched". Seeding (A1, A6) and A7 contradict this.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 T08 Record

```yaml
audit_info:
  id: "audit-b170cf6a"
  title: "Re-check of change-b170cf6a — bin/propagate.sh follow-up fixes N-01 to N-08"
  date: "2026-09-23"
  mode: "strategic"
  status: "complete"
  auditor: "Strategic Domain (Claude, Cowork; independent session — not the implementing session)"

scope:
  target: "bin/propagate.sh at b48bd40; dev/change/change-b170cf6a; ai/governance.md 10.5 P10.6; docs/guide-install.md; docs/guide-getting-started.md"
  criteria:
    - "status of audit-c5270084 follow-up findings N-01 to N-08"
    - "claim: no project content is lost, including local edits to framework files"
    - "claim: nothing is applied if the target changes during the prompt"
  exclusions:
    - "macOS execution: APFS case-insensitivity, BSD userland, openrsync (not available to this session)"
    - "bash 3.2 execution (source download blocked by egress policy)"
    - "Real downstream projects (not accessed)"

findings:
  critical: []
  high: []
  medium:
    - location: "bin/propagate.sh:210, 322-323, 389-395, 472-488"
      description: >
        A1. Seeding overwrites a declared file created during the prompt.
        Seeding need is fixed before the prompt and the re-plan skips declared
        paths, so ai/context.md or ai/task.md created while the prompt is open
        is overwritten by the template (R2c, R2c2: project text lost, exit 0).
      issue_ref: ""
    - location: "bin/propagate.sh:223, 237"
      description: >
        A2. find errors inside process substitution are ignored. Entries in an
        unlistable directory are neither backed up nor relocated. A local edit
        there is overwritten by rsync with exit 0 and 'deleted nothing' (F2);
        an unreadable project directory yields 'Target is up to date' (F1).
      issue_ref: ""
  low:
    - location: "bin/propagate.sh:271-279, 290, 389-395, 429"
      description: >
        A3. ai-local/ is not re-validated after the prompt, and the backup cp
        clobbers and follows symlinks. A file created at the backup destination
        during the prompt is overwritten (R2e); a symlink there, or an ai-local
        symlink, redirects writes outside the project (R2f, R2g).
    - location: "bin/propagate.sh:240, 307-313"
      description: >
        A4. The re-plan compares path lists only. A candidate edited during the
        prompt keeps its plan-time label, e.g. 'retired framework file'
        (safe to delete) on edited content (R2d). No content lost.
    - location: "bin/propagate.sh:183, 191-196, 218-221"
      description: >
        A5. Backup and label decisions trust blobs on any branch, tag or
        remote-tracking ref of the framework clone. Content matching a
        non-default-branch blob is overwritten without a backup; after branch
        deletion and gc it exists nowhere (R16).
    - location: "bin/propagate.sh:322-323, 472-488"
      description: >
        A6. Seeding follows symlinks. A dangling symlink at context.md or
        task.md gives exit 1 after the copy, with no summary (S, GNU cp).
        Inferred for BSD cp: the template is written at the link target,
        possibly outside ai/.
    - location: "bin/propagate.sh:102-122; macOS only"
      description: >
        A7. (Inference; untested.) Case-variant names of declared paths are not
        declared on APFS and are relocated, removing the live project file from
        ai/ while the summary reports it preserved. A case-variant framework
        directory causes framework files to be relocated as 'project content'
        on every run. No content lost.

metrics:
  items_audited: 8
  findings_total: 7
  findings_by_severity:
    critical: 0
    high: 0
    medium: 2
    low: 5

recommendations:
  - "Keep change-b170cf6a open; remediate A1 and A2 in iteration 2 (P04), then re-check."
  - "A1: include declared-file existence (context.md, task.md) in the fingerprint, or decide seeding at seed time with a no-clobber write (refuse if the file appeared)."
  - "A2: capture find's exit status (e.g. write its output to a file and check the status) and refuse with exit 3 on any enumeration error."
  - "A3: re-run the destination and log checks after the prompt; write backups no-clobber (e.g. cp to a temporary name in the same directory, then mv -n), refusing on a symlinked destination."
  - "A4 to A7: fix together with A1/A2 or record acceptance in the change document; correct guide-install 'never touched' wording (A1, A6, A7)."
  - "N-08 residual (C1 bytes): optional; mask bytes 0x80-0x9F or accept."
  - "Run the follow-up audit §8.0 macOS procedure, plus a case-variant directory (ai/Templates/) and a declared case variant (ai/Context.md), before the next downstream propagation."

traceability:
  design_refs:
    - "ai/governance.md P10.6 (10.5), P02.8"
  issue_refs:
    - "issue-b170cf6a (coupled); A1 to A7 not yet raised"
  related_audits:
    - audit_ref: "dev/audit/closed/audit-c5270084-followup-2026-09-23.md"
      relationship: "follow_up"

notes: >
  Positive results: every N-01 to N-08 scenario the change targeted behaved as
  claimed under bash 5.1 with GNU userland. No pre-existing target content was
  lost in any non-race case except A2 and A5. The exit-3 refusals left the
  tree unchanged, and relocations were logged before their actions.

version_history:
  - version: "1.0"
    date: "2026-09-23"
    changes:
      - "Initial re-check report"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Experiments

"10.5" means `git archive HEAD ai`; "9.16" means `git archive pre-eb782f83 ai`. Every run used `--yes` unless it is marked "prompt".

| Case | Setup | Observed |
|---|---|---|
| R1a | 10.5; line appended to `primer.md` (committed base) and to `templates/T02-design.md` | 2 backups labelled `local modification`; framework in place; 0 lost; exit 0 |
| R1b | 10.5; `primer.md` from `5a502e4` | `update primer.md`; no backup; exit 0 |
| R1c | Re-run on R1a | "Target is up to date"; exit 0 |
| R2a | Prompt; edit `index.md` at prompt | Exit 3; edit intact |
| R2b | Prompt; create `ai/new.md` at prompt | Exit 3; file intact |
| R2c, R2c2 | Prompt; `context.md` / `task.md` absent; create with project text at prompt | Seeded over; project text nowhere; exit 0 |
| R2d | Prompt; 9.16; append to retired `templates/T01-design.md` at prompt | Moved with label `retired framework file`; note present in the moved file |
| R2e | Prompt; edited `primer.md`; create `ai-local/primer.md` at prompt | Overwritten by the backup; user text nowhere; exit 0 |
| R2f | As R2e with a symlink to a file outside the target | Outside file overwritten with the backup |
| R2g | Prompt; `ai-local` created as a symlink to an outside directory | `RELOCATED.md` and the backup written outside |
| R16 | Target `primer.md` equals a blob on framework branch `exp` | `update`, no backup; after `branch -D`, `gc`: content nowhere |
| E | Edited `primer.md`, mode 000 | Exit 3, FAILED row, edit intact |
| F1 | `ai/proj/` mode 000 | find error; "Target is up to date"; not relocated |
| F2 | `ai/templates` mode 300 with edited `T02-design.md`; `ai/notes.md` | notes relocated; T02 edit overwritten; exit 0 |
| S | Dangling symlink at `ai/context.md` | Copy applied; `cp` refuses; exit 1 |
| N03a | 10.5; committed `workflow.md` = "stale" | Backed up and updated |
| N03b | rsync shim exit 23 | Backup done; exit 4 with message |
| N04 | `ai/-x.md`, `ai/--` | Relocated; exit 0 |
| N05a–d | See §3.0 | See §3.0 |
| N06 | Blob only in `refs/stash` | Label `project content` |
| N07a, b | Symlinked `ai/ael`; relative symlink | Exit 3, unchanged; note in log |
| N08a | FIFO at `workflow.md` | Relocated as FIFO; framework file placed |
| N08b | Names with ESC, `U+009B`, raw `0x9B`; `C.UTF-8` and `C` | ESC masked; C1 forms pass as described in §3.0 |
| ED | Empty directory at `workflow.md` | Replaced by the framework file |
| P1–P3 | 9.16 migration; 1,500 project files; 3,000 `state/` files | 7 relocated, 0 backups; 7.1 s; 1.6 s |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Closure Recommendation

- **Recommendation:** Do not close change-b170cf6a, and do not close issue-b170cf6a.
- **Reason:** The change resolves what it targeted (N-01 and N-03 to N-07 fully; N-02 in code only). Its two headline claims, however, are refuted by reproducible cases with content loss: A1 (plausible operator sequence) and A2 (silent, exit 0). The fixes are small and local (see recommendations).
- **Path:**
  - Iteration 2 of issue/change b170cf6a covers A1 and A2. For A3 to A7, the human decides whether to fix them or to record acceptance.
  - Independent re-check of iteration 2.
  - Run the macOS procedure (N-02, A7, BSD tools, bash 3.2) before the next downstream propagation.
- **Human approval:** pending operator decision.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial re-check report |

---

Copyright (c) 2026 William Watson. MIT License.
