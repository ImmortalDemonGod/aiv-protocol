# AIV Evidence File (v1.0)

**File:** `tests/aiv-f15.bug-catalog.md`
**Commit:** `9f78605`
**Generated:** 2026-07-15T05:48:37Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/aiv-f15.bug-catalog.md"
  classification_rationale: "R1"
  classified_by: "Claude"
  classified_at: "2026-07-15T05:48:37Z"
```

## Claim(s)

1. RED test pins the finding's defect against the cited baseline
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25)
- **Requirements Verified:** design-tests: a failing test that names the finding's defect

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`9f78605`](https://github.com/Black-Box-Research-Labs/aiv-protocol/tree/9f7860541e52dca882f5e53da8d2cf10b0c4506f))

- [`tests/aiv-f15.bug-catalog.md#L1-L33`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/9f7860541e52dca882f5e53da8d2cf10b0c4506f/tests/aiv-f15.bug-catalog.md#L1-L33)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | RED test pins the finding's defect against the cited baselin... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

aiv-f15.bug-catalog.md for the finding
