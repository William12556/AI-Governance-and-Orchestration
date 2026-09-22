Created: 2026 September 22

# Pre-Migration Baseline: Primer Divergence and Broken-Link Inventory

**Coupled to:** `dev/proposals/proposal-eb782f83-protocol-template-reordering.md`
**UUID:** `eb782f83`
**Captured:** 2026-09-22, against the pre-migration working tree

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Method](<#2.0 method>)
[3.0 Primer Divergence](<#3.0 primer divergence>)
[4.0 Broken-Link Inventory](<#4.0 broken-link inventory>)
[5.0 Post-Migration Comparison Procedure](<#5.0 post-migration comparison procedure>)
[6.0 Findings Requiring a Decision](<#6.0 findings requiring a decision>)
[Version History](<#version history>)

---

## 1.0 Purpose

Record the state of two known defects before the `eb782f83` migration, so that
post-migration verification can distinguish migration damage from conditions
that already existed.

Two baselines are captured:

1. The divergence between `ai/primer.md` and `docs/claude/primer.md`, ahead of
   the decision to treat `ai/primer.md` as canonical and overwrite the `docs/`
   copy from it.
2. Every broken relative file link in the migration set, so that verification
   check V4 has a reference point.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- Divergence: `diff -u ai/primer.md docs/claude/primer.md`, then a
  set-difference pass isolating lines present only in the `docs/` copy.
- Links: every `](target)` construct in `ai/**`, `docs/**`, `README.md`,
  `RATIONALE.md` and `CLAUDE.md`, excluding `closed/` directories. Internal
  anchors (`](<#heading>)`) were separated from file links and counted but not
  resolved; 461 anchor links were found and are out of scope for this baseline.
  Each file link was resolved relative to its containing document and tested
  for existence.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Primer Divergence

### 3.1 Version State

| File | Version | Dated | Lines | Bytes |
|---|---|---|---|---|
| `ai/primer.md` | 0.14 | 2026-08-21 | 332 | 14 309 |
| `docs/claude/primer.md` | 0.11 | 2026-07-08 | 317 | 12 843 |

The `docs/` copy is three revisions behind. Its own version history ends at an
entry numbered 0.11 whose text corresponds to entry 0.12 in `ai/primer.md`,
with the phrase "AEL-targeted" absent — that is, the `docs/` copy predates the
rescoping recorded in `ai/primer.md` v0.11.

Note the historical inversion: `ai/primer.md` entry 0.7 (2026-06-17) describes
`docs/claude/primer.md` as canonical. That was true in June 2026.
`ai/primer.md` has since advanced past it through v0.11, v0.13 and v0.14 while
the `docs/` copy remained static. The canonical designation in that entry is
stale, which is the defect this operation resolves.

### 3.2 Divergence Inventory

Nine substantive divergences. In every case the `ai/` text is the later form.

| # | Location | `ai/primer.md` (canonical) | `docs/claude/primer.md` (stale) |
|---|---|---|---|
| D1 | §2.0 Claude Code profile reference | `ai/profiles/claude-code.md` | `ai/profiles/claude.md` — path corrected in `ai/` v0.13 |
| D2 | §2.0 Tactical execution options | Options A, B and C presented as one selection set | Single `ael-mcp` paragraph; Option C absent entirely |
| D3 | §2.1 profile comparison table | `claude-code.md` | `claude.md` |
| D4 | §3.0 Execution Coordination | "Context budget check before every AEL-targeted T04 prompt" | "before every T04 prompt" — predates the v0.11 rescoping |
| D5 | §3.0 Governance | Includes the `ai/task.md` open-work register bullet | Bullet absent |
| D6 | §4.0 Workflow block | Flattened, Options A/B/C as one selection set | Older nested form: AEL branch with Options A/B, separate Claude Code branch |
| D7 | §6.1 Naming | Includes the `ai/task.md` UUID and lifecycle exemption note | Note absent |
| D8 | §7.0 Context Budget | Scoped to AEL-targeted prompts, cites `prompt_info.target_profile: ael` | Unscoped, applies to all T04 prompts |
| D9 | Version History | Entries 0.1 through 0.14 | Entries 0.1 through 0.11 |

### 3.3 Principal Finding

**The `docs/` copy contains no information absent from `ai/primer.md`.**

Sixteen lines exist only in the `docs/` copy, excluding its version-history
table. Every one is an earlier wording of content that `ai/primer.md` carries in
a later form. There is no content unique to the `docs/` copy — no section,
directive, table row or note that `ai/primer.md` lacks.

Consequence: overwriting `docs/claude/primer.md` from `ai/primer.md` loses
nothing. The only information discarded is the `docs/` copy's own version-history
table, which records the revision path of a file that is about to cease being
independently maintained. That table is preserved in this report and in git
history.

### 3.4 Residual Risk

Low. The one thing this baseline cannot rule out is an external consumer that
reads `docs/claude/primer.md` and depends on its stale content — for example a
Claude Desktop project configuration pointing at the `docs/` path. Nothing in
the repository does so: the only references to `docs/claude/` are a directory
entry in `docs/claude/project_information.md`, a `README.md` version-history
line, and a broken link in `ai/profiles/README.md` (§4.0, category C).

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Broken-Link Inventory

Seventeen broken relative file links exist in the migration set **before** any
migration work. None are caused by this change. All must be expected to persist
unless separately corrected.

### 4.1 Category A — governance template links (8)

`ai/governance.md` links each template by bare filename. The documents reside in
`ai/templates/`, so the correct target is `templates/T0n-<name>.md`.

| Source | Broken target | Correct target |
|---|---|---|
| `ai/governance.md` | `T01-design.md` | `templates/T01-design.md` |
| `ai/governance.md` | `T02-change.md` | `templates/T02-change.md` |
| `ai/governance.md` | `T03-issue.md` | `templates/T03-issue.md` |
| `ai/governance.md` | `T04-prompt.md` | `templates/T04-prompt.md` |
| `ai/governance.md` | `T05-test.md` | `templates/T05-test.md` |
| `ai/governance.md` | `T06-result.md` | `templates/T06-result.md` |
| `ai/governance.md` | `T07-requirements.md` | `templates/T07-requirements.md` |
| `ai/governance.md` | `T08-audit.md` | `templates/T08-audit.md` |

These eight links are also the links the migration must rewrite, since the
template filenames change. See §6.1.

### 4.2 Category B — governance profile link (1)

| Source | Broken target | Correct target |
|---|---|---|
| `ai/governance.md` | `claude-code.md` | `profiles/claude-code.md` |

### 4.3 Category C — profiles README (2)

| Source | Broken target | Note |
|---|---|---|
| `ai/profiles/README.md` | `../../../docs/claude/claude-desktop-instructions.md` | Target does not exist anywhere in the repository; also one directory level too high |
| `ai/profiles/README.md` | `claude.md` | Renamed to `claude-code.md` |

### 4.4 Category D — profile setup-guide links, depth error (6)

`ai/profiles/<file>.md` requires `../../docs/...`. All six use `../../../`,
which resolves above the repository root. Both targets exist at the correct
depth.

| Source | Occurrences | Broken target |
|---|---|---|
| `ai/profiles/mlx_devstral_magistral_heterogeneous.md` | 2 | `../../../docs/setup-apple-silicon-mlx.md` |
| `ai/profiles/mlx_devstral_magistral_heterogeneous.md` | 2 | `../../../docs/setup-apple-silicon-mlx-magistral.md` |
| `ai/profiles/mlx_devstral_small_2_2512_6bit.md` | 1 | `../../../docs/setup-apple-silicon-mlx.md` |
| `ai/profiles/mlx_north_mini_code_1_0_6bit.md` | 1 | `../../../docs/setup-apple-silicon-mlx.md` |

### 4.5 Baseline Assertion

Post-migration, the broken-link count in the migration set must be **17 or
fewer**, and every remaining entry must appear in §4.1 to §4.4. Any link not
listed here is migration damage.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Post-Migration Comparison Procedure

1. Re-run the link scan described in §2.0. Compare against §4.5.
2. Diff the regenerated `docs/claude/primer.md` against `ai/primer.md`. Expect
   an empty diff.
3. Confirm each of the nine divergences in §3.2 has resolved to the `ai/` form
   in the regenerated `docs/` copy.
4. Confirm no section heading, table row, directive or note present in
   `ai/primer.md` v0.14 is absent from the regenerated copy. Compare heading
   lists and table row counts, not only the byte diff.
5. Record the `docs/` copy's discarded version history as retained in §3.1 of
   this report.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Findings Requiring a Decision

### 6.1 Category A links coincide with the migration

The eight `ai/governance.md` template links are broken because of a missing
`templates/` path segment, and are simultaneously due for renaming because the
template filenames change. Two options:

- **Rename only.** The migration updates the filename and leaves the path
  defect in place. Strictly semantics-preserving; the links stay broken;
  post-migration count remains 17. Recommended, with the path defect raised as
  a separate issue.
- **Rename and repair.** The migration also inserts the `templates/` segment.
  One fewer defect, but it mixes a corrective fix into a mechanical migration
  and weakens the "every diff hunk is an identifier or a citation" acceptance
  criterion.

### 6.2 Categories B, C and D are unrelated to this change

Nine broken links have no connection to protocol or template numbering. They
should be corrected under their own issue, either before or after the migration,
but not within it.

### 6.3 The `docs/claude/` directory contains an untracked `.DS_Store`

`docs/claude/.DS_Store`, dated 2026-06-17. `.gitignore` covers `.DS_Store` and
`**/.DS_Store`, so it is correctly excluded. Noted only for completeness.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-22 | Initial baseline. Records the nine-point divergence between `ai/primer.md` v0.14 and `docs/claude/primer.md` v0.11, the finding that the `docs/` copy holds no unique information, and the seventeen pre-existing broken file links in the migration set with their correct targets. |

---

Copyright (c) 2026 William Watson. MIT License.
