"""RED test pinning SSRF-guard behavior for LinkValidator._head_check (Finding F15).

src/aiv/lib/validators/links.py:163-176 passes any URL straight to urlopen with no
scheme/host validation. These tests assert the correct (not-yet-implemented) behavior:
urlopen must never be reached for file:///etc/shadow, the cloud metadata address, or
127.0.0.1, while a normal https URL must still trigger exactly one HEAD request.
"""

from __future__ import annotations

import pytest

from aiv.lib.validators.links import LinkValidator


class _SpyResp:
    status = 200
    reason = "OK"

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _make_spy_urlopen(calls):
    def _spy(req, **kwargs):
        calls.append(getattr(req, "full_url", str(req)))
        return _SpyResp()

    return _spy


@pytest.mark.parametrize(
    "malicious_url",
    [
        "file:///etc/shadow",
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1/",
    ],
)
def test_head_check_blocks_ssrf_targets_without_reaching_urlopen(monkeypatch, malicious_url):
    """LinkValidator._head_check must reject dangerous schemes/hosts before ever calling urlopen."""
    calls: list[str] = []
    monkeypatch.setattr("aiv.lib.validators.links.urlopen", _make_spy_urlopen(calls))

    LinkValidator._head_check(malicious_url)

    assert calls == [], (
        f"_head_check reached urlopen for {malicious_url!r} (calls={calls}); "
        "expected the SSRF guard to block it before any network/file request."
    )


def test_head_check_still_issues_head_request_for_normal_https_url(monkeypatch):
    """A legitimate https URL must still reach urlopen exactly once."""
    calls: list[str] = []
    monkeypatch.setattr("aiv.lib.validators.links.urlopen", _make_spy_urlopen(calls))

    status, reason = LinkValidator._head_check("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")

    assert len(calls) == 1, f"expected exactly one urlopen call for an allowed https URL, got {calls}"
    assert status == 200
