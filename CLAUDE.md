# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

paciLab is a system-level verification and orchestration companion for pacgate. It provides scenario validation, packet simulation (mock and real modes), topology testing, and CI-friendly JSON output.

### Architecture
- **pacilab/** — Python package with core modules
  - `scenario_lib.py` — Schema validation and normalization (v1/v2)
  - `engine.py` — Packet simulation engine (mock + real pacgate modes)
  - `run_regress.py` — High-volume regression runner
  - `topology.py` — 2-port RMAC/L3 switch topology simulator
  - `validate.py` — CLI scenario validator
  - `sync.py` — Scenario import/export to central store
- **docs/** — JSON schemas (v1, v2) and architecture docs
- **examples/** — Sample scenarios and central store
- **tests/** — Unit tests

### Common Commands
```bash
bash bootstrap.sh && source .venv/bin/activate
make validate          # Validate example scenarios
make sim-regress       # Run regression (1000 packets, mock)
make sim-topology      # Run topology simulation
make test              # Run unit tests
```

### Key Design
- Two execution modes: `mock` (fast/deterministic) and `real` (uses pacgate binary)
- JSON schemas enforce scenario structure (v1=basic, v2=topology-aware)
- CI pipeline validates, simulates, and tests on every push
## Requirements Management

This project uses AIDA for requirements tracking. **Do NOT maintain a separate REQUIREMENTS.md file.**

Requirements database: `requirements.db`

### Database Storage
AIDA supports both YAML and SQLite backends:
- **YAML**: Human-readable, git-friendly, good for single-user scenarios
- **SQLite**: Better for concurrent access (GUI + CLI), optimistic locking

To migrate: `aida db migrate --from yaml --to sqlite`

### CLI Commands
```bash
aida list                              # List all requirements
aida list --status draft               # Filter by status
aida show <ID>                         # Show requirement details (e.g., FR-0042)
aida add --title "..." --description "..." --status draft  # Add new requirement
aida edit <ID> --status completed      # Update status
aida comment add <ID> "..."            # Add implementation note
```

### During Development
- When implementing a feature, update its requirement status
- Add comments to requirements with implementation decisions
- Create child requirements for sub-tasks discovered during implementation
- Link related requirements with: `aida rel add --from <FROM> --to <TO> --type <Parent|Verifies|References>`

### Session Workflow
If you work conversationally without explicit /aida-req calls, use `/aida-capture` at session end to review and capture any requirements that were discussed but not yet added to the database.

## Code Traceability

### Inline Trace Comments
When implementing requirements, add inline trace comments:

```rust
// trace:FR-0042 | ai:claude
fn implement_feature() {
    // Implementation
}
```

Format: `// trace:<SPEC-ID> | ai:<tool>[:<confidence>]`

### Commit Message Format
**Standard format:**
```
[AI:tool] type(scope): description (REQ-ID)
```

**Examples:**
```
[AI:claude] feat(auth): add login validation (FR-0042)
[AI:claude:med] fix(api): handle null response (BUG-0023)
chore(deps): update dependencies
docs: update README
```

**Rules:**
- `[AI:tool]` - Required when commit includes AI-assisted code
- `type` - Required: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- `(scope)` - Optional: component or area affected
- `(REQ-ID)` - Required for feat/fix commits, optional for chore/docs

**Confidence levels:**
- `[AI:claude]` - High confidence (implied, >80% AI-generated)
- `[AI:claude:med]` - Medium (40-80% AI with modifications)
- `[AI:claude:low]` - Low (<40% AI, mostly human)

**Configuration:**
Set `AIDA_COMMIT_STRICT=true` to reject non-conforming commits, or create `.aida/commit-config`.

## Claude Code Skills

This project uses AIDA requirements-driven development:

### /aida-req
Add new requirements with AI evaluation:
- Interactive requirement gathering
- Immediate database storage with draft status
- Background AI evaluation for quality feedback
- Follow-up actions: improve, split, link, accept

### /aida-implement
Implement requirements with traceability:
- Load and display requirement context
- Break down into child requirements as needed
- Update requirements during implementation
- Add inline traceability comments to code

### /aida-capture
Review session and capture missed requirements:
- Scan conversation for discussed features/bugs/ideas
- Identify implemented work not yet in requirements database
- Prompt to add missing requirements or update statuses
- Use at end of conversational sessions as a safety net

