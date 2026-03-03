# paciLab

paciLab is a standalone system-level verification and orchestration companion for pacgate.

## Scope

- Scenario validation (`v1` and `v2` schemas)
- Scenario import/export synchronization
- High-volume regression runner
- 2-port topology runner (RMAC + switch software model)
- CI-friendly JSON outputs and mismatch gating

## Quickstart

```bash
cd /home/joe/ai/pacilab
bash bootstrap.sh
source .venv/bin/activate
make validate
make sim-regress
make sim-topology
```

The default Make flow uses `mock` mode (no external binary required).

To use a real pacgate binary:

```bash
make sim-regress SIM_MODE=real PACGATE_BIN=/path/to/pacgate
make sim-topology SIM_MODE=real PACGATE_BIN=/path/to/pacgate
```

## Project Layout

- `bootstrap.sh`: create local virtualenv and install developer deps
- `requirements-dev.txt`: optional developer Python dependencies
- `pacilab/`: Python package and CLI modules
- `docs/`: schemas and architecture docs
- `examples/`: sample scenarios and outputs
- `tests/`: lightweight unit tests
- `.github/workflows/ci.yml`: basic CI checks

## Commands

```bash
python3 -m pacilab.validate docs/scenario_v2.example.json --json
python3 -m pacilab.sync validate --in-dir examples/scenarios
python3 -m pacilab.run_regress --scenario examples/scenarios/allow_arp_regression_v1.json --count 100
python3 -m pacilab.topology --scenario examples/scenarios/rmac2_l3_switch_baseline.json --mode mock
```
