"""
aiv/lib/validators/links.py

URL validation and immutability checking (Addendum 2.2).
"""

from __future__ import annotations

import contextlib
import ipaddress
import logging
import socket
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

if TYPE_CHECKING:
    from collections.abc import Iterator

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
    def _is_disallowed_ip(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        """True if addr is loopback/private/link-local/reserved/multicast/unspecified."""
        return bool(
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        )

    @staticmethod
    def _resolve_validated_ip(hostname: str) -> str | None:
        """Resolve hostname to a single IP parsed_ip, rejecting it if any resolved
        address is internal. Returns None if the host is disallowed or unresolvable.

        Hostnames that Python's ``ipaddress`` module rejects as malformed (e.g. the
        legacy short form ``127.1``) are NOT assumed safe — they still go through
        DNS resolution and are validated like any other hostname, closing the
        bypass where `ipaddress.ip_address()` raising ValueError was previously
        treated as "not an IP, so it must be a normal hostname".
        """
        try:
            parsed_ip = ipaddress.ip_address(hostname)
        except ValueError:
            parsed_ip = None
        if parsed_ip is not None:
            return None if LinkValidator._is_disallowed_ip(parsed_ip) else hostname

        try:
            infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            return None
        if not infos:
            return None

        resolved_ip: str | None = None
        for _family, _type, _proto, _canonname, sockaddr in infos:
            ip_str = str(sockaddr[0])
            try:
                resolved_addr = ipaddress.ip_address(ip_str)
            except ValueError:
                return None
            if LinkValidator._is_disallowed_ip(resolved_addr):
                return None
            if resolved_ip is None:
                resolved_ip = ip_str
        return resolved_ip

    @staticmethod
    def _is_url_allowed(url: str) -> bool:
        """Reject non-http(s) schemes and requests to loopback/private/link-local hosts."""
        parsed = urlparse(url)
        if parsed.scheme not in LinkValidator._ALLOWED_SCHEMES:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        return LinkValidator._resolve_validated_ip(hostname) is not None

    @staticmethod
    @contextlib.contextmanager
    def _pinned_dns(hostname: str, resolved_ip: str) -> Iterator[None]:
        """Force DNS lookups of `hostname` to `resolved_ip` for the duration of the
        request.

        Without this, `urlopen` re-resolves the hostname at connect time, after the
        SSRF allowlist check already ran — a DNS-rebinding attacker can flip the
        record to an internal address in that window. Pinning collapses the
        check-then-connect race by making the validated address the only address
        the connection can ever use.
        """
        real_getaddrinfo = socket.getaddrinfo

        def _pinned(host: str, *args: Any, **kwargs: Any) -> object:
            if host == hostname:
                return real_getaddrinfo(resolved_ip, *args, **kwargs)
            return real_getaddrinfo(host, *args, **kwargs)

        socket.getaddrinfo = _pinned  # type: ignore[assignment]
        try:
            yield
        finally:
            socket.getaddrinfo = real_getaddrinfo

    @staticmethod
    def _head_check(url: str) -> tuple[int | None, str]:
        """Send an HTTP HEAD request. Returns (status_code, reason) or (None, error_msg)."""
        parsed = urlparse(url)
        hostname = parsed.hostname
        if parsed.scheme not in LinkValidator._ALLOWED_SCHEMES or not hostname:
            return (None, "blocked by SSRF guard: disallowed scheme or host")

        validated_ip = LinkValidator._resolve_validated_ip(hostname)
        if validated_ip is None:
            return (None, "blocked by SSRF guard: disallowed scheme or host")

        try:
            req = Request(url, method="HEAD")
            req.add_header("User-Agent", "aiv-link-checker/1.0")
            with LinkValidator._pinned_dns(hostname, validated_ip), urlopen(req, timeout=_LINK_CHECK_TIMEOUT) as resp:
                return (resp.status, resp.reason)
        except HTTPError as e:
            return (e.code, str(e.reason))
        except URLError as e:
            return (None, str(e.reason))
        except Exception as e:
            log.debug("Link check failed for %s: %s", url, e)
            return (None, str(e))
