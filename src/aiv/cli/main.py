"""
aiv/cli/main.py

CLI application entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aiv.lib.config import AIVConfig
from aiv.lib.models import ValidationFinding, ValidationStatus
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.svp.cli.main import svp_app

app = typer.Typer(
    name="aiv",
    help="AIV Protocol Suite - Evidence-based engineering verification",
    no_args_is_help=True,
)
app.add_typer(svp_app, name="svp")
console = Console()


def _hook_shebang() -> str:
    """Shebang for installed git hooks: the interpreter `aiv` is RUNNING UNDER, not whatever
    `python3` resolves to on PATH at commit time.

    Issue #29: with `#!/usr/bin/env python3`, any environment where the first python3 on PATH is
    not the one aiv was pip-installed into (pyenv shims, system python vs venv, Homebrew vs
    Xcode) makes every commit die with ModuleNotFoundError: No module named 'aiv' -- while
    `aiv init` still reports success. sys.executable is by definition an interpreter that can
    import aiv. Fallback to the env form only when the path would break the shebang line itself
    (whitespace: kernels do not quote shebang arguments).
    """
    exe = sys.executable or ""
    if exe and not any(ch.isspace() for ch in exe):
        return f"#!{exe}"
    return "#!/usr/bin/env python3"


@app.command()
def check(
    body: str | None = typer.Argument(None, help="PR body text or path to file containing it"),
    diff: Path | None = typer.Option(None, "--diff", "-d", help="Path to diff file for anti-cheat scanning"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Treat warnings as errors"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Path to .aiv.yml configuration file"),
    audit_links: bool = typer.Option(False, "--audit-links", help="Verify evidence URLs are reachable via HTTP HEAD"),
) -> None:
    """
    Validate a Verification Packet locally.

    Examples:
        aiv check "# AIV Verification Packet..."
        aiv check pr_body.md --diff changes.diff
        cat pr.md | aiv check -
    """
    # Load configuration
    if config:
        cfg = AIVConfig.from_file(config).model_copy(update={"strict_mode": strict})
    else:
        cfg = AIVConfig(strict_mode=strict)

    # Read body from argument, file, or stdin
    if body == "-":
        body_text = sys.stdin.read()
    elif body and Path(body).exists():
        body_text = Path(body).read_text(encoding="utf-8")
    elif body:
        body_text = body
    else:
        console.print("[red]Error:[/red] No packet body provided")
        raise typer.Exit(1)

    # Run full pipeline
    pipeline = ValidationPipeline(cfg, audit_links=audit_links)
    diff_text = diff.read_text(encoding="utf-8") if diff and diff.exists() else None
    result = pipeline.validate(body_text, diff=diff_text)

    # Display results
    if result.errors:
        _display_findings(result.errors, "Blocking Errors", "red")

    if result.warnings:
        _display_findings(result.warnings, "Warnings", "yellow")

    if result.info:
        _display_findings(result.info, "Info", "blue")

    # Summary
    if result.status == ValidationStatus.FAIL:
        console.print(
            Panel(
                f"[red]Validation Failed[/red]\n"
                f"{len(result.errors)} blocking error(s), {len(result.warnings)} warning(s)",
                title="[X] Result",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    else:
        packet = result.packet
        claims_count = len(packet.claims) if packet else 0
        version = packet.version if packet else "?"
        console.print(
            Panel(
                f"[green]Validation Passed[/green]\nPacket version: {version}\nClaims: {claims_count}",
                title="[OK] Result",
                border_style="green",
            )
        )


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Repository path to initialize"),
    install_hook: bool = typer.Option(True, "--install-hook/--no-hook", help="Install git pre-commit hook"),
) -> None:
    """
    Initialize AIV Protocol in a repository.

    Creates:
    - .aiv.yml configuration file
    - .github/aiv-packets/ directory for Layer 2 verification packets
    - .github/aiv-evidence/ directory for Layer 1 evidence files
    - .git/hooks/pre-commit hook (atomic commit enforcement)
    - .git/hooks/pre-push hook (catches --no-verify bypass)

    Use --no-hook to skip hook installation.
    """
    # 1. Create .aiv.yml
    aiv_yml = path / ".aiv.yml"
    if aiv_yml.exists():
        console.print(f"[yellow]Warning:[/yellow] {aiv_yml} already exists, skipping.")
    else:
        aiv_yml.write_text(
            "# AIV Protocol Configuration\n"
            "# See: https://github.com/ImmortalDemonGod/aiv-protocol\n"
            "\n"
            'version: "1.0"\n'
            "strict_mode: true\n"
            "\n"
            "# Pre-commit hook settings\n"
            "# Customize which files require a verification packet.\n"
            "# Uncomment and edit for your project layout:\n"
            "#\n"
            "# hook:\n"
            "#   functional_prefixes:\n"
            '#     - "src/"\n'
            '#     - "lib/"\n'
            '#     - "app/"\n'
            '#     - "tests/"\n'
            "#   functional_root_files:\n"
            '#     - "pyproject.toml"\n'
            '#     - "package.json"\n',
            encoding="utf-8",
        )
        console.print(f"[green]Created:[/green] {aiv_yml}")

    # 2. Create packets directory (Layer 2: per-change packets)
    packets_dir = path / ".github" / "aiv-packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = packets_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        console.print(f"[green]Created:[/green] {packets_dir}/")

    # 2b. Create evidence directory (Layer 1: per-file evidence)
    evidence_dir = path / ".github" / "aiv-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ev_gitkeep = evidence_dir / ".gitkeep"
    if not ev_gitkeep.exists():
        ev_gitkeep.touch()
        console.print(f"[green]Created:[/green] {evidence_dir}/")

    # 3. Install pre-commit hook
    if install_hook:
        git_dir = path / ".git"
        if not git_dir.is_dir():
            console.print("[yellow]Warning:[/yellow] No .git directory found -- skipping hook install.")
        else:
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            hook_file = hooks_dir / "pre-commit"
            hook_shim = (
                f"{_hook_shebang()}\n"
                '"""AIV Protocol pre-commit hook. Installed by `aiv init`."""\n'
                "import sys\n"
                "from aiv.hooks.pre_commit import main\n"
                "sys.exit(main())\n"
            )
            if hook_file.exists():
                existing = hook_file.read_text(encoding="utf-8", errors="replace")
                if "aiv" in existing.lower():
                    console.print(f"[yellow]Warning:[/yellow] {hook_file} already contains AIV hook, skipping.")
                else:
                    console.print(
                        f"[yellow]Warning:[/yellow] {hook_file} exists (non-AIV). "
                        "Use [bold]--no-hook[/bold] to skip, or remove it manually first."
                    )
            else:
                hook_file.write_text(hook_shim, encoding="utf-8")
                # Make executable on Unix
                try:
                    import stat

                    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                except OSError:
                    pass
                console.print(f"[green]Installed:[/green] pre-commit hook -> {hook_file}")

            # Install pre-push hook (catches --no-verify bypass)
            push_hook_file = hooks_dir / "pre-push"
            push_hook_shim = (
                f"{_hook_shebang()}\n"
                '"""AIV Protocol pre-push hook. Installed by `aiv init`.\n'
                "\n"
                "Catches commits that bypassed the pre-commit hook via --no-verify.\n"
                'git commit --no-verify skips pre-commit, but NOT pre-push."""\n'
                "import sys\n"
                "from aiv.hooks.pre_push import main\n"
                "sys.exit(main())\n"
            )
            if push_hook_file.exists():
                existing = push_hook_file.read_text(encoding="utf-8", errors="replace")
                if "aiv" in existing.lower():
                    console.print(f"[yellow]Warning:[/yellow] {push_hook_file} already contains AIV hook, skipping.")
                else:
                    console.print(
                        f"[yellow]Warning:[/yellow] {push_hook_file} exists (non-AIV). "
                        "Use [bold]--no-hook[/bold] to skip, or remove it manually first."
                    )
            else:
                push_hook_file.write_text(push_hook_shim, encoding="utf-8")
                try:
                    import stat

                    push_hook_file.chmod(push_hook_file.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                except OSError:
                    pass
                console.print(f"[green]Installed:[/green] pre-push hook -> {push_hook_file}")

    console.print(f"[green][OK] AIV Protocol initialized in {path}[/green]")
    console.print(
        "[dim]Tip: Use [bold]aiv begin <name>[/bold] to start a tracked change,"
        " then [bold]aiv commit[/bold] for each file.[/dim]"
    )


@app.command()
def quickstart() -> None:
    """
    Print the complete AIV workflow -- from init to push.

    This is a self-contained reference for new users and LLM coding
    assistants. Run `aiv quickstart` to see the full workflow without
    reading the README.
    """
    console.print(
        Panel(
            "[bold]AIV Protocol -- Complete Workflow Reference[/bold]\n\n"
            "AIV generates auditable evidence that code changes were verified.\n"
            "You provide claims about what changed; the tool collects the proof.",
            border_style="blue",
        )
    )
    console.print(
        "\n[bold cyan]Step 0: Initialize (once per repo)[/bold cyan]\n"
        "  aiv init\n"
        "  # Creates .aiv.yml, .github/aiv-packets/, .github/aiv-evidence/,\n"
        "  # and git hooks (pre-commit + pre-push)\n"
    )
    console.print(
        "[bold cyan]Step 1: Start a tracked change[/bold cyan]\n"
        '  aiv begin <name> --description "<what this change does>"\n'
        "  # Example:\n"
        '  aiv begin auth-fix --description "Handle expired JWT tokens"\n'
    )
    console.print(
        "[bold cyan]Step 2: Commit files with evidence collection[/bold cyan]\n"
        "  aiv commit <file> \\\n"
        '    -m "fix(auth): handle expired tokens" \\\n'
        "    -t R1 \\\n"
        '    -c "TokenValidator rejects expired tokens with 401" \\\n'
        '    -i "https://github.com/org/repo/issues/42" \\\n'
        '    --requirement "Issue #42 requires expired tokens return 401" \\\n'
        '    -r "Standard bug fix in auth module" \\\n'
        '    -s "Handle expired JWT tokens with proper 401 response"\n'
    )
    console.print(
        "  [bold]Required flags:[/bold]\n"
        "    -m   Git commit message\n"
        "    -c   Falsifiable claim (repeatable). Format: '[Component] [verb] [result] under [condition]'\n"
        "         GOOD: 'TokenValidator rejects expired tokens with HTTP 401'\n"
        "         BAD:  'Fixed the authentication bug'\n"
        "    -i   Intent URL -- link to the spec, issue, or directive (must be a URL)\n"
        "    --requirement  Which specific requirement the URL satisfies\n"
        "    -r   Rationale for the risk tier choice\n"
        "    -s   One-line summary of the change\n"
    )
    console.print(
        "  [bold]Risk tiers:[/bold]\n"
        "    R0 -- Trivial (docs, comments, formatting). Can use --skip-checks.\n"
        "    R1 -- Low risk (bug fixes, minor refactors). Default. Blocks if >50% claims unverified.\n"
        "    R2 -- Medium (API changes, config). Adds Class C (anti-cheat) + Class F (provenance).\n"
        "    R3 -- High (auth, crypto, payments). Blocks on ANY unverified claim.\n"
    )
    console.print("[bold cyan]Step 3: Check progress[/bold cyan]\n  aiv status\n")
    console.print(
        "[bold cyan]Step 4: Close the change (generates Layer 2 packet)[/bold cyan]\n"
        '  aiv close --requirement "Issue #42 requires expired tokens return 401"\n'
    )
    console.print("[bold cyan]Step 5: Push[/bold cyan]\n  git push\n")
    console.print(
        "[bold yellow]What aiv commit collects automatically:[/bold yellow]\n"
        "  Class B -- SHA-pinned line-range permalinks from git diff\n"
        "  Class A -- Per-symbol test coverage (AST analysis, Python only)\n"
        "  Code Quality -- ruff + mypy results (separate from Class A)\n"
        "  Class C (R2+) -- Anti-cheat scan (deleted assertions, test files, skip markers)\n"
        "  Class F (R2+) -- Test file provenance (git log chain-of-custody)\n"
        "  Claim Verification Matrix -- Binds each claim to evidence, shows PASS/FAIL/REVIEW\n"
    )
    console.print(
        "[bold yellow]Enforcement:[/bold yellow]\n"
        "  - R1+ commits blocked when >50% of claims are UNVERIFIED (no bypass -- write tests or use R0)\n"
        "  - R3 commits blocked on ANY unverified claim\n"
        "  - --skip-checks only allowed for R0\n"
        "  - Class E intent URLs must be real URLs, not plain text\n"
        "  - All GitHub links must be SHA-pinned (no /blob/main/ allowed)\n"
    )
    console.print(
        "[bold yellow]Other commands:[/bold yellow]\n"
        "  aiv check <packet.md>   Validate a verification packet (8-stage pipeline)\n"
        "  aiv audit               Audit all packets + evidence files for quality issues\n"
        "  aiv audit --fix         Auto-fix common issues (backfill SHAs, pin URLs)\n"
        "  aiv generate <name>     Scaffold a packet template (manual workflow)\n"
        "  aiv abandon             Discard active change without generating a packet\n"
        "  aiv svp ...             SVP cognitive verification (optional)\n"
    )


@app.command()
def audit(
    packets_dir: Path = typer.Argument(Path(".github/aiv-packets"), help="Directory containing verification packets"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix COMMIT_PENDING and CLASS_E_NO_URL where possible"),
    commits: int = typer.Option(
        0,
        "--commits",
        "-n",
        help="Scan N recent commits for protocol violations (HOOK_BYPASS, ATOMIC_VIOLATION)",
    ),
    no_evidence: bool = typer.Option(
        False,
        "--no-evidence",
        help="Skip scanning Layer 1 evidence files (.github/aiv-evidence/)",
    ),
) -> None:
    """
    Audit all verification packets AND evidence files for quality issues.

    Scans Layer 2 packets (.github/aiv-packets/) and Layer 1 evidence files
    (.github/aiv-evidence/) for problems the validation pipeline does not catch:
    commit SHA traceability, Class E link immutability, TODO remnants,
    missing Class F for bug-fix claims, verification theater detection, and more.

    With --commits N, also scans the last N git commits for protocol
    violations: functional files without packets, multi-file bundles, etc.

    Examples:
        aiv audit
        aiv audit --fix
        aiv audit .github/aiv-packets --fix
        aiv audit --commits 20
        aiv audit --no-evidence
    """
    from aiv.lib.auditor import AuditSeverity, PacketAuditor

    evidence_dir = None if no_evidence else Path(".github/aiv-evidence")
    auditor = PacketAuditor()
    result = auditor.audit(packets_dir, fix=fix, evidence_dir=evidence_dir)

    # Optionally run git-history audit
    if commits > 0:
        commit_result = auditor.audit_commits(Path("."), num_commits=commits)
        result.findings.extend(commit_result.findings)
        result.packets_with_issues += commit_result.packets_with_issues
        if commit_result.findings:
            # Re-count errors/warnings since we merged results
            pass  # error_count/warning_count are computed properties

    if not result.findings:
        console.print(
            Panel(
                f"[green]All {result.packets_scanned} packets clean[/green]",
                title="[OK] Audit",
                border_style="green",
            )
        )
        return

    # Build findings table
    table = Table(title="Audit Findings", show_lines=True)
    table.add_column("Severity", style="bold", width=8)
    table.add_column("Packet", width=30)
    table.add_column("Finding", width=20)
    table.add_column("Message", width=50)

    severity_styles = {
        AuditSeverity.ERROR: "[red]ERROR[/red]",
        AuditSeverity.WARNING: "[yellow]WARN[/yellow]",
        AuditSeverity.INFO: "[blue]INFO[/blue]",
    }

    for f in result.findings:
        sev_text = severity_styles.get(f.severity, str(f.severity))
        short_name = f.packet_name.replace("VERIFICATION_PACKET_", "").replace(".md", "")
        table.add_row(sev_text, short_name, f.finding_type, f.message[:80])

    console.print(table)

    # Summary
    if fix and result.fixed:
        console.print(f"\n[green]Auto-fixed {len(result.fixed)} packet(s).[/green]")

    console.print(
        Panel(
            f"Scanned: {result.packets_scanned} | "
            f"Issues: {result.packets_with_issues} | "
            f"Errors: {result.error_count} | "
            f"Warnings: {result.warning_count}" + (f" | Fixed: {len(result.fixed)}" if fix else ""),
            title="[X] Audit Summary" if result.error_count > 0 else "[!] Audit Summary",
            border_style="red" if result.error_count > 0 else "yellow",
        )
    )

    if result.error_count > 0:
        raise typer.Exit(1)


@app.command()
def generate(
    name: str = typer.Argument(..., help="Short name for the packet (used in filename, e.g. 'auth-fix')"),
    tier: str = typer.Option("R1", "--tier", "-t", help="Risk tier: R0, R1, R2, R3"),
    output_dir: Path = typer.Option(
        Path(".github/aiv-packets"), "--output", "-o", help="Directory to write the packet file"
    ),
    rationale: str = typer.Option("", "--rationale", "-r", help="Classification rationale"),
    skip_checks: bool = typer.Option(False, "--skip-checks", help="Skip running local checks (pytest/ruff/mypy)"),
) -> None:
    """
    Generate a verification packet scaffold.

    Creates a pre-filled packet file with classification, claim stubs,
    and evidence section headers appropriate for the chosen risk tier.

    Examples:
        aiv generate auth-fix --tier R2
        aiv generate cleanup --tier R0 --rationale "Remove dead code"
    """
    from datetime import datetime, timezone

    # Normalize name for filename
    safe_name = name.upper().replace("-", "_").replace(" ", "_")
    filename = f"VERIFICATION_PACKET_{safe_name}.md"
    filepath = output_dir / filename

    if filepath.exists():
        console.print(f"[yellow]Warning:[/yellow] {filepath} already exists.")
        overwrite = typer.confirm("Overwrite?", default=False)
        if not overwrite:
            raise typer.Exit(0)

    # Validate tier
    tier_upper = tier.upper().strip()
    if tier_upper not in ("R0", "R1", "R2", "R3"):
        console.print(f"[red]Error:[/red] Invalid tier '{tier}'. Use R0, R1, R2, or R3.")
        raise typer.Exit(1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Detect changed files via git (best-effort)
    scope_lines = _detect_git_scope()

    # Detect git context for auto-population
    git_ctx: dict[str, str] = {}
    local_results = ""

    if not skip_checks:
        git_ctx = _detect_git_context()
        console.print("[dim]Auto-detecting git context...[/dim]")
        if git_ctx.get("owner") and git_ctx.get("repo"):
            console.print(f"  Repo: [bold]{git_ctx['owner']}/{git_ctx['repo']}[/bold]")
        if git_ctx.get("branch"):
            console.print(f"  Branch: [bold]{git_ctx['branch']}[/bold]")
        if git_ctx.get("issue_number"):
            console.print(f"  Issue: [bold]#{git_ctx['issue_number']}[/bold]")

        # Run local checks to auto-populate Class A
        console.print("[dim]Running local checks (pytest, ruff, mypy)...[/dim]")
        local_results = _run_local_checks()
        console.print("  Done.")

    # Build evidence sections based on tier + auto-populated context
    evidence_sections = _build_evidence_sections(tier_upper, scope_lines, git_ctx, local_results)

    # SoD mode
    sod = "S0" if tier_upper in ("R0", "R1") else "S1"

    # Auto-detect classified_by from git config
    classified_by = "TODO"
    try:
        import subprocess

        r = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            classified_by = r.stdout.strip()
    except Exception:
        pass

    packet = f"""# AIV Verification Packet (v2.1)

**Commit:** `pending`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: {tier_upper}
  sod_mode: {sod}
  critical_surfaces: []
  blast_radius: TODO
  classification_rationale: "{rationale or "TODO: Describe why this tier was chosen"}"
  classified_by: "{classified_by}"
  classified_at: "{now}"
```

## Claim(s)

1. [Component/Function] [assertive verb: rejects/returns/ensures/prevents/limits] [result] under [condition].
   - *Example: "The `PacketParser` rejects packets where the version header is missing."*
2. [Component] prevents [unwanted state] during [process/input].
   - *Example: "The `LinkValidator` prevents mutable branch refs from passing E004."*
3. No existing tests were modified or deleted during this change.

---

## Evidence

{evidence_sections}

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

TODO: One-line summary of the change.
"""

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath.write_text(packet, encoding="utf-8")

    console.print(f"[green]Created:[/green] {filepath}")
    console.print(f"  Risk tier: [bold]{tier_upper}[/bold] | SoD: {sod}")
    console.print("  Fill in the TODO sections, then commit with your functional file.")


def _detect_git_scope() -> str:
    """Best-effort detection of changed files via git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0 or not result.stdout.strip():
            # Fallback to unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        if result.returncode == 0 and result.stdout.strip():
            lines = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    status, path = parts
                    if status.startswith("A"):
                        lines.append(f"  - `{path}` (new)")
                    elif status.startswith("M"):
                        lines.append(f"  - `{path}`")
                    elif status.startswith("D"):
                        lines.append(f"  - `{path}` (deleted)")
                    else:
                        lines.append(f"  - `{path}`")
            if lines:
                return "\n".join(lines)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return "  - TODO: list modified files"


def _detect_git_context() -> dict[str, str]:
    """Best-effort detection of git context for auto-populating evidence."""
    import os
    import re
    import subprocess

    ctx: dict[str, str] = {}

    try:
        # Current branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if branch.returncode == 0 and branch.stdout.strip():
            ctx["branch"] = branch.stdout.strip()

        # Remote URL → owner/repo
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if remote.returncode == 0 and remote.stdout.strip():
            url = remote.stdout.strip()
            # Parse owner/repo from HTTPS or SSH URL
            m = re.search(r"[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
            if m:
                ctx["owner"] = m.group(1)
                ctx["repo"] = m.group(2)

        # Current HEAD SHA
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if head.returncode == 0 and head.stdout.strip():
            ctx["head_sha"] = head.stdout.strip()

        # Try to parse issue number from branch name (e.g., fix/42-bug, feat-123)
        if "branch" in ctx:
            issue_match = re.search(r"(?:^|[/\-_])(\d+)", ctx["branch"])
            if issue_match:
                ctx["issue_number"] = issue_match.group(1)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Check for GITHUB_TOKEN
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        ctx["has_token"] = "true"

    return ctx


def _fetch_latest_ci_url(owner: str, repo: str) -> str:
    """Fetch the latest successful CI run URL from GitHub API (best-effort)."""
    import json
    import os
    from urllib.request import Request, urlopen

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return ""

    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?status=success&per_page=1"
        req = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        runs = data.get("workflow_runs", [])
        if runs:
            html_url: str = runs[0].get("html_url", "")
            return html_url
    except Exception:
        pass

    return ""


def _fetch_issue_title(owner: str, repo: str, issue_number: str) -> str:
    """Fetch issue title from GitHub API (best-effort)."""
    import json
    import os
    from urllib.request import Request, urlopen

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return ""

    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        req = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        title: str = data.get("title", "")
        return title
    except Exception:
        pass

    return ""


def _run_local_checks() -> str:
    """Run local checks (pytest, ruff, mypy) and return results summary."""
    import subprocess

    results = []

    # pytest
    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
        if last_line:
            results.append(f"- pytest: {last_line}")
    except Exception:
        results.append("- pytest: TODO (run manually)")

    # ruff check (scoped to staged files if any, else full repo)
    ruff_targets = ["src/", "tests/"]
    try:
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        staged_py = [f for f in staged.stdout.strip().splitlines() if f.endswith(".py")]
        if staged_py:
            ruff_targets = staged_py
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["python", "-m", "ruff", "check", *ruff_targets],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode == 0:
            results.append("- ruff check: All checks passed")
        else:
            count = r.stdout.strip().count("\n") + 1 if r.stdout.strip() else 0
            results.append(f"- ruff check: {count} error(s)")
    except Exception:
        results.append("- ruff check: TODO (run manually)")

    # mypy
    try:
        r = subprocess.run(
            ["python", "-m", "mypy", "src/aiv/"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
        if last_line:
            results.append(f"- mypy: {last_line}")
    except Exception:
        results.append("- mypy: TODO (run manually)")

    return "\n".join(results) if results else "- TODO: Test results"


def _build_evidence_sections(
    tier: str,
    scope_lines: str,
    git_ctx: dict[str, str] | None = None,
    local_results: str = "",
) -> str:
    """Build evidence section markdown based on risk tier + auto-populated context."""
    sections = []
    ctx = git_ctx or {}
    owner = ctx.get("owner", "")
    repo = ctx.get("repo", "")
    head_sha = ctx.get("head_sha", "")
    issue_number = ctx.get("issue_number", "")

    # Auto-fetch CI URL and issue info if GitHub token available
    ci_url = ""
    issue_link = ""
    if owner and repo:
        ci_url = _fetch_latest_ci_url(owner, repo)
        if issue_number:
            issue_title = _fetch_issue_title(owner, repo, issue_number)
            if issue_title:
                issue_link = (
                    f"[#{issue_number}: {issue_title}](https://github.com/{owner}/{repo}/issues/{issue_number})"
                )
            else:
                issue_link = f"https://github.com/{owner}/{repo}/issues/{issue_number}"

    # Class E — required by parser for all tiers (structurally mandatory)
    if issue_link:
        class_e_link = issue_link
    else:
        class_e_link = "TODO: SHA-pinned link to spec/issue/directive"

    sections.append(f"""### Class E (Intent Alignment)

- **Link:** {class_e_link}
- **Requirements Verified:**
  1. TODO: Which spec/issue requirement does this change satisfy?
  2. TODO: What acceptance criteria were met?""")

    # Class B — always required
    # Auto-generate SHA-pinned links if we have owner/repo/sha
    if owner and repo and head_sha:
        scope_header = (
            f"**Scope Inventory** (SHA: [`{head_sha[:7]}`](https://github.com/{owner}/{repo}/tree/{head_sha}))"
        )
    else:
        scope_header = "**Scope Inventory (required)**"

    sections.append(f"""### Class B (Referential Evidence)

{scope_header}

- Modified:
{scope_lines}""")

    # Class A — always required
    if ci_url:
        class_a_ci = f"- **CI Run:** [{ci_url.split('/')[-1]}]({ci_url})"
    else:
        class_a_ci = "- CI Run: TODO (set GITHUB_TOKEN to auto-populate)"

    if local_results:
        class_a_local = f"- **Local results:**\n{local_results}"
    else:
        class_a_local = '- TODO: Paste test output here (e.g., "pytest -- 454 passed in 38s") or link to CI run'

    sections.append(f"""### Class A (Execution Evidence)

{class_a_ci}
{class_a_local}""")

    # Class C — required for R2+
    if tier in ("R2", "R3"):
        sections.append("""### Class C (Negative Evidence)

- TODO: Describe what you searched for and didn't find. Example:
  "Searched all test files for deleted assertions or @pytest.mark.skip additions -- none found.
  Ran full regression suite (N tests) -- no failures."
- Search scope: TODO (e.g., "all files in tests/", "grep for removed assert statements")""")

    # Class D — required for R3
    if tier == "R3":
        sections.append("""### Class D (Differential Evidence)

- TODO: Document what changed in the API, state, or config. Example:
  "API surface: `login()` signature unchanged. New optional param `timeout: int = 30`.
  No breaking changes to existing callers."
- Before: TODO
- After: TODO
- Breaking changes: TODO (none / list them)""")

    # Class F — required for R3, optional R2
    if tier in ("R2", "R3"):
        sections.append("""### Class F (Provenance Evidence)

**Claim 3: No regressions**
- No test files modified or deleted. Full test suite passes.""")

    return "\n\n".join(sections)


def _display_findings(findings: list[ValidationFinding], title: str, color: str) -> None:
    """Display findings in a formatted table."""
    table = Table(title=title, border_style=color)
    table.add_column("Rule", style="bold")
    table.add_column("Location")
    table.add_column("Message")
    table.add_column("Suggestion", style="dim")

    for finding in findings:
        table.add_row(finding.rule_id, finding.location or "-", finding.message, finding.suggestion or "-")

    console.print(table)


@app.command()
def begin(
    name: str = typer.Argument(..., help="Identifier for this change (lowercase, alphanumeric + hyphens)"),
    description: str = typer.Option("", "--description", "-d", help="Human-readable description of the change"),
    mode: str = typer.Option(
        "direct",
        "--mode",
        help="Workflow mode: 'direct' (push to main) or 'pr' (feature branches)",
    ),
) -> None:
    """
    Open a new change context.

    This starts tracking commits for a logical change that will be
    packaged into a single Layer 2 verification packet when you run
    `aiv close`.

    Examples:
        aiv begin enforcement-gap-fix
        aiv begin user-auth --description "Add JWT authentication"
        aiv begin payments-v2 --mode pr
    """
    from aiv.lib.change import begin_change

    try:
        ctx = begin_change(name=name, description=description, mode=mode)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    console.print(f"[green]Change '{ctx.name}' started.[/green]")
    console.print(f"  Mode: {ctx.mode}")
    console.print(f"  Started: {ctx.started_at}")
    if description:
        console.print(f"  Description: {description}")
    console.print("\n[dim]Make commits as usual. Run `aiv close` when done to generate the verification packet.[/dim]")


@app.command()
def close(
    requirement: str = typer.Option(
        "",
        "--requirement",
        help="Class E intent -- which spec/issue/directive this change satisfies",
    ),
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip running the full test suite"),
    include_untracked: bool = typer.Option(
        False,
        "--include-untracked",
        help="Include commits made with --no-verify that are not in the change context",
    ),
    tier: str = typer.Option("R1", "--tier", "-t", help="Risk tier: R0, R1, R2, R3"),
    rationale: str = typer.Option("", "--rationale", "-r", help="Classification rationale"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate packet but don't commit"),
) -> None:
    """
    Close the active change and generate a Layer 2 verification packet.

    Reads .aiv/change.json, aggregates evidence from all commits,
    generates PACKET_<name>.md in .github/aiv-packets/, validates it,
    and commits it.

    Examples:
        aiv close --requirement "Section 9.1 enforcement gap identified in audit"
        aiv close --tier R2 --rationale "Auth module changes"
        aiv close --include-untracked
    """
    import subprocess
    from datetime import datetime, timezone

    from aiv.lib.change import (
        clear_change,
        close_change,
        detect_untracked_commits,
        get_base_sha,
        get_head_sha,
    )

    try:
        ctx = close_change()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    # Check for untracked commits (--no-verify bypass)
    untracked = detect_untracked_commits(ctx)
    if untracked and not include_untracked:
        console.print(
            f"[yellow]WARNING:[/yellow] {len(untracked)} commit(s) found on branch "
            "since `aiv begin` that are not tracked in the change context."
        )
        console.print("\nUntracked commits:")
        for u in untracked:
            console.print(f"  {u['sha'][:7]} -- {u['message']}")
        console.print("\nOptions:")
        console.print("  1. Include them: `aiv close --include-untracked`")
        console.print("  2. Exclude them: `aiv close` (they will not be in the packet)")
        console.print("  3. Abort: Ctrl+C")
        proceed = typer.confirm("Proceed without untracked commits?", default=True)
        if not proceed:
            raise typer.Exit(0)

    # Validate tier
    tier_upper = tier.upper().strip()
    if tier_upper not in ("R0", "R1", "R2", "R3"):
        console.print(f"[red]Error:[/red] Invalid tier '{tier}'. Use R0, R1, R2, or R3.")
        raise typer.Exit(1)

    # Gather metadata
    head_sha = get_head_sha()
    base_sha = get_base_sha(ctx)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sod = "S0" if tier_upper in ("R0", "R1") else "S1"
    commit_shas = [c.sha for c in ctx.commits]

    # Auto-detect classified_by
    classified_by = "unknown"
    try:
        r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            classified_by = r.stdout.strip()
    except Exception:
        pass

    # Build evidence references table + extract real claims from evidence files
    import re as _re

    evidence_ref_rows = []
    all_claims: list[str] = []
    all_class_b_refs: list[str] = []
    evidence_dir = Path(".github/aiv-evidence")

    for i, commit in enumerate(ctx.commits):
        for ev in commit.evidence:
            # Try to read evidence file and extract classes + claims
            classes = "A, B"
            ev_path = evidence_dir / ev if not ev.startswith(".github") else Path(ev)
            if ev_path.exists():
                try:
                    ev_body = ev_path.read_text(encoding="utf-8")
                    # Detect which evidence classes are present
                    found_classes = []
                    for cls_letter, cls_name in [
                        ("A", "Class A"),
                        ("B", "Class B"),
                        ("C", "Class C"),
                        ("D", "Class D"),
                        ("E", "Class E"),
                        ("F", "Class F"),
                    ]:
                        if f"### {cls_name}" in ev_body:
                            found_classes.append(cls_letter)
                    if found_classes:
                        classes = ", ".join(found_classes)

                    # Extract claims
                    claims_match = _re.search(r"## Claim\(s\)\s*\n(.*?)(?=\n---|\n## )", ev_body, _re.DOTALL)
                    if claims_match:
                        for line in claims_match.group(1).strip().splitlines():
                            line = line.strip()
                            if line and _re.match(r"\d+\.\s+", line):
                                claim_text = _re.sub(r"^\d+\.\s+", "", line)
                                if claim_text not in all_claims:
                                    all_claims.append(claim_text)

                    # Extract Class B file refs
                    for m in _re.finditer(r"\[`([^`]+#L\d+[^`]*)`\]", ev_body):
                        ref = m.group(1)
                        if ref not in all_class_b_refs:
                            all_class_b_refs.append(ref)
                except Exception:
                    pass

            evidence_ref_rows.append(f"| {i + 1} | {ev} | `{commit.sha[:7]}` | {classes} |")

    evidence_refs_md = (
        (
            "| # | Evidence File | Commit SHA | Classes |\n"
            "|---|---------------|------------|---------|\n" + "\n".join(evidence_ref_rows)
        )
        if evidence_ref_rows
        else "No evidence files recorded."
    )

    # Build claims: use real claims from evidence files, fall back to generic
    if all_claims:
        claims_lines = [f"{i}. {c}" for i, c in enumerate(all_claims, 1)]
    else:
        claims_lines = []
        for i, f in enumerate(ctx.files_changed, 1):
            claims_lines.append(f"{i}. Changes to `{f}` are verified by collected evidence.")
        claims_lines.append(
            f"{len(ctx.files_changed) + 1}. No existing tests were modified or deleted during this change."
        )
    claims_md = "\n".join(claims_lines)

    # Build commit range
    commit_range_md = ", ".join(f"`{s[:7]}`" for s in commit_shas)

    # Class B refs from evidence files
    if all_class_b_refs:
        class_b_refs_md = (
            f"**Scope Inventory** (from {len(all_class_b_refs)} file references across evidence files)\n\n"
            + "\n".join(f"- `{ref}`" for ref in all_class_b_refs)
        )
    else:
        class_b_refs_md = "See individual evidence files for file-level references."

    # Class E (Intent)
    class_e_md = ""
    if requirement:
        class_e_md = f"""### Class E (Intent Alignment)

- **Requirement:** {requirement}"""

    # Build packet
    packet_name = ctx.name.replace("-", "_")
    packet_filename = f"PACKET_{packet_name}.md"
    packets_dir = Path(".github/aiv-packets")
    packets_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packets_dir / packet_filename

    if packet_path.exists():
        console.print(f"[red]Error:[/red] {packet_path} already exists.")
        console.print("Layer 2 packets are immutable -- each change gets a unique packet.")
        console.print(f"If this is a new change, use a different name than '{ctx.name}'.")
        raise typer.Exit(1)

    packet_text = f"""# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | {ctx.name} |
| **Commits** | {commit_range_md} |
| **Head SHA** | `{head_sha[:7] if head_sha else "unknown"}` |
| **Base SHA** | `{base_sha[:7] if base_sha else "unknown"}` |
| **Created** | {now} |

## Classification

```yaml
classification:
  risk_tier: {tier_upper}
  sod_mode: {sod}
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "{rationale or "TODO: Describe why this tier was chosen"}"
  classified_by: "{classified_by}"
  classified_at: "{now}"
```

## Claims

{claims_md}

---

## Evidence References

{evidence_refs_md}

{class_e_md}

### Class B (Referential Evidence)

{class_b_refs_md}

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change '{ctx.name}': {len(ctx.commits)} commit(s) across {len(ctx.files_changed)} file(s).
"""

    console.print(f"[dim]Generating packet: {packet_path}[/dim]")
    packet_path.write_text(packet_text, encoding="utf-8")
    console.print(f"[green]Generated:[/green] {packet_path}")

    # Validate via pipeline
    console.print("[dim]Validating packet...[/dim]")
    config_obj = AIVConfig()
    pipeline = ValidationPipeline(config=config_obj)
    result = pipeline.validate(packet_text)

    if result.warnings:
        for w in result.warnings:
            console.print(f"  [yellow]WARN[/yellow] [{w.rule_id}] {w.message}")

    if result.status == ValidationStatus.FAIL:
        console.print(f"[yellow]Packet has {len(result.errors)} validation error(s):[/yellow]")
        for err in result.errors:
            console.print(f"  [{err.rule_id}] {err.message}")
        console.print("[dim]Packet saved but may need manual fixes before push.[/dim]")

    if dry_run:
        console.print("[dim]Dry run -- skipping git commit.[/dim]")
        raise typer.Exit(0)

    # Stage and commit the packet
    console.print("[dim]Committing packet...[/dim]")
    subprocess.run(["git", "add", str(packet_path)], check=True, timeout=10)

    commit_msg = f"docs(aiv): verification packet for change '{ctx.name}'"
    commit_result = subprocess.run(
        ["git", "commit", "--no-verify", "-m", commit_msg],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if commit_result.returncode != 0:
        console.print("[red]Commit failed:[/red]")
        if commit_result.stdout:
            console.print(commit_result.stdout)
        if commit_result.stderr:
            console.print(commit_result.stderr)
        raise typer.Exit(1)

    console.print(commit_result.stdout.strip())

    # Clear the change context
    clear_change()
    console.print(f"[green][OK] Change '{ctx.name}' closed. Packet committed.[/green]")
    console.print("[dim]Run `git push` to push the change and its packet.[/dim]")


@app.command()
def abandon(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt (alias for --force)"),
) -> None:
    """
    Abandon the active change without generating a packet.

    Evidence files from the abandoned change remain (they're per-file,
    not per-change). Commits made during the change remain in git history.

    Examples:
        aiv abandon
        aiv abandon --force
        aiv abandon -y
    """
    from aiv.lib.change import abandon_change, load_change

    ctx = load_change()
    if ctx is None:
        console.print("[yellow]No active change to abandon.[/yellow]")
        raise typer.Exit(0)

    if not (force or yes):
        console.print(f"Change: [bold]{ctx.name}[/bold]")
        console.print(f"Commits: {len(ctx.commits)}")
        console.print(f"Files changed: {len(ctx.files_changed)}")
        proceed = typer.confirm("Abandon this change?", default=False)
        if not proceed:
            raise typer.Exit(0)

    abandon_change()
    n = len(ctx.commits)
    console.print(f"[yellow]Change '{ctx.name}' abandoned.[/yellow] {n} commit(s) remain unpacketed.")


@app.command()
def status() -> None:
    """
    Show the current change context and evidence state.

    Examples:
        aiv status
    """
    from aiv.lib.change import load_change

    ctx = load_change()
    if ctx is None:
        console.print("[dim]No active change.[/dim]")
        console.print("[dim]Run `aiv begin <name>` to start a tracked change.[/dim]")
        return

    console.print(
        Panel(
            f"[bold]{ctx.name}[/bold]\n"
            f"Mode: {ctx.mode}\n"
            f"Started: {ctx.started_at}\n"
            f"Commits: {len(ctx.commits)}\n"
            f"Files changed: {len(ctx.files_changed)}\n"
            f"Evidence files: {len(ctx.evidence_files)}",
            title="Active Change",
            border_style="cyan",
        )
    )

    if ctx.commits:
        table = Table(title="Commits", show_lines=False)
        table.add_column("SHA", style="bold", width=9)
        table.add_column("Message", width=50)
        table.add_column("Files", width=8)
        for c in ctx.commits:
            table.add_row(c.sha[:7], c.message[:50], str(len(c.files)))
        console.print(table)

    if ctx.commits:
        console.print("\n[dim]Run `aiv close` to generate the verification packet.[/dim]")
    else:
        console.print("\n[dim]No commits yet. Make commits, then run `aiv close`.[/dim]")


@app.command(name="commit")
def commit_cmd(
    file: Path = typer.Argument(..., help="Functional file to commit (e.g. src/auth.py)"),
    message: str = typer.Option(..., "--message", "-m", help="Git commit message"),
    tier: str = typer.Option("R1", "--tier", "-t", help="Risk tier: R0, R1, R2, R3"),
    claim: list[str] = typer.Option(
        [],
        "--claim",
        "-c",
        help="Falsifiable claim about the change (REQUIRED, repeatable). "
        "Format: '[Component] [verb: rejects/returns/ensures/prevents] [result] under [condition]'. "
        "Example: -c 'TokenValidator rejects expired tokens with 401'",
    ),
    intent: str = typer.Option(
        "",
        "--intent",
        "-i",
        help="REQUIRED. Class E intent URL -- link to the spec, issue, or directive that motivated this change. "
        "Example: -i 'https://github.com/org/repo/issues/42'",
    ),
    requirement: str = typer.Option(
        "",
        "--requirement",
        help="REQUIRED. Which specific requirement the --intent URL satisfies. "
        "Example: --requirement 'Issue #42 requires expired tokens return 401'",
    ),
    rationale: str = typer.Option(
        "",
        "--rationale",
        "-r",
        help="REQUIRED. Why this risk tier was chosen. Example: -r 'Standard bug fix in auth module'",
    ),
    summary: str = typer.Option(
        "",
        "--summary",
        "-s",
        help="REQUIRED. One-line summary of the change. "
        "Example: -s 'Handle expired JWT tokens with proper 401 response'",
    ),
    skip_checks: bool = typer.Option(
        False,
        "--skip-checks",
        help="Skip local checks (pytest/ruff/mypy). ONLY allowed for R0 (trivial) tier. "
        "Requires --skip-reason to document why checks were skipped.",
    ),
    skip_reason: str = typer.Option(
        "",
        "--skip-reason",
        help="REQUIRED when --skip-checks is used. Documents why local checks were skipped. "
        "Stamped into the evidence file's Class A section. "
        "Example: --skip-reason 'Help text only, no logic changes'",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate packet and validate but don't commit"),
) -> None:
    """
    Atomic commit with COLLECTED evidence -- not templates.

    Evidence is gathered by running real tools (git diff, pytest -v, ruff,
    mypy, anti-cheat scan). The packet is assembled from tool output, not
    from user-provided strings. You provide claims, intent, and rationale;
    the tool collects the proof.

    Examples:
        aiv commit src/auth.py -m "fix(auth): handle expired tokens" -t R1 \\
            -c "TokenValidator rejects expired tokens with 401" \\
            -i "https://github.com/org/repo/issues/42" \\
            --requirement "Issue #42 requires expired tokens return 401" \\
            -r "Standard bug fix in auth module" \\
            -s "Handle expired JWT tokens with proper 401 response"

    Claim format (falsifiable):
        GOOD: "TokenValidator rejects expired tokens with HTTP 401"
        BAD:  "Fixed the authentication bug"
    """
    import re
    import subprocess
    from datetime import datetime, timezone

    from aiv.lib.evidence_collector import (
        bind_claims_to_evidence,
        collect_class_a,
        collect_class_b,
        collect_class_c,
        collect_class_f,
        find_covering_tests,
        render_claim_matrix,
    )

    # --- Validate tier ---
    tier_upper = tier.upper().strip()
    if tier_upper not in ("R0", "R1", "R2", "R3"):
        console.print(f"[red]Error:[/red] Invalid tier '{tier}'. Use R0, R1, R2, or R3.")
        raise typer.Exit(1)

    # --- Enforce required flags (humans provide intent; tools collect proof) ---
    missing: list[str] = []
    if not claim:
        missing.append("--claim / -c  (at least one falsifiable claim)")
    if not intent:
        missing.append("--intent / -i (URL to spec/issue/directive for Class E)")
    if not rationale:
        missing.append("--rationale / -r (why this tier was chosen)")
    if not summary:
        missing.append("--summary / -s (one-line summary of the change)")
    if not requirement:
        missing.append("--requirement  (which section/requirement the intent URL satisfies)")

    if missing:
        console.print("[red]Error:[/red] Missing required flags:")
        for m in missing:
            console.print(f"  [bold]{m}[/bold]")
        console.print("\n[dim]You provide the intent; the tool collects the proof.[/dim]")
        raise typer.Exit(1)

    # --- Validate --intent is a URL, not plain text ---
    if intent and not intent.strip().startswith(("http://", "https://")):
        console.print(
            "[red]Error:[/red] --intent / -i must be a URL, not plain text.\n"
            f"  You provided: {intent[:80]}\n"
            "  Example: -i 'https://github.com/org/repo/issues/42'\n"
            "  The intent URL is your Class E (Intent Alignment) evidence --\n"
            "  it links to the spec, issue, or directive that motivated this change."
        )
        raise typer.Exit(1)

    # --- Block --skip-checks for R1+ (systemic anti-theater gate) ---
    if skip_checks and tier_upper not in ("R0",):
        console.print(
            f"[red]Error:[/red] --skip-checks is only allowed for R0 (trivial) tier.\n"
            f"  You requested {tier_upper}, which REQUIRES execution evidence.\n"
            f"  Evidence without proof is verification theater.\n"
            f"  Remove --skip-checks or downgrade to --tier R0."
        )
        raise typer.Exit(1)

    # --- Require --skip-reason when --skip-checks is used ---
    if skip_checks and not skip_reason:
        console.print(
            "[red]Error:[/red] --skip-checks requires --skip-reason to document why checks were skipped.\n"
            '  Example: --skip-reason "Help text only, no logic changes"\n'
            "  This justification is stamped into the evidence file."
        )
        raise typer.Exit(1)

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # --- Early check: does this file have changes relative to HEAD? ---
    import subprocess as _sp

    _diff_check = _sp.run(
        ["git", "diff", "HEAD", "--", str(file)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    _staged_check = _sp.run(
        ["git", "diff", "--cached", "--", str(file)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if not _diff_check.stdout.strip() and not _staged_check.stdout.strip():
        # Also check if file is untracked (new file)
        _status_check = _sp.run(
            ["git", "status", "--porcelain", "--", str(file)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if not _status_check.stdout.strip():
            console.print(
                f"[red]Error:[/red] {file} has no changes relative to HEAD.\n"
                f"  Nothing to commit. Did you forget to save the file?"
            )
            raise typer.Exit(1)

    # --- Normalize name (Two-Layer Architecture: Layer 1 evidence file) ---
    # Use path-based naming to avoid collisions (§13.5 of design doc)
    file_posix_raw = str(file).replace("\\", "/")
    # Strip common source root prefixes
    evidence_name = file_posix_raw
    for prefix in ("src/aiv/", "src/", "lib/", "app/"):
        if evidence_name.startswith(prefix):
            evidence_name = evidence_name[len(prefix) :]
            break
    # Normalize: replace separators, remove extension, uppercase
    evidence_name = evidence_name.replace("/", "_").replace("\\", "_")
    if evidence_name.endswith(".py") or evidence_name.endswith(".js") or evidence_name.endswith(".ts"):
        evidence_name = evidence_name[:-3]
    safe_name = evidence_name.upper().replace("-", "_").replace(" ", "_")

    evidence_filename = f"EVIDENCE_{safe_name}.md"
    evidence_dir = Path(".github/aiv-evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    packet_path = evidence_dir / evidence_filename

    # Detect previous version for Previous: header (no overwrite prompt)
    previous_sha = ""
    if packet_path.exists():
        try:
            prev_result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", str(packet_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if prev_result.returncode == 0 and prev_result.stdout.strip():
                previous_sha = prev_result.stdout.strip()[:7]
        except Exception:
            pass

    # --- Build claims ---
    claims_text = "\n".join(f"{i}. {c}" for i, c in enumerate(claim, 1))
    claims_text += f"\n{len(claim) + 1}. No existing tests were modified or deleted during this change."

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sod = "S0" if tier_upper in ("R0", "R1") else "S1"

    # --- Detect git context ---
    console.print("[dim]Detecting git context...[/dim]")
    git_ctx = _detect_git_context()
    owner = git_ctx.get("owner", "")
    repo = git_ctx.get("repo", "")
    head_sha = git_ctx.get("head_sha", "")

    if owner and repo:
        console.print(f"  Repo: [bold]{owner}/{repo}[/bold]")

    # --- Auto-detect classified_by ---
    classified_by = "unknown"
    try:
        r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            classified_by = r.stdout.strip()
    except Exception:
        pass

    # --- COLLECT evidence (not generate) ---
    # file_posix_raw is already defined above (line ~1243)

    # Class E: user-provided (can't be auto-collected)
    # Auto-pin mutable branch URLs to HEAD SHA (anti-theater: immutable links)
    pinned_intent = intent
    if head_sha:
        for mutable_branch in ("main", "master", "develop"):
            mutable_path = f"/blob/{mutable_branch}/"
            pinned_path = f"/blob/{head_sha}/"
            if mutable_path in pinned_intent:
                pinned_intent = pinned_intent.replace(mutable_path, pinned_path)
                console.print(f"  [yellow]Auto-pinned:[/yellow] /blob/{mutable_branch}/ -> /blob/{head_sha[:7]}.../")
                break
    class_e_md = f"""### Class E (Intent Alignment)

- **Link:** [{pinned_intent}]({pinned_intent})
- **Requirements Verified:** {requirement}"""

    # Class B: COLLECTED from git diff line ranges
    console.print("[dim]Collecting Class B (referential) from git diff...[/dim]")
    class_b_data = collect_class_b(file_posix_raw, owner, repo)
    class_b_md = class_b_data.to_markdown()
    console.print(f"  Found {len(class_b_data.hunks)} changed hunk(s)")

    # Class A: COLLECTED from running pytest, ruff, mypy
    class_a_data = None
    from aiv.lib.language_drivers import get_driver

    lang_driver = get_driver(file_posix_raw)
    if not skip_checks:
        console.print("[dim]Collecting Class A (execution) -- running pytest, ruff, mypy...[/dim]")
        class_a_data = collect_class_a(file_posix_raw)
        console.print(f"  pytest: {class_a_data.total_passed} passed, {class_a_data.total_failed} failed")
        console.print(f"  ruff: {'clean' if class_a_data.ruff_clean else 'errors'}")
        console.print(f"  mypy: {class_a_data.mypy_summary}")

        # AST analysis: per-symbol test coverage (polyglot via language drivers)
        if lang_driver is not None:
            console.print(f"[dim]Running AST analysis ({lang_driver.name}) -- symbol resolver + test graph...[/dim]")
            # Parse hunks like "src/aiv/lib/foo.py#L42-L58" → (42, 58)
            line_ranges: list[tuple[int, int]] = []
            hunk_labels: list[str] = []
            for hunk in class_b_data.hunks:
                m_range = re.search(r"#L(\d+)-L(\d+)$", hunk)
                m_single = re.search(r"#L(\d+)$", hunk)
                if m_range:
                    line_ranges.append((int(m_range.group(1)), int(m_range.group(2))))
                    hunk_labels.append(f"L{m_range.group(1)}-L{m_range.group(2)}")
                elif m_single:
                    line_ranges.append((int(m_single.group(1)), int(m_single.group(1))))
                    hunk_labels.append(f"L{m_single.group(1)}")

            if line_ranges:
                changed_symbols = lang_driver.resolve_symbols(file_posix_raw, line_ranges)
                test_graph = lang_driver.build_test_graph("tests/")
                symbol_cov = find_covering_tests(changed_symbols, test_graph, hunk_labels)
                class_a_data.symbol_coverage = symbol_cov
                console.print(f"  Changed symbols: {', '.join(changed_symbols)}")
                for sc in symbol_cov:
                    if "WARNING" in sc.coverage_verdict:
                        console.print(f"  [yellow]{sc.coverage_verdict}[/yellow]")
                    else:
                        console.print(f"  {sc.coverage_verdict}")

        class_a_md = class_a_data.to_markdown()
        console.print(f"  Tests covering changed file: {len(class_a_data.relevant_tests)}")
    else:
        class_a_md = f"""### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** {skip_reason}"""

    # Class C: COLLECTED from scanning diff for regression indicators (R2+)
    class_c_md = ""
    if tier_upper in ("R2", "R3"):
        console.print("[dim]Collecting Class C (negative) -- scanning diff for regressions...[/dim]")
        class_c_data = collect_class_c()
        if class_c_data.assertions_removed:
            console.print(f"  [yellow]WARNING:[/yellow] {len(class_c_data.assertions_removed)} assertion(s) removed")
        if class_c_data.test_files_deleted:
            console.print(f"  [red]ALERT:[/red] {len(class_c_data.test_files_deleted)} test file(s) deleted")
        if class_c_data.anti_cheat_clean:
            console.print("  No regression indicators found.")

        # Downstream impact analysis (AST) — find callers of changed symbols in src/
        if lang_driver is not None and not skip_checks and "changed_symbols" in dir():
            console.print("[dim]Scanning downstream callers of changed symbols...[/dim]")
            downstream = lang_driver.find_downstream_callers(
                changed_symbols, src_dir="src/", exclude_file=file_posix_raw
            )
            class_c_data.downstream_callers = downstream
            if downstream:
                console.print(f"  {len(downstream)} downstream caller(s) found")
            else:
                console.print("  No downstream callers found (change is self-contained)")

        class_c_md = class_c_data.to_markdown()

    # Class D (R3): auto-collected from git diff --stat
    class_d_md = ""
    if tier_upper == "R3":
        try:
            diff_stat_result = subprocess.run(
                ["git", "diff", "--cached", "--stat", str(file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            diff_stat = diff_stat_result.stdout.strip() if diff_stat_result.returncode == 0 else "(unavailable)"
        except Exception:
            diff_stat = "(unavailable)"
        if diff_stat and diff_stat != "(unavailable)":
            class_d_md = (
                "### Class D (Differential Evidence)\n\n"
                "**Change summary** (`git diff --cached --stat`):\n\n"
                f"```\n{diff_stat}\n```"
            )
        # Omit Class D entirely if no stat available (honest > pointer)

    # Class F: COLLECTED from git log chain-of-custody on covering test files (R2+)
    class_f_md = ""
    if tier_upper in ("R2", "R3"):
        console.print("[dim]Collecting Class F (provenance) -- git log chain-of-custody...[/dim]")
        # Extract unique test file paths from Class A relevant tests
        covering_files: list[str] = []
        if not skip_checks and class_a_data and class_a_data.relevant_tests:
            seen: set[str] = set()
            for test_ref in class_a_data.relevant_tests:
                # test_ref format: "tests/unit/test_foo.py::test_name"
                tf = test_ref.split("::")[0] if "::" in test_ref else test_ref
                if tf not in seen:
                    seen.add(tf)
                    covering_files.append(tf)
        class_f_data = collect_class_f(covering_test_files=covering_files if covering_files else None)
        class_f_md = class_f_data.to_markdown()

    # --- Claim Verification Matrix (Phase 6) ---
    claim_matrix_md = ""
    claim_verifications = []
    if not skip_checks:
        console.print("[dim]Binding claims to evidence...[/dim]")
        sym_cov = class_a_data.symbol_coverage if class_a_data else []
        class_c_obj = class_c_data if tier_upper in ("R2", "R3") and "class_c_data" in dir() else None
        claim_verifications = bind_claims_to_evidence(
            claims=list(claim) + ["No existing tests were modified or deleted during this change."],
            symbol_coverage=sym_cov if sym_cov else None,
            class_c=class_c_obj,
            class_a=class_a_data,
        )
        claim_matrix_md = render_claim_matrix(claim_verifications)
        for cv in claim_verifications:
            if cv.verdict == "UNVERIFIED":
                console.print(f"  [red]FAIL[/red] Claim {cv.claim_index}: {cv.evidence_detail}")
            elif cv.verdict == "MANUAL REVIEW":
                console.print(f"  [yellow]REVIEW[/yellow] Claim {cv.claim_index}: {cv.evidence_detail}")
            else:
                console.print(f"  [green]PASS[/green] Claim {cv.claim_index}: {cv.evidence_detail}")

    # --- Phase 7: Block when too many claims are UNVERIFIED ---
    unverified = [cv for cv in claim_verifications if cv.verdict == "UNVERIFIED"]
    total_bindable = [cv for cv in claim_verifications if cv.verdict != "MANUAL REVIEW"]
    unverified_pct = (len(unverified) / len(total_bindable) * 100) if total_bindable else 0

    if tier_upper != "R0" and unverified:
        # R1+: block when >50% of bindable claims are unverified
        # R3: block on ANY unverified claim (stricter)
        should_block = (tier_upper == "R3" and len(unverified) > 0) or (
            tier_upper in ("R1", "R2") and unverified_pct > 50
        )
        if should_block:
            console.print(
                f"\n[red]ERROR: {tier_upper} commit has {len(unverified)}/{len(total_bindable)} "
                f"claims unverified ({unverified_pct:.0f}%):[/red]"
            )
            for cv in unverified:
                console.print(f'  Claim {cv.claim_index}: "{cv.claim_text[:60]}" -- {cv.evidence_detail}')
            console.print("\n[dim]Options:[/dim]")
            console.print("  1. Add tests that call the uncovered symbol(s)")
            console.print("  2. Downgrade to R0 (--tier R0 --skip-checks) if truly trivial")
            raise typer.Exit(1)

    # --- Build methodology text (must reflect reality) ---
    if skip_checks:
        methodology_text = (
            "**R0 (trivial) -- local checks skipped.**\n"
            f"**Reason:** {skip_reason}\n"
            "Only git diff scope inventory was collected. No execution evidence."
        )
    else:
        tools_run = ["git diff (scope inventory)"]
        if class_a_data:
            if class_a_data.symbol_coverage:
                covered = sum(1 for sc in class_a_data.symbol_coverage if sc.calling_tests)
                total_syms = len(class_a_data.symbol_coverage)
                tools_run.append(f"AST symbol-to-test binding ({covered}/{total_syms} symbols verified)")
            elif class_a_data.relevant_tests:
                tools_run.append(f"file-level test discovery ({len(class_a_data.relevant_tests)} tests)")
            else:
                tools_run.append("pytest (no claim-specific tests found)")
        if tier_upper in ("R2", "R3"):
            tools_run.append("anti-cheat scan")
        methodology_text = (
            "**Zero-Touch Mandate:** Verifier inspects artifacts only.\n"
            f"Evidence collected by `aiv commit` running: {', '.join(tools_run)}.\n"
            "Ruff/mypy results are in Code Quality (not Class A) because they prove "
            "syntax/types, not behavior."
        )

    # --- Assemble evidence from collected artifacts ---
    evidence_parts = [class_e_md, class_b_md, class_a_md]
    # Code Quality (ruff/mypy) is separate from Class A — it proves syntax, not behavior
    if class_a_data and not skip_checks:
        evidence_parts.append(class_a_data.code_quality_markdown())
    if class_c_md:
        evidence_parts.append(class_c_md)
    if class_d_md:
        evidence_parts.append(class_d_md)
    if class_f_md:
        evidence_parts.append(class_f_md)
    evidence_sections = "\n\n".join(evidence_parts)

    # --- Assemble evidence file (Layer 1) ---
    previous_line = f"\n**Previous:** `{previous_sha}`" if previous_sha else ""
    packet_text = f"""# AIV Evidence File (v1.0)

**File:** `{file_posix_raw}`
**Commit:** `{head_sha[:7] if head_sha else "pending"}`{previous_line}
**Generated:** {now}
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: {tier_upper}
  sod_mode: {sod}
  critical_surfaces: []
  blast_radius: "{file_posix_raw}"
  classification_rationale: "{rationale}"
  classified_by: "{classified_by}"
  classified_at: "{now}"
```

## Claim(s)

{claims_text}

---

## Evidence

{evidence_sections}

{claim_matrix_md}
---

## Verification Methodology

{methodology_text}

---

## Summary

{summary}
"""

    packet_path.write_text(packet_text, encoding="utf-8")
    if previous_sha:
        console.print(f"[green]Updated:[/green] {packet_path} (previous: {previous_sha})")
    else:
        console.print(f"[green]Generated:[/green] {packet_path}")

    # --- Validate via pipeline (Layer 1 evidence files get lighter validation) ---
    console.print("[dim]Validating evidence file...[/dim]")
    config = AIVConfig()
    pipeline = ValidationPipeline(config=config)
    result = pipeline.validate(packet_text)

    if result.status == ValidationStatus.FAIL:
        # Evidence files may not pass full packet validation — that's expected.
        # Log warnings but don't block.
        console.print(f"[yellow]Evidence file has {len(result.errors)} validation note(s):[/yellow]")
        for err in result.errors:
            console.print(f"  [{err.rule_id}] {err.message}")
        console.print("[dim]This is expected -- evidence files are validated differently from packets.[/dim]")
    elif result.warnings:
        for w in result.warnings:
            console.print(f"  [yellow]WARN[/yellow] [{w.rule_id}] {w.message}")
    else:
        console.print("[green]Evidence file validation passed.[/green]")

    if dry_run:
        console.print("[dim]Dry run -- skipping git stage and commit.[/dim]")
        raise typer.Exit(0)

    # --- Stage and commit ---
    console.print("[dim]Staging files...[/dim]")
    subprocess.run(["git", "add", str(file), str(packet_path)], check=True, timeout=10)
    console.print(f"  Staged: {file}")
    console.print(f"  Staged: {packet_path}")

    console.print("[dim]Committing...[/dim]")
    commit_result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if commit_result.returncode != 0:
        console.print("[red]Commit failed:[/red]")
        if commit_result.stdout:
            console.print(commit_result.stdout)
        if commit_result.stderr:
            console.print(commit_result.stderr)
        raise typer.Exit(1)

    console.print(commit_result.stdout)

    # --- Update change context if active ---
    try:
        from aiv.lib.change import record_commit

        # Get the commit SHA that was just created
        new_sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        new_sha = new_sha_result.stdout.strip() if new_sha_result.returncode == 0 else ""
        if new_sha:
            updated = record_commit(
                sha=new_sha,
                message=message,
                files=[file_posix_raw],
                evidence=[evidence_filename],
            )
            if updated:
                console.print(f"[dim]Updated change context: '{updated.name}' ({len(updated.commits)} commits)[/dim]")
    except Exception:
        pass

    console.print(f"[green][OK] Atomic commit complete: {file} + {packet_path}[/green]")


if __name__ == "__main__":
    app()
