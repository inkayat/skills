# simple-engineering evaluation — 2026-11-10

This package contains synthetic tasks, frozen method snapshots, recorded coding outputs, graders, and independent review evidence. It is development evidence, not an installed skill or a model runner.

Read the [evaluation report](../../../docs/simple-engineering-evaluation.md) for the verdict and limitations. [protocol.md](protocol.md) records the rules fixed before the coding runs. [runs.json](runs.json) maps all 21 runs to their conditions and records the initial grading results. Snapshot files use `.txt` so they do not become duplicate discoverable skills.

## Reproduce the recorded behavior

Requirements: Python 3 with its standard library, and Git. No model, credentials, network, or installed skill is required. From this directory:

```sh
python3 replay.py
```

This reconstructs each submitted implementation from its initial fixture and saved patch in a temporary directory, then runs its public tests and predeclared contract tests. All 21 recorded implementations passed those checks. This is replay of outputs, not a new agent evaluation or proof of the original generation process.

To reproduce the CSV problems discovered later by blind review:

```sh
python3 replay.py --posthoc r04 r05 r06 r13 r14 r15
```

**Expected exit status: 1.** Every CSV implementation fails at least one additional diagnostic. The predeclared results remain unchanged; these checks were added after inspecting the outputs. The original fixture passes these compatibility/validation diagnostics but fails the initially requested quoted-field feature, so it is not a solution either.

## Contents

- `cases/`: original task prompts, input projects, and predeclared graders. The independent held-out case also includes its author's rubric.
- `methods/`: exact candidate and Ponytail instruction snapshots, candidate provenance, and the upstream Ponytail MIT notice.
- `results/<run>/`: original grading outputs and submitted changes. Absolute local paths in grading logs are replaced with placeholders.
- `reviews/`: anonymized inputs, blind review reports, and the codebooks revealed after review; plus the methodology audit when included.
- `diagnostics/`: post-hoc CSV checks and observed results, kept separate from the predeclared tests.
- `provenance/`: original input manifests, normalized dispatch requests, held-out control logs, and summaries of solvers' reported checks. Completion-message summaries are not full tool transcripts.
- `creator-plus-audit.json`: actual mechanical validator output. Judgment-based authoring checks are discussed in the evaluation report.
- `fixture-validation.json`: existing public suites passed before solving; new feature requirements failed before implementation.
- `sha256.json`: content hashes for this evidence package, excluding the manifest itself.

The candidate's runtime instructions are unchanged. Neither model-performance gains nor native Claude/Firstmate/Astro adoption is established by this package.
