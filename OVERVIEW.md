# paciLab — Overview

## Vision

paciLab is the system-level verification and orchestration companion for **pacgate**, a packet filtering/policy engine. It enables teams to validate, simulate, and regression-test packet filtering scenarios across mock and real execution paths, with CI-friendly output.

## What It Does

1. **Scenario Validation** — Validates JSON scenario files against v1 and v2 schemas
2. **Packet Simulation** — Runs events through mock or real pacgate engines
3. **High-Volume Regression** — Exercises thousands of packets with pass/drop verification
4. **Topology Simulation** — Models 2-port L3 switches with RMAC endpoints, subnet gating, and routing
5. **Scenario Sync** — Import/export scenarios to/from a central store
6. **CI Integration** — JSON output format for automated gating

## Architecture

```
pacilab/
├── scenario_lib.py    # Core validation and normalization
├── engine.py          # Simulation engine (mock + real)
├── run_regress.py     # Regression runner CLI
├── topology.py        # Topology simulator CLI
├── validate.py        # Scenario validator CLI
└── sync.py            # Scenario store import/export CLI
```

### Execution Modes

- **Mock** — Deterministic local logic (ARP→pass, 10.0.1.*→pass, else→drop). No external binary required.
- **Real** — Invokes `pacgate simulate --json` with actual rules files.

### Scenario Schemas

- **v1** — Basic packet events with expected pass/drop actions
- **v2** — Extends v1 with topology (ports, subnets, MACs), egress expectations, and RMAC error injection

## Technology

- Python 3.12+
- jsonschema for schema validation
- Optional: pacgate binary for real mode
- GitHub Actions CI pipeline

## Quick Start

```bash
bash bootstrap.sh && source .venv/bin/activate
make validate        # Validate scenarios
make sim-regress     # Run 1000-packet regression
make sim-topology    # Run topology simulation
make test            # Unit tests
```

## Migration Status

paciLab's functionality has been migrated into pacgate as native Rust subcommands (`pacgate scenario`, `pacgate regress`, `pacgate topology`). The Rust implementation calls `simulate()` directly instead of shelling out, achieving ~600x speedup (~600K pps vs ~1K pps). The Python code in this repo remains as a reference but is superseded by the pacgate implementation.

## Related Projects

- **pacgate** — The packet filtering engine that paciLab validates against (now includes pacilab functionality natively)
