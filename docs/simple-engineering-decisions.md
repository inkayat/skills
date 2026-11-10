# simple-engineering 0.1.0 — decision record

Status: discussion draft, 2026-11-10. Target repository: `inkayat/skills`.
This record does not inherit admission rules or acceptance claims from the deleted `inkayat/tolga-skills` repository.

The intended benefit is fewer unnecessary changes without losing required behavior. That remains a design hypothesis: the subsequent [comparative evaluation](simple-engineering-evaluation.md) did not demonstrate reliable incremental benefit.

## What was selected and why

Source identifiers and immutable links are in the skill's [source record](../skills/simple-engineering/references/sources.md).

| Source point | Decision in this skill | Reason and expected benefit |
| --- | --- | --- |
| K §1, Think Before Coding | Inspect evidence first; ask about consequential ambiguity | Avoid hidden product decisions while allowing routine reversible work to proceed |
| K §2, Simplicity First; P, smallest complete change | Preserve every explicit requirement; exclude speculative extras | Prevent both scope creep and incomplete delivery |
| P, Before you write | Trace relevant consumers, configuration, tests, and data contracts | Find the actual scope before optimizing the size of a patch |
| P, solution preference order | Prefer fitting existing patterns, then platform/library capabilities | Reuse maintained solutions and avoid redundant helpers |
| K §2; P, abstraction rules | Require a concrete reason for abstractions; allow useful single-use boundaries | Avoid speculative frameworks without banning a boundary that protects an invariant |
| K §3, Surgical Changes | Remove newly obsolete code; avoid unrelated cleanup | Keep changes reviewable and reduce unrelated regression risk |
| P, root-cause and never-cut rules | Diagnose the cause; preserve safeguards and check consumers | Avoid a tiny local patch that hides a systemic defect or weakens protection |
| K §4; P, non-trivial checks | Verify changed behavior with risk-appropriate evidence and required project checks | Avoid both ceremonial tests and unsupported completion claims |
| T, the two imagined edits | Test observable behavior and derive expectations from requirements | Catch behavioral regressions without binding tests to private implementation details |
| User's orchestration requirement | Keep the method independent of tools, models, and session modes | Let Claude, Firstmate, and Astro apply the same method; native host discovery remains a separate concern |

## What was changed or left out

| Source point | Not carried over | Reason |
| --- | --- | --- |
| K §1 | Stop and ask for every uncertainty | Routine details can be resolved from project conventions; substantive ambiguity still requires a decision |
| K §2 | A blanket ban on single-use abstractions; the 200-to-50-line heuristic | Usage count and line count do not establish simplicity or correctness |
| P, Levels and opening | `lite/full/ultra/off`, persistent activation, and the lazy-developer persona | They add session state and mode selection to a reusable method; these can be discussed separately if needed |
| P, solution preference order | An absolute ban on dependencies for small amounts of code | A short security-sensitive implementation may still warrant a maintained dependency |
| P, smallest complete change | Shortest diff as the winning rule; one-line comments; mandatory `shortcut:` comments | Favor readable complete changes and useful explanations rather than textual constraints |
| P, reporting | A mandatory closing list of skipped work | Report only meaningful verification gaps and risks instead of repetitive boilerplate |
| P, new non-trivial logic | A fixed minimum of one test or assertion | Adequacy depends on behavior and risk; existing coverage can suffice, while one assertion may be inadequate |
| S, Subtract Before You Add | Broad cleanup before construction | It conflicts with a narrow task when the old complexity is unrelated; remove only what the change makes obsolete or must replace |
| Superpowers and Matt Pocock | Full TDD, debugging, planning, and review workflows | These remain candidates for separate skills; this skill only establishes the simplicity and completeness boundary |
| Humanizer and Be Ambitious | Writing transformations and task-ambition procedures | They solve different problems and should not silently expand a coding change |

The last two rows are scope decisions, not claims that those other packages were exhaustively assessed for this draft.

## Author scenario review

The following are manual decision walkthroughs of the written instructions, not executed coding-agent trials. The author applied the draft to each input and recorded the decision below. They can expose contradictions, but cannot establish reliable model behavior or comparative benefit.

| Input | Decision reached from the draft | Rule exercised |
| --- | --- | --- |
| TLW must support Claude by default plus Firstmate and Astro | Keep all three options; choose a small common interface where required; do not invent extra providers | Explicit options are scope; concrete abstraction need |
| Fix a shared parser used by an API and CLI | Establish the cause; inspect both consumers; preserve both contracts and verify the failing input | Scope tracing and root cause |
| Correct one README typo | Inspect the prose diff; run any required project checks; do not introduce a code test for the text | Verification proportional to impact |
| Remove a payment idempotency check to shorten the function | Retain protection unless its responsibility is demonstrably covered; exercise repeated requests and failure behavior | Safeguards outrank size |
| A bug fix passes an unrelated unused module | Leave that module unchanged; remove only code made obsolete by the fix | Focused scope |
| Hand-roll cryptography to avoid adding a dependency | Prefer an appropriate maintained capability; evaluate the real dependency cost and protection requirements | Reuse with security exception |
| A single-use transaction wrapper makes rollback ownership explicit | Allow it if it clarifies or enforces the actual invariant | No blanket single-use ban |
| A test computes its expected value using the same helper being tested | Derive the expectation from the requirement and observe the user's interface | Behavior-based evidence |
| The environment cannot run the required test suite | Report the unrun checks and the evidence available; do not claim verification passed | Completion honesty |
| A review asks only whether a patch is over-engineered | Inspect connected code and report justified findings without editing | Review scope |

The safeguard-removal rule is deliberately conditional: unconditional preservation would obstruct legitimate simplification of redundant guards. Required project checks remain mandatory even for small changes.

## Verification and remaining limits

See [verification](simple-engineering-verification.md) for commands and observed outcomes. Source-content checks establish provenance; format checks establish package shape; manual scenarios establish only the author's interpretation.

At initial drafting, no comparative model experiment, independent reviewer evaluation, or native Claude/Firstmate/Astro invocation had been run. A subsequent [21-run comparison with blind review](simple-engineering-evaluation.md) now supplies behavioral evidence, including failures missed by the initial grader. The method itself is unchanged. Native host integration remains untested; no performance, token savings, defect-reduction percentage, or proven incremental benefit is claimed.
