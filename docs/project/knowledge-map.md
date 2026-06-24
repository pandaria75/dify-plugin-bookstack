# Knowledge Map

This file routes agents and humans to project knowledge.

It must not become a code index. Do not list every file, class, function, or symbol here.

Docs explain context. Rules enforce constraints. Keep them separate and update this file whenever docs or rules are added, moved, renamed, or deleted.

Rule files may also record rule metadata such as `type`, `confidence`, and `source`. Read those semantics from `AGENTS.md` and the rule files themselves; do not treat every rule entry as equally strong by default.

When `harness.config.yaml` exists, read `knowledge.mode` and `knowledge.maturity` before deciding how much knowledge to load or create.

## Project Overview

- Knowledge Docs:
  - `docs/project/` for repository-wide workflow and routing
  - `docs/current/` for current-state knowledge about how the project works today
  - `docs/target/` for desired future design, migration direction, or proposed architecture
  - `docs/user/` for consolidated user-facing setup, usage, and disclosure guidance
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

- Areas: harness task flow, routing, gate boundaries
- Tags: workflow, gate-policy, task-state
- Docs:
  - Current: `docs/project/harness-workflow.md`
- Rules:
  - `AGENTS.md`
- Read When:
  - working on harness execution flow, task routing, or gate behavior
- Boundaries:
  - keep `gatePolicy` semantics unchanged
  - treat harness workflow docs as current process guidance
- Validation:
  - confirm project-neutral language
  - confirm workflow guidance stays aligned with current harness-managed docs

## BookStack Plugin Design

- Areas: Dify Tool plugin structure, BookStack API integration, provider credentials, Tool-first scope, future Datasource direction
- Tags: dify-plugin, bookstack, tool-plugin, credentials, datasource-later
- Docs:
  - Current: `docs/current/system-map.md`
  - User docs: `docs/user/en/usage.md`, `docs/user/zh/usage.md`
  - Target: `docs/target/architecture-intent.md`
- Rules:
  - `AGENTS.md`
  - `.aiassistant/rules/00-repository-rules.md`
  - `.aiassistant/rules/workflow-rules.md`
- Read When:
  - adding or changing BookStack tools
  - changing provider credentials, plugin YAML, icons, or Dify source references
  - changing `BookStackClient`, user-facing error terms, or API response mapping
  - designing Datasource behavior after Tool plugin behavior stabilizes
- Boundaries:
  - treat `docs/current/system-map.md` as observed current behavior, not future intent
  - treat `docs/target/architecture-intent.md` as planned direction, not current availability
  - keep credentials in the Dify provider schema and do not hardcode BookStack URLs or secrets
  - keep delete/archive behavior out of scope unless an issue explicitly calls for it
- Validation:
  - tests should mock BookStack HTTP calls when tests exist
  - until tests exist, report validation as `NOT_RUN` with the reason instead of inventing live BookStack checks
  - re-check README and usage-doc wording so planned tools are not described as available

## Documentation Structure Routing

- Areas: entry docs, user guidance, harness/project routing
- Tags: docs-routing, navigation
- Docs:
  - Entry README: `README.md`
  - Harness/project docs: `docs/project/harness-workflow.md`, `docs/project/knowledge-map.md`
  - Current-state design: `docs/current/system-map.md`
  - Future intent: `docs/target/architecture-intent.md`
  - User docs: `docs/user/en/usage.md`, `docs/user/zh/usage.md`
- Read When:
  - moving or renaming docs
  - updating user-facing setup, usage, or disclosure wording
- Boundaries:
  - keep `README.md` concise and English-only
  - keep Chinese user-facing docs in `docs/user/zh/usage.md`
  - keep Tool-first, Datasource-later positioning
  - keep disclosures and product-status wording synchronized across `README.md`, `docs/user/en/usage.md`, and `docs/user/zh/usage.md`

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
