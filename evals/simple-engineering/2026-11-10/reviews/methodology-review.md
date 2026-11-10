# Methodology and replay review

Verdict: no blocking findings for the claim that these small, same-runtime synthetic trials demonstrated no incremental correctness advantage from the candidate. This is a tie on the specified checks, not evidence of universal equivalence, production effectiveness, or native Claude/Firstmate/Astro compatibility.

## Evidence checked

- Read the protocol, schedule and request wrappers, frozen manifests, run preparation, collector, packaging and replay code, all three primary prompts/fixtures/graders, and the held-out prompt, fixture, rubric and grader. Did not read the blind-review directories or codebooks.
- Verified all 22 primary frozen-input hashes, all 8 held-out input hashes, and all 75 packaged-file hashes. No mismatches. Every supplied candidate/comparator method copy matches its frozen source.
- Executed `python3 -B package/replay.py` from the evaluation root. All 21 runs passed both public and contract checks; the command exited zero.
- Independently reconstructed every patch and checked each changed file against its recorded final SHA-256. All matched. The recorded changed paths contain no added dependencies or unrelated sentinel changes. No patch removes existing test definitions or assertion lines.
- Primary baseline validation demonstrates that the original fixtures fail task-specific contract checks while passing their existing public tests. Held-out validation records the analogous negative control and a passing temporary positive control.

The graders check observable requirements from the prompts and fixtures rather than demanding a preferred decomposition, helper count, diff size, or skill vocabulary. No material arm-specific grading rule or unsupported behavioral requirement was found. Unchanged safeguards remain in the test results, as the protocol requires. Public tests include solver additions, so their differing counts must not be treated as comparable independent outcome samples; the shared contract checks and run-level full-success indicator are the appropriate comparison.

## Ranked nonblocking follow-ups

1. **Preserve the distinction between output replay and inference/process provenance.** The package contains the fixtures, methods, patches and detailed grader outputs needed to reproduce these observed correctness outcomes. It does not include the complete dispatch schedule/request wrappers, frozen-input manifests, held-out validation records, or solvers' completion reports. In particular, the collector records the commands the evaluator ran, not the commands solvers reported running, despite the protocol requesting the latter. Preserve those existing records alongside the report if verification practices or protocol execution are discussed. This is an archival/process-evidence gap, not a reason to reject the replayed correctness tie. Do not infer model effort or verification behavior from the grader logs.

2. **Record the small dispatch-order deviation.** The protocol says held-out runs occur after the primary runs. The supplied audit context states that two held-out solvers were dispatched just before the last primary solver returned, with no feedback or candidate changes. Disclose this in the methods account. Given the frozen candidate, independent held-out authorship, fresh solver contexts and absence of feedback, this overlap does not undermine the stated correctness conclusion. Dispatch timing itself cannot be independently reconstructed from the packaged metadata.

## Explicit limits, not defects

- Eighteen primary runs comprise only three cases with two repetitions per arm; the three held-out runs add one independently authored synthetic case with one repetition per arm. All arms reaching the ceiling supports “no advantage demonstrated on these checks,” not equivalence or statistical significance.
- Fresh-agent, instruction-level separation is not enforced filesystem isolation. The shared host guidance also means the baseline is not an unprompted model. These limitations are disclosed in the protocol; the available artifacts cannot independently prove the absence of every possible context leak.
- The archive reproduces recorded output behavior, not stochastic model inference or exact runtime/model conditions. Token usage and solver durations are null for all runs; no speed, cost or effort advantage can be established from these records.
- Finite contract checks do not prove every possible input correct. No additional production benchmark or test framework is necessary to substantiate the narrow observed-result claim.
- This review does not validate the separate blind-review judgments or their anonymization because those artifacts were deliberately excluded from scope.

## Addendum: post hoc CSV boundary diagnostics

Reviewed `posthoc_csv_grader.py`, `posthoc-csv-results.json`, and `posthoc-csv-observations.json`. These are fair, implementation-independent diagnostic probes applied to the original fixture and all six existing CSV outputs. They are post hoc checks discovered after reviewing the outputs, not additional model runs or amendments to the frozen success criterion. The original 21 predeclared passes remain unchanged.

The findings have different evidentiary strength:

- **Explicit contract defect:** r04 (baseline), r05 (candidate), r13 (Ponytail), and r14 (baseline) silently accept a quoted single-space record with only one field. That record is valid CSV syntax but invalid inventory data: the documented contract requires two fields and a nonblank name. Calling it a “malformed inventory row” is more precise than “malformed CSV quoting.” The original fixture rejects it. These four outputs therefore have a concrete correctness defect missed by the predeclared checks.
- **Compatibility regression with weaker task wording:** r06 (Ponytail) and r15 (candidate) reject unquoted whitespace-only physical lines that the original fixture skips. The original implementation establishes the previous behavior; the prompt's permission to skip blank rows does not define whitespace-only lines as clearly. Report this separately as a compatibility observation, not as equally unambiguous failure of an explicit new requirement.

Thus “all six CSV outputs fail at least one post hoc diagnostic” is supported. “All six violate the explicit two-column contract” is not. Neither this selected pair of post hoc checks nor the small per-arm counts establish comparative skill superiority. They narrow the meaning of the original tie to correctness on the predeclared checks and reinforce that passing those checks did not establish complete correctness.

**Reporting caution resolved:** the diagnostics now include `test_malformed_upload_keeps_stock_unchanged_independently`, which invokes the importer in a separate test regardless of the parser test outcome. Re-executing the updated diagnostics on the original fixture and all six existing outputs confirms that r04, r05, r13 and r14 change stock from `{'old': 9}` to `{'old': 9, 'apple': 2}` for the malformed inventory upload. Stock mutation is therefore directly observed, not inferred from the parser failure. The original fixture passes all three diagnostic methods; r06 and r15 pass the independent malformed-upload test and fail only the whitespace compatibility probe. The packaged diagnostic grader and results match their source records. This remains post hoc testing of existing outputs, with no new model runs or change to the 21 predeclared passes. The third method independently checks the consequence of the same malformed-row defect; it is not a third independent defect or statistical sample.
