# 01 — Understanding

_Generated 2026-06-17 19:19:15 · branch `claude/eloquent-goodall-sqfrhf` · forensic-audit-pipeline (consolidated)_

**Coverage denominator:** 242 files (every one classified — see appendix).

## Architecture

A Python package (`src/aiv`) distributed as the `aiv` console script (pyproject.toml:54 → aiv.cli.main:app), built on Typer with a main CLI exposing subcommands (check, init, audit, commit, begin, close, generate) and an `aiv svp` sub-application (src/aiv/svp/cli/main.py) for a four-phase predict/trace/probe/ownership/validate/status workflow. The library API (src/aiv/__init__.py) exports AIVConfig, PacketParser, ValidationPipeline and core models for programmatic use. Enforcement is delivered through git hooks (src/aiv/hooks/pre_commit.py, pre_push.py installed by `aiv init`, plus a Husky .husky/pre-commit) and CI workflows (.github/workflows/ci.yml runs ruff/mypy/pytest across Python 3.10–3.13 plus `aiv audit`, and aiv-guard-python.yml runs a guard runner via src/aiv/guard/__main__.py → aiv.guard.runner:main). Module entry points exist for `python -m aiv` and `python -m aiv.guard`. Of 242 files the bulk is documentation (109) and generated artifacts (58), with 46 source and 20 test files; tests cover CLI subcommands, hooks, the auditor, coverage, and end-to-end/SVP integration. The structure is layered: CLI/entry layer → validation/audit pipeline and SVP subsystem → hook & CI guard enforcement.

## Provisional intent

PROVISIONAL: The apparent goal is to define and enforce an 'AIV' protocol — a verification/audit discipline for code changes in which work is organized into atomic 'verification packets' that must pass validation, auditing, and evidence generation before being committed. The tool enforces this policy automatically at the developer's machine (pre-commit/pre-push git hooks installed by `aiv init`) and in CI (the aiv-guard and `aiv audit --commits N` jobs), making compliance non-bypassable. The SVP subsystem (predict/trace/probe/ownership/validate) appears to add a structured, evidence-backed workflow for predicting, tracing, and validating changes with ownership and rating. The heavy documentation-to-source ratio and an exported library API suggest the project also aims to specify the protocol formally and offer it both as a CLI gate and an embeddable library. This intent is inferred from entry points, inventory composition, and naming, and must be confirmed against the actual packet/validation source and protocol docs.

## Role distribution

| Role | Count |
| --- | --- |
| config | 5 |
| doc | 104 |
| generated | 63 |
| asset | 3 |
| dead | 1 |
| source | 46 |
| test | 20 |

## Entry points (19)

| Entry | What |
| --- | --- |
| .husky/pre-commit | Git pre-commit hook — shell script executed by Husky on every commit; enforces AIV atomic commit policy, calls `aiv check` and `aiv audit` on staged packets, runs lint-staged |
| .github/workflows/ci.yml | Primary CI pipeline entry point — triggers on push/PR to main; runs ruff, mypy, pytest matrix (Python 3.10-3.13), `aiv audit --commits 20`, and evidence generation job |
| .github/workflows/aiv-guard-python.yml | CI workflow entry point — runs Python-based AIV guard on PRs/pushes |
| pyproject.toml:54 → aiv.cli.main:app | Console script `aiv` — primary CLI entry point for all protocol commands (check, init, audit, commit, begin, close, etc.) |
| src/aiv/__main__.py | `python -m aiv` module entry point; delegates to aiv.cli.main:app |
| src/aiv/guard/__main__.py → aiv.guard.runner:main | `python -m aiv.guard` module entry point; runs the GitHub Action guard runner |
| src/aiv/svp/cli/main.py:svp_app | SVP Typer sub-application mounted on main CLI as `aiv svp`; commands: status, predict, trace, probe, ownership, validate, rating |
| src/aiv/hooks/pre_commit.py:main | Git pre-commit hook; installed into .git/hooks/pre-commit by `aiv init` |
| src/aiv/hooks/pre_push.py:main | Git pre-push hook; installed into .git/hooks/pre-push by `aiv init` to catch --no-verify bypasses |
| src/aiv/__init__.py | Exported library API: AIVConfig, PacketParser, ValidationPipeline, and core model classes for programmatic use |
| src/aiv/svp/lib/validators/session.py:19 | Exported library API: validate_session(session: SVPSession) -> SVPValidationResult |
| python -m aiv check | CLI subcommand: validates a verification packet; exercised in tests/integration/test_e2e_compliance.py |
| python -m aiv generate | CLI subcommand: generates evidence sections; exercised in tests/integration/test_e2e_compliance.py and tests/unit/test_coverage.py |
| python -m aiv svp predict\|trace\|probe\|ownership\|validate\|status | CLI subcommands for SVP four-phase workflow; exercised in tests/integration/test_svp_full_workflow.py |
| python -m aiv audit | CLI subcommand: runs PacketAuditor; exercised in tests/unit/test_auditor.py |
| python -m aiv commit | CLI subcommand: commits with optional skip-checks/skip-reason flags; exercised in tests/unit/test_cli_commit_skip.py |
| python -m aiv init | CLI subcommand: initialises repo with .aiv.yml and git hooks; exercised in tests/unit/test_cli_init.py |
| aiv.hooks.pre_commit:main | Git pre-commit hook entry point; tested in tests/unit/test_pre_commit_hook.py |
| aiv.hooks.pre_push:main | Git pre-push hook entry point; tested in tests/unit/test_pre_push_hook.py |


