# Tier Policy Workflow Design Draft

This document is an installed target-project design note for deferred workflow research. It is intentionally kept in core templates so projects can see the boundary between the implemented Tier-policy MVP and future workflow-engine ideas without mistaking the future design for active behavior.

It defines an MVP boundary for configurable Tier policy without implementing a general workflow DAG engine.

## Purpose

- keep Tier policy focused on task classification and workflow hints
- preserve current gate vocabulary and gate-policy semantics
- record where future workflow configurability would interact with existing harness flow
- give target projects a stable place to record future workflow questions without rewriting current harness behavior docs

## Why This Document Is Installed

This file stays in the core installed docs set for now because it serves a project-neutral documentation role:

- it explains why `.harness/tier-policy.yml` exists without implying that Tier policy can already rewire execution
- it separates current implemented workflow rules from deferred workflow-engine ideas
- it gives target projects a safe reference when they want to discuss future extensibility or roadmap questions

Projects should treat this file as a target/future-facing design note, not as executable current-state behavior. The current source of truth for actual harness execution remains `docs/project/harness-workflow.md` plus `harness.config.yaml` `gatePolicy`.

## Current Workflow Nodes

The current harness workflow is a mostly fixed directed flow with a few policy-driven branches:

1. task intake and Tier classification
2. analysis helpers as needed
   - requirement freezing when needed
   - workflow or module inspection when needed
   - implementation slicing when needed
   - context-pack creation
3. analysis-to-coding gate
4. approved slice execution
5. automatic review for that same slice or approved group
6. critic gates when required by Tier or risk
7. slice gate or final gate

The existing Tier split is coarse-grained:

- Tier S: direct coding and review
- Tier M: analysis plus context pack before coding
- Tier L: full harness flow with stricter gating and critic expectations

## Conceptual Agent And Skill I/O

Current workflow behavior can be described as node contracts rather than a configurable engine:

| Node | Inputs | Outputs |
| --- | --- | --- |
| Task intake | user request, repo rules, local config | Tier suggestion, task type, next harness step |
| Requirement freeze | unclear behavior or scope | requirement artifact or clarified stop condition |
| Inspection | selected files, docs, rules | workflow/module findings and risk notes |
| Implementation slicing | requirements, findings | approved slices or groups with gate hints |
| Context-pack build | active task artifacts, relevant docs/rules | `.task/<task-id>/context-pack.md` |
| Coding | approved slice, context pack | scoped file changes and slice validation evidence |
| Review | changed-file inventory, approved scope | scope verdict, risk notes, follow-up actions |
| Critic gate | task artifacts, review/validation evidence | gate verdict and missing-evidence report |

This framing keeps node responsibilities stable even if later Tier policy adds more configurable routing hints.

## Where Tier Policy Can Safely Influence Flow

An MVP Tier policy can safely influence only advisory decisions such as:

- how a task is classified by Tier
- what level of analysis is recommended
- whether critic use is suggested or expected
- what model profile role is preferred
- what workflow hint label best matches the task

The MVP should not let Tier policy directly redefine gates, invent new gate classes, or bypass required human confirmation.

## Workflow DAG Configuration Complexity

Full workflow DAG configurability is deferred because it introduces multiple coupled concerns at once:

1. **Node contract stability**: configurable edges require stable, documented input/output contracts for every skill and agent handoff.
2. **Safety invariants**: some edges are not optional, such as analysis before non-trivial coding and human confirmation at mandatory gates.
3. **Conflict handling**: user-configured routing could contradict safer defaults or create ambiguous paths.
4. **Execution semantics**: optional, required, repeated, and parallel nodes need a clear state model.
5. **Validation semantics**: different paths would need explicit rules for what counts as sufficient review, critic evidence, and final validation.
6. **Template portability**: a project-neutral framework must avoid encoding stack-specific workflows while still remaining understandable.

Because these concerns are intertwined, a full DAG engine would be a separate design and implementation track, not an incidental extension of Tier policy.

## MVP Proposal

For the configurable Tier policy MVP:

- keep the executable workflow fixed as documented in `docs/project/harness-workflow.md`
- allow Tier policy to provide **workflow hints**, not executable graph rewrites
- keep gate behavior under `gatePolicy` and existing workflow rules
- keep critic requirements expressed as current workflow expectations, not arbitrary user-defined nodes
- allow builder/config flows to explain which current path was chosen and why
- allow builder/config flows to turn natural-language policy requests into candidate YAML only after showing a diff and waiting for explicit persistence confirmation

Recommended hint categories for later implementation work:

