# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/Black-Box-Research-Labs/aiv-protocol |
| **Change ID** | aiv-f15-adopt-5096b42 |
| **Commits** | `5096b42` |
| **Head SHA** | `58cea65` |
| **Base SHA** | `2766dd4` |
| **Risk tier** | R1 |
| **Classification rationale** | R1/S0: this packet adopts an out-of-band operator commit (`5096b42`) that stays entirely inside `LinkValidator._head_check`/`_is_url_allowed` in a single validator module (`src/aiv/lib/validators/links.py`) plus its dedicated test file (`tests/test_aiv_f15.py`); no shared infrastructure, auth, or data-persistence code is touched, so blast radius is limited to this component and no split-duties reviewer is required. |
| **Created** | 2026-07-15T06:37:00Z |

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "R1/S0: out-of-band operator commit 5096b42 stays inside LinkValidator._head_check/_is_url_allowed in src/aiv/lib/validators/links.py plus tests/test_aiv_f15.py; no shared infrastructure, auth, or persistence code touched."
  classified_by: "Claude"
  classified_at: "2026-07-15T06:37:00Z"
```

---

## Provenance of this packet

Commit `5096b42` ("fix(security): close DNS-based SSRF bypass in LinkValidator._head_check") landed on this branch as an **out-of-band operator review-as-edit** mid-drive, with no AIV packet of its own. This packet adopts it into the evidence chain per the fix-pipeline's `adopt-human-commit` stage: it does not revert or alter the operator's change, and instead documents what changed and re-establishes Class A–F evidence bound to it.

## What 5096b42 changed and why

The `aiv-f15-impl` change (`9cd36dd`, packet `PACKET_aiv_f15_impl.md`) fixed the original F15 finding by adding `LinkValidator._is_url_allowed`: it rejected `file://`/non-http(s) schemes and literal loopback/private/link-local/reserved/multicast/unspecified IP addresses. That closed the three literal-target bypasses named in the finding (`file:///etc/shadow`, `http://169.254.169.254/latest/meta-data/`, `http://127.0.0.1/`).

It left two gaps that `5096b42` closes, both still squarely inside the F15 SSRF class:

1. **Malformed-literal / non-literal hostnames were never resolved.** `_is_url_allowed`'s only host check was `ipaddress.ip_address(hostname)`; if that raised `ValueError` (true for `"127.1"` — a legacy short form Python's `ipaddress` module rejects — `"localhost"`, or any DNS name), the old code treated the hostname as "not an IP, so must be a normal hostname" and returned `True` unconditionally, **without ever performing DNS resolution**. An attacker-controlled DNS name pointing at `169.254.169.254`, or the literal `127.1`, or plain `localhost`, sailed through unchecked and reached `urlopen`.
2. **No protection against DNS rebinding (TOCTOU).** Even a hostname validated at check time could re-resolve to a different (internal) address by the time `urlopen` actually connects, since `urlopen` re-resolves DNS independently.

`5096b42`'s fix, in `src/aiv/lib/validators/links.py`:

- Adds `LinkValidator._resolve_validated_ip(hostname)` (new, L184-L220 at HEAD): parses the hostname as a literal IP first; if that fails, calls `socket.getaddrinfo(hostname, ...)` to resolve it for real and validates **every** returned address against the same private/loopback/link-local/reserved/multicast/unspecified predicate (factored out into the new `LinkValidator._is_disallowed_ip`, L172-L182). Returns `None` (disallowed) if resolution fails or any resolved address is internal.
- Rewrites `_is_url_allowed` (L222-L231) to route all non-literal hosts through `_resolve_validated_ip` instead of assuming they're safe.
- Adds `LinkValidator._pinned_dns(hostname, resolved_ip)` (new, `@contextlib.contextmanager`, L233-L256): monkeypatches `socket.getaddrinfo` for the duration of the `urlopen` call so the connection is forced to use the address that was actually validated, collapsing the check-then-connect DNS-rebinding race.
- `_head_check` (L258-L281) now calls `_resolve_validated_ip` directly and wraps the `urlopen` call in `_pinned_dns(hostname, validated_ip)`.

`tests/test_aiv_f15.py` gained DNS-mocking helpers (`_fake_resolver`) and new parametrized cases (`http://localhost/`, `http://127.1/`, `http://metadata.internal.example.com/`, `http://rebind.example.com/`) plus a dedicated `test_pinned_dns_forces_resolution_to_validated_ip` unit test for the pinning context manager. No pre-existing test assertion was weakened; the 3 original SSRF-target cases and the 1 non-regression case are preserved verbatim (see Class F).

## Why branch HEAD stays correct after 5096b42

- The finding's acceptance condition (urlopen unreached for the three named SSRF targets; a normal https URL still checked) still holds — those 3 original parametrized cases plus the non-regression case are unchanged and still pass (Class A).
- The fix is strictly additive/tightening: it can only turn previously-`True`/allowed decisions into `False`/blocked for hosts that resolve to an internal address; it cannot newly allow anything that was previously blocked. `_ALLOWED_SCHEMES` is unchanged.
- Full existing suite for the same module (`tests/unit/test_validators.py`, 41 tests covering `LinkValidator` end-to-end including `audit_links` network paths) is green at HEAD with no modifications (Class A).
- Static analysis (`ruff`, `mypy`) is clean on both changed files at HEAD (Class D).

