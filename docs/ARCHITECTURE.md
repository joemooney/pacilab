# paciLab Architecture

## Boundaries

- paciLab orchestrates scenarios, topology modeling, and reporting.
- pacgate (external binary) performs packet policy simulation when mode is `real`.

## Pipeline

1. Scenario load + normalize
2. Optional topology context (ports/subnets)
3. Event execution
4. Expected vs actual comparison
5. JSON output for CI gating

## Execution Modes

- `mock`: deterministic local behavior, no external dependency
- `real`: invokes `pacgate simulate --json`
