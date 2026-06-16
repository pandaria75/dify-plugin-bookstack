# Harness Workflow

This project uses a lightweight file-based harness so requirements, knowledge routing, implementation slices, and execution context stay visible in normal repository files. The goal is to keep repository-agent work reproducible without adding a separate workflow system.

When `harness.config.yaml` exists, read `knowledge.mode` and `knowledge.maturity` before deciding how much documentation, governance, and validation ceremony to apply.

## Standard Task Flow

This project uses a branched harness workflow based on task complexity:

1. **Tier S (Minor)**: Skip `.task/` documents and gates. Direct coding and review.
2. **Tier M (Standard)**: Analysis plus task-scoped `.task/<task-id>/context-pack.md` before coding. `requirement-freezer` is optional and only used when behavior or business rules are unclear.
3. **Tier L (Complex)**: Full mandatory harness with analysis, approved slice execution, automatic slice review, and finalization.

For Tier M and L, the agent must complete phases in order and must not automatically cross analysis or inter-slice gates.

Critic defaults by tier are:
- **Tier S**: no critic by default
- **Tier M**: critic optional, but recommended for risky or boundary-sensitive work
- **Tier L**: critic required before coding and before declaring approved work done

Treat a task as high-risk when it includes sensitive refactors, workflow-sensitive changes, boundary ambiguity, unusual validation uncertainty, or explicit high-risk wording in the task artifacts.

In this file, `<task-id>` means the active `taskId` value from `.task/active.json`.

## Gate Policy Defaults

When `harness.config.yaml` defines `gatePolicy`, it sets the repository default gate posture for non-trivial work:

```yaml
gatePolicy:
  defaultMode: "balanced" # strict | balanced | autonomous
  finalApprovalRequired: true
  allowTaskOverride: true
```

Mode semantics:

- `strict`: stop at the analysis-to-coding gate and after every approved coding slice or approved parallel group.
- `balanced`: preserve the analysis gate and final approval by default; allow continuation only for already-approved slices whose frozen `gateClass` and supplemental `risk_score` do not require a stronger stop, and only when the approved plan and selected policy explicitly permit that continuation.
- `autonomous`: preserve the analysis gate and final approval by default; stop mid-task for `gateClass: high-risk`, `gateClass: boundary-sensitive`, critic-required, explicitly requested gates, or any slice whose supplemental `risk_score` requires a stronger pause than `gateClass` alone.

`allowTaskOverride: true` means task-local artifacts may choose a different gate mode than `defaultMode` for that task. It does not let task-local artifacts bypass higher-priority user instructions, required analysis gates, required final approval, or any other explicit stop condition in this workflow.

Selecting a task-local override is a policy choice for that task, not a bypass of required gates. A task may become more or less interruption-tolerant within the allowed workflow, but it must still stop wherever this workflow or the user explicitly requires a stop.

Template default is `balanced` for general target-project usability. Tier L or otherwise high-risk tasks should recommend `strict` unless the user explicitly chooses a different policy.

`gatePolicy` does not replace normal stop conditions. Human confirmation is still required for protected-area changes, requirement ambiguity, compatibility tradeoffs, or any other explicitly blocked decision.

## Gate Class Vocabulary

For this workflow, `gateClass` is a non-replaced hint vocabulary frozen to:

- `simple`
- `standard`
- `boundary-sensitive`
- `high-risk`

`risk_score` is supplemental per-slice gate metadata with an integer range from `1` to `5`:

- `1`: very low additional risk signal
- `2`: low additional risk signal
- `3`: moderate additional risk signal
- `4`: elevated additional risk signal
- `5`: highest additional risk signal

`risk_score` does not replace `gateClass`, invent new gate classes, or weaken any pause that `gateClass`, critic requirements, or explicit gate reasons already require.

Use `risk_score` only to preserve or strengthen the safer pause behavior relative to `gateClass`. If the numeric score indicates higher risk than `gateClass` alone, agents must keep the stricter stop.

