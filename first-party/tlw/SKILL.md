---
name: tlw
description: Explicit-use handoff for running ONE specifically authorized job through an already-installed TLW (Codex-hosted Super Board wave with a deterministic gate and routed Review - Build, gate, QA, gate, Review, then human approval or the native merge gate). Use only when the user or a supervising task names TLW for a named job (one GitHub issue/card) after scope, project, TLW source/version, prerequisites and delivery path are resolved. Not a router or task picker, not for informational questions about TLW, not stacked on top of no-mistakes for the same job, and not permission to merge, publish, install, authenticate or change models.
license: MIT
---

# TLW job entry

A read-and-apply handoff. It adds no code, command, router, wrapper or lifecycle of its own: it names the existing TLW instructions to read and what must hold before, during and after one job. Everything below was derived from TLW commit `8566b3b0d39b3fa1bf21d5138b63ea0c0e22297c` (Super Board base `d0b7d5a6850614ca809477c1af43d5d7da408726`, `VERSION` 3.3.0) and nothing else.

Paths without a prefix are relative to the TLW source root `<TLW>`. A target project holds the same files as `.claude/bin` (`scripts/`), `.claude/skills` (`skills/`) and `.claude/factory` (`factory/`) (TLW `README.md`, "Flow"). `<target>` is the project checkout that holds that installation.

## Use only when

- A person or the supervising task has named TLW for one bounded job: one issue/card in one repository, and the lane it enters (`build`, `qa` or `review`).
- Informational questions ("how does TLW work?") are answered from the source files below. They start no stage and produce no implementation, QA, review or approval.
- Not for: "pick the next card", draining or sweeping a board, `onboard`/`lint`/`status`/`stop` verbs, installing or upgrading TLW, or model/provider/account changes.

## Who owns what

- The outer supervisor (for example FirstMate) owns the task, its worktree, its authority and what is reported upward. This skill creates no job, agent, scheduler or state store above that.
- TLW owns the selected inner workflow. In TLW's terms the session applying this skill is the *orchestrator*: it checks preconditions, claims the card, launches the wave, reconciles and reports. It never builds, tests or reviews itself (`skills/super-board/SKILL.md` "Orchestrator vs worker"; `skills/super-board/references/run-workflow.md` "Orchestrator delegation contract").
- Target-project instructions and the current user's authority outrank this file and TLW's text. TLW wording such as "run", "merge" or "fix" is not authority.

## Delivery path

TLW and no-mistakes are alternative delivery paths for a job, never two stacked pipelines. If the project's standing mode or the task says no-mistakes, reconcile with the supervisor before launching TLW and do not override that policy. Do not start no-mistakes inside a TLW job. (no-mistakes may still validate changes to TLW's own source; that is a different job.)

## Before launching: resolve or stop

If any item is unresolved, report the exact missing item and stop. No installation, upgrade, login, scope expansion or fallback.

