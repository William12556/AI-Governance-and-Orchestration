# Task

Implement `split_into_chunks(items, n)` in `src/split.py`.

## Requirements

1. Return a list of exactly `n` lists.
2. Every element of `items` appears exactly once across the returned chunks, preserving original order.
3. Chunk sizes differ by at most 1.
4. Assume `n >= 1`. An empty `items` list returns `n` empty lists.

## Verification

Tests are in `tests/test_split.py` and must pass.

Do not modify `tests/test_split.py`.

## Scope

Write only `src/split.py`. You have no tool to run the tests; the engine runs them after your work phase.

```yaml
prompt_info:
  id: "smoke-scoped"
  title: "dev/smoke task with a declared deliverable"
deliverable:
  files:
    - path: "src/split.py"
```
