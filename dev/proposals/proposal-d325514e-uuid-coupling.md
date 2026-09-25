# Proposal: Replace Sequence Numbering with UUID-Based Document Coupling

**Created:** 2025-12-12  
**Status:** Draft  
**Author:** Claude Desktop  

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Problem Statement](#problem-statement)
- [Proposed Solution](#proposed-solution)
- [Detailed Changes](#detailed-changes)
- [Impact Analysis](#impact-analysis)
- [Implementation Plan](#implementation-plan)
- [Migration Strategy](#migration-strategy)
- [Acceptance Criteria](#acceptance-criteria)
- [References](#references)
- [Version History](#version-history)

---

## Executive Summary

Current framework uses sequence numbering (NNNN) to couple related documents. This proposal replaces sequence numbers with 8-character UUIDs while maintaining iteration-based synchronization and bidirectional references. This eliminates sequence counter management overhead while preserving strict document coupling requirements.

[Return to Table of Contents](#table-of-contents)

---

## Problem Statement

### Current Mechanism

Documents couple through three elements:
1. Shared sequence numbers (NNNN format)
2. Synchronized iteration counters
3. Explicit `coupled_docs` references

### Issues

- **Sequence counter management**: Claude Desktop must maintain contiguous numbering per document class
- **Cross-repository coordination**: Sequence number conflicts possible when synchronizing across repositories
- **Document creation order dependency**: Sequence numbers imply temporal ordering not always meaningful
- **Cognitive overhead**: Sequence numbers provide no semantic value, exist solely for coupling

### Constraints

- Must maintain strict one-to-one coupling (issue↔change, change↔prompt, test↔prompt, test↔result)
- Must preserve iteration synchronization mechanism
- Must ensure bidirectional reference verification
- Must support document lifecycle management (active→closed)
- Must maintain Obsidian cross-linking

[Return to Table of Contents](#table-of-contents)

---

## Proposed Solution

### UUID-Based Identification

Replace sequence numbers with 8-character UUID v4 prefixes:
- Format: `<document-class>-<uuid>-<name>.md`
- Example: `issue-a3f2b891-memory-leak.md`
- UUID generation: First 8 hex characters of UUID v4
- Uniqueness: 4.3 billion possible values (16^8)
- Collision probability: ~0.01% at 10,000 documents

### Coupling Mechanism

Documents couple through:
1. **UUID references** in `coupled_docs` fields
2. **Iteration synchronization** (unchanged)
3. **Bidirectional verification** (unchanged)

### Document Relationships

**Strict One-to-One Coupling:**
- Issue ↔ Change (via UUID)
- Change ↔ Prompt (via UUID)
- Test ↔ Prompt (via UUID)
- Test ↔ Result (via UUID)

**Hierarchical (One-to-Many):**
- Design Master → Domain Designs (via cross-links)
- Domain Design → Component Designs (via cross-links)
- Component Design → Source Files (via file path references)

**Many-to-Many:**
- Requirements ↔ Designs (via traceability matrix)
- Designs ↔ Tests (via traceability matrix)
- Changes ↔ Design Updates (via cross-links)

[Return to Table of Contents](#table-of-contents)

---

## Detailed Changes

### P00 1.1.10 Documents

**Current:**
```markdown
- Master documents have '0000' as a sequence number and are named as <document class>-0000-master_<document name>.md
- Claude Desktop: Based on document class (design, change, issue, proposal, prompt, trace, test, result, audit) adds a sequentially contiguous <sequence number> starting at 0001 to all created documents
- Claude Desktop: Based on document class (design, change, issue, proposal, prompt, trace, test, result, audit) follows naming format <document class>-<sequence number>-<document name>.md when creating documents
- Coupled documents share sequence number and maintain synchronized iteration numbers
```

**Proposed:**
```markdown
- Master documents named: <document class>-0000-master_<document name>.md
- Claude Desktop: Generates 8-character UUID (first 8 hex digits of UUID v4) for each new document
- Claude Desktop: Naming format: <document class>-<uuid>-<document name>.md
- Claude Desktop: Design documents follow tier naming convention: master_, domain_, component_ prefixes
- Claude Desktop: Ensures related documents are Obsidian cross linked
- Document classes requiring master document: design, audit, trace, test
- All document classes (issue, change, prompt, test, result) contain internal iteration field starting at 1
- Iteration increments when document enters new cycle after failed verification
- Git commit required after iteration field modification
- Filesystem contains only current iteration; GitHub history preserves prior iterations
- Coupled documents maintain synchronized iteration numbers via explicit UUID references
```

### P00 1.1.8 Communication

**Change:**
```markdown
- Claude Desktop: Saves T04 prompt to workspace/prompt/prompt-<uuid>-<name>.md
```

### P03 1.4.2 Document Coupling

**Current:**
```markdown
- Claude Desktop: Change sequence number matches source issue sequence number
- Claude Desktop: Change iteration number matches source issue iteration number at creation
```

**Proposed:**
```markdown
- Claude Desktop: Change references source issue UUID in coupled_docs.issue_ref field
- Claude Desktop: Change iteration number matches source issue iteration number at creation
```

### P04 1.5.7 Issue-Change Coupling

**Current:**
```markdown
- Claude Desktop: Updates issue document with change_ref field when change created
```

**Proposed:**
```markdown
- Claude Desktop: Updates issue document with change_ref field (UUID) when change created
- Claude Desktop: Verifies bidirectional linkage exists: issue.change_ref ↔ change.coupled_docs.issue_ref
```

### P06 1.7.12 Test-Prompt Coupling

**Current:**
```markdown
- Test sequence number matches source prompt sequence number
```

**Proposed:**
```markdown
- Test references source prompt UUID in coupled_docs.prompt_ref field
```

### P06 1.7.13 Test Result Lifecycle

**Current:**
```markdown
- Results named: result-NNNN-<n>.md in workspace/test/result/
- Failed results trigger issue creation with matching sequence number
```

**Proposed:**
```markdown
- Results named: result-<uuid>-<n>.md in workspace/test/result/
- Result references parent test UUID in coupled_docs.test_ref field
- Failed results trigger issue creation (new UUID assigned)
```

### P08 1.9.5 Audit Deliverables

**Current:**
```markdown
- Claude Desktop: Creates audit report following naming format: audit-<sequence number>-<audit name>.md
```

**Proposed:**
```markdown
- Claude Desktop: Creates audit report following naming format: audit-<uuid>-<audit name>.md
```

### P09 1.10.2 Prompt Creation

**Current:**
```markdown
- Claude Desktop: Saves prompts with naming format prompt-<sequence number>-<name>.md in workspace/prompt/
- Claude Desktop: Prompt sequence number matches source change sequence number
```

**Proposed:**
```markdown
- Claude Desktop: Saves prompts with naming format prompt-<uuid>-<name>.md in workspace/prompt/
- Claude Desktop: Prompt references source change UUID in coupled_docs.change_ref field
```

[Return to Table of Contents](#table-of-contents)

---

## Detailed Changes (Templates)

### T02 Change Template

**Current:**
```yaml
change_info:
  id: ""  # change-NNNN format
  coupled_docs:
    issue_ref: "issue-NNNN"  # Must match sequence number
    issue_iteration: 1  # Must match issue.iteration
```

**Proposed:**
```yaml
change_info:
  id: ""  # change-<uuid> format (8 char hex)
  coupled_docs:
    issue_ref: ""  # issue-<uuid> format
    issue_iteration: 1  # Must match issue.iteration
```

### T02 Change Schema

**Current:**
```yaml
id:
  type: string
  pattern: "^change-[0-9]{4}$"
coupled_docs:
  properties:
    issue_ref:
      type: string
      pattern: "^issue-[0-9]{4}$"
```

**Proposed:**
```yaml
id:
  type: string
  pattern: "^change-[0-9a-f]{8}$"
coupled_docs:
  properties:
    issue_ref:
      type: string
      pattern: "^issue-[0-9a-f]{8}$"
```

### T03 Issue Template

**Current:**
```yaml
issue_info:
  id: ""  # issue-NNNN format
  coupled_docs:
    change_ref: ""  # change-NNNN when created
    change_iteration: null  # Matches change.iteration
```

**Proposed:**
```yaml
issue_info:
  id: ""  # issue-<uuid> format (8 char hex)
  coupled_docs:
    change_ref: ""  # change-<uuid> when created
    change_iteration: null  # Matches change.iteration
```

### T03 Issue Schema

**Current:**
```yaml
id:
  type: string
  pattern: "^issue-[0-9]{4}$"
coupled_docs:
  properties:
    change_ref:
      type: string
      pattern: "^change-[0-9]{4}$"
```

**Proposed:**
```yaml
id:
  type: string
  pattern: "^issue-[0-9a-f]{8}$"
coupled_docs:
  properties:
    change_ref:
      type: string
      pattern: "^change-[0-9a-f]{8}$"
```

### T04 Prompt Template

**Current:**
```yaml
prompt_info:
  id: ""  # prompt-NNNN format
  coupled_docs:
    change_ref: "change-NNNN"  # Must match sequence number
    change_iteration: 1  # Must match change.iteration
```

**Proposed:**
```yaml
prompt_info:
  id: ""  # prompt-<uuid> format (8 char hex)
  coupled_docs:
    change_ref: ""  # change-<uuid> format
    change_iteration: 1  # Must match change.iteration
```

### T04 Prompt Schema

**Current:**
```yaml
id:
  type: string
  pattern: "^prompt-[0-9]{4}$"
coupled_docs:
  properties:
    change_ref:
      type: string
      pattern: "^change-[0-9]{4}$"
```

**Proposed:**
```yaml
id:
  type: string
  pattern: "^prompt-[0-9a-f]{8}$"
coupled_docs:
  properties:
    change_ref:
      type: string
      pattern: "^change-[0-9a-f]{8}$"
```

### T05 Test Template

**Current:**
```yaml
test_info:
  id: ""  # test-NNNN format
  coupled_docs:
    prompt_ref: "prompt-NNNN"  # Must match sequence number
    prompt_iteration: 1  # Must match prompt.iteration
    result_ref: ""  # result-NNNN when created
```

**Proposed:**
```yaml
test_info:
  id: ""  # test-<uuid> format (8 char hex)
  coupled_docs:
    prompt_ref: ""  # prompt-<uuid> format
    prompt_iteration: 1  # Must match prompt.iteration
    result_ref: ""  # result-<uuid> when created
```

### T05 Test Schema

**Current:**
```yaml
id:
  type: string
  pattern: "^test-[0-9]{4}$"
coupled_docs:
  properties:
    prompt_ref:
      type: string
      pattern: "^prompt-[0-9]{4}$"
    result_ref:
      type: string
      pattern: "^result-[0-9]{4}$"
```

**Proposed:**
```yaml
id:
  type: string
  pattern: "^test-[0-9a-f]{8}$"
coupled_docs:
  properties:
    prompt_ref:
      type: string
      pattern: "^prompt-[0-9a-f]{8}$"
    result_ref:
      type: string
      pattern: "^result-[0-9a-f]{8}$"
```

### T06 Result Template

**Current:**
```yaml
result_info:
  id: ""  # result-NNNN format
  coupled_docs:
    test_ref: "test-NNNN"  # Must match test sequence
    test_iteration: 1  # Must match test.iteration
```

**Proposed:**
```yaml
result_info:
  id: ""  # result-<uuid> format (8 char hex)
  coupled_docs:
    test_ref: ""  # test-<uuid> format
    test_iteration: 1  # Must match test.iteration
```

### T06 Result Schema

**Current:**
```yaml
id:
  type: string
  pattern: "^result-[0-9]{4}$"
coupled_docs:
  properties:
    test_ref:
      type: string
      pattern: "^test-[0-9]{4}$"
```

**Proposed:**
```yaml
id:
  type: string
  pattern: "^result-[0-9a-f]{8}$"
coupled_docs:
  properties:
    test_ref:
      type: string
      pattern: "^test-[0-9a-f]{8}$"
```

[Return to Table of Contents](#table-of-contents)

---

## Impact Analysis

### Benefits

**Eliminates Complexity:**
- No sequence counter management per document class
- No contiguous numbering requirements
- No cross-repository sequence coordination

**Maintains Coupling:**
- UUID references provide unique identification
- Iteration synchronization unchanged
- Bidirectional verification unchanged
- Document lifecycle management unchanged

**Improves Scalability:**
- 4.3 billion unique IDs per document class
- Natural distributed document creation
- Cross-repository document references trivial

**Preserves Semantics:**
- Document names remain human-readable
- Master/domain/component prefixes unchanged
- Obsidian cross-linking compatible

### Risks

**UUID Collision:**
- Probability: ~0.01% at 10,000 documents
- Mitigation: Collision detection in document creation
- Fallback: Regenerate UUID on collision

**Human Readability:**
- UUIDs less readable than sequence numbers
- Mitigation: Document names provide semantic context
- Pattern: `<class>-<uuid>-<descriptive-name>.md`

**Migration Complexity:**
- Existing sequence-numbered documents remain valid
- New documents use UUID format
- Mixed naming during transition period

### Affected Components

**Protocol Sections:**
- P00 1.1.8 Communication
- P00 1.1.10 Documents
- P03 1.4.2 Document Coupling
- P04 1.5.7 Issue-Change Coupling
- P06 1.7.12 Test-Prompt Coupling
- P06 1.7.13 Test Result Lifecycle
- P08 1.9.5 Audit Deliverables
- P09 1.10.2 Prompt Creation

**Templates:**
- T02 Change (template + schema)
- T03 Issue (template + schema)
- T04 Prompt (template + schema)
- T05 Test (template + schema)
- T06 Result (template + schema)

**Unchanged:**
- Iteration synchronization mechanism
- Document lifecycle management
- Closure criteria
- Traceability matrix structure
- Design hierarchy (master/domain/component)

[Return to Table of Contents](#table-of-contents)

---

## Implementation Plan

### Phase 1: Governance Document Updates

1. Update P00 1.1.10 Documents section
2. Update P00 1.1.8 Communication section
3. Update P03 1.4.2 Document Coupling
4. Update P04 1.5.7 Issue-Change Coupling
5. Update P06 1.7.12 Test-Prompt Coupling
6. Update P06 1.7.13 Test Result Lifecycle
7. Update P08 1.9.5 Audit Deliverables
8. Update P09 1.10.2 Prompt Creation

### Phase 2: Template Updates

1. Update T02 Change template and schema
2. Update T03 Issue template and schema
3. Update T04 Prompt template and schema
4. Update T05 Test template and schema
5. Update T06 Result template and schema

### Phase 3: Validation

1. Verify schema pattern regex: `^[document-class]-[0-9a-f]{8}$`
2. Verify coupled_docs reference patterns
3. Test UUID generation (Python: `uuid.uuid4()[:8]`)
4. Validate Obsidian cross-linking with UUID format

### Phase 4: Documentation

1. Update version history in governance.md
2. Create migration guide for existing projects
3. Document UUID collision handling procedure

[Return to Table of Contents](#table-of-contents)

---

## Migration Strategy

### New Projects

- Use UUID format from P01 initialization
- No sequence-numbered documents created
- Clean implementation of UUID-based coupling

### Existing Projects

**Option 1: Coexistence**
- Existing sequence-numbered documents remain valid
- New documents use UUID format
- Mixed naming convention during transition
- No forced migration required

**Option 2: Bulk Migration**
- Create migration script to rename documents
- Update all coupled_docs references
- Single transition commit
- Higher risk, clean result

**Recommendation:** Option 1 (Coexistence)
- Lower risk
- Gradual transition
- Existing work preserved
- New work benefits immediately

### Collision Detection

```python
import uuid
import os
from pathlib import Path

def generate_unique_uuid(document_class: str, workspace_path: Path) -> str:
    """Generate unique 8-char UUID, retry on collision."""
    max_attempts = 100
    for _ in range(max_attempts):
        doc_uuid = str(uuid.uuid4())[:8]
        pattern = f"{document_class}-{doc_uuid}-*.md"
        if not list(workspace_path.glob(pattern)):
            return doc_uuid
    raise RuntimeError(f"Failed to generate unique UUID after {max_attempts} attempts")
```

[Return to Table of Contents](#table-of-contents)

---

## Acceptance Criteria

### Functional Requirements

- [ ] Claude Desktop generates 8-character UUIDs for new documents
- [ ] Document naming follows `<class>-<uuid>-<name>.md` format
- [ ] Coupled documents reference via UUID in `coupled_docs` fields
- [ ] Iteration synchronization maintains current behavior
- [ ] Bidirectional reference verification works with UUIDs
- [ ] Document closure workflow unchanged
- [ ] Obsidian cross-linking functions with UUID format

### Schema Validation

- [ ] All template schemas validate UUID patterns
- [ ] Pattern regex: `^[document-class]-[0-9a-f]{8}$`
- [ ] coupled_docs fields validate referenced UUIDs
- [ ] Iteration fields remain integer validation

### Traceability

- [ ] Traceability matrix references documents by UUID
- [ ] Requirements ↔ Design ↔ Code ↔ Test links maintain
- [ ] Audit reports reference findings by document UUID

### Documentation

- [ ] Governance document updated with UUID format
- [ ] All protocol sections reflect UUID coupling
- [ ] All templates updated with UUID fields
- [ ] All schemas updated with UUID patterns
- [ ] Version history reflects changes

[Return to Table of Contents](#table-of-contents)

---

## References

- Governance Framework: `/Users/williamwatson/Documents/GitHub/AI-Governance-and-Orchestration/governance.md`
- Python UUID module: `uuid.uuid4()` for UUID v4 generation
- ISO/IEC 9834-8:2014 - UUID specification
- Regex pattern for 8-char hex: `^[0-9a-f]{8}$`

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date       | Author         | Changes                              |
|---------|------------|----------------|--------------------------------------|
| 1.0     | 2025-12-12 | Claude Desktop | Initial proposal draft               |
| 1.1 | 2026-09-25 | Claude Desktop | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
