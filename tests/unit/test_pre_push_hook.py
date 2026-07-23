"""
tests/unit/test_pre_push_hook.py

Unit tests for the pre-push hook — verifies detection of commits
that bypassed the pre-commit hook via ``git commit --no-verify``.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from aiv.hooks.pre_push import (
    _aiv_adoption_sha,
    _is_functional,
    _is_packet,
    _is_pre_adoption,
    check_commits,
    main,
)

# ---------------------------------------------------------------------------
# Helper classification tests
# ---------------------------------------------------------------------------


class TestIsPacket:
    def test_standard_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_FOO.md") is True

    def test_legacy_packet(self) -> None:
        assert _is_packet(".github/VERIFICATION_PACKET_OLD.md") is True

    def test_not_a_packet(self) -> None:
        assert _is_packet("README.md") is False
        assert _is_packet("src/main.py") is False


class TestIsFunctional:
    def test_src_functional(self) -> None:
        assert _is_functional("src/aiv/cli/main.py") is True

    def test_tests_functional(self) -> None:
        assert _is_functional("tests/unit/test_foo.py") is True

    def test_root_file(self) -> None:
        assert _is_functional("pyproject.toml") is True

    def test_docs_not_functional(self) -> None:
        assert _is_functional("docs/guide.md") is False
        assert _is_functional("README.md") is False

    def test_custom_prefixes_respected(self) -> None:
        """P0-4: _is_functional accepts custom prefixes from .aiv.yml."""
        custom_prefixes = ("backend/", "frontend/")
        custom_roots: set[str] = set()
        assert _is_functional("backend/api.py", custom_prefixes, custom_roots) is True
        assert _is_functional("frontend/app.ts", custom_prefixes, custom_roots) is True
        assert _is_functional("src/main.py", custom_prefixes, custom_roots) is False

    def test_custom_root_files_respected(self) -> None:
        """P0-4: _is_functional accepts custom root files from .aiv.yml."""
        custom_prefixes: tuple[str, ...] = ()
        custom_roots = {"Makefile", "Dockerfile"}
        assert _is_functional("Makefile", custom_prefixes, custom_roots) is True
        assert _is_functional("pyproject.toml", custom_prefixes, custom_roots) is False

    def test_empty_prefixes_means_nothing_functional(self) -> None:
        """Empty tuple/set should mean nothing is functional, not fall back to defaults."""
        assert _is_functional("src/main.py", (), set()) is False
        assert _is_functional("pyproject.toml", (), set()) is False


# ---------------------------------------------------------------------------
# check_commits tests
# ---------------------------------------------------------------------------


class TestCheckCommitsConfigPropagation:
    """P0-4: check_commits reads .aiv.yml via load_hook_config."""

    def test_custom_prefix_detected_as_functional(self) -> None:
        """A file under a custom prefix from .aiv.yml is treated as functional."""
        custom_cfg = (("backend/",), set())
        with (
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
            patch("aiv.hooks.pre_push.load_hook_config", return_value=custom_cfg),
        ):
            mock_files.return_value = ["backend/api.py"]
            violations = check_commits(["a" * 40])
        assert len(violations) == 1  # functional without packet = violation

    def test_default_prefix_ignored_with_custom_config(self) -> None:
        """src/ is NOT functional when .aiv.yml only lists backend/."""
        custom_cfg = (("backend/",), set())
        with (
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
            patch("aiv.hooks.pre_push.load_hook_config", return_value=custom_cfg),
        ):
            mock_files.return_value = ["src/main.py"]
            violations = check_commits(["a" * 40])
        assert len(violations) == 0  # not functional = no violation


class TestCheckCommits:
    def test_violation_detected(self) -> None:
        """Commit with functional files but no packet is a violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = ["src/aiv/cli/main.py"]
            violations = check_commits(["a" * 40])

        assert len(violations) == 1
        assert violations[0][0] == "a" * 7
        assert "src/aiv/cli/main.py" in violations[0][1]

    def test_clean_commit(self) -> None:
        """Commit with functional file + packet has no violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = [
                "src/aiv/cli/main.py",
                ".github/aiv-packets/VERIFICATION_PACKET_MAIN.md",
            ]
            violations = check_commits(["b" * 40])

        assert len(violations) == 0

    def test_docs_only_skipped(self) -> None:
        """Commit with only docs files has no violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = ["README.md", "docs/guide.md"]
            violations = check_commits(["c" * 40])

        assert len(violations) == 0

    def test_multiple_commits_covered_by_range_packet(self) -> None:
        """Two-Layer: functional-only commit is covered by a packet elsewhere in the range."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: has a packet (covers the range)
                ["src/foo.py", ".github/aiv-packets/VERIFICATION_PACKET_FOO.md"],
                # Commit 2: functional-only, but covered by range evidence
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 0

    def test_multiple_commits_no_evidence_anywhere(self) -> None:
        """No evidence in range: all functional-only commits are violations."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                ["src/foo.py"],
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 2

    def test_layer2_packet_covers_range(self) -> None:
        """A PACKET_*.md in the range covers functional-only commits."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: functional-only
                ["src/aiv/lib/change.py"],
                # Commit 2: functional-only
                ["src/aiv/hooks/pre_commit.py"],
                # Commit 3: Layer 2 packet only
                [".github/aiv-packets/PACKET_feature.md"],
            ]
            violations = check_commits(["a" * 40, "b" * 40, "c" * 40])

        assert len(violations) == 0

    def test_evidence_file_covers_range(self) -> None:
        """An EVIDENCE_*.md in the range covers functional-only commits."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: functional + evidence (aiv commit)
                ["src/foo.py", ".github/aiv-evidence/EVIDENCE_FOO.md"],
                # Commit 2: functional-only, covered by range evidence
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 0


