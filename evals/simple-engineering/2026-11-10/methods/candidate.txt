---
name: simple-engineering
description: Choose and implement the simplest complete solution when writing, fixing, or refactoring code, selecting dependencies, or reviewing unnecessary complexity. Use to keep a change focused while preserving required behavior. Does not define a delivery pipeline or replace specialized debugging, testing, or security review.
metadata:
  version: "0.1.0"
---

# Simple Engineering

Optimize for a solution that is easy to understand, correct, and complete for the requested outcome. Use code size as a clue to complexity, not a target.

## Establish the scope

- Identify the required observable result and constraints. Explicitly requested options, compatibility, and quality requirements belong to the scope; do not remove them to make the task smaller.
- Read the affected code and project guidance. Trace relevant callers, interfaces, tests, configuration, and data contracts before deciding how small the change can be.
- Resolve questions from available evidence first. Ask when competing interpretations materially change behavior, compatibility, data safety, or the requested scope. For reversible implementation details, follow project conventions and state consequential assumptions without blocking independent work.

## Choose the solution

- Prefer an existing project pattern or capability when it fits. Next consider the standard library or platform and suitable installed dependencies. Add a dependency when its reliability or maintenance benefit justifies its cost; do not recreate security-sensitive functionality merely to avoid one.
- Add a boundary, abstraction, or configuration option for a concrete requirement or an invariant it makes clearer. A single use alone neither justifies nor rules out an abstraction. Avoid infrastructure for hypothetical future needs.
- Prefer readable control flow to compressed expressions. Compare options by correctness, clarity, and maintenance burden before diff size.
- Preserve validation at trust boundaries, error handling, data integrity, security, accessibility, and required compatibility. Remove an existing safeguard only when evidence establishes that its responsibility is unnecessary or remains covered elsewhere.

## Make the complete change

- Keep edits tied to the requested outcome. Update affected callers, tests, configuration, documentation, and migrations when the change requires them.
- For a bug, establish the cause before choosing a fix; use the existing diagnosis process when evidence is insufficient. Fix shared behavior at its appropriate owner and check affected consumers.
- Remove code made obsolete by this change. Leave unrelated cleanup out unless necessary for the requested result; mention a separate finding only when useful.
- Explain non-obvious constraints or compromises where maintainers need them. Use comments for reasoning the code cannot express; do not impose a line limit or a mandatory comment format.

## Verify the result

- Choose checks that could expose a failure in the changed behavior. For a bug, reproduce the failure before the fix when feasible and check the same behavior afterwards. For a refactor, check the behavior that must remain unchanged.
- Add or update tests for new or changed non-trivial behavior when existing checks do not cover it. Derive expected results from the requirement and observe public behavior, including externally visible effects, rather than mirroring internal helpers.
- Match additional verification to risk and run required project checks. A prose typo may need inspection; a payment or persistence change needs checks for relevant failure cases. A small diff can carry high risk.
- If verification fails, investigate within the agreed scope. If required tools, access, or a decision are missing, report the unresolved check and continue only independent work. Do not equate an unrun check with a passing result.

## Report

Briefly explain the result, the checks actually run, and material remaining limits. In a review, report actionable findings without silently editing code. Follow the task's requested output format; omit ritual lists of things that were not done.

This method does not select an orchestrator, model, tool, or approval policy. It introduces no persistent session mode and requires no sibling skill. Specialized methods may supply deeper diagnosis, test design, or review when the task needs them.

Source revisions, adaptations, and attribution: [sources](references/sources.md). Read that file when auditing provenance, not as an additional task procedure.