## Claims

1. `5096b42` is a genuine, in-scope refinement of the F15 SSRF fix: it closes a DNS-resolution/rebinding gap left open by `9cd36dd`, not a cosmetic or unrelated change.
2. No existing test assertion was weakened or removed by `5096b42`; the original 3 SSRF-target cases and the 1 non-regression case are preserved, and 5 new cases were added.
3. Branch HEAD (`58cea65`) is behaviorally green: the full `tests/test_aiv_f15.py` suite (9 cases) and the full `tests/unit/test_validators.py` suite (41 cases, same module) pass with no regression.
4. `5096b42` did NOT break any test; no fix-forward commit is required.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `.github/aiv-evidence/EVIDENCE_LIB_VALIDATORS_LINKS.md` | `5096b42` | A, B, E |
| 2 | `.github/aiv-packets/evidence/aiv-f15/dns_rebind_red_on_5096b42_parent.txt` | (run against `2766dd4` = `5096b42^`) | A, C |
| 3 | `.github/aiv-packets/evidence/aiv-f15/test_dns_bypass_red_on_parent.py` | (harness source, not part of the change) | A, C |
| 4 | `.github/aiv-packets/evidence/aiv-f15/dns_rebind_green_at_branch_head.txt` | `58cea65` (branch HEAD) | A |
| 5 | `.github/aiv-packets/evidence/aiv-f15/head_check_dns_pin_fix.txt` | `58cea65` (branch HEAD, pre-existing capture) | A, D |
| 6 | `.github/aiv-packets/evidence/aiv-f15/ruff_5096b42.txt` | `58cea65` (branch HEAD) | D |
| 7 | `.github/aiv-packets/evidence/aiv-f15/mypy_5096b42.txt` | `58cea65` (branch HEAD) | D |

### Class B (Referential Evidence)

