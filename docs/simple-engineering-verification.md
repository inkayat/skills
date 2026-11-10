# simple-engineering 0.1.0 — verification

Date: 2026-11-10. Scope: initial discussion-draft checks, not production acceptance. The later [comparative evaluation](simple-engineering-evaluation.md) records 21 actual agent runs, independent review, and additional failures found after the initial tests.

## Observed results

| Check | Observed outcome | What it establishes |
| --- | --- | --- |
| Read target repository through authenticated GitHub CLI | `inkayat/skills`, private, default branch `main`; base commit `416f6a38c1b79a460ff7632decdb41b9b9f31ab8`; README only | The draft targets the new repository rather than the deleted library |
| Fetch immutable upstream files | K, P, T, S and two license notices retrieved at the commits in the source record | Reviewed source versions are identifiable |
| Recompute each fetched file's Git blob ID | All six matched the GitHub-reported SHA-1 blob IDs | The inspected snapshots match those source objects; this is integrity evidence, not a signature or benefit test |
| Run the installed skill-creator `quick_validate.py` against `skills/simple-engineering` | Exit 0: `Skill is valid!` | Supported frontmatter, name, description and placeholder checks pass |
| Author scenario review | Ten inputs and the author's resulting decisions recorded in the decision record | The author found the intended scope and tradeoffs consistent in those walkthroughs |
| Resolve relative Markdown links | All seven resolve to files inside this repository | The packaged source reference and review documents are reachable |
| Run `git diff --cached --check` on the complete staged change | Exit 0, no findings | No whitespace errors or conflict markers detected by that check |

The standard validator ran with Python 3.14 and PyYAML 6.0.3 in an isolated temporary development environment. No validator dependency is required to use the skill.

To repeat the format check, use the skill-creator validator available in your environment:

```sh
python /path/to/skill-creator/scripts/quick_validate.py skills/simple-engineering
```

To repeat source integrity verification, fetch the exact revision/path links in [sources](../skills/simple-engineering/references/sources.md), preserve their bytes, and compare `git hash-object <file>` to the listed file blob IDs. The snapshots themselves are development evidence outside this repository, not installed skill content.

## Limits

- Scenario walkthroughs are author review, not independent behavioral trials and not ten passing model tests.
- No comparison against a baseline or the original skills had been run at initial drafting. The subsequent comparative report now contains that experiment; it did not establish reliable incremental benefit. Expected benefits remain hypotheses.
- Native discovery and invocation in Claude, Firstmate, and Astro have not been tested. The method contains no host-specific runtime dependency, but that does not prove host integration.
- No application code, automated delivery pipeline, installation, or activation is included.
- No repository CI workflow exists at the inspected base revision. Local validation must not be described as a green CI run.

The source record notes the difference between an upstream MIT label and a full retrieved license notice; missing notices are not fabricated.
