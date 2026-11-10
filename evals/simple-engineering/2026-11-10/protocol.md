# Predeclared evaluation protocol

Frozen before any solver runs. Candidate: simple-engineering v0.1.0, repository commit 922f92269dd5abdff33a9f41a41c24e5048c3a28. Comparator: Ponytail at commit 96608e078b2d5ea607c5c3b8b5a54d1c1fba6846.

Three primary cases, three conditions, two fresh-context repetitions per condition: 18 runs. One independently authored held-out case gets one run per condition after the primary runs: 3 runs. Do not revise the candidate between these runs. A later revision requires a separately recorded evaluation.

Conditions: no additional skill, candidate, original Ponytail. Every solver gets the same task and starting fixture, shared host/model defaults, tools and experiment restrictions. Conditions differ only in whether an additional method file is provided. Baseline still includes the host's unavoidable system/developer guidance; it is not a bare model. Disable discretionary unrelated skills for every condition. No parent conversation, grading criteria, or sibling results are provided. Context separation is instruction-level and fresh-agent, not filesystem access enforcement.

Success: all public tests and all independently run hidden behavioral contract tests pass. Keep each contract test in the report, including those that pass for all conditions; safeguards are not discarded for low discrimination. A full-success count is primary; per-assertion counts are diagnostic, not independent samples. Also record changes to unrelated files, dependency additions, changes to existing public tests, and the tests solvers actually report running. Blind review judges completeness, readability and unnecessary complexity from anonymized artifacts. Diff size alone is not a quality score.

Scope sentinels: csv/legacy_format.py and retry/reporting.py are unrelated to the task. Their existing bytes should remain unchanged unless a solver supplies a concrete task-related reason. API compatibility and failure behavior are observed by graders. Documentation for new planner options receives manual review. Tests that only echo implementation wording do not earn verification credit.

Decision rule: do not claim benefit from a tie, a single favorable example, or self-reported compliance. Critical regressions prevent accepting a proposed revision even if average scores improve. Two repetitions and four small synthetic exercises cannot establish statistical significance or production generalization. Hold-out means the candidate is not modified in response to it; it was authored independently without seeing the candidate, not sampled from production.

Time is observed wall time including scheduling/tool overhead, useful only descriptively. Token usage is unmeasured unless the runtime provides an actual counter. No invented cost estimates. No native Claude, Firstmate, or Astro integration claims follow from same-runtime subagent trials.
