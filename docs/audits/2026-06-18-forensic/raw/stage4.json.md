# stage4.json (verbatim)

> Raw audit artifact, wrapped in Markdown for fast-track-eligible tracking. Content below is byte-for-byte the original `stage4.json`. To extract: delete this header and the surrounding fence lines.

```json
{
  "candidates": [
    {
      "goal": "Define and enforce the AIV protocol: organize AI-assisted code changes into atomic 'verification packets' that must pass structured validation/audit before they can be committed, with enforcement made non-bypassable at the developer machine (git hooks) and in CI.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Project self-describes as an enforceable verification standard, not just a doc",
          "evidence": "pyproject.toml:8 description 'Auditable Verification Standard for AI-Assisted Code Changes'; README.md:9-11 frames AIV as replacing 'someone reviewed it' with immutable auditable evidence",
          "met": true
        },
        {
          "signal": "Local enforcement via installed git hooks",
          "evidence": "src/aiv/hooks/pre_commit.py and pre_push.py installed by `aiv init`; cli main.py exposes init/check/audit/commit/close/begin commands (src/aiv/cli/main.py:27-1339)",
          "met": true
        },
        {
          "signal": "CI enforcement gate runs protocol audit on push",
          "evidence": ".github/workflows/ci.yml protocol-audit job runs `aiv audit --commits 20`; aiv-guard-python.yml runs guard runner via src/aiv/guard/runner.py:393 main()",
          "met": true
        },
        {
          "signal": "Enforcement is genuinely non-bypassable for ALL commits",
          "evidence": "close command runs `git commit --no-verify` for the packet commit (src/aiv/cli/main.py ~line 1237), skipping _validate_packet/atomic-commit hook checks; top-findings document this compliance gap",
          "met": false
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Ship the AIV protocol in two consumable forms — a CLI gate (`aiv` console script) AND an embeddable Python library API — so other projects can both enforce and programmatically run validation.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Console-script entry point exposing the CLI",
          "evidence": "pyproject.toml:54-55 [project.scripts] aiv = 'aiv.cli.main:app'; also `python -m aiv` and `python -m aiv.guard` module entry points",
          "met": true
        },
        {
          "signal": "Curated public library API surface",
          "evidence": "src/aiv/__init__.py:10-40 exports AIVConfig, PacketParser, ValidationPipeline, VerificationPacket, RiskTier, EvidenceClass and core models via __all__",
          "met": true
        },
        {
          "signal": "Packaged for distribution as a typed wheel",
          "evidence": "pyproject.toml:63-64 hatch wheel packages ['src/aiv']; classifiers include 'Typing :: Typed' (pyproject.toml:26)",
          "met": true
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Formally specify the AIV protocol (risk tiers, evidence classes, error codes, two-layer architecture) as authoritative documentation/spec, treating the spec itself as a primary deliverable alongside the implementation.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Documentation is the largest file category in the inventory",
          "evidence": "Stage-1 inventory: 109 documentation + 58 generated artifacts vs 46 source + 20 test files (per task architecture summary)",
          "met": true
        },
        {
          "signal": "Dedicated normative spec documents exist",
          "evidence": "docs/ contains ERROR_CODES.md, TWO_LAYER_VERIFICATION_ARCHITECTURE.md, AIV_SVP_PROTOCOL_USER_STORY.md, CLAIM_AWARE_EVIDENCE_PLAN.md, docs/specs/",
          "met": true
        },
        {
          "signal": "Spec concepts are reified in code models",
          "evidence": "src/aiv/lib/models exports RiskTier, EvidenceClass, Severity, VerificationPacket (src/aiv/__init__.py:11-22)",
          "met": true
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Provide the SVP (Systematic Verifier Protocol) subsystem: a structured, evidence-backed predict/trace/probe/ownership/validate workflow with verifier ownership and ELO-based rating/tiering to make human verification accountable and gameable-resistant.",
      "status": "grounded",
      "signals": [
        {
          "signal": "SVP is a first-class sub-application with the full phase workflow",
          "evidence": "src/aiv/svp/cli/main.py:41-519 defines svp_app with status/predict/trace/probe/ownership/validate/rating commands; mounted via app.add_typer(svp_app, name='svp') at cli/main.py:27",
          "met": true
        },
        {
          "signal": "Verifier reputation modeled via tiers and ELO",
          "evidence": "VerifierTier / VerifierRating with from_elo thresholds and tiers NOVICE/COMPETENT exercised in test_validators tests (lines ~154-388, 883-886 per top-findings)",
          "met": true
        },
        {
          "signal": "Workflow guards against fabricated evidence (anti-cheat / hallucination cascade)",
          "evidence": "README.md:21 documents the 'Hallucination Cascade'; anti-cheat deleted-files / diff line-number scanning tests referenced in top-findings (test_validators, scanner.scan_diff)",
          "met": true
        },
        {
          "signal": "Rating boundary semantics are fully consistent as-built",
          "evidence": "top-findings show conflicting initial-tier assertions: from_elo(500)=COMPETENT vs initial-rating tests asserting NOVICE at elo 500 — boundary spec is internally inconsistent",
          "met": false
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Deliver enforcement as a two-layer architecture — Layer 1 pre-commit structural/packet checks and Layer 2 pre-push evidence-coverage checks — so structural compliance and evidence completeness are gated at distinct stages.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Distinct pre-commit and pre-push hook implementations",
          "evidence": "src/aiv/hooks/pre_commit.py and src/aiv/hooks/pre_push.py both present and installed by `aiv init`; plus .husky/pre-commit",
          "met": true
        },
        {
          "signal": "Two-layer model is documented as intended design",
          "evidence": "docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md; top-findings reference 'Layer 2 verification packet' and pre-push layer-2 evidence coverage",
          "met": true
        },
        {
          "signal": "Config-driven classification is tamper-resistant within a commit",
          "evidence": "test_pre_commit_hook.py:308-355 shows main() reads functional_prefixes from the live (staged) .aiv.yml at commit time with no tamper-detection — config can be weakened in the same commit it gates",
          "met": false
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Demonstrate the protocol on itself (the 'quine' property): build and maintain this repository under AIV with full pre-commit enforcement to serve as reference/proof that verification overhead does not destroy velocity.",
      "status": "needs-human-confirm",
      "signals": [
        {
          "signal": "Repo ships its own verification packets / generated evidence artifacts",
          "evidence": "Stage-1 inventory counts 58 generated artifacts; README.md:36-39 states 74 verification packets (+2 templates)",
          "met": true
        },
        {
          "signal": "Self-application proof / velocity metrics",
          "evidence": "README.md:25-55 claims 331 commits in 10h47m at 30.7 commits/hr with enforcement active — narrative metrics, not verified against git log in this audit (invariant 8: stated-positive)",
          "met": false
        },
        {
          "signal": "Architecture verification is itself CI-gated",
          "evidence": ".github/workflows/verify-architecture.yml present alongside ci.yml and aiv-guard-python.yml",
          "met": true
        }
      ],
      "judge_grounded_votes": "0/3"
    }
  ],
  "research": [
    {
      "idea": "in-toto Attestation Framework (CNCF graduated project)",
      "advances": "Provides a standardized, cryptographically signed format for recording 'what was done at each supply-chain step and by whom' — directly parallel to AIV's verification packets. Adopting in-toto's link/attestation envelope would make AIV packets interoperable with the broader SLSA/Sigstore ecosystem and verifiable by external tooling without running the AIV Python package.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/in-toto/attestation",
        "https://slsa.dev/blog/2023/05/in-toto-and-slsa",
        "https://sbomify.com/2024/08/14/what-is-in-toto/",
        "https://mikael.barbero.tech/blog/post/2023-12-28-slsa-and-in-toto/"
      ]
    },
    {
      "idea": "SLSA Framework (Supply-chain Levels for Software Artifacts, OpenSSF/Google)",
      "advances": "Defines graduated provenance levels (Build L0–L3 in v1.0) that map conceptually to AIV's R0–R3 risk tiers. Aligning AIV packet metadata with SLSA provenance format would let CI consumers verify packets using slsa-verifier without bespoke AIV infrastructure, and would frame AIV's compliance levels in a widely adopted industry taxonomy.",
      "corroboration": "corroborated",
      "sources": [
        "https://slsa.dev/",
        "https://slsa.dev/spec/v1.0/verifying-artifacts",
        "https://github.com/slsa-framework/slsa-verifier",
        "https://www.practical-devsecops.com/slsa-framework-guide-software-supply-chain-security/"
      ]
    },
    {
      "idea": "Sigstore suite: Rekor transparency log + Gitsign keyless commit signing",
      "advances": "Rekor is a tamper-evident, append-only public ledger for signing events. AIV could write each packet-close event into Rekor, converting the mutable on-disk JSON audit trail into a globally verifiable, timestamped record. Gitsign adds keyless commit signing (OIDC-based, no GPG required) to `aiv close`, cryptographically binding the committing developer identity to each packet commit and partially addressing the --no-verify compliance gap.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/sigstore/rekor",
        "https://www.sigstore.dev/",
        "https://github.com/sigstore/gitsign",
        "https://openssf.org/blog/2025/12/19/catching-malicious-package-releases-using-a-transparency-log/",
        "https://buildkite.com/resources/blog/securing-your-software-supply-chain-signed-git-commits-with-oidc-and-sigstore/"
      ]
    },
    {
      "idea": "Kosli Evidence Vault — production-grade compliance governance platform",
      "advances": "Kosli provides a tamper-proof, append-only Evidence Vault for regulated software delivery with automated audit trail generation for SOC2, IEC 62304, and FDA 21 CFR Part 11. AIV's guard/audit output could be pushed to Kosli as an alternative persistence backend, addressing the mutable on-disk JSON problem and enabling enterprise compliance reporting without building a bespoke vault.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.kosli.com/",
        "https://www.kosli.com/evidence-vault/",
        "https://www.kosli.com/blog/using-git-for-a-compliance-audit-trail/"
      ]
    },
    {
      "idea": "Open Policy Agent (OPA) + Conftest for declarative packet validation",
      "advances": "AIV's Python-based packet validators contain known semantic errors (prefix-match vs. equality for evidence class values; conditional logic gaps for methodology sections) and require the full Python toolchain. Conftest applies OPA Rego policies to structured JSON/YAML files with no language-specific runtime. Expressing AIV's evidence-class requirements, section presence rules, and link-type constraints as auditable Rego policies would make validation language-agnostic, composable, and independently runnable in CI without the aiv package.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.openpolicyagent.org/",
        "https://www.conftest.dev/",
        "https://secure-pipelines.com/ci-cd-security/policy-as-code-ci-cd-opa-rego-security-gates/",
        "https://dev.to/florianlenz/terraform-testing-with-open-policy-agent-and-conftest-secure-infrastructure-through-terraform-3fk4"
      ]
    },
    {
      "idea": "Evidence Gate GitHub Action — verification-packet gating for CI",
      "advances": "Implements the same enforcement model as AIV's aiv-guard but as a composable GitHub Action: gates merges on artifact presence and produces Evidence Manifests with SHA-256 hashes and governance verdicts (VERIFIED, REFUTED, ABSTAINED, INADMISSIBLE_UPDATE). Its manifest schema and verdict vocabulary could directly inform AIV's packet schema design, and the overlap with 'attesting LLM pipelines' references AIV's likely primary audience.",
      "corroboration": "single-source",
      "sources": [
        "https://github.com/marketplace/actions/evidence-gate-action",
        "https://arxiv.org/pdf/2603.28988"
      ]
    },
    {
      "idea": "Witness — in-toto attestation collection and aggregation tool",
      "advances": "Witness wraps arbitrary CI commands and automatically collects signed attestations (test results, static analysis, SBOM) from each pipeline step into a verifiable in-toto chain. AIV's multi-phase SVP workflow (predict → trace → probe → ownership → validate) maps naturally to a Witness pipeline: each phase would produce a signed attestation that Witness aggregates, replacing the current JSON-on-disk evidence model with a cryptographically linked chain.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/in-toto/witness",
        "https://witness.dev/"
      ]
    },
    {
      "idea": "GitHub Artifact Attestations — native SLSA provenance emission in GitHub Actions",
      "advances": "GitHub Actions can emit Sigstore-signed SLSA provenance attestations for any artifact as a first-class CI step. AIV's aiv-guard job could emit a GitHub Artifact Attestation for each guarded commit range, making the guard verdict a verifiable, GitHub-native record visible in the repository's security tab and queryable via the GitHub API — without a separate audit store or external tool dependency.",
      "corroboration": "corroborated",
      "sources": [
        "https://docs.github.com/en/actions/concepts/security/artifact-attestations",
        "https://docs.gitlab.com/ci/yaml/signing_examples/",
        "https://www.chainguard.dev/unchained/where-do-i-sign-step-by-step-sigstore-adoption"
      ]
    },
    {
      "idea": "CUE Language — portable, declarative packet schema validation",
      "advances": "CUE is a data validation language (JSON superset) with constraint propagation: schemas and data share the same format, are testable, and distributable as modules. AIV's packet format is currently validated by imperative Python with documented semantic bugs (e.g., startswith prefix collision on single-character evidence-class values). CUE schemas would express required/optional sections, enumerated evidence-class values, and link-type constraints as machine-checkable invariants validatable by any CUE-capable tool without the Python package.",
      "corroboration": "corroborated",
      "sources": [
        "https://cuelang.org/",
        "https://github.com/cue-lang/cue"
      ]
    },
    {
      "idea": "ReviewRanker — ML-based code review quality scoring (ICSE 2024)",
      "advances": "ReviewRanker assigns confidence scores to code reviews using semi-supervised learning on developer-labeled data, providing a quantitative estimate of review quality. This directly advances AIV's ELO-based VerifierRating: the current system derives ELO deltas from binary pass/fail outcomes alone, but ReviewRanker-style confidence scores could serve as finer-grained inputs to ELO updates, reducing boundary ambiguities (e.g., the documented inconsistency between from_elo(500) returning COMPETENT vs. newly-created ratings initializing as NOVICE).",
      "corroboration": "corroborated",
      "sources": [
        "https://arxiv.org/abs/2307.03996",
        "https://github.com/saifarnab/code_review",
        "https://link.springer.com/chapter/10.1007/978-981-97-3442-9_50"
      ]
    },
    {
      "idea": "ARMS (Actor Reputation Metric Systems) — structured OSS contributor security credentialing",
      "advances": "ARMS maps seven industry-standard security qualification signals (certifications, CVE credits, signed-commit history, patch acceptance rate, etc.) to concrete reputation metrics for OSS contributors. AIV's VerifierTier/VerifierRating currently derives all signals from internal packet outcomes only. Integrating ARMS-style external signals would make the credentialing more robust, externally anchored, and resistant to gaming by reviewers who optimize for packet-outcome metrics rather than review quality.",
      "corroboration": "single-source",
      "sources": [
        "https://arxiv.org/html/2505.18760"
      ]
    },
    {
      "idea": "Ants-Review — blockchain-based privacy-preserving peer review with quality-proportional incentives",
      "advances": "Ants-Review (Euro-Par 2021) uses Ethereum smart contracts and the Aztec privacy protocol to pay peer reviewers proportional to assessed review quality, with reviews kept anonymous until payment. While blockchain may be over-engineered for AIV's scope, its incentive model — tying reviewer reward to measurable quality rather than mere participation — directly informs how AIV could design verifier incentives to prevent ELO gaming (a reviewer who consistently approves defective packets accrues rating if those packets later pass CI undetected).",
      "corroboration": "corroborated",
      "sources": [
        "https://arxiv.org/abs/2101.09378",
        "https://link.springer.com/chapter/10.1007/978-3-030-71593-9_2"
      ]
    },
    {
      "idea": "pre-commit.ci — managed CI service for pre-commit hooks with auto-fix and automated weekly updates",
      "advances": "AIV installs enforcement via `aiv init` writing raw git hooks, with no mechanism to keep hook versions current or auto-repair violations. pre-commit.ci runs the pre-commit framework in CI, auto-commits fixes, and delivers weekly hook-version updates with zero project configuration. Distributing AIV's enforcement as a pre-commit config entry (alongside the existing Husky path) would let projects adopt enforcement without `aiv init` and receive security-patch delivery for the hook layer automatically.",
      "corroboration": "corroborated",
      "sources": [
        "https://pre-commit.ci/",
        "https://pre-commit.com/"
      ]
    },
    {
      "idea": "Mutation testing (Stryker / Mutmut) as quantitative SVP predict-phase evidence",
      "advances": "AIV's SVP 'predict' phase documents expected behavior before changes are made. Mutation testing generates synthetic faults and measures whether tests detect them, producing a numeric mutation score as quantitative evidence that the test suite will catch the predicted change. Requiring a mutation score above a configurable threshold as Class A evidence in the predict phase would give predict-phase claims a verifiable, automated artifact rather than a narrative assertion, directly strengthening the predict→validate evidence chain.",
      "corroboration": "unverified",
      "sources": [
        "https://stryker-mutator.io/",
        "https://mutmut.readthedocs.io/"
      ]
    },
    {
      "idea": "SLSA v1.2 Source Track (Supply-chain Levels for Software Artifacts)",
      "advances": "SLSA's Source Track (approved Nov 2025) defines graduated levels for SCM-enforced provenance: at Source L3 the platform technically enforces policies (signed commits, mandatory code review, no direct push) so violations become cryptographically impossible rather than merely discouraged. This directly addresses the --no-verify bypass gap in `aiv close` (top finding #6/#17) by moving enforcement to the server side. The slsa-verifier and slsa-github-generator tools provide Python-compatible provenance generation; the in-toto attestation format (SLSA's wire format) is a natural upgrade path for AIV's verification packet schema.",
      "corroboration": "corroborated",
      "sources": [
        "https://slsa.dev/",
        "https://github.com/slsa-framework",
        "https://safeguard.sh/resources/blog/slsa-v1-2-source-track-deep-dive-2025",
        "https://openssf.org/projects/slsa/",
        "https://cloud.google.com/blog/products/application-development/google-introduces-slsa-framework"
      ]
    },
    {
      "idea": "Gittuf — cryptographic Reference State Log for Git policy enforcement",
      "advances": "Gittuf stores a cryptographically signed Reference State Log (RSL) under refs/gittuf/* that records every branch/tag change with policy metadata; unauthorized pushes are rejected at the RSL level regardless of local hook state. Policy rules (who may push, which commits are permitted) are expressed in TUF semantics and enforced at push time via cryptography rather than server configuration, removing forge trust. This is the strongest available mitigation for the --no-verify bypass: requiring a valid RSL entry for packet commits makes bypass detectable at verification time even if not preventable locally. Gittuf integrates with Sigstore/Gitsign for identity. (Go CLI, callable from Python subprocess.)",
      "corroboration": "corroborated",
      "sources": [
        "https://gittuf.dev/",
        "https://github.com/gittuf/gittuf",
        "https://www.ndss-symposium.org/ndss-paper/rethinking-trust-in-forge-based-git-security/",
        "https://openssf.org/blog/2024/01/18/introducing-gittuf-a-security-layer-for-git-repositories/",
        "https://openssf.org/blog/2025/06/06/from-sandbox-to-incubating-gittufs-next-step-in-open-source-security/"
      ]
    },
    {
      "idea": "Sigstore / Rekor — keyless signing and append-only transparency log for commit attestations",
      "advances": "Sigstore's Gitsign component signs git commits using short-lived OIDC certificates (no long-lived key management) and records each signing event in Rekor, an append-only Merkle-tree transparency log. This provides tamper-evident, non-repudiable proof that a specific identity committed at a specific time. For AIV, Rekor is a natural external anchor for verification packet attestations: the packet's SHA can be recorded in Rekor so retroactive modification is detectable. The SSRF risk in aiv's `audit_links` feature (top finding) could be partially mitigated by replacing raw URL fetching with Rekor-anchored attestation lookups. Python Rekor clients exist; REST/OpenAPI accessible from any language.",
      "corroboration": "corroborated",
      "sources": [
        "https://docs.sigstore.dev/logging/overview/",
        "https://github.com/sigstore/rekor",
        "https://docs.sigstore.dev/cosign/signing/gitsign/",
        "https://github.com/sigstore/gitsign",
        "https://buildkite.com/resources/blog/securing-your-software-supply-chain-signed-git-commits-with-oidc-and-sigstore/"
      ]
    },
    {
      "idea": "in-toto supply chain integrity framework",
      "advances": "in-toto defines a signed Layout specifying required pipeline steps, authorized functionaries, and inspections; each step produces signed Link metadata recording commands and file hashes. Verification at deployment time checks that all steps occurred as signed and in order. This is directly isomorphic to AIV's verification packet concept: the Layout becomes the AIV protocol definition, each packet becomes a Link record, and `aiv audit` becomes the in-toto verification pass. Critically, in-toto verification happens at deployment (not commit) time, so --no-verify bypasses are detected before artifact promotion rather than being silently committed. SLSA recommends in-toto attestation format; Python implementation is actively maintained.",
      "corroboration": "corroborated",
      "sources": [
        "https://in-toto.io/",
        "https://github.com/in-toto/in-toto",
        "https://slsa.dev/blog/2023/05/in-toto-and-slsa",
        "https://sbomify.com/2024/08/14/what-is-in-toto/",
        "https://docs.devguard.org/explanations/supply-chain-security/in-toto-framework/"
      ]
    },
    {
      "idea": "Witness (CNCF / TestifySec) — CI-agnostic attestation generation",
      "advances": "Witness wraps CI pipeline commands and automatically generates signed in-toto attestations recording who ran what, when, and how — without modifying existing pipelines. Unlike Tekton Chains (Kubernetes-only), Witness works with GitHub Actions, GitLab, Jenkins, etc. Paired with Archivista (attestation storage), it creates a server-side, tamper-evident audit trail complementary to AIV's client-side hooks. For the aiv-guard CI workflow, Witness could attest each `aiv audit` run, producing non-repudiable records that the guard passed and on which commit, closing the gap where a passing CI run could be spoofed.",
      "corroboration": "corroborated",
      "sources": [
        "https://witness.dev/",
        "https://github.com/in-toto/witness",
        "https://www.testifysec.com/blog/what-is-a-supply-chain-attestation/"
      ]
    },
    {
      "idea": "Glicko-2 rating system as a drop-in upgrade for VerifierRating",
      "advances": "Glicko-2 (Glickman, 2012) augments Elo with a Rating Deviation (RD) parameter that quantifies confidence in the rating and increases automatically during inactivity. This directly resolves the ELO boundary inconsistency found at test_svp.py:154-155 vs :387-388 vs :883-886: at initial creation (ELO 500, RD=high) the system can correctly represent 'competence is uncertain' (NOVICE-equivalent treatment) without an incorrect boundary, because the tier display includes uncertainty. Implementations exist in Python (elote library). The volatility parameter additionally handles verifiers with inconsistent performance.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/Glicko_rating_system",
        "https://elote.mcginniscommawill.com/rating_systems/glicko.html",
        "https://mcginniscommawill.com/posts/2025-04-29-glicko1-rating-system/"
      ]
    },
    {
      "idea": "Mutation testing (mutmut / cosmic-ray) for the SVP probe phase",
      "advances": "Mutation testing makes small deliberate changes to source code and runs tests against each mutant; a mutant that survives (tests pass on broken code) reveals that the test suite does not actually verify the behaviour being claimed. Mutation score is a concrete, quantifiable evidence artifact. For AIV's SVP probe phase, mutation score is exactly the kind of falsification evidence a verification packet should require: it proves that the tests cited in the packet can detect the class of defect the change addresses. mutmut is actively maintained for Python; cosmic-ray supports distributed execution. Peer-reviewed comparative studies (ACM SBES 2024, NSF) confirm both tools are production-ready.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/sixty-north/cosmic-ray",
        "https://dl.acm.org/doi/10.1145/3701625.3701659",
        "https://par.nsf.gov/servlets/purl/10573281"
      ]
    },
    {
      "idea": "Hypothesis property-based testing for SVP falsification evidence",
      "advances": "Hypothesis generates inputs satisfying user-defined properties and automatically shrinks failing cases to minimal reproducers; it records the database of failing examples across runs. For the SVP falsification sub-phase, a Hypothesis test that attempts to violate the claim's stated invariant is stronger evidence than a hand-written example-based test. The `@given` decorator + `settings(database=ExampleDatabase(...))` produces a reproducible, serialisable test artifact that can be embedded in a verification packet as a Class A falsification artifact. Property-based testing has been shown equivalent to coverage-guided fuzzing for logic bugs.",
      "corroboration": "corroborated",
      "sources": [
        "https://pypi.org/project/hypothesis/",
        "https://blog.nelhage.com/post/property-testing-is-fuzzing/",
        "https://www.infoq.com/news/2021/01/google-python-atheris-fuzzing/"
      ]
    },
    {
      "idea": "pre-commit framework hook isolation and YAML-declarative hook registry",
      "advances": "The `pre-commit` framework (pre-commit.com) installs per-hook virtualenvs and fetches hooks from versioned repository refs, isolating each hook's dependencies and making its version pinnable in `.pre-commit-config.yaml`. This directly mitigates the config-tamper attack found at test_pre_commit_hook.py:308-314: a `.pre-commit-config.yaml` change in a staged commit is not re-executed by the hook manager during that same commit, unlike AIV's `.aiv.yml` which is read live from the working tree. AIV could publish its enforcement logic as a `pre-commit` hook repository, gaining tamper-resistance and the ecosystem's caching/isolation model for free.",
      "corroboration": "corroborated",
      "sources": [
        "https://pre-commit.com/",
        "https://github.com/pre-commit/pre-commit",
        "https://pypi.org/project/pre-commit/"
      ]
    },
    {
      "idea": "Difftastic structural (AST-aware) diff for the SVP trace phase",
      "advances": "Difftastic parses source files into syntax trees using Tree-sitter and diffs at the expression level, distinguishing semantic changes from formatting noise (whitespace, comment reformatting). For AIV's SVP trace phase — which must record what actually changed — a structural diff produces a more accurate and compact evidence artifact than the line-based diff currently extracted in pre_commit.py. The existing operator-precedence bug in line-counting (top finding #1) affects the line-based diff parser; switching to a structural diff eliminates the entire class of off-by-one line attribution errors. Supports 30+ languages; integrates with git via GIT_EXTERNAL_DIFF.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/Wilfred/difftastic"
      ]
    },
    {
      "idea": "Conventional Commits specification + commitlint for structured packet metadata in commit messages",
      "advances": "Conventional Commits defines a machine-parseable commit message schema (type[scope]: description, optional body, footers) that enables automated changelog generation and semver inference. Footers are an ideal carrier for AIV verification packet references: `AIV-Packet: <uuid>`, `AIV-Tier: R2`, `AIV-Coverage-Delta: +1.8%` become queryable fields in git log. commitlint validates these at commit-msg hook time. This would give AIV a standardised, ecosystem-compatible metadata format rather than a bespoke packet file format, and would make compliance status queryable with standard git tooling.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.conventionalcommits.org/en/v1.0.0/",
        "https://www.conventionalcommits.org/en/about/",
        "https://github.com/conventionalcommit/commitlint"
      ]
    },
    {
      "idea": "Commitizen (Python) — enforced commit schema with automated versioning and changelog",
      "advances": "Commitizen is a Python CLI tool that enforces Conventional Commits format via a commit-msg hook and drives version bumping (`cz bump`) and changelog generation (`cz changelog`) from commit history. For AIV, Commitizen's extensible schema system (`cz_customise` in `pyproject.toml`) could embed required verification packet fields as mandatory commit-message sections, rejecting commits that lack packet references. The automated changelog output would constitute a human-readable audit trail of all verified changes with their packet metadata, directly satisfying the protocol's evidence generation goal.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/commitizen-tools/commitizen",
        "https://commitizen-tools.github.io/commitizen/"
      ]
    },
    {
      "idea": "OpenSSF Scorecard — automated security posture scoring as a packet evidence component",
      "advances": "OpenSSF Scorecard runs 20+ automated checks (branch protection, signed releases, SAST, fuzzing, pinned dependencies, code review, token permissions) and outputs JSON with per-check scores and risk weights. For AIV, a Scorecard run could generate a security attestation component of the verification packet: a timestamped JSON snapshot proving the repository met minimum security posture at commit time. The --pypi flag supports Python package scanning; the JSON output is machine-readable and embeddable. Critical check failures (Token-Permissions, Signed-Releases) could block `aiv close` until resolved, directly strengthening compliance.",
      "corroboration": "corroborated",
      "sources": [
        "https://openssf.org/projects/scorecard/",
        "https://scorecard.dev/",
        "https://github.com/ossf/scorecard",
        "https://github.com/ossf/scorecard/blob/main/docs/checks.md"
      ]
    },
    {
      "idea": "GitHub Rulesets with required status checks (non-bypassable merge gate)",
      "advances": "GitHub Rulesets (available at org and repo level) can enforce required status checks with zero bypass actors — including repository admins. Unlike legacy branch protection, rulesets can be layered and apply to fork PRs. Configuring a required `aiv-guard` status check in a ruleset means no PR can be merged without a passing `aiv audit` CI run, providing server-side enforcement that complements and partially compensates for the client-side --no-verify bypass. Rulesets also support require-signed-commits, which pairs with Gitsign to enforce commit identity. This is the lowest-friction hardening for existing AIV deployments.",
      "corroboration": "corroborated",
      "sources": [
        "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets",
        "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets"
      ]
    },
    {
      "idea": "Evidence-Based Software Engineering (EBSE) as the methodological framework for the SVP validate phase",
      "advances": "EBSE (Kitchenham, Dybå, Jørgensen, 2004) applies evidence-based medicine principles to software: decisions must be grounded in empirical evidence rather than expert opinion, with systematic reviews and meta-analyses as the gold standard. The SVP validate phase's claim structure (predict → probe → falsification → ownership) is isomorphic to EBSE's evidence hierarchy. Adopting EBSE's evidence grading schema (Class I systematic review → Class V expert opinion) would give AIV's packet evidence classes a well-studied theoretical grounding, enable comparison with the broader SE research community, and provide a principled basis for the risk tier (R0–R3) and compliance level mappings that are currently ad hoc.",
      "corroboration": "corroborated",
      "sources": [
        "https://ebse.webspace.durham.ac.uk/",
        "https://www.researchgate.net/publication/4083466_Evidence-based_software_engineering",
        "https://link.springer.com/article/10.1007/s10664-021-09953-9"
      ]
    },
    {
      "idea": "git-absorb / git-autofixup — automated atomic commit enforcement",
      "advances": "git-absorb uses patch commutation analysis to identify which existing commits a staged change logically belongs to and creates fixup! commits automatically; git-autofixup uses git blame for the same purpose. Both enforce the atomic-commit invariant that AIV requires (one packet per logical change) by making it easy to correctly split accidental multi-concern commits before `aiv close`. The commutation check in git-absorb also provides a formal correctness property: a fixup is only assigned to a parent commit if applying the hunks in either order produces identical results, which is a stronger guarantee than visual inspection. Integrates as a pre-commit hook step or as a recommended step in `aiv begin`.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/tummychow/git-absorb",
        "https://github.com/torbiak/git-autofixup",
        "https://news.ycombinator.com/item?id=41653191"
      ]
    },
    {
      "idea": "python-semantic-release — automated changelog and version evidence from structured commits",
      "advances": "python-semantic-release parses Conventional Commits history to determine semantic version increments, generate changelogs, and produce release notes in configurable Jinja2 templates. For AIV, this provides automated evidence artifacts at the release boundary: a changelog that is machine-generated from verified packet metadata is itself an auditable record of what was changed, why, and which tier it was validated at. Custom templates could produce AIV-flavoured release notes that aggregate packet UUIDs, evidence links, and coverage deltas per release, replacing manual documentation with generated, commit-anchored evidence.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/python-semantic-release/python-semantic-release",
        "https://python-semantic-release.readthedocs.io/"
      ]
    },
    {
      "idea": "SLSA (Supply-chain Levels for Software Artifacts) — OpenSSF tiered maturity framework (levels 0–3) defining non-bypassable controls for build provenance, tampering prevention, and hermetic build environments.",
      "advances": "Establishes a precedent for AIV's tiered, non-bypassable enforcement model: each SLSA level maps to progressively stronger evidence-collection requirements analogous to AIV's risk tiers (R0–R3). SLSA provenance metadata (who built it, from what source, how) formalizes the 'verification packet' concept at the supply-chain layer. Adopting SLSA v1.1 vocabulary would let AIV interoperate with existing supply-chain tooling and make its evidence artifacts machine-consumable outside the repo.",
      "corroboration": "corroborated",
      "sources": [
        "https://slsa.dev/",
        "https://openssf.org/projects/slsa/",
        "https://www.practical-devsecops.com/slsa-framework-guide-software-supply-chain-security/",
        "https://www.wiz.io/academy/application-security/slsa-framework"
      ]
    },
    {
      "idea": "in-toto Attestation Framework — CNCF-graduated project defining cryptographically signed metadata envelopes ('links' and 'layouts') that prove each supply-chain step executed exactly as intended, with policy enforcement via functionary inspection.",
      "advances": "Directly addresses AIV's biggest unresolved gap: the absence of a signed, machine-verifiable format for verification packets. in-toto layouts can encode AIV's four-phase SVP workflow (predict/trace/probe/validate) as a formal policy; signed links from each phase serve as tamper-evident evidence artifacts. Because SLSA recommends in-toto format for provenance, adopting it would make AIV verification packets interoperable with the broader OpenSSF ecosystem without bespoke serialisation.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/in-toto/attestation",
        "https://slsa.dev/blog/2023/05/in-toto-and-slsa",
        "https://developers.redhat.com/articles/2025/05/15/how-we-use-software-provenance-red-hat",
        "https://devsecopsschool.com/blog/in-toto/"
      ]
    },
    {
      "idea": "Sigstore / Cosign — Linux Foundation keyless cryptographic signing service using short-lived OIDC certificates and append-only transparency logs (Rekor) to provide non-repudiation for software artifacts without long-lived key management.",
      "advances": "AIV currently relies on git commit SHAs and file hashes for evidence linkage but has no cryptographic signing layer for packet authenticity. Sigstore's keyless model eliminates the key-distribution problem that has historically blocked signing adoption in developer workflows. Integrating Cosign into the 'aiv close' command would sign each verification packet and log the signature to Rekor, providing an immutable, publicly auditable record that addresses the '--no-verify bypass' finding — even without the hook, the signed packet is a verifiable attestation.",
      "corroboration": "corroborated",
      "sources": [
        "https://docs.sigstore.dev/about/overview/",
        "https://github.com/sigstore/cosign",
        "https://www.qcecuring.com/education/code-signing/sigstore-and-cosign",
        "https://docs.docker.com/dhi/core-concepts/signatures/"
      ]
    },
    {
      "idea": "Gittuf — OpenSSF sandbox project recording every git ref update as a signed entry in a hash-chained Reference State Log (RSL) using in-toto attestations, enabling cryptographic proof of legitimate branch history.",
      "advances": "Gittuf directly closes AIV's pre-push bypass gap: a gittuf-protected branch rejects any ref update that lacks a valid signed entry in the RSL, regardless of '--no-verify'. This complements AIV's hook approach with a server-side guarantee. Gittuf's policy model (who may push to which ref) maps cleanly onto AIV's ownership and verifier-tier concepts; ownership claims in an AIV packet could be verified against the gittuf policy at push time, turning SVP ownership data into an enforceable access control mechanism.",
      "corroboration": "corroborated",
      "sources": [
        "https://nesbitt.io/2026/06/04/gittuf-a-signed-log-for-git-refs.html",
        "https://lwn.net/Articles/972467/",
        "https://gittuf.dev/documentation/contributors/signing-keys",
        "https://www.kenmuse.com/blog/using-gitsign-for-keyless-git-commit-signing/"
      ]
    },
    {
      "idea": "Conventional Commits Specification — Lightweight machine-readable commit message convention (<type>[scope]: <description>) enabling automated changelog generation, semantic versioning, and tooling integration.",
      "advances": "AIV's verification packets encode intent, risk tier, and evidence references in structured YAML/JSON files attached to commits, but the commit messages themselves have no enforced schema. Adopting or extending Conventional Commits as a required message format for 'aiv close'-generated commits would allow external tooling (changelogs, release notes, issue trackers) to consume AIV metadata without bespoke parsers, and would give the 'aiv audit' command a lightweight secondary signal for detecting packets that were closed with mismatched intents.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.conventionalcommits.org/en/v1.0.0/",
        "https://www.conventionalcommits.org/en/about/",
        "https://dev.to/tene/mastering-conventional-commits-structure-benefits-and-tools-3cpo",
        "https://www.sei.cmu.edu/blog/versioning-with-git-tags-and-conventional-commits/"
      ]
    },
    {
      "idea": "Commitlint — Tool that lints commit messages against configurable rule sets at pre-commit time, enforcing structural conventions via a plugin architecture with 70+ built-in rules.",
      "advances": "AIV's pre-commit hook validates packet presence and functional-file classification but does not validate the commit message itself. Commitlint's rule engine and plugin model could be embedded or replicated inside 'aiv/hooks/pre_commit.py' to enforce that the message references an open packet ID, matches the risk tier declared in the packet, or satisfies other structural invariants — without building a full rule engine from scratch. Its staged-files interception pattern also demonstrates how to distinguish amendment commits from fresh ones, relevant to fixing AIV's initial-commit edge case.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/conventional-changelog/commitlint",
        "https://medium.com/@the.sikandar.dev/how-to-set-up-commitlint-to-enforce-clean-git-commit-messages-9082cce5ca03",
        "https://dev.to/shnjd/git-good-automating-commit-message-standards-with-husky-and-commitlint-3f36"
      ]
    },
    {
      "idea": "pre-commit framework (pre-commit.com) — Language-agnostic multi-hook manager that installs hooks as isolated virtual environments per tool, with a YAML-configured hook registry and reproducible hook versions pinned in '.pre-commit-config.yaml'.",
      "advances": "AIV's hook installation via 'aiv init' is bespoke and requires Python to be available at commit time. The pre-commit framework offers a distribution mechanism where 'aiv' could be published as a pre-commit hook repository, letting teams add AIV enforcement with a single '.pre-commit-config.yaml' entry rather than running 'aiv init'. The isolated venv per hook also eliminates the class of bugs where AIV's dependencies conflict with the project's own dependencies. This would accelerate adoption and reduce the configuration drift that leads to tampered '.aiv.yml' bypasses.",
      "corroboration": "corroborated",
      "sources": [
        "https://pre-commit.com/",
        "https://github.com/pre-commit/pre-commit",
        "https://pre-commit.com/hooks.html"
      ]
    },
    {
      "idea": "GitHub Artifact Attestations (Actions) — GitHub Actions native feature generating OIDC-bound Sigstore attestations for workflow-produced artifacts, verifiable with 'gh attestation verify' before deployment or release.",
      "advances": "AIV's CI guard ('aiv-guard-python.yml') currently runs structural checks but produces no cryptographically verifiable output that downstream consumers can independently audit. GitHub Artifact Attestations would let the guard job sign its 'aiv audit' passing verdict as an attestation, creating an unforgeable link between the CI run identity and the audit result. This converts a 'CI job exited 0' pass into a verifiable claim, addressing the compliance-gap finding where '--no-verify' commits cannot be retroactively audited.",
      "corroboration": "single-source",
      "sources": [
        "https://docs.github.com/en/actions/concepts/security/artifact-attestations"
      ]
    },
    {
      "idea": "VERIBIN / PatchGuru — Recent academic tools (NDSS 2025, arXiv 2026) applying automated formal methods and LLM-assisted semantic analysis to verify that a patch implements exactly and only what its description states.",
      "advances": "AIV's SVP 'predict' phase asks the developer to declare expected changes, and the 'trace' and 'probe' phases collect evidence that those changes happened. VERIBIN's approach of analysing a patch's binary-level effect against a specification provides a model for automating AIV's Class E evidence: instead of requiring a developer to manually link a test run, an automated patch-semantic checker could generate a machine-signed claim that the diff matches the declared intent. PatchGuru's natural-language-to-patch-semantics pipeline is directly applicable to AIV's intent-vs-diff consistency check.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.ndss-symposium.org/wp-content/uploads/2025-359-paper.pdf",
        "https://arxiv.org/pdf/2602.05270",
        "https://www.amazon.science/blog/how-to-integrate-formal-proofs-into-software-development"
      ]
    },
    {
      "idea": "DO-178C (Software Considerations in Airborne Systems and Equipment Certification) — FAA-accepted aerospace standard requiring bidirectional requirements-to-code-to-test traceability, configuration management, and change impact analysis for safety-critical avionics software.",
      "advances": "DO-178C is the regulatory existence proof that AIV's core discipline — mandatory, auditable change packets with structured evidence linking requirements to code to tests — can be imposed non-optionally at scale in commercial software. AIV's risk tiers (R0–R3) map closely to DO-178C's DAL A–E assurance levels. Adopting DO-178C's change impact analysis vocabulary ('derived requirements', 'traceability matrix') into AIV's packet schema would make AIV applicable to regulated-software teams and provide a defensible basis for the structural checks 'aiv audit' performs.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/DO-178C",
        "https://visuresolutions.com/aerospace-and-defense/do-178c/",
        "https://medium.com/@umutt.akbulut/do-178c-a-discipline-on-the-provability-of-reliability-in-airborne-software-9d2f3afb83b",
        "https://www.parasoft.com/solutions/do-178/"
      ]
    },
    {
      "idea": "ISO 26262 (Road Vehicles — Functional Safety) — International automotive standard mandating systematic change management, configuration control, and impact analysis throughout the development lifecycle for safety-relevant electrical/electronic systems.",
      "advances": "ISO 26262 Part 8 (Supporting Processes) formalises change request, impact analysis, regression test selection, and confirmation measure workflows that correspond to AIV's packet lifecycle (begin → generate → check → close). Its ASIL-decomposition concept (splitting a high-integrity requirement across independently verified components) provides a model for AIV's multi-verifier ownership claims. Aligning AIV's compliance_level output with ASIL designations would open AIV adoption in automotive software organisations where regulatory coverage is a hard requirement.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/ISO_26262",
        "https://www.keysight.com/blogs/en/tech/sim-des/achieve-compliance-with-iso-261262-functional-safety-standards",
        "https://www.jamasoftware.com/requirements-management-guide/automotive-engineering/iso-26262-and-recent-updates-ensuring-functional-safety-in-the-automotive-industry/",
        "https://visuresolutions.com/automotive/iso-26262/"
      ]
    },
    {
      "idea": "SBOM Standards (SPDX ISO/IEC 5962 and CycloneDX OWASP) — Machine-readable bill-of-materials formats capturing component identity, version, license, and vulnerability metadata for every artifact in a software product.",
      "advances": "AIV's verification packets track evidence about code changes but not about the dependency graph those changes operate on. Emitting a CycloneDX or SPDX SBOM fragment as a required Class C evidence artifact for any commit touching dependency manifests would allow 'aiv audit' to detect supply-chain-relevant changes that lack dependency impact analysis, closing a class of compliance gaps not currently addressed. SBOM tooling (Syft, Trivy) is mature enough to auto-generate these fragments in the 'aiv generate' step.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.kiuwan.com/blog/sbom-standards/",
        "https://www.opswat.com/blog/sbom-formats",
        "https://www.legitsecurity.com/blog/what-is-an-sbom-sbom-explained-in-5-minutes",
        "https://jfrog.com/learn/grc/sbom/"
      ]
    },
    {
      "idea": "GUAC (Graph for Understanding Artifact Composition) — OpenSSF incubating project (Google/Kusari) ingesting SLSA provenance, in-toto links, SBOMs, and vulnerability feeds into a Neo4j graph queryable via GraphQL to answer cross-artifact traceability questions.",
      "advances": "AIV generates per-packet evidence files but has no mechanism to answer cross-packet queries: 'which commits touched this module in the last 30 days without an R2 packet?', or 'which verifiers attested changes to authentication code?'. GUAC's graph model — with nodes for artifacts, sources, builders, and vulnerabilities — is exactly the substrate needed for AIV's 'aiv audit --commits N' to become a rich compliance dashboard rather than a linear scan. AIV packet metadata could be ingested as GUAC 'hasSBOM' or custom predicates, enabling portfolio-level compliance queries.",
      "corroboration": "corroborated",
      "sources": [
        "https://openssf.org/blog/2024/03/07/guac-joins-openssf-as-incubating-project/",
        "https://guac.sh/guac/",
        "https://www.legitsecurity.com/blog/guac-explained-in-5-minutes",
        "https://www.techtarget.com/searchitoperations/news/365532041/SBOM-graph-database-aims-to-be-cloud-security-secret-sauce"
      ]
    },
    {
      "idea": "Zero-Trust CI/CD — Architecture pattern applying Zero-Trust principles (verify every identity, limit blast radius, continuous attestation) to CI/CD pipelines via OIDC ephemeral tokens per job, artifact signing, and policy-as-code (OPA/Rego, Kyverno).",
      "advances": "AIV's current enforcement model assumes developers are honest (hooks can be bypassed with '--no-verify') and that CI jobs are trusted (the guard runner is not itself attested). Zero-Trust CI/CD patterns provide the missing layer: each CI job receives an OIDC token that identifies the workflow, repository, and run; every artifact signed with that token can be later verified to have originated from a specific, unmodified pipeline run. Applying this to AIV's guard runner would produce machine-verifiable evidence that the 'aiv audit' CI job passed, addressing the audit-result trust gap that exists today.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.infisign.ai/blog/implement-zero-trust-principles-for-software-supply-chain-security",
        "https://em360tech.com/tech-articles/zero-trust-cicd-pipelines-securing-your-software-supply-chain/",
        "https://dzone.com/articles/zero-trust-cicd-pipelines-implementation-guide"
      ]
    },
    {
      "idea": "ELO-based Trust / Reputation Systems in Peer Review — Academic literature on applying Elo rating (and derived Glicko-2, TrueSkill) to expert assessment quality scoring in software engineering contexts, including code-review credibility weighting and expert calibration.",
      "advances": "AIV's SVP subsystem implements an ELO-based VerifierRating with a NOVICE/COMPETENT/EXPERT tier system, but the audit findings reveal a boundary inconsistency at ELO=500. Existing literature on Glicko-2 (which adds rating deviation for uncertainty) and TrueSkill (Bayesian extension) provides theoretically grounded alternatives that handle the initial-rating problem correctly: new verifiers start with high uncertainty (not a fixed NOVICE/COMPETENT ambiguity), and the boundary resolves itself as evidence accumulates. Adopting Glicko-2 would also give AIV a confidence interval on verifier tier, enabling it to require higher-confidence verifiers for R3 packets.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/Glicko_rating_system",
        "https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/",
        "https://arxiv.org/abs/2002.09305"
      ]
    },
    {
      "idea": "OpenChain (ISO/IEC 5230 and ISO/IEC 18974) — Linux Foundation standards defining minimum process requirements for open-source license compliance (5230) and security assurance (18974), with self-certification checklists.",
      "advances": "AIV's heavy documentation-to-source ratio and formal protocol specification suggest an intent to be adopted as a process standard, not just a CLI tool. OpenChain 18974 (Security Assurance) defines exactly the kind of 'specification + conformance checklist' model that AIV could adopt for its own governance: a published AIV specification with a conformance checklist would allow organizations to certify their development process as AIV-compliant independently of the CLI tool version. This would also clarify which protocol requirements are normative versus advisory, addressing the ambiguity in the current packet-structure validation.",
      "corroboration": "single-source",
      "sources": [
        "https://openchainproject.org/",
        "https://openchainproject.org/security-assurance"
      ]
    }
  ],
  "research_blocked": false
}
```
