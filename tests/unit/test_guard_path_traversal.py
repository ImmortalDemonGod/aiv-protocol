"""F14: the guard's `Packet Source:` path must not escape `.github/`.

`_resolve_packet` gated the PR-body-supplied path with `startswith(".github/")`,
which is bypassable by traversal (`.github/../../etc/passwd`) — a path-traversal /
arbitrary-file-read. The fix must resolve the path and require it to stay inside
`.github/`.
"""

from __future__ import annotations

from aiv.guard.models import GuardContext
from aiv.guard.runner import GuardRunner


def _runner(body: str) -> GuardRunner:
    ctx = GuardContext(
        pr_number=42,
        head_sha="a" * 40,
        base_sha="b" * 40,
        owner="TestOwner",
        repo="test-repo",
        pr_body=body,
    )
    return GuardRunner(ctx)


class TestPacketSourcePathTraversal:
    def test_traversal_outside_github_is_blocked(self) -> None:
        # `.github/../README.md` resolves to <repo>/README.md — OUTSIDE .github/.
        # Vulnerable code (startswith ".github/") reads it; the fix must block it.
        assert _runner("Packet Source: `.github/../README.md`")._resolve_packet() is None

    def test_absolute_path_is_blocked(self) -> None:
        assert _runner("Packet Source: `/etc/passwd`")._resolve_packet() is None

    def test_valid_github_path_is_read(self) -> None:
        # A real file inside .github/ must still resolve and be read (regression).
        content = _runner("Packet Source: `.github/PULL_REQUEST_TEMPLATE.md`")._resolve_packet()
        assert content is not None
