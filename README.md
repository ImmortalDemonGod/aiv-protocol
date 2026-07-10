# AIV Protocol

**Auditable Verification Standard for AI-Assisted Code Changes**

---

## What Is AIV?

AIV is a formal specification for proving that code changes — especially those authored or assisted by AI — were verified with immutable, auditable evidence before deployment.

In a world where AI writes 60–80% of code, organizations need more than green CI badges. AIV replaces "someone reviewed it" with **"here is the documented, immutable evidence of what was verified, by whom, and when."**

## The Problem

AI-assisted development increases code throughput beyond what humans can reliably comprehend line-by-line. Without structured verification:

- **Orphan Code** — Logic exists in repositories but in no human's mental model
- **Debug Inability** — Engineers cannot troubleshoot code they didn't understand when approving
- **Verification Theater** — Green CI badges provide false assurance without semantic comprehension
- **Cognitive Debt** — Accumulated unverified changes compound into systemic fragility

This isn't theoretical. During this project's own AI audit, we observed the **Hallucination Cascade**: an AI predicted a nonexistent function, "mentally traced" its execution, wrote a falsification scenario testing it, and produced a perfectly valid verification session describing a reality that didn't exist. Every step looked correct. None of it was real. ([Full audit →](#empirically-validated-the-ai-first-pass-proof))

## The v1.0 Bootstrap: 331 Commits in 10 Hours 47 Minutes

The most common objection to verification protocols is that they kill velocity. This project is the counter-evidence.