Treat these as common higher-risk inputs when assigning or explaining `risk_score`:

- database schema updates
- permissions or security logic
- device communication
- scheduling
- public APIs
- build scripts
- code deletion
- dependency upgrades
- production configuration

In `balanced` mode, continuation remains limited to already-approved slices whose frozen `gateClass` and supplemental `risk_score` both support continuation, and only when no explicit gate reason or task instruction requires a pause.

## Tier Policy And Future Workflow Configuration

Tier policy is intended to guide task classification and workflow hints. It must not replace this workflow definition, change mandatory gate behavior, or redefine `gatePolicy` semantics.

If the project later adopts configurable Tier policy, treat the executable flow in this document as the MVP source of truth unless a future approved design explicitly introduces a broader workflow engine. For the deferred-design boundary of that future work, see `docs/project/tier-policy-workflow-design.md`.

When `.harness/tier-policy.yml` exists, use it as the project-local source for Tier descriptions, match-rule text, workflow hints, review hints, and model-profile hints during task intake.

The installed `.harness/tier-policy.yml` file is a safe managed starting point:

- `harness init` may install it as framework-managed project scaffolding
- `harness diff` and `harness sync` must preserve project-local edits instead of silently overwriting them
- task intake should explain whether it is using the project-local file, framework defaults, or a safe fallback after parse/validation problems

Precedence for the MVP is:

1. this workflow document and `gatePolicy` remain the source of executable gate behavior
2. built-in framework Tier defaults apply when `.harness/tier-policy.yml` is missing
3. project-local `.harness/tier-policy.yml` may refine Tier classification and hint text within the fixed Tier `S` / `M` / `L` vocabulary
4. refinements may be auto-accepted with explanation, explicit overrides should be marked clearly, and unsafe downgrades must fall back to safer framework defaults instead of silently relaxing them

In `.harness/tier-policy.yml`, `tiers.<tier>.gateHint` is advisory only. It may suggest labels such as `default` or `prefer-strict`, but it does not replace `gatePolicy.defaultMode`, does not change the selected task-local gate mode, and does not bypass any required stop in this workflow.

In `.harness/tier-policy.yml`, `tiers.<tier>.modelProfileHint` must reference an existing profile role or name from `.harness/model-profiles.yml`. It must not embed provider IDs or model IDs directly.

For the current MVP, this is a documented authoring constraint and advisory hint. Automatic cross-validation of `modelProfileHint` against `.harness/model-profiles.yml` is deferred future hardening, so agents should explain uncertainty instead of inventing or silently accepting raw provider/model IDs.

Current schema boundary for `.harness/tier-policy.yml`:

- root keys: `schemaVersion`, `tiers`
- required tier entries: `S`, `M`, `L`
- required fields inside each tier: `description`, `matchRules`, `workflowHint`, `gateHint`, `reviewLevel`, `modelProfileHint`
- optional fields inside each tier: `minTier`, `maxTier`
- allowed scalar values for `minTier` and `maxTier`: `S`, `M`, `L`, or `null`
- `matchRules` is a list of plain strings only

Do not use anchors, merge keys, inline objects, or multi-document YAML in this file for the current MVP.

Unknown or unsupported ordered-field values should be treated conservatively and explained clearly. Stricter automatic rejection behavior for those cases is deferred future hardening rather than part of the current MVP contract.

### Implemented MVP Vs Deferred Hardening

Implemented now:

- managed install path at `.harness/tier-policy.yml`
- framework defaults when the project-local file is missing
- parse/validation feedback with safe fallback where needed
- advisory hints for `workflowHint`, `gateHint`, `reviewLevel`, and `modelProfileHint`
- conflict handling that distinguishes refinement, explicit override, soft conflict, and unsafe downgrade
- natural-language candidate authoring with diff-before-write and explicit confirmation before persistence

