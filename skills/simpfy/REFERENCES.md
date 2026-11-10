# simpfy: references and decisions

Human-readable record of where `SKILL.md` comes from and what was decided. It is
not loaded at runtime; the runtime prompt is `SKILL.md` only.

Terms used below:

- **Adopted**: the idea is in `SKILL.md`.
- **Not adopted**: read and decided against, with the reason.
- **Deferred**: out of scope for this skill; may belong to a later skill.
- **Unreviewed**: not read for this skill; no decision exists, and none is implied.

## Actual sources of the text

`SKILL.md` is original text. It was written from the two sources below, not copied
from any upstream.

### 1. Astro `simpfy` starter (origin)

Astro repository `internal/skills/starters.go`, lines 88-98, commit
`a3daac53221f0906166d4fe252e274ff23215731` (read-only; Astro is unchanged).
Description: "Propose the smallest simplification of the selected code or text."

| Starter point | Decision | Why it matters / how adapted |
|---|---|---|
| Name what is extra: dead code, needless layer, duplicate, long way round | Adopted (step 2), plus an equivalent for text | This is the core of the skill: say concretely what is unnecessary before changing it. |
| Smallest simplification that pays, with the exact change | Adopted, adapted (step 3) | "Propose" became "apply" (see source 2). "One" became "smallest complete", because a change that leaves callers or references stale is not a simplification. |
| Say how to check behavior stays the same | Adopted, adapted (step 4) | The check is now run, not described, and its result is reported. Prose targets get a read-through, not compile tests. |
| Do not rewrite the whole thing or add anything new | Adopted (Do not) | Keeps the change small and reviewable; also covers abstractions, dependencies and features. |

### 2. The user's answer: apply, not only propose

