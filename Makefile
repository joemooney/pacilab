PACGATE_BIN ?= pacgate
REGRESS_COUNT ?= 1000
REGRESS_SCENARIO ?= examples/scenarios/allow_arp_regression_v1.json
TOPOLOGY_SCENARIO ?= examples/scenarios/rmac2_l3_switch_baseline.json

.PHONY: validate sim-regress sim-topology

validate:
	$(PACGATE_BIN) scenario validate docs/scenario_v1.example.json docs/scenario_v2.example.json
	$(PACGATE_BIN) scenario validate examples/scenarios/*.json

sim-regress:
	$(PACGATE_BIN) regress --scenario $(REGRESS_SCENARIO) --count $(REGRESS_COUNT) --json

topology:
	$(PACGATE_BIN) topology --scenario $(TOPOLOGY_SCENARIO) --json

sim-topology: topology
