# Repository Rules

## Priority

1. User instructions
2. `AGENTS.md`
3. `.aiassistant/rules/*.md`
4. `docs/**/*.md`

Rules define constraints. Docs provide knowledge.

## Rule Metadata Convention

Rule files may attach lightweight metadata to a rule or rule section:

```md
- Rule: <constraint statement>
  - type: observed | confirmed | target | hard
  - confidence: low | medium | high
  - source: <where this came from>
```

Use metadata when rule strength or evidence matters.

- `type` describes how strongly agents should apply the rule.
- `confidence` describes evidence quality, not priority.
- `source` records where the rule came from, such as code observation, config, runtime behavior, user instruction, review decision, repository policy, or target design.

### Rule Type Semantics

- `hard`: enforce by default unless a higher-priority instruction explicitly overrides it.
- `confirmed`: treat as an active repository convention or verified constraint; follow it by default, but escalate if it conflicts with newer evidence or higher-priority instructions.
- `observed`: treat as current-state evidence or working hypothesis. Do not block implementation or review solely because an observed rule exists unless a clear safety risk is present or a reviewer/user confirms it.
- `target`: treat as intended future direction. Do not describe it as current behavior and do not enforce it against current-state work unless the approved task is explicitly implementing that target.

### Upgrade Guidance

- Do not silently promote `observed` or `target` rules into `confirmed` or `hard` constraints.
- Upgrade an `observed` rule only after explicit review, stronger evidence, or direct user confirmation.
- When a rule is upgraded, update its metadata and keep the `source` specific enough that later readers can understand why the strength changed.

## General Constraints

- Do not expand task scope without explicit approval.
- Do not overwrite project-local knowledge during harness sync.
- Do not treat documentation as a replacement for source inspection.
- Prefer small, reversible changes.
- Preserve existing project conventions.

## Example Rules

- Rule: Preserve repository-global safety boundaries even when local patterns differ.
  - type: hard
  - confidence: high
  - source: repository policy

- Rule: This subsystem currently appears to depend on configuration file ordering.
  - type: observed
  - confidence: medium
  - source: observed code and runtime behavior
