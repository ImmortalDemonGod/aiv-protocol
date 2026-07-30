"""
aiv/guard/runner.py

Main AIV Guard orchestrator.  Replaces the 2244-line inline JS in
aiv-guard.yml with a clean Python implementation backed by aiv-lib.

Usage (from GitHub Actions workflow):
    python -m aiv.guard
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..lib.config import AIVConfig
from ..lib.validators.pipeline import ValidationPipeline
from .canonical import REQUIRED_CLASSES, validate_canonical
from .github_api import ChangedFile, GitHubAPI
from .models import (
    GITHUB_ACTIONS_RUN,
    EvidenceClassResult,
    GuardContext,
    GuardResult,
    GuardSeverity,
    OverallResult,
)

# ------------------------------------------------------------------ #
# Critical-surface detection (ported from JS guard)
# ------------------------------------------------------------------ #
_CS_PATH: list[tuple[str, re.Pattern[str]]] = [
    ("Authentication", re.compile(r"(^|/)(auth|authentication|login|session|token|oauth|sso)(/|$)", re.I)),
    (
        "Authorization",
        re.compile(r"(^|/)(authz|authorization|rbac|acl|permission|permissions|policy|policies)(/|$)", re.I),
    ),
    (
        "Secrets Management",
        re.compile(r"(^|/)(secret|secrets|vault|apikey|api_key|credential|credentials|password|\.env)(/|$)", re.I),
    ),
    (
        "Cryptography",
        re.compile(r"(^|/)(crypto|cryptography|encrypt|encryption|cipher|signature|signing|hash)(/|$)", re.I),
    ),
    (
        "Privilege Boundaries",
        re.compile(r"(^|/)(sandbox|privilege|capability|capabilities|setuid|docker|container)(/|$)", re.I),
    ),
    (
        "Audit/Logging",
        re.compile(r"(^|/)(audit|audit[-_]?log|audittrail|security[-_]?log|event[-_]?log|ledger)(/|$)", re.I),
    ),
    ("PII Handling", re.compile(r"(^|/)(pii|privacy|gdpr|redact|sanitiz)(/|$)", re.I)),
]

_CS_SEMANTIC: list[tuple[str, re.Pattern[str]]] = [
    (
        "Authentication",
        re.compile(r"\b(timingSafeEqual|verify[_-]?token|tokenMatches|HEALTHCHECK_TOKEN|AUDIT_LINK_SECRET)\b", re.I),
    ),
    ("Authorization", re.compile(r"\b(rbac|acl|permission|permissions|policy|access[_-]?control)\b", re.I)),
    ("Secrets Management", re.compile(r"\bprocess\.env\.[A-Z0-9_]*(SECRET|TOKEN|KEY)\b", re.I)),
    ("Cryptography", re.compile(r"\b(createHmac|HMAC[_-]?SHA256|sha256|sha512|crypto\.|gpg|clearsign)\b", re.I)),
    (
        "Privilege Boundaries",
        re.compile(r"\b(no-new-privileges|cap_drop|--security-opt|network_mode\s*:\s*[\"']none[\"'])\b", re.I),
    ),
    ("Audit/Logging", re.compile(r"\b(audit[_-]?log|analysis_ledger|destruction_ledger|hash[-_ ]chained)\b", re.I)),
    ("PII Handling", re.compile(r"\b(PII|email|ip address|redact|redaction|sanitize|anonymiz)\b", re.I)),
]


# ------------------------------------------------------------------ #
# Public entry point
# ------------------------------------------------------------------ #


class GuardRunner:
    """Orchestrates the full AIV Guard validation."""

    def __init__(
        self,
        ctx: GuardContext,
        api: GitHubAPI | None = None,
        config: AIVConfig | None = None,
    ) -> None:
        self.ctx = ctx
        self.api = api or GitHubAPI()
        self.config = config or AIVConfig()
        # Compile fast-track patterns from config (single source of truth)
        self._fast_track_patterns = [re.compile(p) for p in self.config.fast_track_patterns]
        self.result = GuardResult(
            repository=ctx.full_repo,
            pr_id=ctx.pr_number,
            head_sha=ctx.head_sha,
            validated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._changed_files: list[ChangedFile] | None = None

    # -- helpers --------------------------------------------------- #

    def _changed(self) -> list[ChangedFile]:
        if self._changed_files is None:
            self._changed_files = self.api.list_pr_files(self.ctx)
        return self._changed_files

    def _changed_paths(self) -> list[str]:
        return [f.filename for f in self._changed()]

    def _is_fast_track(self) -> bool:
        paths = self._changed_paths()
        if not paths:
            return False
        for p in paths:
            if not any(pat.search(p) for pat in self._fast_track_patterns):
                return False
        return True

    # -- main pipeline --------------------------------------------- #

    def run(self) -> GuardResult:
        """Execute the full guard validation pipeline."""

        # 1. Resolve packet content
        packet_content = self._resolve_packet()
        if packet_content is None:
            self.result.finalize()
            return self.result

        # 2. Check for canonical JSON block
        canonical_match = re.search(r"```aiv-canonical-json\s*([\s\S]*?)```", packet_content)
        self.result.canonical_enabled = canonical_match is not None

        # 3. Markdown-only validation (using aiv-lib pipeline)
        self._validate_markdown(packet_content, canonical_match is not None)

        # 4. If no canonical block, we're done (markdown-only mode)
        if not canonical_match:
            if not self._is_fast_track():
                self.result.add_warn(
                    "CT-001",
                    "Canonical packet block missing; markdown-only validation applied.",
                )
            self.result.finalize()
            return self.result

        # 5. Parse canonical JSON
        try:
            canonical_packet = json.loads(canonical_match.group(1))
        except json.JSONDecodeError:
            self.result.add_block("CT-001", "Canonical packet block is not valid JSON.")
            self.result.finalize()
            return self.result

        # 6. Canonical validation
        validate_canonical(canonical_packet, self.ctx, self.result, self._changed_paths())

        risk_tier = self.result.risk_tier_validated

        # 7. Critical surface detection
        self._check_critical_surfaces(canonical_packet, risk_tier)

        # 8. CI artifact inspection (Class A run verification)
        self._inspect_class_a_run(canonical_packet, risk_tier)

        # 9. Build evidence class results
        self._build_evidence_class_results(canonical_packet, risk_tier)

        self.result.finalize()
        return self.result

    # -- packet resolution ----------------------------------------- #

    def _resolve_packet(self) -> str | None:
        """Resolve packet content from PR body or Packet Source file."""
        body = self.ctx.pr_body
        packet_content = body

        # Check for Packet Source: reference
        m = re.search(r"Packet Source:\s*`(.+?)`", body)
        if not m:
            m = re.search(r"Packet Source:\s*(\S+)", body)

        if m:
            file_path = m.group(1).strip()
            # Resolve the path and require it to stay inside .github/. A bare
            # startswith(".github/") check is bypassable with traversal such as
            # ".github/../../etc/passwd" (path traversal -> arbitrary file read).
            github_dir = Path(".github").resolve()
            resolved = Path(file_path).resolve()
            if github_dir not in resolved.parents:
                self.result.add_block(
                    "CT-001",
                    f"Invalid Packet Source path: {file_path} (must resolve within .github/)",
                )
                return None

            if resolved.is_file():
                packet_content = resolved.read_text(encoding="utf-8")
            else:
                self.result.add_block("CT-001", f"Failed to read packet source at {file_path}")
                return None

        return packet_content

    # -- markdown validation --------------------------------------- #

    def _validate_markdown(self, content: str, has_canonical: bool) -> None:
        """Run aiv-lib pipeline for markdown structure validation."""
        pipeline = ValidationPipeline(self.config)
        lib_result = pipeline.validate(content)

        # Map aiv-lib findings to guard findings
        for finding in lib_result.errors:
            self.result.add_block(finding.rule_id, finding.message)

        for finding in lib_result.warnings:
            self.result.add_warn(finding.rule_id, finding.message)

        # Check required markdown sections (when no canonical)
        if not has_canonical:
            required_sections_with_alts: list[tuple[str, ...]] = [
                ("# AIV Verification Packet (v2.1)", "# AIV Verification Packet (v2.2)"),
                ("## Claim(s)", "## Claims"),
                ("## Evidence", "## Evidence References"),
                ("### Class E (Intent Alignment)",),
                ("### Class B (Referential Evidence)",),
                ("### Class A (Execution Evidence)",),
                ("## Summary",),
            ]
            # In v2.2, Class A evidence is covered by the Evidence References table
            has_evidence_table = "## Evidence References" in content
            missing = [
                alts[0]
                for alts in required_sections_with_alts
                if not any(alt in content for alt in alts)
                and not (alts[0] == "### Class A (Execution Evidence)" and has_evidence_table)
            ]
            optional = ["## Verification Methodology", "## Reproduction"]
            has_optional = any(h in content for h in optional)

            if missing and not self._is_fast_track():
                self.result.add_block(
                    "CT-001",
                    f"Missing required packet sections: {', '.join(missing)}",
                )

            if not has_optional and not missing:
                self.result.add_block(
                    "CT-001",
                    'Must include "## Verification Methodology" or "## Reproduction"',
                )

    # -- critical surfaces ----------------------------------------- #

    def _check_critical_surfaces(self, packet: dict[str, Any], risk_tier: str) -> None:
        """Detect critical surfaces in changed files."""
        hits: set[str] = set()

        for f in self._changed():
            for surface, pattern in _CS_PATH:
                if pattern.search(f.filename):
                    hits.add(surface)
            if f.patch:
                haystack = f"{f.filename}\n{f.patch}"
                for surface, pattern in _CS_SEMANTIC:
                    if pattern.search(haystack):
                        hits.add(surface)

        if hits and risk_tier != "R3":
            self.result.add_block(
                "CLS-002",
                f"Change touches critical surfaces ({', '.join(sorted(hits))}); risk_tier MUST be R3.",
            )
            return

        if risk_tier == "R3":
            cs = packet.get("classification", {}).get("critical_surfaces", [])
            if not isinstance(cs, list) or len(cs) == 0:
                self.result.add_block(
                    "CLS-002",
                    "R3 requires critical_surfaces to be a non-empty array.",
                )
                return

            missing = [s for s in hits if s not in cs]
            if missing:
                self.result.add_block(
                    "CLS-002",
                    f"critical_surfaces missing detected: {', '.join(missing)}",
                )

    # -- CI artifact inspection ------------------------------------ #

    def _inspect_class_a_run(self, packet: dict[str, Any], risk_tier: str) -> None:
        """Verify Class A CI run reference and inspect artifacts."""
        evidence_items = packet.get("evidence_items", [])
        class_a = [e for e in evidence_items if isinstance(e, dict) and e.get("class") == "A"]

        if not class_a:
            self.result.add_block("A-001", "L1 requires at least one Class A evidence item.")
            return

        # Find a GitHub Actions run URL in Class A artifacts
        run_ref = None
        for e in class_a:
            for a in e.get("artifacts", []):
                if isinstance(a, dict) and isinstance(a.get("reference"), str):
                    if GITHUB_ACTIONS_RUN.search(a["reference"]):
                        run_ref = a["reference"]
                        break
            if run_ref:
                break

        if not run_ref:
            if self.ctx.is_draft:
                self.result.add_warn(
                    "A-002",
                    "Class A evidence has no GitHub Actions run URL.",
                )
            else:
                self.result.add_block(
                    "A-002",
                    "L1 requires Class A artifact with GitHub Actions run URL.",
                )
            return

        # Extract run ID and verify via API
        m = re.search(r"actions/runs/(\d+)", run_ref)
        if not m:
            self.result.add_block("A-002", "Could not parse workflow run ID from Class A URL.")
            return

        run_id = int(m.group(1))
        run_data = self.api.get_workflow_run(self.ctx, run_id)

        if run_data is None:
            self.result.add_block("A-002", "Class A run URL could not be fetched via API.")
            return

        run_head = run_data.get("head_sha", "")
        if run_head and run_head.lower() != self.ctx.head_sha.lower():
            self.result.add_block(
                "CT-005",
                f"Class A CI run head_sha mismatch. Run: {run_head}, PR: {self.ctx.head_sha}",
            )
            return

        # Check for aiv-evidence artifact
        artifacts = self.api.list_run_artifacts(self.ctx, run_id)
        aiv_artifact = next(
            (a for a in artifacts if a.get("name") == "aiv-evidence" and not a.get("expired")),
            None,
        )

        if not aiv_artifact:
            if self.ctx.is_draft:
                self.result.add_warn("A-005", "No aiv-evidence artifact found on CI run.")
            else:
                self.result.add_block("A-005", "Requires non-expired aiv-evidence artifact on CI run.")
            return

        self.result.upsert_rule_result("A-002", "PASS")
        self.result.upsert_rule_result("A-005", "PASS")

    # -- evidence class results ------------------------------------ #

    def _build_evidence_class_results(self, packet: dict[str, Any], risk_tier: str) -> None:
        """Build the evidence_class_results array."""
        evidence_items = packet.get("evidence_items", [])
        required = REQUIRED_CLASSES.get(risk_tier, [])
        all_classes = ["A", "B", "C", "D", "E", "F"]

        for cls in all_classes:
            present = any(isinstance(e, dict) and e.get("class") == cls for e in evidence_items)
            is_required = cls in required
            self.result.evidence_class_results.append(
                EvidenceClassResult(
                    evidence_class=cls,
                    required=is_required,
                    present=present,
                    valid=present,
                )
            )


# ------------------------------------------------------------------ #
# CLI entry point
# ------------------------------------------------------------------ #


def main() -> None:
    """Entry point for ``python -m aiv.guard``."""
    api = GitHubAPI()
    ctx = GitHubAPI.context_from_env()

    runner = GuardRunner(ctx, api)
    result = runner.run()

    # Write result JSON
    output_path = Path("aiv_validation_result.json")
    output_path.write_text(
        json.dumps(result.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    # Print summary
    vr = result
    print(f"AIV Guard: {vr.overall_result.value}")
    print(f"  Findings: {vr.block_count} block, {vr.warn_count} warn, {vr.info_count} info")
    if vr.canonical_enabled:
        print(f"  Risk tier: {vr.risk_tier_validated}")
        print(f"  Compliance: {vr.compliance_level}")

    if vr.overall_result == OverallResult.FAIL:
        for f in vr.findings:
            if f.severity == GuardSeverity.BLOCK:
                print(f"  BLOCK [{f.rule_id}]: {f.description}")
        sys.exit(1)
