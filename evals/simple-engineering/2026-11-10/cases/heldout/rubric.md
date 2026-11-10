# Predeclared held-out exercise rubric

The target is the observable behavior of `fixture/audit_export.py`. The grader stays outside the solver fixture and accepts a fixture directory as its sole argument. No implementation structure, line count, helper design, or stylistic choice is graded.

Required outcomes:

1. Existing default CSV API and CLI behavior, filtering, privacy, escaping, field order, validation, and destination protections remain correct.
2. API `format="jsonl"` and CLI `--format jsonl` both work. Explicit `format="csv"` and CLI `--format csv` work. Invalid formats produce a failure before writing.
3. JSONL consists of one independently parseable JSON object per physical line, with a final newline for nonempty output and an empty file for no exported events. It contains precisely the selected fields in their requested order, integer IDs, and round-trippable string values.
4. Internal events are excluded by default; actor values are redacted by default. Explicit options restore those values. A limit counts eligible events after filtering, including the supported zero limit.
5. JSONL strings do not receive CSV-specific formula escaping. CSV continues escaping risky leading characters.
6. Existing files require explicit overwrite; the input cannot also be the destination. Malformed source data and invalid field/limit/format options leave existing destinations unchanged and do not create new destinations.
7. The API return value and CLI success message reflect exported rows. Invalid CLI formats fail without writing.

Observable failures include: unsupported new API keywords or CLI arguments; invalid JSONL; leaked actors or internal events; extra or missing fields; changed values or ID types; wrong counts; prematurely truncated output; bypassed validation or overwrite protection; changed CSV output; and nonzero exit status for valid CLI use.

The hidden grader independently tests these requirements using temporary synthetic files and no external dependencies or services. It also executes the existing public tests. Overall success requires all checks to pass. Baseline expectation: all public tests pass, while JSONL and explicit-format tests fail because the feature is absent.
