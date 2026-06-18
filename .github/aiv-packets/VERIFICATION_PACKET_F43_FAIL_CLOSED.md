# AIV Verification Packet (v2.1)

**Commit:** `fix/f43-fail-closed-precommit` (PR head)
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R3
  sod_mode: S0
  critical_surfaces: ["verification-gate integrity (pre-commit packet enforcement)"]
  blast_radius: service
  classification_rationale: "Modifies the central pre-commit enforcement gate (_validate_packet in src/aiv/hooks/pre_commit.py). This is a Section 5.2 critical surface (verification-gate / audit-integrity): the function decides whether unverified work may be committed. The pre-fix code failed OPEN (except Exception: return True), so any validator error silently approved the commit - the exact defect class AIV exists to police. R3 is mandated by the critical surface regardless of the small diff size."
  classified_by: "Claude (Author) + Miguel Ingram (Verifier)"
  classified_at: "2026-06-18T22:10:00Z"
  sod_waiver: "S1 (two natural persons) waived per established repo convention of solo-operator + AI verification at this tier; documented per Section 10. The AI is the Author, the operator is the Verifier."
```

## Claim(s)

1. `_validate_packet` now FAILS CLOSED: an exception raised during validation returns `False` (block the commit), not `True` (skip). Falsifiable by: forcing an exception inside the function and observing the return value or `main()` exit code.
2. `main()` returns a non-zero exit (blocks the commit) when validation raises an exception, because every call site is `if not _validate_packet(p): return 1`. Falsifiable by: a `main()` run whose `_validate_packet` raises returning 0.
3. Temp artifacts (the NamedTemporaryFile and the audit mkdtemp dir) are cleaned up on every path including the exception path, via a `finally` block (closes F113). Falsifiable by: a leaked `aiv-audit-check-*` dir or `.md` temp after a raising run.
4. No regression: the existing pre-commit hook behavior (rule engine, packet-validation-fail blocks) is unchanged; the full hook suite stays green.

---

## Evidence

### Class E (Intent Alignment)

- **Finding:** `docs/audits/2026-06-18-forensic/FINDINGS.md` C1 (Raw ID **F43**) - "Packet validation fails *open* in the pre-commit hook" - and H12 (Raw ID **F113**) - "temp files leaked in exception paths inside `_validate_packet`".
- **Goal condition (F43 recipe):** "a forced exception inside `_validate_packet` causes `main()` to block the commit (non-zero exit)."
- **Requirements verified:**
  1. Exception -> fail closed (block), never skip.
  2. `main()` exit is non-zero on a validation exception.
  3. Temp artifacts cleaned up on the exception path (F113).

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/hooks/pre_commit.py` - `_validate_packet` (def at line 148): the `except Exception` now prints a `[BLOCK]` message and `return False`; a `finally` unlinks the temp file and removes the audit dir; redundant inline cleanups removed.
- Added:
  - `tests/unit/test_pre_commit_hook.py` - `class TestValidatePacketFailsClosed` with `test_validate_packet_returns_false_on_internal_exception` and `test_main_blocks_commit_when_validation_raises`, plus the `_validate_packet` import.

**Claim 1-2 (fail closed + non-zero exit):** the `except` branch and the `finally` in `_validate_packet`; call sites `if not _validate_packet(p): return 1` in `main()`.

**Claim 3 (no leak):** the `finally` block guarding `tmp_path` and `audit_dir`.

### Class A (Execution Evidence)

- Env: Python via `.venv`, pytest 9.0.3, macOS (Darwin).
- `pytest tests/unit/test_pre_commit_hook.py::TestValidatePacketFailsClosed`: **2 passed** (both FAILED on the pre-fix code - TDD red->green captured).
- `pytest tests/unit/test_pre_commit_hook.py`: **55 passed** (53 pre-existing + 2 new), 0 failed.
- `pytest` (full suite): **748 passed, 2 failed**. The 2 failures (`test_cli_init.py::test_skips_existing_aiv_hook`, `..._push_hook`) are PRE-EXISTING and unrelated (hook-install idempotency, near F96); proven not caused by this change via stash-and-rerun on clean `main` (both still fail with this change stashed).
- `ruff check` + `ruff format --check` + `mypy src/aiv/hooks/pre_commit.py`: all clean.

### Class C (Negative Evidence - Conservation)

- **Search scope:** `src/aiv/hooks/pre_commit.py` (the changed file).
- **Search method:** `grep -nE 'except[^:]*:\s*$' -A3` over `_validate_packet`; manual read of every return path.
- **Result:** no remaining `except ...: return True` fail-open path in the function; the only `return True` paths are the empty-content guard (line ~155) and the all-checks-passed terminal (unchanged behavior). No new disallowed pattern introduced.
- **Leak check:** 0 `aiv-audit-check-*` temp dirs and 0 stray `.md` temps remain after the test run (F113 conserved).

### Class D (Differential Evidence)

- **Behavioral diff bound to `src/aiv/hooks/pre_commit.py` `_validate_packet` except path:**
  - BEFORE: validator exception -> `print("WARNING: ... skipped")`; `return True` -> `main()` `if not True` -> no block -> **exit 0 (commit ALLOWED on a crashed validator).**
  - AFTER: validator exception -> `print("[BLOCK] ...")`; `return False` -> `main()` `if not False` -> `return 1` -> **exit 1 (commit BLOCKED).**
- This is the only behavioral change: success and explicit-validation-failure paths return the same values as before; only the exception path inverts (fail open -> fail closed) and temp cleanup is added.

### Class F (Provenance)

- The fix is bound to the PR head commit on `fix/f43-fail-closed-precommit`; the regression tests `TestValidatePacketFailsClosed` are the durable artifact that pins the fail-closed behavior against future drift.
- Full cryptographic provenance (signed commits / OIDC attestation) is N/A: no signing substrate is wired in this repo yet. The commit-bound diff + the committed regression tests are the available integrity anchors.

---

## Verification Methodology

Test-driven: the two regression tests were written first and observed to FAIL against the unmodified (fail-open) code (validator returned `True`; `main()` returned 0), then the fix was applied and the tests observed to PASS. Pre-existing unrelated failures were isolated by `git stash` + re-run on clean `main`. Lint (ruff), format, and types (mypy) were run on the changed files. Temp-leak was checked by listing `aiv-audit-check-*` after the run.

---

## Summary

Fixes F43 (the audit's headline critical): the central pre-commit packet-validation gate failed OPEN - any exception during validation returned `True`, silently approving an unverified commit. `_validate_packet` now fails CLOSED (`return False`) so a crashed or unavailable validator blocks the commit, and a `finally` block cleans up temp artifacts on every path (closes F113). R3 (verification-gate integrity). Proven red->green with two regression tests; full hook suite green; the only suite failures are pre-existing and isolated.
