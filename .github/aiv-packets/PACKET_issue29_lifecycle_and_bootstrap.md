# AIV Verification Packet (v2.2)

## Summary

Fixes the two remaining bugs in issue #29 (bug #1, the hook shebang, shipped in #30).
Bug #2: the `aiv begin -> commit -> aiv close` lifecycle could never close because no
hook recorded commits into `change.json`. Bug #3: a fresh `aiv init` repo was
unpushable because the pre-push hook enforced packets on the pre-adoption bootstrap
commits, and its diagnostic misattributed the block to `--no-verify`. Both are fixed
with bite tests that fail on pre-fix HEAD and pass after. Full suite: 774 passed.

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/Black-Box-Research-Labs/aiv-protocol |
| **Change ID** | issue29-lifecycle-and-bootstrap |
| **Commits** | `d0c92d9`, `4ca16e9` |
| **Head SHA** | `4ca16e9` |
| **Base SHA** | `958b2ba` |
| **Created** | 2026-07-23 |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Two isolated bug fixes to the change-lifecycle and pre-push hook. No API removal; new behavior is additive (a post-commit hook, a close-time reconstruction fallback, and a pre-adoption exemption). All git operations are read-only except change.json bookkeeping, which the tooling already owns."
  classified_by: "money-agent integration follow-up"
  classified_at: "2026-07-23"
```

## Claims

1. Bug #2 — the recommended lifecycle now closes. `aiv/hooks/post_commit.py` (new) records
   each commit into the active change (installed by `aiv init`), and `close_change`
   reconstructs commits from git history when none were recorded, so `aiv close` no longer
   raises "has no commits". `ChangeContext.base_sha` anchors the change at `begin`, and
   `detect_untracked_commits` uses it so it is no longer circular on an empty `commits` list.
2. Bug #3 — a fresh `aiv init` repo is pushable. `pre_push.py` exempts commits at or before
   the `.aiv.yml` adoption baseline from packet enforcement, and the block diagnostic states
   hypotheses instead of asserting `--no-verify` was used.
3. No existing behavior was removed: commits after adoption are still enforced (asserted by
   `test_post_adoption_functional_without_packet_still_flagged`), and `close_change` still
   raises when a change genuinely has no new commits
   (`test_close_still_raises_when_no_new_commits`).

---

## Evidence

### Class A (Execution Evidence)

A) Execution: full suite after both fixes — **774 passed** (`python -m pytest -q`); `ruff check
src/ tests/` and `ruff format --check src/ tests/` clean; `mypy src/aiv/` adds zero errors over
the pre-change baseline (20 pre-existing third-party-stub errors, unchanged). Bite proofs, each
demonstrated failing-then-passing by reverting only the functional file: (1) reverting
`lib/change.py`, `test_close_reconstructs_when_commits_empty` fails with `ValueError: ... has no
commits` and passes after; (2) reverting `hooks/pre_push.py`, a bootstrap adoption commit is
returned as a violation (`[('5094087', ['src/scaffold.py'])]`, unpushable) and is exempt (`[]`,
pushable) after.

### Class B (Referential Evidence)

B) Referential: commit `d0c92d9` — `hooks/post_commit.py` (new `main`/`record` path),
`lib/change.py` (`base_sha` field, `reconstruct_commits`, `close_change` fallback, `begin_change`
anchor, `detect_untracked_commits` anchor), `cli/main.py` (`aiv init` post-commit shim). Commit
`4ca16e9` — `hooks/pre_push.py` (`_aiv_adoption_sha`, `_is_pre_adoption`, the `check_commits`
exemption, softened diagnostic). Tests: `test_post_commit_hook.py` (new), and additions to
`test_change.py`, `test_pre_push_hook.py`, `test_cli_init.py`.

### Class F (Provenance)

F) Provenance: the change is content-addressed by its commits — `d0c92d9` (bug #2) and `4ca16e9`
(bug #3), head `4ca16e9` over base `958b2ba` (the #30 merge). Each SHA binds the exact diff this
packet describes.

### Class E (Intent Alignment)

E) Intent: the mandate is to fix the two first-run bugs left open when #29 was closed by #30 —
the change-lifecycle recording gap and the bootstrap-push gap — so the issue closes only when it
is actually addressed. Both fixes remove reasons a downstream adopter (the money-agent
integration) must carry local workarounds. Tracked as issue #29 (bugs 2 and 3).

---

## Verification Methodology

Each bug was reproduced against pre-fix HEAD before fixing: the lifecycle close raising "has no
commits" with an empty `change.json`, and the pre-push hook flagging a bootstrap adoption commit.
The fixes were then applied and the same scenarios verified passing, the bite tests added, and the
full suite plus lint and type-check run. The bite proofs were run by reverting only the single
functional file (`git stash` of that path) so the assertion executes against otherwise-current
code, then restoring it — because a whole-tree revert would also remove the tests.

## Honest limitations

- `close_change` reconstruction and `detect_untracked_commits` depend on `base_sha`, which is only
  set for changes begun after this fix; a change begun by an older version (no `base_sha`)
  reconstructs from `HEAD` (all branch commits) rather than from the begin point. This is strictly
  better than the prior behavior (which recorded nothing) and self-heals on the next `aiv begin`.
- The bootstrap exemption keys on the first commit that adds `.aiv.yml`. A repo that removes and
  re-adds `.aiv.yml` later would move the baseline to the earliest add (correct), but a repo that
  never commits `.aiv.yml` gets no exemption (fail-safe: everything is scanned).
- `git diff-tree` reports no files for a root commit (no parent), so a root commit is never flagged
  regardless of exemption; the tests add a baseline commit first so the exemption path is actually
  exercised (a root adoption commit would pass the test for the wrong reason).
