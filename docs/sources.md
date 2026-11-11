# Source intake, terms and consumer boundaries

Observed 2026-11-11 through read-only `gh-axi api` requests. All ten supplied repositories were inspected; the additional Superpowers authoring URL belongs to the same repository. This table is the **intake observation**, not a second mutable version lock. Active imported versions/checksums are authoritative only in [`upstreams.lock.json`](../upstreams.lock.json).

## Complete supplied intake

| Supplied reference | Observed commit | Terms and decision |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | `b48c832f0f809c1b5658edbb838c2521b72f2413` | **Selected:** Humanizer. MIT in `LICENSE`; preserve its Wikipedia attribution/citations. Useful prose-editing source; no AI-detector or efficacy claim is adopted. |
| [mattpocock/skills/tree/main](https://github.com/mattpocock/skills/tree/main) | `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | **Selected:** canonical `grilling`, MIT in `LICENSE`. Interactive design interviewing adds distinct standalone coverage. `grill-me` is only a Skill-tool forwarding alias and is not imported. Engineering orchestration/setup/in-progress catalogues are deferred, not cloned. |
| [obra/superpowers](https://github.com/obra/superpowers) | `22f0b463e7a5e579904dd6211a520321035526f7` | **Selected:** systematic debugging, TDD and verification, including their supporting files. MIT in `LICENSE`. These three methods correspond to existing firstmate-config bindings. No plugin, hooks, whole workflow catalogue or automatic “using-superpowers” activation. |
| [cursor/plugins/pstack/skills](https://github.com/cursor/plugins/tree/main/pstack/skills) | `5866df557357d005b3c0c9d3da0d9e739b4bdde3` | **Selected:** `principle-test-behavior-not-implementation`. MIT applies to the **pstack subtree**, copyright Lauren Tan, retained in `pstack/LICENSE`; it is not a blanket license assertion about all Cursor plugins. Other plugin/tool-specific methods are deferred. Repository HEAD advanced from the original intake pin `246bc508c139c5e036dfafea8978d31a7433279f`; selected body/license bytes were unchanged. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `301b02b12bff98e4688e6984af6556802322bbde` | **Selected:** code simplification and measured performance optimization, with both local patterns and the ancestor performance checklist. MIT in `LICENSE`. Covers behavior-preserving refactoring and measurement/caching tradeoffs without importing the entire catalogue. Other firstmate-config-owned Addy methods remain with that consumer. |
| [robonuggets/be-ambitious](https://github.com/robonuggets/be-ambitious) | `dc116a3ebd8cf772e4d0930626f67369bd60399d` | **Selected:** explicit ambition/outcome reframing, MIT in `LICENSE`, copyright RoboNuggets. Keep the Felix Rieseberg article attribution, README and referenced banner. Astro already owns a built-in at this revision; this repository does not update it. No default expansion of task permissions. |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | `2c606141936f1eeef17fa3043a72095b4765b9c2` | **Excluded from redistribution:** frontmatter says MIT, but the inspected tree has no complete license/copyright grant. Exact constraint retained; no body or paraphrased substitute is distributed. Safe alternative: the separately licensed Ponytail/Code Simplification sources already selected for the same broad simplicity need. |
| [DietrichGebert/ponytail/tree/main](https://github.com/DietrichGebert/ponytail/tree/main) | `96608e078b2d5ea607c5c3b8b5a54d1c1fba6846` | **Selected:** `ponytail` and `ponytail-review`, MIT in `LICENSE`. Both correspond to firstmate-config bindings. No Pi extension, mode/settings reconciliation, installer, alternative runtime copies or unrelated audit/debt/gain catalogue. Session-level wording remains upstream wording; consumer/task policy still has precedence. |
| [robonuggets/skill-creator-plus](https://github.com/robonuggets/skill-creator-plus) | `13446e8bb45c2d656c393ecf0948c9b2379296ad` | **Deferred, linked authoring reference:** observed MIT in `LICENSE`. Do not import another overlapping authoring/scaffolding toolchain merely because it was a research reference. Future first-party authoring can consult its pinned method under a separate task; no scripts or content copied here. |
| [Superpowers writing-skills](https://github.com/obra/superpowers/tree/main/skills/writing-skills) | `22f0b463e7a5e579904dd6211a520321035526f7` | **Deferred as a package:** repository MIT is observed, but the required package includes `references/anthropic-best-practices.md`, a 1,150-line republication of Anthropic documentation. A separate grant for that republished material was not established here. Keep the upstream [authoring method](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/writing-skills/SKILL.md) and [original Anthropic guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) linked, rather than distribute an incomplete package or assume its third-party terms. This is a conservative scope decision, not a finding of infringement. |
| [Agent Skills evaluating-skills](https://agentskills.io/skill-creation/evaluating-skills), source [agentskills/agentskills](https://github.com/agentskills/agentskills) | `83021e2be457a9b6679148719c1f6074f0ad975e` | **Linked documentation, not a distributable skill:** `docs/LICENSE` is CC-BY-4.0; repository code has separate Apache-2.0 terms. No documentation text/code or evaluation platform is copied into this candidate. No blanket MIT assertion or new evaluation activation. |

License facts are observed terms, **not a legal opinion or independent copyright clearance**. Each selected source's full license/copyright notice is included unchanged. No additional NOTICE was present in the selected scope at these pins. The updater detects declared legal-file/header changes and relevant new legal files rather than silently accepting them. Attribution embedded in source bodies remains intact.

The three original input files were snapshotted privately before edits and never modified:

| Input | SHA-256 |
|---|---|
| `Humanizer.md` | `bd67e13a00567fc0cf2b0ecca50bfb027b317652dce21f766ebb7badc25eb403` |
| `Other Skills.md` | `9a5b9f2e1b77766a442ba6eb7d2a30cbee204674a6c70d534292e84efc8d6589` |
| `Simplicity & Best Practices.md` | `bb787ab5e2c05943bcd864a735194cac2f880d2f7e6e72f35c32cd24ec0566be` |

## Consumer ownership and binding

### firstmate-config

Read-only evidence: its README “Worker context and skill classes”, `skills/external.lock`, and the complete `scripts/update-ponytail.sh`. Its existing mechanism owns source caches, global shared-skill links and a separate Pi package checkout. Reusing that updater here would write outside this repository; none of it was invoked.

The inspected configuration pins Superpowers to `bb92a77741419a4ab5f06e711a283343f1ada0c3`, Ponytail to `16352ac229eb08a9598dcae48fe9f2b342567d86`, and Addy to `aeac41d4d005999432bb7312f7ff06383a91d59d`. Those are **consumer configuration observations**, not a claim that a live installation was reconciled. This repository's newer source snapshots do not replace those pins.

The imported methods matching configured binding names are systematic-debugging, test-driven-development, verification-before-completion, ponytail, ponytail-review and code-simplification. Existing Addy planning, incremental implementation, context, API design, security, code review, specification, browser testing, frontend and documentation bindings remain consumer-owned and are not wholesale mirrored here.

For later authorized explicit-path use, retain the complete checkout, select the exact entrypoint from the README, and supply that absolute `SKILL.md` path/body plus its original support-file base in the worker handoff. Record the lock commit/file SHA-256. Precedence remains project-native instructions → project-local skills → role/task policy → shared worker skills. Do not assume global discovery or run a consumer installer from this checkout. Grilling needs an interactive session; no task-local skill overrides a worker's delegation/permission boundary.

### TLW

The available local TLW reference is README-only: “Reusable workflow presets and host-native skill bindings.” It contains no executable loader, configuration, source lock or schema to validate. The current owner contract explicitly keeps TLW on **Super Board skills**. No Super Board source/pin is invented, no alternate owner is installed, and current TLW preparation is not gated on this repository. The files here can be considered for a later explicit host-native binding; native TLW loading is **unverified**.

### Astro

Read-only evidence: `internal/skills/skills.go` and `internal/skills/builtin.go`. Astro already embeds Be Ambitious at `dc116a3ebd8cf772e4d0930626f67369bd60399d`; its body SHA-256 is `b180b90b55f1bb3b6100a9558929480197e3c1c68b59de7d96b00f7ca2ec3c5b`. That owner and its source copies remain unchanged.

Astro discovers only immediate skill directories below its fixed native roots, reads frontmatter in the first 8 KiB (name ≤64, description ≤1,024), and copies plain-file folders for runs (≤1 MiB, ≤64 files, depth <6). Its refs use `<root label>/<entry name>`. Merely checking out this repository does not register a root or discover every nested source. `verify` checks the relevant frontmatter bounds and source-relative resources; it does **not** execute Astro's Go loader.

At this candidate, ten entrypoints have no outside-leaf resource references; their observed folder sizes/counts fit the stated bounds. A later authorized package must still include the applicable license/NOTICE and all supporting files. **Performance Optimization is not a standalone leaf copy:** its `../../references/performance-checklist.md` is retained at `upstream/addyosmani/references/performance-checklist.md`. Flattening the leaf breaks that reference. Keep full source-aware access or establish a separate consumer-owned packaging adapter before binding it; no speculative adapter is shipped here.

Astro Chat instructions read only `SKILL.md`, whereas a run receives the bounded folder; these are not interchangeable loading claims. Skill runs are read-only. Native discovery/loading, application behavior and agent adherence are **unverified** in this task; no live Astro process or consumer test suite was run.

### Standalone use

Use an explicit entrypoint with the full retained source context in a capable agent session. These are upstream methods, not permission grants. Read source-specific prerequisites and session/mode wording before binding. No default global loading, paid calls, software installation or expanded task scope follows from selection.

## What verification means

`python3 scripts/update_upstreams.py verify` checks the manifest/lock relationship, source file identities/modes, conventional name/description bounds and retained source-relative file references. The offline suite exercises actual import/update/first-party preservation and failure behavior in isolated temporary directories. An online `check` resolves public upstream identities read-only.

Those results establish repository/update mechanics, **not skill success, native consumer adoption, stylistic quality, AI-detector accuracy or model benefit**. The superseded original candidates' failed comparisons remain failed in private evidence. There are no active first-party skills or new model evaluations in this reorganization.
