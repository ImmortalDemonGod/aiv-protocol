# Curated Findings — Forensic Audit (2026-06-18)

_A deduplicated, severity-ranked view of the Stage-2 static audit, with an explicit
**independent-verification** column. This document is a curation layer over the raw evidence;
it does not add, soften, or invent findings. Every issue here traces back to one or more raw
finding IDs in [`raw/stage2.json.md`](raw/stage2.json.md), and the clustering is reproducible from
[`raw/distinct-issues.json.md`](raw/distinct-issues.json.md)._

> **No fixes are applied in this PR.** This is a record-and-triage deliverable only.

---

## Why this layer exists

The raw audit reports **251 findings**. That headcount is inflated by re-discovery across four
adversarial rounds with no cross-round deduplication: the 251 raw findings map to **39 distinct
file locations** and **147 distinct issues**. For example, the guard path-traversal is reported
four times (F14, F83, F146, F197) and the link-validator SSRF ten times across two files
(F15/F84/F147/F196 + F19/F66/F90/F151/F202/F203).

Curation collapses the duplicates so the real surface is legible:

| Severity | Raw findings | Distinct issues |
|---|---:|---:|
| Critical | 2 | **2** |
| High | 36 | **21** |
| Medium | 108 | 66 |
| Low | 90 | 53 |
| Info | 15 | 5 |
| **Total** | **251** | **147** |

The headline actionable surface is the **2 critical + 21 high** issues below. Medium/low/info are
summarized by theme at the end and remain available in full in the raw artifacts.

---

## Independent verification