- `workflowHint`: labels such as direct, analysis-context, or full-harness
- `reviewLevel`: labels such as standard or critic-required
- `modelProfileHint`: existing model profile role/name only
- `gateHint`: advisory only; must not replace `gatePolicy`

## Implemented MVP Boundary Vs Deferred Hardening

Implemented MVP behavior today:

- `.harness/tier-policy.yml` is the installed project-local Tier-policy file
- framework defaults remain available when the project file is missing
- parse and validation problems fall back to safer framework behavior with explanation
- conflict handling distinguishes refinements, explicit overrides, soft conflicts, and unsafe downgrades
- natural-language policy requests go through candidate YAML, diff display, and explicit confirmation before persistence

Deferred future hardening beyond the MVP:

- cross-validating every `modelProfileHint` against `.harness/model-profiles.yml`
- stricter automatic rejection of unknown ordered-field values instead of the current conservative explanation/fallback posture
- a full configurable workflow DAG or workflow-engine state model

## Concrete MVP Schema Freeze

The current MVP freezes the project-local Tier policy file as `.harness/tier-policy.yml` with this shape:

```yaml
schemaVersion: "1"
tiers:
  S:
    description: "..."
    matchRules:
      - "..."
    minTier: null
    maxTier: "S"
    workflowHint: "direct"
    gateHint: "default"
    reviewLevel: "standard"
    modelProfileHint: "build"
  M:
    description: "..."
    matchRules:
      - "..."
    minTier: "M"
    maxTier: "M"
    workflowHint: "analysis-context"
    gateHint: "default"
    reviewLevel: "standard"
    modelProfileHint: "build"
  L:
    description: "..."
    matchRules:
      - "..."
    minTier: "L"
    maxTier: null
    workflowHint: "full-harness"
    gateHint: "prefer-strict"
    reviewLevel: "critic-required"
    modelProfileHint: "think"
```

Schema rules for dependent slices:

- `schemaVersion` is required and currently fixed to string `"1"`
- `tiers` is required
- tier keys are fixed to `S`, `M`, and `L`; the MVP does not add custom tier names
- `description`, `matchRules`, `workflowHint`, `gateHint`, `reviewLevel`, and `modelProfileHint` are required for each tier
- `minTier` and `maxTier` are optional and may be `S`, `M`, `L`, or `null`
- `matchRules` is a plain string list; no inline maps or nested rule objects

Precedence and boundary notes:

- framework defaults remain the fallback when the file is missing
- project-local file content is an override/refinement layer for Tier classification and hints only
- `tiers.<tier>.gateHint` is advisory and must not replace `gatePolicy.defaultMode` or the selected task gate policy
- `tiers.<tier>.modelProfileHint` must reference an existing model-profile role/name and must not carry provider/model IDs
- refinements should be auto-accepted with rationale, explicit overrides should be surfaced clearly, and unsafe downgrades should fall back to framework defaults rather than silently accepted

## Natural-Language Candidate Workflow Boundary

The MVP natural-language authoring path is intentionally narrow:

1. user describes desired Tier-policy changes in prose
2. builder/config workflow drafts candidate `.harness/tier-policy.yml` content
3. builder shows the candidate and a diff against the current file or framework defaults
4. builder includes any already-available conflict or override explanation relevant to the candidate
5. builder stops for explicit confirmation before writing

This is a guided config-authoring workflow, not a new standalone CLI command and not a general workflow-DAG editor.

Parser-compatibility boundary for this schema:

- no anchors
- no merge keys
- no multi-document YAML
- no complex inline YAML structures

## Deferred Boundaries

The following remain out of scope for the MVP and should be deferred beyond Tier-policy basics:

- user-defined workflow nodes
- arbitrary edge rewiring between existing nodes
- per-project replacement of mandatory harness gates
- new gate vocabulary or numeric workflow scoring
- a standalone workflow-DAG execution engine
- automatic persistence of natural-language workflow changes without explicit confirmation

## Suggested Future Design Questions

If a later slice explicitly explores configurable workflow execution, it should answer:

1. Which workflow edges are hard invariants versus configurable suggestions?
2. Which node contracts are stable enough to expose in project-neutral templates?
3. How are invalid or unsafe workflow graphs detected and explained?
4. How does task state record active path selection without making `state.json` engine-specific too early?
5. How do parallel groups interact with configurable routing while preserving sequential fallback?

## Summary

Tier policy should first become a safe classification-and-hints layer. A full configurable workflow DAG is a separate future capability that should begin only after the framework freezes node contracts, safety invariants, and validation semantics.
