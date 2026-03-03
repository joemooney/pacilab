# paciLab

Scenario validation, regression testing, and topology simulation for pacgate.

## Scope

- Scenario validation (`v1` and `v2` schemas)
- Scenario import/export synchronization
- High-volume regression runner (~600K packets/sec)
- 2-port topology runner (RMAC + L3 switch model)
- CI-friendly JSON outputs and mismatch gating

All functionality is implemented natively in **pacgate** as Rust subcommands.

## Quickstart

Requires `pacgate` binary in PATH (build from [pacgate](https://github.com/joemooney/pacgate)).

```bash
make validate        # Validate example scenarios
make sim-regress     # Run 1000-packet regression
make sim-topology    # Run topology simulation
```

## Project Layout

- `docs/`: JSON schemas (v1, v2) and architecture docs
- `examples/`: sample scenarios and central store
- `.github/workflows/ci.yml`: CI checks

## Commands

```bash
pacgate scenario validate docs/scenario_v2.example.json --json
pacgate scenario validate examples/scenarios/*.json
pacgate regress --scenario examples/scenarios/allow_arp_regression_v1.json --count 1000
pacgate topology --scenario examples/scenarios/rmac2_l3_switch_baseline.json
pacgate scenario import --in-dir examples/scenarios --store store.json
pacgate scenario export --store store.json --out-dir out/
```
