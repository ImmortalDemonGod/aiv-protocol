# AIV Verification Packet (v2.1)

**Commit:** `fix/f14-guard-path-traversal` (PR head)
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R3
  sod_mode: S0
  critical_surfaces: ["verification-gate integrity (guard Packet Source resolution)"]
  blast_radius: "src/aiv/guard/runner.py (_resolve_packet)"
  classification_rationale: "Fixes a path-traversal / arbitrary-file-read in the AIV Guard's Packet Source resolution (F14). The PR-body-supplied path was gated only by startswith('.github/'), bypassable with '.github/../../etc/passwd'. This is a Section 5.2 critical surface (guard integrity), so R3 is mandated regardless of the small diff."
  classified_by: "Claude (Author) + Miguel Ingram (Verifier)"
  classified_at: "2026-07-14T00:00:00Z"
  sod_waiver: "S1 (two natural persons) waived per established repo convention of solo-operator + AI verification at this tier; documented per Section 10. The AI is the Author, the operator is the Verifier."
```

## Claim(s)

1. `_resolve_packet` now BLOCKS a `Packet Source:` path that resolves outside `.github/` (path traversal), adding a CT-001 block and returning `None` instead of reading the file. Falsifiable by: a PR body with `Packet Source: .github/../README.md` making `_resolve_packet()` return `None` (pre-fix it returned the README's contents).
2. A valid path inside `.github/` is still resolved and read (no regression). Falsifiable by: `Packet Source: .github/PULL_REQUEST_TEMPLATE.md` returning that file's content.
3. Existing behavior and tests are preserved: no other production code changed and no existing test was modified or deleted; the full guard suite still passes.

---

## Evidence

### Class E (Intent Alignment)

- **Intent:** Finding F14 in the forensic audit (`docs/audits/2026-06-18-forensic/FINDINGS.md`) - "path traversal in the guard's Packet Source resolution: the `.github/` prefix check is defeated by `.github/x/../../../etc/passwd`."
- **Requirements verified:** the guard must not read a file outside `.github/`; a traversal path must be blocked, and valid `.github/` paths must still be read.

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/guard/runner.py` - `_resolve_packet`: replaced the `startswith(".github/")` check with `Path(file_path).resolve()` + containment under `Path(".github").resolve()`; reads only when the resolved path `is_file()`.
- Added:
  - `tests/unit/test_guard_path_traversal.py` - `TestPacketSourcePathTraversal` (traversal blocked, absolute blocked, valid `.github/` path read).

### Class A (Execution Evidence)

- Env: Python (repo `.venv`), pytest, Linux.
- `pytest tests/unit/test_guard_path_traversal.py`: **3 passed** (the traversal test was RED against the pre-fix code - it read `README.md` via `.github/../README.md` - and is GREEN after the fix).
- `pytest tests/unit/test_guard.py`: **36 passed** (no regression).
- `ruff check` + `ruff format --check` + `mypy src/aiv/guard/runner.py`: clean.
- CI runs the full suite + the AIV guard on this PR.

### Class C (Negative Evidence - Conservation)

- **Search scope:** the change set (`runner.py` `_resolve_packet` + one new test file).
- **Result:** the change does NOT modify or delete any existing test, does NOT add any skip marker, and does NOT alter any guard behavior other than rejecting out-of-`.github/` paths. Absence of test manipulation and of collateral behavior change confirmed; the existing 36-test guard suite passes unchanged.

### Class D (Differential Evidence)

- **Behavioral diff (bound to `runner.py` `_resolve_packet`):**
  - BEFORE: any `Packet Source:` path starting with the literal `.github/` was read, so `.github/../../etc/passwd` (traversal) resolved outside the repo's `.github/` and was read -> arbitrary file read.
  - AFTER: the path is `resolve()`d and must sit inside `Path(".github").resolve()`; otherwise a CT-001 block is added and `None` returned. Only `is_file()` targets are read.
  - Valid-path behavior and the guard's public interface are unchanged.

### Class F (Provenance)

- **Claim 3** (conservation / preserved tests): no existing test was modified or deleted; the only additions are the new regression tests, which are the durable artifact pinning the fix. The change is bound to the PR head commit on `fix/f14-guard-path-traversal`; its commit-bound diff and the CI run re-executing the suite are the chain-of-custody anchors.
- Cryptographic provenance (signed commits / OIDC): N/A - no signing substrate is wired in this repo yet.

---

## Verification Methodology

Test-driven: `test_traversal_outside_github_is_blocked` was written first and observed to FAIL against the unmodified guard (it returned `README.md`'s contents via `.github/../README.md`, proving the arbitrary-file-read), then the fix was applied and it PASSED. The valid-path and absolute-path tests guard against regression. Ruff/format/mypy run clean on the changed files; the full guard suite (36) passes.

---

## Summary

Fixes F14: the AIV Guard's `Packet Source:` resolution allowed path traversal (`startswith(".github/")` is bypassable with `.github/../../etc/passwd`) -> arbitrary file read. `_resolve_packet` now resolves the path and requires it to sit inside `.github/`, blocking traversal while still reading valid `.github/` packets. Two regression tests pin the behavior (red->green). R3 (guard integrity).
