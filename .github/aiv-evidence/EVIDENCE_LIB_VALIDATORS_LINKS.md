# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/validators/links.py`
**Commit:** `dc1c5c3`
**Generated:** 2026-07-15T05:50:15Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/validators/links.py"
  classification_rationale: "R1"
  classified_by: "Claude"
  classified_at: "2026-07-15T05:50:15Z"
```

## Claim(s)

1. implements the converged plan for the finding per its acceptance condition
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25)
- **Requirements Verified:** write-code: implement the converged plan within scope

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`dc1c5c3`](https://github.com/Black-Box-Research-Labs/aiv-protocol/tree/dc1c5c3a9bc8a29d07d2251b2d29fb3535e94807))

- [`src/aiv/lib/validators/links.py#L9`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/dc1c5c3a9bc8a29d07d2251b2d29fb3535e94807/src/aiv/lib/validators/links.py#L9)
- [`src/aiv/lib/validators/links.py#L12`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/dc1c5c3a9bc8a29d07d2251b2d29fb3535e94807/src/aiv/lib/validators/links.py#L12)
- [`src/aiv/lib/validators/links.py#L164-L187`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/dc1c5c3a9bc8a29d07d2251b2d29fb3535e94807/src/aiv/lib/validators/links.py#L164-L187)
- [`src/aiv/lib/validators/links.py#L191-L192`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/dc1c5c3a9bc8a29d07d2251b2d29fb3535e94807/src/aiv/lib/validators/links.py#L191-L192)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`LinkValidator`** (L9): PASS -- 6 test(s) call `LinkValidator` directly
  - `tests/unit/test_validators.py::test_audit_links_off_skips_network`
  - `tests/unit/test_validators.py::test_audit_links_404_blocks`
  - `tests/unit/test_validators.py::test_audit_links_200_passes`
  - `tests/unit/test_validators.py::test_audit_links_network_error_warns`
  - `tests/unit/test_validators.py::test_audit_links_403_blocks`
  - `tests/unit/test_validators.py::test_audit_links_deduplicates_urls`
- **`LinkValidator._is_url_allowed`** (L12): FAIL -- WARNING: No tests import or call `_is_url_allowed`
- **`LinkValidator._head_check`** (L164-L187): PASS -- 2 test(s) call `_head_check` directly
  - `tests/test_aiv_f15.py::test_head_check_blocks_ssrf_targets_without_reaching_urlopen`
  - `tests/test_aiv_f15.py::test_head_check_still_issues_head_request_for_normal_https_url`

**Coverage summary:** 2/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | implements the converged plan for the finding per its accept... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

links.py for the finding
