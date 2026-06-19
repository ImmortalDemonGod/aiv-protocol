# AIV Verification Packet (v2.1)

**Commit:** `fix/f96-husky-delegates-to-python` (PR head)
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R3
  sod_mode: S0
  critical_surfaces: ["verification-gate integrity (pre-commit enforcement parity)"]
  blast_radius: service
  classification_rationale: "Rewrites the bash pre-commit enforcement gate (.husky/pre-commit) to delegate to the authoritative Python hook. Section 5.2 critical surface (verification-gate integrity): the bash hook was a stale parallel implementation that rejected Layer-1 EVIDENCE_*.md, so aiv commit output was blocked, a drift/bypass defect (F96/C2). R3 is mandated by the critical surface."
  classified_by: "Claude (Author) + Miguel Ingram (Verifier)"
  classified_at: "2026-06-18T23:30:00Z"
  sod_waiver: "S1 waived per established repo convention of solo-operator + AI verification at this tier; documented per Section 10. AI is Author, operator is Verifier."
```

## Claim(s)

1. `.husky/pre-commit` delegates the gate to the Python hook (`python -m aiv.hooks.pre_commit`); no duplicated rule logic remains in bash. Falsifiable by: a `PACKET_PATTERN` or per-rule reject branch still present in the bash hook.
2. The `aiv commit` output (one source file plus one `EVIDENCE_*.md`) is accepted by both hooks. Falsifiable by: either hook exiting non-zero on that staged set.
3. Both hooks reach the same decision for the same staged set, so the two surfaces cannot drift. Falsifiable by: a staged set where the bash and Python exit codes differ.
4. The deny path is unchanged: a functional file with no packet and no evidence is still rejected by both hooks. Falsifiable by: such a commit passing either hook.

---

## Evidence

### Class E (Intent Alignment)

- **Finding:** `docs/audits/2026-06-18-forensic/FINDINGS.md` C2 (Raw IDs F96, F97, F98) and H3c (F210): packet-pattern drift across the three enforcement surfaces; the husky pattern omits Layer-1 EVIDENCE.
- **Goal condition (F96 recipe):** the exact `aiv commit` output (one EVIDENCE_*.md plus one source file) passes both hooks; a multi-file commit in an active change context is allowed by both; the rule list matches what is implemented.

### Class B (Referential Evidence)

- Modified: `.husky/pre-commit` (285 to 44 lines): the duplicated safety-snapshot, pattern definitions, atomicity rules, and rubric are removed; replaced with `"$PY" -m aiv.hooks.pre_commit || exit 1`.
- Added: `tests/integration/test_hook_evidence_parity.py::TestHookEvidenceParity` (three parity tests).

### Class A (Execution Evidence)

- Env: Python via `.venv`, pytest 9.0.3, macOS (Darwin).
- `pytest tests/integration/test_hook_evidence_parity.py`: 3 passed (two FAILED on the pre-delegation hook; TDD red to green captured).
- `pytest tests/unit/test_pre_commit_hook.py` (the delegate): 55 passed, 0 failed.
- Full suite: 753 passed, 2 failed. The 2 `test_cli_init` failures are a pre-existing local rich-console wrap artifact, green in CI.
- `ruff check` and `ruff format --check` on the new test: clean. `sh -n .husky/pre-commit`: syntax OK.

### Class C (Negative Evidence - Conservation)

- Search scope `.husky/pre-commit`, method `grep -nE 'PACKET_PATTERN|Rule [0-9]|validate_staged_packet'`: no atomicity rule logic, no packet-pattern, and no per-rule reject branches remain in the bash hook.
- No new bypass is introduced and no deny path is removed: a functional-only commit is still rejected by both hooks.

### Class D (Differential Evidence)

- Before: staging `src/x.py` plus `.github/aiv-evidence/EVIDENCE_X.md` hit the bash "Code without Evidence" rule and returned 1, while the Python hook returned 0 (the drift).
- After: the same staged set delegates to the Python hook and returns 0, identical to the Python hook. Net change: `.husky/pre-commit` minus 241 lines.

### Class F (Provenance)

- Bound to the PR head commit; the parity tests are the durable artifact pinning agreement between the two surfaces. No signing substrate is wired yet (cryptographic provenance N/A); the commit-bound diff plus committed tests are the integrity anchors.

---

## Verification Methodology

Test-driven: the three parity tests were written first and observed to FAIL against the pre-delegation bash hook (it returned 1 where the authoritative hook returned 0 on the source-plus-EVIDENCE and multi-file cases), after which the bash hook was rewritten to delegate and the tests observed to PASS. The delegate's own 55-test unit suite is unchanged. Hook syntax was confirmed with a no-execute shell parse.

---

## Summary

Fixes F96/C2 (and H3c/F210): the bash `.husky/pre-commit` was a stale 285-line parallel reimplementation that rejected Layer-1 `EVIDENCE_*.md`, so `aiv commit` output was blocked by bash but accepted by Python (a drift/bypass defect). The bash hook now delegates the whole gate decision to `python -m aiv.hooks.pre_commit` (single source of truth, 44 lines), so the two surfaces cannot drift. R3 (verification-gate integrity). Proven red to green with integration parity tests; the delegate's 55-test suite is unchanged.
