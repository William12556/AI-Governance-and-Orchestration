Created: 2026 September 22

# Strategic Audit — eb782f83 Protocol and Template Renumbering

```yaml
# T08 Audit Report — eb782f83 protocol and template renumbering, 2026-09-22
# Subject: b3369f5 (governance-v10.0). Declared baseline: 9a1767f (pre-eb782f83).
#
# Independence note. dev/audit/audit-eb782f83-brief.md was read in full before
# source review, as instructed. It is treated as a witness statement. Every
# verdict below rests on evidence derived in this session against the git
# objects and the working tree; where a result could only be obtained by running
# the implementer's tooling, that is stated and the result is not treated as
# proof. migrate_identifiers.py and verify_migration.py were read but never
# imported or executed. The mapping used for every comparison was transcribed by
# hand from Appendix A of the migrated governance.md, and the substitution
# engine used to apply it was written for this audit.
#
# Nothing in the repository was modified. git status is clean.

audit_info:
  id: "audit-eb782f83"
  title: "Strategic audit — eb782f83 protocol and template renumbering, b3369f5 against 9a1767f"
  date: "2026-09-22"
  mode: "strategic"
  status: "complete"
  auditor: "Strategic Domain (Claude Desktop, independent session — not the implementing session)"

scope:
  target: "b3369f5 (tag governance-v10.0) against 9a1767f (tag pre-eb782f83); migration set ai/, docs/, CLAUDE.md, README.md, RATIONALE.md; dev/tools/mapping.yaml, migrate_identifiers.py, verify_migration.py; dev/ proposal, requirements, design and baseline report for eb782f83"
  criteria:
    - "claim adjudication — C1 to C12 of dev/audit/audit-eb782f83-brief.md §4.0"
    - "independent derivation of clause preservation, mapping bijectivity, link counts and substitution counts"
    - "the five untested claims of brief §5.1"
    - "the three CON-08 boundary decisions of brief §5.4"
    - "the criteria revised mid-flight, brief §5.5"
    - "defect classes absent from brief §5.0"
  exclusions:
    - "Protocol clause content and the merit of the banded scheme (brief §7.0)"
    - "The 102 linter and 38 protocol-checker pre-existing errors, and the nine surviving broken links"
    - "Downstream repositories — not reachable from this working tree; see C12"
    - "Any execution that would alter the repository: --rollback, bin/propagate.sh, and the AEL were not run"

method:
  independent_derivations:
    - >
      Clause preservation. Protocol-body content lines were extracted from
      ai/governance.md at both commits under a stated definition (non-blank,
      non-heading, non-rule, excluding 'Return to Table of Contents' links).
      The Appendix A mapping was applied by a single-pass alternation
      substitutor written for this audit — positional citation, redundant
      prefix, template filename, bare template, bare protocol — and the result
      compared to the migrated file both as a multiset over the whole body and
      in order within each of the eleven protocol sections.
    - >
      Bijectivity. Read directly from dev/tools/mapping.yaml and checked by
      hand, including the disjointness of the target set from the reserved set,
      which validate_bijection does not test.
    - >
      Link counts. A link scanner written for this audit walked the migration
      set at both commits, resolving relative file targets on the filesystem
      and anchor targets against lowercased heading text.
    - >
      Substitution counts. Token-class occurrences were counted over the
      baseline write set with version-history regions removed by the same
      region rule the design specifies.
    - >
      Snapshot integrity. Every row of dev/backup/2026-09-22-eb782f83/
      manifest.csv was re-hashed against its stored copy and against the blob
      at the pre-eb782f83 tag, and the baseline write set was checked for rows
      the manifest omits.
  tooling_borrowed:
    - >
      linter.py and protocol_checker.py were run read-only against dev/ to
      obtain current counts for the V-05 and V-06 assessment. These are the
      subject tooling, not the verification tooling, and the result is used
      only as a data point about corpus drift.

findings:
  critical: []

  high:
    - location: "ai/governance.md table of contents; dev/requirements/requirements-eb782f83-protocol-template-reordering.md FR-07-04; dev/proposals/proposal-eb782f83-protocol-template-reordering.md OQ-7; dev/todo.md line 20"
      description: >
        F-01. A ratified decision was reversed during execution and recorded as
        a discharge rather than as a change. The baseline report §6.1 set out
        two options for the eight Category A template links and recommended
        'Rename only', naming the cost of the alternative in terms: it 'mixes a
        corrective fix into a mechanical migration and weakens the every diff
        hunk is an identifier or a citation acceptance criterion'. Proposal OQ-7
        resolved 'rename only. The path defect is deferred to dev/todo.md and
        corrected after this change'. FR-07-04 codified it: 'Their missing
        templates/ path segment is not repaired (CON-08).' The delivered table
        of contents emits templates/T01-requirements.md and its seven siblings —
        the repaired form. The requirements document still carries FR-07-04
        unamended at v0.6, so the delivered artefact does not satisfy its own
        requirements baseline, and V-14 in the same document now contradicts
        FR-07-04 directly. The dev/todo.md item was closed [x] with the
        rationale 'Generation, not repair'. That distinction is about mechanism.
        The effect is that the generator was given information — the correct
        location of the templates directory — that is not derivable from the
        identifier mapping, and emitted it. Independently confirmed: the
        baseline table of contents emitted bare filenames, the migrated one
        emits path-qualified filenames. Functionally the new links are correct
        and no reader is harmed. The defect is in the governance record, which
        is what this framework exists to keep.
      issue_ref: ""

    - location: "dev/tools/migrate_identifiers.py — rollback()"
      description: >
        F-02. --rollback does not restore the pre-migration state. It iterates
        manifest.csv, copies each recorded file back over its target and
        re-hashes it. It never removes a file the migration created. Seven
        template files were created by rename — T01-requirements.md,
        T02-design.md, T03-prompt.md, T04-test.md, T05-result.md, T06-issue.md,
        T07-change.md — and none appears in the manifest, because the manifest
        records the pre-migration write set. After a rollback, ai/templates/
        would hold the seven restored originals alongside the seven new files,
        fifteen templates in a directory that should hold eight, and the
        governance table of contents restored to the retired scheme would point
        at the restored originals while the new files sit beside them
        unreferenced. C8's own falsification test — 'A rollback that does not
        restore the pre-migration state exactly' — is met. This was derived by
        reading; the function was not executed, because executing it would
        modify the repository. It has also never been executed against the live
        snapshot (brief §5.1.3), so the defect has had no opportunity to
        surface. The snapshot itself is sound: see the C8 verdict.
      issue_ref: ""

    - location: "dev/tools/migrate_identifiers.py — evaluate_gates(), scheme marker test"
      description: >
        F-03. The idempotence gate cannot distinguish a corpus that is already
        migrated from one where the marker file does not exist. The test is
        'marker.exists() and mp.marker_text in marker.read_text(...)'; a false
        result from either conjunct is treated identically, as 'not yet
        migrated', and the run proceeds. The marker is a property of one file,
        ai/governance.md, not of the corpus. Applied to any root that does not
        carry that file at that path — and the declared next step, decision D5,
        is propagation to downstream repositories whose layouts have not been
        surveyed — the gate passes and the mapping is applied a second time.
        A second pass is destructive, not inert: P03 and P04 transpose back,
        P01 to P10 to P11, T01 to T02 to T07, and all eight template targets lie
        inside the source alphabet. C10's own falsification test — 'a marker
        that can be absent on a migrated corpus' — is satisfied by construction
        for any corpus without ai/governance.md. The related hazard, that
        write_snapshot is anchored at root/dev/backup/, means such a run would
        also create a dev/ tree in a repository that has none.
      issue_ref: ""

  medium:
    - location: "ai/templates/*.md schema_type keys; ai/ael/src/linter.py _ENUMS, _ID_PATTERNS, _ITERATION_FIELDS; ai/ael/src/protocol_checker.py _TERMINAL_STATUS"
      description: >
        F-04. A second template namespace exists and was not migrated, and its
        survival is accidental rather than designed. Seven templates declare
        retired-scheme schema_type values: ai/templates/T07-change.md declares
        schema_type "t02_change", T02-design.md declares "t01_design",
        T06-issue.md declares "t03_issue", T04-test.md declares "t05_test",
        T05-result.md declares "t06_result", T01-requirements.md declares
        "t07_requirements". linter.py and protocol_checker.py key their enum,
        identifier-pattern, iteration-field and terminal-status tables on the
        same retired tokens. Fifty-four occurrences across the live corpus.
        The pairing is internally consistent, so nothing is broken today and
        C5 is unaffected; that is why no check caught it. Three observations
        make it a finding rather than an accepted exclusion. First, schema_type
        appears nowhere in the proposal, the requirements, the design, the
        tooling or the brief: it was never considered, so it was never excluded.
        Second, its survival depends on a boundary rule, not a decision — \bt02\b
        does not match t02_change because the underscore is a word character —
        while design §5.5 states that lowercase template tokens migrate
        ('T04 becomes T03, t04 becomes t03'), so the outcome contradicts the
        design's stated intent. Had the token been spelled t02-change the
        migration would have rewritten it and broken both linters. Third, the
        result is two live, mutually contradictory template numbering schemes in
        the same file, with nothing in Appendix A or anywhere else recording the
        split. The next maintainer who aligns one side to the other breaks the
        compliance tooling.
      issue_ref: ""

    - location: "commit 7b47345, ancestor of the declared baseline 9a1767f; ai/governance.md P02.3 Audit Scope and P00.17 Templates"
      description: >
        F-05. Two protocol clauses changed meaning, and they sit outside the
        window in which CON-01 was measured. The five range-expression rewrites
        that brief §5.4 lists as a CON-08 boundary decision landed in 7b47345,
        one commit before the tag pre-eb782f83. Two of the five are protocol
        clauses: 'Protocol compliance: All protocols P00-P09' became 'Protocol
        compliance: All protocols', and 'Templates T01-T07 are external
        documents in ai/templates/ directory' became 'All templates are external
        documents in ai/templates/ directory'. The first is not a neutral
        rewording: it replaces a closed enumerated set with an open one, so the
        audit scope now includes Requirements and every future protocol, which
        it previously did not. The design is candid that three of the five
        corrected pre-existing factual errors incidentally, and argues the
        edits were required to unblock the run — which is true, since a range
        expression cannot survive a non-monotonic renumbering. The problem is
        placement. V-16 reviews the complete diff, V-17 compares the frozen
        corpus, C1 and C2 compare governance.md, and this audit's own clause
        comparison all anchor at pre-eb782f83, so none of them can see these
        edits. Re-running the clause comparison against 9f7fe29, the last
        commit before the range rewrites, yields exactly two differences and
        they are these two clauses. CON-01 holds over the range the brief
        specifies and does not hold over the change as a whole.
      issue_ref: ""

    - location: "ai/governance.md — Appendix A, preamble"
      description: >
        F-06. Appendix A's scope statement is false, in a document declared
        permanent and immutable. It reads 'The frozen historical corpus in dev/
        and every closed/ directory cites the retired scheme and is read through
        this appendix.' Two classes of dev/ content are current-scheme. The
        regenerated smoke corpus dev/smoke/ai/ — six tracked files including a
        full migrated governance.md carrying the scheme marker — uses the
        current scheme throughout: dev/smoke/ai/governance.md line 14 reads
        '[P03 Issue]', and the appendix rule resolves P03 to Change. The
        eb782f83 proposal, requirements, design, baseline report and brief are
        also written in the current scheme. The identifiers valid in both
        schemes — P01, P02, P03, P04, P10 and all eight template numbers — are
        precisely the ones the rule silently mis-resolves. A secondary gap: A.2
        is keyed on filenames only, so a bare T04 in dev/, of which there are
        411 occurrences, requires an inference step through T04-prompt.md that
        the appendix does not state.
      issue_ref: ""

    - location: "ai/governance.md, ai/primer.md, docs/claude/primer.md, ai/workflow.md, ai/doc/guide-audit-loop.md, docs/guide-audit-loop.md, ai/profiles/claude-code.md, ai/skills/validation/run-tests.md — Version History sections"
      description: >
        F-07. The version-history exemption is implemented and argued but
        recorded nowhere a reader will look. Ninety-five positional citations
        of the form §1.x survive in the live corpus, all inside version-history
        tables, together with roughly a hundred retired bare identifiers. The
        exclusion is deliberate — PROTECTED_HEADING_RE in the migration script,
        argued in design §5.2 and permitted by FR-05-04 — and the reasoning is
        sound: rewriting a version history falsifies the historical record.
        But Appendix A scopes itself to dev/ and closed/ directories, so a
        reader of ai/primer.md who meets 'governance §1.10.3' in its version
        history has no pointer to the resolution rule, and the live corpus
        carries no statement that version histories are read under the scheme
        in force at the time. The fix is one sentence in Appendix A, not a
        migration.
      issue_ref: ""

  low:
    - location: "dev/audit/audit-eb782f83-brief.md §3.0 measures table; ai/governance.md version history, entry 10.0"
      description: >
        F-08. The substitution total does not reconcile with its own breakdown.
        The brief records 'Substitutions 614 — C0 60, C1 140, C2 185, C3 225,
        C4 44'. The components sum to 654. An independent token count over the
        baseline write set, with version-history regions removed by the design's
        own region rule, gives C0 58, C1 140, C2 185, C3 225, C4 44, total 652 —
        corroborating the breakdown and not the total. Subtracting the identity
        substitutions P00 and T08 gives 629, which does not close the gap
        either. The figure 614 is now in the permanent version-history entry for
        governance v10.0. The run log, if retained, should settle which figure
        is right; the breakdown is the one the evidence supports.
      issue_ref: ""

    - location: "dev/audit/audit-eb782f83-brief.md §3.0 measures table"
      description: >
        F-09. 'Templates renamed 8' overstates by one. Seven templates were
        renamed; T08-audit.md is a fixed point of the permutation and was
        modified in place. git diff --name-status -M shows seven R entries and
        one M.
      issue_ref: ""

    - location: "dev/tools/mapping.yaml — migration_set and refuse_paths"
      description: >
        F-10. bin/ is in neither list. The write set is ai, docs, CLAUDE.md,
        README.md, RATIONALE.md; the refusal list is dev, deprecated, tests,
        .git. bin/ holds three tracked scripts — propagate.sh, bootstrap.sh,
        release.sh — and was therefore neither migrated nor deliberately
        excluded. It currently carries no protocol or template identifier, so
        coverage holds by accident rather than by construction; the same is true
        of .claude/, .ael/ and tmp/. This bears on brief §5.7: bin/propagate.sh
        rsyncs without --delete and so cannot carry a rename, and the design
        specified template renames from the outset. It was foreseeable, and the
        reason it was not foreseen is structural — no step in the design was
        ever going to look at a directory that appears in neither list.
      issue_ref: ""

    - location: ".gitignore line 47; dev/tools/mapping.yaml exclude_paths"
      description: >
        F-11. The ignore rule is ai/state/ralph/, not ai/state/. C7's evidence
        states that both excluded paths are gitignored. That is true of the
        content that exists — nothing under ai/state is tracked — and false of
        the excluded path as written. A file placed directly in ai/state/ would
        be tracked and permanently outside the write set with no record.
      issue_ref: ""

    - location: "dev/backup/ (gitignored by .gitignore line 79); docs/claude/project_information.md"
      description: >
        F-12. The only rollback path for the untracked file is itself untracked.
        docs/claude/project_information.md is gitignored and was modified by the
        migration; the tag cannot restore it, so the snapshot is its sole
        rollback path, as brief §5.6 states. dev/backup/ is also gitignored, by
        decision OQ-04. The consequence is that the sole rollback path for that
        file exists on one machine, is not version-controlled and has not been
        pushed. Losing the working tree loses it.
      issue_ref: ""

    - location: "dev/requirements/requirements-eb782f83-protocol-template-reordering.md V-05, V-06"
      description: >
        F-13. The restated criteria are already unreproducible. V-05 and V-06
        were restated as before-and-after output comparison against pre-existing
        counts of 102 linter errors and 38 protocol_checker errors. Run today
        against dev/, linter.py reports 103 errors and 102 warnings, against a
        baseline of 102 and 101; protocol_checker reports 38, unchanged. The
        delta is explained by documents added to dev/ after the migration, not
        by the migration — git diff pre-eb782f83..b3369f5 -- dev is empty — but
        the criterion as restated cannot be re-run by a later auditor, because
        the corpus it measures is a live working directory. It is also largely
        redundant with V-17, which establishes the same fact by digest.
      issue_ref: ""

    - location: "dev/audit/audit-eb782f83-brief.md §4.0 C1 evidence column"
      description: >
        F-14. The figure '1086 clause lines each side' cannot be reproduced
        without the implementer's line definition, which is not stated. Under
        an explicitly stated definition this audit counts 971 protocol-body
        content lines on each side. The two are not in conflict; the point is
        that the published figure carries no independent check, and a figure
        offered as evidence should.
      issue_ref: ""

claim_adjudication:
  - claim: "C1"
    verdict: "confirmed"
    basis: >
      Independently derived and stronger than claimed. Protocol-body content
      lines number 971 at each commit. Under the Appendix A mapping applied by a
      substitutor written for this audit, the multiset comparison shows zero
      missing and zero extra lines, and the comparison repeated in order within
      each of the eleven protocol sections is identical in every one. Protocol
      names are preserved exactly. No clause was lost, duplicated or altered.
      Two qualifications. The comparison is anchored at pre-eb782f83 and is
      therefore blind to F-05. The claim's own figure of 1086 is not
      reproducible; see F-14.
  - claim: "C2"
    verdict: "refuted"
    basis: >
      Refuted narrowly, and not by anything inside the audited range. Within
      pre-eb782f83..b3369f5 the claim holds: every changed line in governance.md
      is an identifier, a citation, a heading change or generated content;
      intra-protocol ordering is exact; and a search of the live corpus for
      positional constructions — 'the following protocol', 'as described above',
      'the next stage', 'listed below', 'preceding', 'subsequent' — returns one
      hit, 'when all five criteria below are satisfied' in P04.12, which is
      intra-clause and correct. Outside that range, two protocol clauses changed
      meaning at 7b47345. See F-05. CON-01 holds over the window in which it was
      measured and not over the change.
  - claim: "C3"
    verdict: "confirmed"
    basis: >
      Verified by hand from mapping.yaml without loading the script. Eleven
      protocol sources map to eleven distinct targets; the template table is the
      permutation (T01 T02 T07)(T03 T06 T05 T04) with T08 fixed, and its eight
      targets are distinct. The target set and the reserved set are disjoint —
      a property validate_bijection does not test and which therefore rested on
      inspection until now. One clarification on terms: the protocol map is an
      injection into a larger alphabet, not a permutation of one set. Five
      targets lie inside the source alphabet, which is the root cause of F-03
      and of the §5.3 limitation.
  - claim: "C4"
    verdict: "confirmed"
    basis: >
      git diff --name-only pre-eb782f83..b3369f5 -- dev returns nothing, and no
      path containing closed/ appears anywhere in the commit's name list. The
      exclusions the claim offers for backup/, smoke/ and tools/ were not needed:
      the unrestricted comparison is already empty. Derived from git objects, not
      from the implementer's tooling.
  - claim: "C5"
    verdict: "confirmed"
    basis: >
      Confirmed as to executable constructs, and the falsification test as
      written is not met. The complete Python diff was read line by line: every
      hunk in linter.py, protocol_checker.py, govwatch.py and overwatch.py is a
      comment or a docstring. All five modules parse. No .py or .sh file in the
      repository references a template filename, so the seven renames cannot
      reach them. The single string change in orchestrator.py is not in a
      comment: 'When authoring the next tactical_brief or T04 prompt' sits
      inside the report f-string of write_context_report and is written to
      context-budget.md, which the Strategic Domain reads. Program output
      changed. The implementer disclosed the string; the point is that C5's
      stated falsifier is 'a behavioural difference in any of the five modules',
      and generated document text is behaviour. Confirmed on the narrow reading,
      not on the test as worded.
  - claim: "C6"
    verdict: "refuted"
    basis: >
      The arithmetic is confirmed and the characterisation is refuted. An
      independent link scan reproduces the implementer's figures exactly under
      their implied definition — broken file-link occurrences fall from 17 to 9
      — and adds two results the brief does not carry: counting all link
      occurrences including anchors the fall is 21 to 11, and deduplicating per
      file and target it is 19 to 9. The two additional repairs are the broken
      anchors '#1.0 protocols' and '#2.0 templates', which the baseline report
      does track separately and the brief does not mention. On the
      characterisation: the baseline table of contents emitted bare filenames
      and the migrated one emits templates/-qualified filenames. The path
      segment is not derivable from the identifier mapping; it is knowledge of
      where the templates live, supplied to the generator. That is repair, and
      it reverses OQ-7, contradicts FR-07-04 and weakens the criterion the
      baseline report itself named. See F-01.
  - claim: "C7"
    verdict: "confirmed"
    basis: >
      No tracked file exists under ai/state at either commit, and nothing
      present there carries a protocol or template token; ai/dashboard-alerts.md
      is gitignored and rewritten by every govwatch scan; bin/propagate.sh
      excludes both independently, which is corroboration from a script written
      before this work. No real corpus was removed, and the exclusion does not
      make any problem disappear — the excluded content has no identifiers to
      migrate. One imprecision recorded as F-11.
  - claim: "C8"
    verdict: "refuted"
    basis: >
      The snapshot is sound and the restore is not. Independently verified:
      manifest.csv carries 55 rows; every row's SHA-256 matches its stored copy;
      all 54 rows that were tracked at the baseline are byte-identical to their
      pre-eb782f83 blobs; the 55th is docs/claude/project_information.md, which
      was untracked, as declared; and no file in the baseline write set is
      missing from the manifest. The snapshot is a faithful and complete
      capture. The rollback function, however, restores without pruning, so the
      seven files created by the template renames survive it — see F-02. The
      claim's falsifier is met. The pre-eb782f83 tag restores the tracked
      portion exactly and is unaffected by this; the snapshot path is the one
      that fails, and it is the only path for the untracked file.
  - claim: "C9"
    verdict: "refuted"
    basis: >
      Appendix A resolves every retired form this audit could find — all eleven
      protocol identifiers, all eleven positional ordinals, all eight template
      filenames — and no §1.<ordinal> with an ordinal above eleven exists in
      dev/. On the narrow test the claim survives. It is refuted on its own
      terms because the appendix does not merely resolve, it instructs: it
      declares all of dev/ to be retired-scheme, and two classes of dev/ content
      are current-scheme. Following the instruction produces wrong answers for
      exactly the identifiers that are valid in both schemes. See F-06.
  - claim: "C10"
    verdict: "refuted"
    basis: >
      Confirmed for this corpus, refuted as a general property. The reasoning
      behind the marker is correct — content inspection cannot decide the
      question, because the target alphabet contains the source alphabet — and
      the marker is present and detected here. But the gate conflates a missing
      marker with a missing marker file, so the claim fails for any corpus that
      does not carry ai/governance.md at that path. See F-03. The exposure is
      not hypothetical: D5 defers propagation to downstream repositories, and
      that is the next planned use of this mapping.
  - claim: "C11"
    verdict: "refuted"
    basis: >
      Refuted as stated, confirmed on the reading the implementer intended.
      P05 through P09 occur roughly a hundred times outside the appendix and the
      reserved tables — in the version-history sections of ai/governance.md,
      ai/primer.md, docs/claude/primer.md, ai/doc/guide-audit-loop.md,
      docs/guide-audit-loop.md and ai/skills/validation/run-tests.md — where
      they denote retired protocols. By Appendix A.4's own rule, 'a citation
      resolving to one is a defect, not a reference', each is a defect. The
      intended claim holds: a search of every live document outside
      version-history regions finds no citation resolving to a reserved
      identifier. The claim is true only under an exemption that the live corpus
      never states. See F-07.
  - claim: "C12"
    verdict: "unverifiable"
    basis: >
      No downstream repository is reachable from this working tree, and none is
      named in the audited artefacts. What can be confirmed is internal: the pin
      at governance 9.16 is recorded in proposal D5, in CON-06 and FR-10-04, in
      the risk register at R7 and on dev/todo.md; bin/propagate.sh requires a
      TTY and cannot have run non-interactively; and nothing in the commit
      reaches outside this repository. The claim is consistent with every
      observation available and cannot be established here. Establishing it
      requires inspecting the downstream repositories, which is outside this
      audit's reach rather than beyond proof.

brief_weak_points_assessed:
  - point: "§5.1.1 positional prose"
    result: >
      Tested and clear. The live corpus was searched for positional
      constructions referring to protocol order; the single hit is intra-clause
      and correct. Intra-protocol clause ordering is preserved exactly in all
      eleven sections. Residual risk low. This was the implementer's leading
      candidate for a genuine CON-01 violation; it is not where the violation
      is. The violation is F-05, and it predates the baseline.
  - point: "§5.1.2 heading depth"
    result: >
      Tested, risk low. linter.py extracts headings with ^#{1,6} and compares
      anchors against lowercased full heading text, so it is depth-agnostic; all
      table-of-contents anchors in the restructured file resolve under that
      rule. No Python module in the repository parses governance.md at all.
      orchestrator.py's '##\s+[\d.]+\s+Tactical Brief' and 'Success Criteria'
      regexes apply to T03 prompt documents, whose numbering is untouched.
      Obsidian outline depth is presentational. One consequence worth noting
      rather than fixing: governance.md is now the only document in the
      repository whose sections are unnumbered, and the '## 1.0 Protocols
      (Directives)' section that introduced the protocol set as a set no longer
      exists.
  - point: "§5.1.3 rollback never exercised"
    result: >
      Now tested by reading, and defective. See F-02. The function was not
      executed, since execution would modify the repository.
  - point: "§5.1.4 AEL not run"
    result: >
      Narrowed but still open. The four recipes under ai/ael/recipes/ contain no
      protocol or template token, so the write set's inclusion of them was a
      no-op, and no module reads governance.md. The residual exposure is
      confined to prompt and context documents rather than to the migrated
      corpus. A Ralph Loop has still not been executed against the migrated
      framework.
  - point: "§5.1.5 govwatch not run"
    result: >
      Risk low. Its diff is three comment lines; it parses; it references no
      template filename. It remains unexercised.
  - point: "§5.2 circularity"
    result: >
      Confirmed by inspection — verify_migration.py imports from
      migrate_identifiers at module level and shares its token patterns
      directly, so the ten passing checks are one instrument reporting on
      itself. The C1, C3, C4, C6 and C8 results in this report were derived
      without importing or executing either module, and are the part of the
      evidence base that does not inherit the assumption.
  - point: "§5.3 admitted incompleteness and its four compensating controls"
    result: >
      The limitation is correctly stated and the controls do not close it. Taken
      one at a time: control 1, V-03 flagging citations that resolve to a
      reserved protocol, addresses P05 through P09 and P16 through P19, not the
      P01 to P04 and P10 collision that the limitation is actually about, and it
      is silent inside the protected regions where every surviving retired
      identifier lives; control 2, the Pass 1 assertions, proves that every
      token the patterns matched was rewritten, which is closure of the matcher
      and not coverage of the corpus; control 3, deterministic write-set
      enumeration, cannot report a directory that was never in migration_set,
      and one such directory exists (F-10); control 4, manual semantic diff
      review, reads hunks, and a token that should have changed and did not
      produces no hunk, so it is blind to this class by construction, and being
      bounded at pre-eb782f83 it is also blind to F-05. F-04 is a concrete
      instance of the class all four controls miss: fifty-four lowercase
      template tokens that the design's own §5.5 says should have migrated, that
      were never matched, and that no control could have surfaced. The judgement
      'in combination sufficient' is not established.
  - point: "§5.4 three decisions near CON-08"
    result: >
      The pattern the brief asks to be examined is real, and the three instances
      are not alike. The five range expressions had to change: a range cannot
      survive a non-monotonic renumbering, and any faithful translation would
      have been unreadable. That is necessity. But two of the five are protocol
      clauses whose meaning changed, and they were committed one commit before
      the baseline tag, which removed them from every check that measures
      CON-01 (F-05). The eight template links did not have to change: an
      explicit decision had been taken not to change them, twice, and it was
      reversed at execution (F-01). The docs/claude/primer.md 'canonical'
      designation was examined and is the weakest of the three as a concern —
      the file was regenerated wholesale from ai/primer.md under FR-08, so a
      stale designation could not survive regeneration in any case. Reading the
      three together: the constraint was not wrong, and it was not uniformly
      worked around. One instance was unavoidable and mis-scoped, one was a
      reversal presented as a discharge, and one was a consequence of a
      regeneration decision taken on other grounds. The recommendation is to
      record the first two as CON-08 exceptions in the change record rather than
      to reclassify them as something other than repair.
  - point: "§5.5 criteria revised mid-flight"
    result: >
      Both listed revisions are corrections in substance, and the list is
      incomplete. V-15 as written — plain AST equivalence including string
      constants — was unsatisfiable for a migration whose declared purpose
      includes rewriting citation strings inside docstrings, so the criterion
      was wrong when written. The replacement is nonetheless weaker in a way
      that matters: it verifies that every string which differs equals the
      substitution applied to the original, and therefore cannot detect a string
      that should have changed and did not. F-04 is exactly that, and the
      revised V-15 passes over it. The revision closed the hole that blocked the
      run and left open the one that mattered. V-05 and V-06 are corrections —
      'runs clean' was, as the baseline report says plainly, written without
      checking — but the restatement proves less than its name suggests and has
      already drifted (F-13). The omission: V-14 belongs in §5.5 and is not
      there. It acquired its expected result of 9 at requirements v0.5, after
      the rehearsal, and its stated justification contradicts FR-07-04 in the
      same document. Of the criteria touched mid-flight, it is the one where the
      reading 'relaxed because it was inconvenient' has the most support, and it
      is the one the brief does not list.
  - point: "§5.6 untracked file migrated"
    result: >
      Confirmed and extended. docs/claude/project_information.md is in the write
      set, is gitignored, was modified, and is captured in the snapshot as row
      55. The migration script reports untracked write-set members explicitly
      before proceeding, which is the right behaviour. The unrecorded
      consequence is F-12: dev/backup/ is itself gitignored, so the sole
      rollback path for that file is neither version-controlled nor pushed.
  - point: "§5.7 propagation blocked"
    result: >
      Confirmed by reading bin/propagate.sh: rsync -av at line 125 carries no
      --delete, and line 117 is an interactive read -r -p confirmation. Both
      defects are real. On foreseeability, the answer is yes, and the reason
      they were not foreseen is structural rather than an oversight of
      attention: bin/ appears in neither migration_set nor refuse_paths (F-10),
      so no step in the design was ever directed at the script that had to
      carry the renames.

blind_spots_not_in_the_brief:
  - >
    The schema_type namespace (F-04). The class of defect the brief's §1.1
    predicts — a misunderstanding held consistently throughout — and the only
    finding here that fits that description exactly.
  - >
    The rollback's failure to prune (F-02), which no amount of exercising the
    tooling on a rehearsal corpus without renames would have revealed.
  - >
    The marker gate's conflation of an absent marker with an absent file (F-03).
  - >
    The placement of the range-expression edits before the baseline tag (F-05),
    which makes the audit the brief commissions structurally unable to test the
    constraint it most wants tested.
  - >
    Appendix A's false scope statement (F-06), in a document declared immutable.
  - >
    The write set's silence about bin/ (F-10).

metrics:
  items_audited: 19
  findings_total: 14
  findings_by_severity:
    critical: 0
    high: 3
    medium: 4
    low: 7
  claims_confirmed: 5
  claims_refuted: 6
  claims_unverifiable: 1

recommendations:
  - >
    F-01. Do not amend Appendix A or the table of contents. Raise a T06 issue
    recording that the Category A link repair reversed OQ-7 and does not satisfy
    FR-07-04, and resolve it by amending FR-07-04 and OQ-7 to the decision
    actually taken, with the reversal recorded as a CON-08 exception. The links
    are correct; the record is not. Reverting the links to restore conformance
    would be the wrong repair.
  - >
    F-02. Raise a T06 issue against dev/tools/migrate_identifiers.py. rollback()
    should compute the set of files present under the write set but absent from
    the manifest and either remove them or refuse to proceed and list them. Until
    it does, a rollback must be performed by git checkout of the pre-eb782f83
    tag, with the snapshot used only for docs/claude/project_information.md.
    Record that instruction wherever the rollback procedure is written down.
  - >
    F-03. Raise a T06 issue. evaluate_gates() should fail with a distinct exit
    code when the marker file does not exist at the configured path, rather than
    treating its absence as evidence of an unmigrated corpus. This is a
    precondition for D5 propagation, not a post-hoc tidy.
  - >
    F-04. Raise a T06 issue to decide the schema_type question explicitly. Three
    options: migrate both sides together in one coupled change; leave both and
    record the split in Appendix A as a named exception so no future maintainer
    aligns one side alone; or retire the numeric schema_type in favour of the
    class word. Recommend the second as the immediate step and the third as the
    durable one. Whichever is chosen, record it — the present state is a decision
    nobody made.
  - >
    F-05. Re-baseline the CON-01 assessment at 9f7fe29 rather than 9a1767f, and
    record the two clause edits as CON-08 exceptions in the change record. Decide
    separately whether P02.3's widened audit scope is the intended policy; it
    now reads on every protocol including those not yet written, which may well
    be what is wanted, but it was not decided.
  - >
    F-06 and F-07. One editorial change to Appendix A, which is the cheapest
    high-value item in this report: state that dev/smoke/ai/ and the eb782f83
    document set are current-scheme, and that version-history sections
    throughout the corpus are read under the scheme in force at the time of the
    entry. Add a bare-identifier column to A.2. Appendix A is declared immutable;
    a correction to a false scope statement is not the kind of change that
    declaration is meant to prevent, but it should be made under P04 rather than
    silently.
  - >
    F-08. Reconcile 614 against the run log and correct whichever figure is
    wrong, including the version-history entry for governance v10.0 if that is
    the one. Retain the run log with the audit artefacts.
  - >
    F-10. Add bin/ to refuse_paths or to migration_set, as a decision rather
    than an omission, and fold bin/propagate.sh's two defects into that change.
  - >
    Before D5 propagation, resolve F-03, F-10 and the propagate.sh defects
    together. They are the same problem seen from three sides: the migration
    instrument was designed for one repository with a known layout, and
    propagation is the first use that breaks those assumptions.
  - >
    For the next migration of this kind, place the baseline tag before the first
    preparatory edit to the corpus, not after it. F-05 exists only because the
    tag moved.

traceability:
  design_refs:
    - "dev/proposals/proposal-eb782f83-protocol-template-reordering.md v1.6 — D1 to D6, OQ-7"
    - "dev/requirements/requirements-eb782f83-protocol-template-reordering.md v0.6 — CON-01, CON-04, CON-08, CON-09, FR-02-04, FR-07-04, V-05, V-06, V-14, V-15, V-16, V-17"
    - "dev/design/design-eb782f83-protocol-template-reordering.md v0.4 — §5.2, §5.3, §5.4, §5.5, §5.6, §11.0"
    - "dev/reports/report-eb782f83-pre-migration-baseline.md v1.3 — §4.1, §6.1, §7.0"
    - "dev/audit/audit-eb782f83-brief.md v1.0"
  issue_refs: []
  related_audits:
    - audit_ref: "dev/audit/closed/audit-p08-2026-07-29-orchestrator-changes.md"
      relationship: "related"

notes: >
  Overall judgement. The migration is mechanically sound. The strongest evidence
  in this report is affirmative: the protocol corpus was carried across intact,
  line for line and in order, and that was established here without touching the
  implementer's tooling. The mapping is well formed, the frozen corpus is
  genuinely untouched, the snapshot is complete and faithful, and the Python
  modules are unaltered in substance. Nothing found here calls the renumbering
  itself into question.

  The defects cluster in two places, and neither is the corpus. The first is the
  instrument: the rollback does not prune, and the idempotence gate cannot tell a
  migrated corpus from a missing file. Both are latent, both are invisible to a
  rehearsal that never renames files or runs against a second repository, and
  both become live the moment D5 propagation begins. The second is the record:
  a ratified decision was reversed and filed as a discharge; two clause edits
  that change meaning sit one commit outside the window where CON-01 was
  measured; a namespace nobody considered now contradicts the scheme it belongs
  to; and the appendix that is supposed to make all of this legible for good
  describes its own scope incorrectly.

  On the brief's own framing. Its §5.0 was offered as incomplete and it is,
  though not where it expected. Positional prose, its leading candidate, is
  clean. The CON-08 question it raises is the right question and its answer is
  more specific than the brief allows: one accommodation was unavoidable, one
  was a reversal, and the three do not share a cause. The finding that best fits
  the brief's own description of what a self-audit cannot reach is F-04, the
  schema_type namespace — a misunderstanding held consistently from proposal to
  execution, invisible to all four compensating controls, and surviving only
  because of a word-boundary rule that contradicts the design's stated intent.

  On this audit's limits. Nothing was executed that would alter the repository,
  so F-02 and F-03 are derived by reading rather than by demonstration, and both
  should be confirmed by test before remediation is designed. C12 could not be
  established from this working tree and is recorded as unverifiable rather than
  assumed. The clause comparison at the heart of C1 depends on a stated
  definition of a clause line, given above; a different definition could yield a
  different count, though not, on this evidence, a different verdict.

version_history:
  - version: "1.0"
    date: "2026-09-22"
    changes:
      - "Initial strategic audit of b3369f5 against 9a1767f. Twelve claims adjudicated: five confirmed, six refuted, one unverifiable. Fourteen findings: three high, four medium, seven low. All eleven weak points declared in the brief assessed; six blind spots recorded that the brief does not carry."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-22 | Initial strategic audit report. Claims C1–C12 adjudicated; fourteen findings recorded by severity; brief §5.1–§5.7 assessed; six unlisted blind spots recorded. |

---

Copyright (c) 2026 William Watson. MIT License.
