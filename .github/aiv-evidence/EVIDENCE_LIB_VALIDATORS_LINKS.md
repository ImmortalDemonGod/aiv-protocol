# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/validators/links.py`
**Commit:** `2766dd4`
**Previous:** `ebfd7ec`
**Generated:** 2026-07-15T06:17:43Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/validators/links.py"
  classification_rationale: "R1/S0: the fix is confined to the SSRF guard inside LinkValidator._head_check in a single validator module (src/aiv/lib/validators/links.py) -- hostname resolution + validation + DNS pinning added, no shared infra/auth/persistence code touched, so blast radius stays limited to this component"
  classified_by: "Claude"
  classified_at: "2026-07-15T06:17:43Z"
```

## Claim(s)

1. LinkValidator._head_check rejects hostnames whose resolved DNS address is loopback/private/link-local/reserved/multicast/unspecified (e.g. 127.1, localhost, or attacker DNS names pointing at 169.254.169.254), not just literal IP addresses
2. LinkValidator._head_check pins the outbound connection to the address already validated by the SSRF guard, so a DNS-rebinding attacker cannot flip the record between the allowlist check and the actual connect
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25)
- **Requirements Verified:** the SSRF guard must not treat any non-literal-IP hostname as automatically safe; internal addresses reached via DNS resolution (including rebinding) must be rejected the same as literal internal IPs

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`2766dd4`](https://github.com/Black-Box-Research-Labs/aiv-protocol/tree/2766dd4018e4c08a093f184fde58229a6b1e3a08))

- [`src/aiv/lib/validators/links.py#L9`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L9)
- [`src/aiv/lib/validators/links.py#L12-L13`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L12-L13)
- [`src/aiv/lib/validators/links.py#L18-L20`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L18-L20)
- [`src/aiv/lib/validators/links.py#L172-L221`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L172-L221)
- [`src/aiv/lib/validators/links.py#L231-L252`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L231-L252)
- [`src/aiv/lib/validators/links.py#L254-L256`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L254-L256)
- [`src/aiv/lib/validators/links.py#L261-L267`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L261-L267)
- [`src/aiv/lib/validators/links.py#L269`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L269)
- [`src/aiv/lib/validators/links.py#L273`](https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/2766dd4018e4c08a093f184fde58229a6b1e3a08/src/aiv/lib/validators/links.py#L273)

### Class A (Execution Evidence)

**Captured execution (real pytest run, not AST):**

- `tests/test_aiv_f15.py -v` → `9 passed` (7 SSRF-block cases incl. the DNS-resolved bypasses `127.1`, `localhost`, and attacker-hostname-to-internal-IP; the non-regression normal-https case; the DNS-pinning/rebinding-prevention case). Transcript committed at `.github/aiv-packets/evidence/aiv-f15/head_check_dns_pin_fix.txt`.
- `mypy src/aiv/lib/validators/links.py` → `Success: no issues found in 1 source file` (same transcript file, appended).

**Per-symbol test coverage (AST analysis):**

- **`LinkValidator`** (L9): PASS -- 6 test(s) call `LinkValidator` directly
  - `tests/unit/test_validators.py::test_audit_links_off_skips_network`
  - `tests/unit/test_validators.py::test_audit_links_404_blocks`
  - `tests/unit/test_validators.py::test_audit_links_200_passes`
  - `tests/unit/test_validators.py::test_audit_links_network_error_warns`
  - `tests/unit/test_validators.py::test_audit_links_403_blocks`
  - `tests/unit/test_validators.py::test_audit_links_deduplicates_urls`
- **`LinkValidator._is_disallowed_ip`** (L12-L13): FAIL -- WARNING: No tests import or call `_is_disallowed_ip`
- **`LinkValidator._resolve_validated_ip`** (L18-L20): FAIL -- WARNING: No tests import or call `_resolve_validated_ip`
- **`LinkValidator._is_url_allowed`** (L172-L221): FAIL -- WARNING: No tests import or call `_is_url_allowed`
- **`LinkValidator._pinned_dns`** (L231-L252): PASS -- 1 test(s) call `_pinned_dns` directly
  - `tests/test_aiv_f15.py::test_pinned_dns_forces_resolution_to_validated_ip`
- **`_pinned`** (L254-L256): FAIL -- WARNING: No tests import or call `_pinned`
- **`LinkValidator._head_check`** (L261-L267): PASS -- 2 test(s) call `_head_check` directly
  - `tests/test_aiv_f15.py::test_head_check_blocks_ssrf_targets_without_reaching_urlopen`
  - `tests/test_aiv_f15.py::test_head_check_still_issues_head_request_for_normal_https_url`

**Coverage summary:** 3/7 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** `mypy src/aiv/lib/validators/links.py` → Success: no issues found in 1 source file (see transcript above)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | LinkValidator._head_check rejects hostnames whose resolved D... | symbol | 8 test(s) call `LinkValidator._head_check`, `LinkValidator` | PASS VERIFIED |
| 2 | LinkValidator._head_check pins the outbound connection to th... | symbol | 8 test(s) call `LinkValidator._head_check`, `LinkValidator` | PASS VERIFIED |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (3/7 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Resolve and validate every hostname (not just literal IPs) before the HEAD check, and pin the connection to the validated address to close the DNS-rebinding TOCTOU gap CodeRabbit demonstrated (127.1 bypass PoC)