User answer, verbatim: "sadece oneri degil uygulasinda" ("not only a proposal;
apply it"). This changed the skill's capability from advise to edit.

Rules not in the starter were specified in the task brief for this skill, which
builds on that answer, and are bounded by it:

- Invocation authorizes the edit only within authority the caller already has; no
  new permissions, no standing mode (intro paragraph).
- Read target, direct callers and contracts first (step 1), because editing without
  that can break behavior.
- Preserve behavior, data, errors, security, accessible and user-visible contracts
  (Preserve), and no public-API change, destructive action or deletion of unlanded
  work without authority (Do not).
- Ask only on genuine ambiguity or a consequential authority boundary; do not ask
  routine approval (When to ask or stop).
- If nothing safe and useful exists, say so and change nothing.
- Analysis-only requests still win, so the user can get the old behavior.

Only the apply answer is the user's own wording. The finer rules above come from
the task brief, and the exact text is the author's.

## Public references read for this record

Read-only, public, via the GitHub API at the pinned commits below. Nothing was
installed, run, cloned or configured. Raw snapshots are kept privately by the
task, not in this repository. Both repositories were named by the user in a
reference note ("Simplicity & Best Practices"); that note is only a pointer, not a
statement of what to adopt.

No upstream text was copied or vendored into `SKILL.md`. During authoring, ponytail
was used by the author as a working method, which is why some ideas overlap; that
overlap is not a claim of derivation. Neither upstream is a dependency or a shipped
provenance of this skill.

### ponytail (DietrichGebert/ponytail)

Pin `96608e078b2d5ea607c5c3b8b5a54d1c1fba6846`. License: a root `LICENSE` file is
present (MIT, "Copyright (c) 2026 DietrichGebert"); the README also says MIT, and
`skills/ponytail/SKILL.md` frontmatter says `license: MIT`. Read: `SKILL.md`, README
(how it works, review and audit sections, band, license), `LICENSE`, root tree.

| Upstream point | Decision | Reason |
|---|---|---|
| Read the code the change touches, list callers/tests/config the change must reach | Overlaps with step 1 and "complete" in step 3; independently reasoned | Importance: a simplification that skips callers breaks them. Not copied. |
| "Never cut" list: validation, data-loss handling, security, accessibility | Overlaps with Preserve | Same safety intent. Wording is original. |
| End the reply with what was skipped or not checked, plus risks | Overlaps with step 5 ("what you could not check") | Honest limits matter more than a tidy summary. |
| Six-rung ladder (exists? already in codebase? stdlib? dependency? one line? minimum) | Not adopted | It is for choosing how to write new code. simpfy edits existing code, where the question is what to remove. Adding it would grow the prompt without changing behavior. |
| "Active for the whole session" mode | Not adopted | The user asked for a skill that does one scoped job when invoked. A standing mode is a different feature. |
| Levels lite / full / ultra, `/ponytail` switching | Not adopted | Configuration nobody asked for. |
| "Ultra" challenges the request itself | Not adopted | simpfy simplifies the named target; it does not renegotiate the request. It asks only on real ambiguity. |
| One small test for new logic; `shortcut:` comment format | Not adopted | simpfy adds no new logic and relies on existing checks. The comment format is ponytail's convention, not this repo's. |
| Plugin machinery: hooks, band/board, per-agent installers | Not adopted | Runtime framework outside a single prompt. The README describes a local ledger at `~/.config/ponytail/band/`; I did not review the hook code itself. |
| `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help` | Unreviewed here (README descriptions of review and audit only) | Review and audit belong to a later `review` skill decision; the others have no read. No verdict. |

Pin note: the earlier inventory recorded pin `96608e0`; the local working copy used
by the author is at a newer commit. At the pin, `skills/ponytail/SKILL.md` has the
same text as that copy except for a trailing newline.

### andrej-karpathy-skills (multica-ai)

Pin `2c606141936f1eeef17fa3043a72095b4765b9c2` (2026-04-20). Read: `skills/karpathy-guidelines/SKILL.md`,
README, `.claude-plugin/plugin.json`, root tree.

License status: MIT is declared in three places (README "License: MIT",
`plugin.json`, and `SKILL.md` frontmatter `license: MIT`). **No `LICENSE` file exists
in the tree at this pin.** That is an evidence gap, not a rejection and not proof
that reuse is allowed. It does not matter for this skill because no text was
copied; it would matter before any future copy.

| Upstream point | Decision | Reason |
|---|---|---|
| 2. Simplicity First: minimum code, no speculative features, no single-use abstractions | Consistent with Do not (no abstraction, dependency, option, feature) | The direction matches; independently stated. |
| 3. Surgical Changes: touch only what you must; match existing style; remove only orphans your change created | Consistent with Preserve ("follow the project's conventions, stay inside the scope the user named") | Importance: keeps diffs reviewable. |
| 3. "Mention unrelated dead code, don't delete it" | Consistent with "stay inside the scope the user named"; not stated as a rule, and differs inside the target | Inside the named target, removing dead code is the job. Outside it, scope applies. SKILL.md does not tell the agent to mention such code. |
| 1. Think Before Coding: state assumptions; if uncertain, stop and ask | Adapted, narrowed | simpfy asks only on genuine ambiguity or a consequential authority boundary. The user wanted application, not a question for each harmless change. |
| 4. Goal-Driven Execution: write tests first, plan with a verify check per step | Not adopted | simpfy verifies with existing checks and does not write new tests or plans for a small edit. Test-first belongs to a later `fix` or `test` skill. |
| Always-on guidance file (CLAUDE.md, Cursor rule) | Not adopted | Same reason as ponytail's session mode. |
| `EXAMPLES.md`, `CURSOR.md`, translations | Unreviewed | Not read; no decision. |

## Alternatives considered for the skill's shape

Origin: the earlier inventory listed three options.

| Option | Decision | Reason |
|---|---|---|
| A: own short `simpfy`, ponytail optional and separate, proposal-only | Superseded in part | Own short text and separation from ponytail kept; "proposal-only" replaced by the user's apply answer. |
| B: merge ponytail's ladder into `simpfy` | Not adopted | Detaches the text from upstream and enlarges the prompt; the ladder is not needed for this job. |
| C: ponytail replaces `simpfy` | Not adopted | Loses the user's name and scope and adds an always-on mode. |

## Unreviewed or deferred for later skills

- Other simplification-related skills named in the inventory (`code-simplification`
  from addyosmani/agent-skills; `principle-subtract-before-you-add`,
  `principle-laziness-protocol`, `no-comments` from pstack) were not read for this
  skill. Unreviewed; no verdict.
- Review-style checks (bugs, security, load) and test-first workflows are deferred to
  later skills of their own.

## Limits

- This record documents decisions; it does not show that a model follows the prompt.
  The runtime behavior of `SKILL.md` has been checked only by static reading.
- The spelling `simpfy` is the user's and is kept on purpose.