Deferred future hardening:

- automatic cross-validation that every `modelProfileHint` resolves in `.harness/model-profiles.yml`
- stricter handling for unknown ordered-field values beyond the current conservative explanation/fallback posture
- any configurable workflow-DAG or broader workflow-engine behavior

### Natural-Language Tier Policy Editing

Projects may ask the builder/config workflow to update `.harness/tier-policy.yml` from natural-language instructions.

For this MVP, the safe authoring flow is:

1. interpret the user's prose as a candidate Tier-policy change
2. draft candidate YAML in the current schema only
3. compare the candidate against the current `.harness/tier-policy.yml`, or against framework defaults when the file does not exist yet
4. show the candidate YAML and a diff before any write
5. surface any already-available Tier-policy explanation, refinement, override, or conflict notes
6. require explicit user confirmation before persisting the candidate

The agent must not silently write Tier-policy changes from prose alone. If the user requests revisions, update the candidate and show the revised diff again before persistence.

### Analysis Phase

The agent may perform any of the following as needed:
- use `task-intake` to classify the task and identify the next harness step
- use `requirement-freezer` when business rules, expected behavior, compatibility, or scope need stabilization
- use `workflow-inspector` when execution flow or workflow impact is important
- use `module-inspector` when module ownership, modifiability, or dependency direction is unclear
- use `implementation-slicer` to convert requirements or goals into slices
- use `context-pack-builder` to create `.task/<task-id>/context-pack.md` before coding

**Bugfix Fast-Track**: For bug fixes, the analysis phase is considered complete once a failing test case or clear reproduction steps are confirmed. Formal requirement freezing is usually bypassed unless expected behavior is unclear.

The analysis phase may produce:
- `.task/active.json`
- `.task/<task-id>/requirement.md`
- `.task/<task-id>/implementation-plan.md`
- `.task/<task-id>/context-pack.md`
- `.task/<task-id>/state.json`

When building `.task/<task-id>/context-pack.md`, route context in this order:
1. load global rules and task artifacts first
2. use `docs/project/knowledge-map.md` to match only the relevant knowledge areas
3. prefer `docs/current/...` for actual present-day behavior and use `docs/target/...` only when future design matters to the task
4. if target files are known, walk upward from those paths to load nearby `MODULE_RULES.md`, `AGENTS.md`, and `HARNESS_RULES.md`
5. exclude unrelated docs and note the exclusion briefly

For incident or bugfix work, include `.task/<task-id>/incident.md` when it exists and is relevant.

### Knowledge Mode And Maturity

Use `harness.config.yaml` as the local default when it defines:

- `knowledge.mode`: `standard` or `mudball`
- `knowledge.maturity`: `L0`, `L1`, `L2`, `L3`, or `L4`

Knowledge mode sets the starting posture:

- `standard`: balance current-state understanding with design intent
- `mudball`: start from present-day behavior, risk, and safe-change advice; do not assume clean boundaries

Knowledge maturity scales how much documentation depth and governance the agent should expect:

- **L0 — Minimal capture**: task-local context, sparse docs, explicit unknowns, low ceremony
- **L1 — Current-state map**: capture entrypoints, major flows, risk zones, unknowns, and safe-change notes first
- **L2 — Reusable area knowledge**: maintain stable routing, important current/target docs, and reviewed rule metadata for important areas
- **L3 — Governed knowledge**: stronger docs/rules sync, clearer ownership, and regular drift checks between current and target knowledge
- **L4 — Strict governance**: curated high-trust knowledge, explicit hard/confirmed constraints, and strong validation/review expectations for boundary-sensitive change

Scaling guidance:

- At **L0-L1**, do not require broad documentation before small safe changes.
- At **L2**, expect meaningful docs updates when design understanding changes.
- At **L3-L4**, expect stronger docs/rules synchronization and clearer validation evidence for architecture or boundary changes.
- In `mudball` mode, default to current-state-first behavior even when maturity is higher, and do not pressure the project toward L3/L4 unless users explicitly choose that posture.

