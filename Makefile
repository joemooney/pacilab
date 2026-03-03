PACGATE_BIN ?= pacgate
SIM_MODE ?= mock
REGRESS_COUNT ?= 1000
REGRESS_SCENARIO ?= examples/scenarios/allow_arp_regression_v1.json
TOPOLOGY_SCENARIO ?= examples/scenarios/rmac2_l3_switch_baseline.json

.PHONY: bootstrap validate sim-regress sim-topology test

bootstrap:
	bash bootstrap.sh

validate:
	python3 -m pacilab.validate docs/scenario_v1.example.json
	python3 -m pacilab.validate docs/scenario_v2.example.json
	python3 -m pacilab.sync validate --in-dir examples/scenarios

sim-regress:
	python3 -m pacilab.run_regress \
		--scenario $(REGRESS_SCENARIO) \
		--count $(REGRESS_COUNT) \
		--mode $(SIM_MODE) \
		--pacgate-bin $(PACGATE_BIN) \
		--output regress_result.json

topology:
	python3 -m pacilab.topology \
		--scenario $(TOPOLOGY_SCENARIO) \
		--mode $(SIM_MODE) \
		--pacgate-bin $(PACGATE_BIN) \
		--output topology_result.json

sim-topology: topology

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
