"""Tests for `aiv init` command — hook installation and directory scaffolding.

Closes the FAIL UNVERIFIED gap in VERIFICATION_PACKET_MAIN.md:
  Claim 1: aiv init installs a pre-push hook shim into .git/hooks/pre-push
  Claim 2: Pre-push hook catches commits that bypassed pre-commit via --no-verify
  Claim 3: Same skip/overwrite logic as pre-commit hook installation
"""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def fresh_repo(tmp_path: Path) -> Path:
    """Create a bare git repo with no hooks."""
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    return tmp_path


class TestInitCreatesDirectories:
    """aiv init scaffolds .aiv.yml, aiv-packets, and aiv-evidence dirs."""

    def test_creates_aiv_yml(self, fresh_repo: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert (fresh_repo / ".aiv.yml").exists()

    def test_creates_packets_dir(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (fresh_repo / ".github" / "aiv-packets").is_dir()

    def test_creates_evidence_dir(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (fresh_repo / ".github" / "aiv-evidence").is_dir()


class TestInitInstallsPreCommitHook:
    """aiv init installs a pre-commit hook shim."""

    def test_installs_pre_commit_hook(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        hook = fresh_repo / ".git" / "hooks" / "pre-commit"
        assert hook.exists(), "pre-commit hook was not installed"
        content = hook.read_text(encoding="utf-8")
        assert "from aiv.hooks.pre_commit import main" in content

    def test_skips_existing_aiv_hook(self, fresh_repo: Path) -> None:
        """If an AIV hook already exists, init warns and skips."""
        hooks_dir = fresh_repo / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\n# aiv hook already here\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "already contains AIV hook" in result.stdout
        # Original content preserved
        assert "# aiv hook already here" in hook.read_text(encoding="utf-8")

    def test_warns_on_non_aiv_hook(self, fresh_repo: Path) -> None:
        """If a non-AIV pre-commit hook exists, init warns but does NOT overwrite."""
        hooks_dir = fresh_repo / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\necho 'custom hook'\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "exists (non-AIV)" in result.stdout
        # Original content preserved — NOT overwritten
        assert "custom hook" in hook.read_text(encoding="utf-8")


class TestInitInstallsPostCommitHook:
    """Issue #29 bug #2: aiv init must install a post-commit hook that records
    commits into the active change (the SHA is only knowable after the commit)."""

    def test_installs_post_commit_hook(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        hook = fresh_repo / ".git" / "hooks" / "post-commit"
        assert hook.exists(), "post-commit hook was not installed"
        content = hook.read_text(encoding="utf-8")
        assert "from aiv.hooks.post_commit import main" in content


class TestInitInstallsPrePushHook:
    """Claim 1: aiv init installs a pre-push hook shim into .git/hooks/pre-push."""

    def test_installs_pre_push_hook(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        hook = fresh_repo / ".git" / "hooks" / "pre-push"
        assert hook.exists(), "pre-push hook was not installed"
        content = hook.read_text(encoding="utf-8")
        assert "from aiv.hooks.pre_push import main" in content

    def test_pre_push_hook_content_mentions_no_verify(self, fresh_repo: Path) -> None:
        """Claim 2: Pre-push hook catches commits that bypassed pre-commit via --no-verify."""
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        hook = fresh_repo / ".git" / "hooks" / "pre-push"
        content = hook.read_text(encoding="utf-8")
        assert "--no-verify" in content, "Pre-push hook shim should document --no-verify bypass"

    def test_skips_existing_aiv_push_hook(self, fresh_repo: Path) -> None:
        """Claim 3: Same skip logic as pre-commit — skips if AIV hook exists."""
        hooks_dir = fresh_repo / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        hook = hooks_dir / "pre-push"
        hook.write_text("#!/bin/sh\n# aiv push hook\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "already contains AIV hook" in result.stdout

    def test_warns_on_non_aiv_push_hook(self, fresh_repo: Path) -> None:
        """Claim 3: Same overwrite-protection as pre-commit — warns on non-AIV hook."""
        hooks_dir = fresh_repo / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        hook = hooks_dir / "pre-push"
        hook.write_text("#!/bin/sh\necho 'custom push hook'\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "exists (non-AIV)" in result.stdout
        # Original content preserved
        assert "custom push hook" in hook.read_text(encoding="utf-8")


class TestInitNoHookFlag:
    """--no-hook skips all hook installation."""

    def test_no_hook_skips_installation(self, fresh_repo: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(fresh_repo), "--no-hook"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert not (fresh_repo / ".git" / "hooks" / "pre-commit").exists()
        assert not (fresh_repo / ".git" / "hooks" / "pre-push").exists()


class TestInitNoGitDir:
    """When .git doesn't exist, hook installation is skipped gracefully."""

    def test_no_git_dir_skips_hooks(self, tmp_path: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "init", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "No .git directory" in result.stdout
        # Config and dirs still created
        assert (tmp_path / ".aiv.yml").exists()
        assert (tmp_path / ".github" / "aiv-packets").is_dir()


class TestInitIdempotent:
    """Running init twice doesn't break anything."""

    def test_double_init(self, fresh_repo: Path) -> None:
        for _ in range(2):
            result = subprocess.run(
                [sys.executable, "-m", "aiv", "init", str(fresh_repo)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
        # Hooks still valid after second run
        hook = fresh_repo / ".git" / "hooks" / "pre-commit"
        assert "from aiv.hooks.pre_commit import main" in hook.read_text(encoding="utf-8")
        push_hook = fresh_repo / ".git" / "hooks" / "pre-push"
        assert "from aiv.hooks.pre_push import main" in push_hook.read_text(encoding="utf-8")