# ---------------------------------------------------------------------------
# main() tests — stdin parsing + exit code
# ---------------------------------------------------------------------------


class TestMain:
    def test_clean_push_returns_0(self) -> None:
        """Push with all clean commits returns 0."""
        stdin_line = f"refs/heads/main {'b' * 40} refs/heads/main {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
        ):
            mock_range.return_value = ["b" * 40]
            mock_files.return_value = [
                "src/foo.py",
                ".github/aiv-packets/VERIFICATION_PACKET_FOO.md",
            ]
            result = main()

        assert result == 0

    def test_violation_returns_1(self) -> None:
        """Push with a violating commit returns 1."""
        stdin_line = f"refs/heads/main {'b' * 40} refs/heads/main {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
        ):
            mock_range.return_value = ["b" * 40]
            mock_files.return_value = ["src/aiv/cli/main.py"]
            result = main()

        assert result == 1

    def test_empty_stdin_returns_0(self) -> None:
        """No push refs = nothing to check."""
        with patch("aiv.hooks.pre_push.sys.stdin", []):
            result = main()

        assert result == 0

    def test_branch_deletion_returns_0(self) -> None:
        """Deleting a branch (local sha = 0*40) should pass."""
        zero = "0" * 40
        stdin_line = f"refs/heads/old {zero} refs/heads/old {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
        ):
            mock_range.return_value = []
            result = main()

        assert result == 0


# ---------------------------------------------------------------------------
# Issue #29 bug #3: bootstrap / pre-adoption exemption
# ---------------------------------------------------------------------------


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=str(root), capture_output=True, check=True)
    # A baseline root commit, so the commits under test are NOT the repo root:
    # `git diff-tree -r <root>` reports no files (no parent to diff against), which
    # would make a root adoption commit look empty and pass the test for the wrong reason.
    (root / "README.md").write_text("baseline\n")
    subprocess.run(["git", "add", "README.md"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "docs: baseline"], cwd=str(root), capture_output=True, check=True)


def _commit(root: Path, files: dict[str, str], message: str) -> str:
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        subprocess.run(["git", "add", name], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=str(root), capture_output=True, check=True)
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout.strip()


class TestBootstrapExemption:
    """The bite test for bug #3: commits at/before the .aiv.yml adoption baseline are
    exempt from packet enforcement (so a fresh aiv-init repo is pushable), while
    commits after adoption are still enforced."""

    def test_bootstrap_commit_exempt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)  # check_commits runs git in CWD
        # Bootstrap: adds .aiv.yml + functional scaffolding, no packet (cannot have one yet).
        boot = _commit(tmp_path, {".aiv.yml": "{}\n", "src/scaffold.py": "x\n"}, "chore: adopt aiv")
        assert check_commits([boot]) == []  # would be a violation without the exemption

    def test_post_adoption_functional_without_packet_still_flagged(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        boot = _commit(tmp_path, {".aiv.yml": "{}\n"}, "chore: adopt aiv")
        bad = _commit(tmp_path, {"src/feature.py": "y\n"}, "feat: no packet")  # after adoption
        violations = check_commits([boot, bad])
        shas = [v[0] for v in violations]
        assert bad[:7] in shas  # enforced
        assert boot[:7] not in shas  # bootstrap still exempt

    def test_adoption_sha_none_when_no_aiv_yml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _commit(tmp_path, {"src/x.py": "x\n"}, "feat: x")  # no .aiv.yml ever
        assert _aiv_adoption_sha() is None
        # with no adoption baseline, nothing is exempt (fail-safe: scan everything)
        assert _is_pre_adoption("a" * 40, None) is False
