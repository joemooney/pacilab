# paciLab — Prompt History

## Session 1 — 2026-03-02 — Initial Setup

### Prompt
> Explore this project, and add as a new repo in github. Scaffold with aida.

### Actions Taken
1. Explored pacilab project structure and all source files
2. Initialized local git repo (was previously under parent `/home/joe/ai/` repo)
3. Renamed default branch from `master` to `main`
4. Created GitHub repo: https://github.com/joemooney/pacilab
5. Pushed initial commit with all existing code
6. Registered project with aida (`aida db register`)
7. Applied aida scaffold (`aida scaffold apply`) — generated 19 files:
   - `CLAUDE.md` with project context
   - 8 Claude Code commands (`.claude/commands/`)
   - 9 Claude Code skills (`.claude/skills/`)
   - Git commit-msg hook
8. Updated CLAUDE.md with project-specific architecture and commands
9. Created OVERVIEW.md, REQUIREMENTS.md, PROMPT_HISTORY.md
10. Committed and pushed all scaffolding and documentation

## Session 2 — 2026-03-02 — Migrate pacilab into pacgate as Rust subcommands

### Prompt
> Migrate pacilab's ~700 lines of Python (scenario validation, packet regression, topology simulation) into pacgate as native Rust subcommands, eliminating subprocess overhead and type duplication.

### Actions Taken
1. Added `Ipv4Prefix::contains()` method to `pacgate/src/model.rs` (~15 lines)
2. Created `pacgate/src/scenario.rs` (~600 lines) with:
   - Serde-derived types: `Scenario`, `ScenarioEvent`, `Topology`, `TopologyPort`, `ScenarioStore`, `ExpectedAction`, `SwitchAction`
   - JSON key validation (mirrors Python's strict ALLOWED_*_KEYS checking)
   - Semantic validation (ID regex, non-empty events, topology port uniqueness, tag dedup)
   - `load_scenario()` / `load_scenario_from_str()` — file loading with key + semantic validation
   - `packet_spec_to_sim_packet()` — converts JSON packet specs to `SimPacket` via existing `parse_packet_spec()`
   - `validate_files()` — batch validation with summary output
   - Store operations: `load_store()`, `save_store()`, `import_scenarios()`, `export_scenarios()`
   - `run_regress()` — regression runner calling `simulator::simulate()` directly (~600K pps vs Python subprocess)
   - `run_topology()` — RMAC/L3 switch topology simulation with subnet gating, ingress validation, egress routing
   - 10 unit tests (v1/v2 parsing, bad ID, empty events, unknown keys, packet conversion, IPv4 contains, store roundtrip, tag dedup, port uniqueness)
3. Added CLI wiring to `pacgate/src/main.rs` (~80 lines):
   - `ScenarioAction` enum: `Validate`, `Import`, `Export`
   - `Commands::Scenario`, `Commands::Regress`, `Commands::Topology`
   - Match arms with human-readable + `--json` output, exit code 1 on mismatches
4. All 277 tests pass (267 existing + 10 new scenario tests)
5. Verified CLI parity:
   - `pacgate scenario validate` — matches Python `validate.py` output format
   - `pacgate regress` — matches Python `run_regress.py` JSON output
   - `pacgate topology` — matches Python `topology.py` JSON output
6. Updated pacgate `CLAUDE.md` and `OVERVIEW.md` with new commands
7. Updated pacilab `PROMPT_HISTORY.md`
8. Committed and pushed to both repos

### Key Design Decisions
- **No mock mode**: Python's mock mode (hardcoded ARP/subnet rules) was only needed because pacilab couldn't link to pacgate's simulator. With direct `simulate()` calls, all tests exercise real rule matching logic.
- **Direct function calls**: `simulator::simulate()` and `simulator::simulate_stateful()` called directly instead of subprocess `pacgate simulate --json`. Performance improvement: ~600K pps vs ~1K pps (subprocess overhead).
- **Strict key validation**: Raw JSON keys checked against allowed sets before serde deserialization, matching Python's unknown-key rejection behavior.
- **Output compatibility**: JSON output formats match pacilab's Python output exactly for CI/scripting continuity.
