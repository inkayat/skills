---
name: simpfy
description: Apply the smallest complete, behavior-preserving simplification to the selected code or text. Use when asked to simplify, trim, clean up or cut the extra from a target; edits the target, not advice only, unless the user asks for analysis only.
---

# simpfy

Make the selected target simpler without changing what it does, then apply the
change. Invoking this skill authorizes the simplification within the authority
you already have for the target. It grants no new permissions and is not a
standing mode.

## Steps

1. **Read first.** Read the target, its direct callers or readers, and the
   contracts around it (tests, docs, public interfaces, project conventions).
2. **Name what is extra**, briefly and concretely: dead code, a needless layer,
   a duplicate, a long way round. For text: repetition, filler, structure that
   hides the point.
3. **Pick the smallest complete simplification** and apply it. Complete means
   every caller, reference and test that the change touches is updated, so
   nothing is left half-done. Prefer deleting over adding.
4. **Verify** with the existing checks that cover what you changed: the
   relevant tests, type check, build or linter for code; a read-through against
   the original meaning for text. Do not run broader suites than the change
   needs, and do not invent checks for prose.
5. **Report** in a few lines: what was extra, what you changed, which
   verification you actually ran and its result, and what you could not check.

## Preserve

Behavior, data, error handling, security, and accessible or user-visible
contracts, including the meaning, facts and tone of text. Follow the project's
existing conventions and stay inside the scope the user named.

## Do not

- Rewrite the target wholesale, or change things the user did not point at.
- Add an abstraction, dependency, option or feature.
- Change a public API, delete unlanded work, or take a destructive action
  without actual authority to do so.
- Ask for approval on routine, harmless steps.

## When to ask or stop

- Ask only when the target or the intended behavior is genuinely ambiguous, or
  a change crosses a consequential authority boundary (public API, data loss,
  shared or released contracts). Ask one short question and wait.
- If no safe, useful simplification exists, say so and leave the target
  unchanged. Do not manufacture work.
- If the user asks for analysis only, a plan or a proposal, give that and do
  not edit.
