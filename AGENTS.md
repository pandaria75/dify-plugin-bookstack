# Project Agent Guide

<!-- marionettist-kit:start -->

## Purpose

This file is the primary repository-agent instruction entrypoint for this project.

Use it to understand:
- repository-level execution strategy
- where constraints and knowledge live
- how to route knowledge lookup for the task at hand
- documentation and review expectations

Keep this file concise. Detailed constraints belong in `.aiassistant/rules`.
Project knowledge and architecture explanations belong in `docs`.

## Constraint Sources

1. `AGENTS.md`
2. `.aiassistant/rules/*.md`

If constraints conflict, this file takes precedence unless the user explicitly overrides it.

Rule files may include metadata such as `type`, `confidence`, and `source`.
Use that metadata to decide enforcement strength:
- `hard`: enforce by default
- `confirmed`: follow as an active repository convention unless higher-priority instructions or newer evidence override it
- `observed`: treat as current-state evidence, not a default hard blocker
- `target`: treat as intended future direction, not current required behavior unless the approved task is implementing it

Do not silently upgrade `observed` or `target` rules into stronger constraints.

## Knowledge Sources

- `docs/**/*.md` contains project knowledge, architecture explanations, workflow notes, and boundary context.
- `docs/project/knowledge-map.md` routes agents to relevant project knowledge.
- `marionettist.config.yaml` may define `knowledge.mode` and `knowledge.maturity` for local documentation posture.

Do not treat knowledge sources as stronger than constraint sources.

## Knowledge Routing

Docs are read on demand. Do not load all docs by default.

Use `docs/project/knowledge-map.md` as a routing guide, not as a code index or a reason to load all docs.

When `marionettist.config.yaml` exists, read `knowledge.mode` and `knowledge.maturity` early and scale documentation depth, routing strictness, and governance expectations accordingly.

Knowledge maturity guidance:

- **L0**: minimal capture; rely on task-local context and explicit unknowns
- **L1**: current-state mapping first; good default for messy or legacy-heavy projects
- **L2**: reusable area knowledge with stable routing and meaningful docs updates when design understanding changes
- **L3**: governed knowledge with stronger docs/rules sync and clearer ownership expectations
- **L4**: strict governance with curated high-trust knowledge and stronger validation expectations for sensitive changes

Mudball guidance:

- in `knowledge.mode: mudball`, start from `docs/current/` and observed behavior first
- do not treat target docs as evidence of current behavior
- do not push L3/L4 governance by default; L0-L1 may be appropriate steady states and L2 is a gradual improvement point

Use `module-inspector` when the task involves:
- modifying a module, package, feature area, or bounded subsystem
- cross-module or cross-area changes
- unfamiliar ownership or dependency direction
- boundary or modifiability decisions

For module-level work, start from `docs/project/knowledge-map.md`, then read only the relevant docs and rules.

If target files are already known, also check for nearby `MODULE_RULES.md`, `AGENTS.md`, and `HARNESS_RULES.md` by walking upward from those paths.
If a local path rule conflicts with repository-global safety or boundary rules, follow the global rules.

Use `workflow-inspector` when the task involves:
- process or workflow design
- orchestration or state transitions
- event-driven or asynchronous behavior
- call-chain analysis
- frontend-backend or service integration flow

For workflow-level work, identify the entrypoint first, then read only the docs and rules relevant to the involved flow.

If the target area or flow is unclear, state the uncertainty and inspect the smallest relevant project structure before loading more docs.

## Code Lookup Policy

Docs must not be used as a code index.

Use available IDE tools, MCP tools, local search, or direct source inspection for:
- file lookup
- symbol lookup
- call-site lookup
- class or function inventories
- implementation details

## Task Entry Policy

Use `task-intake` as the default entrypoint for non-trivial repository tasks. Use it to classify the task into one of the following tiers:

When `.marionettist/tier-policy.yml` exists, use it as project-local guidance for Tier descriptions, match-rule language, workflow hints, review hints, and model-profile hints. Keep the executable workflow and all gate behavior anchored to `docs/project/marionettist-workflow.md` and `marionettist.config.yaml` `gatePolicy`.

- **Tier S (Minor)**: Extremely limited scope such as a typo, comment tweak, or one-file low-risk fix.
  - *Flow*: Skip `.task/` documents and analysis skills. Proceed directly to coding, followed by review.