## Machine-checkable data

```json
{
  "denominator": 242,
  "roleCounts": {
    "config": 5,
    "doc": 104,
    "generated": 63,
    "asset": 3,
    "dead": 1,
    "source": 46,
    "test": 20
  },
  "entry_points": [
    {
      "entry": ".husky/pre-commit",
      "what": "Git pre-commit hook — shell script executed by Husky on every commit; enforces AIV atomic commit policy, calls `aiv check` and `aiv audit` on staged packets, runs lint-staged"
    },
    {
      "entry": ".github/workflows/ci.yml",
      "what": "Primary CI pipeline entry point — triggers on push/PR to main; runs ruff, mypy, pytest matrix (Python 3.10-3.13), `aiv audit --commits 20`, and evidence generation job"
    },
    {
      "entry": ".github/workflows/aiv-guard-python.yml",
      "what": "CI workflow entry point — runs Python-based AIV guard on PRs/pushes"
    },
    {
      "entry": "pyproject.toml:54 → aiv.cli.main:app",
      "what": "Console script `aiv` — primary CLI entry point for all protocol commands (check, init, audit, commit, begin, close, etc.)"
    },
    {
      "entry": "src/aiv/__main__.py",
      "what": "`python -m aiv` module entry point; delegates to aiv.cli.main:app"
    },
    {
      "entry": "src/aiv/guard/__main__.py → aiv.guard.runner:main",
      "what": "`python -m aiv.guard` module entry point; runs the GitHub Action guard runner"
    },
    {
      "entry": "src/aiv/svp/cli/main.py:svp_app",
      "what": "SVP Typer sub-application mounted on main CLI as `aiv svp`; commands: status, predict, trace, probe, ownership, validate, rating"
    },
    {
      "entry": "src/aiv/hooks/pre_commit.py:main",
      "what": "Git pre-commit hook; installed into .git/hooks/pre-commit by `aiv init`"
    },
    {
      "entry": "src/aiv/hooks/pre_push.py:main",
      "what": "Git pre-push hook; installed into .git/hooks/pre-push by `aiv init` to catch --no-verify bypasses"
    },
    {
      "entry": "src/aiv/__init__.py",
      "what": "Exported library API: AIVConfig, PacketParser, ValidationPipeline, and core model classes for programmatic use"
    },
    {
      "entry": "src/aiv/svp/lib/validators/session.py:19",
      "what": "Exported library API: validate_session(session: SVPSession) -> SVPValidationResult"
    },
    {
      "entry": "python -m aiv check",
      "what": "CLI subcommand: validates a verification packet; exercised in tests/integration/test_e2e_compliance.py"
    },
    {
      "entry": "python -m aiv generate",
      "what": "CLI subcommand: generates evidence sections; exercised in tests/integration/test_e2e_compliance.py and tests/unit/test_coverage.py"
    },
    {
      "entry": "python -m aiv svp predict|trace|probe|ownership|validate|status",
      "what": "CLI subcommands for SVP four-phase workflow; exercised in tests/integration/test_svp_full_workflow.py"
    },
    {
      "entry": "python -m aiv audit",
      "what": "CLI subcommand: runs PacketAuditor; exercised in tests/unit/test_auditor.py"
    },
    {
      "entry": "python -m aiv commit",
      "what": "CLI subcommand: commits with optional skip-checks/skip-reason flags; exercised in tests/unit/test_cli_commit_skip.py"
    },
    {
      "entry": "python -m aiv init",
      "what": "CLI subcommand: initialises repo with .aiv.yml and git hooks; exercised in tests/unit/test_cli_init.py"
    },
    {
      "entry": "aiv.hooks.pre_commit:main",
      "what": "Git pre-commit hook entry point; tested in tests/unit/test_pre_commit_hook.py"
    },
    {
      "entry": "aiv.hooks.pre_push:main",
      "what": "Git pre-push hook entry point; tested in tests/unit/test_pre_push_hook.py"
    }
  ]
}
```
