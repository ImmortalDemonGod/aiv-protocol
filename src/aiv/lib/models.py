"""
aiv/lib/models.py

Core data models for the AIV Protocol Suite.
All models are immutable (frozen) to ensure validation integrity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class EvidenceClass(str, Enum):
    """
    The six classes of evidence defined by the AIV Protocol.

    Each class proves a different aspect of the change:
    - A: Behavior (execution)
    - B: Structure (code references)
    - C: Safety (negative evidence)
    - D: Differential (state changes)
    - E: Alignment (intent)
    - F: Provenance (integrity)
    """

    EXECUTION = "A"
    REFERENTIAL = "B"
    NEGATIVE = "C"
    DIFFERENTIAL = "D"
    INTENT = "E"
    PROVENANCE = "F"

    @classmethod
    def from_string(cls, value: str) -> EvidenceClass:
        """Parse evidence class from various string formats."""
        normalized = value.strip().upper()

        # Handle "A", "Class A", "A (Execution)", etc.
        for member in cls:
            if normalized == member.value:
                return member
            if normalized == member.name:
                return member
            if normalized.startswith(member.value):
                return member

        raise ValueError(f"Unknown evidence class: {value}")


class Severity(str, Enum):
    """Validation result severity levels."""

    BLOCK = "block"  # PR cannot be merged
    WARN = "warn"  # Flagged but not blocking
    INFO = "info"  # Informational only


class ValidationStatus(str, Enum):
    """Overall validation status."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class ArtifactLink(BaseModel):
    """
    A validated URL reference to evidence.

    Performs structural validation and immutability detection.
    """

    model_config = ConfigDict(frozen=True)

    url: HttpUrl
    is_immutable: bool = Field(description="Whether the link is SHA-pinned")
    immutability_reason: str | None = Field(default=None, description="Why the link is/isn't immutable")
    link_type: Literal["github_blob", "github_actions", "github_pr", "external"] = Field(
        description="Categorized link type"
    )

    @classmethod
    def from_url(
        cls,
        url: str,
        mutable_branches: set[str] | None = None,
        min_sha_length: int = 7,
    ) -> ArtifactLink:
        """
        Parse and validate a URL, detecting immutability.

        Immutability rules:
        - GitHub blob/tree URLs must contain a 40-char SHA, not branch names
        - GitHub Actions URLs are immutable (run IDs are permanent)
        - External URLs are assumed mutable unless they contain version/hash
        """
        parsed = urlparse(url)

        # Detect GitHub URLs
        if "github.com" in (parsed.netloc or ""):
            path_parts = parsed.path.strip("/").split("/")

            # Check for actions run
            if "actions" in path_parts and "runs" in path_parts:
                return cls(
                    url=url,  # type: ignore[arg-type]
                    is_immutable=True,
                    immutability_reason="GitHub Actions run IDs are permanent",
                    link_type="github_actions",
                )

            # Check for blob/tree references
            if "blob" in path_parts or "tree" in path_parts:
                # Find the ref (comes after blob/tree)
                try:
                    idx = path_parts.index("blob") if "blob" in path_parts else path_parts.index("tree")
                    ref = path_parts[idx + 1] if idx + 1 < len(path_parts) else None
                except (ValueError, IndexError):
                    ref = None

                if ref:
                    # Check if ref is a SHA (40 hex chars) or short SHA
                    is_sha = len(ref) >= min_sha_length and all(c in "0123456789abcdef" for c in ref.lower())

                    # Check for known mutable refs (configurable)
                    _default_mutable = {"main", "master", "develop", "staging", "trunk", "dev", "HEAD"}
                    mutable_refs = mutable_branches if mutable_branches is not None else _default_mutable
                    is_mutable_branch = ref.lower() in {r.lower() for r in mutable_refs}

                    if is_sha:
                        return cls(
                            url=url,  # type: ignore[arg-type]
                            is_immutable=True,
                            immutability_reason=f"SHA-pinned reference: {ref[:7]}...",
                            link_type="github_blob",
                        )
                    elif is_mutable_branch:
                        return cls(
                            url=url,  # type: ignore[arg-type]
                            is_immutable=False,
                            immutability_reason=f"Mutable branch reference: {ref}",
                            link_type="github_blob",
                        )
                    else:
                        # Could be a tag or custom branch - warn but don't block
                        return cls(
                            url=url,  # type: ignore[arg-type]
                            is_immutable=False,
                            immutability_reason=f"Non-SHA reference: {ref} (may be tag or branch)",
                            link_type="github_blob",
                        )

            # GitHub PR
            if "pull" in path_parts:
                return cls(
                    url=url,  # type: ignore[arg-type]
                    is_immutable=True,
                    immutability_reason="PR numbers are permanent",
                    link_type="github_pr",
                )

        # External URL - assume mutable
        return cls(
            url=url,  # type: ignore[arg-type]
            is_immutable=False,
            immutability_reason="External URL (immutability unknown)",
            link_type="external",
        )


class Claim(BaseModel):
    """
    A single claim within a Verification Packet.

    Each claim asserts something about the change and provides
    evidence to support that assertion.
    """

    model_config = ConfigDict(frozen=True)

    section_number: int = Field(ge=1, description="Section number in packet")
    description: str = Field(min_length=10, description="The claim statement")
    evidence_class: EvidenceClass
    artifact: ArtifactLink | str = Field(description="Evidence artifact (URL or description)")
    reproduction: str = Field(description="How to reproduce/verify the evidence")

    # Optional fields for specific evidence classes
    fallback_artifact: str | None = Field(default=None, description="Fallback if primary artifact unavailable")
    justification: str | None = Field(default=None, description="Required for Class F when tests are modified")


