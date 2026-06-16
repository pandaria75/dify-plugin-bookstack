---
name: task-intake
description: Default lightweight entrypoint for non-trivial repository tasks, including feature development, bug fixing, refactoring, documentation updates, investigations, reviews, and workflow-sensitive work. Use when a new task starts and the harness flow has not started yet; use fast path when structured task artifacts or a clearly scoped ongoing slice are already provided.
phase: analysis
model_requirement: reasoning
can_edit: true
risk_level: low
---

# Task Intake

Use this skill to collect task information and route the task into the lightweight file-based harness.

## When To Use

- Use when a new non-trivial repository task starts and the harness flow has not started yet.
- Use the fast path when structured task artifacts or a clearly scoped ongoing slice already exist.

## Inputs Required

- User task goal and requested outcome
- Relevant repository constraints, paths, or evidence when available
- Existing task artifacts if the task is already in progress

## Fast Path

If the user already provides structured task artifacts or a clearly scoped ongoing slice, do not ask the full intake questions.

Structured task artifacts include:
- `.task/active.json`
- `.task/<task-id>/state.json`
- `.task/<task-id>/requirement.md`
- `.task/<task-id>/implementation-plan.md`
- `.task/<task-id>/context-pack.md`

Use the local task date for `<yyyy-MM-dd>`, for example `.task/2026-04-28/`.

For fast-path tasks:
1. Summarize the current task state.
2. Identify the next required harness step.
3. Route directly to that step.
4. Ask only blocking questions needed for routing.

## Steps

1. Read `AGENTS.md`.
2. Read `harness.config.yaml` if present.
3. Classify the task type:
   - feature
   - bugfix
   - refactor
   - documentation
   - review
   - investigation
   - build/deployment
4. Recommend an initial gate policy for the task:
   - `strict` for existing harness Tier L, high-risk, workflow-sensitive, or boundary-sensitive work
   - `balanced` for most existing harness Tier M work with clear approved slices
   - `autonomous` only when the task is already well-bounded, validation is clear, and fewer mid-task pauses are acceptable
5. Explain that a task-local policy override changes the task's default gate posture only. It does not bypass required analysis gates, final approval by default, or any other explicit stop condition.
6. Ask only the minimum blocking questions required to choose the next workflow.
7. Do not implement code.
8. Do not create large documents unless the task requires them.
9. For non-trivial new tasks, create a dated task directory and point `.task/active.json` to it.
10. Route to the correct next skill or workflow.

## Questions To Ask

### Common Questions

- What is the task goal?
- Which module, package, feature area, API, page, or workflow is involved?
- Is this a new feature, bug fix, refactor, investigation, documentation task, or review?
- Is the expected behavior already known?
- Are there files, logs, screenshots, APIs, or docs that must be used?
- Is any area forbidden to modify?
- What validation command or manual verification is expected?

### Feature Task Questions

- What user or system scenario should be supported?
- What is in scope?
- What is explicitly out of scope?
- Are UI, API, database, workflow, or infrastructure changes required?
- Are compatibility requirements involved?

### Bugfix Task Questions

- What is the observed behavior?
- What is the expected behavior?
- How can the issue be reproduced?
- Is there an error log or stack trace?
- Is the bug stable or intermittent?
- Which version, branch, environment, customer, or deployment context is affected?
- Is this a regression?

### Refactor Task Questions

- What problem should the refactor solve?
- What behavior must remain unchanged?
- What areas are allowed to change?
- What areas are forbidden to change?

## Routing Rules

### Feature

Use:

1. requirement-freezer when scope, business rules, or expected behavior are unclear
2. module-inspector or workflow-inspector when boundaries or flows need analysis
3. implementation-slicer
4. context-pack-builder
5. coding
6. boundary-reviewer

### Bugfix

Use:

1. bug intake section in this skill
2. workflow-inspector if call chain or runtime flow is unclear
3. module-inspector if module boundary is unclear
4. requirement-freezer only when expected behavior or business rule is unclear
5. context-pack-builder
6. coding
7. boundary-reviewer

### Refactor

Use:

1. module-inspector
2. workflow-inspector if behavior flow may be affected
3. implementation-slicer
4. context-pack-builder
5. coding
6. boundary-reviewer

### Documentation

Use:

1. workspace-knowledge-manager
2. update `docs/project/knowledge-map.md` when docs or rules are added, moved, renamed, or deleted

## Output Artifact

- A compact intake result that captures task type, current understanding, gate policy recommendation, blocking questions, assumptions, and the recommended next step
- Task artifacts only when the task requires initialization or the caller asks for them

## Output Format

```md
# Task Intake Result

## Task Type

## Current Understanding

## Recommended Gate Policy

## Blocking Questions

## Non-blocking Assumptions

## Recommended Next Step

## Suggested Prompt For Next Step
```

## Guardrails

- Ask only blocking questions.
- Do not implement code.
- Do not generate full implementation plans directly.
- Keep the intake lightweight.
- Prefer repository evidence over asking the user when possible.
- Recommend a gate policy at task start for non-trivial work.
- Treat Tier L / Tier M references here as existing harness task classification guidance only, not as a configurable tier-policy mapping.
- Preserve final approval by default unless higher-priority instructions explicitly change it.
- Treat task override as policy selection, not as permission to bypass required gates.

## Gate / Stop Condition

- Stop and ask blocking questions when the goal, task type, or safe next workflow cannot be determined from available evidence.
- Stop before coding, implementation planning, or broad document creation.

## Red Flags

- Missing task goal, scope, or validation expectation
- Conflicting instructions about allowed or forbidden areas
- Fast-path artifacts that disagree about current slice or gate status
- Requests that implicitly skip required harness steps

## Exit Criteria

- The next harness step is identified
- Blocking questions are minimized and explicit
- Recommended gate policy is stated for non-trivial work
- The task is routed without implementing code

## Handoff

- Send the task to the next skill with the intake result, task type, known scope, open blocking questions, and any task-local gate policy selection
