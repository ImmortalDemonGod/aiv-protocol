"""
aiv/lib/validators/links.py

URL validation and immutability checking (Addendum 2.2).
"""

from __future__ import annotations

import ipaddress
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ..config import MutableBranchConfig
from ..models import (
    ArtifactLink,
    ValidationFinding,
    VerificationPacket,
)
from .base import BaseValidator

log = logging.getLogger(__name__)

_LINK_CHECK_TIMEOUT = 10  # seconds per HEAD request


class LinkValidator(BaseValidator):
    """
    Validates artifact links for accessibility and immutability.
    """

    def __init__(
        self,
        config: MutableBranchConfig | None = None,
        *,
        audit_links: bool = False,
    ):
        self.config = config or MutableBranchConfig()
        self.audit_links = audit_links

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate all links in a packet."""
        return self.validate_packet_links(packet)

    def validate_packet_links(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """
        Validate all links in a packet.

        Checks:
        - Class E links must be immutable (SHA-pinned)
        - All GitHub blob/tree links should be immutable
        - Links are checked for vitality when audit_links=True (HTTP HEAD)
        """
        errors: list[ValidationFinding] = []

        # Validate intent link (Class E) - MUST be immutable if it's a URL
        intent_link = packet.intent.evidence_link
        if isinstance(intent_link, ArtifactLink):
            if not intent_link.is_immutable:
                errors.append(
                    self._make_finding(
                        rule_id="E004",
                        severity="block",
                        message=(f"Class E Evidence must be immutable. Reason: {intent_link.immutability_reason}"),
                        location="Section 0 (Intent Alignment)",
                        suggestion=(
                            "Link to a specific commit SHA, not a branch. "
                            "Example: /blob/a1b2c3d/docs/spec.md instead of /blob/main/..."
                        ),
                    )
                )
        elif isinstance(intent_link, str):
            errors.append(
                self._make_finding(
                    rule_id="E004",
                    severity="info",
                    message=(
                        "Class E Evidence is a plain text reference, not a URL. "
                        "Consider using a SHA-pinned permalink for immutability."
                    ),
                    location="Section 0 (Intent Alignment)",
                )
            )

        # Validate claim artifacts using configured mutable branch set
        for claim in packet.claims:
            if isinstance(claim.artifact, ArtifactLink):
                link = claim.artifact

                # Re-check blob/tree links with configured mutable branches
                if link.link_type == "github_blob":
                    recheck = ArtifactLink.from_url(
                        str(link.url),
                        mutable_branches=self.config.mutable_branches,
                        min_sha_length=self.config.min_sha_length,
                    )
                    if not recheck.is_immutable:
                        errors.append(
                            self._make_finding(
                                rule_id="E009",
                                severity="block",
                                message=(f"Evidence artifact link is mutable. Reason: {recheck.immutability_reason}"),
                                location=f"Section {claim.section_number}",
                                suggestion=(
                                    "Use a SHA-pinned link. Copy the link from the 'Copy permalink' option in GitHub."
                                ),
                            )
                        )

        # Optional: verify link vitality via HTTP HEAD requests
        if self.audit_links:
            errors.extend(self._check_link_vitality(packet))

        return errors

    def _check_link_vitality(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Send HTTP HEAD requests to verify all URLs in the packet are reachable."""
        findings: list[ValidationFinding] = []
        urls_checked: set[str] = set()

        # Collect all ArtifactLink URLs
        url_locations: list[tuple[str, str]] = []

        intent_link = packet.intent.evidence_link
        if isinstance(intent_link, ArtifactLink):
            url_locations.append((str(intent_link.url), "Section 0 (Intent Alignment)"))

        for claim in packet.claims:
            if isinstance(claim.artifact, ArtifactLink):
                url_locations.append((str(claim.artifact.url), f"Section {claim.section_number}"))

        for url, location in url_locations:
            if url in urls_checked:
                continue
            urls_checked.add(url)

            status, reason = self._head_check(url)
            if status is not None and status >= 400:
                findings.append(
                    self._make_finding(
                        rule_id="E021",
                        severity="block",
                        message=f"Evidence link unreachable (HTTP {status}): {url}",
                        location=location,
                        suggestion=(
                            "Verify the URL is correct — check for SHA typos, deleted resources, or permission issues."
                        ),
                    )
                )
            elif status is None:
                findings.append(
                    self._make_finding(
                        rule_id="E021",
                        severity="warn",
                        message=f"Evidence link could not be reached ({reason}): {url}",
                        location=location,
                        suggestion="Check network connectivity or URL validity.",
                    )
                )

        return findings

    _ALLOWED_SCHEMES = {"http", "https"}

    @staticmethod
    def _is_url_allowed(url: str) -> bool:
        """Reject non-http(s) schemes and requests to loopback/private/link-local hosts."""
        parsed = urlparse(url)
        if parsed.scheme not in LinkValidator._ALLOWED_SCHEMES:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        try:
            addr = ipaddress.ip_address(hostname)
        except ValueError:
            return True
        return not (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        )

    @staticmethod
    def _head_check(url: str) -> tuple[int | None, str]:
        """Send an HTTP HEAD request. Returns (status_code, reason) or (None, error_msg)."""
        if not LinkValidator._is_url_allowed(url):
            return (None, "blocked by SSRF guard: disallowed scheme or host")
        try:
            req = Request(url, method="HEAD")
            req.add_header("User-Agent", "aiv-link-checker/1.0")
            with urlopen(req, timeout=_LINK_CHECK_TIMEOUT) as resp:
                return (resp.status, resp.reason)
        except HTTPError as e:
            return (e.code, str(e.reason))
        except URLError as e:
            return (None, str(e.reason))
        except Exception as e:
            log.debug("Link check failed for %s: %s", url, e)
            return (None, str(e))
