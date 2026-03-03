# paciLab — Overview

## Vision

paciLab provides scenario definitions, JSON schemas, and examples for **pacgate**'s scenario validation, regression testing, and topology simulation. All runtime functionality is implemented natively in pacgate as Rust subcommands.

## What It Does

1. **Scenario Validation** — Validates JSON scenario files against v1 and v2 schemas
2. **High-Volume Regression** — Exercises thousands of packets with pass/drop verification (~600K pps)
3. **Topology Simulation** — Models 2-port L3 switches with RMAC endpoints, subnet gating, and routing
4. **Scenario Sync** — Import/export scenarios to/from a central store
5. **CI Integration** — JSON output format for automated gating

## Scenario Schemas

- **v1** — Basic packet events with expected pass/drop actions
- **v2** — Extends v1 with topology (ports, subnets, MACs), egress expectations, and RMAC error injection

## Quick Start

Requires `pacgate` binary in PATH.

```bash
make validate        # Validate scenarios
make sim-regress     # Run 1000-packet regression
make sim-topology    # Run topology simulation
```

## Related Projects

- **pacgate** — The packet filtering engine; includes scenario validation, regression, and topology simulation natively
