# Source intake, terms and consumer boundaries

Observed 2026-11-11 through read-only `gh-axi api` requests. All ten supplied repositories were inspected; the additional Superpowers authoring URL belongs to the same repository. This table is the **intake observation**, not a second mutable version lock. Active imported versions/checksums are authoritative only in [`upstreams.lock.json`](../upstreams.lock.json).

## Complete supplied intake

| Supplied reference | Observed commit | Terms and decision |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | `b48c832f0f809c1b5658edbb838c2521b72f2413` | **Selected:** Humanizer. MIT in `LICENSE`; preserve its Wikipedia attribution/citations. Useful prose-editing source; no AI-detector or efficacy claim is adopted. |
| [mattpocock/skills/tree/main](https://github.com/mattpocock/skills/tree/main) | `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | **Selected:** canonical `grilling`, MIT in `LICENSE`. Interactive design interviewing adds distinct standalone coverage. `grill-me` is only a Skill-tool forwarding alias and is not imported. **Added 2026-11-12 at the same pin:** `codebase-design` (see [planning and design additions](#planning-and-design-additions)). **Added 2026-11-13 at the same pin:** `implement`, `tdd`, `code-review`, `diagnosing-bugs` (see [helper additions](#original-super-board-helper-additions)). Other engineering orchestration/setup/in-progress catalogues remain deferred. |
| [obra/superpowers](https://github.com/obra/superpowers) | `22f0b463e7a5e579904dd6211a520321035526f7` | **Selected:** systematic debugging, TDD and verification, including their supporting files. MIT in `LICENSE`. These three methods correspond to existing firstmate-config bindings. No plugin, hooks, whole workflow catalogue or automatic “using-superpowers” activation. |
| [cursor/plugins/pstack/skills](https://github.com/cursor/plugins/tree/main/pstack/skills) | `5866df557357d005b3c0c9d3da0d9e739b4bdde3` | **Selected:** `principle-test-behavior-not-implementation`. MIT applies to the **pstack subtree**, copyright Lauren Tan, retained in `pstack/LICENSE`; it is not a blanket license assertion about all Cursor plugins. Other plugin/tool-specific methods are deferred. Repository HEAD advanced from the original intake pin `246bc508c139c5e036dfafea8978d31a7433279f`; selected body/license bytes were unchanged. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `301b02b12bff98e4688e6984af6556802322bbde` | **Selected:** code simplification and measured performance optimization, with both local patterns and the ancestor performance checklist. MIT in `LICENSE`. Covers behavior-preserving refactoring and measurement/caching tradeoffs without importing the entire catalogue. **Added 2026-11-12 at the same pin:** `planning-and-task-breakdown` and its ancestor `references/definition-of-done.md`. Other firstmate-config-owned Addy methods remain with that consumer. |
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

## Planning and design additions

Added 2026-11-12 to cover two stage gaps in the existing eleven methods: **planning/task breakdown** (none present) and **architecture/design discussion or design preparation** (only `grilling`, an interview method, was present). Both come from sources and revisions already pinned; no pin, existing file or existing selection moved. Source-level read-only GitHub API requests at the locked commits supplied the candidate bodies; selection is a source-fit judgment, **not** a model-efficacy result.

| Candidate (at the locked pin) | Decision | Evidence |
|---|---|---|
| Addy `planning-and-task-breakdown` | **Selected (planning)** | Read-only plan mode, dependency graph, vertical slices, per-task acceptance/verification, checkpoints, human plan approval. No mandated sub-skill, commit or execution handoff. Default output files `tasks/plan.md`/`tasks/todo.md` yield to a project/user-designated target. Needs ancestor `references/definition-of-done.md` (added as a distinct dependency resource). |
| Superpowers `writing-plans` | Not selected | Plan header and Execution Handoff require `superpowers:subagent-driven-development`/`executing-plans` and make the user choose an execution method; steps include per-task commits. That would assign implementation ownership the consumer's fixed delivery flow keeps elsewhere, and neither sub-skill is imported. |
| Superpowers `brainstorming` | Not selected | Hard gate ends by invoking `superpowers:writing-plans` "and no other skill"; description claims it MUST run before any creative work; default output is a committed `docs/superpowers/specs/` document; optional visual companion ships a local Node server. Product-discovery oriented rather than structural design. |
| mattpocock `codebase-design` | **Selected (design)** | Module/interface/seam vocabulary, deletion test, dependency categories (`DEEPENING.md`) and an on-request parallel option comparison (`DESIGN-IT-TWICE.md`). Four plain files, no executables, no workflow gate, commit or file output of its own. |
| mattpocock `improve-codebase-architecture` | Not selected | Refactor-opportunity scan that writes an HTML report using CDN assets, opens a browser and depends on `HTML-REPORT.md` and three other skills. |
| pstack `architect` | Not selected | Multi-model `arena` runs against named models from a `pstack-models.mdc` rule, depends on `how`/`why`/`arena` skills, and defaults to implementing after sketching. |
| Addy `spec-driven-development` | Not selected | Brings its own gated SPECIFY→PLAN→TASKS→IMPLEMENT workflow, overlapping the planning method and any consumer's fixed delivery stages; stays consumer-owned. |
| firstmate-config `architecture-review` | Not imported | Original configuration text; the inspected checkout has no license file for it. Not copied, paraphrased or listed as a source here. |

**Limits.** `codebase-design` is a structural-design method, not an architecture-review verdict method: it does not cover data models, failure behavior, migration shape or a decision-record format. `grilling` (already present) supplies the interactive discussion; recording decisions stays with the consumer-owned Addy documentation/ADR binding. Its glossary rules (for example preferring "seam" over "boundary") are upstream wording scoped to that method. Planning and design remain optional stages; selecting or skipping them per task is the consumer's decision.

**Import mode.** `cursor/plugins` `main` had already advanced past its locked pin when these methods were added, so a live `update` would also have moved pstack. The import instead used the updater's own `--offline` interface with read-only API snapshots of the *locked* commits (`commits/main` answered by the locked commit). Every existing source pin and all 29 existing locked files are byte-for-byte unchanged; only the six new files, `manifest_sha256` and the manifest selections changed. A later live `check` still reports pstack's pre-existing drift; that is not part of this addition.

## Original Super Board helper additions

Added 2026-11-13 for the explicitly requested seven-helper set. Five missing skills were imported; two existing canonical entries were reused, not duplicated or aliased. Read-only `gh-axi` repository, immutable commit, recursive tree and Git blob responses independently confirmed public repository identities and file bytes. The independent mixed Claude/Codex test owns its own target and execution; this library change neither runs nor gates that test.

| Required helper | Library decision | Retained source-relative resources |
|---|---|---|
| `implement` | Added from Matt Pocock | `skills/engineering/implement/{SKILL.md,agents/openai.yaml}` |
| `tdd` | Added from Matt Pocock; not an alias of Superpowers TDD | `skills/engineering/tdd/{SKILL.md,tests.md,mocking.md,agents/openai.yaml}` |
| `codebase-design` | Already present, unchanged | `skills/engineering/codebase-design/{SKILL.md,DEEPENING.md,DESIGN-IT-TWICE.md,agents/openai.yaml}` |
| `code-review` | Added from Matt Pocock | `skills/engineering/code-review/{SKILL.md,agents/openai.yaml}` |
| `diagnosing-bugs` | Added from Matt Pocock | `skills/engineering/diagnosing-bugs/{SKILL.md,agents/openai.yaml,scripts/hitl-loop.template.sh}` |
| `testing-strategy` | Added from Anthropic | `engineering/skills/testing-strategy/SKILL.md` |
| `verification-before-completion` | Already present from Superpowers, unchanged | `skills/verification-before-completion/SKILL.md` |

| Public source (numeric repository ID) | Library commit / tree | Observed redistribution terms |
|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) (`1148788086`) | [`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`](https://github.com/mattpocock/skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d) / `a73b182b5f22565e829e0969eb0bfd284508a7b8` | MIT, copyright 2026 Matt Pocock; root `LICENSE` retained unchanged |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (`1140828898`) | [`43ccfc0d22c5dbe2dd7e1b3670a6fbaed4dfe745`](https://github.com/anthropics/knowledge-work-plugins/commit/43ccfc0d22c5dbe2dd7e1b3670a6fbaed4dfe745) / `14d6d4183959ef7d2e6d7e79bb517eda63c937ac` | Apache-2.0 in root `LICENSE`; retain the complete file, including its unusual trailing text. No relevant NOTICE or additional legal file in the selected/ancestor scope |
| [obra/superpowers](https://github.com/obra/superpowers) (`1073224795`) | [`22f0b463e7a5e579904dd6211a520321035526f7`](https://github.com/obra/superpowers/commit/22f0b463e7a5e579904dd6211a520321035526f7) / `8fddc972a73e9af7501442df0e638d8e29842b6b` | MIT, copyright 2025 Jesse Vincent; root `LICENSE` retained unchanged |

**Pin compatibility.** All 15 files in the five selected Matt helper directories, plus `LICENSE`, have identical blob IDs, sizes and modes at the existing library pin and the separate test's `5863806dd4e15c63174bee4e7515a4256792ecfa` pin. Superpowers Verification Before Completion and its license likewise match the test's `bb92a77741419a4ab5f06e711a283343f1ada0c3` pin. No existing pin or file was refreshed. The importer used its existing offline snapshot flow to resolve existing tracking refs at their captured locked revisions, as in the earlier planning/design addition; the new Anthropic source declares its exact commit as its ref. All 35 existing locked files remain unchanged; 13 files were added, yielding 8 sources, 18 skills and 48 files.

**Packaging and permissions.** All imported bodies and resources retain original bytes, paths and Git modes (`100644` for these additions, including the shell template). Root licenses are included once per source; no selected skill declares a separate license header. TDD's Markdown references and the diagnosis template are retained. `agents/openai.yaml` files are inert supporting assets here, not new agent/tool registrations, hooks, plugin activation or permission grants. No imported script was executed. The upstream Implement body asks for a commit and Skill-tool calls; TDD asks for seam confirmation; Code Review asks for setup/delegation. Those words are preserved as source data and remain subordinate to the consumer's actual task and permission policy. Optional/conditional skill mentions do not expand this seven-helper import.

**Verification boundary.** Existing importer behavior and fixture tests need no code/expectation changes: they exercise controlled repositories, not the selected catalog's incidental counts. Run the documented offline suite and `verify` for file/reference/import consistency. These checks establish neither model effectiveness nor native discovery/adoption. No consumer installation, mixed-model call, scheduler or unattended refresh was performed.


## Consumer ownership and binding

### firstmate-config

Read-only evidence: its README “Worker context and skill classes”, `skills/external.lock`, and the complete `scripts/update-ponytail.sh`. Its existing mechanism owns source caches, global shared-skill links and a separate Pi package checkout. Reusing that updater here would write outside this repository; none of it was invoked.

The inspected configuration pins Superpowers to `bb92a77741419a4ab5f06e711a283343f1ada0c3`, Ponytail to `16352ac229eb08a9598dcae48fe9f2b342567d86`, and Addy to `aeac41d4d005999432bb7312f7ff06383a91d59d`. Those are **consumer configuration observations**, not a claim that a live installation was reconciled. This repository's newer source snapshots do not replace those pins.

The imported methods matching configured binding names are systematic-debugging, test-driven-development, verification-before-completion, ponytail, ponytail-review, code-simplification and planning-and-task-breakdown. Existing Addy incremental implementation, context, API design, security, code review, specification, browser testing, frontend and documentation bindings remain consumer-owned and are not wholesale mirrored here. The old config-owned `architecture-review` is not a source here and is not replaced by name; see the limits in [planning and design additions](#planning-and-design-additions).

For later authorized explicit-path use, retain the complete checkout, select the exact entrypoint from the README, and supply that absolute `SKILL.md` path/body plus its original support-file base in the worker handoff. Record the lock commit/file SHA-256. Precedence remains project-native instructions → project-local skills → role/task policy → shared worker skills. Do not assume global discovery or run a consumer installer from this checkout. Grilling needs an interactive session; no task-local skill overrides a worker's delegation/permission boundary.

### TLW

The available local TLW reference is README-only: “Reusable workflow presets and host-native skill bindings.” It contains no executable loader, configuration, source lock or schema to validate. The current owner contract explicitly keeps TLW on **Super Board skills**. No Super Board source/pin is invented, no alternate owner is installed, and current TLW preparation is not gated on this repository. The files here can be considered for a later explicit host-native binding; native TLW loading is **unverified**.

Later, separate from that intake observation and ownership: [`first-party/tlw/SKILL.md`](../first-party/tlw/SKILL.md) is an original, explicit-use handoff for running one authorized job through an already-installed TLW (reviewed against TLW `8566b3b0d39b3fa1bf21d5138b63ea0c0e22297c` only). It copies no TLW text, adds no router or wrapper, and does not migrate TLW's Super Board skills or pins here. This repository does not install or activate it (any host command is external integration, verified where used), and the updater does not manage or validate it. There has been no native trial of `8566b3b…`.

### Astro

Read-only evidence: `internal/skills/skills.go` and `internal/skills/builtin.go`. Astro already embeds Be Ambitious at `dc116a3ebd8cf772e4d0930626f67369bd60399d`; its body SHA-256 is `b180b90b55f1bb3b6100a9558929480197e3c1c68b59de7d96b00f7ca2ec3c5b`. That owner and its source copies remain unchanged.

Astro discovers only immediate skill directories below its fixed native roots, reads frontmatter in the first 8 KiB (name ≤64, description ≤1,024), and copies plain-file folders for runs (≤1 MiB, ≤64 files, depth <6). Its refs use `<root label>/<entry name>`. Merely checking out this repository does not register a root or discover every nested source. `verify` checks the relevant frontmatter bounds and source-relative resources; it does **not** execute Astro's Go loader.

At this candidate, sixteen of eighteen entrypoints have no outside-leaf resource references; their observed folder sizes/counts fit the stated bounds. A later authorized package must still include the applicable license/NOTICE and all supporting files. **Performance Optimization and Planning and task breakdown are not standalone leaf copies:** their `../../references/performance-checklist.md` and `../../references/definition-of-done.md` are retained at `upstream/addyosmani/references/`. Flattening either leaf breaks that reference. Keep full source-aware access or establish a separate consumer-owned packaging adapter before binding them; no speculative adapter is shipped here.

Astro Chat instructions read only `SKILL.md`, whereas a run receives the bounded folder; these are not interchangeable loading claims. Skill runs are read-only. Native discovery/loading, application behavior and agent adherence are **unverified** in this task; no live Astro process or consumer test suite was run.

### Standalone use

Use an explicit entrypoint with the full retained source context in a capable agent session. These are upstream methods, not permission grants. Read source-specific prerequisites and session/mode wording before binding. No default global loading, paid calls, software installation or expanded task scope follows from selection.

## What verification means

`python3 scripts/update_upstreams.py verify` checks the manifest/lock relationship, source file identities/modes, conventional name/description bounds and retained source-relative file references. The offline suite exercises actual import/update/first-party preservation and failure behavior in isolated temporary directories. An online `check` resolves public upstream identities read-only.

Those results establish repository/update mechanics, **not skill success, native consumer adoption, stylistic quality, AI-detector accuracy or model benefit**. The superseded original candidates' failed comparisons remain failed in private evidence. The only first-party skill is `first-party/tlw`, which the updater and `verify` do not read; its current revision has had no native trial (see the TLW section), and there have been no model evaluations of the upstream reorganization.
