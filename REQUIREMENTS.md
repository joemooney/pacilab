# paciLab — Requirements

## Scenario Management

- **R-SM-01**: Validate scenario JSON files against v1 schema (id, name, events, expected_action)
- **R-SM-02**: Validate scenario JSON files against v2 schema (topology, ports, egress expectations)
- **R-SM-03**: Normalize and validate scenario objects programmatically via `scenario_lib`
- **R-SM-04**: Import scenarios from directory into central JSON store (merge or replace)
- **R-SM-05**: Export scenarios from central store to individual files
- **R-SM-06**: Validate all scenarios in a directory batch

## Packet Simulation

- **R-PS-01**: Mock mode provides deterministic local filtering (ARP pass, 10.0.1.* pass, others drop)
- **R-PS-02**: Real mode invokes external `pacgate simulate --json` binary
- **R-PS-03**: Convert packet dicts to comma-separated spec strings for pacgate CLI
- **R-PS-04**: Return structured result with status, action, matched_rule, is_default, fields

## Regression Testing

- **R-RT-01**: Load scenario and repeat events cyclically for N iterations
- **R-RT-02**: Count mismatches between expected and actual actions
- **R-RT-03**: Output JSON with statistics (count, mismatches, elapsed_sec, packets_per_sec)
- **R-RT-04**: Return first 50 results in output for debugging
- **R-RT-05**: Exit code 0 on all pass, 1 on mismatch

## Topology Simulation

- **R-TS-01**: Model 2-port L3 switch with RMAC endpoints
- **R-TS-02**: Subnet-based source validation on ingress
- **R-TS-03**: IP-based egress routing decisions
- **R-TS-04**: Track drop reasons: rmac_error, ingress_subnet_mismatch, pacgate_drop, no_route
- **R-TS-05**: Support injected RMAC errors for fault testing
- **R-TS-06**: Output comprehensive statistics and per-event results as JSON

## CI/CD

- **R-CI-01**: GitHub Actions workflow validates schemas and scenarios
- **R-CI-02**: CI runs regression in mock mode (100 iterations)
- **R-CI-03**: CI runs topology simulation in mock mode
- **R-CI-04**: CI runs unit tests
- **R-CI-05**: All CLI tools produce JSON output for automated gating

## Output Formats

- **R-OF-01**: Regression output includes scenario_id, count, mode, mismatches, elapsed_sec, packets_per_sec, results
- **R-OF-02**: Topology output includes scenario_id, mode, mismatch_count, stats (with drop reason breakdown), results
- **R-OF-03**: Validation output supports human-readable and JSON formats