class RiskTier(str, Enum):
    """Risk classification tiers per §5.1 of the AIV specification."""

    R0 = "R0"  # Trivial: docs, comments, formatting only
    R1 = "R1"  # Low: isolated logic, no critical surfaces
    R2 = "R2"  # Medium: broad refactors, API changes, migrations
    R3 = "R3"  # High: critical surfaces (auth, crypto, PII)

    @classmethod
    def from_string(cls, value: str) -> RiskTier:
        """Parse risk tier from string like 'R0', 'R2', etc."""
        upper = value.strip().upper()
        try:
            return cls(upper)
        except ValueError as err:
            raise ValueError(f"Unknown risk tier: {value!r}. Expected R0, R1, R2, or R3.") from err


class IntentSection(BaseModel):
    """
    Section 0: Intent Alignment (Mandatory).

    Must contain a Class E evidence link to the originating spec.
    The link can be a validated ArtifactLink (URL) or a plain text
    reference (e.g. "AIV Protocol Addendum 2.5 — description").
    """

    model_config = ConfigDict(frozen=True)

    evidence_link: ArtifactLink | str
    verifier_check: str = Field(min_length=10, description="Description of what the verifier should confirm")


class VerificationPacket(BaseModel):
    """
    Complete parsed Verification Packet.

    This is the structured representation of the markdown packet
    attached to a Pull Request.
    """

    model_config = ConfigDict(frozen=True)

    version: str = Field(default="2.1", pattern=r"^\d+\.\d+$")
    risk_tier: RiskTier | None = Field(
        default=None, description="Risk classification from ## Classification YAML block"
    )
    evidence_classes_present: set[EvidenceClass] = Field(
        default_factory=set,
        description="All evidence classes found in evidence sections, regardless of claim assignment",
    )
    intent: IntentSection
    claims: list[Claim] = Field(min_length=1)
    raw_markdown: str = Field(description="Original markdown for reference")

    @property
    def all_links(self) -> list[ArtifactLink]:
        """Extract all artifact links for bulk validation."""
        links: list[ArtifactLink] = []
        if isinstance(self.intent.evidence_link, ArtifactLink):
            links.append(self.intent.evidence_link)
        for claim in self.claims:
            if isinstance(claim.artifact, ArtifactLink):
                links.append(claim.artifact)
        return links

    @property
    def has_provenance_evidence(self) -> bool:
        """Check if packet includes Class F (Provenance) evidence.

        Consults both claim assignments and `evidence_classes_present`: a packet whose
        `### Class F (Provenance)` section carries real content has provenance evidence even when
        no individual claim parsed as PROVENANCE-classed. Checking claims alone made E010 fire on
        honest packets that mentioned an issue number anywhere in the intent text while their
        Class F section sat right there (false positive found by the money-agent integration).
        """
        return EvidenceClass.PROVENANCE in self.evidence_classes_present or any(
            c.evidence_class == EvidenceClass.PROVENANCE for c in self.claims
        )


class ValidationFinding(BaseModel):
    """A single validation error or warning."""

    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(pattern=r"^E\d{3}$", description="Rule identifier")
    severity: Severity
    message: str
    location: str | None = Field(default=None, description="Where in the packet the error occurred")
    suggestion: str | None = Field(default=None, description="How to fix the issue")


class ValidationResult(BaseModel):
    """Complete validation result for a packet."""

    model_config = ConfigDict(frozen=True)

    status: ValidationStatus
    packet: VerificationPacket | None = Field(default=None, description="Parsed packet if parsing succeeded")
    errors: list[ValidationFinding] = Field(default_factory=list)
    warnings: list[ValidationFinding] = Field(default_factory=list)
    info: list[ValidationFinding] = Field(default_factory=list)

    # Metadata
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    validator_version: str = Field(default="1.0.0")

    @property
    def blocking_errors(self) -> list[ValidationFinding]:
        """Get only errors that block merge."""
        return [e for e in self.errors if e.severity == Severity.BLOCK]

    @property
    def is_valid(self) -> bool:
        """Check if packet passes all blocking validations."""
        return len(self.blocking_errors) == 0


class AntiCheatFinding(BaseModel):
    """A potential anti-cheat violation detected in the diff."""

    model_config = ConfigDict(frozen=True)

    finding_type: Literal["deleted_assertion", "skipped_test", "mock_bypass", "relaxed_condition", "removed_test_file"]
    file_path: str
    line_number: int | None = None
    original_content: str | None = None
    severity: Severity = Severity.BLOCK
    requires_justification: bool = True


class AntiCheatResult(BaseModel):
    """Results of anti-cheat analysis on a diff."""

    model_config = ConfigDict(frozen=True)

    findings: list[AntiCheatFinding] = Field(default_factory=list)
    files_analyzed: int
    test_files_modified: int

    @property
    def has_violations(self) -> bool:
        """Check if any blocking violations were found."""
        return any(f.severity == Severity.BLOCK for f in self.findings)

    @property
    def requires_justification(self) -> bool:
        """Check if any findings require justification in packet."""
        return any(f.requires_justification for f in self.findings)


class FrictionScore(BaseModel):
    """Quantified measure of reproduction instruction complexity."""

    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=0, description="Higher = more friction")
    step_count: int = Field(ge=0)
    prohibited_patterns_found: list[str] = Field(default_factory=list)
    is_zero_touch_compliant: bool
    recommendation: str | None = None