1. **Job and authority.** Repository, issue/card number, entry lane, and whether the authority covers: the GitHub writes TLW makes (claim assignee, board moves, labels, comments, branch pushes, draft PR), `codex` model calls, and merging this job's PR.
2. **Source and version.** A caller-provided or read-verified TLW path. Read its `UPSTREAM.md`. Confirm the files installed in `<target>` match the revision above (for example compare each installed script/skill blob against that commit's). Different, unknown or locally edited, including the earlier `1d401c4…` this file was first reviewed against, = report the mismatch; this file is not reviewed against it.
3. **Installation present** in the checkout the job names, including what the one-card Codex path actually calls: `scripts/` `super-board-{verification-ready.py,wave-plan.sh,skills-ready.py,github-read.py,gh-guard.sh,codex-wave.sh,lane.sh,merge-gate.sh}`, `tlw-gate.py`, `tlw-route.py`, `factory/`. A name the source mentions but does not ship is classified in "Named by TLW but not shipped"; do not improvise it.
4. **Prerequisites** (`README.md` "Live setup"; `run-workflow.md` "Preconditions"): board config `.claude/super-board/configs/<board>.json` (`repo.remote`, `project`, `host: "codex"`, `human_approves_merge`, `notifications.bot_identity`); trusted `.claude/super-board/checks.sh` and usable `verify_commands`; labels; ticket format; the pinned helper skills; `git`, `jq`, `python3` and `codex` on PATH, with `bash -n` passing on `.claude/bin/super-board-codex-wave.sh` and `.claude/bin/super-board-lane.sh` (the Codex form of the "both launcher scripts" check); `gh` already authenticated; clean base checkout. No wave or lane process for this repo (`super-board-codex-wave.sh`, `super-board-lane.sh`; the text also names the unshipped `super-board-codex-lane.sh`) and no `.claude/super-board/codex-wave.pid` or `inflight/workflow-wave.lock` you did not create; an uncertain marker is reported, never removed. Setup scripts (`tlw-board-setup.py`) write to GitHub: run them only if the job's authority names that. Stale-worktree scans may remove worktrees: confine them to the target's `.claude/worktrees/issue-<N>*` paths.
5. **Merge reachability and the production-merge guard.** Read the effective `human_approves_merge`, `merge_policy` and `host`. If the config could let the gate merge without a person and merging this PR is not explicitly authorized, stop and report; do not edit the config. Also apply the guard in `run-workflow.md` Preconditions 2 and `run.md` Preconditions: refuse when `base_branch` is `main`, `human_approves_merge` is false, `merge_policy.default` is not `"human"`, `merge_policy.allow_auto_on_production` is not true, and production signals fire (`skills/super-board/references/onboard.md` "base branch"). No shipped script enforces this on the Codex path, so you must; ambiguous signals are reported, not guessed.

## What TLW does (the real boundary)

```text
Ready  -> Build  (super-build, draft PR, tests first)          -> QA
          gate: tlw-gate.py on the PR branch's exact full head
QA     -> Tester (super-qa issue-scoped)                       -> Review
          fail -> Ready (back to Build) with loop:rebuild-N
          gate again on the current head, then route picks the Reviewer model from risk
Review -> Reviewer (super-review) -> super-board-merge-gate.sh pinned to the reviewed head
          exit 7/8: human approval or human merge      exit 0: merged -> readback -> Done
```

- The wave advances a card only on lane status `advanced`; `bounced`, `blocked`, `human-gate`, `failed` and `halted` end that card's chain for the wave (`scripts/super-board-codex-wave.sh`). Continuing is a later explicit wave, not a loop inside this skill.
- Before every QA or Review agent, `tlw-gate.py` runs the trusted `checks.sh` on a scratch worktree at the PR branch's full head and fails on changed `protected_paths`. FAIL or cannot-gate = `bounced`, the agent never starts; a head that moved since the gate = `bounced` with `head moved:` (`scripts/super-board-lane.sh` "TLW: the deterministic gate"). A Ready `qa` card has no branch yet and skips the gate; its Tester creates the branch.
- **Board QA is not standalone QA.** The board Tester (`skills/super-board/references/run.md` "Tester") checks the diff against the ACs, may write tests and evidence on the same branch, runs `pr-security-review`, and returns product defects or High gaps that need app code to Build (QA to Ready). Standalone `skills/super-qa/SKILL.md` is a route-crawling bug-bash with credential bootstrap ("Auth bootstrap"); its overview has workers commit directly to the active branch, and its bounded product-fix rules live in `skills/super-qa/references/iteration-preamble.md`. It is outside this skill and needs its own explicit authority.
- Review does not fix: `[builder]` findings go to Build, `[qa]` findings to QA. Over-engineering alone never bounces (`run.md` "Reviewer").
- Merge only through `scripts/super-board-merge-gate.sh --expect-head <reviewed sha>`. Route every gate exit as `run.md` "Merge protocol" step 5 says; this skill adds no row. Reviewing with the explicit `--codex` flag is what lets the Reviewer own the merge (`scripts/super-board-lane.sh`, review prompt).
- Lane workers are `codex exec` runs (`--ignore-user-config --ephemeral --json`). The lane prompt forbids launching Claude or sub-agents, so preflight, classification, review and truth-check helpers run inline in that one worker. QA and Review being separate lanes does not mean separate or independent models.

## Launch for one card

Commands are from `run-workflow.md` ("Codex runs", "The wave loop") and the scripts' own usage. They are inert here; run them only through the job's authority, from `<target>`.

1. `python3 .claude/bin/super-board-verification-ready.py --config <config>`. Exit 9 halts: repairing `verify_commands` is the owner's job.
2. `python3 .claude/bin/super-board-github-read.py --check` (non-zero = a paused run: stop, preserve) and the quota guard `source .claude/bin/super-board-gh-guard.sh && sb_gh_guard_check 200` (the source waits for a reset below the threshold; report the wait, never bypass it). The source requires the check before claims, writes and each new wave.
3. `bash .claude/bin/super-board-wave-plan.sh --config <config>` is read-only. Copy the target's object from `cards` verbatim; never hand-build a card. Not in `cards`: report why (claimed, blocked, not in Ready/QA/Review) and stop. In `sweep`, `resume`, `refreshApproval`, `stranded` or `flag`: the source requires that move before launch, so do it for the target only, only if authority covers board writes, and never create or copy approval evidence. Do not touch other cards or run the board-wide crash-recovery sweep; list them in the report.
4. Write `<one-card.json>` now, before anything reads it: a one-element JSON array holding that copied object.
5. `python3 .claude/bin/super-board-skills-ready.py --root <target> --host codex --cards <one-card.json> --hydrate`. Exit 10 halts. (`--hydrate` only fills an absent issue body, read-only. The wave repeats this check itself.)
6. Claim only the target (`run-workflow.md` step 3): add the claim identity as assignee, re-read, proceed only if the assignee list is exactly that identity. Use the GitHub interface the outer task requires for your own writes; TLW's scripts call `gh` themselves, so verify it is authenticated, never change it.
7. `bash .claude/bin/super-board-codex-wave.sh --config <config> --cards <one-card.json> --codex[=<model>] --tier <low|medium|high> --output <wave-result.json>`
   Exactly one explicit `--codex` is required. Without `--codex=<model>`, `codex.model` or a `complexity` on the card, a Ready card first costs a `gpt-6-luna` grading `codex exec` call. That call passes `--ignore-user-config` like the lanes', so a personal `$CODEX_HOME/config.toml` is not loaded for grading; auth still uses `CODEX_HOME`. This skill adds no model selection.
8. Read `<wave-result.json>` (`cards[].finalStatus`, `lanesRun`, `column`, `prUrl`, `detail`; exit 9 verification, 10 skills, 79 GitHub halt). A halt preserves claims, worktrees and approval evidence; do not release, bounce or retry. Otherwise release the claim (loop step 5). The loop also appends a line to `docs/super-board/runs/<date>-<slug>.md` in the checkout; leave it uncommitted unless the job's delivery authority says otherwise. The loop's throttle step is not run (see below); if the result shows a GitHub-limit hit, report it and start no further wave until step 2 passes again.
9. A bounce is a stop point: report it. Start another wave for the same card only if the job's authority allows iterating; TLW's `rebuild_cap` and halt gates stay in force.

## Named by TLW but not shipped (pinned source)

Checked against every caller in the pinned source; a missing filename alone decided nothing.

| Name | Caller and condition | Bounded one-card explicit `--codex` path |
|---|---|---|
| `super-board-host.sh` | `run-workflow.md` "Codex runs": a plain `run` in a host with no Workflow tool, and "Unknown host halts" | Not needed. Host and backend are given, not guessed: the wave requires exactly one explicit `--codex`, skills-ready gets `--host codex`, and merge policy reads `host` from config only. Never start a plain `run`. |
| `super-board-usage.sh` | Wave loop step 1 "Usage guard (Claude waves only; skip for `--codex`)"; `config-schema.json` `usage_pause_pct` | The source skips it for explicit `--codex`. |
| `super-board-codex-lane.sh` | Usage fallback only (usage guard exit 10 without `--codex`); a process name in Preconditions 5b | Not used; the lane launcher is `super-board-lane.sh`. Check both names for live processes. |
| `workflows/super-board-wave.js` | Claude workflow waves; the `node --check` step is "for Claude waves" | Not used. Codex needs `codex` on PATH and `bash -n` on the launchers (item 4). |
| `super-board-throttle.sh` | Wave loop step 5, only on `hit: true` (GraphQL at 0 or a lane failed on the limit): lowers `max_workers` in the config for the next wave | Not a launch prerequisite. A one-card wave runs one worker whatever `max_workers` is. The quota safety is supplied by items 2, `super-board-gh-guard.sh` in each lane and the exit-79 halt. Not run; never improvise it, and never edit `max_workers` by hand. |
| `super-board-stop.sh` | "Codex stop", only when a stop is wanted | Contingency, not a launch prerequisite. A supported path exists: see "Stopping". |

## Stopping a wave you launched

The documented one-command stop is not shipped, but the guarded path in `run-workflow.md` "Codex stop" (GitHub-halt variant) uses things the source does ship: verify that the PID in `.claude/super-board/codex-wave.pid` is alive (`kill -0`) and is that wave's process, then SIGTERM only that PID. The wave's handler (`scripts/super-board-codex-wave.sh`) cancels its lane process groups, each lane returns `halted` (`scripts/super-board-lane.sh`), and worktrees are preserved. Then, only with GitHub available and the job's authority covering it, apply TLW's claim/comment protocol to the target card only (`skills/super-board/references/stop.md` "Per-worker wrap-up" steps 1-4: stop comment on issue and PR, release the assignee, drop `loop:in-*` labels). No `pkill`, no chasing other processes or cards. If the PID cannot be verified, report and stop.

## Human gates and approval

- Exit 7/8 means a person decides. The canonical request lives in the issue block as the gate's exact `approval-request:` line pinning repo, PR, full head and scope; the PR gets no `Reason tag: 🙋` and no `needs-you:` line for the approval itself (`skills/super-board/references/block-template.md` "🙋 Needs you"; `run.md` Merge protocol).
- A trusted `done` approves only the current exact request. Changed head, steps or scope, a newer request-less 🙋 comment, a bot or insufficient-permission author, edited evidence or unreadable GitHub state all mean no approval. Unknown, mismatched or failed checks stop; they are never read as passing.
- Never post the human's `done`. TLW's own trust boundary forbids agents writing it, and this skill creates no exception. Approval of any other PR (including a TLW source PR) is not permission to merge this job's PR.
- Metadata repair, PR publication or merge, branch deletion, and cleanup or deletion of original evidence need the actual task's authority, not this skill.

## Side effects to disclose, not avoid

- Lane workers move board cards, post comments, push `issue-<N>-*` branches and open a draft PR on GitHub, and write `.claude/super-board/{gate,inflight}/`, `codex-wave.pid`, `.claude/worktrees/issue-<N>-*` and `.claude/factory/jobs/issue-<N>/` (`tlw-route.py`) in the checkout.
- Gate scratch worktrees and lock directories are created and removed by the scripts' own traps. On merge the gate runs `gh pr merge --squash --delete-branch --match-head-commit`, so the remote branch is deleted by default; with `.claude/hooks/cleanup-wt.py` installed it also tidies local worktrees afterward. Never promise "no temp files" or "no branch deletion".

## Report

Report each fact only if observed: lanes run with status, exact head SHA at the last gate/review, PR URL, the `approval-request:` line verbatim, human-only steps and who must act, bounced/blocked/halted reasons, files and GitHub writes made, and what you did not do.

- **Merged or Done only after server readback**: `gh pr view <PR> --json state,mergeCommit` shows `MERGED <sha>` and `git merge-base --is-ancestor <sha> origin/<base>` passes (`run.md` Merge protocol step 3). An exit code or log line is not proof; in the live run the gate's `gh pr merge` printed nothing through its `tail -3`.
- Leftover board or issue state (a card still `Blocked`, a `needs-you` label after a human merge, the closing issue) stays as found and is reported. Tidying it needs its own authority.

## Evidence and limits

- Observed live (`inkayat/tlw-live-trial-1` PR 16): the native merge gate verified the approval and base and squash-merged. That run used the gate only, after a one-time operator repair of historical PR/issue metadata; no planner, wave, Build, QA, Reviewer or product model ran. A full Review lane is a `codex exec` product-model run, which that test did not exercise.
- Prior bounded evidence, earlier revision only: a FirstMate file-pointer handoff of this skill drove one card through native Build, QA and Review on TLW `1d401c4…` (explicit `--codex`, one card) to the human merge gate (exit 7); a later merge was a separate attended act, not a native gate rerun. A model-free readback in one harness also showed a `/tlw <job>` template expanding to a pointer to this file. That is not evidence about `8566b3b`: no native job or model trial has run on it, and the earlier result does not transfer.
- Body and comment conventions in `8566b3b` (PR-body writer refuses a status rewrite that changes `needs-you:` steps, exit 64; Reviewer instructions keep one canonical request) are checked by model-free tests and instruction text. They do not show that a future model obeys them. Raw `gh api` edits bypass the writer; the gate then stays strict (exit 7).
- The grader's `--ignore-user-config` is proven only by TLW's fake-`codex` contract tests (argv and the documented flag semantics). No live grading run showed that a real `codex` process ignored a personal config.
- A newer request-less `Reason tag: 🙋` comment voids the canonical request. Two different things are involved. Preventing a model from posting such a comment is instruction-only (nothing stops it from posting). Refusing to merge after one exists is mechanical: the unchanged approval reader counts every trusted 🙋 comment as a request, so the gate stays at exit 7 until a person answers a fresh pinned request.
- Configured checks may be narrow, no CI configured is not passing, and branch protection can be unreadable. Do not treat any as proof.
- This file was not run through a model trial for `8566b3b` and no live TLW command was executed to write it. This repository installs or activates nothing; any host command or global link (for example `/tlw`) is external integration whose presence and behavior must be verified where it is used. Use this file through an explicit file-pointer handoff and never assume such a command exists.

## Handoff example (template, not executed)

```text
Read and apply <skills checkout>/first-party/tlw/SKILL.md for exactly one job.
  repo / issue: <owner>/<repo> #<N>, entering lane <build|qa|review>
  checkout with TLW installed: <abs path>      TLW source verified at 8566b3b: <abs path>
  config: <abs path to .claude/super-board/configs/<board>.json>
  authority: GitHub writes TLW makes <yes/no>; codex model calls <yes/no>; merge of this PR <no>
  delivery path: TLW (not no-mistakes) for this job
Report the lanes run, head SHA, PR URL, approval-request line and human-only steps.
Stop on any missing prerequisite or mismatch and name it.
```

## Provenance and license

Original text in this repository, MIT like [the repository license](../../LICENSE). It describes TLW and cites TLW file paths and one commit; it copies no TLW, Super Board or ZazenCodes text, code or skill body. Command lines and paths above are cited facts. TLW itself declares no license (its `UPSTREAM.md`: licensing undecided) and its `factory/` component is GPL-3.0; nothing here relicenses or redistributes either. Not managed by the upstream updater.
