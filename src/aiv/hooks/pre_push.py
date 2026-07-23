"""
aiv/hooks/pre_push.py

Pre-push hook for AIV protocol enforcement.
Installed by ``aiv init``. Works on all platforms.

This hook closes the ``--no-verify`` gap:

- ``git commit --no-verify`` bypasses the pre-commit hook.
- But ``git push`` still runs this pre-push hook.
- This hook scans every commit about to be pushed and blocks the push
  if any commit has functional files without a verification packet.

To bypass THIS hook, someone would need ``git push --no-verify``,
which is a separate, deliberate action. The CI protocol-audit job
(layer 3) catches even that.

Defence-in-depth:
  1. pre-commit hook  — blocks at commit time
  2. pre-push hook    — catches --no-verify commits before they leave
  3. CI protocol-audit — catches --no-verify push (server-side)
  4. Branch protection — require PRs (GitHub settings)
"""

from __future__ import annotations

import subprocess
import sys

from aiv.lib.config import (
    _DEFAULT_FUNCTIONAL_PREFIXES,
    _DEFAULT_FUNCTIONAL_ROOT_FILES,
    load_hook_config,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PACKET_PREFIXES = (
    ".github/aiv-packets/VERIFICATION_PACKET_",
    ".github/VERIFICATION_PACKET_",
    ".github/aiv-packets/PACKET_",
)
PACKET_SUFFIX = ".md"
EVIDENCE_PREFIX = ".github/aiv-evidence/EVIDENCE_"


def _is_packet(path: str) -> bool:
    """
    Check whether a file path refers to a verification packet.

    Returns:
        `True` if the path starts with a defined packet prefix and ends with the packet suffix, `False` otherwise.
    """
    return any(path.startswith(p) for p in PACKET_PREFIXES) and path.endswith(PACKET_SUFFIX)


def _is_functional(
    path: str,
    prefixes: tuple[str, ...] | None = None,
    root_files: set[str] | None = None,
) -> bool:
    """
    Determine whether a file path should be treated as a functional file for AIV checks.

    Parameters:
        path (str): File path to evaluate.
        prefixes (tuple[str, ...] | None): Optional sequence of functional path prefixes to match against;
            when `None`, the configured default functional prefixes are used.
        root_files (set[str] | None): Optional set of root file paths considered functional;
            when `None`, the configured default functional root files are used.

    Returns:
        bool: `True` if the path starts with any functional prefix or is
            present in the functional root files, `False` otherwise.
    """
    _prefixes = _DEFAULT_FUNCTIONAL_PREFIXES if prefixes is None else prefixes
    _root_files = _DEFAULT_FUNCTIONAL_ROOT_FILES if root_files is None else root_files
    if any(path.startswith(p) for p in _prefixes):
        return True
    return path in _root_files


def _get_commits_in_range(local_sha: str, remote_sha: str) -> list[str]:
    """
    Determine the list of commit SHAs introduced by a push range.

    When local_sha is the all-zero SHA (branch deletion) this returns an empty list.
    When remote_sha is the all-zero SHA (new branch) this returns commits reachable from
    local_sha that are not present on any remote. Otherwise this returns commits in the
    range `remote_sha..local_sha`. On git failures, timeouts, or if there are no commits,
    an empty list is returned.

    Parameters:
        local_sha (str): The local commit SHA at the tip of the pushed ref.
        remote_sha (str): The remote commit SHA that the ref pointed to before the push.

    Returns:
        list[str]: A list of full commit SHAs in the push range, or an empty list if none
        are found or on error.
    """
    # Zero SHA means new branch or deleted branch
    zero = "0" * 40
    if local_sha == zero:
        # Branch deletion — nothing to check
        return []
    if remote_sha == zero:
        # New branch — check all commits not on any remote branch
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    local_sha,
                    "--not",
                    "--remotes",
                    "--format=%H",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return [s for s in result.stdout.strip().split("\n") if s]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    # Normal push — commits between remote and local
    try:
        result = subprocess.run(
            ["git", "log", f"{remote_sha}..{local_sha}", "--format=%H"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return [s for s in result.stdout.strip().split("\n") if s]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def _get_commit_files(sha: str) -> list[str]:
    """Return list of files changed in a single commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split("\n") if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def _is_evidence(path: str) -> bool:
    return path.startswith(EVIDENCE_PREFIX) and path.endswith(PACKET_SUFFIX)


def _aiv_adoption_sha() -> str | None:
    """SHA of the commit that first added ``.aiv.yml`` — the AIV enforcement baseline.

    Commits at or before this predate AIV adoption (the repo's bootstrap: installing
    aiv, adding config, the scaffolding commits) and cannot be expected to carry
    verification packets. Enforcing packets on them makes a fresh ``aiv init`` repo
    permanently unpushable (issue #29, bug #3). Returns None if ``.aiv.yml`` is not
    in history, in which case no exemption applies (fail-safe: scan everything).
    """
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "--", ".aiv.yml"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        shas = [s for s in result.stdout.strip().split("\n") if s]
        # git log is newest-first; the LAST line is the earliest add of .aiv.yml.
        return shas[-1] if shas else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _is_pre_adoption(sha: str, adoption_sha: str | None) -> bool:
    """True if ``sha`` is the adoption commit or an ancestor of it (i.e. at/before
    AIV was adopted in this repo). Such commits are exempt from packet enforcement."""
    if not adoption_sha:
        return False
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, adoption_sha],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_commits(commits: list[str]) -> list[tuple[str, list[str]]]:
    """
    Identify commits that modify functional files but lack verification packet or evidence coverage.

    For each provided commit SHA, determines whether the commit contains functional files and,
    if so, whether those files are covered by a verification packet or evidence file in the
    same commit or elsewhere in the push range. Commits that contain functional files with
    no such coverage are reported as violations.

    Parameters:
        commits (list[str]): Commit SHAs comprising the push range to validate.

    Returns:
        list[tuple[str, list[str]]]: Tuples of (short_sha, functional_files) for violating commits.
            `short_sha` is the first 7 characters of the commit SHA; `functional_files` is the list
            of functional file paths present in that commit.
    """
    # Load config from .aiv.yml (consistent with pre-commit hook and CI auditor)
    func_prefixes, func_root_files = load_hook_config()

    # Commits at/before AIV adoption (the .aiv.yml bootstrap) are exempt — they could
    # not have carried packets (issue #29, bug #3). Resolve the baseline once.
    adoption_sha = _aiv_adoption_sha()

    violations: list[tuple[str, list[str]]] = []

    # Cache files per commit (single query each).
    files_by_sha: dict[str, list[str]] = {}
    for sha in commits:
        files_by_sha[sha] = _get_commit_files(sha)

    # Scan the entire push range for Layer 2 packets and evidence files.
    # If present, functional-only commits are covered by the aggregate.
    range_has_evidence = any(_is_packet(f) or _is_evidence(f) for files in files_by_sha.values() for f in files)

    for sha in commits:
        # Pre-adoption / bootstrap commits are not subject to packet enforcement.
        if _is_pre_adoption(sha, adoption_sha):
            continue
        files = files_by_sha[sha]
        functional = [f for f in files if _is_functional(f, func_prefixes, func_root_files)]
        packets = [f for f in files if _is_packet(f)]
        evidence = [f for f in files if _is_evidence(f)]

        if not functional:
            continue

        # Covered by same-commit packet or evidence → OK
        if packets or evidence:
            continue

        # Covered by a Layer 2 packet elsewhere in the push range → OK
        if range_has_evidence:
            continue

        # No coverage at all → violation
        violations.append((sha[:7], functional))

    return violations


def _check_unclosed_change() -> tuple[bool, str, int]:
    """Check if there's an unclosed change context.

    Returns (has_unclosed, change_name, commit_count).
    """
    try:
        from aiv.lib.change import load_change

        ctx = load_change()
        if ctx is not None and ctx.commits:
            return True, ctx.name, len(ctx.commits)
    except Exception:
        pass
    return False, "", 0


def _is_on_protected_branch() -> bool:
    """Check if the current branch is a protected branch."""
    try:
        from aiv.lib.change import get_current_branch, is_protected_branch

        branch = get_current_branch()
        return is_protected_branch(branch)
    except Exception:
        return False


def main() -> int:
    """Run the AIV pre-push hook.

    Reads push info from stdin (git provides this):
        <local_ref> <local_sha> <remote_ref> <remote_sha>

    Returns 0 to allow push, 1 to block.
    """
    # -----------------------------------------------------------------------
    # Two-Layer Architecture: Unclosed change detection (§8.2 of design doc)
    # -----------------------------------------------------------------------
    if _is_on_protected_branch():
        has_unclosed, change_name, commit_count = _check_unclosed_change()
        if has_unclosed:
            print()
            print("=" * 79)
            print("[BLOCK] AIV Pre-Push Hook: Unclosed Change Detected")
            print("=" * 79)
            print()
            print(f"Open change '{change_name}' has {commit_count} commit(s)")
            print("without a verification packet.")
            print()
            print("Run `aiv close` to generate the verification packet, or")
            print("`aiv abandon` to discard the change context.")
            print("=" * 79)
            return 1

    # -----------------------------------------------------------------------
    # Legacy: per-commit violation scanning
    # -----------------------------------------------------------------------
    violations: list[tuple[str, list[str]]] = []

    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) < 4:
            continue

        local_sha = parts[1]
        remote_sha = parts[3]

        commits = _get_commits_in_range(local_sha, remote_sha)
        violations.extend(check_commits(commits))

    if not violations:
        return 0

    # Block the push
    print()
    print("=" * 79)
    print("[BLOCK] AIV Pre-Push Hook: Protocol Violation Detected")
    print("=" * 79)
    print()
    print("WHAT HAPPENED:")
    print(f"  {len(violations)} commit(s) touch functional files but carry no verification packet.")
    print("  Likely causes (in order of probability):")
    print("    - a commit bypassed the pre-commit hook (e.g. `git commit --no-verify`);")
    print("    - functional work was committed before a packet was written for it;")
    print("    - the interpreter running the hook could not import `aiv` (see `aiv init`).")
    print("  (Commits at or before the `.aiv.yml` adoption baseline are already exempt,")
    print("   so a first-run bootstrap should not reach this message.)")
    print()
    print("WHY THIS IS BLOCKED:")
    print("  Every functional file change MUST have a paired verification packet, and this")
    print("  pre-push hook catches an uncovered commit before it reaches the remote.")
    print()

    print("VIOLATING COMMITS:")
    for short_sha, func_files in violations:
        print(f"  {short_sha}:")
        for f in func_files[:5]:
            print(f"    - {f}")
        if len(func_files) > 5:
            print(f"    ... and {len(func_files) - 5} more")
    print()

    print("HOW TO FIX:")
    print(f"  1. git reset --soft HEAD~{len(violations)}")
    print("  2. git reset HEAD -- .")
    print("  3. For EACH functional file, run:")
    print("       aiv commit <file> -m '<message>' -t R1 -c '<claim>' \\")
    print("         -i '<intent-url>' --requirement '<req>' \\")
    print("         -r '<rationale>' -s '<summary>'")
    print("  4. git push")
    print()
    print("DO NOT use `--no-verify` on git commit or git push.")
    print("DO NOT hand-write verification packets. Use `aiv commit`.")
    print("=" * 79)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
