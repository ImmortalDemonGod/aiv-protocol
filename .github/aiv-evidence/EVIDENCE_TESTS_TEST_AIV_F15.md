# AIV Evidence File (v1.0)

**File:** `tests/test_aiv_f15.py`
**Commit:** `1a60eb4`
**Generated:** 2026-07-15T05:48:38Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_aiv_f15.py"
  classification_rationale: "R1"
  classified_by: "Claude"
  classified_at: "2026-07-15T05:48:38Z"
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

**Scope Inventory** (SHA: [`1a60eb4`](https://github.com/Black-Box-Research-Labs/aiv-protocol/tree/1a60eb4c4d67902e4fb41b721708d3d79ef0adf6))

- [`tests/test_aiv_f15.py#L1-L64`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/1a60eb4c4d67902e4fb41b721708d3d79ef0adf6/tests/test_aiv_f15.py#L1-L64)

### Class A (Execution Evidence)

**Captured execution (SEAM harness, real pytest runs — not AST):**

- RED baseline (`src/aiv/lib/validators/links.py` reverted at HEAD): `git show e838435:.github/aiv-packets/evidence/aiv-f15/seam_baseline_red_harness.txt` — `tests/test_aiv_f15.py FFF.` → `3 failed, 1 passed`, all 3 failures assert `_head_check reached urlopen` for the finding's three SSRF targets (`file:///etc/shadow`, `http://169.254.169.254/latest/meta-data/`, `http://127.0.0.1/`).
- GREEN at HEAD (fix applied): `git show e838435:.github/aiv-packets/evidence/aiv-f15/seam_head_green_harness.txt` — `tests/test_aiv_f15.py ....` → `4 passed`.
- These transcripts are committed in-repo at `.github/aiv-packets/evidence/aiv-f15/seam_baseline_red_harness.txt` and `.github/aiv-packets/evidence/aiv-f15/seam_head_green_harness.txt`; they are the actual RED-on-baseline/GREEN-at-HEAD demonstration for this test file, captured by the harness, not a forward reference to a later gate.

**Per-symbol test coverage (AST analysis, supplementary — static binding, not execution):**

- **`_SpyResp`** (L1-L64): PASS -- 2 test(s) call `_SpyResp` directly
  - `tests/test_aiv_f15.py::test_head_check_blocks_ssrf_targets_without_reaching_urlopen`
  - `tests/test_aiv_f15.py::test_head_check_still_issues_head_request_for_normal_https_url`
- **`_make_spy_urlopen`** (unknown): PASS -- 2 test(s) call `_make_spy_urlopen` directly
  - `tests/test_aiv_f15.py::test_head_check_blocks_ssrf_targets_without_reaching_urlopen`
  - `tests/test_aiv_f15.py::test_head_check_still_issues_head_request_for_normal_https_url`
- **`test_head_check_blocks_ssrf_targets_without_reaching_urlopen`** (unknown): FAIL -- WARNING: No tests import or call `test_head_check_blocks_ssrf_targets_without_reaching_urlopen`
- **`test_head_check_still_issues_head_request_for_normal_https_url`** (unknown): FAIL -- WARNING: No tests import or call `test_head_check_still_issues_head_request_for_normal_https_url`
- **`_SpyResp.__enter__`** (unknown): FAIL -- WARNING: No tests import or call `__enter__`
- **`_SpyResp.__exit__`** (unknown): FAIL -- WARNING: No tests import or call `__exit__`
- **`_spy`** (unknown): FAIL -- WARNING: No tests import or call `_spy`

**Coverage summary:** 2/7 symbols verified by tests.

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
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/7 symbols verified). Captured execution (RED baseline / GREEN at HEAD) collected separately by the harness's SEAM gate and cross-referenced above by commit SHA `e838435`.
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

test_aiv_f15.py for the finding
