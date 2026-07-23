"""
tests/unit/test_change.py

Tests for the change lifecycle module (aiv begin / close / abandon / status).
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from aiv.lib.change import (
    ChangeContext,
    CommitRecord,
    abandon_change,
    begin_change,
    clear_change,
    close_change,
    load_change,
    record_commit,
    save_change,
)


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a minimal repo-like structure with .aiv/ directory."""
    aiv_dir = tmp_path / ".aiv"
    aiv_dir.mkdir()
    return tmp_path


@pytest.fixture
def active_change(tmp_repo: Path) -> ChangeContext:
    """Create and return an active change with one commit."""
    begin_change(name="test-change", description="A test change", repo_root=tmp_repo)
    record_commit(
        sha="abc1234def5678",
        message="feat: add something",
        files=["src/aiv/lib/foo.py"],
        evidence=["EVIDENCE_LIB_FOO.md"],
        repo_root=tmp_repo,
    )
    return load_change(tmp_repo)


# ---------------------------------------------------------------------------
# begin_change
# ---------------------------------------------------------------------------


class TestBeginChange:
    def test_creates_change_json(self, tmp_repo: Path) -> None:
        ctx = begin_change(name="my-feature", repo_root=tmp_repo)
        assert ctx.name == "my-feature"
        assert ctx.mode == "direct"
        assert ctx.commits == []
        assert (tmp_repo / ".aiv" / "change.json").exists()

    def test_with_description(self, tmp_repo: Path) -> None:
        ctx = begin_change(name="auth-fix", description="Fix JWT expiry", repo_root=tmp_repo)
        assert ctx.description == "Fix JWT expiry"

    def test_with_pr_mode(self, tmp_repo: Path) -> None:
        ctx = begin_change(name="payments", mode="pr", repo_root=tmp_repo)
        assert ctx.mode == "pr"

    def test_rejects_duplicate(self, tmp_repo: Path) -> None:
        begin_change(name="first", repo_root=tmp_repo)
        with pytest.raises(ValueError, match="already active"):
            begin_change(name="second", repo_root=tmp_repo)

    def test_rejects_invalid_name_uppercase(self, tmp_repo: Path) -> None:
        with pytest.raises(ValueError, match="Invalid change name"):
            begin_change(name="MyFeature", repo_root=tmp_repo)

    def test_rejects_invalid_name_spaces(self, tmp_repo: Path) -> None:
        with pytest.raises(ValueError, match="Invalid change name"):
            begin_change(name="my feature", repo_root=tmp_repo)

    def test_rejects_invalid_name_starts_with_hyphen(self, tmp_repo: Path) -> None:
        with pytest.raises(ValueError, match="Invalid change name"):
            begin_change(name="-bad", repo_root=tmp_repo)

    def test_accepts_valid_names(self, tmp_repo: Path) -> None:
        # Just test that these don't raise
        ctx = begin_change(name="a", repo_root=tmp_repo)
        assert ctx.name == "a"
        clear_change(tmp_repo)

        ctx = begin_change(name="fix-123", repo_root=tmp_repo)
        assert ctx.name == "fix-123"
        clear_change(tmp_repo)

        ctx = begin_change(name="enforcement-gap-fix", repo_root=tmp_repo)
        assert ctx.name == "enforcement-gap-fix"


# ---------------------------------------------------------------------------
# load_change / save_change
# ---------------------------------------------------------------------------


class TestLoadSave:
    def test_load_returns_none_when_no_file(self, tmp_repo: Path) -> None:
        assert load_change(tmp_repo) is None

    def test_roundtrip(self, tmp_repo: Path) -> None:
        ctx = ChangeContext(
            name="test",
            started_at="2026-02-08T19:00:00+00:00",
            mode="direct",
            commits=[
                CommitRecord(
                    sha="abc1234",
                    message="feat: something",
                    files=["src/foo.py"],
                    evidence=["EVIDENCE_FOO.md"],
                    timestamp="2026-02-08T19:05:00+00:00",
                )
            ],
            files_changed=["src/foo.py"],
            evidence_files=["EVIDENCE_FOO.md"],
        )
        save_change(ctx, tmp_repo)
        loaded = load_change(tmp_repo)
        assert loaded is not None
        assert loaded.name == "test"
        assert len(loaded.commits) == 1
        assert loaded.commits[0].sha == "abc1234"

    def test_load_handles_corrupt_json(self, tmp_repo: Path) -> None:
        path = tmp_repo / ".aiv" / "change.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not valid json{{{", encoding="utf-8")
        assert load_change(tmp_repo) is None


# ---------------------------------------------------------------------------
# record_commit
# ---------------------------------------------------------------------------


