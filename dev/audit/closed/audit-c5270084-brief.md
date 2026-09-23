Created: 2026 September 23

# Strategic Audit Brief — propagate.sh Deletion Scope (07087e91, c5270084)

**Status:** Brief. This is not an audit report.
**Subject:** `0a3dd27` (change-07087e91), `6b2aebe` (change-c5270084 iteration 1), and change-c5270084 iteration 2 (the commit following this brief)
**Baseline commit:** `6f6988b`

---

## Table of Contents

[1.0 Purpose and Standing](<#1.0 purpose and standing>)
[2.0 Reading Order](<#2.0 reading order>)
[3.0 What Was Done](<#3.0 what was done>)
[4.0 Claims To Test](<#4.0 claims to test>)
[5.0 Known Weak Points](<#5.0 known weak points>)
[6.0 Constraints](<#6.0 constraints>)
[7.0 Deliverable](<#7.0 deliverable>)
[Version History](<#version history>)

---

## 1.0 Purpose and Standing

One session designed, implemented, tested and closed change-07087e91, which
added `rsync --delete` to `bin/propagate.sh`. Its independent audit was
waived. The first live run, against solax-modbus, deleted project-local files
under `ai/`, one of them gitignored and unrecoverable. The same session then
wrote change-c5270084 to correct it. That session's premise failed once
already; its tests share the premise.

This brief is written by the implementer. Treat it as a witness statement,
not as instructions. Its claims are listed so they can be attacked. A
conclusion reached by re-running the implementer's own test commands is weak
evidence.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Reading Order

1. `bin/propagate.sh` at `6b2aebe` — the subject.
2. `dev/issue/closed/issue-07087e91-propagate-renames-and-noninteractive.md`, `dev/change/closed/change-07087e91-propagate-mirror-and-flags.md`.
3. `dev/issue/issue-c5270084-propagate-deletes-project-files.md`, `dev/change/change-c5270084-propagate-protect-project-files.md`, `dev/prompt/prompt-c5270084-propagate-protect-project-files.md`.
4. `git diff 6f6988b 6b2aebe -- bin/propagate.sh`.
5. `ai/governance.md` P02 Audit; `ai/templates/T08-audit.md`.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 What Was Done

- 07087e91: `rsync --delete` in preview and apply; `--yes`; non-TTY without `--yes` exits 2; governance major-version guard requiring `--allow-major` with `--yes`.
- c5270084 iteration 1 (superseded): rsync protect rules for untracked files and an `ai/.propagate-keep` list.
- c5270084 iteration 2 (subject): every file `--delete` would remove is classified by content. If `git hash-object` of the file exists as a blob in the framework repository, it is deleted; otherwise it is moved to `<project-root>/ai-local/<path>` before the apply, never overwriting, logged in `ai-local/RELOCATED.md`, with a warning if it loses gitignore coverage. Governance 10.3 P10.6 states that project files other than the declared set do not belong in `ai/`.
- Tests: scratch targets in a Linux VM with GNU bash and rsync 3.2.7. Not run on macOS.
- Live: one run against solax-modbus (9.11 → 10.2) under 07087e91 only, which deleted project files. Iteration 2 has been dry-run against solax-modbus only.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Claims To Test

| ID | Claim | Falsified by |
|---|---|---|
| C1 | No file is deleted unless its exact content is a blob in the framework repository. | Any deletion of content not recoverable from framework history. |
| C2 | Every other file `--delete` would remove is relocated to `ai-local/` with its relative path, before the apply. | A project file deleted, left in place, or moved to a wrong path. |
| C3 | Relocation never overwrites, and every move is logged in `ai-local/RELOCATED.md`. | An overwrite, or a move without a log row. |
| C4 | A relocated file that loses gitignore coverage is flagged. | A newly committable previously-ignored file without a warning. |
| C5 | Excluded paths (declared project files) are never transferred, moved or deleted. | Any change to an excluded path. |
| C6 | Tracked files absent from the source whose content is framework content are deleted, so renames propagate. | A retired unmodified framework file surviving. |
| C7 | A non-TTY run without `--yes`, or a major-version run under `--yes` without `--allow-major`, applies nothing and exits 2. | Any write, move, or another exit code. |
| C8 | The script behaves as above under macOS `/bin/bash` 3.2 and macOS `/usr/bin/rsync`. | Any divergence on macOS. |
| C9 | The preview is a complete and accurate statement of what the apply does. | Any action not listed, or listed and not taken. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Known Weak Points

Suspected, not established. Each is a place to look first.

1. **macOS rsync.** The live run printed `Transfer starting: 47 files`, which suggests macOS ships openrsync rather than rsync 3.x. The classification parses `*deleting` lines from `--itemize-changes`; their format and completeness under openrsync were never checked. A missing line means a file deleted without classification (C1).
2. **Directory deletions.** rsync may report a deleted directory as one line. The script expands directory lines with `find`; verify every file inside is classified, including dotfiles and nested directories.
3. **Blob check scope.** `git cat-file -e` succeeds for any object in the framework repository, including objects from unrelated branches, stashes or unreachable objects. Consider whether that widens "framework file" beyond intent.
4. **Line-ending and filter effects.** `hash-object --no-filters` hashes raw bytes; a framework file checked out with CRLF or other conversion in the target would not match and would be relocated (safe direction). Confirm no conversion makes project content match a framework blob (unsafe direction).
5. **Quoting and special characters.** Paths with newlines, leading dashes or non-ASCII characters through the rsync → sed → read pipeline.
6. **Partial failure.** Relocation happens before the apply. Behaviour if the apply fails, or if the run is interrupted mid-relocation.
7. **Race.** Target changes between the preview and the apply.
8. **Version parsing.** `gov_version` takes the last row of any version-history-shaped table in `governance.md`.
9. **Test circularity.** Every test was designed by the implementer.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Constraints

- Read-only with respect to the repository and every downstream project. Do not run `bin/propagate.sh` against a real project.
- Experiments on throwaway directories only, e.g. under `/tmp`.
- If macOS cannot be exercised from the audit session, record C8 as unverifiable and state what the operator must run.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Deliverable

A T08 audit report at `dev/audit/audit-c5270084-strategic-2026-MM-DD.md`,
following `ai/templates/T08-audit.md`, with `mode: strategic`. For each claim
C1–C9 state confirmed, refuted or unverifiable, with evidence. Record findings
by severity. Findings warranting remediation become issues under P03 coupled
to changes under P04; the audit does not modify source.

A report concluding that a claim could not be established is more useful than
a confirmation reached by re-running the implementer's checks.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial brief |
| 1.1 | 2026-09-23 | Rewritten for change-c5270084 iteration 2 (content classification and relocation to ai-local/) |

---

Copyright (c) 2026 William Watson. MIT License.