- **Tier M (Standard)**: Small features, bugfixes, refactors, or documentation tasks with clear scope but more than trivial risk.
  - *Flow*: Analysis plus task-scoped `.task/<task-id>/context-pack.md`. `requirement-freezer` is optional and only used when behavior or business rules are unclear.
- **Tier L (Complex)**: Large features, sensitive refactors, multi-module work, workflow-sensitive changes, or tasks with boundary ambiguity.
  - *Flow*: Full Marionettist flow (intake -> freezer when needed -> inspection -> slicer -> context-pack).

Use `task-intake` when:
- a new feature starts
- a bugfix starts
- a refactor starts
- an investigation starts
- a documentation task starts
- the task type or scope is unclear
- the user provides only natural-language requirements
- the Marionettist flow has not started yet for the current task
- the user does not already provide a current approved slice or task artifact

Skip `task-intake` when:
- the user already provides a requirement document
- the user already provides an implementation plan
- the user already provides `.task/active.json` and task-scoped `.task/<task-id>/context-pack.md`
- the current task is already in progress and continuing an existing slice
- the task is trivial and low-risk
- the user explicitly instructs the agent to use another skill

After `task-intake`, route by task type:
- feature -> requirement-freezer when needed -> module/workflow inspection when needed -> implementation-slicer -> context-pack-builder -> coding -> boundary-reviewer
- bugfix -> module/workflow inspection when needed -> context-pack-builder -> coding -> boundary-reviewer
- refactor -> module/workflow inspection -> implementation-slicer -> context-pack-builder -> coding -> boundary-reviewer
- documentation -> workspace-knowledge-manager or direct docs update flow

## Marionettist Workflow

Read `docs/project/marionettist-workflow.md` for the detailed workflow.

For non-trivial work, the default Marionettist flow is:
1. analysis: classify the task, inspect knowledge when needed, freeze requirements when needed, slice the work when needed, and create or update `.task/<task-id>/context-pack.md`
2. slice execution: implement only the current approved slice or approved parallel group, then automatically review that same slice or group
3. finalization: report validation status, remaining risks, and any required knowledge or rules sync

When `marionettist.config.yaml` defines `gatePolicy`, use it as the local default gate posture:
- `strict`: stop at the analysis-to-coding gate and after every approved coding slice or approved parallel group
- `balanced`: preserve the analysis gate and final approval by default; allow continuation only for already-approved slices whose frozen `gateClass` and supplemental `risk_score` do not require a stronger stop, and only when the approved plan and current policy explicitly permit that continuation
- `autonomous`: preserve the analysis gate and final approval by default; allow continuation only for already-approved next slices or approved parallel groups whose frozen `gateClass` is `simple` or `standard`, whose supplemental `risk_score` is `3` or lower, and for which no mandatory stop applies; still stop mid-task for `gateClass: high-risk`, `gateClass: boundary-sensitive`, critic-required, explicit gates or stop conditions, protected-area or dangerous-command work, or any slice whose supplemental `risk_score` requires a stronger pause than `gateClass` alone

Template default is `gatePolicy.defaultMode: balanced` for general usability, but Tier L or otherwise high-risk work should recommend `strict` unless the user explicitly chooses a different policy.

When task-local artifacts record `gatePolicy.selected`, that selected mode wins for the current task over `gatePolicy.defaultMode`. Treat `defaultMode` as fallback posture only when no task-local selection exists. Treat `recommended` values from tier hints or task artifacts as advisory only; they must not override an explicit selected mode.

If `.marionettist/tier-policy.yml` provides `gateHint`, treat it as advisory classification context only. It must not replace `gatePolicy.defaultMode`, the selected task-local gate mode, or any required human-confirmation stop.

If `.marionettist/tier-policy.yml` provides `modelProfileHint`, resolve it through existing profile roles or names from `.marionettist/model-profiles.yml`. Do not treat Tier policy as a place to embed raw provider or model identifiers.

For the current MVP, treat `modelProfileHint` as an advisory profile reference with a documented authoring constraint. Full automatic cross-validation against `.marionettist/model-profiles.yml` is deferred future hardening.

