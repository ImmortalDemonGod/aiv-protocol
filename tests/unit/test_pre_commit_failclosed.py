"""
Regression tests for F43 / issue #24 — the pre-commit gate must fail CLOSED on a
CONTENT-INVALID packet, not only on an internal exception.

PR #10 fixed F43 (exception path: ``except Exception: return True`` -> ``return False``)
and pinned the *exception* arm of fail-closed. The SVP review of #10 (issue #24) noted the
*explicit-validation-failure* arm was only covered indirectly (by stubbing the whole
``_validate_packet``). These tests drive the real function with a mocked ``aiv check`` /
``aiv audit`` returning a non-zero exit, asserting the commit is blocked
(``_validate_packet`` returns False) — the exact condition that would falsify the claim.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from aiv.hooks.pre_commit import _validate_packet

_PACKET = ".github/aiv-packets/VERIFICATION_PACKET_X.md"
_CONTENT = "# AIV Verification Packet (v2.1)\n\nsome staged packet content\n"


class TestValidatePacketFailsClosedOnInvalidContent:
    """#24: a packet that FAILS validation must block the commit (return False),
    not just pass on the happy path."""

    def test_blocks_when_aiv_check_reports_invalid(self) -> None:
        # `aiv check` exits non-zero (e.g. E004 link not SHA-pinned) -> block.
        with (
            patch("aiv.hooks.pre_commit._run_git", return_value=_CONTENT),
            patch(
                "aiv.hooks.pre_commit.subprocess.run",
                return_value=Mock(returncode=1, stdout="[E004] link not SHA-pinned", stderr=""),
            ),
        ):
            assert _validate_packet(_PACKET) is False

    def test_blocks_when_aiv_audit_reports_invalid(self) -> None:
        # `aiv check` passes (0) but `aiv audit` fails (1, e.g. TODO remnant) -> block.
        with (
            patch("aiv.hooks.pre_commit._run_git", return_value=_CONTENT),
            patch(
                "aiv.hooks.pre_commit.subprocess.run",
                side_effect=[
                    Mock(returncode=0, stdout="", stderr=""),
                    Mock(returncode=1, stdout="TODO remnant found", stderr=""),
                ],
            ),
        ):
            assert _validate_packet(_PACKET) is False
