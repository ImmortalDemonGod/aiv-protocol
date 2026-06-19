"""
F96 / C2 - parity between the bash husky hook and the Python hook.

The bash `.husky/pre-commit` was a stale reimplementation of the atomic-commit
rules and disagreed with the authoritative Python hook (`aiv.hooks.pre_commit`):
it did not recognize Layer-1 `EVIDENCE_*.md` files, so the exact output of
`aiv commit` (one source file + one EVIDENCE_*.md) was accepted by the Python
hook but REJECTED by the bash hook. These tests pin parity: for the same staged
set, both hooks must reach the same decision, and the `aiv commit` shape must pass.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASH_HOOK = Path(__file__).resolve().parents[2] / ".husky" / "pre-commit"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def _make_repo(root: Path, staged: dict[str, str], active_change: bool = False) -> Path:
    repo = root / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    # Stub the husky bootstrap so the hook's `. _/husky.sh` source line is a no-op.
    (repo / ".husky" / "_").mkdir(parents=True)
    (repo / ".husky" / "_" / "husky.sh").write_text("")
    shutil.copy(BASH_HOOK, repo / ".husky" / "pre-commit")
    if active_change:
        (repo / ".aiv").mkdir()
        (repo / ".aiv" / "change.json").write_text('{"id": "x", "mode": "pr", "commits": []}')
    for rel, content in staged.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        _git(repo, "add", rel)
    return repo


def _env_with_aiv() -> dict[str, str]:
    # Ensure the hook's `python`/`python3` resolves to the interpreter that has aiv installed.
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def _run_bash_hook(repo: Path) -> int:
    r = subprocess.run(["sh", ".husky/pre-commit"], cwd=str(repo), env=_env_with_aiv(), capture_output=True, text=True)
    return r.returncode


def _run_python_hook(repo: Path) -> int:
    r = subprocess.run(
        [sys.executable, "-m", "aiv.hooks.pre_commit"],
        cwd=str(repo),
        env=_env_with_aiv(),
        capture_output=True,
        text=True,
    )
    return r.returncode


_EVIDENCE = "# EVIDENCE\n\nLayer-1 evidence file.\n"
_SOURCE = "x = 1\n"


class TestHookEvidenceParity:
    def test_source_plus_evidence_accepted_by_both(self, tmp_path: Path) -> None:
        """The exact `aiv commit` output (1 source + 1 EVIDENCE_*.md) passes BOTH hooks (goal: both exit 0)."""
        staged = {"src/x.py": _SOURCE, ".github/aiv-evidence/EVIDENCE_X.md": _EVIDENCE}
        bash = _run_bash_hook(_make_repo(tmp_path / "bash", staged))
        py = _run_python_hook(_make_repo(tmp_path / "py", staged))
        assert py == 0, "Python hook should accept source + EVIDENCE"
        assert bash == 0, "bash hook must accept source + EVIDENCE (F96 parity)"
        assert bash == py

    def test_multifile_aiv_artifacts_parity(self, tmp_path: Path) -> None:
        """A >2-file commit of only AIV artifacts (change-context) reaches the same decision in both hooks."""
        staged = {
            ".github/aiv-evidence/EVIDENCE_A.md": _EVIDENCE,
            ".github/aiv-evidence/EVIDENCE_B.md": _EVIDENCE,
            ".github/aiv-evidence/EVIDENCE_C.md": _EVIDENCE,
        }
        bash = _run_bash_hook(_make_repo(tmp_path / "bash", staged, active_change=True))
        py = _run_python_hook(_make_repo(tmp_path / "py", staged, active_change=True))
        assert bash == py, f"hooks disagree on multi-file AIV-artifact commit (bash={bash}, py={py})"

    def test_functional_without_evidence_rejected_by_both(self, tmp_path: Path) -> None:
        """Conservation: a bare functional file with no packet/evidence is still rejected by both (deny path intact)."""
        staged = {"src/x.py": _SOURCE}
        bash = _run_bash_hook(_make_repo(tmp_path / "bash", staged))
        py = _run_python_hook(_make_repo(tmp_path / "py", staged))
        assert bash != 0 and py != 0, "a functional-only commit must be blocked by both hooks"
        assert bash == py