If a user asks to change Tier policy in natural language, route that through the normal builder/config workflow as candidate authoring: draft candidate `.marionettist/tier-policy.yml`, show a diff against the current file or framework defaults, surface any available conflict/override explanation, and require explicit confirmation before writing.

If Tier-policy fields use unknown or unsupported ordered-field values, explain the uncertainty conservatively and keep safer workflow behavior. Stricter rejection for those cases is deferred future hardening, not current MVP behavior.

If `gatePolicy.allowTaskOverride` is true, task-local artifacts may select a different mode than `gatePolicy.defaultMode` for that task; when they do, `gatePolicy.selected` becomes the active mode for that task. This changes the task's default posture, not the higher-priority requirement for explicit user confirmation where this workflow already requires it.

For this workflow, the `gateClass` vocabulary is intentionally frozen to `simple`, `standard`, `boundary-sensitive`, and `high-risk`.

`risk_score` is supplemental per-slice gate metadata with an integer range from `1` to `5`. It does not replace `gateClass`, does not invent new gate classes, and may only preserve or strengthen required pauses relative to `gateClass`, critic requirements, explicit gate reasons, and explicit stop conditions.

Treat these as common higher-risk inputs when assigning or explaining `risk_score`: database schema updates, permissions or security logic, device communication, scheduling, public APIs, build scripts, code deletion, dependency upgrades, and production configuration.

The agent may continue through small steps inside the analysis phase without pausing after each one.
For bug fixes, the analysis phase is complete once a failing test case or clear reproduction steps are confirmed.
After the analysis phase is complete, the agent must stop and wait for explicit user confirmation before entering coding, except for Tier S.
During slice execution, the agent may proceed directly from coding into review for the same approved slice or group without a separate user confirmation.
If review fails for the current slice or group, the agent may plan and apply the smallest slice-local fix and re-run review up to 3 total review attempts before pausing for user decision.
After each implementation-plan slice or approved parallel group passes review or exhausts the allowed retry attempts, the agent must stop and wait for explicit user confirmation before starting the next slice or group, unless the selected gate policy explicitly allows continuation for the next already-approved slice or group and no mandatory stop applies.
Having task-scoped `.task/<task-id>/context-pack.md` means the agent may skip repeated intake or analysis work when appropriate; it does not authorize automatic entry into coding.

## Marionettist Gates

For all non-trivial tasks, repository Marionettist gates are mandatory.

The agent MUST NOT cross these gates without explicit user confirmation:
- after analysis is complete, before coding starts
- after each coding slice or approved parallel group has completed coding and review, before the next slice or group starts, unless the selected gate policy explicitly allows continuation for the next already-approved slice and that slice's frozen `gateClass`, supplemental `risk_score`, critic requirements, and explicit gate reasons do not require a stronger pause

By default, final approval remains required even when the selected gate policy is `balanced` or `autonomous`.

For continuation decisions, apply policy precedence in this order:
1. explicit user instruction and task-local `gatePolicy.selected` for the current task
2. repository `gatePolicy.defaultMode` as fallback when no task-local selection exists
3. `recommended` values from tier hints or task artifacts as advisory context only

Under selected `autonomous`, the agent may continue to the next already-approved slice or approved parallel group without extra slice confirmation only when all of the following are true:
- the next approved work has frozen `gateClass: simple` or `gateClass: standard`
- the next approved work has `risk_score <= 3`
- no critic is required for that next approved work
- no explicit gate reason, stop condition, protected-area decision, or dangerous command requires a pause
- the analysis-to-coding gate has already been crossed with explicit approval

Selected `autonomous` never removes mandatory stops for the analysis-to-coding gate, final approval when required, `gateClass: boundary-sensitive`, `gateClass: high-risk`, critic-required work, explicit gates or stop conditions, protected-area or dangerous-command decisions, or any approved work with `risk_score >= 4`.

At every Marionettist gate, the agent must stop and report:
- current phase
- completed work
- files created or changed
- validation status
- recommended next step
- `User confirmation required to continue.`

When the completed work is a parallel group, the gate report must also include the group name, member slices, execution mode used, fallback order if used, shared files, and merge owner.

Creating task documents or `.task/<task-id>/context-pack.md` does not authorize coding.