When analysis is complete, the agent must stop and wait for explicit user confirmation before starting coding, except Tier S.

### Critic Gates

The critic gate is a risk-control checkpoint, not a coding authorization.

1. **Plan-review critic gate**
   - Runs after the relevant requirement, implementation plan, and context pack exist.
   - Required for Tier L and high-risk work before coding starts.
   - Optional for Tier M when the work is straightforward and low-risk.
   - A critic `PASS` may satisfy `criticPassed`, but it does not bypass `allowedToCode`, the current phase, or human confirmation.

2. **Pre-done critic gate**
    - Runs after coding and review for Tier L or high-risk approved work.
   - Checks gate evidence before the agent declares the approved work done: reviewer verdict, validation result, unresolved blockers, changed-file inventory, forbidden-file status, and state/gate consistency.
    - Does not replace `harness-reviewer`, validation, or the normal slice gate.
   - Must not repeat full code review or broad repository discovery. If evidence is missing, report the missing evidence instead of rediscovering the repository.

### Coding Phase

The agent must code only from the approved context pack and approved implementation slice or approved parallel slice group.

For complex tasks, the approved implementation plan may define `parallel-capable` slices or approved parallel slice groups. This is optional planning metadata, not a requirement that every agent must run in parallel.

The agent may complete temporary substeps inside the current approved slice or group without asking again, for example:
- editing multiple files inside the same approved slice
- local refactoring required only for that slice
- running validation commands for that slice
- fixing slice-local test failures

When a confirmed parallel slice group is active:
- agents with subagent or safe parallel execution support may execute the group members concurrently
- agents without that capability must execute the same group members sequentially in the declared fallback order
- the primary agent remains responsible for merging results, resolving conflicts, and running group validation

When the current coding slice is complete, the agent must automatically perform review for that same slice before stopping at the slice gate.

For Tier L or high-risk work, the agent should also run the pre-done critic gate after coding and review, then include the result in the slice or final summary.

When the current approved work is a parallel slice group, the agent must stop only after the whole approved group is complete, merged, validated, and reviewed, then wait for explicit user confirmation before the next slice or group.

If review fails for the current slice or group, the agent may plan the smallest slice-local fix, apply it, and re-run review. Stop for user decision if the same slice or group is still blocked after 3 total review attempts.

When all approved coding slices and groups are complete, the agent must stop with a final validation and review summary.

Validation levels are:
- slice validation: checks the current slice only
- group validation: checks all members of the approved parallel group after merge or sequential fallback execution
- final validation: checks the full approved implementation after slice review is complete
- review validation: records boundary-reviewer findings and any remaining validation gaps

### Review Phase

Review for the current approved slice or group starts automatically after implementation. A separate user confirmation is not required between coding and review for the same approved slice or group.

Review includes:
- boundary review
- scope check against allowed and forbidden modifications
- rule conflict check
- validation status check
- docs, rules, and knowledge-map sync decision

Review is diff-first and bounded to the current approved slice or group. The reviewer starts from the changed-file inventory and reads only changed files plus directly required context. Repository-wide search is exceptional and should be tied to a specific unresolved risk.

The coding agent may perform lightweight self-check to report changed files and obvious forbidden-scope issues, but independent diff review belongs to `harness-reviewer`. The pre-done critic gate audits evidence and gate readiness; it does not redo the reviewer role.

For critic-gated work, review remains mandatory even if the critic already passed.

## Human Confirmation

Humans must confirm blocking business questions, scope tradeoffs, protected-area changes, compatibility breaks, and any requirement that cannot be inferred from existing code, docs, or rules.

The agent must also stop at these harness gates:
- after the analysis phase is complete, before coding starts
- after each coding slice or approved parallel group has completed coding and review, before the next slice or group starts

