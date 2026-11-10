# simple-engineering 0.1.0 — comparative evaluation

Date: 2026-11-10. Status: evaluated discussion draft; incremental benefit not demonstrated.

## Verdict

Keep the skill as an unproven candidate, not a final or proven improvement. The candidate, the no-additional-skill baseline, and original Ponytail all passed the predeclared checks in seven runs each. Blind review subsequently found CSV boundary problems in every condition. The candidate did not consistently prevent them, and the other cases produced no material qualitative winner.

The skill text remains unchanged. Adding another universal rule would require evidence that the revision improves fresh task outcomes; the present experiment does not establish that. The supported improvement from this round is a stronger, reproducible evaluation and a more accurate assessment of the draft.

## Design fixed before solving

- Candidate: repository commit `922f92269dd5abdff33a9f41a41c24e5048c3a28`; skill SHA-256 `3f79befb9ec8d1c6bb54576324ed37d58c17ca3ea02d426c3bb2ab316d7a8026`.
- Comparator: original Ponytail at upstream commit `96608e078b2d5ea607c5c3b8b5a54d1c1fba6846`; snapshot SHA-256 `9badd22a32e19cb884e46dfa8d3aae82bb81dfa5484105b8b4f0262df823a509`.
- Three primary coding tasks × three conditions × two fresh-agent repetitions = 18 runs. One independently authored held-out task × three conditions = 3 additional runs. Total: 21 model task runs.
- Every run received the same starting project and task within its case. Only the additional method differed. Solvers inherited the same parent model/effort configuration through the Codex collaboration runtime; exact model identifier and inference settings were not independently exposed or pinned.
- New agents started without the parent chat. Requests prohibited reading sibling outputs/graders and loading other discretionary skills. Those boundaries were instructions, not separate filesystem sandboxes. Unavoidable host system/developer guidance remained in every condition, including baseline.
- The candidate, tasks, and predeclared graders remained frozen throughout. The held-out author did not see the candidate. Small scheduling deviation: two held-out solvers started shortly before the final primary solver returned; no results or revisions were supplied to them.

These are realistic small synthetic fixtures, not the real TLW codebase or production tasks. They have explicit specifications and may be easier than ambiguous real work. Two repetitions do not support significance claims or reliable failure-rate estimates.

## Initial results

Success here means the submitted implementation passed its public suite and all predeclared external behavioral contract tests. It does not mean every possible behavior is correct.

| Task | No additional skill | simple-engineering | Original Ponytail |
| --- | --- | --- | --- |
| Assistant options, CLI/config precedence, invalid-selection errors | 2/2 | 2/2 | 2/2 |
| Shared CSV parser, preview/import, validation and rejected-upload behavior | 2/2 | 2/2 | 2/2 |
| Zero/default retries, pre-call negative rejection, exception propagation | 2/2 | 2/2 | 2/2 |
| Independent JSONL extension, privacy, field selection, limits and file protections | 1/1 | 1/1 | 1/1 |
| Total runs passing predeclared checks | **7/7** | **7/7** | **7/7** |

No run changed the unrelated CSV/retry sentinel modules. All implementations used the standard library. Test quantity and diff size were not scored as proxies for quality.

Independent reviewers received only task text, starting files, and anonymized patches, with no method identities or prior grades. Providers, retries, and the held-out export task were qualitative ties. The CSV review found the following gaps, subsequently confirmed by execution.

## Post-hoc CSV diagnostics

Two input distinctions were absent from the initial grader:

1. A quoted single-field whitespace record such as `" "` is valid CSV syntax but not a two-column inventory row. Four solutions skip it instead of rejecting the malformed inventory upload. An independent importer diagnostic directly confirms that those outputs change stock despite the invalid upload. This conflicts with the explicit two-column validation and rejected-upload contracts.
2. An unquoted whitespace-only physical line was skipped by the original parser. Two solutions now reject it. This is a verified compatibility difference, although the prompt's wording about blank rows is less explicit than the two-column requirement.

The original fixture passes both added diagnostics. Each solved CSV implementation fails at least one. The extra tests were applied to the already frozen outputs; they were not new agent runs and were not retroactively inserted into the original grading totals.

