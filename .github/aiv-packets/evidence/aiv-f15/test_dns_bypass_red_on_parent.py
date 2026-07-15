"""Standalone RED harness: proves the pre-5096b42 `_is_url_allowed` treats any
hostname that fails `ipaddress.ip_address()` parsing as automatically safe,
with NO DNS resolution performed at all. Run against the 5096b42^ worktree
checkout (old links.py). No monkeypatch of `socket` is needed/possible here
because the old module never imports or calls `socket` -- that omission is
exactly the bug 5096b42 fixes.
"""

from __future__ import annotations

from typing import Any

from aiv.lib.validators.links import LinkValidator


class _SpyResp:
    status = 200
    reason = "OK"

    def __enter__(self) -> "_SpyResp":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def _make_spy_urlopen(calls: list[str]) -> Any:
    def _spy(req: Any, **kwargs: Any) -> _SpyResp:
        calls.append(getattr(req, "full_url", str(req)))
        return _SpyResp()

    return _spy


DNS_BYPASS_TARGETS = [
    "http://127.1/",  # malformed-literal IP; ipaddress.ip_address("127.1") raises ValueError
    "http://localhost/",  # resolves to 127.0.0.1 but is not a literal IP
    "http://metadata.internal.example.com/",  # attacker DNS name that would resolve to 169.254.169.254
]


def test_dns_bypass_targets_reach_urlopen_on_pre_fix_code(monkeypatch: Any) -> None:
    calls: list[str] = []
    monkeypatch.setattr("aiv.lib.validators.links.urlopen", _make_spy_urlopen(calls))
    for url in DNS_BYPASS_TARGETS:
        allowed = LinkValidator._is_url_allowed(url)
        status, _ = LinkValidator._head_check(url)
        assert allowed is True, f"expected pre-fix bug: _is_url_allowed({url!r}) should wrongly return True"
        assert status == 200, f"expected pre-fix bug: _head_check({url!r}) should wrongly reach urlopen"
    assert len(calls) == len(DNS_BYPASS_TARGETS), (
        f"expected pre-fix code to call urlopen for all {len(DNS_BYPASS_TARGETS)} DNS-bypass targets, got {calls}"
    )