Do not stop between small analysis steps such as intake, requirement freezing, inspection, slicing, and context-pack creation. Do not stop for temporary implementation substeps inside a coding slice, such as file batches, local test fixes, or slice-local refactoring.

## Mandatory Gate Behavior

At each harness gate, the agent must output a short gate report with all of the following fields:
- `Phase`
- `Completed Work`
- `Files Created or Changed`
- `Validation Status`
- `Recommended Next Step`
- `User Confirmation Required`

When the completed work is a parallel slice group, the gate report must also state the group name, member slices, execution mode used, fallback order if used, shared files, and merge owner.

The final line must be exactly:

`User confirmation required to continue.`

## Priority Rule

This harness workflow overrides any general default behavior that would otherwise continue automatically from analysis to coding or from one coding slice to the next. Coding may continue automatically into review only for the currently approved slice or group.

If instructions conflict, the agent must follow the harness gates unless the user explicitly overrides them.

## Trivial Task Exception (Tier S)

A task is Tier S only if it is a single low-risk change with clear scope, no boundary ambiguity, no workflow impact, and no need for task documents. If any of those conditions is not clearly true, treat the task as non-trivial.

## Agent Automation

Repository agents may inspect files, classify questions, write task docs, build context packs, slice implementation work, apply scoped code changes, run validation commands, and review diffs against allowed scope within the currently confirmed phase. They must not automatically cross from analysis to coding or from one coding slice or group to the next. They may automatically cross from coding into review only for the current approved slice or group.

## Agent Capability And Parallel Fallback

Parallel execution is optional and capability-dependent. For single-agent environments, it refers to processing independent file groups continuously within one approved coding phase.

Preferred uses for parallel execution:
- parallel exploration during analysis
- independent module or workflow inspection
- independent investigation of logs, tests, or call paths
- implementation of disjoint files inside an approved parallel slice group

Do not use parallel execution for:
- trivial or low-risk tasks
- shared-file edits without a clear merge owner
- SQL or data migration steps that require strict ordering
- public API or contract changes without an explicit serial owner
- architecture-sensitive refactors without a dependency graph

If the current agent does not support subagents, or cannot safely coordinate parallel execution, it must execute the same approved work sequentially in dependency order.

`parallel-capable` means optional parallelism with a required sequential fallback, not a mandatory parallel execution model.

## Knowledge Policy

Docs explain design, architecture, functional behavior, workflow, and boundaries.

For current-vs-target knowledge:
- `docs/current/` records observed current-state behavior, risk, and safe-change guidance
- `docs/target/` records desired future design and migration intent
- current-state docs should label fact, inference, and unknown when certainty matters
- target-state guidance must not be treated as proof of current behavior

Use maturity to scale expectations, not to force unnecessary document volume:

- `L0-L1`: compact docs are acceptable if unknowns and risks are made explicit
- `L2`: keep reusable area docs and routing reasonably current
- `L3-L4`: keep docs, rules, and validation evidence more tightly aligned

For `knowledge.mode: mudball`, current-state capture is the default. L0 or L1 may be a valid steady state, and L2 is a reasonable gradual improvement point.

Docs must not become source-code indexes. Use IDE tools or local search for code navigation.

Context packs should record loaded context compactly under categories such as:
- Global Rules
- Knowledge Map Matches
- Path-Proximity Rules
- Excluded Context

When local path-proximity rules conflict with repository-global safety or boundary rules, the global rules win.

Rules define enforceable constraints. When adding, moving, renaming, or deleting docs or rules, update `docs/project/knowledge-map.md`.

## File Roles