Treat a task as trivial only when it is a single low-risk change with clear scope, no boundary ambiguity, no workflow impact, and no need for task documents. If any of those conditions is not clearly true, treat the task as non-trivial.

Do not treat `gatePolicy` as permission to skip required human decisions for protected-area changes, compatibility breaks, unclear requirements, or other explicit stop conditions.

## Parallel Slice Compatibility

For complex non-trivial tasks, an implementation plan may declare `parallel-capable` slices or parallel slice groups when the work is independent and file scopes do not conflict.

Parallel execution is optional and capability-dependent:
- agents that support subagents or safe parallel task execution may run approved `parallel-capable` work concurrently
- agents that do not support subagents, or cannot safely coordinate parallel execution, must execute the same work sequentially in declared dependency order
- `parallel-capable` never means parallel-required

Use parallel-capable planning only for complex tasks. Simple or low-risk tasks should remain sequential.

The primary agent remains responsible for:
- enforcing `AGENTS.md` and `.aiassistant/rules`
- merging results from parallel work when used
- resolving file or behavior conflicts
- running validation
- producing Marionettist gate reports

## Task Context Policy

For non-trivial implementation tasks, create or update `.task/<task-id>/context-pack.md` before coding. Here `<task-id>` means the active task selected by `.task/active.json`. The context pack should stay compact and reference requirement or implementation documents instead of duplicating them when possible.

The full task state contract is defined in `docs/project/marionettist-workflow.md`.

The current task is selected by `.task/active.json`. A non-trivial task should use this structure:
- `.task/active.json`
- `.task/<task-id>/requirement.md`
- `.task/<task-id>/implementation-plan.md`
- `.task/<task-id>/context-pack.md`
- `.task/<task-id>/state.json`

`.task/active.json` is a local repository-root or worktree singleton pointer. Use it to identify the current task in the local checkout, not as implicit cross-worktree delegation context.

Generated requirement and implementation plan documents belong under the current task directory.

The context pack should include:
- task goal
- requirement source
- implementation source
- involved modules or knowledge areas
- loaded rules
- loaded docs
- allowed modification scope
- forbidden modification scope
- key existing entrypoints when relevant
- current approved slice or approved parallel group
- execution mode
- validation commands
- assumptions
- risks
- stop conditions

When delegating across parallel flows or multiple worktrees, the primary agent should preflight context once and pass explicit delegation context such as `worktreeRoot`, `taskId`, `phase`, `allowedToCode`, the current approved slice or group, and `artifactPaths`. Delegated agents should use bounded reads against those provided artifacts, return `CONTEXT_UNAVAILABLE` for missing, stale, inaccessible, or ambiguous context, and stop after bounded empty or cancelled delegation outcomes instead of looping. This is a delegation-safety boundary, not full runtime git-worktree scheduling support.

## Implementation Policy

- Do not implement broad changes directly from conversation history.
- Do not start coding until the user explicitly confirms moving from analysis to coding.
- Implement from one of:
  - `.task/<task-id>/requirement.md`
  - `.task/<task-id>/implementation-plan.md`
  - `.task/<task-id>/context-pack.md`
- Prefer small slices.
- Implement only the currently approved slice or parallel group.
- Do not expand task scope.
- Confirm relevant boundaries before changing architecture-sensitive code.
- Match existing naming, layout, and local patterns.
- Legacy `.task/context-pack.md` may be read only as a migration fallback. If used, warn the user and recommend moving the context pack into the active task directory.

## Review Policy

- For the current approved slice or group, review starts automatically after implementation and does not require a separate user confirmation.
- Do not start review for unrelated scope or the next slice until that slice is explicitly approved.
- After implementation, check the actual diff against allowed and forbidden scope.
- Check boundary violations.
- Check rule conflicts, including incorrect treatment of `observed` or `target` rules as if they were automatically `hard`.
- Check missing validation.
- Check whether docs, rules, or `knowledge-map.md` need sync.

## Documentation Policy

Project docs should explain software design and architecture:
- responsibilities
- functional behavior
- workflows
- domain concepts
- extension points
- boundaries and risks

Project docs should not list every source file, class, function, or implementation detail.

Rules should define behavioral constraints, not general design explanation.
When rule files use metadata, treat only `hard` and normally `confirmed` rules as default enforcement constraints.
Use `observed` rules for current-state caution and `target` rules for future direction unless the approved work says otherwise.

