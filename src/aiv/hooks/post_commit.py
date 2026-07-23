"""
aiv/hooks/post_commit.py

Post-commit hook: record the just-created commit into the active change context.

Installed by ``aiv init``. This is the counterpart the Two-Layer lifecycle was
missing (issue #29, bug #2): the pre-commit hook runs BEFORE the commit object
exists, so it cannot know the SHA to record. Git runs *post-commit* AFTER the
commit is written, with HEAD pointing at the new commit -- the first moment the
SHA is knowable. Without this hook, ``change.json``'s ``commits`` list stays
empty and ``aiv close`` fails with "has no commits."

Contract:
  - No-op when no change is active (safe to install unconditionally).
  - Idempotent: recording a SHA already present in the change is a no-op.
  - Never aborts the commit. A post-commit hook cannot un-make a commit anyway,
    and a bookkeeping failure must not masquerade as a broken commit -- any error
    is reported to stderr and the hook still exits 0.
"""

from __future__ import annotations

import subprocess
import sys

PACKET_PREFIXES = (
    ".github/aiv-packets/VERIFICATION_PACKET_",
    ".github/VERIFICATION_PACKET_",
    ".github/aiv-packets/PACKET_",
)
EVIDENCE_PREFIX = ".github/aiv-evidence/EVIDENCE_"
PACKET_SUFFIX = ".md"


def _run_git(*args: str) -> str:
    """Run a git command, returning stripped stdout ("" on any failure)."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _is_evidence_or_packet(path: str) -> bool:
    if not path.endswith(PACKET_SUFFIX):
        return False
    return path.startswith(EVIDENCE_PREFIX) or any(path.startswith(p) for p in PACKET_PREFIXES)


def _commit_files(sha: str) -> list[str]:
    out = _run_git("diff-tree", "--no-commit-id", "--name-only", "-r", sha)
    return [f for f in out.split("\n") if f]


def main() -> int:
    """Record HEAD into the active change context, if any. Always returns 0."""
    try:
        from aiv.lib.change import load_change, record_commit

        ctx = load_change()
        if ctx is None:
            return 0

        sha = _run_git("rev-parse", "HEAD")
        if not sha:
            return 0
        if any(c.sha == sha for c in ctx.commits):
            return 0  # idempotent -- already recorded

        message = _run_git("log", "-1", "--format=%s", sha)
        files = _commit_files(sha)
        evidence = [f for f in files if _is_evidence_or_packet(f)]
        record_commit(sha=sha, message=message, files=files, evidence=evidence)
    except Exception as exc:  # never fail the commit over bookkeeping
        print(f"aiv post-commit: could not record commit ({exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
