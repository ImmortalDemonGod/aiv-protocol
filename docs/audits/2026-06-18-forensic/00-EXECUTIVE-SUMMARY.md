# 00 — Executive Summary

_Forensic technical due-diligence audit of `aiv-protocol` · branch `claude/eloquent-goodall-sqfrhf` · generated 2026-06-18_

This is the human-readable synthesis of the five-stage forensic audit. The full evidence is in the
companion artifacts `01-understanding.md` … `05-plan.md`; machine-readable data is embedded in each.

## What ran

The full 5-stage forensic pipeline (`forensic_pipeline.mjs`, included) executed against this repository
over ~6.5 hours wall-clock, driving headless `claude -p` subagents with adversarial falsification gates
between stages. The run survived **two usage-limit interruptions and one container restart** via per-stage
checkpoint/resume plus a stdout-heartbeat fix (an idle worker was being reaped during long silent agent
windows). Every stage passed its adversarial stop-test. Commits were made locally to the working branch;
`git push` was 403-blocked in this environment, so durability was carried by out-of-band resume kits.

| Stage | Artifact | Result |
|---|---|---|
| 1 — Understanding | `01-understanding.md` | Full file inventory (the coverage denominator), architecture map, entry points, provisional intent |
| 2 — Static audit | `02-static-audit.md` | **251 findings** — 2 critical, 36 high, 108 medium, 90 low, 15 info; 250/251 upheld across 4 adversarial falsification rounds |
| 3 — Execution | `03-execution.md` | Real `pip install` + pytest + deep dependency pass → **70.75% production-code coverage**; findings runtime-confirmed/refined |
| 4 — Goal | `04-goal.md` | **6 candidate goals, 5 grounded 3/3** by an independent judge panel; external research ran (not blocked) |
| 5 — Plan | `05-plan.md` | **79 dependency-ordered change items**, each tied to a finding/goal-gap with a concrete verification signal |

## Headline finding

**The verification tool's own enforcement contains the class of defect AIV exists to prevent.**

- **CRITICAL — F43** (`src/aiv/hooks/pre_commit.py:212`): packet validation is wrapped in
  `except Exception: return True`, so any transient error makes the central gate **fail _open_** — it
  silently passes.
- **CRITICAL — F96** (`.husky/pre-commit:61` vs `cli/main.py:1879` vs `hooks/pre_commit.py:342`):
  packet-pattern drift means staged packets aren't consistently recognized across the three enforcement
  surfaces → bypass gaps.
- **HIGH — F14** (`src/aiv/guard/runner.py:191`): **path traversal** — the `.github/` prefix check is
  defeated by `.github/x/../../../../etc/passwd`.
- **HIGH — F15 / F19** (`src/aiv/lib/validators/links.py:163`): **SSRF** — `--audit-links` passes
  packet-supplied URLs straight to `urllib.urlopen` with no scheme allowlist and no loopback/link-local block.
- **HIGH — F23** (`src/aiv/hooks/pre_commit.py:240`): tier-requirement drift — the R1 rubric prints
  "A + B" while the pipeline enforces A + B + **E**.

Stage 3 confirmed the behavioral findings against real execution rather than trusting a green test suite.

## Grounded goal

As-built, the repository is **an enforceable AI-code-verification standard shipped in three forms**: a CLI
gate plus embeddable Python library, a formal specification treated as a first-class deliverable, and the
SVP (Systematic Verifier Protocol) subsystem with ELO-based verifier rating. The judge panel appropriately
**rejected** the "quine / proves-velocity-isn't-hurt" goal as `needs-human-confirm` (0/3) — it is a
narrative claim, not an as-built signal.

## The plan

79 items, security-first and dependency-ordered. Recommended start:

- **P1** — unify the tier→evidence-class requirement map (eliminates the drift findings F23/F24/…)
- **P3** — bring the husky bash hook to parity with the Python hook (or delegate to it)
- **P4** — canonicalize PR-body packet paths to close the path traversal (F14)
- **P5** — add an SSRF guard (scheme allowlist + loopback/link-local block) to the link validator (F15/F19)
- **P6** — validate/encode owner/repo parsed from the git remote

…and crucially, fix **F43** (fail-open packet validation) — the gate must fail _closed_.

## Honest caveats

1. **2 of 79 plan items did not converge** to unambiguous diff-targets after 2 attempts (`P77`:
   `manifest.py` dead code — invoke or delete; `P79`: the quine goal-gap). Flagged in `05`, not hidden;
   both need a human decision.
2. **Stage 2's optional 5th falsification round was finalized from the round-4-validated finding set**
   (already 250/251 upheld over 4 opus rounds) after infrastructure limits twice killed the redundant 5th
   round. Disclosed in `02`'s provenance note.
3. Cost was tracked, never gated (~$117 **API-equivalent** total across all sessions, dominated by Stage 2's
   adversarial rounds; real subscription draw is far lower).

## How to reproduce / resume

```bash
# from the repo root, with the audit/ directory restored:
node audit/forensic_pipeline.mjs            # resume from first incomplete stage
node audit/forensic_pipeline.mjs --fresh    # discard audit/ and re-run from scratch
node audit/forensic_pipeline.mjs --stage 3  # re-run exactly one stage
```

See `RESUME.md` for the full pause/resume procedure.