Scale documentation expectations by `knowledge.maturity`:

- `L0-L1`: keep docs compact and current-state-oriented; explicit unknowns are acceptable
- `L2`: keep important routing and area knowledge maintained when meaning changes
- `L3-L4`: keep docs, rules, and validation evidence more tightly synchronized for boundary-sensitive work

Do not use maturity as a reason to turn docs into source-code indexes.

## Project Knowledge

Use `docs/project/marionettist-workflow.md` as the task-process reference.
Use `docs/project/knowledge-map.md` as the routing reference for docs and rules.

Docs explain context; rules define constraints with possible strength metadata.
Read detailed docs only on demand through `module-inspector`, `workflow-inspector`, or `workspace-knowledge-manager` when appropriate.
When adding, moving, renaming, or deleting docs or rules, update `docs/project/knowledge-map.md`.

## Marionettist Sync Policy

Framework-managed sections may be updated by `marionettist sync`.

Project-local docs, rules, skills, and task files must be preserved unless the user explicitly requests replacement.

<!-- marionettist-kit:end -->

<!-- project-local:start -->

Add project-specific agent instructions here.

<!-- project-local:end -->

<!-- project-local-imported:start -->

## Repository Shape

- This repo is an early-stage Dify Tool plugin for BookStack, not a finished product.
- The current code includes the plugin skeleton, shared `BookStackClient`, provider validation, and `validate_credentials`; the other Phase 1 tools are planned only.
- Keep planned functionality marked as planned in docs and README files; do not describe unfinished tools as available.

## Dify Plugin Rules

- Use the current Dify plugin layout in this repo: `manifest.yaml`, `provider/bookstack.yaml`, `provider/bookstack.py`, `tools/*.yaml`, `tools/*.py`, `_assets/`.
- Use repository-relative paths for plugin YAML references and `extra.python.source` values, such as `provider/bookstack.yaml`, `tools/validate_credentials.yaml`, `provider/bookstack.py`, and `tools/validate_credentials.py`; `dify_plugin` 0.9.x loads these paths from the plugin source directory.
- Use `_assets/icon.svg` in `manifest.yaml`; keep provider YAML icon references aligned with the current Dify provider schema, such as `icon.svg` in `provider/bookstack.yaml`.
- Keep credentials in Dify provider schema only: `base_url`, `token_id`, `token_secret`, plus optional defaults.
- Do not hardcode BookStack URLs, tokens, or secrets in code, docs examples, or tests.
- Keep `README.md` English-only; put Chinese user-facing text in `docs/user/zh/usage.md`.
- Preserve the current plugin focus: Tool first, Datasource later.

## BookStack Integration Rules

- `BookStackClient` is the shared HTTP wrapper; put base URL normalization, `/api` prefixing, auth header, timeout, SSL, and error mapping there.
- Treat these errors as user-facing contract terms: `Invalid credentials`, `Permission denied`, `Book not found`, `Chapter not found`, `Shelf not found`, `Page not found`, `BookStack API unavailable`, `Invalid BookStack response`.
- Never log `token_secret` or echo raw authorization headers.
- Tests should mock BookStack HTTP calls; do not require a live BookStack instance unless explicitly requested.
- Until tests exist, report validation as `NOT_RUN` with the reason instead of inventing live BookStack checks.

## Docs and Planning

- Keep product status, planned-vs-available scope, and setup guidance aligned across `README.md`, `docs/user/en/usage.md`, and `docs/user/zh/usage.md`.
- Keep version-sensitive Dify or BookStack behavior notes in the active user/developer docs that describe that behavior; do not leave stale references to removed planning-note files.
- If a change affects Marketplace, privacy, or disclosure expectations, keep the relevant statements synchronized across `README.md` and the usage docs.

## Working Style

- Prefer the smallest correct change.
- When adding a new tool, implement the YAML contract first, then the Python source, then tests.
- Do not add delete/archive behavior unless the issue explicitly calls for it.

## Issue Reporting

- When a task is driven by a GitHub issue, add a comment to that issue upon completion.
- The comment should include: completion status, summary of changes made, and any follow-up notes if relevant.
- Use `gh issue comment` to post the update.

<!-- project-local-imported:end -->