- `AGENTS.md` defines repository-level workflow and constraint priority.
- `.aiassistant/rules/*.md` contains enforceable agent constraints.
- `docs/**/*.md` contains project knowledge and architecture explanations.
- `docs/project/knowledge-map.md` is the routing index for ownership, docs, rules, and boundary notes.
- `docs/current/**/*.md` contains current-state knowledge about how the project works today.
- `docs/target/**/*.md` contains desired future design, migration direction, and proposed boundaries.
- `.task/active.json` selects the current task and records phase, gate, and next-command summary.
- `.task/<task-id>/requirement.md` freezes task requirements.
- `.task/<task-id>/implementation-plan.md` defines executable implementation slices.
- `.task/<task-id>/state.json` records durable task phase, status, gates, files, and current slice.
- `.task/<task-id>/context-pack.md` contains the compact context for the current coding slice or approved parallel group.

Use the local task date for `<yyyy-MM-dd>`, for example `.task/2026-04-28/`. Keep task docs concise. Prefer references and distilled summaries over copying full source documents.

Legacy `.task/context-pack.md` is supported only as a migration fallback. Prefer the active task directory for all new context packs.

## Task State Contract

`taskId` is a relative task path under `.task/`, using `yyyy-MM-dd/task-slug` such as `2026-05-27/add-login`.

### `.task/active.json`

`active.json` is a flat pointer to the current task.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `taskId` | string | yes | Active task path. |
| `type` | string | no | Task classification: `feature`, `bugfix`, `refactor`, `documentation`, or `investigation`. |
| `phase` | string | no | Current phase: `analysis`, `coding`, `review`, or `finalization`. |
| `allowedToCode` | boolean | no | Whether the analysis-to-coding gate has been confirmed. |
| `currentSlice` | string \| null | no | Currently approved slice identifier. |
| `lastGate` | string \| null | no | Last gate where the agent stopped. |
| `nextCommand` | string | no | Recommended next CLI command or skill action. |
| `updatedAt` | string | no | Last update timestamp in ISO-8601 format. |

Example:

```json
{
  "taskId": "2026-05-27/example-task",
  "type": "feature",
  "phase": "analysis",
  "allowedToCode": false,
  "currentSlice": null,
  "lastGate": null,
  "nextCommand": "/harness-context",
  "updatedAt": "2026-05-27T00:00:00Z"
}
```

### `.task/<task-id>/state.json`

`state.json` records durable task execution state. Its `taskId` must match `.task/active.json.taskId`.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `taskId` | string | yes | Same value as `.task/active.json.taskId`. |
| `type` | string | no | Task classification: `feature`, `bugfix`, `refactor`, `documentation`, or `investigation`. |
| `phase` | string | no | Current phase: `analysis`, `coding`, `review`, or `finalization`. |
| `status` | string | no | Task status: `in_progress`, `completed`, or `blocked`. |
| `allowedToCode` | boolean | no | Whether the analysis-to-coding gate has been confirmed. |
| `currentSlice` | string \| null | no | Currently approved slice identifier. |
| `gatePolicy` | object | no | Task-local gate policy record with fields such as `recommended`, `selected`, `reason`, and `finalApprovalRequired`. A task-local override changes the task's default gate posture only; it does not bypass required gates or explicit stop conditions. |
| `slices` | object[] | no | Planned slices or approved groups for this task. |
| `gates` | object | no | Gate booleans such as `requirementFrozen`, `planApproved`, `contextPackReady`, `criticPassed`, `implementationDone`, `reviewPassed`, and `validationPassed`. `criticPassed` records the plan-review critic gate, not permission to code by itself. |
| `files` | object | no | Task artifact paths such as `requirement`, `implementationPlan`, and `contextPack`. |
| `updatedAt` | string | no | Last update timestamp in ISO-8601 format. |

Example:

