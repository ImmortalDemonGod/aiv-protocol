"""
tests/unit/test_post_commit_hook.py

Issue #29 bug #2: the post-commit hook records each commit into the active change
context, so `aiv close` can package them. Without it, change.json.commits stays
empty and the recommended begin -> commit -> close lifecycle cannot close.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from aiv.hooks import post_commit
from aiv.lib.change import begin_change, load_change

if TYPE_CHECKING:
    from pathlib import Path


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, check=True)
    return r.stdout.strip()


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=True)
    _git(tmp_path, "config", "user.email", "t@t.com")
    _git(tmp_path, "config", "user.name", "T")
    (tmp_path / "README.md").write_text("x\n")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "chore: baseline")
    return tmp_path


def _commit(repo: Path, name: str, content: str, message: str) -> str:
    p = repo / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


class TestPostCommitRecords:
    def test_records_commit_into_active_change(self, git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(git_repo)
        begin_change(name="my-change", repo_root=git_repo)
        sha = _commit(git_repo, "src/aiv/foo.py", "print('x')\n", "feat: add foo")

        assert post_commit.main() == 0

        ctx = load_change(git_repo)
        assert ctx is not None
        assert [c.sha for c in ctx.commits] == [sha]
        assert ctx.commits[0].message == "feat: add foo"
        assert "src/aiv/foo.py" in ctx.commits[0].files

    def test_noop_when_no_active_change(self, git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(git_repo)
        _commit(git_repo, "src/aiv/bar.py", "print('y')\n", "feat: bar")

        assert post_commit.main() == 0
        assert load_change(git_repo) is None  # hook created nothing

    def test_idempotent(self, git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(git_repo)
        begin_change(name="c", repo_root=git_repo)
        _commit(git_repo, "src/aiv/baz.py", "z\n", "feat: baz")

        post_commit.main()
        post_commit.main()  # second run must not duplicate

        ctx = load_change(git_repo)
        assert ctx is not None
        assert len(ctx.commits) == 1

    def test_records_evidence_files(self, git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(git_repo)
        begin_change(name="c", repo_root=git_repo)
        # a commit carrying an evidence file should classify it as evidence
        (git_repo / ".github" / "aiv-evidence").mkdir(parents=True, exist_ok=True)
        (git_repo / ".github" / "aiv-evidence" / "EVIDENCE_FOO.md").write_text("e\n")
        (git_repo / "src").mkdir(exist_ok=True)
        (git_repo / "src" / "foo.py").write_text("x\n")
        _git(git_repo, "add", "src/foo.py", ".github/aiv-evidence/EVIDENCE_FOO.md")
        _git(git_repo, "commit", "-m", "feat: foo + evidence")

        assert post_commit.main() == 0
        ctx = load_change(git_repo)
        assert ctx is not None
        assert ".github/aiv-evidence/EVIDENCE_FOO.md" in ctx.commits[0].evidence
        assert "src/foo.py" not in ctx.commits[0].evidence
