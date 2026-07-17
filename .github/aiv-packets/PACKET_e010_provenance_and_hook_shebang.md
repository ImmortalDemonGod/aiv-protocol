# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/Black-Box-Research-Labs/aiv-protocol |
| **Change ID** | e010-provenance-and-hook-shebang |
| **Commits** | `21fde2f`, `16f2bd2` |
| **Head SHA** | `16f2bd2` |
| **Base SHA** | `55e1979` |
| **Created** | 2026-07-17T17:01:42Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Two isolated bug fixes: a validator false positive (E010) and the installed-hook interpreter pinning (#29). No API change; validator behavior only widens on packets that carry a filled Class F section."
  classified_by: "money-agent integration session"
  classified_at: "2026-07-17T17:01:42Z"
```

## Claims

1. `has_provenance_evidence` (src/aiv/lib/models.py) now consults `evidence_classes_present` in
   addition to per-claim class assignments, so E010 no longer blocks an honest packet whose
   `### Class F (Provenance)` section is filled but whose claims did not parse as
   PROVENANCE-classed.
2. Hooks installed by `aiv init` (src/aiv/cli/main.py) pin the interpreter aiv is running under
   (`sys.executable`) instead of PATH's `python3`, closing #29's silent
   ModuleNotFoundError-on-every-commit failure; whitespace-path fallback keeps the env form.
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class A (Execution)

A) Execution: full suite after both fixes: **739 passed, 22 skipped** (`python -m pytest tests -q`).
Regression demonstrations: (1) a downstream money-agent R3 packet containing "issue 6" in its
Class E text failed `aiv check --no-strict` with E010 before the models.py fix and passes after,
with its Class F section unchanged; (2) fresh `aiv init` in a scratch repo writes a pre-commit
hook whose first line is the absolute path of the owning interpreter (verified by reading
`.git/hooks/pre-commit` line 1), where it previously wrote `#!/usr/bin/env python3`.

### Class B (Referential)

B) Referential: commit `21fde2f` (models.py, `has_provenance_evidence`), commit `16f2bd2`
(cli/main.py, `_hook_shebang()` helper + both hook shims). The pre-existing model field consulted
by the fix is `VerificationPacket.evidence_classes_present` (models.py, "All evidence classes
found in evidence sections, regardless of claim assignment") — the fix uses the field for exactly
its documented meaning.

### Class F (Provenance)

F) Provenance: the change is content-addressed by its commits — `21fde2f` (models.py) and
`16f2bd2` (cli/main.py), head `16f2bd2` over base `55e1979`; each SHA binds the exact diff this
packet describes. Meta-note worth keeping: this packet is itself classified as a bug fix by the
E010 heuristic, so it validates **only because of the fix it ships** — under the pre-fix
validator, this Class F section (section-level, no PROVENANCE-classed claim) would not have
counted and the packet would have been blocked. Running `aiv check` on this packet with the fix
installed is therefore a self-demonstrating regression test.

### Class E (Intent Alignment)

E) Intent: #29 (init shebang) is an open tracked defect; the E010 false positive was surfaced by
the downstream money-agent R3 integration, whose harness now runs `aiv check` fail-closed on every
iteration packet and hit the false block on an honest packet. Both fixes remove a reason for
downstream consumers to carry local workarounds (money-agent's setup_sandbox.sh hook sed-repair
and its template's E010 trap note become deletable once a release carries these).

---

## Verification Methodology

Fixes were reproduced failing first (the downstream packet under E010; the hook shebang under a
venv whose interpreter is not first on PATH), then fixed, then re-verified passing, then the full
suite run. The E010 fix widens `has_provenance_evidence` for every consumer; call-site review
found E010 the sole consumer today — flagged for maintainer confirmation that the widened meaning
matches the field's intent.

## Honest limitations

`_hook_shebang()`'s whitespace fallback reintroduces the original PATH ambiguity for interpreters
installed under paths containing spaces — rare on dev machines, but such users keep the old
behavior. The E010 regression was demonstrated against a downstream packet, not added as an
upstream unit test; a maintainer may want a test pinning `evidence_classes_present`-only
provenance passing the bug-fix branch of EvidenceValidator.
