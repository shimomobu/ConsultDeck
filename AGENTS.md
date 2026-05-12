# AGENTS.md

## Project

ConsultDeck is a local system for semi-automated consulting deck generation.

The final output is Microsoft PowerPoint `.pptx`.
The core architecture is:

User Input → RequirementSpec → OutlineSpec → SlideSpec → Renderer → PPTX

## Core Principles

- TDD is mandatory.
- Do not implement without a failing test first.
- Keep MVP scope small.
- Avoid over-engineering.
- SlideSpec is the central contract.
- Renderer must be replaceable.
- PPTX generation must be isolated behind Renderer boundary.
- Stable Diffusion is only for supplemental images.
- GPU workloads must not run concurrently.

## Architecture Rules

- Non-renderer modules must not depend on PPTX libraries.
- SlideSpec must not import renderer modules.
- Renderer interface must remain narrow.
- MCP integration must be isolated behind McpRenderer / McpClient / McpAdapter.
- Template management must not be hardcoded into Renderer.
- Configuration must support both file-based settings and future UI-based settings.

## TDD Rules

For each task:

1. Write or update tests first.
2. Confirm RED.
3. Implement the minimum code.
4. Confirm GREEN.
5. Refactor only if needed.
6. Run the relevant test suite.
7. Report test results.

## Git Rules

- Commit after each coherent phase.
- Do not leave completed work uncommitted.
- Use concise commit messages.
- Do not mix unrelated changes.

## Review Checklist

Before reporting completion, check:

- Does this follow the RFP?
- Does this preserve SlideSpec as the central contract?
- Is the Renderer boundary preserved?
- Is this still MVP-sized?
- Are tests meaningful?
- Are docs updated if behavior or architecture changed?

## Reporting Format

Report in Japanese with:

- Changed files
- Test results
- Design decisions
- Remaining risks
- Commit status

## Documentation update rule

For every implementation or review task, check whether the change introduces, resolves, or modifies:
- design decisions
- known risks
- residual risks
- operational constraints

If applicable, update:
- docs/06_decisions.md
- docs/07_risks.md

If no update is needed, explicitly report why.

# Agent Rules

## Task Management

Before starting work:
- Read `docs/tasks/backlog.md`
- Move the target task to `docs/tasks/doing.md`
- Confirm acceptance criteria

During work:
- Follow TDD
- Add failing tests first
- Keep implementation minimal
- Do not change unrelated files

After completing work:
- Run tests
- Move the task to `docs/tasks/done.md`
- Update `docs/progress.md` if it exists
- Update `docs/06_decisions.md` if design decisions changed
- Update `docs/07_risks.md` if risks were found

Never finish with code changes only.

## Scope Control

Do not expand scope without explicit justification.
Prefer the smallest viable implementation that satisfies tests and architecture constraints.

## Task Naming Rule

Use the following task format in `docs/tasks/*.md`:

- [ ] TASK-001: Short task name
- [x] TASK-001: Short task name

Rules:
- Keep TASK IDs unique.
- Do not reuse completed TASK IDs.
- Do not change task meaning when moving between Backlog, Doing, and Done.
- Preserve checkbox state according to task status.