"""RED test pinning SSRF-guard behavior for LinkValidator._head_check (Finding F15).

src/aiv/lib/validators/links.py:163-176 passes any URL straight to urlopen with no
scheme/host validation. These tests assert the correct behavior: urlopen must never
be reached for file:///etc/shadow, the cloud metadata address, 127.0.0.1, or hostnames
(literal-but-malformed IPs, "localhost", or attacker-controlled DNS names) that resolve
to an internal address — while a normal https URL must still trigger exactly one HEAD
request. DNS resolution is mocked throughout so these tests never touch the network.
"""

from __future__ import annotations

import socket
from typing import Any

import pytest

from aiv.lib.validators.links import LinkValidator


class _SpyResp:
    status = 200
    reason = "OK"

    def __enter__(self) -> _SpyResp:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def _make_spy_urlopen(calls: list[str]) -> Any:
    def _spy(req: Any, **kwargs: Any) -> _SpyResp:
        calls.append(getattr(req, "full_url", str(req)))
        return _SpyResp()

    return _spy


def _fake_resolver(mapping: dict[str, str]) -> Any:
    """Deterministic stand-in for socket.getaddrinfo, so tests never touch real DNS."""

    def _resolve(host: str, *args: Any, **kwargs: Any) -> list[tuple[Any, ...]]:
        ip = mapping.get(host)
        if ip is None:
            raise socket.gaierror(f"no mapping configured for {host!r}")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    return _resolve


@pytest.mark.parametrize(
    "malicious_url,dns_map",
    [
        ("file:///etc/shadow", {}),
        ("http://169.254.169.254/latest/meta-data/", {}),
        ("http://127.0.0.1/", {}),
        ("http://localhost/", {"localhost": "127.0.0.1"}),
        ("http://127.1/", {"127.1": "127.0.0.1"}),
        (
            "http://metadata.internal.example.com/",
            {"metadata.internal.example.com": "169.254.169.254"},
        ),
        ("http://rebind.example.com/", {"rebind.example.com": "10.0.0.5"}),
    ],
)
def test_head_check_blocks_ssrf_targets_without_reaching_urlopen(
    monkeypatch: pytest.MonkeyPatch, malicious_url: str, dns_map: dict[str, str]
) -> None:
    """LinkValidator._head_check must reject dangerous schemes/hosts before ever calling urlopen.

    dns_map covers hostnames that Python's ipaddress module cannot parse as a
    literal (e.g. "127.1", "localhost", attacker-controlled DNS names) but that
    still resolve to an internal address — these must be blocked too, not just
    the literal-IP targets.
    """
    calls: list[str] = []
    monkeypatch.setattr("aiv.lib.validators.links.urlopen", _make_spy_urlopen(calls))
    monkeypatch.setattr("aiv.lib.validators.links.socket.getaddrinfo", _fake_resolver(dns_map))

    LinkValidator._head_check(malicious_url)

    assert calls == [], (
        f"_head_check reached urlopen for {malicious_url!r} (calls={calls}); "
        "expected the SSRF guard to block it before any network/file request."
    )


def test_head_check_still_issues_head_request_for_normal_https_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """A legitimate https URL must still reach urlopen exactly once."""
    calls: list[str] = []
    monkeypatch.setattr("aiv.lib.validators.links.urlopen", _make_spy_urlopen(calls))
    monkeypatch.setattr(
        "aiv.lib.validators.links.socket.getaddrinfo",
        _fake_resolver({"github.com": "140.82.114.4"}),
    )

    status, reason = LinkValidator._head_check("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")

    assert len(calls) == 1, f"expected exactly one urlopen call for an allowed https URL, got {calls}"
    assert status == 200


def test_pinned_dns_forces_resolution_to_validated_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Even if the hostname would later resolve elsewhere (DNS rebinding), the
    pinned context must force resolution to the address that was already
    validated by the SSRF guard, closing the check-then-connect TOCTOU race."""

    def _rebinding_resolver(host: str, *args: Any, **kwargs: Any) -> list[tuple[Any, ...]]:
        if host == "attacker.example.com":
            # What DNS would return if queried again at connect time.
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 0))]
        if host == "203.0.113.10":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.10", 0))]
        raise socket.gaierror(f"unexpected host {host!r}")

    monkeypatch.setattr("aiv.lib.validators.links.socket.getaddrinfo", _rebinding_resolver)

    with LinkValidator._pinned_dns("attacker.example.com", "203.0.113.10"):
        result = socket.getaddrinfo("attacker.example.com", None)

    assert result[0][4][0] == "203.0.113.10", (
        "expected the pinned context to force resolution to the validated IP, "
        f"got {result[0][4][0]!r} (a DNS-rebinding attacker would win the race otherwise)"
    )
