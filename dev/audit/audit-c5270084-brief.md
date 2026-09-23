Created: 2026 September 23

# Strategic Audit Brief — propagate.sh Deletion Scope (07087e91, c5270084)

**Status:** Brief. This is not an audit report.
**Subject commits:** `0a3dd27` (change-07087e91), `6b2aebe` (change-c5270084)
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
- c5270084: every path from `git ls-files --others` in the target `ai/` becomes an rsync protect rule `P /<path>`; each line of `<project>/ai/.propagate-keep` likewise; a non-git target gets `P *`; `.propagate-keep` is excluded from transfer.
- Tests: scratch targets in a Linux VM with GNU bash and rsync 3.2.7. Not run on macOS.
- Live: one run against solax-modbus (9.11 → 10.2) under the 07087e91 version only.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Claims To Test

| ID | Claim | Falsified by |
|---|---|---|
| C1 | No untracked or gitignored file under the target `ai/` is deleted. | Any such file deleted in any reachable configuration. |
| C2 | No path listed in `ai/.propagate-keep` is deleted, and the keep file itself is neither overwritten nor deleted. | A listed path or the keep file removed or changed. |
| C3 | A target that is not a git work tree has no deletions. | Any deletion in a non-git target. |
| C4 | Tracked files absent from the source are deleted, so renames propagate. | A retired tracked file surviving. |
| C5 | Excluded paths are never transferred or deleted. | Any change to an excluded path. |
| C6 | A non-TTY run without `--yes` applies nothing and exits 2. | Any write, or another exit code. |
| C7 | A major-version difference under `--yes` without `--allow-major` applies nothing and exits 2. | Any write, or another exit code. |
| C8 | The script behaves as above under macOS `/bin/bash` 3.2 and macOS `/usr/bin/rsync`. | Any divergence on macOS. |
| C9 | "Tracked, therefore recoverable" holds for every file the script deletes. | A deletion git cannot restore to its pre-run content. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Known Weak Points

Suspected, not established. Each is a place to look first.

1. **macOS rsync.** The live run printed `Transfer starting: 47 files`, which suggests macOS ships openrsync rather than rsync 3.x. Support for `--filter`, the `P` rule and `--delete` semantics under openrsync was never checked. If `P` is unsupported or silently ignored, C1–C3 fail on the operator's machine.
2. **Quoted paths.** `git ls-files --others` quotes paths containing non-ASCII or special characters unless `-z` or `core.quotePath=false` is used. A quoted path produces a protect rule that matches nothing.
3. **Wildcards.** Protect rules are rsync patterns. A filename containing `*`, `?` or `[` is interpreted as a pattern.
4. **Uncommitted edits (C9).** A tracked file with uncommitted modifications is deleted; `git checkout HEAD` restores the committed version, not the edit.
5. **Repository boundaries.** Target `ai/` inside a submodule, a nested repository, or a repository other than `<project-root>`'s; `git` not installed.
6. **Keep-file parsing.** CRLF line endings, leading `/`, directory entries with trailing `/`, inline comments, trailing whitespace.
7. **Protected directories.** Behaviour when a directory to be deleted contains protected files.
8. **Version parsing.** `gov_version` takes the last row of any version-history-shaped table in `governance.md`.
9. **Test circularity.** Every test was designed by the implementer against targets built from the source `ai/`.

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

---

Copyright (c) 2026 William Watson. MIT License.