The **v1.0 kernel** of this codebase — the parser, validators, guard, SVP suite, CLI, and all verification packets — was built in a single **11-hour session** ([`v1.0-genesis`](https://github.com/ImmortalDemonGod/aiv-protocol/releases/tag/v1.0-genesis)).

| Metric | Value |
| --- | --- |
| Sprint commits (excludes 2 pre-existing spec commits) | **331** |
| Wall-clock time | **10 h 47 min** (Feb 6 4:02 PM → Feb 7 2:49 AM) |
| Commit rate | **30.7 commits/hour** (~1 every 1 min 57 sec) |
| Python source + tests | **12,960 lines** across 47 files |
| Verification artifacts (packets, docs, specs) | **15,849 lines** across 87 files |
| Config (yml, toml, json) | **4,916 lines** across 9 files |
| **Total output** | **33,725 lines** across 143 files |
| Tests passing | **454** (unit + integration) |
| Verification packets | **74** (+ 2 templates) |

47% of total output was verification artifacts. The other 53% — source code and tests — was higher quality *because* of it. Every number is reproducible from `git log`. Stats reflect the `v1.0-genesis` tag.

### Why It Didn't Slow Down

The atomic commit strategy (1 functional file + 1 verification packet) **enabled** this speed:

1. **Externalized context** — Instead of holding 30 files in your head, you verify *one* file and its evidence at a time. The packet is your working memory on disk.
2. **No regression loops** — Strict tests and evidence requirements catch errors at the commit gate, not 4 hours and 200 commits later.
3. **AI amplification** — AI generates code at superhuman speed. AIV forces every generated artifact through an evidence checkpoint, converting raw throughput into *verified* throughput.

### The Quine Property

This project used the AIV protocol to build the AIV protocol. The fact that it survived 331 atomic commits at 30.7/hour — with pre-commit enforcement active the entire time — is a self-referential proof that the overhead is negligible when the alternative is unverified chaos.

### Limitations

This is a greenfield project built by one developer + AI. The velocity claim is that AIV overhead was negligible *relative to the same project without it* — not that these exact numbers transfer to a 50-person team with a legacy codebase. Multi-team adoption is a harder problem; the risk-tier system (R0–R3) and separation-of-duties requirements are designed to scale to that context without imposing R3-level ceremony on R0 changes.

## Empirically Validated: The AI First-Pass Proof

We gave an AI 3 change sets to verify using the SVP protocol (which works against PRs, feature branches, or any scoped change), then audited every claim it produced. The results define the core value proposition.

### The Scorecard

| SVP Phase | Accuracy | Takeaway |
| --- | --- | --- |
| **Adversarial Probe** (bug hunting) | **100%** (11/11) | Found 8 real bugs that 371 unit tests missed |
| **Trace** (execution-verified) | 100% (10/10) | Accurate when forced to execute |
| **Trace** (code-read only) | 87% (13/15) | Misread complex conditionals without execution |
| **Prediction** (architecture) | 74% (22/31) | Hallucinated functions that don't exist |
| **Falsification** (claim validation) | **40%** (8/20) | Parroted wrong numbers; verified theater, not logic |

### The Core Discovery: Hunter vs. Validator

The AI is a **superb Hunter** but a **dangerous Validator**.

- **As Hunter** (Probe phase — 100%): Reading code adversarially, the AI found logic collisions, missing regex patterns, hardcoded assumptions, and a header injection vulnerability. Every finding was real.
- **As Validator** (Falsification phase — 40%): Attempting to "prove" claims true, the AI defaulted to pattern matching — repeating "12 models" from its own prediction even though the code had 13.

### AIV Is a Hallucination Firewall

An AI can hallucinate a function, but it cannot hallucinate a **Class A artifact** (a URL to a passing CI run) or a **Class B permalink** to a file that doesn't exist. The evidence class taxonomy forces every claim to be grounded in artifacts that exist in reality, making phantom approvals — an approval an AI fabricates by citing evidence that does not exist — structurally impossible. (This closes the *hallucination* path. It does not claim to prevent two colluding humans from signing off; that is a separate axis the protocol handles through Separation of Duties and an auditable trail — accountability, not prevention.)

The audit also revealed the **Hallucination Cascade** — a recursive failure loop where an AI predicts a nonexistent function, "mentally traces" it, writes a falsification scenario testing it, and produces a perfectly valid JSON session describing a reality that doesn't exist. Artifact-based evidence classes break this loop at step one.

As models develop stronger internal reasoning capabilities, this risk increases — a model that can "think" more convincingly can also hallucinate more convincingly. AIV evidence classes are the external grounding wire.

### The Honest AI Protocol

These findings produced three protocol rules that harden SVP against AI yes-men:

| Rule | Enforcement |
| --- | --- |
| **S015** — Execution Trace | AI sessions must include `verified_output` from actual execution; mental simulation is banned |
| **S016** — Falsification-as-Code | AI falsification scenarios must be executable pytest snippets, not prose |
| **Adversarial Primacy** | The AI's primary deliverable is the Adversarial Report (probe findings), not approval |

Full details: [`.svp/AUDIT_AI_FIRST_PASS.md`](.svp/AUDIT_AI_FIRST_PASS.md)

## Adopting AIV in Your Project

### 1. Install

```bash
# From PyPI (coming soon) or from git:
pip install git+https://github.com/ImmortalDemonGod/aiv-protocol.git

# Or for local development of the protocol itself:
pip install -e ".[dev]"
```

### 2. Initialize

```bash
cd your-project
aiv init
```

This creates:
- **`.aiv.yml`** — Configuration file (strict mode enabled by default)
- **`.github/aiv-packets/`** — Directory for Layer 2 verification packets (per-change)
- **`.github/aiv-evidence/`** — Directory for Layer 1 evidence files (per-file)
- **`.git/hooks/pre-commit`** — Atomic commit enforcement hook
- **`.git/hooks/pre-push`** — Catches commits that bypassed pre-commit via `--no-verify`

Use `aiv init --no-hook` to skip hook installation if you prefer manual enforcement.

### 3. The Workflow

AIV uses a **Two-Layer Architecture**:
- **Layer 1 (per-file):** Each `aiv commit` generates an evidence file (`EVIDENCE_*.md`) with collected proof
- **Layer 2 (per-change):** `aiv close` aggregates all evidence into a verification packet (`PACKET_*.md`)

#### Quickstart (Recommended)

```bash
# 1. Start a tracked change
aiv begin auth-fix --description "Handle expired JWT tokens"

# 2. Commit files with evidence collection
aiv commit src/auth.py \
    -m "fix(auth): handle expired tokens" \
    -t R1 \
    -c "TokenValidator rejects expired tokens with 401" \
    -i "https://github.com/org/repo/issues/42" \
    --requirement "Issue #42 requires expired tokens return 401" \
    -r "Standard bug fix in auth module" \
    -s "Handle expired JWT tokens with proper 401 response"

# 3. Check progress at any time
aiv status

# 4. Close the change — generates the Layer 2 packet
aiv close --requirement "Issue #42 requires expired tokens return 401"

# 5. Push
git push
```

#### What Each Step Does

**`aiv begin <name>`** opens a change context (`.aiv/change.json`, gitignored). While active:
- The pre-commit hook allows multi-file commits (no 1:1 atomic rule)
- Each `aiv commit` is tracked in the change context

**`aiv commit <file>`** collects evidence by running real tools and writes it to `.github/aiv-evidence/EVIDENCE_*.md`:
- **Class B:** SHA-pinned line-range permalinks from `git diff --cached`
- **Class A:** pytest results + per-symbol test coverage (AST-based, Python only)
- **Class C (R2+):** Anti-cheat scan — deleted assertions, deleted test files, skip markers
- **Class F (R2+):** Test file provenance — git log chain-of-custody

You provide: claims (`-c`), intent URL (`-i`), rationale (`-r`), summary (`-s`).
The tool collects: the proof.

**`aiv close`** reads the change context, aggregates all evidence references into a Layer 2 packet (`PACKET_<name>.md`), validates it, and commits it. The packet links to each evidence file by commit SHA.

**`aiv abandon`** discards the change context without generating a packet. Evidence files remain.

> **Note:** Per-symbol test coverage analysis (AST-based) works for **Python files only**. Non-Python files get grep-based test discovery. The rest of `aiv commit` (Class B permalinks, anti-cheat, provenance) works for any language.

#### `aiv commit` Flag Reference

| Flag | Required | Description |
|------|----------|-------------|
| `--claim` / `-c` | Yes (repeatable) | Falsifiable claim about the change |
| `--intent` / `-i` | Yes | Class E: URL to spec/issue/directive |
| `--requirement` | Yes | Which specific requirement the URL satisfies |
| `--rationale` / `-r` | Yes | Why this risk tier was chosen |
| `--summary` / `-s` | Yes | One-line summary of the change |
| `--tier` / `-t` | No (default: R1) | Risk tier: R0, R1, R2, R3 |
| `--skip-checks` | No | Skip pytest/ruff/mypy (**R0 only** — blocked for R1+) |
| `--skip-reason` | With `--skip-checks` | Documents why checks were skipped (stamped into evidence) |
| `--dry-run` | No | Generate + validate, don't commit |

#### Claim Verification Gate

`aiv commit` binds each claim to test coverage via AST analysis. If too many claims lack test evidence, the commit is **blocked**:

- **R1/R2:** Blocked when >50% of bindable claims are UNVERIFIED
- **R3:** Blocked on ANY unverified claim
- **R0:** No gate (checks are skipped)

There is no `--force` bypass. If blocked, your options are:
1. **Write tests** that call the uncovered symbol(s)
2. **Downgrade to R0** (`--tier R0 --skip-checks --skip-reason "..."`) if the change is truly trivial

#### Alternative Workflows

**Single-file atomic commits (without `aiv begin`):** `aiv commit` works standalone — it generates an evidence file and commits atomically (1 functional file + 1 evidence file). The pre-commit hook enforces this pattern when no change context is active.

**Manual packet creation:** Use `aiv generate` to scaffold a packet template, edit it, then commit:

```bash
aiv generate auth-fix --tier R1
# Edit the generated packet, then:
git add src/auth.py .github/aiv-packets/VERIFICATION_PACKET_AUTH_FIX.md
git commit -m "fix(auth): handle expired tokens"
```

### 4. Validation Commands

```bash
# Validate a verification packet through the 8-stage pipeline
aiv check .github/aiv-packets/VERIFICATION_PACKET_AUTH_FIX.md

# Lenient mode (warnings don't block)
aiv check --no-strict packet.md

# With anti-cheat diff scanning
aiv check packet.md --diff changes.patch

# With link vitality checks (HTTP HEAD probes on evidence URLs)
aiv check packet.md --audit-links

# Audit all packets for quality issues (TODO remnants, missing SHAs, etc.)
aiv audit

# Auto-fix common audit issues (backfill commit SHAs, pin URLs)
aiv audit --fix
```

### 5. SVP Cognitive Verification (Optional)

```bash
aiv svp predict 42 --verifier alice --test-file tests/test_auth.py --approach "..." --edge-cases "..."
aiv svp trace 42 --verifier alice --function src/auth.py::login --notes "..." --edge-case "..." --predicted-output "..."
aiv svp probe 42 --verifier alice --assessment "..." --why-question "..."
aiv svp status 42
```

Full protocol reference: [`SPECIFICATION.md`](SPECIFICATION.md)

## CLI Commands

### `aiv check`

Validates a verification packet through an 8-stage pipeline:

1. **Parse** — Markdown → structured `VerificationPacket`
2. **Structure** — Completeness and quality checks
3. **Links** — SHA-pinned immutability enforcement + link vitality (E021)
4. **Evidence** — Class-specific requirement validation
5. **Risk-Tier** — Evidence requirements per classification (R0–R3)
6. **Zero-Touch** — Reproduction instruction compliance
7. **Anti-Cheat** — Git diff scanning for test manipulation
8. **Cross-Reference** — Anti-cheat findings vs. packet justifications

```
$ aiv check .github/aiv-packets/VERIFICATION_PACKET_GITIGNORE.md
+-------------------------------- [OK] Result --------------------------------+
| Validation Passed                                                           |
| Packet version: 2.1                                                         |
| Claims: 3                                                                   |
+-----------------------------------------------------------------------------+
```

**Key flags:**

- `--no-strict` — Lenient mode (strict is the default; warnings don't block in lenient)
- `--diff <path>` — Enable anti-cheat scanning against a git diff
- `--audit-links` — Verify evidence URLs are reachable via HTTP HEAD (E021). Dead links — pointing to deleted files, force-pushed commits, or renamed repos — are flagged as blocking errors. Unreachable links (network failures) are flagged as warnings.

### `aiv quickstart`

Prints the complete AIV workflow reference — from `init` to `push`. Designed for LLMs and new users who need the full picture in one command:

```bash
aiv quickstart
```

### `aiv init`

Initializes AIV in a repository: creates `.aiv.yml`, `.github/aiv-packets/`, `.github/aiv-evidence/`, and installs pre-commit + pre-push hooks.

### `aiv begin`

Opens a change context for tracking a multi-commit logical change:

```bash
aiv begin auth-fix --description "Handle expired JWT tokens"
aiv begin payments-v2 --mode pr    # Feature branch mode
```

While a change is active, the pre-commit hook relaxes the 1:1 atomic rule, allowing multi-file commits. Each `aiv commit` is tracked in `.aiv/change.json` (gitignored).

### `aiv commit`

Collects evidence and commits a single functional file atomically:

```bash
aiv commit src/auth.py \
    -m "fix(auth): handle expired tokens" \
    -c "TokenValidator rejects expired tokens with 401" \
    -i "https://github.com/org/repo/issues/42" \
    --requirement "Issue #42 requires expired tokens return 401" \
    -r "Standard bug fix in auth module" \
    -s "Handle expired JWT tokens with proper 401 response"
```

Generates `.github/aiv-evidence/EVIDENCE_*.md` with Class A/B/C/F evidence collected from real tools.

### `aiv close`

Closes the active change and generates a Layer 2 verification packet:

```bash
aiv close --requirement "Issue #42 requires expired tokens return 401"
aiv close --include-untracked   # Include commits made without aiv commit
aiv close --tier R2 --rationale "Auth module changes"
```

### `aiv status`

Shows the active change context — tracked commits, files, and evidence files.

### `aiv abandon`

Discards the change context without generating a packet. Evidence files remain in git.

### `aiv audit`

Audits all verification packets AND evidence files for quality issues the validation pipeline does not catch:

- Commit SHA traceability (`COMMIT_PENDING`)
- Class E link immutability
- TODO remnants
- Missing Class F for bug-fix claims
- **Unverified claims** (`EVIDENCE_UNVERIFIED_CLAIM`) — flags each FAIL UNVERIFIED in the Claim Verification Matrix
- **High unverified rate** (`EVIDENCE_HIGH_UNVERIFIED`) — flags evidence files where >50% of claims are unverified
- **Manual review needed** (`EVIDENCE_MANUAL_REVIEW`) — flags claims that need human review

```bash
# Audit all packets
aiv audit

# Audit with auto-fix
aiv audit --fix

# Audit a specific directory
aiv audit .github/aiv-packets --fix
```

### `aiv generate`

Scaffolds a new verification packet with tier-appropriate evidence sections:

```bash
# Generate an R2 packet with auto-detected git scope
aiv generate auth-fix --tier R2

# Generate with rationale
aiv generate cleanup --tier R0 --rationale "Remove dead code"
```

Auto-detects staged/unstaged files via `git diff` and populates the scope inventory.

### `aiv svp` (SVP Protocol Suite)

Cognitive verification commands for the Systematic Verifier Protocol:

| Command | Phase | Description |
| --- | --- | --- |
| `aiv svp status <PR>` | — | Show SVP completion status and phase checklist |
| `aiv svp predict <PR>` | 1 | Record a Black Box Prediction before seeing the diff |
| `aiv svp trace <PR>` | 2 | Record a Mental Trace (simulate execution flow) |
| `aiv svp probe <PR>` | 3 | Submit an Adversarial Probe checklist |
| `aiv svp ownership <PR>` | 4 | Record an Ownership Lock commit |
| `aiv svp validate <PR>` | — | Validate session completeness (JSON output) |
| `aiv svp rating <ID>` | — | Calculate and display verifier ELO rating |

## Evidence Classes (A–F)

| Class | Name         | Proves                                         | R0 | R1 | R2 | R3 |
| ----- | ------------ | ---------------------------------------------- |:--:|:--:|:--:|:--:|
| **A** | Execution    | Tests passed in a defined environment          | ✓  | ✓  | ✓  | ✓  |
| **B** | Referential  | Traceability to exact code locations (SHA-pinned) | ✓  | ✓  | ✓  | ✓  |
| **C** | Negative     | Absence of disallowed patterns                 |    | ○  | ✓  | ✓  |
| **D** | Differential | Change impact beyond test coverage             |    |    | ○  | ✓  |
| **E** | Intent       | Alignment with upstream requirement            |    | ✓  | ✓  | ✓  |
| **F** | Provenance   | Artifact integrity and chain-of-custody        |    |    | ○  | ✓  |

**Legend:** ✓ = Required | ○ = Optional

### What Valid Evidence Looks Like

**Class A (Execution)** — Link to a CI run or paste local test output:
```markdown
- CI Run: https://github.com/org/repo/actions/runs/12345678
- Local: pytest — 454 passed, 0 failed in 38s
```

**Class B (Referential)** — SHA-pinned GitHub permalinks (branch URLs like `/blob/main/` are rejected):
```markdown
**Scope Inventory** (SHA: [`abc1234`](https://github.com/org/repo/tree/abc1234def5678))
- Modified: [`src/auth.py#L42-L58`](https://github.com/org/repo/blob/abc1234/src/auth.py#L42-L58)
```

**Class C (Negative)** — Describe what you searched for and didn't find:
```markdown
- Searched all test files for deleted assertions or `@pytest.mark.skip` additions — none found.
- Ran full regression suite (454 tests) — no failures.
```

**Class D (Differential)** — Show what changed in API, state, or config:
```markdown
- API surface: `login()` signature unchanged. New optional param `timeout: int = 30` added.
- No breaking changes to existing callers.
```

**Class E (Intent)** — SHA-pinned link to the spec, issue, or directive that motivated the change:
```markdown
- **Link:** [`SPECIFICATION.md#L120-L135`](https://github.com/org/repo/blob/abc1234/SPECIFICATION.md#L120-L135)
- **Requirements Verified:** Section 4.2 requires token expiry handling.
```

**Class F (Provenance)** — Git log chain-of-custody for covering test files:
```markdown
**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/unit/test_auth.py` | 12 | alice (a1b2c3d) | bob (e4f5g6h) | 47 |
| `tests/unit/test_tokens.py` | 5 | alice (i9j0k1l) | alice (m2n3o4p) | 23 |
```

Full specification: [`SPECIFICATION.md`](SPECIFICATION.md)

### Error Code Reference

When `aiv check` rejects a packet, it reports error codes like `[E004]`. The most common:

| Code | Severity | What It Means | Fix |
|------|----------|---------------|-----|
| E001 | BLOCK | Packet parse failure | Use `aiv generate` or `aiv commit` to create a valid packet |
| E004 | BLOCK | Link not SHA-pinned | Replace `/blob/main/` with `/blob/<commit-sha>/` |
| E008 | BLOCK | Zero-Touch violation | Remove manual steps from reproduction instructions |
| E019 | BLOCK | Required evidence class missing | Add the missing class (R0/R1: A+B, R2: +C+E, R3: +D+F) |
| E011 | BLOCK | Test modification without justification | Add Class F explaining why tests changed |

Full reference: [`docs/ERROR_CODES.md`](docs/ERROR_CODES.md)

### Complete Minimal Packet (R1 Example)

This is what a valid, `aiv check`-passing R1 packet looks like. Generated by `aiv commit`:

```markdown
# AIV Verification Packet (v2.1)

**Commit:** `abc1234`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/auth.py"
  classification_rationale: "Standard bug fix in auth module"
  classified_by: "alice"
  classified_at: "2026-02-08T12:00:00Z"
```

## Claim(s)

1. TokenValidator rejects expired tokens with HTTP 401
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Issue #42](https://github.com/org/repo/issues/42)
- **Requirements Verified:** Token expiry must return 401

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`abc1234`](https://github.com/org/repo/tree/abc1234))

- [`src/auth.py#L42-L58`](https://github.com/org/repo/blob/abc1234/src/auth.py#L42-L58)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`TokenValidator.validate`** (L42-L58): PASS — 3 test(s) call `validate` directly
  - `tests/unit/test_auth.py::test_expired_token_returns_401`
  - `tests/unit/test_auth.py::test_valid_token_passes`
  - `tests/unit/test_auth.py::test_malformed_token_returns_400`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** clean

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | TokenValidator rejects expired tokens with HTTP 401 | symbol | 3 test(s) call `validate` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted | structural | Class C: all structural indicators clean | PASS VERIFIED |

**Verdict summary:** 2 verified, 0 unverified, 0 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Handle expired JWT tokens with proper 401 response
```

### Cognitive Verification (Class G — Optional)

| Phase | Name                | Purpose                                      |
| ----- | ------------------- | -------------------------------------------- |
| 1     | Black Box Prediction | Predict implementation before seeing the diff |
| 2     | Mental Trace         | Simulate execution flow without running code  |
| 3     | Adversarial Probe    | Hunt for AI hallucinations and edge cases     |
| 4     | Ownership Lock       | Push a commit proving you touched the code    |

## Risk Tiers

| Tier   | Name    | SoD      | Examples                                    |
| ------ | ------- | -------- | ------------------------------------------- |
| **R0** | Trivial | S0 (Self)| Docs, comments, formatting                  |
| **R1** | Low     | S0 (Self)| Isolated bug fixes, minor refactors         |
| **R2** | Medium  | S1 (Ind.)| API changes, config, dependency upgrades    |
| **R3** | High    | S1 (Ind.)| Auth, crypto, payments, PII, audit logging  |

## Repository Structure

```bash
aiv-protocol/
├── src/aiv/                         # Python implementation
│   ├── cli/main.py                  # CLI entry point (typer)
│   ├── lib/
│   │   ├── models.py                # Pydantic models (frozen, typed)
│   │   ├── parser.py                # Markdown → VerificationPacket
│   │   ├── config.py                # .aiv.yml configuration
│   │   ├── errors.py                # Exception hierarchy
│   │   ├── auditor.py               # Packet quality auditor
│   │   ├── evidence_collector.py    # AST-based evidence collection for aiv commit
│   │   ├── change.py                # Change lifecycle (begin/close/abandon/status)
│   │   └── validators/
│   │       ├── pipeline.py          # 8-stage validation orchestrator
│   │       ├── base.py              # Base validator class
│   │       ├── structure.py         # Packet completeness
│   │       ├── evidence.py          # Class-specific rules (E010–E022)
│   │       ├── links.py             # SHA-pinned immutability + link vitality (E021)
│   │       ├── zero_touch.py        # Zero-Touch mandate (E008)
│   │       └── anti_cheat.py        # Test manipulation scanner (E011)
│   ├── hooks/
│   │   ├── pre_commit.py            # Pre-commit: atomic commit + change-context gate
│   │   └── pre_push.py              # Pre-push: catches --no-verify bypass + unclosed changes
│   ├── guard/                       # Python AIV Guard (CI module)
│   │   ├── models.py                # Guard-specific Pydantic models
│   │   ├── github_api.py            # GitHub API client
│   │   ├── canonical.py             # Canonical packet validation
│   │   ├── manifest.py              # CI artifact manifest validation
│   │   ├── runner.py                # Guard orchestrator
│   │   └── __main__.py              # python -m aiv.guard support
│   ├── svp/                         # SVP Protocol Suite
│   │   ├── cli/main.py              # SVP CLI commands (typer)
│   │   └── lib/
│   │       ├── models.py            # SVP Pydantic models (sessions, ratings)
│   │       ├── rating.py            # Verifier ELO rating engine
│   │       └── validators/
│   │           └── session.py       # Session rules S001–S016
│   └── __main__.py                  # python -m aiv support
├── tests/                           # 580+ tests (unit + integration)
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_parser.py
│   │   ├── test_validators.py
│   │   ├── test_guard.py            # Guard module tests
│   │   ├── test_svp.py              # SVP module tests
│   │   ├── test_auditor.py          # Auditor module tests
│   │   ├── test_evidence_collector.py # Evidence collector tests
│   │   ├── test_change.py           # Change lifecycle tests
│   │   ├── test_pre_commit_hook.py  # Pre-commit hook tests
│   │   ├── test_pre_push_hook.py    # Pre-push hook tests
│   │   └── test_coverage.py         # Coverage gap tests
│   └── integration/
│       ├── test_full_workflow.py
│       ├── test_e2e_compliance.py   # E2E compliance tests
│       └── test_svp_full_workflow.py # SVP integration tests
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard-python.yml     # PR validation — Python (live)
│   │   ├── ci.yml                   # CI: lint, format, type-check, test
│   │   └── verify-architecture.yml  # Evidence generation (disabled)
│   ├── aiv-packets/                 # Layer 2: per-change verification packets
│   └── aiv-evidence/                # Layer 1: per-file evidence files
├── docs/
│   ├── TWO_LAYER_VERIFICATION_ARCHITECTURE.md  # Two-Layer Architecture design doc
│   ├── AIV_SVP_PROTOCOL_USER_STORY.md          # Problem statement and user story
│   ├── CLAIM_AWARE_EVIDENCE_PLAN.md            # Evidence collector design doc
│   └── specs/
│       ├── AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md
│       ├── SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md
│       └── E2E_COMPLIANCE_TEST_SUITE_SPEC.md
├── .svp/                            # SVP session data & audit reports
│   ├── AUDIT_AI_FIRST_PASS.md       # AI First-Pass empirical audit
│   ├── session-pr*.json             # SVP verification sessions
│   └── ratings.json                 # Verifier ELO ratings
├── scripts/
│   ├── map_packets.py               # Source-file-to-packet mapping generator
│   └── migrate_two_layer.py         # Migration script for Two-Layer Architecture
├── .husky/pre-commit                # Legacy atomic commit enforcement (JS)
├── FILE_PACKET_MAP.md               # Evidence index: file ↔ packet mapping
├── FILE_PACKET_MAP.json             # Machine-readable mapping (same data)
├── SPECIFICATION.md                 # Canonical AIV standard (v1.0.0)
├── AUDIT_REPORT.md                  # Comprehensive codebase audit
├── CHANGELOG.md                     # Version history
└── pyproject.toml                   # Build config (hatchling)
```

## Key Documents

| Document | Description |
| --- | --- |
| [`SPECIFICATION.md`](SPECIFICATION.md) | Canonical AIV standard — normative, RFC-style, formal validation rules |
| [`AUDIT_REPORT.md`](AUDIT_REPORT.md) | Comprehensive codebase audit with cross-analysis |
| [`docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md`](docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md) | AIV automation suite implementation spec |
| [`docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md`](docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md) | SVP cognitive verification suite implementation spec |
| [`docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md`](docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md) | End-to-end compliance test suite specification |
| [`.svp/AUDIT_AI_FIRST_PASS.md`](.svp/AUDIT_AI_FIRST_PASS.md) | AI First-Pass audit — empirical proof of Hunter vs. Validator dichotomy |
| [`FILE_PACKET_MAP.md`](FILE_PACKET_MAP.md) | Evidence index — maps every source file to its verification packets (and vice versa) |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history and release notes |

## Enforcement (Live)

Four enforcement layers, all active:

1. **Pre-commit hook** — Enforces atomic commits (1 functional file + 1 evidence file). With an active change context (`aiv begin`), allows multi-file commits. On protected branches without a change context, blocks functional files that lack a paired evidence file.
2. **Pre-push hook** — Catches commits that bypassed the pre-commit hook via `git commit --no-verify`. Also blocks pushes on protected branches with unclosed change contexts.
3. **`aiv check` CLI** — Local validation with 8-stage pipeline, strict mode, anti-cheat scanning, link vitality checks
4. **AIV Guard CI (Python)** — PR-level validation as a Python module (`src/aiv/guard/`): canonical packet validation, manifest verification, critical surface detection, SoD checks, and GitHub API integration

## Configuration

Create `.aiv.yml` in your repository root (or run `aiv init`):

```yaml
# AIV Protocol Configuration
version: "1.0"
strict_mode: true
```

### Hook Configuration (Important for Non-Standard Layouts)

The pre-commit hook classifies files as "functional" (requiring a verification packet) based on path prefixes. The defaults are:

```
src/  lib/  app/  pkg/  cmd/  internal/  engine/  infrastructure/  scripts/  tests/  .github/workflows/  .husky/
```

Plus root files: `pyproject.toml`, `setup.py`, `package.json`, `.gitignore`, etc.

**If your project uses a different layout** (e.g., `mypackage/` or `backend/`), the hook won't recognize those files as functional and will silently allow commits without packets. Add a `hook:` section to `.aiv.yml`:

```yaml
hook:
  functional_prefixes:
    - "src/"
    - "mypackage/"
    - "backend/"
    - "tests/"
  functional_root_files:
    - "pyproject.toml"
    - "Dockerfile"
```

## Design Principles

- **Zero-Touch** — Verifiers never run code locally; all evidence is artifact-based
- **Falsifiability** — Every rule produces deterministic pass/fail
- **Defense in Depth** — All external data is untrusted until validated
- **Separation of Concerns** — AIV validates evidence quality, not code quality
- **Immutability** — All links must be SHA-pinned; branch-based URLs are rejected

## Standards Alignment

| Standard               | AIV Alignment                                |
| ---------------------- | -------------------------------------------- |
| SOC 2 (CC8.1)          | Change management, testing evidence          |
| SLSA v1.0              | Build provenance, artifact integrity         |
| ISO 27001 (A.14.2)     | Secure development, change control           |
| NIST SSDF (PW.7, PW.8) | Code review, security testing               |