These findings were re-checked against the actual source on `main` during PR preparation (not
trusting the audit's self-report). All held. Line numbers are from the audited branch
`claude/eloquent-goodall-sqfrhf` and may drift by a line or two on `main`.

| Issue | Claim | Re-checked against source | Verdict |
|---|---|---|---|
| C1 | `pre_commit.py` wraps validation in `except Exception: return True` (fails **open**) | `src/aiv/hooks/pre_commit.py:211-214` | ✅ Confirmed verbatim |
| C2 | husky pattern matches only `VERIFICATION_PACKET_*.md`; Python hook also accepts `EVIDENCE_*.md` | `.husky/pre-commit:60` vs `src/aiv/hooks/pre_commit.py:342` | ✅ Confirmed |
| H1 | guard path check is `startswith(".github/")` only, then `Path(...).read_text()` | `src/aiv/guard/runner.py:191-204` | ✅ Confirmed (traversal reachable) |
| H2 | link validator calls `urlopen` with no scheme allowlist / loopback block | `src/aiv/lib/validators/links.py:164-176` | ✅ Confirmed |
| H3 | pipeline R1 enforces 3 evidence classes while hook rubric documents 2 | `src/aiv/lib/validators/pipeline.py:181-183` | ✅ Confirmed |
| H4 | `aiv close` commits the packet with `git commit --no-verify` | `src/aiv/cli/main.py:1236-1238` | ✅ Confirmed |
| H5 | one Class F claim >20 chars clears **all** anti-cheat findings | `src/aiv/lib/validators/anti_cheat.py:203-209` | ✅ Confirmed |
| — | "70.75% production-code coverage" | `python -m pytest --cov=aiv` re-run on `main` | ✅ Reproduced: **72%** (5073 stmts, 1403 miss) |

The 14 remaining high issues are recorded as **audit-asserted (runtime_confirmed by the
pipeline)** and were not independently re-executed for this PR; they are flagged as such below.

---

## Critical (2)

### C1 — Packet validation fails *open* in the pre-commit hook
- **Location:** `src/aiv/hooks/pre_commit.py:211-214`
- **Raw IDs:** F43
- **Verification:** ✅ independently confirmed against source
- **What:** `_validate_packet` is wrapped in `except Exception as exc: print("WARNING…"); return True`.
  Any transient error (subprocess failure, parse error, I/O) causes the central gate to **pass
  silently**. The enforcement point fails open instead of closed.
- **Why it matters:** This is the exact defect class AIV exists to prevent — a verification gate
  that can be made to approve unverified work by inducing an error. It is the audit's headline
  thesis ("the tool's own enforcement contains the class of defect it polices").
- **Plan ref:** `05-plan.md` — fix `F43` (gate must fail closed).

### C2 — Packet-pattern drift across the three enforcement surfaces
- **Location:** `.husky/pre-commit:60-61` vs `src/aiv/cli/main.py:1879` vs `src/aiv/hooks/pre_commit.py:342`
- **Raw IDs:** F96, F97, F98
- **Verification:** ✅ independently confirmed against source
- **What:** The bash husky hook recognizes only `^\.github/(aiv-packets/)?VERIFICATION_PACKET_.*\.md$`,
  while the Python pre-commit hook also accepts `EVIDENCE_*.md` (Layer-1 evidence files) and the
  CLI stages packets the bash hook will not classify as packets. The three surfaces disagree on
  what *is* a packet → bypass gaps depending on which gate runs.
- **Plan ref:** P2 (shared prefix module) + P3 (bring husky to parity / delegate to Python hook).

---

## High (21 distinct)

Grouped by root cause; cross-file duplicates of one root cause are merged.

### Security surfaces

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H1 | **Path traversal** — `.github/` prefix check defeated by `.github/x/../../../../etc/passwd`; resolved + read unconditionally | `guard/runner.py:191-204` | F14, F83, F146, F197 | ✅ source |
| H2 | **SSRF** — packet-supplied URLs passed to `urlopen` (HEAD) with no scheme allowlist, no loopback/link-local block | `lib/validators/links.py:163-176` (+ `test_validators.py:427`) | F15, F84, F147, F196, F19, F66, F90, F151, F202, F203 | ✅ source |
| H5 | **Anti-cheat blanket-clear** — any single Class F claim >20 chars marks *every* anti-cheat finding as justified, regardless of scope | `lib/validators/anti_cheat.py:203-209` | F134, F187 | ✅ source |
| H10 | SVP verifier identity is self-asserted via CLI arg, no authentication | `test_svp_full_workflow.py:387` | F91, F94 | audit-asserted |

### Enforcement / bypass

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H4 | `aiv close` commits the packet with `git commit --no-verify`, bypassing the hook it installs | `cli/main.py:1236-1238` | F69, F209, F17, F48, F87, F99, F26, F149, F6 | ✅ source |
| H9 | guard `_inspect_class_a_run` does not check the CI run's *conclusion* — a failed run can satisfy Class A | `guard/runner.py:336-365` | F135 | audit-asserted |
| H12 | temp files leaked in exception paths inside `_validate_packet` | `hooks/pre_commit.py:155-214` | F113, F175 | audit-asserted |

### Tier → evidence-class rubric drift (one logical defect, three surfaces)

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H3 | R1 rubric documents `{A,B}` while pipeline enforces `{A,B,E}` | `lib/validators/pipeline.py:183` | F159, F23, F24 | ✅ source |
| H3b | R3 rubric brackets D and F as optional; pipeline enforces all six | `hooks/pre_commit.py:237` | F24 | audit-asserted |
| H3c | husky `PACKET_PATTERN` omits Layer-1 `EVIDENCE_*.md`, diverging from Python hook | `.husky/pre-commit:61` | F210 | ✅ source (see C2) |

> P1 in the plan unifies all tier-drift findings (F23/F24/F159/F212/F228/F229/F41/F112) behind a
> single canonical `_TIER_REQUIRED` map. Treat H3/H3b/H3c as one work item.

### Error handling — silent failures that fabricate or drop evidence

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H6 | `github_api._request` / `_request_bytes` don't catch `URLError`; `list_pr_files` returns a *partial* file list on pagination error | `guard/github_api.py:51-117` | F44, F45, F115, F174, F177, F178, F237 | audit-asserted |
| H7 | `_run_git` claims "never raises" but omits try/except (FileNotFoundError, TimeoutExpired) | `lib/evidence_collector.py:249-255` | F114, F173, F232, F52 | audit-asserted |
| H8 | `aiv close` silently fabricates empty claims when evidence files are unreadable | `cli/main.py:1085` | F49, F117, F118, F238 | audit-asserted |
| H11 | `collect_class_b` emits non-functional GitHub permalinks when `git rev-parse` fails | `lib/evidence_collector.py:283-285` | F47, F54 | audit-asserted |

### Dead code

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H13 | `EvidenceValidator.validate_file_type_triggers` is never called | `lib/validators/evidence.py:261` | F46, F59, F158, F217 | audit-asserted |

### Test-suite integrity (assertions/docstrings that contradict themselves)

| # | Issue | Location | Raw IDs | Verified |
|---|---|---|---|---|
| H14 | `or` instead of `and` in unlinked-evidence-consumption assertion | `test_validators.py:608` | F8, F78, F141 | audit-asserted |
| H15 | OR-logic assertion contradicts its "Claims 2 AND 3 must differ" comment | `test_validators.py:606` | F226, F109, F166 | audit-asserted |
| H16 | test name/docstring say "main should NOT be mutable" but asserts it **is** mutable | `test_models.py:296` | F222, F38, F143 | audit-asserted |
| H17 | Phase-4 docstring claims JSON injection but code runs a CLI command | `test_svp_full_workflow.py:321` | F104, F220, F35, F36, F105, F164, F165, F221 | audit-asserted |
| H18 | `test_template_is_not_packet` contradicts its own assertion | `test_pre_commit_hook.py:36` | F106 | audit-asserted |

> The test-integrity cluster (H14–H18) matters because these are the tests that are supposed to
> *pin* the verifier's behavior. A self-contradicting assertion provides false assurance — the
> green suite does not mean what it appears to mean.

---

## Medium / Low / Info (summary)

Full detail in [`02-static-audit.md`](02-static-audit.md) and [`raw/stage2.json.md`](raw/stage2.json.md).
Distinct-issue counts after dedup:

| Severity | Distinct issues | Raw IDs | Dominant themes |
|---|---:|---:|---|
| Medium | 66 | 97 | correctness (13), doc/code drift (16), error-handling (8), injection (5), resource handling (4), claim-not-verified (3) |
| Low | 53 | 72 | dead-code (10), correctness (10), doc (6), error-handling (4), logic-bug (4), injection (3) |
| Info | 5 | 5 | one each: correctness, injection, logic-error, path-traversal, dead-code |

None of the medium/low/info items were independently re-verified for this PR.

---

## How to read the raw evidence

- [`02-static-audit.md`](02-static-audit.md) — every finding with full evidence text (385 KB).
- [`raw/stage2.json.md`](raw/stage2.json.md) — machine-readable findings (`id`, `severity`, `class`,
  `location`, `evidence`, `status`, `runtime_confirmed`).
- [`raw/distinct-issues.json.md`](raw/distinct-issues.json.md) — the dedup clustering used to produce
  this document (each cluster lists its member raw IDs).
- [`05-plan.md`](05-plan.md) — the 79-item remediation plan keyed to these findings (security-first).

## Caveats carried from the audit

1. **Severity is the auditor's own calibration.** H1/H2 are real but bounded in exploitability
   (the attacker must control a PR body or packet content fed to the guard; the SSRF is HEAD-only).
   "High" is defensible but context-dependent — these surfaces are not internet-facing by default.
2. **"audit-asserted" ≠ unverified-by-the-pipeline.** 244/251 raw findings carry
   `runtime_confirmed: true` from the pipeline's own execution pass; "audit-asserted" here means
   only that *this PR's* independent re-check did not separately re-execute them.
3. **2 plan items did not converge** (P77 `manifest.py` dead code; P79 the "quine" goal-gap) and
   need a human decision — see `05-plan.md`.
