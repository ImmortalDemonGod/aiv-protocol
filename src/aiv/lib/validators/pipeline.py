"""
aiv/lib/validators/pipeline.py

Complete validation pipeline that orchestrates all validators.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from ..config import AIVConfig
from ..errors import PacketParseError
from ..models import (
    AntiCheatResult,
    EvidenceClass,
    RiskTier,
    Severity,
    ValidationFinding,
    ValidationResult,
    ValidationStatus,
    VerificationPacket,
)
from ..parser import PacketParser
from .anti_cheat import AntiCheatScanner
from .evidence import EvidenceValidator
from .links import LinkValidator
from .structure import StructureValidator
from .zero_touch import ZeroTouchValidator


@dataclass
class ValidationContext:
    """Context passed through validation pipeline."""

    body: str
    diff: str | None
    config: AIVConfig
    packet: VerificationPacket | None = None
    anti_cheat_result: AntiCheatResult | None = None


class ValidationPipeline:
    """
    Orchestrates the complete validation process.

    Pipeline stages:
    1. Parse - Convert markdown to structured packet
    2. Structure - Validate packet structure completeness
    3. Links - Validate URL immutability
    4. Evidence - Validate evidence class requirements
    5. Risk-Tier - Validate required evidence classes per risk tier
    6. Zero-Touch - Validate reproduction instructions
    7. Anti-Cheat - Scan diff for test manipulation
    8. Cross-Reference - Ensure anti-cheat findings are justified
    """

    def __init__(self, config: AIVConfig | None = None, *, audit_links: bool = False):
        self.config = config or AIVConfig()

        # Initialize validators
        self.parser = PacketParser()
        self.structure_validator = StructureValidator()
        self.link_validator = LinkValidator(self.config.mutable_branches, audit_links=audit_links)
        self.evidence_validator = EvidenceValidator()
        self.zero_touch_validator = ZeroTouchValidator(self.config.zero_touch)
        self.anti_cheat_scanner = AntiCheatScanner(self.config.anti_cheat)

    def validate(self, body: str, diff: str | None = None) -> ValidationResult:
        """
        Run complete validation pipeline.

        Args:
            body: PR description markdown
            diff: Git diff (optional, for anti-cheat)

        Returns:
            Complete validation result
        """
        ctx = ValidationContext(
            body=body,
            diff=diff,
            config=self.config,
        )

        all_errors: list[ValidationFinding] = []
        all_warnings: list[ValidationFinding] = []
        all_info: list[ValidationFinding] = []

        # Stage 1: Parse
        try:
            ctx.packet = self.parser.parse(body)
            # Collect parser errors by severity
            for finding in self.parser.errors:
                if finding.severity == Severity.BLOCK:
                    all_errors.append(finding)
                elif finding.severity == Severity.WARN:
                    all_warnings.append(finding)
                else:
                    all_info.append(finding)
        except (PacketParseError, ValidationError) as e:
            all_errors.append(
                ValidationFinding(
                    rule_id="E001",
                    severity=Severity.BLOCK,
                    message=f"Failed to parse packet: {e}",
                )
            )
            return ValidationResult(
                status=ValidationStatus.FAIL,
                packet=None,
                errors=all_errors,
            )

        packet = ctx.packet
        assert packet is not None  # guaranteed by successful parse above

        # Stage 2: Structure
        structure_findings = self.structure_validator.validate(packet)
        self._distribute_findings(structure_findings, all_errors, all_warnings, all_info)

        # Stage 3: Links
        link_findings = self.link_validator.validate(packet)
        self._distribute_findings(link_findings, all_errors, all_warnings, all_info)

        # Stage 4: Evidence
        evidence_findings = self.evidence_validator.validate(packet)
        self._distribute_findings(evidence_findings, all_errors, all_warnings, all_info)

        # Stage 5: Risk-Tier Evidence Requirements
        tier_findings = self._check_tier_requirements(packet)
        self._distribute_findings(tier_findings, all_errors, all_warnings, all_info)

        # Stage 6: Zero-Touch
        zero_touch_findings = self.zero_touch_validator.validate(packet)
        self._distribute_findings(zero_touch_findings, all_errors, all_warnings, all_info)

        # Stage 7: Anti-Cheat (if diff provided)
        if diff:
            ctx.anti_cheat_result = self.anti_cheat_scanner.scan_diff(diff)

            # Stage 8: Cross-Reference
            if ctx.anti_cheat_result.requires_justification:
                unjustified = self.anti_cheat_scanner.check_justification(ctx.anti_cheat_result, packet.claims)

                for ac_finding in unjustified:
                    all_errors.append(
                        ValidationFinding(
                            rule_id="E011",
                            severity=Severity.BLOCK,
                            message=(
                                f"Test modification requires Class F justification: "
                                f"{ac_finding.finding_type} in {ac_finding.file_path}"
                            ),
                            location=f"{ac_finding.file_path}:{ac_finding.line_number or 'N/A'}",
                            suggestion=(
                                "Add a claim with Evidence Class F and include "
                                "**Justification:** explaining why this test change is valid"
                            ),
                        )
                    )

        # Determine final status
        if self.config.strict_mode:
            has_failures = len(all_errors) > 0 or len(all_warnings) > 0
        else:
            has_failures = len(all_errors) > 0

        status = ValidationStatus.FAIL if has_failures else ValidationStatus.PASS

        return ValidationResult(
            status=status,
            packet=ctx.packet,
            errors=all_errors,
            warnings=all_warnings,
            info=all_info,
        )

    # Evidence class requirements per risk tier (§6.1 of the specification).
    # ✓ = required, ○ = optional (info if missing), blank = not applicable.
    _TIER_REQUIRED: dict[RiskTier, set[EvidenceClass]] = {
        RiskTier.R0: {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL},
        RiskTier.R1: {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL, EvidenceClass.INTENT},
        RiskTier.R2: {
            EvidenceClass.EXECUTION,
            EvidenceClass.REFERENTIAL,
            EvidenceClass.INTENT,
            EvidenceClass.NEGATIVE,
        },
        RiskTier.R3: {
            EvidenceClass.EXECUTION,
            EvidenceClass.REFERENTIAL,
            EvidenceClass.INTENT,
            EvidenceClass.NEGATIVE,
            EvidenceClass.DIFFERENTIAL,
            EvidenceClass.PROVENANCE,
        },
    }
    _TIER_OPTIONAL: dict[RiskTier, set[EvidenceClass]] = {
        RiskTier.R0: set(),
        RiskTier.R1: {EvidenceClass.NEGATIVE},
        RiskTier.R2: {EvidenceClass.DIFFERENTIAL, EvidenceClass.PROVENANCE},
        RiskTier.R3: set(),
    }

    def _check_tier_requirements(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Enforce evidence class requirements based on risk tier."""
        findings: list[ValidationFinding] = []

        if packet.risk_tier is None:
            # No classification section — warn but don't block
            findings.append(
                ValidationFinding(
                    rule_id="E014",
                    severity=Severity.WARN,
                    message="Missing ## Classification section. Cannot enforce risk-tier evidence requirements.",
                    location="Packet-wide",
                    suggestion="Add a ## Classification (required) section with a risk_tier field.",
                )
            )
            return findings

        tier = packet.risk_tier
        present_classes = packet.evidence_classes_present

        required = self._TIER_REQUIRED.get(tier, set())
        optional = self._TIER_OPTIONAL.get(tier, set())

        for ev_class in required:
            if ev_class not in present_classes:
                findings.append(
                    ValidationFinding(
                        rule_id="E019",
                        severity=Severity.BLOCK,
                        message=(
                            f"Risk tier {tier.value} requires Class {ev_class.value} "
                            f"({ev_class.name.title()}) evidence, but none was found."
                        ),
                        location="Packet-wide",
                        suggestion=f"Add a claim or evidence section with Class {ev_class.value} evidence.",
                    )
                )

        for ev_class in optional:
            if ev_class not in present_classes:
                findings.append(
                    ValidationFinding(
                        rule_id="E020",
                        severity=Severity.INFO,
                        message=(
                            f"Risk tier {tier.value}: Class {ev_class.value} "
                            f"({ev_class.name.title()}) evidence is recommended but not required."
                        ),
                        location="Packet-wide",
                    )
                )

        return findings

    @staticmethod
    def _distribute_findings(
        findings: list[ValidationFinding],
        errors: list[ValidationFinding],
        warnings: list[ValidationFinding],
        info: list[ValidationFinding],
    ) -> None:
        """Distribute findings into error/warning/info lists by severity."""
        for finding in findings:
            if finding.severity == Severity.BLOCK:
                errors.append(finding)
            elif finding.severity == Severity.WARN:
                warnings.append(finding)
            else:
                info.append(finding)
