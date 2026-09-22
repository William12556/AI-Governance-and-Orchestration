Created: 2026 September 22

# Strategic Audit Brief — eb782f83 Protocol and Template Renumbering

**Status:** Brief. This is not an audit report.
**UUID:** `eb782f83`
**Subject commit:** `b3369f5`, tagged `governance-v10.0`
**Baseline commit:** `9a1767f`, tagged `pre-eb782f83`

---

## Table of Contents

[1.0 Purpose and Standing](<#1.0 purpose and standing>)
[2.0 Reading Order](<#2.0 reading order>)
[3.0 What Was Done](<#3.0 what was done>)
[4.0 Claims To Test](<#4.0 claims to test>)
[5.0 Known Weak Points](<#5.0 known weak points>)
[6.0 Reproduction](<#6.0 reproduction>)
[7.0 Out of Scope](<#7.0 out of scope>)
[8.0 Deliverable](<#8.0 deliverable>)
[Version History](<#version history>)

---

## 1.0 Purpose and Standing

### 1.1 Why this audit is independent

One agent wrote the requirements, the design, the migration tooling, the
verification checks, and then ran the migration and reviewed its own diff. Every
defect found during that work was found because a rehearsal contradicted the
agent, never because the agent re-read its own reasoning and disagreed with it.

A self-audit could not find the class of defect that arises from a
misunderstanding held consistently throughout. That is the gap this audit
exists to close.

### 1.2 The standing of this brief

This brief was written by the implementing agent. Treat it as a witness
statement, not as instructions. Specifically:

- The claims in §4.0 are the implementer's claims. They are listed so they can
  be attacked, not so they can be confirmed.
- §5.0 lists where the implementer believes the work is weakest. It is offered
  in good faith and is certainly incomplete. Do not treat it as the boundary of
  the audit.
- The reproduction commands in §6.0 use tooling the implementer wrote. Verifying
  a claim by running that tooling inherits its assumptions. Where a claim
  matters, derive it independently.
- Nothing here constrains the audit's scope except §7.0, and even that is a
  recommendation about effort rather than a prohibition.

If this brief and the artefacts disagree, the artefacts are the evidence.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Reading Order

| Order | Document | Note |
|---|---|---|
| 1 | `ai/primer.md` | Orientation. Already migrated; describes the current scheme. |
| 2 | `dev/proposals/proposal-eb782f83-protocol-template-reordering.md` v1.6 | Decisions D1–D6 and the procedure |
| 3 | `dev/requirements/requirements-eb782f83-...md` v0.6 | FR, TR, NFR, CON, V |
| 4 | `dev/design/design-eb782f83-...md` v0.4 | Mappings, collision analysis, algorithm, gates |
| 5 | `dev/reports/report-eb782f83-pre-migration-baseline.md` v1.3 | Three pre-migration baselines |
| 6 | `dev/issue|change|prompt/...e36a35d3...` | The Python-module triple |
| 7 | `dev/tools/mapping.yaml`, `migrate_identifiers.py`, `verify_migration.py` | The instrument |
| 8 | `git diff pre-eb782f83..b3369f5` | The change itself |

The version histories of documents 2 to 5 record several criteria that were
changed mid-flight. Those revisions are themselves worth auditing: a criterion
weakened after it failed is a different thing from a criterion corrected because
it was wrong, and the documents claim the latter in each case.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 What Was Done

Protocol identifiers were renumbered into two bands, template identifiers into
document-creation order, and positional citations of the form `§1.x.y` replaced
by dotted fully-qualified citations of the form `Pnn.x.y`. `ai/governance.md`
was restructured so each protocol is a top-level section keyed by its
identifier, and an alias appendix was generated.

| Measure | Value |
|---|---|
| Files in write set | 55 |
| Files changed | 32 |
| Substitutions | 614 — C0 60, C1 140, C2 185, C3 225, C4 44 |
| Templates renamed | 8 |
| Commits | `b3369f5` migration; `fe392d0` version entry; `d60a8b9` V-17 fix |

Relevant commits:

```
d60a8b9  fix: bound V-17 at both ends
fe392d0  docs: governance v10.0 version-history entry; record propagate.sh defects
b3369f5  refactor: execute eb782f83 protocol and template renumbering
9a1767f  fix: rehearsal findings for eb782f83; refine V-15
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Claims To Test

Each row states a claim made by the implementer, the evidence offered, and what
would falsify it. The evidence column is what was actually done, not what should
have been done.

| # | Claim | Evidence offered | Falsified by |
|---|---|---|---|
| C1 | No protocol clause was lost, duplicated or altered by the restructuring | The pre-migration `governance.md` was migrated independently and compared line-multiset against the result: 1086 clause lines each side, differing only in table-of-contents entries | Any clause present before and absent after, or duplicated, or altered other than by identifier substitution |
| C2 | The change is semantics-preserving (CON-01) | Manual review of the diff; every changed line carries an identifier, a citation, a heading change or generated content | A clause whose meaning differs, including by having moved relative to prose that refers to its position |
| C3 | The mapping is bijective in both namespaces | Asserted at script load; self-test covers the transposition, both cycles and both fixed points | Two sources mapping to one target, or a source with no target |
| C4 | The frozen corpus is untouched | `git diff pre-eb782f83..b3369f5 -- dev` excluding `backup/`, `smoke/`, `tools/`: 0 files | Any change under `dev/` or any `closed/` directory attributable to the migration |
| C5 | No executable construct changed in any Python module | V-15: AST skeleton with docstrings removed and string constants blanked is identical; each differing string equals the substitution applied to the original. One string differs, in `orchestrator.py` | A behavioural difference in any of the five modules |
| C6 | The reduction in broken links, 17 to 9, is generation rather than repair, so CON-08 holds | The eight links are emitted by a regenerated table of contents, not edited in place | A finding that this is repair by another name, and that CON-08 should have blocked it |
| C7 | Excluding `ai/state/` and `ai/dashboard-alerts.md` was correct | Both are ephemeral or generated; both gitignored; `bin/propagate.sh` independently excludes both | A finding that exclusion removed real corpus, or was chosen to make a problem disappear |
| C8 | The change is reversible | Snapshot at `dev/backup/2026-09-22-eb782f83/` with SHA-256 manifest, plus the `pre-eb782f83` tag | A rollback that does not restore the pre-migration state exactly |
| C9 | The alias appendix makes the frozen corpus readable indefinitely | Generated from `mapping.yaml`; covers protocols, templates, the citation rule and reserved identifiers | A retired identifier or citation form in `dev/` that the appendix does not resolve |
| C10 | Idempotence holds | Scheme marker: the appendix heading. Content inspection cannot suffice, because the target alphabet contains the source alphabet | A second run that changes anything, or a marker that can be absent on a migrated corpus |
| C11 | Reserved identifiers carry no content | `P05`, `P06`–`P09`, `P16`–`P19` appear only in the appendix and reserved tables | A citation resolving to a reserved identifier |
| C12 | Downstream projects are unaffected | No downstream repository was touched; pin at governance 9.16 recorded | Evidence of a downstream repository altered by this work |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Known Weak Points

Offered by the implementer. Incomplete by construction.

### 5.1 Untested claims

These were asserted but not verified, and the implementer is aware of it:

1. **Positional prose.** Reordering protocols breaks any prose that refers to a
   protocol by position — "the following protocol", "as described above", "the
   next stage". No search for such constructions was performed. This is the
   most likely place for a genuine CON-01 violation and it is untested.
2. **Heading depth changed.** Protocols moved from `####` to `##`. Nothing was
   checked for dependence on heading depth — `linter.py`'s anchor extraction,
   Obsidian outline behaviour, or any downstream parser.
3. **Rollback was never exercised against the live snapshot.** `--rollback` was
   tested only in rehearsal. C8 rests on code that has not been run in anger.
4. **The AEL was not run after the migration.** `linter.py` and
   `protocol_checker.py` were compared old-versus-new, and `overwatch.py`
   completed a scan, but no Ralph Loop was executed. Recipes under
   `ai/ael/recipes/` were in the write set.
5. **`govwatch.py` was not run.** It is a TUI; only its parse was checked.

### 5.2 Circularity

`verify_migration.py` was written by the implementing agent from the same design
that produced `migrate_identifiers.py`, and shares its token patterns by direct
import. A misunderstanding in the design propagates to both. The ten passing
checks are therefore weaker evidence than their number suggests.

### 5.3 Admitted incompleteness

Design §11.0 records that V-02 is complete for positional citations but not for
bare protocol identifiers, because `P01`–`P04` and `P10` are valid in both
schemes. A stale `P05` meaning Trace is indistinguishable by pattern from a
deliberate `P05` meaning the reserved continuous-integration slot. Four
compensating controls are claimed. Whether they suffice is a judgement worth
testing.

### 5.4 Boundaries that may have been crossed

Three decisions sit close to CON-08, which forbids repairing pre-existing
defects:

- Five range expressions were replaced with scheme-neutral wording. Three of the
  five were already factually wrong, and the replacement corrected them.
- Eight broken template links were emitted correctly by the regenerated table of
  contents.
- The stale "canonical" designation on `docs/claude/primer.md` was corrected.

Each is argued in the documents as necessary or as generation rather than
repair. The pattern is worth examining: three separate accommodations of the
same constraint may indicate the constraint was wrong, or that it was being
worked around.

### 5.5 Criteria revised mid-flight

Two acceptance criteria were changed after they failed:

- **V-15** was plain AST equivalence; it forbade the one string change the
  migration required. Replaced with a skeleton comparison plus per-string
  verification.
- **V-05 and V-06** required the linters to "run clean"; they never have. 102
  and 38 pre-existing errors. Restated as before-and-after comparison.

Both revisions are argued as corrections of criteria that were wrong when
written. The alternative reading — that a criterion was relaxed because it was
inconvenient — deserves testing.

### 5.6 An untracked file was migrated

`docs/claude/project_information.md` is gitignored and was modified by the
migration. The tag cannot restore it; the snapshot is its only rollback path.
This was reported before the run but not otherwise mitigated.

### 5.7 Propagation is blocked

`bin/propagate.sh` rsyncs without `--delete`, so it cannot carry a rename, and
it cannot run non-interactively. Both were found after the migration, while
regenerating `dev/smoke/ai/`. Whether they were foreseeable during design — the
design specified template renames from the outset — is a fair question.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Reproduction

Every command below uses tooling written by the implementer. Treat results as
corroborating, not as proof. Where a claim matters, derive it independently.

```
git diff --stat -M pre-eb782f83..b3369f5
git diff pre-eb782f83..b3369f5 -- ai/governance.md
git diff --name-only pre-eb782f83..b3369f5 -- dev

python3 dev/tools/migrate_identifiers.py --self-test
python3 dev/tools/verify_migration.py --baseline-anchors 3 --until-ref b3369f5

grep -rn "§1\." ai/ docs/ *.md
grep -rnE "\bP(0[5-9])\b" ai/ docs/ *.md
```

Independent derivations worth performing:

- Extract every clause line from `governance.md` at both commits, apply the
  mapping by hand or with your own script, and compare. Do not reuse
  `substitute()`.
- Resolve a sample of citations in `dev/` against Appendix A and confirm each
  reaches a real clause.
- Restore the snapshot into a scratch directory and diff it against
  `pre-eb782f83`.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Out of Scope

Recommended, not binding.

- The content or merit of any protocol clause. This change moved identifiers; it
  did not alter policy.
- The banded scheme as a design choice. It was ratified as decision D1.
- The five reserved protocols, unauthored by design.
- Downstream propagation, deferred by decision D5.
- The 102 linter and 38 protocol-checker pre-existing errors, recorded in the
  baseline report §7.0 and on `dev/todo.md`.
- The nine remaining broken links in categories B, C and D.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Deliverable

A T08 audit report at
`dev/audit/audit-eb782f83-strategic-2026-09-DD.md`, following
`ai/templates/T08-audit.md`, with `mode: strategic`.

It should state, for each claim C1 to C12, whether it is confirmed, refuted or
unverifiable on the evidence available, and record findings by severity.
Findings that warrant remediation become issues under `P03`, coupled to changes
under `P04`.

A report concluding that no defects were found is a legitimate outcome. So is
one concluding that the audit could not establish a claim. The second is more
useful than a confirmation reached by re-running the implementer's own checks.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-22 | Initial brief. Twelve claims to test, seven categories of known weakness including five untested claims, reproduction commands with their limitations stated, and the deliverable specification. |

---

Copyright (c) 2026 William Watson. MIT License.
