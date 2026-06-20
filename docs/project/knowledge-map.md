# Knowledge Map

This file routes agents and humans to project knowledge.

It must not become a code index. Do not list every file, class, function, or symbol here.

Docs explain context. Rules enforce constraints. Keep them separate and update this file whenever docs or rules are added, moved, renamed, or deleted.

Rule files may also record rule metadata such as `type`, `confidence`, and `source`. Read those semantics from `AGENTS.md` and the rule files themselves; do not treat every rule entry as equally strong by default.

When `harness.config.yaml` exists, read `knowledge.mode` and `knowledge.maturity` before deciding how much knowledge to load or create.

## Project Overview

- Knowledge Docs:
  - `docs/project/` for repository-wide workflow and routing
  - `docs/project/tier-policy-workflow-design.md` for installed future-facing Tier-policy workflow research boundaries and roadmap context
  - `docs/current/` for current-state knowledge about how the project works today
  - `docs/target/` for desired future design, migration direction, or proposed architecture
- Rule Files:
  - `AGENTS.md`
  - `.aiassistant/rules/*.md`
- Scope:
  - route readers to the smallest relevant set of docs and rules
  - keep current fact separate from target intent
- When To Read:
  - before loading detailed docs for a non-trivial task
  - whenever docs, rules, or file roles change
- Boundary Notes:
  - `docs/current/` is for observed reality first
  - `docs/target/` is for future intent, not current fact
  - label knowledge as fact, inference, or unknown inside detailed docs
  - keep rule-strength metadata in rule files, not in knowledge docs

## Current-State-First Routing

For mixed-responsibility, legacy-heavy, or mudball projects, start with `docs/current/` unless the task is explicitly about future design.

Use this order:

1. read `AGENTS.md` and relevant rules first
2. read `docs/project/knowledge-map.md` to choose the smallest relevant knowledge area
3. read `docs/current/...` for how the project works today
4. read `docs/target/...` only when the task involves planned changes, migration direction, or intentional future-state design

If the current state is unclear, document the uncertainty as an unknown instead of filling the gap with target design.

## Project Workflow Design

- Areas: harness task flow, Tier-based routing, gate boundaries, future workflow configurability
- Tags: workflow, tier, gate-policy, task-state, research
- Docs:
  - Current: `docs/project/harness-workflow.md`
  - Target: `docs/project/tier-policy-workflow-design.md`
- Rules:
  - `AGENTS.md`
- Read When:
  - working on harness execution flow, Tier policy, gate behavior, or future workflow design boundaries
- Boundaries:
  - keep `gatePolicy` semantics unchanged
  - treat Tier policy as classification/workflow-hint logic until a later approved design says otherwise
  - do not treat the design draft as implemented behavior
  - use the design draft to understand deferred hardening and future-engine boundaries, not current execution rules
- Validation:
  - confirm project-neutral language
  - confirm proposed workflow configurability remains design-only unless explicitly implemented in an approved slice

## BookStack Plugin Design

- Areas: Dify Tool plugin structure, BookStack API integration, provider credentials, tool roadmap, future Datasource direction
- Tags: dify-plugin, bookstack, tool-plugin, credentials, api-mapping, datasource-later
- Docs:
  - Current: `docs/current/system-map.md`
  - Architecture: `docs/ARCHITECTURE.md`
  - API Mapping: `docs/API_MAPPING.md`
  - Marketplace: `docs/MARKETPLACE.md`
  - Target: `docs/target/architecture-intent.md`
  - Planning: `docs/ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/ISSUES.md`
- Rules:
  - `AGENTS.md`
  - `.aiassistant/rules/00-repository-rules.md`
  - `.aiassistant/rules/workflow-rules.md`
- Read When:
  - adding or changing BookStack tools
  - changing provider credentials, plugin YAML, icons, or Dify source references
  - changing `BookStackClient`, user-facing error terms, or API response mapping
  - updating roadmap status for planned versus implemented functionality
  - updating Marketplace readiness, packaging, import, or release-checklist guidance
  - designing Datasource behavior after Tool plugin behavior stabilizes
- Boundaries:
  - treat `docs/current/system-map.md` as observed current behavior, not future intent
  - treat `docs/target/architecture-intent.md` as planned direction, not current availability
  - keep credentials in the Dify provider schema and do not hardcode BookStack URLs or secrets
  - keep delete/archive behavior out of scope unless an issue explicitly calls for it
- Validation:
  - tests should mock BookStack HTTP calls when tests exist
  - until tests exist, report validation as `NOT_RUN` with the reason instead of inventing live BookStack checks
  - re-check README and roadmap wording so planned tools are not described as available

## Knowledge Maturity Routing

Use `knowledge.maturity` to scale routing depth and governance expectations:

- **L0**: route only the minimum docs and rules needed for the task; prefer explicit unknowns over broad discovery
- **L1**: prioritize `docs/current/` coverage for entrypoints, major flows, risk zones, and safe-change advice
- **L2**: maintain reusable routing for important areas and load both current and target docs only when they materially affect the task
- **L3**: expect stronger routing discipline, clearer ownership notes, and docs/rules sync when meaning changes
- **L4**: expect high-trust curated routing, stronger confirmed/hard rule usage, and careful separation of current fact vs target intent

Use maturity as a scaling guide, not as a reason to load all docs.

For `knowledge.mode: mudball`:

- default to `docs/current/` first at every maturity level
- keep target docs optional and future-facing
- treat L0-L1 as valid operating levels
- do not assume L3/L4 governance unless the project explicitly chose it

## Knowledge Labels

Detailed docs should distinguish:

- **Fact**: directly observed in code, config, runtime behavior, logs, or confirmed repository docs
- **Inference**: likely interpretation of current behavior that still needs confirmation
- **Unknown**: unresolved question, missing evidence, or area not yet inspected
- **Target**: desired future behavior or design direction; keep this in `docs/target/` unless a current-state doc must reference it for contrast

Do not silently upgrade inference or target guidance into present-day fact.
Do not silently upgrade `observed` or `target` rules into enforceable hard constraints.

## How To Use This File

- Use this file to choose a small set of relevant docs and rules.
- Match the task to one or more knowledge areas by purpose, workflow, ownership, validation needs, or change surface.
- Read only the entries that match the current task.
- Prefer `docs/current/` for real behavior and `docs/target/` for intended future behavior.
- Prefer rule files for constraints, and check rule metadata before treating a rule as a blocker.
- Use repository search or source inspection for file and symbol lookup.
- Do not list the whole repository here.

## Mudball-Friendly Documentation Guidance

For codebases with unclear boundaries or mixed responsibilities:

- document current entrypoints, call paths, risk zones, and safe-change advice before proposing cleanup
- keep related-file notes small and purpose-based, not exhaustive
- prefer facts and unknowns over polished architecture language
- prefer gradual maturity growth over immediate governance escalation
- add target-state docs only when they help explain a proposed improvement or migration path

## Path-Proximity Rule Reminder

When target files are known, agents should also look upward from those paths for local rule files such as:

- `MODULE_RULES.md`
- `AGENTS.md`
- `HARNESS_RULES.md`

Local path rules narrow area-specific behavior, but repository-global safety and boundary rules still take precedence if there is a conflict.
