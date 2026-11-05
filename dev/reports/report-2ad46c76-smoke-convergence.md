# REVISE → Fix → SHIP Convergence in dev/smoke

Created: 2026 November 5

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Runs](#30-runs)
- [4.0 Reviewer Comparison](#40-reviewer-comparison)
- [5.0 Observations](#50-observations)
- [6.0 Verdict](#60-verdict)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records the live check of the loop's convergence path: a review that rejects faulty work (REVISE), a worker fix, and a SHIP in a later round. The path had been seen only up to REVISE (change-c37198be Run B2, `ael_20260924-154002`). It also records a comparison of the local reviewer with the Mistral API reviewer on the same task.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Project:** `dev/smoke`, refreshed with `bin/propagate.sh` on 2026-11-05 (engine and governance after change-b8a6c445).
- **Starting code:** `dev/smoke-fixtures/split_defective.py` without its header comment (`tail -n +15`), copied to `src/split.py` before each run. The fixture violates requirements 1, 3 and 4 of the task.
- **Worker:** `mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit` on oMLX in every run.
- **Procedure:** engine reset, then `--mode loop --max-iterations 3`.
- **Tasks:**
  - `task.md`: free text; the worker may write anywhere in the project.
  - `task-scoped.md`: the same text, plus one scope sentence and a YAML block that declares `src/split.py` as the only deliverable. Logged write scope: `src/split.py, tests/, ai/state/`.
- **Configurations:**
  - `ai/config.yaml` (from `config.reference.yaml`): reviewer `Magistral-Small-2509-MLX-8bit` on oMLX.
  - `ai/config-mistral.yaml` (from `config-mistral.reference.yaml`): reviewer `mistral-medium-2604` on the Mistral API, key from the Keychain item `ai-go-mistral`.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Runs

| Run | Task, reviewer | Log | Result |
|---|---|---|---|
| 1 | `task.md`, Magistral | `engine_20261105-095303.LOG` | BLOCKED (stall) after round 6 |
| A | `task-scoped.md`, Magistral | `engine_20261105-112120.LOG` | SHIP in round 2, rc 0 |
| B | `task-scoped.md`, mistral-medium-2604 | `engine_20261105-114104.LOG` | SHIP in round 2, rc 0 |

**Run 1.**
- **Round 1:** the worker edited `src/split.py`; the result was still faulty. The pytest gate failed and the reviewer said REVISE.
- **Round 2:**
  - The worker rewrote the function correctly, then wrote 9 helper scripts in the project root until the 600 s phase cap.
  - The syntax and pytest gates passed and the reviewer said SHIP.
  - The read-evidence SHIP gate then found 9 unread deliverables, the helper scripts, and replaced SHIP with REVISE.
- **Rounds 3 to 6:**
  - The operator continued the run after round 3.
  - The worker wrote nothing, so both gates were skipped.
  - The reviewer's final message repeated the runtime context and the work summary; the engine read it as REVISE.
  - The engine stopped the run after three identical feedbacks.
- **Side effects:**
  - The worker changed the tracked file `run_tests.sh`.
  - Its summary claimed it had added tests to `tests/test_split.py`, which git shows unchanged.

**Runs A and B.**
- **Round 1:**
  - In both runs the worker made the same edit: it added the empty-list case and left the chunk-size logic unchanged.
  - Its summary stated that all requirements were met.
  - The pytest gate failed (8 failed, 31 passed) and the reviewer said REVISE.
- **Round 2:** the worker rewrote the function with a base size and a remainder. The pytest gate passed (39 passed), the reviewer said SHIP, and the engine ended with rc 0.
- **Scope:** no write was refused, no helper file was written, and `tests/test_split.py` was not changed.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Reviewer Comparison

Runs A and B, which differ only in the reviewer.

| Measure | A: Magistral (oMLX) | B: mistral-medium-2604 (API) |
|---|---|---|
| Rounds to SHIP | 2 | 2 |
| Review phase duration, rounds 1 and 2 | 61 s, 34 s | 5 s, 5 s |
| Run duration | 7 min 0 s | 4 min 48 s |
| Round 1 feedback | Correct verdict and requirement; supporting figures wrong ("maximum chunk size (15) and minimum chunk size (10)" for 7 items in 3 chunks) | Correct example (10 items in 3 chunks give sizes 4, 4, 2) and the correct distribution rule |
| Round 2 response | `SHIP` only | A requirement-by-requirement check; its figures (39 tests, two files compiled) match the gate output |

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Observations

- **O-01:** with a free-text task the worker may write anywhere in the project. In run 1 the worker wrote helper scripts it could not execute, and those files became deliverables for the read-evidence SHIP gate. A declared deliverable avoided this in runs A and B. The engine behaved as designed.
- **O-02:** in both scoped runs the worker's round 1 summary claimed requirements that the pytest gate showed as failing. The gate output, not the summary, drove the REVISE.
- **O-03:** in run 1, rounds 3 to 6, Magistral returned its input instead of a verdict. This is the same class of failure as `report-14e05e35-live-verification` OB-01.
- **O-04:** this is one task with one worker model and one run per reviewer. It is not a general comparison of the two reviewers.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Verdict

- The path REVISE → fix → SHIP was observed in runs A and B, with SHIP only after the pytest gate passed.
- The open item in `dev/task.md` ("Validate the REVISE → fix → SHIP convergence path") is complete.
- Runs A and B are further evidence for the operator decision of 2026-11-05 to use `mistral-medium-2604` as reviewer (OB-01).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-05 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
