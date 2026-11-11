# Skills

Pinned upstream skills for explicit reuse by firstmate-config, TLW, Astro and standalone agent sessions. Original skills belong separately in [`first-party/`](first-party/README.md).

This is a source repository, not an installer, marketplace or activation policy. Selection records intended use and observed license terms. It does **not** establish model effectiveness or incremental benefit. No consumer configuration, installation or schedule is changed by this repository.

## Layout

```text
upstreams.json                 selected repositories, paths and reviewed terms
upstreams.lock.json            exact commit/tree pins, file hashes and modes
upstream/<source>/<original-path>
first-party/                   future original skills; never managed by updater
scripts/update_upstreams.py    one repository-local refresh command
tests/test_upstreams.py        offline import/update/safety tests
```

Upstream bodies and supporting files retain their original bytes and paths. Each source retains its license at its original path; there are no local prompt rewrites, forwarding aliases or plugin installations. See the [complete intake, license and consumer map](docs/sources.md).

## Included skills

Paths below are relative to `upstream/`. Keep the complete source tree when preparing an explicit-path handoff; a leaf copy can lose licenses or ancestor references.

| Skill | Entry point | Selection purpose |
|---|---|---|
| Humanizer | `humanizer/SKILL.md` | Prose editing with factual meaning and register preserved |
| Grilling | `mattpocock/skills/productivity/grilling/SKILL.md` | Explicit interactive plan/design interviews; not an unattended worker default |
| Systematic debugging | `superpowers/skills/systematic-debugging/SKILL.md` | Diagnosis before fixes; configured firstmate-config source family |
| Test-driven development | `superpowers/skills/test-driven-development/SKILL.md` | Behavioral red/green development; configured source family |
| Verification before completion | `superpowers/skills/verification-before-completion/SKILL.md` | Evidence before success claims; configured source family |
| Test behavior, not implementation | `pstack/pstack/skills/principle-test-behavior-not-implementation/SKILL.md` | Consumer-observable regression tests |
| Code simplification | `addyosmani/skills/code-simplification/SKILL.md` | Behavior-preserving readability improvements; configured source family |
| Performance optimization | `addyosmani/skills/performance-optimization/SKILL.md` | Measured optimization and caching tradeoffs; includes ancestor checklist |
| Ponytail | `ponytail/skills/ponytail/SKILL.md` | Small complete changes and existing-facility reuse; configured source family |
| Ponytail review | `ponytail/skills/ponytail-review/SKILL.md` | Correctness/safety/necessity review; configured source family |
| Be ambitious | `be-ambitious/SKILL.md` | Explicit outcome/depth reframing; already an Astro-owned upstream at the inspected revision |

Firstmate-config still owns its roles, shared-skill pins and installation. **TLW remains on Super Board skills** until an explicitly authorized migration. Astro still owns its built-ins and native roots. Mirroring a source here does not change any of those owners. The separately approved manual global `minimal-change` copy is outside this repository and remains unchanged.

## Verify and refresh

Python 3.11+ on macOS/Linux; only the standard library is used. Online operations require an already configured `gh-axi` supporting the documented `api --jq --full` interface. Nothing installs tools, requests keys or changes accounts.

```sh
# Entire project suite: controlled local fixtures, no network or model calls.
python3 -m unittest discover -s tests -v

# Check the locked files, frontmatter and source-relative resources offline.
python3 scripts/update_upstreams.py verify

# Resolve the declared refs through read-only GitHub GETs; do not write.
python3 scripts/update_upstreams.py check

# Refresh this checkout's upstream/ and generated lock only, if clean and valid.
python3 scripts/update_upstreams.py update

# Reconstruct an entirely absent upstream/ at the existing exact lock pins.
# Refuses partial deletion, local edits, config drift or different output hashes.
python3 scripts/update_upstreams.py update --locked
```

[CI](.github/workflows/ci.yml) runs the same offline suite and locked-file verification on pull requests and pushes to `main`, using Python 3.14. The canonical command is pinned in [`.no-mistakes.yaml`](.no-mistakes.yaml). CI does not run online checks or refreshes, request personal credentials, or modify consumer installations.

`check`: exit `0` = current, `1` = update available, `2` = refusal/error. `update` and `verify`: `0` = success, `2` = refusal/error. `verify` does not check remote freshness. JSON results identify the outcome and source layout; the lock is the authoritative version/file inventory. Never treat an unavailable source as current.

Tracking refs are explicit in the manifest; the initial selection follows `main`. Installed consumers do **not** follow those refs. A refresh resolves each ref once into a full immutable commit and writes that pin into the lock. Review the resulting source/lock diff before any later consumer binding. Existing consumer stable-release pins are not advanced.

### Automatic invocation, not automatic adoption

`python3 scripts/update_upstreams.py update` is a repeatable noninteractive refresh entry point for later authorized automation. **No unattended refresh, scheduler, remote writer or consumer reconciliation is activated.** Activating unattended updates still requires an exact checkout/target, scheduler and write permissions to be established separately. The command never commits, pushes or opens a pull request.

### Drift and terms

- Local file edits, executable-bit changes, missing files, extra files/directories and symbolic links in `upstream/` cause refusal. There is no force option. Unrelated root files and `first-party/` are not managed or traversed.
- Repository name **and numeric GitHub ID**, resolved commit/tree identities, Git blob IDs, SHA-256 and file modes are checked. Submodules, symlinks, LFS pointers, truncated responses, unsafe/colliding paths and project instruction files are refused.
- Selected entrypoint names and their file set cannot silently expand. Required files and source-relative Markdown/resource references must resolve inside that source's retained tree.
- Reviewed LICENSE/LICENCE/NOTICE/COPYING/COPYRIGHT files, relevant LICENSES/LICENCES directories and selected skill license headers are pinned in the manifest. New, missing or changed legal surfaces stop the refresh. Inspect the upstream change and update the explicit terms declaration only after review; never bypass it by altering the generated lock.
- These are known legal-surface checks, not a legal opinion or an automatic interpretation of every sentence in every document. Upstream attribution/citations stay intact. Unknown terms are not made safe by paraphrasing.

Writes are staged on the same filesystem. The old tree/lock remain available until replacement; ordinary failures roll back. An interrupted operation leaves `.upstream-update/` and subsequent commands refuse. Inspect/recover that material before continuing; it is never automatically discarded. Use one writer; this protects ordinary checkout/update operations, not against a malicious same-user process racing filesystem changes, and is not an OS sandbox. The reviewed manifest/lock and GitHub/`gh-axi` transport remain trust inputs; no signed-commit verification is claimed.

For controlled offline reproduction, `--offline <directory>` reads JSON API snapshots named `SHA256(endpoint).json` and never falls back to the network. The unit suite constructs these fixtures itself. Real source snapshots used for this candidate's import are preserved with the private task evidence.

## Consumption and limits

Use the [consumer map](docs/sources.md#consumer-ownership-and-binding) before binding anything. Conventional frontmatter and source-relative references are checked; **native consumer execution and model benefit are not claimed**. In particular, Astro's folder-only copy cannot carry Performance Optimization's `../../references/performance-checklist.md` by copying only that skill's leaf folder.

The former task-local `minimal-change`/`faithful-editing` candidates and evaluation engine are no longer active repository content. Complete prior source and experiment evidence was preserved privately before this cutover. Their failed benefit comparisons were not reclassified, and no new model evaluations were run for this upstream reorganization.

## License

[`LICENSE`](LICENSE) covers original repository tooling, tests and documentation. Imported material retains its source-specific license, copyright and attribution. Do not remove those notices when redistributing or preparing a consumer package.
