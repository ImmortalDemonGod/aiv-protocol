"""
aiv/hooks/pre_commit.py

Portable pre-commit hook for AIV atomic commit enforcement.
Installed by ``aiv init``. Works on all platforms (no bash/husky dependency).

Feature-complete port of the original .husky/pre-commit (285 lines of bash):
  - Safety snapshots (diff, cached diff, status, untracked files)
  - Atomic commit rules (1 functional file + 1 verification packet)
  - Packet validation via ``aiv check`` (non-strict)
  - Packet quality audit via ``aiv audit``
  - Submodule commit rules (.gitmodules + submodule path + packet)
  - Evidence taxonomy rubric printed on rejection

Rules:
  1. Dependency pair exception: package.json + package-lock.json
  2. AIV atomic unit: 1 functional file + 1 verification packet (validate packet)
  3. Packet + .gitkeep: packet directory tracking commit
  4. Submodule update: 1 submodule path + 1 packet
  5. Submodule add: .gitmodules + submodule path + 1 packet (3 files)
  6. Packet-only update (1 file)
  7. Docs-only / non-functional commits: no packet required
  8. >2 staged files without matching a rule above: reject
  9. Functional code without a verification packet: reject (print rubric)
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from aiv.lib.config import (
    _DEFAULT_FUNCTIONAL_PREFIXES,
    _DEFAULT_FUNCTIONAL_ROOT_FILES,
)
from aiv.lib.config import (
    load_hook_config as _load_hook_config,
)

PACKET_PREFIXES = (
    ".github/aiv-packets/VERIFICATION_PACKET_",
    ".github/VERIFICATION_PACKET_",
    ".github/aiv-packets/PACKET_",
)
PACKET_SUFFIX = ".md"
EVIDENCE_PREFIX = ".github/aiv-evidence/EVIDENCE_"


def _run_git(*args: str) -> str:
    """
    Execute a git command and return its standard output with surrounding whitespace removed.

    Parameters:
        *args (str): Arguments to pass to the git command (for example, 'status', '--porcelain').

    Returns:
        stdout (str): The command's standard output with leading and trailing whitespace stripped.
    """
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def _staged_files() -> list[str]:
    output = _run_git("diff", "--cached", "--name-only")
    return [f for f in output.splitlines() if f.strip()]


def _is_packet(path: str) -> bool:
    return any(path.startswith(p) for p in PACKET_PREFIXES) and path.endswith(PACKET_SUFFIX)


def _is_functional(path: str, prefixes: tuple[str, ...] | None = None, root_files: set[str] | None = None) -> bool:
    _prefixes = _DEFAULT_FUNCTIONAL_PREFIXES if prefixes is None else prefixes
    _root_files = _DEFAULT_FUNCTIONAL_ROOT_FILES if root_files is None else root_files
    if any(path.startswith(p) for p in _prefixes):
        return True
    return path in _root_files


def _is_evidence(path: str) -> bool:
    return path.startswith(EVIDENCE_PREFIX) and path.endswith(PACKET_SUFFIX)


def _is_gitkeep(path: str) -> bool:
    return path in (".github/aiv-packets/.gitkeep", ".github/aiv-evidence/.gitkeep")


def _get_submodule_paths() -> list[str]:
    """Return registered submodule paths from .gitmodules."""
    try:
        output = _run_git("config", "-f", ".gitmodules", "--get-regexp", "path")
        return [line.split()[-1] for line in output.splitlines() if line.strip()]
    except Exception:
        return []


def _is_submodule_path(path: str, submodule_paths: list[str]) -> bool:
    return any(path == sp or path.startswith(sp + "/") for sp in submodule_paths)


# ---------------------------------------------------------------------------
# Safety snapshots
# ---------------------------------------------------------------------------


def _write_safety_snapshot(repo_root: Path) -> None:
    """Capture pre-commit state for recovery (mirrors husky safety snapshot)."""
    snap_root = repo_root / ".cache" / "bb-safety-snapshots"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    snap_dir = snap_root / f"{ts}-{os.getpid()}"
    try:
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "status.txt").write_text(_run_git("status", "--porcelain=v1"), encoding="utf-8")
        (snap_dir / "diff.patch").write_text(_run_git("diff"), encoding="utf-8")
        (snap_dir / "diff_cached.patch").write_text(_run_git("diff", "--cached"), encoding="utf-8")
        untracked = _run_git("ls-files", "--others", "--exclude-standard")
        (snap_dir / "untracked_files.txt").write_text(untracked, encoding="utf-8")
        if untracked.strip():
            untracked_dir = snap_dir / "untracked_files"
            for ufile in untracked.splitlines():
                ufile = ufile.strip()
                if ufile and (repo_root / ufile).is_file():
                    dest = untracked_dir / ufile
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with contextlib.suppress(OSError):
                        shutil.copy2(repo_root / ufile, dest)
        print(f"Safety snapshot written to: {snap_dir}", file=sys.stderr)
    except Exception as exc:
        print(f"WARNING: Safety snapshot failed ({exc})", file=sys.stderr)


# ---------------------------------------------------------------------------
# Packet validation
# ---------------------------------------------------------------------------


def _validate_packet(packet_path: str) -> bool:
    """Validate a staged packet using ``aiv check`` (non-strict) and ``aiv audit``.

    Fails CLOSED: any error during validation BLOCKS the commit (returns False). A
    crashed or unavailable validator must never let an unverified packet through -
    a silent pass is an enforcement bypass. Temp artifacts are always cleaned up.
    """
    tmp_path: str | None = None
    audit_dir: str | None = None
    try:
        staged_content = _run_git("show", f":{packet_path}")
        if not staged_content:
            return True

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp.write(staged_content)
            tmp_path = tmp.name

        # --- aiv check (non-strict: warnings don't block) ---
        check_result = subprocess.run(
            [sys.executable, "-m", "aiv", "check", tmp_path, "--no-strict"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if check_result.returncode != 0:
            print()
            print("[BLOCK] PACKET VALIDATION FAILED")
            print("=" * 79)
            print("The staged verification packet failed content validation:")
            print()
            print(check_result.stdout)
            if check_result.stderr:
                print(check_result.stderr)
            print()
            print("Fix the packet errors before committing.")
            print("=" * 79)
            return False

        # --- aiv audit (catches FIX_NO_CLASS_F, TODO remnants, etc.) ---
        audit_dir = tempfile.mkdtemp(prefix="aiv-audit-check-")
        packet_basename = Path(packet_path).name
        shutil.copy2(tmp_path, Path(audit_dir) / packet_basename)

        audit_result = subprocess.run(
            [sys.executable, "-m", "aiv", "audit", audit_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if audit_result.returncode != 0:
            print()
            print("[BLOCK] PACKET AUDIT FAILED")
            print("=" * 79)
            print("The staged verification packet has quality issues:")
            print()
            print(audit_result.stdout)
            if audit_result.stderr:
                print(audit_result.stderr)
            print()
            print("Fix the audit errors before committing.")
            print("=" * 79)
            return False

        return True
    except Exception as exc:
        # FAIL CLOSED: a validation error blocks the commit, it never skips it.
        print()
        print("[BLOCK] PACKET VALIDATION ERROR")
        print("=" * 79)
        print(f"Packet validation could not complete ({exc}).")
        print("Failing closed: the commit is blocked because the packet could NOT be verified.")
        print("Fix the environment (e.g. make `aiv` importable) or the packet, then retry.")
        print("=" * 79)
        return False
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
        if audit_dir:
            shutil.rmtree(audit_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------


def _print_rubric(staged: list[str]) -> None:
    """Print the AIV evidence taxonomy rubric on rejection."""
    print()
    print("[BLOCK] AIV CUMULATIVE COMPLIANCE GATING (Shift-Left)")
    print("=" * 79)
    print("ERROR: You modified code but did not include a Verification Packet.")
    print("You must self-assess the Risk Tier and provide CUMULATIVE evidence.")
    print()
    print("STAGED FILES DETECTED:")
    for f in staged:
        print(f"  {f}")
    print()
    print("RISK CLASSIFICATION & EVIDENCE REQUIREMENTS:")
    print("-" * 79)
    print("  [R3] HIGH RISK   : Auth, Crypto, Payments, PII, Audit Logs.")
    print("                     REQUIRES: A + B + C + E + [D + F]")
    print()
    print("  [R2] MEDIUM RISK : Infrastructure, Config, Schema, Public APIs.")
    print("                     REQUIRES: [R1] + [C + E]")
    print()
    print("  [R1] LOW RISK    : Standard Logic, Features, Bug Fixes.")
    print("                     REQUIRES: [A + B]")
    print()
    print("  [R0] TRIVIAL     : Docs, comments, formatting.")
    print("                     REQUIRES: [A + B]")
    print("-" * 79)
    print()
    print("EVIDENCE TAXONOMY REFERENCE:")
    print("  [Class A] Execution    : CI run URL or local test output proving it runs.")
    print("  [Class B] Referential  : SHA-pinned GitHub permalinks to changed lines.")
    print("  [Class C] Negative     : Proof that regressions are absent (search scope + method).")
    print("  [Class D] Differential : Detailed diff of API, State, or Config changes.")
    print("  [Class E] Intent       : SHA-pinned link to the Spec/Issue/Directive.")
    print("  [Class F] Provenance   : Cryptographic hashes/signatures for chain-of-custody.")
    print()
    print("INSTRUCTION FOR AGENT:")
    print("1. Identify the Risk Tier for the staged files above.")
    print("2. Run: aiv generate <name> --tier <R0|R1|R2|R3>")
    print("3. Fill in the TODO sections in the generated packet.")
    print("4. Stage the packet: git add .github/aiv-packets/VERIFICATION_PACKET_<NAME>.md")
    print("5. Retry commit.")
    print("=" * 79)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def _is_on_protected_branch() -> bool:
    """Check if the current branch is a protected branch."""
    try:
        from aiv.lib.change import get_current_branch, is_protected_branch

        branch = get_current_branch()
        return is_protected_branch(branch)
    except Exception:
        return False


def _has_active_change() -> bool:
    """Check if there is an active change context."""
    try:
        from aiv.lib.change import load_change

        return load_change() is not None
    except Exception:
        return False


def main() -> int:
    """Run the AIV pre-commit hook. Returns 0 on success, 1 on rejection."""
    # Safety snapshot
    try:
        repo_root_str = _run_git("rev-parse", "--show-toplevel")
        if repo_root_str:
            _write_safety_snapshot(Path(repo_root_str))
    except Exception:
        pass

    staged = _staged_files()
    if not staged:
        return 0

    # Load hook config from .aiv.yml (falls back to defaults)
    func_prefixes, func_root_files = _load_hook_config()

    count = len(staged)
    packets = [f for f in staged if _is_packet(f)]
    evidence = [f for f in staged if _is_evidence(f)]
    functional = [f for f in staged if _is_functional(f, func_prefixes, func_root_files)]
    has_gitkeep = any(_is_gitkeep(f) for f in staged)

    # Submodule detection
    submodule_paths = _get_submodule_paths()
    submodule_files = [f for f in staged if _is_submodule_path(f, submodule_paths)]
    has_gitmodules = ".gitmodules" in staged

    # -----------------------------------------------------------------------
    # Two-Layer Architecture: Change-context awareness (§8 of design doc)
    # Evidence-only or packet-only commits always pass (both modes).
    # -----------------------------------------------------------------------

    all_aiv = all(_is_packet(f) or _is_evidence(f) or _is_gitkeep(f) for f in staged)
    if all_aiv:
        for p in packets:
            if not _validate_packet(p):
                return 1
        return 0

    # -----------------------------------------------------------------------
    # Legacy atomic commit rules (still active for backward compatibility).
    # These allow functional+packet pairs without needing a change context.
    # -----------------------------------------------------------------------

    # Rule 1: Dependency pair exception
    if count == 2 and set(staged) == {"package.json", "package-lock.json"}:
        return 0

    # Rule 2: AIV atomic unit (1 functional + 1 packet or evidence)
    if count == 2 and (len(packets) == 1 or len(evidence) == 1) and len(functional) == 1:
        for p in packets:
            if not _validate_packet(p):
                return 1
        return 0

    # Rule 3: Packet + .gitkeep (packet directory tracking)
    if count == 2 and len(packets) == 1 and has_gitkeep:
        if not _validate_packet(packets[0]):
            return 1
        return 0

    # Rule 4: Submodule update (1 submodule path + 1 packet)
    if count == 2 and len(packets) == 1 and len(submodule_files) == 1:
        if not _validate_packet(packets[0]):
            return 1
        return 0

    # Rule 5: Submodule add (.gitmodules + submodule path + 1 packet)
    if count == 3 and len(packets) == 1 and has_gitmodules and len(submodule_files) >= 1:
        if not _validate_packet(packets[0]):
            return 1
        return 0

    # Rule 6: Packet-only update
    if count == 1 and len(packets) == 1:
        if not _validate_packet(packets[0]):
            return 1
        return 0

    # Rule 7: Docs-only / non-functional commits (no functional files, no packets needed)
    if not functional:
        return 0

    # -----------------------------------------------------------------------
    # At this point we have functional files WITHOUT a matching packet.
    # Two-Layer Architecture: if an active change context exists, allow
    # the commit (the verification boundary is the change, not the commit).
    # -----------------------------------------------------------------------
    if _has_active_change():
        return 0

    # -----------------------------------------------------------------------
    # No active change context and no packet. On a protected branch this is
    # always blocked (direct mode requires `aiv begin` first). On a feature
    # branch, fall through to legacy rules which print the rubric.
    # -----------------------------------------------------------------------
    if _is_on_protected_branch():
        print()
        print("[BLOCK] No active change context.")
        print("=" * 79)
        print("You are committing functional files to a protected branch")
        print("without an active change context or a verification packet.")
        print()
        print("Option 1 (recommended): Use the change lifecycle:")
        print("  aiv begin <name>")
        print("  git commit ...")
        print("  aiv close")
        print()
        print("Option 2 (legacy): Pair each file with a verification packet:")
        print("  aiv commit <file> -m '<message>' ...")
        print("=" * 79)
        return 1

    # Rule 8: Too many files
    if count > 2:
        print(f"[BLOCK] REJECTION: Atomic Commit Policy Violated ({count} files staged).")
        print("This repository enforces: 1 Functional File + 1 Verification Packet per commit.")
        print()
        print("Staged files:")
        for f in staged:
            print(f"  {f}")
        print()
        print("Split your changes into atomic commits: 1 file + 1 packet each.")
        print("Or use `aiv begin <name>` to start a tracked change that allows multi-file commits.")
        return 1

    # Rule 9: Functional code without a packet
    if functional and not packets:
        _print_rubric(staged)
        return 1

    # Rule 10: Any other 2-file combination not matching above rules
    if count == 2:
        print(f"[BLOCK] REJECTION: Atomic Commit Policy Violated ({count} files staged).")
        print("Allowed 2-file commits are:")
        print("  - package.json + package-lock.json")
        print("  - 1 functional file + 1 Verification Packet")
        print()
        print("Staged files:")
        for f in staged:
            print(f"  {f}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