**Scope Inventory** (functional diff of `5096b42`, SHA [`5096b42`](https://github.com/Black-Box-Research-Labs/aiv-protocol/commit/5096b4202811df407140e1f1f71b40a725f97e86))

- `src/aiv/lib/validators/links.py#L9-L19` (new imports: `contextlib`, `socket`, `typing.TYPE_CHECKING`/`Any`)
- `src/aiv/lib/validators/links.py#L172-L182` (`_is_disallowed_ip`, factored out predicate)
- `src/aiv/lib/validators/links.py#L184-L220` (`_resolve_validated_ip`, new)
- `src/aiv/lib/validators/links.py#L222-L231` (`_is_url_allowed`, rewritten to call `_resolve_validated_ip`)
- `src/aiv/lib/validators/links.py#L233-L256` (`_pinned_dns` context manager, new)
- `src/aiv/lib/validators/links.py#L258-L281` (`_head_check`, now resolves + pins before `urlopen`)
- `tests/test_aiv_f15.py#L1-L124` (DNS-mocking helpers, 4 new parametrized cases, 1 new dedicated test)

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only. This packet's Class A evidence was captured by re-running pytest at (a) the pre-`5096b42` baseline commit (`2766dd4` = `5096b42^`, in a disposable git worktree — no repo state was mutated) and (b) branch HEAD (`58cea65`), per the adopt-human-commit stage's evidence-collection requirement.

---

## Summary

Adopted change `5096b42` ("fix(security): close DNS-based SSRF bypass in LinkValidator._head_check"): 1 commit across 2 functional files (`src/aiv/lib/validators/links.py`, `tests/test_aiv_f15.py`), plus its own `.github/aiv-evidence/EVIDENCE_LIB_VALIDATORS_LINKS.md` update.

### Class A (Behavioral/Direct)

- **Baseline defect reproduced against `5096b42^` (`2766dd4`)**, in an isolated `git worktree add --detach <scratch-dir> 5096b42^` (no mutation to the working repo): a standalone harness (`.github/aiv-packets/evidence/aiv-f15/test_dns_bypass_red_on_parent.py`) calls the **pre-fix** `LinkValidator._is_url_allowed` / `._head_check` directly — no `socket` monkeypatch is used or possible against the old module, since the old code never imports/calls `socket` at all, which is precisely the gap being fixed — with a spy `urlopen`, against three DNS-bypass targets: `http://127.1/`, `http://localhost/`, `http://metadata.internal.example.com/`. Result: `1 passed` — the harness's own assertions (`allowed is True`, `status == 200`, all 3 URLs reached the spy `urlopen`) hold, **confirming the pre-fix code wrongly allows and reaches `urlopen` for all three**. Transcript: `.github/aiv-packets/evidence/aiv-f15/dns_rebind_red_on_5096b42_parent.txt`.
- **Fix verified GREEN at branch HEAD (`58cea65`)**: `tests/test_aiv_f15.py` — `9 passed in 0.16s`, covering the original 3 SSRF-target cases + 1 non-regression case (unchanged from `9cd36dd`) plus the 4 new DNS-bypass cases (`localhost`, `127.1`, attacker-controlled metadata hostname, DNS-rebinding hostname) and the new `test_pinned_dns_forces_resolution_to_validated_ip`. Transcript: `.github/aiv-packets/evidence/aiv-f15/dns_rebind_green_at_branch_head.txt` (cross-checked against the pre-existing capture `.github/aiv-packets/evidence/aiv-f15/head_check_dns_pin_fix.txt`, same 9/9 result).
- **No regression in the module's broader suite**: `tests/unit/test_validators.py` (41 tests, exercises `LinkValidator` end-to-end via `audit_links`) — `41 passed` at branch HEAD, re-run as part of this adoption (transcript captured in this session; same suite/count as the pre-`5096b42` baseline).

### Class B (Referential Evidence)

See Scope Inventory above — 7 line-anchored references into the `5096b42` diff, SHA-pinned to `5096b42`.

### Class C (Negative)

- Searched for: any weakened/removed assertion in `tests/test_aiv_f15.py` between `2766dd4` and `5096b42` — **none found**; `git show 5096b42 -- tests/test_aiv_f15.py` shows only additive changes (new helpers, new parametrize cases, one new test function); the 3 original SSRF-target parametrize entries and the original non-regression test are byte-identical in intent (only type annotations were added to existing signatures).
- Searched for: whether the baseline RED harness fails for the *wrong* reason (fixture/setup error) rather than the actual defect — the harness in this packet (`test_dns_bypass_red_on_parent.py`) asserts directly on `_is_url_allowed`'s return value and on `urlopen` call count, not on an incidental error, so the `1 passed` result is a direct behavioral confirmation of the defect, not a fixture artifact. (A naive attempt to run the *new* `tests/test_aiv_f15.py` verbatim against the old module was also tried and produces `9 failed` via `ModuleNotFoundError: ... aiv.lib.validators.links.socket ...` — a monkeypatch-target error, since old code has no `socket` import to patch; that result is **not** used as primary evidence because it fails for a fixture reason, not the defect itself, which is why the standalone harness above was written instead.)
- Bug-catalog 'Skipped' set: none — this is a straight adoption of an operator fix with no unresolved catalog entries for `links.py`/F15.
- No test file was modified or deleted by `5096b42`; both functional files it touches (`links.py`, `test_aiv_f15.py`) are the same files scoped by the original F15 finding.

### Class D (Static analysis)

- `ruff check src/aiv/lib/validators/links.py tests/test_aiv_f15.py` → `All checks passed!` (`.github/aiv-packets/evidence/aiv-f15/ruff_5096b42.txt`).
- `mypy src/aiv/lib/validators/links.py` → `Success: no issues found in 1 source file` (`.github/aiv-packets/evidence/aiv-f15/mypy_5096b42.txt`, cross-checked against the pre-existing `.github/aiv-packets/evidence/aiv-f15/head_check_dns_pin_fix.txt`).
- flake8 and black are not configured in this repository (ruff supersedes both per `pyproject.toml`) and were not run.

### Class E (Intent Alignment)

- Intent URL (canonical, unchanged from the original finding): https://github.com/Black-Box-Research-Labs/aiv-protocol/blob/55e19790f2080dc5881ddd132bf6e66f67e63a94/docs/audits/2026-06-18-forensic/02-static-audit.md#L25
- Alignment: the cited audit source records that `_head_check` "passes any URL string from packet evidence links directly to `urllib.request.urlopen` without validating the scheme or host" and names `file://`/link-local/loopback bypasses as the concrete risk. `5096b42` is a refinement of the same intent, not a new concern: it closes the residual attack surface within that same defect class — hostnames that reach `urlopen` because they were never DNS-resolved and validated, and DNS-rebinding after validation — which the original `9cd36dd` fix's literal-IP-only check did not cover. The operator's edit stays inside `_head_check`/`_is_url_allowed`, the exact function and lines named in the finding.

### Class F (Provenance)

**Claim 2:** https://github.com/Black-Box-Research-Labs/aiv-protocol/compare/2766dd4...5096b42
**Justification:** `git show 5096b42 --stat` touches exactly 3 files: `src/aiv/lib/validators/links.py`, `tests/test_aiv_f15.py`, `.github/aiv-evidence/EVIDENCE_LIB_VALIDATORS_LINKS.md`. Diffing `tests/test_aiv_f15.py` between `2766dd4` and `5096b42` confirms every pre-existing test function and its 4 original parametrize entries are preserved (only type annotations added to existing signatures); the change is additive (new helpers `_fake_resolver`, 4 new parametrize entries, 1 new test function). No pre-existing test was modified in its assertions or deleted.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs and to freshly-captured transcripts in this packet's evidence directory. Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve historical Layer 1 evidence.
- The baseline RED harness (`test_dns_bypass_red_on_parent.py`) is a supplementary evidence artifact authored for this adoption packet; it is not part of the shipped `tests/` suite and is committed only under `.github/aiv-packets/evidence/aiv-f15/` for auditability.
