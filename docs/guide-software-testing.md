Created: 2026 March 05

# Testing Guidance for Software Development

---

## Table of Contents

[Introduction](<#introduction>)
[Testing Workflow](<#testing workflow>)
[Test Types](<#test types>)
[Test Organization](<#test organization>)
[Progressive Validation Strategy](<#progressive validation strategy>)
[Test Isolation](<#test isolation>)
[Platform Considerations](<#platform considerations>)
[Document Coupling](<#document coupling>)
[Traceability](<#traceability>)
[Best Practices](<#best practices>)
[Glossary](<#glossary>)
[Version History](<#version history>)

---

## Introduction

This document provides comprehensive guidance for implementing testing within the AI Governance and Orchestration Framework. Testing follows governance protocol P15 and employs systematic validation across multiple test types.

### Purpose

Testing verifies:
- Component functionality matches design specifications
- Interface contracts are honored
- Error handling is robust
- Non-functional requirements are satisfied
- Regressions are prevented

### Scope

This guidance covers:
- Test workflow from creation to closure
- Test type selection and implementation
- Validation strategies
- Document coupling and traceability
- Platform considerations

[Return to Table of Contents](<#table of contents>)

---

## Testing Workflow

### Overview

```
Code Generation → Test Documentation → Test Script Creation →
Execution → Results → Issue Creation (if needed) → Closure
```

### Workflow Steps

#### 1. Test Documentation Creation (P15.2)

**Actor:** Strategic Domain

**Process:**
1. Read template from `ai/governance/software-engineering/templates/T04-test.md`
2. Create test document from generated source code
3. Save to `ai/workspace/test/test-<uuid>-<n>.md`
4. Couple to source prompt via UUID reference
5. Match iteration numbers with source prompt

**Inputs:**
- Generated source code from Tactical Domain
- Component design specifications
- Requirements traceability

**Outputs:**
- T04 test documentation
- Test strategy and approach
- Test case specifications

#### 2. Test Script Generation (P15.3)

**Actor:** Strategic Domain

**Automatic:** Precedes test execution

**Process:**
1. Generate pytest files from T04 documentation
2. Create test files with `test_*.py` naming convention
3. Place in appropriate directory:
   - Component tests: `tests/<component>/test_*.py`
   - Validation scripts: `tests/test_*.py` (root level)
4. Implement test cases per T04 specifications
5. Use pytest or unittest per `pyproject.toml`

**Outputs:**
- Executable pytest files
- Test fixtures and mocks
- Test utilities

#### 3. Test Execution

**Actor:** Human

**Process:**
1. Execute tests via pytest command
2. Capture pass/fail status
3. Generate coverage reports
4. Preserve test artifacts (logs, reports)

**Commands:**
```bash
# Execute all tests
pytest tests/

# Execute component tests
pytest tests/<component>/

# Execute with coverage
pytest --cov=src tests/

# Verbose output
pytest -v tests/
```

#### 4. Progressive Validation (P15.15)

**Targeted Validation:**
- Execute minimal test for specific fix
- Create ephemeral script at `tests/` root
- Quick verification cycle
- Purpose: Confirm specific bug fix

**Integration Validation:**
- Test dependent components
- Execute component subdirectory tests
- Verify interface contracts
- Purpose: Ensure no ripple effects

**Regression Validation:**
- Full test suite execution
- All permanent tests
- Required before closure
- Purpose: Comprehensive verification

#### 5. Result Documentation (P15.13)

**Actor:** Strategic Domain

**Process:**
1. Review test execution output
2. Create result document using T05 template
3. Save to `ai/workspace/test/result/result-<uuid>-<n>.md`
4. Reference parent test UUID
5. Match parent test iteration number

**Result Document Contains:**
- Test execution summary
- Pass/fail status per test case
- Coverage metrics
- Issues identified
- Recommendations

#### 6. Outcome Handling

**Tests Pass:**
1. Progress through validation stages
2. Update traceability matrix
3. Move to document closure workflow
4. Archive to respective `closed/` subfolders

**Tests Fail:**
1. Create issue document via P03
2. Assign new UUID to issue
3. Follow issue → change → debug cycle
4. Increment iteration numbers
5. Return to test execution

[Return to Table of Contents](<#table of contents>)

---

## Test Types

### Unit Tests

**Definition:** Verification of single component in isolation

**Characteristics:**
- **Scope:** Individual functions, classes, modules
- **Dependencies:** Fully mocked via `unittest.mock`
- **Location:** `tests/<component>/test_*.py`
- **Platform:** Development platform
- **Mandatory:** Yes, for all components

**Purpose:**
- Verify component logic correctness
- Test edge cases and boundary conditions
- Validate error handling
- Confirm interface contracts

**Example Structure:**
```python
# tests/<component>/test_<module>.py

import unittest
from unittest.mock import Mock, patch
from src.<component>.<module> import <ClassName>

class Test<ClassName>(unittest.TestCase):
    def setUp(self):
        """Create test fixtures with mocked dependencies."""
        self.mock_dep = Mock()
        self.instance = <ClassName>(param="value")

    def test_operation_success(self):
        """Verify successful operation."""
        with patch('src.<component>.<dependency>') as mock:
            mock.return_value.method.return_value = True
            result = self.instance.operate()
            self.assertTrue(result)

    def test_operation_timeout(self):
        """Verify timeout handling."""
        with patch.object(self.instance, 'method') as mock:
            mock.side_effect = TimeoutError()
            with self.assertRaises(TimeoutError):
                self.instance.operate()
```

### Integration Tests

**Definition:** Verification of component boundary interactions

**Characteristics:**
- **Scope:** Multi-component interactions
- **Dependencies:** Actual subsystems where integration testing required
- **Location:** `tests/<component>/` or dedicated integration directories
- **Platform:** Target deployment platform
- **Frequency:** As needed for complex interactions

**Purpose:**
- Verify interface contracts between components
- Validate data flow correctness
- Test component coordination
- Confirm integration architecture

**Example Structure:**
```python
# tests/integration/test_<scenario>.py

import pytest
from src.<domain>.<component_a> import <ClassA>
from src.<domain>.<component_b> import <ClassB>

class Test<Scenario>Pipeline:
    @pytest.fixture
    def component_b(self):
        """Create actual component B instance."""
        return <ClassB>(connection_string="test_db")

    @pytest.fixture
    def component_a(self):
        """Create component A with test configuration."""
        return <ClassA>(host="test_host", port=9999)

    def test_data_flow(self, component_a, component_b):
        """Verify data flows from A to B."""
        data = component_a.get_data()
        result = component_b.write(data)
        retrieved = component_b.get_latest("test_key")
        assert retrieved.value == data.value
```

### System Tests

**Definition:** End-to-end application verification

**Characteristics:**
- **Scope:** Full application deployment
- **Dependencies:** Complete system stack
- **Location:** Separate system test suite
- **Platform:** Target deployment platform exclusively
- **Frequency:** Pre-release milestones

**Purpose:**
- Verify complete system functionality
- Test deployment procedures
- Validate system configuration
- Confirm operational readiness

**Example Scenario:**
```python
# tests/system/test_<application>.py

import pytest
import subprocess
import time
import requests

class Test<Application>Deployment:
    def test_full_deployment_cycle(self):
        """Verify complete system deployment and operation."""
        # Start system services (platform-specific command)
        subprocess.run(["<start_command>"])
        time.sleep(5)

        # Verify service health
        response = requests.get("http://localhost:<port>/health")
        assert response.status_code == 200

        # Verify data acquisition
        time.sleep(10)
        data = requests.get("http://localhost:<port>/api/v1/<resource>")
        assert data.json()["<key>"] is not None

        # Cleanup
        subprocess.run(["<stop_command>"])
```

### Acceptance Tests

**Definition:** Requirement validation with stakeholder involvement

**Characteristics:**
- **Scope:** Functional and non-functional requirements
- **Dependencies:** Production-like environment
- **Location:** Acceptance test suite
- **Platform:** Target deployment platform
- **Frequency:** Milestone-based

**Purpose:**
- Verify requirements satisfied
- Obtain stakeholder acceptance
- Validate user workflows

**Example Structure:**
```python
# tests/acceptance/test_<domain>_requirements.py

class Test<Domain>Requirements:
    def test_req_001_configurable_interval(self):
        """REQ-001: System operates at configurable intervals."""
        # Configure interval
        config = {"interval": 1}

        # Execute operation
        # Record timestamps

        # Verify interval compliance
        assert all(delta >= 1.0 for delta in intervals)

    def test_req_nf_perf_001_latency(self):
        """REQ-NF-PERF-001: 99.9% requests within 1 second."""
        # Execute requests
        # Measure latency

        p999 = calculate_percentile(latencies, 99.9)
        assert p999 <= 1.0
```

### Regression Tests

**Definition:** Comprehensive verification preventing new defects

**Characteristics:**
- **Scope:** All unit and integration tests
- **Lifecycle:** Permanent test suite
- **Location:** `tests/<component>/` directories
- **Frequency:** Every code change

**Purpose:**
- Prevent reintroduction of resolved defects
- Verify existing functionality unchanged
- Maintain system stability
- Enable confident refactoring

**Management:**
- Permanent tests remain in repository
- Executed automatically via CI/CD
- Coverage tracked over time
- Failed tests block deployment

### Performance Tests

**Definition:** Non-functional requirement validation

**Characteristics:**
- **Scope:** Response times, throughput, resource usage
- **Platform:** Target deployment platform exclusively
- **Frequency:** Periodic benchmarking

**Purpose:**
- Validate NFR compliance
- Measure system capacity
- Identify bottlenecks
- Establish performance baselines

**Example Structure:**
```python
# tests/performance/test_<component>_performance.py

import pytest
import time
from src.<domain>.<module> import <ClassName>

class Test<ClassName>Performance:
    def test_nfr_poll_rate(self):
        """NFR-PERF-001: Support target operation rate."""
        instance = <ClassName>(host="target_host")

        durations = []
        for _ in range(100):
            start = time.time()
            instance.operate()
            durations.append(time.time() - start)

        p95 = sorted(durations)[95]
        assert p95 <= 1.0

    def test_nfr_memory_footprint(self):
        """NFR-PERF-002: Memory footprint within budget."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 512
```

[Return to Table of Contents](<#table of contents>)

---

## Test Organization

### Directory Structure

```
tests/
├── <component_a>/               # Unit tests for component A
│   ├── test_<module>.py
│   └── test_<module_b>.py
├── <component_b>/               # Unit tests for component B
│   └── test_<module>.py
├── integration/                 # Integration tests
│   └── test_<scenario>.py
├── system/                      # System tests
│   └── test_<application>.py
├── acceptance/                  # Acceptance tests
│   └── test_<domain>_requirements.py
├── performance/                 # Performance tests
│   └── test_<component>_performance.py
└── test_validation_<uuid>.py    # Ephemeral validation (removed post-verification)
```

### Permanent vs. Ephemeral Tests

**Permanent Tests:**
- Location: `tests/<component>/` subdirectories
- Lifecycle: Maintained long-term
- Purpose: Regression suite
- Management: Version controlled, never deleted

**Ephemeral Tests:**
- Location: `tests/` root level
- Lifecycle: Removed post-verification
- Purpose: Targeted fix validation
- Naming: `test_validation_<issue_uuid>.py`

### Test Naming Conventions

**Files:**
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<integration_scenario>.py`
- Validation scripts: `test_validation_<issue_uuid>.py`

**Classes:**
- `TestClassName` (CamelCase)
- Descriptive of component under test

**Methods:**
- `test_<function>_<scenario>` (snake_case)
- Descriptive of test purpose
- Example: `test_connect_timeout_handling`

[Return to Table of Contents](<#table of contents>)

---

## Progressive Validation Strategy

### Three-Stage Validation

Progressive validation employs graduated testing during debug cycles:

#### Stage 1: Targeted Validation

**Purpose:** Verify specific fix works

**Process:**
1. Create minimal ephemeral test at `tests/` root
2. Execute only test relevant to fix
3. Verify issue resolved

**Example:**
```python
# tests/test_validation_a1b2c3d4.py

def test_<specific_fix>():
    """Validate issue a1b2c3d4: <description>."""
    instance = <ClassName>(param="test_value")
    result = instance.operate()

    assert result.value > 0
```

**When to Use:**
- Initial verification after bug fix
- Quick iteration cycles
- Single component changes

#### Stage 2: Integration Validation

**Purpose:** Ensure no ripple effects on dependent components

**Process:**
1. Execute tests for affected component
2. Execute tests for dependent components
3. Verify interface contracts maintained

**Example:**
```bash
# Execute affected component tests
pytest tests/<component_a>/

# Execute dependent component tests
pytest tests/<component_b>/

# Execute integration tests
pytest tests/integration/
```

**When to Use:**
- After targeted validation passes
- Changes affect multiple components
- Interface modifications

#### Stage 3: Regression Validation

**Purpose:** Comprehensive verification before closure

**Process:**
1. Execute full permanent test suite
2. All unit tests
3. All integration tests
4. Generate coverage report

**Example:**
```bash
# Execute complete test suite
pytest tests/ --cov=src --cov-report=html
```

**When to Use:**
- Before document closure
- After integration validation passes
- Pre-release verification

### Validation Workflow Decision Tree

```
Fix Implemented
    ↓
Targeted Validation
    ↓
Pass? → No → Debug → Repeat Targeted
    ↓
   Yes
    ↓
Integration Validation
    ↓
Pass? → No → Debug → Repeat Targeted
    ↓
   Yes
    ↓
Regression Validation
    ↓
Pass? → No → Debug → Repeat Targeted
    ↓
   Yes
    ↓
Human Acceptance
    ↓
Document Closure
```

### Script Lifecycle Management

**Creation:**
- Targeted validation requires ephemeral script
- Create at `tests/` root
- Reference issue UUID in filename

**Execution:**
- Run during targeted validation stage
- May be reused in integration stage
- Not included in regression suite

**Removal:**
- After regression validation passes
- Human acceptance obtained
- Document closure workflow initiated

**Archival:**
- Move to `deprecated/` or delete
- Git history preserves script
- No need for long-term retention

[Return to Table of Contents](<#table of contents>)

---

## Test Isolation

### Purpose

Test isolation ensures:
- Tests do not interfere with each other
- Tests are repeatable
- Tests can execute in parallel
- Test failures are deterministic

### Techniques

#### 1. Temporary Environments

**Problem:** Tests that create files, directories, or modify state

**Solution:** Use `tempfile` and `shutil` for isolated environments

**Example:**
```python
import tempfile
import shutil
import os

class TestFileOperations:
    def setUp(self):
        """Create temporary test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_file_creation(self):
        """Test operates in isolated directory."""
        test_file = os.path.join(self.test_dir, "test.txt")
        # Test file operations in self.test_dir
```

#### 2. Dependency Mocking

**Problem:** Tests that require external services (network, database, hardware)

**Solution:** Use `unittest.mock` to isolate dependencies

**Example:**
```python
from unittest.mock import Mock, patch

class TestComponent:
    def test_operation_with_mock(self):
        """Test operation without actual external dependency."""
        with patch('src.<module>.<ExternalClass>') as mock_dep:
            mock_dep.return_value.method.return_value = Mock(
                data=[1, 2, 3]
            )

            instance = <ClassName>(host="test_host")
            result = instance.operate()

            assert result == [1, 2, 3]
```

#### 3. Fixture Isolation

**Problem:** Tests that share setup code but need independence

**Solution:** Use pytest fixtures with appropriate scope

**Example:**
```python
import pytest

@pytest.fixture
def isolated_database():
    """Create isolated database for each test."""
    db = create_test_database()
    yield db
    db.cleanup()

def test_write_operation(isolated_database):
    """Each test gets fresh database."""
    isolated_database.write(data)
    # Test executes with clean database state
```

#### 4. State Reset

**Problem:** Tests that modify global state or singletons

**Solution:** Reset state in `setUp` and `tearDown`

**Example:**
```python
class TestConfiguration:
    def setUp(self):
        """Save original configuration."""
        self.original_config = Config.get_instance().copy()

    def tearDown(self):
        """Restore original configuration."""
        Config.get_instance().restore(self.original_config)

    def test_config_modification(self):
        """Test can modify config without affecting other tests."""
        Config.get_instance().set("key", "value")
        # Changes isolated to this test
```

### Parallel Execution

Proper isolation enables parallel test execution:

```bash
# Execute tests in parallel (4 workers)
pytest -n 4 tests/

# Requires: pip install pytest-xdist
```

[Return to Table of Contents](<#table of contents>)

---

## Platform Considerations

### Development vs. Target Platforms

**Development Platform:**
- Local development machine
- Extensive mocking capabilities
- Fast iteration cycles
- Unit test execution

**Target Deployment Platform:**
- Defined in project design documents
- Actual system services
- Integration/system testing
- Performance validation

### Test Type Distribution

| Test Type | Development Platform | Target Platform |
|---|---|---|
| Unit | ✓ (Primary) | Optional |
| Integration | ✓ (Mocked) | ✓ (Required) |
| System | ✗ | ✓ (Exclusive) |
| Acceptance | ✗ | ✓ (Exclusive) |
| Regression | ✓ (Primary) | ✓ (Validation) |
| Performance | ✗ | ✓ (Exclusive) |

### Platform-Specific Requirements

**Development Platform:**
- Comprehensive mocking of system dependencies
- Simulated external interfaces
- Fast test execution
- Continuous integration friendly

**Target Platform:**
- Actual external service connections
- Real subsystem instances
- Authentic network conditions
- Production-equivalent configuration

Specific platform details (OS, hardware, tooling) are defined in project design documents per P15.17.

### Cross-Platform Testing Strategy

1. **Unit Tests:** Execute on development platform with full mocking
2. **Pre-Commit:** Run regression suite on development platform
3. **Integration Tests:** Execute subset on target platform periodically
4. **Pre-Release:** Run complete suite on target platform
5. **Performance Benchmarks:** Execute exclusively on target platform

### Hardware Availability

**Limited Target Hardware:**
- Prioritize unit tests with mocking
- Schedule integration testing windows
- Document platform-specific constraints

**Continuous Target Access:**
- Integrate target platform into CI/CD
- Execute integration tests automatically
- Perform continuous performance monitoring

[Return to Table of Contents](<#table of contents>)

---

## Document Coupling

### Test-Prompt Coupling

**Relationship:** One-to-one coupling between test and source prompt

**Mechanism:**
- Test document references source prompt UUID
- Field: `coupled_docs.prompt_ref`
- Iteration numbers synchronized

**Example:**
```yaml
# test-12345678-<component>.md
coupled_docs:
  prompt_ref: "abcd1234"  # UUID of source prompt
  iteration: 1
```

### Test-Result Coupling

**Relationship:** One-to-many (test can have multiple result documents through iterations)

**Mechanism:**
- Result document references parent test UUID
- Field: `coupled_docs.test_ref`
- Iteration numbers synchronized

**Example:**
```yaml
# result-87654321-1.md
coupled_docs:
  test_ref: "12345678"  # UUID of parent test
  iteration: 1
```

### Iteration Synchronization

**Rules:**
1. Test iteration matches source prompt iteration at creation
2. When prompt iteration increments (debug cycle), test iteration increments
3. Result iteration matches parent test iteration
4. Git commit captures synchronized state
5. Validation verifies iteration match before proceeding

**Debug Cycle:**
```
Prompt iteration 1 → Test iteration 1 → Result iteration 1 (FAIL)
    ↓
Issue created → Change created → Debug prompt iteration 2
    ↓
Test iteration 2 → Result iteration 2 (PASS)
    ↓
Document closure
```

### Coupling Verification

Strategic Domain verifies:
- UUID references are valid
- Iteration numbers synchronized
- Bidirectional linkage exists
- No orphaned documents

[Return to Table of Contents](<#table of contents>)

---

## Traceability

### Traceability Matrix Updates

After test execution, Strategic Domain updates the traceability matrix (P01) in:
`ai/workspace/trace/trace-<name>-master.md`

### Required Linkages

**Forward Traceability:**
- Requirement → Design → Code → Test
- Navigate from requirement to test verification

**Backward Traceability:**
- Test → Code → Design → Requirement
- Navigate from test to originating requirement

### Traceability Matrix Sections

#### 1. Functional Requirements

| Req ID | Requirement | Design | Code | Test | Status |
|---|---|---|---|---|---|
| REQ-001 | \<requirement description\> | design-\<name\>-master | src/\<module\>.py | test-\<uuid\> | ✓ |

#### 2. Non-Functional Requirements

| Req ID | Requirement | Target | Design | Code | Test | Status |
|---|---|---|---|---|---|---|
| NFR-PERF-001 | \<nfr description\> | \<target\> | design-\<name\>-master | src/\<module\>.py | test-\<uuid\> | ✓ |

#### 3. Component Mapping

| Component | Requirements | Design | Source | Test |
|---|---|---|---|---|
| \<ComponentName\> | REQ-001, REQ-002 | design-component-\<name\> | src/\<module\>.py | test-\<uuid\> |

#### 4. Test Coverage

| Test File | Requirements Verified | Code Coverage |
|---|---|---|
| test-\<uuid\> | REQ-001, REQ-002 | \<n\>% |

### Coverage Metrics

Strategic Domain tracks:
- **Requirement Coverage:** Percentage of requirements with tests
- **Code Coverage:** Percentage of code exercised by tests
- **Branch Coverage:** Percentage of code branches tested
- **Function Coverage:** Percentage of functions with tests

### Gap Identification

Strategic Domain identifies:
- Requirements without test coverage
- Code without test coverage
- Tests without requirement linkage
- Orphaned test documents

[Return to Table of Contents](<#table of contents>)

---

## Best Practices

### Test Design

1. **Single Responsibility:** Each test verifies one specific behavior
2. **Independence:** Tests do not depend on execution order
3. **Repeatability:** Tests produce consistent results
4. **Self-Documenting:** Test names clearly describe purpose
5. **Fast Execution:** Unit tests complete in milliseconds

### Test Data

1. **Fixtures:** Use fixtures for reusable test data
2. **Factories:** Create test data programmatically
3. **Boundaries:** Test edge cases and boundary conditions
4. **Invalid Input:** Test error handling with invalid data
5. **Realistic Data:** Use representative data values

### Assertion Strategy

1. **Specific Assertions:** Test exact expected values
2. **Multiple Assertions:** Group related assertions logically
3. **Descriptive Messages:** Provide context in assertion messages
4. **Exception Testing:** Verify exceptions raised correctly
5. **State Verification:** Confirm state changes as expected

### Mock Usage

1. **Interface Mocking:** Mock at interface boundaries
2. **Behavior Verification:** Verify mock interactions when appropriate
3. **Minimal Mocking:** Mock only what is necessary
4. **Realistic Behavior:** Mocks behave like real components
5. **Mock Cleanup:** Reset mocks between tests

### Test Maintenance

1. **Update with Code:** Tests evolve with codebase
2. **Refactor Tests:** Apply refactoring to test code
3. **Remove Obsolete:** Delete tests for removed functionality
4. **Document Changes:** Update test documentation
5. **Review Coverage:** Monitor coverage trends

### Performance Testing

1. **Baseline Establishment:** Record initial performance metrics
2. **Consistent Environment:** Test in controlled conditions
3. **Statistical Validity:** Run sufficient iterations
4. **Realistic Load:** Use production-like workloads
5. **Trend Monitoring:** Track performance over time

### Continuous Integration

1. **Automated Execution:** Tests run on every commit
2. **Fast Feedback:** Fail fast on test failures
3. **Coverage Enforcement:** Maintain minimum coverage thresholds
4. **Parallel Execution:** Run tests concurrently
5. **Platform Testing:** Validate on target platforms

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|---|---|
| **Acceptance Test** | Validation test with stakeholder involvement verifying requirements satisfaction |
| **Assertion** | Statement verifying expected test outcome |
| **Code Coverage** | Metric measuring percentage of code exercised by tests |
| **Coupling** | Relationship between documents tracked via UUID references |
| **Ephemeral Test** | Temporary validation script removed after verification |
| **Fixture** | Reusable test setup providing consistent test environment |
| **Integration Test** | Test verifying component boundary interactions |
| **Iteration** | Document version number incremented during debug cycles |
| **Mock** | Simulated object replacing real dependency in tests |
| **Performance Test** | Test validating non-functional requirements (speed, capacity) |
| **Progressive Validation** | Graduated testing strategy: targeted → integration → regression |
| **Regression Test** | Permanent test preventing reintroduction of defects |
| **System Test** | End-to-end test of complete application deployment |
| **Target Platform** | Deployment environment defined in project design documents |
| **Traceability** | Bidirectional linking between requirements, design, code, tests |
| **Unit Test** | Test verifying single component in isolation |
| **Validation Script** | Temporary test verifying specific fix |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-01-08 | Initial testing guidance document |
| 1.1 | 2026-03-05 | Relocated from issues/ to examples/; replaced project-specific content with generic equivalents; replaced Claude Desktop/Claude Code actor labels with Strategic/Tactical Domain; genericised all code examples, directory structures, and traceability matrix entries; updated Platform Considerations to remove hardcoded platform references |
| 1.2 | 2026-06-14 | Relocated workspace/ → ai/workspace/ in test, result, and trace path references |
| 1.3 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |
| 1.4 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