| Additional diagnostic: CSV runs passing | No additional skill | simple-engineering | Original Ponytail |
| --- | --- | --- | --- |
| Reject quoted malformed single-field whitespace rows | 0/2 | 1/2 | 1/2 |
| Preserve whitespace-only physical-line compatibility | 2/2 | 1/2 | 1/2 |
| Satisfy both diagnostics together | **0/2** | **0/2** | **0/2** |

The candidate's isolated favorable result on malformed input is inconsistent across its two runs and accompanied by the compatibility loss. It is not evidence of a reliable overall advantage. These findings demonstrate why passing our own first test set was insufficient to call the skill validated for effectiveness.

## Authoring audit

The pinned [skill-creator-plus validator](https://github.com/robonuggets/skill-creator-plus/blob/13446e8bb45c2d656c393ecf0948c9b2379296ad/scripts/validate_skill.py) ran on the complete skill folder: **0 errors, 0 warnings, 1 note**. The note identifies the dated source-review marker in `references/sources.md`; it records provenance rather than a time-dependent behavioral rule, so it stays. The fetched validator's Git blob matched `4c19cd287ab1a10a76de92537630b33bf167a2a3`. The existing skill-creator format check also passed before this evaluation.

Manual judgment checks distinguish mechanical validity from suitability:

| Area | Assessment |
| --- | --- |
| Purpose and scope | A bounded simplicity/completeness method; no orchestrator selection or installation behavior |
| Self-contained packaging | Local source reference resolves; no sibling skill or external executable is required |
| Proportional guidance | Preserves explicit options and safeguards; allows justified abstractions and dependencies |
| Concision / incremental value | The 665-word method adds instructions to an already capable baseline; no reliable benefit was shown here |
| Evaluation chronology | Initial draft preceded behavioral tests. This was retrospective evaluation of a frozen draft, not a tests-first creation process |
| Actual execution | Fresh assigned-method trials and external graders ran; the earlier ten author walkthroughs remain a separate, weaker evidence class |
| Discovery and target hosts | Automatic triggering and native Claude/Firstmate/Astro invocation remain untested |
| Claude-specific checklist items | Hook enforcement, model-specific advice and session-mode metadata were not imposed on this portable method |

The [Agent Skills evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) supplied the controlled-baseline, output-grading and blind-review approach. [Superpowers writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) informed observing failures and revisiting assumptions before adding guidance. Its forced deletion of an already-written draft and rule-compliance-only scoring were not adopted. No claim is made that all workflows from these sources were followed unchanged.

## Evidence and limits

The [evidence package](../evals/simple-engineering/2026-11-10/README.md) contains task fixtures, method snapshots, patches, grading outputs, anonymized review inputs, reports, and separate diagnostic results. `replay.py` rebuilds the recorded submissions in temporary directories and reruns the checks. Replaying outputs is not rerunning the models.

A separate methodology reviewer verified the original frozen/package hashes, replayed all 21 initial outputs, and checked reconstructed file hashes. It found no blocking issue for the narrow conclusion. Its two archival/scheduling follow-ups are addressed by retaining the dispatch requests, input manifests, held-out control logs and solver-reported check summaries, and disclosing the overlap above. Full solver tool transcripts and comparable timing remain unavailable. Its CSV addendum distinguishes the explicit validation defect from the less explicit compatibility observation and confirms the independently executed stock-mutation probe.

Final package validation also ran from the repository copy: all 42 public/contract replay steps passed, all six expected post-hoc CSV failures reproduced with exit status 1, all 93 evidence-file hashes matched, and all 15 relative Markdown links resolved. Literal patch and blinded-input whitespace is preserved as evidence; it is validated by replay rather than normalized as prose.

No comparable solver wall-time or token counters were exposed and captured; those fields are null. No cost, speedup, or token-saving claim is made. Exact model identity, full solver tool transcripts, and enforced context isolation were not captured, so the package cannot prove every solver's method-reading or verification practices. Runtime grading is independently observed, rather than taken from solver reports.

The initial suites and the additional diagnostics are coverage evidence only. Native host integration, wider language/framework coverage, production generalization, and a causal improvement over the baseline remain unproven. Further refinement should target an observed failure and be assessed against a frozen old version plus fresh tasks; it should not be accepted merely for producing a more detailed instruction file.