```json
{
  "taskId": "2026-05-27/example-task",
  "type": "feature",
  "phase": "analysis",
  "status": "in_progress",
  "allowedToCode": false,
  "currentSlice": null,
  "gatePolicy": {
    "recommended": "balanced",
    "selected": null,
    "reason": "Default non-trivial task posture until a task-specific override is chosen.",
    "finalApprovalRequired": true
  },
  "slices": [],
  "gates": {
    "requirementFrozen": false,
    "planApproved": false,
    "contextPackReady": false,
    "criticPassed": false,
    "implementationDone": false,
    "reviewPassed": false,
    "validationPassed": false
  },
  "files": {
    "requirement": ".task/2026-05-27/example-task/requirement.md",
    "implementationPlan": ".task/2026-05-27/example-task/implementation-plan.md",
    "contextPack": ".task/2026-05-27/example-task/context-pack.md"
  },
  "updatedAt": "2026-05-27T00:00:00Z"
}
```

### `state.json` slice entry shape

When `state.json.slices` is used, each slice entry may record gate-policy hints for that slice or approved group.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Slice or approved group identifier. |
| `status` | string | no | Slice status such as `pending`, `in_progress`, `completed`, or `blocked`. |
| `gateClass` | string | no | Frozen gate hint vocabulary. Use only `simple`, `standard`, `boundary-sensitive`, or `high-risk`. |
| `risk_score` | integer | no | Supplemental per-slice risk score from `1` to `5`. It may preserve or strengthen a pause relative to `gateClass`, but must not weaken required stops or replace `gateClass`. |
| `gateReasons` | string[] | no | Short reason labels that explain the gate posture for the slice or group, including any stricter pause signaled by `risk_score` when relevant. |

Example:

```json
{
  "id": "slice-2-policy-aware-task-artifacts-skills",
  "status": "in_progress",
  "gateClass": "boundary-sensitive",
  "risk_score": 4,
  "gateReasons": ["agent-instructions", "task-state-contract"]
}
```

Agents may preserve extra project-local fields, but must not change the meaning of the fields above.

## Framework-Managed Install And OpenCode Notes

When this project was installed or upgraded through the harness, `.harness/manifest.json` is the ownership record for framework-managed files.

Install/distribution modes:

- `embedded` — default for new installs and the closest match to legacy behavior
- `hybrid` — local install with explicit adapter-aware distribution metadata
- `adapter` — adapter-oriented install while keeping local manifest-based safety checks

When recorded, the mode appears in `.harness/manifest.json` as `distributionMode`. `harness.config.yaml` may mirror it under `distribution.mode` for readability. Legacy installs without manifest `distributionMode` remain valid; `harness diff`, `harness sync`, and `harness doctor` may report or infer the effective mode. The field is written only when the user explicitly selects or provides a mode, when the manifest already contains `distributionMode`, or when `harness.config.yaml` specifies `distribution.mode`.

For optional OpenCode assets:

- the framework template source of truth is `templates/opencode/**` in the framework distribution
- managed entries may record metadata such as `adapter`, `commandSurface`, `templateHash`, `renderedHash`, and legacy `hash`
- safe comparison uses `renderedHash ?? hash` for compatibility with older manifests
- local edits, missing files, conflicts, and orphaned managed entries are reported rather than silently overwritten
- force-style replacement must be explicit

Canonical model profile source:

- `.harness/model-profiles.yml` is the canonical source when present
- `harness.config.yaml` `models.profiles.*` is legacy fallback only when the canonical file is absent
- `harness sync` may restore or re-render the canonical file and OpenCode agent files from effective profile values
- `harness doctor` reports drift and whether expected model values came from the canonical file or the legacy fallback

OpenCode command surfaces:

- `minimal` — `/harness`, `/harness-dev`, `/harness-incident`, `/harness-docs`, `/harness-config`
- `standard` — minimal plus `/harness-context`, `/harness-status`, `/harness-continue`
- `advanced` — standard plus `/harness-feature`, `/harness-bugfix`, `/harness-refactor`
- legacy `full` is a compatibility alias for `advanced`

The intended default is builder-first usage through `/harness`; broader command surfaces are optional ergonomics layers.
