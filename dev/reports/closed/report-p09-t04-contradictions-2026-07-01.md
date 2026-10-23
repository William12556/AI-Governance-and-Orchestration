Created: 2026 July 01

# P09 / T04 Contradiction Analysis Report

> **Status:** Closed 2026-10-23. Immutable. Findings resolved by issue-713437bc and change-713437bc (closed).

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope and Method](<#2.0 scope and method>)
[3.0 Root-Cause Structure](<#3.0 root-cause structure>)
[4.0 Findings](<#4.0 findings>)
[4.1 F1 — tactical_brief mandatory but AEL-exclusive](<#4.1 f1 — tactical_brief mandatory but ael-exclusive>)
[4.2 F2 — change_ref mandatory vs initial-implementation exemption](<#4.2 f2 — change_ref mandatory vs initial-implementation exemption>)
[4.3 F3 — P09 creation clause presumes a change document](<#4.3 f3 — p09 creation clause presumes a change document>)
[4.4 F4 — source_ref vs coupled_docs internal contradiction](<#4.4 f4 — source_ref vs coupled_docs internal contradiction>)
[4.5 F5 — "plain-text" vs "yaml fenced block"](<#4.5 f5 — plain-text vs yaml fenced block>)
[4.6 F6 — context-budget check scope](<#4.6 f6 — context-budget check scope>)
[4.7 F7 — schema / template drift](<#4.7 f7 — schema template drift>)
[4.8 F8 — stale embedded version labels](<#4.8 f8 — stale embedded version labels>)
[4.9 F9 — inconsistent tactical_brief size figures](<#4.9 f9 — inconsistent tactical_brief size figures>)
[5.0 Severity Summary](<#5.0 severity summary>)
[6.0 Resolution Options](<#6.0 resolution options>)
[7.0 Recommendation](<#7.0 recommendation>)
[Glossary](<#glossary>)
[Version History](<#version history>)

---

## 1.0 Purpose

Record logical errors and contradictions between the prompt protocol P09
(`ai/governance.md` §1.10) and its template T04 (`ai/templates/T04-prompt.md`),
as encountered in the prior `Solax-modbus Web UI` session when authoring a T04
prompt for the Claude Code profile.

Authoritative reference: `ai/governance.md` (v9.9). Analysis performed against
the `solax-modbus` working copy; P09 and T04 are shared identically with this
repository.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope and Method

In scope: P09 §1.10 and T04 (template body and schema). Cross-referenced against
`primer.md`, `profiles/claude.md`, the `§1.4.1` initial-implementation exemption,
and the AEL orchestrator source for empirical grounding of consumer claims.

Method: each contradiction is stated as a pair of directives that cannot both
hold for the same prompt, with the governing text cited. One consumer claim
(F1) was verified against `ai/ael/src/orchestrator.py` rather than inferred.

Out of scope: correctness of other protocols; template files other than T04.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Root-Cause Structure

The findings are not independent defects. They resolve into two whole-level
assumptions embedded in the prompt subsystem, each contradicted by a framework
capability added later and never reconciled with the subsystem:

- **Root A — AEL is the sole Tactical Domain.** The `tactical_brief` mechanism
  and the context-budget precondition assume the AEL orchestrator is the prompt
  consumer. The Claude Code profile (added v9.0) and claude-omlx read the full
  document directly; they invoke no orchestrator. Findings F1, F6.
- **Root B — every prompt derives from a change document.** The `coupled_docs`
  requirement and the P09 creation clause assume a preceding change document.
  The initial-implementation exemption (§1.4.1, added v9.8) establishes a
  design → T04 → execution path with no change document. Findings F2, F3, F4.

Findings F5, F7, F8, F9 are documentation-hygiene defects independent of the
two roots.

The two roots explain the prior session's difficulty: the TelemetryServer
prompt was both an initial implementation (Root B) and targeted at Claude Code
(Root A), so it collided with both assumptions simultaneously.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Findings

### 4.1 F1 — tactical_brief mandatory but AEL-exclusive

**Severity: High.**

T04 schema lists `tactical_brief` in `required` with `minLength: 1`, described
as "Used by orchestrator in preference to full document." P09 §1.10.2 directs
the Strategic Domain to "verify `tactical_brief` field is non-empty before
issuing AEL command" and to populate it as "a concise plain-text AEL task
payload."

The field's sole consumer is `extract_tactical_brief` in
`ai/ael/src/orchestrator.py`. The Claude Code profile (`profiles/claude.md`
§5.0) is invoked as `implement <prompt-path>` and reads the entire document;
no orchestrator runs, and nothing extracts the brief.

Contradiction: the field is mandatory for all T04 prompts, yet has a defined
consumer for only one of three tactical profiles. For a Claude Code or
claude-omlx prompt the author must either populate a field no process reads, or
omit a schema-required field. Both violate a stated directive.

[Return to Table of Contents](<#table of contents>)

### 4.2 F2 — change_ref mandatory vs initial-implementation exemption

**Severity: High.**

T04 schema requires `prompt_info.coupled_docs`, and within it `change_ref`
(pattern `^change-[0-9a-f]{8}$`) and `change_iteration`. P09 §1.10.2 states the
prompt "references source change UUID in `coupled_docs.change_ref`" and
"verifies coupling before prompt creation."

Governance §1.4.1 and primer §7.0 establish that initial implementation from an
approved design requires no issue or change document; the path is
design → T04 prompt → execution → review.

Contradiction: an initial-implementation prompt has no change document, so
`change_ref` has no valid value. The pattern rejects `N/A`, a design UUID, or
an empty string. A prompt that governance permits cannot satisfy the schema
governance also mandates.

[Return to Table of Contents](<#table of contents>)

### 4.3 F3 — P09 creation clause presumes a change document

**Severity: Medium.**

P09 §1.10.2: "Creates prompt documents from design *and* change documents using
T04 template." The conjunction presumes both documents exist for every prompt.

This contradicts the §1.4.1 forward path, in which the prompt is created from a
design document alone. Same root as F2; distinct textual location.

[Return to Table of Contents](<#table of contents>)

### 4.4 F4 — source_ref vs coupled_docs internal contradiction

**Severity: Medium.**

Within T04 itself: `prompt_info.source_ref` carries the comment
"design-\<uuid\> or change-\<uuid\>", explicitly anticipating a design-sourced
prompt. The adjacent `coupled_docs.change_ref` is required and locked to the
change pattern, which forbids a design-only origin.

Contradiction: the template both permits and forbids a design-sourced prompt.
The template is internally inconsistent, independent of any other document.

[Return to Table of Contents](<#table of contents>)

### 4.5 F5 — "plain-text" vs "yaml fenced block"

**Severity: Low.**

P09 §1.10.2 describes `tactical_brief` as "a concise plain-text AEL task
payload," then requires it "authored in a ```yaml fenced block with
`tactical_brief` as the root key." The T04 field comment repeats both "Plain
text" and the YAML-block requirement.

The two are reconcilable — a prose string value inside a YAML container — but
the phrasing "plain-text" against "yaml fenced block" invites the exact
misreading (author the brief as a `text` block) that the orchestrator's Pass-2
fallback and governance v8.4 were written to correct. Wording defect, not a
logical contradiction.

[Return to Table of Contents](<#table of contents>)

### 4.6 F6 — context-budget check scope

**Severity: Low.**

Primer §3.0 lists "context budget check before every T04 prompt," and §7.0
states `context-budget.md` "must exist ... before authoring any T04 prompt."
P09 §1.10.2 gates the same check to "before authoring `tactical_brief`."

When `tactical_brief` is inapplicable (non-AEL profile, per F1), the budget
precondition has no target, yet the primer says "every" / "any." The prior
session voided the budget blocker for Claude Code — correct in substance, but
in direct conflict with the primer's literal wording. Consequence of Root A.

[Return to Table of Contents](<#table of contents>)

### 4.7 F7 — schema / template drift

**Severity: Low.**

The T04 schema defines `output_format` (with `structure`, `integration_notes`,
`constraints`) and `deliverable.documentation`. Neither appears in the template
body. Template revision v1.6 removed several fields from the body;
`output_format` persists in the schema only. The schema documents fields the
template does not provide and no directive populates — dead schema.

[Return to Table of Contents](<#table of contents>)

### 4.8 F8 — stale embedded version labels

**Severity: Low.**

The T04 template body header reads "T04 Prompt Template v1.0" and the schema
header "T04 Prompt Schema v1.0". The file Version History records the current
version as 1.9. The embedded labels have not tracked the file since v1.0.

[Return to Table of Contents](<#table of contents>)

### 4.9 F9 — inconsistent tactical_brief size figures

**Severity: Low.** *(Beyond the strict P09/T04 pair; noted for coherence.)*

Three sizing figures for the same field: P09 §1.10.2 and the T04 comment give
"~200-400 tokens"; `orchestrator.py` prints "Recommended tactical_brief size:
≤1,000 tokens"; `budget.py` emits a dynamically computed maximum. An author
following one source contradicts another.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Severity Summary

| ID | Finding | Root | Severity |
|---|---|---|---|
| F1 | tactical_brief mandatory but AEL-exclusive | A | High |
| F2 | change_ref mandatory vs initial-implementation exemption | B | High |
| F3 | P09 creation clause presumes a change document | B | Medium |
| F4 | source_ref vs coupled_docs internal contradiction | B | Medium |
| F5 | "plain-text" vs "yaml fenced block" wording | — | Low |
| F6 | context-budget check scope ("every" vs AEL-gated) | A | Low |
| F7 | schema / template drift (output_format, documentation) | — | Low |
| F8 | stale embedded version labels | — | Low |
| F9 | inconsistent tactical_brief size figures | — | Low |

Load-bearing set: **F1** (Root A) and **F2** (Root B). Between them they account
for the prior session's difficulty.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Resolution Options

Presented for decision only. No change is made by this report. Each option is
independent; selection and sequencing are yours.

**Root A (F1, F6) — decouple the prompt from AEL exclusivity.**

- Option A1: Make `tactical_brief` conditionally required — mandatory when the
  target profile is AEL, optional otherwise. Requires a profile field in
  `prompt_info` and a schema `if/then` on it.
- Option A2: Keep `tactical_brief` universally optional in the schema
  (`minLength` removed from `required`); retain the non-empty directive in P09
  scoped explicitly to the AEL profile.
- Pro of A1: preserves the AEL non-empty guarantee. Con: adds a schema
  conditional and a new field. Pro of A2: minimal. Con: loses the schema-level
  guarantee for AEL, relying on the P09 directive alone.
- F6 follows either: rescope the primer §3.0/§7.0 wording from "every T04
  prompt" to "every AEL T04 prompt."

**Root B (F2, F3, F4) — admit design-sourced prompts.**

- Option B1: Make `coupled_docs.change_ref` optional and widen the pattern to
  accept a design UUID or an explicit sentinel; update P09 §1.10.2 to read
  "from design *or* change documents."
- Option B2: Add a distinct `design_ref` field; require exactly one of
  `design_ref` / `change_ref`.
- F4 resolves under either by aligning the `source_ref` comment with the chosen
  `coupled_docs` rule.

**Hygiene (F5, F7, F8, F9).**

- F5: reword to "prose value, authored inside a ```yaml block."
- F7: remove `output_format` and `deliverable.documentation` from the schema, or
  restore them to the template — whichever matches intent.
- F8: update embedded labels to the file version, or delete them and cite the
  Version History as authoritative.
- F9: choose one figure; make `orchestrator.py` and `budget.py` cite it or the
  computed budget, and align P09 and T04 to match.

Any change to P09 (governance) or T04 (template) is a source-equivalent
framework change and requires the standard issue → change → prompt workflow in
this repository, distinct from the documentation-only edits used in
`solax-modbus`.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Recommendation

Address F1 and F2 first; they are the operative blockers and each has a
low-cost variant (A2, B1) that removes the contradiction without new fields.
The remaining findings are non-blocking and may be batched. This ordering
follows severity and leaves design decisions (A1 vs A2, B1 vs B2) open for
collaborative resolution.

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Meaning |
|---|---|
| P09 | Prompt protocol, `governance.md` §1.10 |
| T04 | Prompt template, `ai/templates/T04-prompt.md` |
| AEL | Autonomous Execution Loop (Ralph Loop); orchestrator-driven tactical profile |
| tactical_brief | Concise AEL task payload extracted by the orchestrator from a T04 prompt |
| coupled_docs | T04 field set linking a prompt to its source change document |
| Root A / Root B | The two whole-level assumptions in §3.0 |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-07-01 | Initial report: nine findings (F1–F9) across two root causes; severity summary; resolution options; recommendation |
| 1.1 | 2026-10-23 | Closed under P00.14.4 and moved to `dev/reports/closed/` |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