class TestRecordCommit:
    def test_appends_commit(self, tmp_repo: Path) -> None:
        begin_change(name="feature", repo_root=tmp_repo)

        updated = record_commit(
            sha="aaa1111",
            message="feat: first",
            files=["src/a.py"],
            evidence=["EVIDENCE_A.md"],
            repo_root=tmp_repo,
        )
        assert updated is not None
        assert len(updated.commits) == 1
        assert updated.commits[0].sha == "aaa1111"

        updated = record_commit(
            sha="bbb2222",
            message="feat: second",
            files=["src/b.py"],
            evidence=["EVIDENCE_B.md"],
            repo_root=tmp_repo,
        )
        assert updated is not None
        assert len(updated.commits) == 2

    def test_deduplicates_files(self, tmp_repo: Path) -> None:
        begin_change(name="feature", repo_root=tmp_repo)

        record_commit(
            sha="aaa1111",
            message="first",
            files=["src/a.py"],
            evidence=["EVIDENCE_A.md"],
            repo_root=tmp_repo,
        )
        updated = record_commit(
            sha="bbb2222",
            message="second",
            files=["src/a.py"],  # same file
            evidence=["EVIDENCE_A.md"],  # same evidence
            repo_root=tmp_repo,
        )
        assert updated is not None
        assert updated.files_changed == ["src/a.py"]  # not duplicated
        assert updated.evidence_files == ["EVIDENCE_A.md"]  # not duplicated

    def test_returns_none_when_no_active_change(self, tmp_repo: Path) -> None:
        result = record_commit(
            sha="aaa1111",
            message="orphan",
            files=["src/x.py"],
            evidence=["EVIDENCE_X.md"],
            repo_root=tmp_repo,
        )
        assert result is None


# ---------------------------------------------------------------------------
# close_change
# ---------------------------------------------------------------------------


class TestCloseChange:
    def test_returns_context(self, tmp_repo: Path, active_change: ChangeContext) -> None:
        ctx = close_change(tmp_repo)
        assert ctx.name == "test-change"
        assert len(ctx.commits) == 1

    def test_fails_when_no_change(self, tmp_repo: Path) -> None:
        with pytest.raises(ValueError, match="No active change"):
            close_change(tmp_repo)

    def test_fails_when_no_commits(self, tmp_repo: Path) -> None:
        begin_change(name="empty", repo_root=tmp_repo)
        with pytest.raises(ValueError, match="has no commits"):
            close_change(tmp_repo)


# ---------------------------------------------------------------------------
# abandon_change
# ---------------------------------------------------------------------------


class TestAbandonChange:
    def test_clears_file(self, tmp_repo: Path, active_change: ChangeContext) -> None:
        result = abandon_change(tmp_repo)
        assert result is not None
        assert result.name == "test-change"
        # File should be gone
        assert load_change(tmp_repo) is None

    def test_returns_none_when_no_change(self, tmp_repo: Path) -> None:
        result = abandon_change(tmp_repo)
        assert result is None


# ---------------------------------------------------------------------------
# clear_change
# ---------------------------------------------------------------------------


class TestClearChange:
    def test_removes_file(self, tmp_repo: Path) -> None:
        begin_change(name="temp", repo_root=tmp_repo)
        assert (tmp_repo / ".aiv" / "change.json").exists()
        clear_change(tmp_repo)
        assert not (tmp_repo / ".aiv" / "change.json").exists()

    def test_noop_when_no_file(self, tmp_repo: Path) -> None:
        # Should not raise
        clear_change(tmp_repo)


# ---------------------------------------------------------------------------
# Issue #29 bug #2: base_sha anchoring + close-time reconstruction
# ---------------------------------------------------------------------------


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=str(root), capture_output=True, check=True)
    (root / "README.md").write_text("x\n")
    subprocess.run(["git", "add", "README.md"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=str(root), capture_output=True, check=True)


def _git_commit(root: Path, name: str, content: str, message: str) -> str:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    subprocess.run(["git", "add", name], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=str(root), capture_output=True, check=True)
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout.strip()


class TestBaseShaAnchoring:
    def test_begin_records_head_as_base_sha(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(tmp_path), capture_output=True, text=True, check=True
        ).stdout.strip()
        ctx = begin_change(name="feat-x", repo_root=tmp_path)
        assert ctx.base_sha == head

    def test_base_sha_empty_in_commitless_repo(self, tmp_repo: Path) -> None:
        # tmp_repo has no git repo -> get_head_sha returns "" -> base_sha ""
        ctx = begin_change(name="x", repo_root=tmp_repo)
        assert ctx.base_sha == ""


class TestCloseReconstructsFromHistory:
    """The bite test for bug #2: with no post-commit hook recording commits,
    `aiv close` must still reconstruct them from git history."""

    def test_close_reconstructs_when_commits_empty(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        begin_change(name="feat-x", repo_root=tmp_path)
        sha = _git_commit(tmp_path, "src/a.py", "a\n", "feat: a")

        # Nothing recorded the commit (no post-commit hook) -> commits is empty.
        assert load_change(tmp_path).commits == []

        ctx = close_change(repo_root=tmp_path)
        assert [c.sha for c in ctx.commits] == [sha]
        assert "src/a.py" in ctx.files_changed

    def test_close_reconstructs_multiple_in_order(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        begin_change(name="feat-x", repo_root=tmp_path)
        s1 = _git_commit(tmp_path, "src/a.py", "a\n", "feat: a")
        s2 = _git_commit(tmp_path, "src/b.py", "b\n", "feat: b")

        ctx = close_change(repo_root=tmp_path)
        assert [c.sha for c in ctx.commits] == [s1, s2]  # oldest-first

    def test_close_still_raises_when_no_new_commits(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        begin_change(name="feat-x", repo_root=tmp_path)
        # no commits after begin -> genuinely empty -> must still raise
        with pytest.raises(ValueError, match="no commits"):
            close_change(repo_root=tmp_path)
