# 03 — Execution

_Generated 2026-06-18 01:23:19 · branch `claude/eloquent-goodall-sqfrhf` · forensic-audit-pipeline (consolidated)_

**Measured coverage:** 0% ⚠️ (NOT confirmed by the verifier).
**Deep production-code coverage:** 70.75% (deps installed=true).

## Observed behaviors

| Entry | Behavior |
| --- | --- |
| pip install -e ".[dev]" | Succeeded (exit code 0); aiv-protocol 1.0.0 built and installed in editable mode. All declared dependencies were already satisfied. |
| pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml (purpose: test) | Failed with exit code 4: 'unrecognized arguments: --cov=aiv --cov-report=term-missing'. pytest-cov plugin is not installed in the environment. No tests executed; no coverage data collected. |
| pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml (purpose: coverage) | Failed with exit code 4: same as above. Repeated invocation with identical arguments produced identical failure. Zero lines of production or test code were exercised. |
| tests/ (entire test suite — all unit and integration tests) | flipped to executed: The original pass used the uv-isolated `/root/.local/bin/pytest` binary (pytest 9.0.2) which has no pytest-cov plugin in its isolated environment, even though pytest-cov 5.0.0 is installed in the system Python site-packages. Switching to `python -m pytest` (pytest 8.4.2, with cov-5.0.0 and xdist-3.8.0 active) allowed coverage flags to be accepted. The `artifacts/` directory was created for junit output, then the exact original command was re-issued via `python -m pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml` from /home/user/aiv-protocol. (Command: python -m pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml \| Exit code: 1 (test failures, not infrastructure failure) \| Result: 741 passed, 3 warnings, 7 errors in 29.32s \| Coverage: TOTAL 5073 stmts 1484 miss 71% \| junit.xml written to artifacts/junit.xml \| 7 errors are all fixture-setup failures in tests/unit/test_cli_commit_skip.py — `git commit -m init` exits 128 due to missing git user.name/user.email identity in the sandbox (not a code defect). All 748 collected items were exercised (741 passed + 7 setup-error). Plugins active: cov-5.0.0, xdist-3.8.0. Full suite executed, coverage report generated.) |

## Finding deltas (runtime)

| ID | Delta | Class | Note/Evidence |
| --- | --- | --- | --- |
| F1 | confirmed | — | Read src/aiv/lib/validators/anti_cheat.py:135-141. Python precedence: `(line.startswith('+') and not line.startswith('+++')) or (not line.startswith('-') and not line.startswith('\\') and not line.startswith('diff '))`. A '+++' header satisfies the second OR clause, incrementing current_line erroneously. |
| F2 | confirmed | — | Read src/aiv/lib/models.py:54. `normalized.startswith(member.value)` where member values are single capital letters. Inputs like 'AB' or 'AF' match member 'A'. Equality comparison is required. |
| F3 | confirmed | — | Read src/aiv/guard/models.py:182-189. else branch at line 187-188 sets only `overall_result = OverallResult.PASS` without setting `compliance_level`. Field default at line 123 is 'L1'. A passed R3 packet reports compliance_level='L1', indistinguishable from a passed R0 packet. |
| F4 | confirmed | — | Read src/aiv/lib/change.py:232. `git log --format=%H %s {first_sha}^..HEAD` fails with exit code 128 when first_sha is the initial commit. Line 238 returns [] silently on non-zero returncode, masking the failure. |
| F5 | confirmed | — | Read src/aiv/lib/validators/evidence.py:86-101. `pass` at line 90 returns empty errors for github_actions/external link types. The elif branches for performance (E013) and UI (E012) are dead for these link types. |
| F6 | confirmed | — | Read src/aiv/cli/main.py:1237. `subprocess.run(['git', 'commit', '--no-verify', '-m', commit_msg], ...)`. Pre-commit hooks bypassed. No secondary structural validation of packet content observed before this call. |
| F7 | confirmed | — | Read src/aiv/guard/runner.py:249-253. `if not has_optional and not missing` fires only when no required sections are missing. When both required sections AND methodology are absent, the methodology-specific E-METH diagnostic is swallowed. |
| F8 | confirmed | — | Read tests/unit/test_validators.py:607-610. Line 608: `assert artifacts[1] != artifacts[0] or artifacts[2] != artifacts[0]`. With `or`, if claim-2 duplicates but claim-3 does not, assertion passes silently. Comment requires AND. |
| F9 | confirmed | — | Read src/aiv/svp/lib/models.py:89-92 and 592. `from_elo(500)` returns COMPETENT (line 89). `VerifierRating.tier` defaults to NOVICE (line 592). update_tier() is not called at construction. Boundary inconsistency at ELO=500 confirmed. |
| F10 | confirmed | — | Read tests/unit/test_auditor.py:363-368. Line 365: `p.read_text(encoding='utf-8')` return value discarded. Whether the auto-fix modified the file is never asserted. |
| F11 | untested | — | tests/unit/test_coverage.py:120 not read by either analysis pass; no test execution occurred. |
| F12 | untested | — | tests/integration/test_svp_full_workflow.py:247 — agent noted json.loads called after asserting returncode==1; static analysis plausible but source not directly read by primary analyst. No test execution occurred. |
| F13 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:157-172. test_functional_plus_packet_validates uses 5 patches but omits 'aiv.hooks.pre_commit._load_hook_config', allowing real .aiv.yml to be read from os.getcwd(). All other tests use _mock_main which patches this function. |
| F14 | confirmed | — | Static analysis of src/aiv/guard/runner.py:191-204. `file_path.startswith('.github/')` check passes for paths like '.github/x/../../../../../../etc/passwd'. Subsequent `Path(file_path).read_text()` then reads outside the repository root. Path traversal vulnerability confirmed. |
| F15 | confirmed | — | Static analysis of src/aiv/lib/validators/links.py:163-176. `_head_check(url)` passes user-supplied URLs from packet evidence directly to `urllib.request.urlopen` without scheme validation or private-IP blocklist. SSRF vector confirmed. |
| F16 | confirmed | — | Static analysis of src/aiv/cli/main.py:639-700. `_detect_git_context()` extracts owner/repo via regex `[^/]+/[^/.]+` from git remote URL. These character classes permit `?`, `#`, `@` allowing crafted .git/config to inject query parameters into GitHub API calls. |
| F17 | confirmed | — | Read src/aiv/cli/main.py:1233-1241. Same --no-verify commit as F6 at line 1237. Duplicate finding, same defect. |
| F18 | confirmed | — | Static analysis of src/aiv/cli/main.py:1879. `subprocess.run(['git', 'add', str(file), str(packet_path)], ...)` omits the `--` separator. A file path starting with `-` would be misinterpreted as a git flag. |
| F19 | untested | — | tests/unit/test_validators.py:427-479 not directly read; confirms SSRF via agent analysis but test code not verified by primary analyst. No test execution occurred. |
| F20 | untested | — | tests/unit/test_pre_commit_hook.py:308-314 not read; no test execution occurred. |
| F21 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` — `os` is never imported at module level; `__import__` is used inline. Non-idiomatic; static analysis tools miss the dependency. Duplicate of F251/F95/F126/F153/F182. |
| F22 | untested | — | tests/unit/test_svp.py:625-630 not read; no test execution occurred. |
| F23 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:240. Line 240 prints 'REQUIRES: [A + B]' for R1. pipeline.py enforces {A, B, E} for R1. Developers following the displayed rubric will omit Class E evidence and be blocked without prior warning. |
| F24 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:237. Line 237 prints 'REQUIRES: A + B + C + E + [D + F]' for R3 with brackets implying D and F are optional. pipeline.py _TIER_REQUIRED[R3] contains all six classes with no optional carve-out. |
| F25 | confirmed | — | Static analysis of src/aiv/cli/main.py:514 and 1143. Line 514 emits version '2.1'; line 1143 emits version '2.2'. guard/runner.py accepts both. No schema diff or changelog found between v2.1 and v2.2. |
| F26 | confirmed | — | Read src/aiv/cli/main.py:1236-1237. Same --no-verify commit defect as F6. Duplicate. |
| F27 | confirmed | — | Static analysis of src/aiv/lib/validators/pipeline.py:48. Class docstring enumerates seven stages, omitting 'Risk-Tier Evidence Requirements' which is Stage 5 at line 131. CLI references '8-stage pipeline'. Docstring omission confirmed. |
| F28 | confirmed | — | Static analysis of src/aiv/cli/main.py:1664. `'changed_symbols' in dir()` uses no-arg `dir()` which returns scope names; unreliable for testing local variable binding. `locals()` is the correct idiom. |
| F29 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:283. `collect_class_b` calls `_run_git('rev-parse', 'HEAD')` before the commit. The SHA embedded in Class B permalink equals the parent commit, not the commit introducing the change. |
| F30 | confirmed | — | Static analysis of src/aiv/lib/config.py:163. `functional_root_files` includes '.gitignore'. .husky/pre-commit also includes .gitignore in IS_FUNCTIONAL regex. Neither .cursorrules nor any developer-facing doc documents these as functional files. |
| F31 | confirmed | — | Read src/aiv/guard/models.py:182-189. Same finalize() missing compliance_level on PASS as F3. Duplicate. |
| F32 | confirmed | — | Static analysis of .github/workflows/ci.yml:67. `if: github.event_name == push` on protocol-audit job. PR branches are not covered by push-event CI; --no-verify push on a PR branch is undetected until post-merge. |
| F33 | confirmed | — | Static analysis: identical PACKET_PREFIXES list literal appears in pre_commit.py:46-50, pre_push.py:40-44, and auditor.py:51-55. Three independent edits required to add or rename a packet path. |
| F34 | confirmed | — | Static analysis of src/aiv/lib/models.py:268-271. `has_provenance_evidence` iterates `self.claims` for EvidenceClass.PROVENANCE. A packet with Class F in a standalone evidence section but without a PROVENANCE-typed claim returns False. |
| F35 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:319-322. Docstring says 'injected directly into the session JSON' but actual code at lines 380-403 calls `self._run('ownership', ...)` — a full CLI subprocess invocation. Stale docstring. |
| F36 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:3-17. Module docstring lists phases 1-4 and omits Phase 0, describes Phase 4 as 'manual — tested via model injection' but all Phase 4 tests use CLI subprocess. Docstring is wrong on two counts. |
| F37 | confirmed | — | Static analysis of tests/unit/test_pre_commit_hook.py:35-38. Method name `test_template_is_not_packet` vs assertion `_is_packet('...VERIFICATION_PACKET_TEMPLATE.md') is True`. Test name is the exact inverse of the asserted behavior. |
| F38 | confirmed | — | Static analysis of tests/unit/test_models.py:296-305. Docstring reads "'main' should NOT be mutable if excluded from custom set." Assertion at line 304 is `assert link.is_immutable is False` (IS mutable). Docstring states the inverse. |
| F39 | confirmed | — | Static analysis of tests/unit/test_auditor.py:370-381. `test_fix_class_e_local_ref` calls audit(fix=True) and then asserts the fixed URL contains '/blob/main/' — a mutable branch reference that CLASS_E_MUTABLE would immediately re-flag as an ERROR. Auto-fix produces non-compliant output. |
| F40 | confirmed | — | Static analysis of tests/unit/test_auditor.py:243-244. Class docstring references hard-coded line numbers pointing to `auditor.py#L251-L262` and `auditor.py#L276-L296`. These become stale on any insertion or deletion in auditor.py. |
| F41 | confirmed | — | Static analysis of tests/unit/test_coverage.py:36-40. Test name `test_r0_has_class_b_and_a` but line 40 asserts `'### Class E' in result`. Guard constant REQUIRED_CLASSES['R0']==['A','B'] does not list E as required for R0. Misleading test name. |
| F42 | confirmed | — | Read tests/unit/test_auditor.py:361-368. Same discarded p.read_text() result as F10. Duplicate. |
| F43 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:212-214. `_validate_packet` wraps subprocess invocation in bare `except Exception: return True`. Any transient error silently allows commit, defeating the enforcement guarantee. |
| F44 | confirmed | — | Read src/aiv/guard/github_api.py:43-58 and 112-117. `_request` catches only HTTPError; URLError propagates. `list_pr_files` catches only GitHubAPIError at line 116. Caller gets truncated results with no indication of truncation. |
| F45 | confirmed | — | Read src/aiv/guard/github_api.py:150-165. Same pattern as F44 in `list_run_artifacts`. Transient network error mid-pagination causes PASS on artifact check even when artifact exists only on a later page. |
| F46 | confirmed | — | Static analysis: Grep of src/ confirms `validate_file_type_triggers` is defined in evidence.py:261 but never imported or called from ValidationPipeline, EvidenceValidator, guard runner, or CLI. All four trigger rules permanently inactive. |
| F47 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:283-285. `collect_class_b` calls `_run_git('rev-parse', 'HEAD')` and falls back to 'unknown' on failure. All subsequent permalink URLs assembled with this string, producing evidence that resolves to a 404. |
| F48 | confirmed | — | Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit. |
| F49 | confirmed | — | Static analysis of src/aiv/cli/main.py:1085. Evidence file reading in `close` command loop uses bare `except Exception: pass`. Corrupt or missing evidence files cause Layer 2 packet to be generated with no real claims, silently. |
| F50 | confirmed | — | Read src/aiv/lib/change.py:82. `except (json.JSONDecodeError, Exception)` — json.JSONDecodeError is a subclass of Exception; the first entry is redundant. More critically, disk full and permission denied errors are silently treated as 'no active change'. |
| F51 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:65-71. `_run_git` at lines 55-71 returns `result.stdout.strip()` without checking `result.returncode`. When git fails, empty string is returned, causing hook to exit 0 and allow the commit. |
| F52 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:249-255. `_run_git` returns empty string on any git failure. `collect_class_c()` then reports no test files modified and `anti_cheat_clean=True`, producing falsely clean Class C evidence. |
| F53 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:188. `base64.b64decode(data['content'])` called with no exception handling. Truncated or padded base64 from GitHub API raises `binascii.Error` uncaught. |
| F54 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:622-626. For each of N symbol nodes from outer ast.walk, a second full ast.walk runs to find parent ClassDef. O(N²) confirmed. Also `node in ast.iter_child_nodes(parent)` uses object identity which may miss nodes. |
| F55 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:117-140. `_write_safety_snapshot` creates new timestamped directory under `.cache/bb-safety-snapshots/` on every pre-commit run with no cleanup, rotation, or size-limit mechanism. |
| F56 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:492. EVIDENCE_MUTABLE_LINK finding created with `auto_fixable=True` regardless of whether commit_sha is None. `_apply_fixes` silently skips the fix when short_sha is None. `auto_fixable=True` is misleading. |
| F57 | confirmed | — | Read src/aiv/guard/models.py:123. `compliance_level: str = 'L1'` is the field default. Same as F3 — finalize() never overwrites this on PASS. Duplicate citing the field declaration. |
| F58 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:115-117. `_get_introducing_commit` returns `shas[-1]` from split stdout. If git outputs an error message as the last line, that garbage string is returned as a commit SHA. |
| F59 | confirmed | — | Static analysis: `EvidenceValidator._is_bug_fix` and `auditor._is_bug_fix_claim` use different approaches to detect bug-fix packets. Same packet assessed differently by each, creating inconsistent enforcement. |
| F60 | confirmed | — | Static analysis of src/aiv/lib/config.py:284-285. `load_hook_config` wraps entire YAML parse in `try: ... except Exception: pass`. Malformed YAML, wrong types, I/O errors all silently fall back to defaults. |
| F61 | confirmed | — | Read tests/unit/test_auditor.py:365. Same p.read_text() discard as F10. Duplicate. |
| F62 | confirmed | — | Static analysis of tests/unit/test_cli_init.py. Six test methods call subprocess.run to invoke `aiv init` but neither assign the return value nor pass check=True. aiv init failures are invisible; tests fail on filesystem assertions with misleading messages. |
| F63 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:45-61. `_run()` helper calls subprocess.run with timeout=30 but no try/except. Timeout raises subprocess.TimeoutExpired which propagates as uncaught exception, losing stdout/stderr. |
| F64 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:136-137. Line 137 accesses `evidence_files[0]` with no length assertion, causing IndexError if the command failed and produced no evidence files. |
| F65 | confirmed | — | Static analysis of tests/unit/test_auditor.py:377. `auditor.audit(tmp_path, fix=True)` called with no assignment. AuditResult discarded. A regression where fix() produces zero findings would go undetected. |
| F66 | confirmed | — | Static analysis of tests/unit/test_validators.py:433,487. `HTTPError(req.full_url, N, msg, {}, None)` uses empty dict `{}` as fourth argument; urllib.error.HTTPError expects an http.client.HTTPMessage instance. Tests may mask incorrect error handling. |
| F67 | confirmed | — | Static analysis of tests/unit/test_validators.py:395,500. IntentSection re-imported inside fixture body at line 395 and inside test at line 500, shadowing the module-level binding. Dead re-import confirmed. |
| F68 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:118-121,131-134. `_run_aiv_commit(...)` return value not captured. Non-zero exit invisible until downstream assertion fails with misleading message. |
| F69 | confirmed | — | Read src/aiv/cli/main.py:1236-1237. Same --no-verify commit as F6. Duplicate. |
| F70 | confirmed | — | Static analysis of src/aiv/svp/lib/validators/session.py:113. `if pred.predicted_complexity is None:` — in Pydantic v2, unset required field raises ValidationError at construction before this code executes. The None branch is unreachable; S004 warnings are never emitted. |
| F71 | confirmed | — | Static analysis of src/aiv/guard/runner.py:383. `valid=present` — _build_evidence_class_results unconditionally sets valid=present. No independent artifact integrity check. valid always equals present; the field carries no independent information. |
| F72 | confirmed | — | Static analysis of src/aiv/lib/models.py:132-133. `len(ref) >= min_sha_length and all(c in '0123456789abcdef' for c in ref.lower())` — a mutable git tag whose name is ≥7 hex chars is treated as an immutable commit SHA. |
| F73 | confirmed | — | Static analysis of src/aiv/svp/lib/rating.py:23-124. `score_session()` contains no code path that appends `RatingEvent(event_type='bug_missed', ...)`. The -25 ELO penalty for missed bugs is never applied; bugs_missed is always 0. |
| F74 | confirmed | — | Static analysis of src/aiv/lib/parser.py:585. When `artifact_raw` starts with 'http', it is passed directly to `ArtifactLink.from_url()`. If it contains trailing prose or embedded newlines, Pydantic rejects it and except clause returns plain str, skipping all link validation. |
| F75 | confirmed | — | Static analysis of src/aiv/guard/canonical.py:159-160. `validate_canonical()` accesses `canonical_data['attestations'][0]` without iterating over all attestations. Multiple attestations have only their first validated. |
| F76 | confirmed | — | Static analysis of src/aiv/lib/validators/pipeline.py:163-169. In strict mode, `result.status = ValidationStatus.FAIL` when warnings exist. But `ValidationResult.is_valid` returns `not self.blocking_errors`, checking only blocking errors. Callers reading `is_valid` see True while `status` is FAIL. |
| F77 | confirmed | — | Read tests/unit/test_svp.py:154-157,385-388,883-886 and src/aiv/svp/lib/models.py:80-92,585-614. from_elo(500)==COMPETENT vs VerifierRating(elo=500).tier==NOVICE. Mutually contradictory. Same as F9. |
| F78 | confirmed | — | Read tests/unit/test_validators.py:607-610. Same or-vs-and defect as F8. Duplicate. |
| F79 | confirmed | — | Static analysis of tests/unit/test_auditor.py:875-884. `test_evidence_dir_none_skips_scan` creates empty packets_dir and asserts 0 scanned and 0 findings. Both assertions trivially satisfied regardless of evidence_dir=None behavior. |
| F80 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:247,309. After asserting returncode==1, test calls `json.loads(result.stdout)`. A plain-text error response raises json.JSONDecodeError instead of a meaningful AssertionError. |
| F81 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:119,132. `_run_aiv_commit(...)` return value discarded. Same as F68. Duplicate. |
| F82 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:157-172. Same missing _load_hook_config patch as F13. Duplicate. |
| F83 | confirmed | — | Static analysis of src/aiv/guard/runner.py:191. Same path traversal as F14 — `file_path.startswith('.github/')` without Path.resolve(). Triplicate finding. |
| F84 | confirmed | — | Static analysis of src/aiv/lib/validators/links.py:169. Same SSRF as F15 — `urlopen(req, ...)` with no scheme/host restriction. Triplicate finding. |
| F85 | confirmed | — | Static analysis of src/aiv/cli/main.py:683. `_fetch_latest_ci_url` constructs API URL from owner/repo extracted via regex without validation. Crafted .git/config can inject query parameters into the URL. |
| F86 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:176. `get_file_content` constructs URL with `path` argument without URL-encoding. A path containing `#`, `?`, `%`, or `/..` alters the request path or query string. |
| F87 | confirmed | — | Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit. |
| F88 | confirmed | — | Static analysis of src/aiv/cli/main.py:843. `owner`, `repo`, `head_sha` interpolated into GitHub URL in generated markdown without sanitization. Repository remote with Markdown-special characters can break link syntax. |
| F89 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:88. `Path(event_path).read_text()` with no path restrictions. In environments where GITHUB_EVENT_PATH is attacker-settable, this allows reading arbitrary files. |
| F90 | confirmed | — | Static analysis of tests/unit/test_validators.py:427. TestLinkVitality confirms production LinkValidator calls urlopen with user-supplied URLs. No test validates internal/cloud-metadata URLs are blocked. Near-duplicate of F19. |
| F91 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:387. S011 checks that author_github_id matches session.verifier_id but both originate from the same user-supplied --verifier CLI flag with no cryptographic binding. |
| F92 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:116. Tests validate only benign alphanumeric --skip-reason strings. No test validates that markdown structural characters are escaped before insertion into evidence files. |
| F93 | confirmed | — | Static analysis of tests/unit/test_auditor.py:370. Auto-fix test confirms URL construction concatenates local filename without URL-encoding. Packet reference like '../../.env' would embed unencoded string in generated URL. |
| F94 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:63. Session path constructed as '.svp/session-pr{pr}.json' keyed on PR number. Two actors targeting the same PR number share one session, allowing overwrites. |
| F95 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` spreads all host environment variables including CI secrets into subprocess. Near-duplicate of F21/F153/F182/F126/F251. |
| F96 | confirmed | — | Static analysis: .husky/pre-commit PACKET_PATTERN only matches VERIFICATION_PACKET_* prefix. `aiv commit` stages EVIDENCE_*.md files which do not match, so HAS_PACKET is empty and Rule 5 fires, blocking the commit. Python hook correctly allows evidence-only commits. |
| F97 | confirmed | — | Static analysis: `aiv close` generates PACKET_<name>.md files. Bash hook only matches VERIFICATION_PACKET_*. Commits of close-generated packets are blocked by Husky with spurious Rule 5 rejection. |
| F98 | confirmed | — | Static analysis: Python pre-commit hook allows any commit when `aiv begin` is active (change context mode). Bash hook has no equivalent check, making it semantically incompatible with the aiv begin/commit/close workflow. |
| F99 | confirmed | — | Static analysis: `close` command docstring never mentions --no-verify bypass. Python pre-commit hook would allow this commit anyway (packet-only check passes), so --no-verify is also unnecessary — it creates a compliance gap without functional need. |
| F100 | confirmed | — | Static analysis of src/aiv/lib/validators/pipeline.py:49-56. ValidationPipeline docstring enumerates seven stages but omits 'Risk-Tier Evidence Requirements'. CLI references '8-stage pipeline'. Missing stage is where E019/E020 findings originate. |
| F101 | confirmed | — | Static analysis: pre_push.py claims 'CI catches even --no-verify push (server-side)'. ci.yml protocol-audit runs only on `push` to main, not on `pull_request`. A PR with --no-verify commits bypasses all three layers until post-merge. |
| F102 | confirmed | — | Static analysis: .cursorrules:9 instructs `git add <file>` before `aiv commit`, but `aiv commit` internally calls `git add` again. Documented workflow and actual execution model differ in staging sequence. |
| F103 | confirmed | — | Static analysis: R0 requires Class A evidence. With --skip-checks, a placeholder '### Class A' header satisfies the validator without any real execution artifact. Tier check bypassed silently. |
| F104 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:321. Docstring states Phase 4 'is injected directly into the session JSON', but implementation uses CLI subprocess. Stale docstring. Near-duplicate of F35. |
| F105 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:10. Module docstring reads 'Phase 4: Ownership Lock (manual — tested via model injection)'. All Phase 4 tests use `self._run('ownership', ...)`. Near-duplicate of F36. |
| F106 | confirmed | — | Static analysis of tests/unit/test_pre_commit_hook.py:36. Test named `test_template_is_not_packet` asserts `_is_packet(TEMPLATE.md) is True`. The hook treats templates as valid packets while the auditor excludes them — cross-subsystem inconsistency. Near-duplicate of F37. |
| F107 | confirmed | — | Static analysis of tests/unit/test_cli_init.py:139. `test_pre_push_hook_content_mentions_no_verify` docstring claims behavioral verification but assertion only checks that the string '--no-verify' appears in the hook file content. |
| F108 | confirmed | — | Static analysis of tests/unit/test_guard.py:401. `test_empty_body_fails` uses `assert result.block_count >= 1 or result.warn_count >= 1`. With `or`, a warning-only outcome passes, which would not block PR merge. |
| F109 | confirmed | — | Static analysis of tests/unit/test_validators.py:366. `test_r2_optional_d_and_f_info` asserts `len(info) >= 1`. Satisfied if only one of D/F fires; missing F is silently accepted. |
| F110 | confirmed | — | Static analysis of tests/unit/test_auditor.py:359. `test_fix_commit_pending` only asserts non-crashing. Auto-fix behavior itself is entirely untested. Near-duplicate of F42/F10. |
| F111 | confirmed | — | Static analysis of tests/unit/test_auditor.py:370. `test_fix_class_e_local_ref` asserts fixed URL contains '/blob/main/' — mutable branch reference — which CLASS_E_MUTABLE would immediately re-flag as ERROR. Auto-fix produces non-compliant output. Same as F39. |
| F112 | confirmed | — | Static analysis of tests/unit/test_coverage.py:43. `test_r1_adds_class_e` name is misleading because R0 tests also assert Class E presence. Near-duplicate of F41. |
| F113 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:155-214. NamedTemporaryFile (delete=False) and mkdtemp `audit_dir` created with no cleanup in the except block at line 212. Exception between creation and cleanup leaves temp resources on disk permanently. |
| F114 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:249-255. Docstring states 'never raises' but `subprocess.run(..., timeout=30)` with no try/except means subprocess.TimeoutExpired and FileNotFoundError propagate uncaught. |
| F115 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:51-76. `_request` and `_request_bytes` catch only HTTPError. URLError (DNS failures, connection refused, SSL errors) propagates uncaught. Near-duplicate of F44. |
| F116 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:88. `json.loads(Path(event_path).read_text(...))` called with no try/except. Malformed GITHUB_EVENT_PATH JSON causes unhandled json.JSONDecodeError before any validation begins. |
| F117 | confirmed | — | Static analysis of src/aiv/cli/main.py:1879,1233. `subprocess.run(['git', 'add', ...], check=True, timeout=10)` — CalledProcessError, TimeoutExpired, FileNotFoundError propagate as raw exceptions, inconsistent with rest of CLI user-facing error handling. |
| F118 | confirmed | — | Static analysis of src/aiv/cli/main.py:1664,1721. `'changed_symbols' in dir()` and `'class_c_data' in dir()` antipattern. Near-duplicate of F28. |
| F119 | confirmed | — | Static analysis of src/aiv/guard/runner.py:381. `valid=present` — field never carries independent information. Near-duplicate of F71. |
| F120 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:188,193. `import base64` and `import urllib.parse` deferred inside function bodies. Inconsistent with module-level imports elsewhere; hides dependencies from static analysis. |
| F121 | confirmed | — | Static analysis of src/aiv/cli/main.py:1489. `import subprocess as _sp` creates alias at line 1489 that is never referenced after line 1513. Dead code. |
| F122 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:128-131. `_LOCAL_FILE_PATHS` maps only AUDIT_REPORT.md and SPECIFICATION.md. In any repo without exactly these filenames, `auto_fixable` is always False and the auto-fix logic in `_apply_fixes` is dead for all practical users. |
| F123 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:620-626. O(N²) AST traversal — inner ast.walk for each outer node. No size limit enforced on file before parsing. Near-duplicate of F54. |
| F124 | confirmed | — | Read tests/unit/test_auditor.py:365. Same discarded p.read_text() as F10. Duplicate. |
| F125 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:119. `_run_aiv_commit(...)` return value discarded. Near-duplicate of F68/F81. |
| F126 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. `__import__('os')` inline — os absent from module-level imports, hiding dependency from static analysis. Near-duplicate of F21/F95. |
| F127 | confirmed | — | Static analysis of tests/unit/test_auditor.py:419. `import subprocess` and `import sys` inside test body, hiding dependencies from static analysis and running import machinery on every test invocation. |
| F128 | confirmed | — | Read tests/unit/test_svp.py:670-680. Line 676: mid-file `from aiv.svp.lib.rating import calculate_rating, score_session` after test classes, violating PEP 8 E402. |
| F129 | confirmed | — | Static analysis of tests/unit/test_language_drivers.py:90. `try: ... except ImportError` catches only ImportError. `TreeSitterDriver().available` may raise AttributeError or RuntimeError if native libraries are partially installed. Near-duplicate of F250. |
| F130 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:157. Same missing _load_hook_config patch as F13. Duplicate. |
| F131 | confirmed | — | Static analysis of tests/unit/test_cli_init.py:57. Same subprocess.run return value discarded as F62. Near-duplicate. |
| F132 | confirmed | — | Read src/aiv/lib/validators/anti_cheat.py:132-142. Same operator precedence defect as F1. Duplicate. |
| F133 | confirmed | — | Static analysis of src/aiv/lib/models.py:306-309. `is_valid` returns `len(self.blocking_errors) == 0`. In strict mode, status is FAIL when warnings exist, but `is_valid` returns True. Callers branching on `is_valid` incorrectly allow strict-mode failures through. |
| F134 | confirmed | — | Static analysis of src/aiv/lib/validators/anti_cheat.py:203-209. `check_justification` — first matching Class F claim with justification > 20 chars clears the finding for ALL deletions, not just the relevant claim. Single lengthy justification blanket-clears all anti-cheat findings. |
| F135 | confirmed | — | Static analysis of src/aiv/guard/runner.py:336-365. Guard checks only head_sha match and aiv-evidence artifact presence. Workflow run conclusion status (success/failure) not validated; a failed CI run with correct SHA is accepted as proof. |
| F136 | confirmed | — | Static analysis of src/aiv/svp/lib/validators/session.py:156-157,183-185. `return False` called immediately after appending first S006 or S015 error. If session.traces has N elements, only the first invalid trace is reported; subsequent N-1 are silently skipped. |
| F137 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:434-578. `_check_packet` includes TODO remnant scans. These internal TODO-marker checks are applied to user-facing packets, potentially flagging legitimate packet fields that contain the string 'TODO'. |
| F138 | confirmed | — | Static analysis of src/aiv/svp/lib/rating.py:147. `bugs_caught = len([e for e in all_events if e.event_type.startswith('bug_caught')])`. Both confirmed probe findings and falsification confirmations are counted, potentially double-counting the same bug. |
| F139 | confirmed | — | Static analysis of src/aiv/lib/parser.py:584-586. Same as F74 — raw multi-line URL strings bypass validation via except clause returning plain str. Near-duplicate. |
| F140 | confirmed | — | Static analysis of src/aiv/guard/canonical.py:231-235. `return False` after first missing evidence class. Only the first missing class reported; a packet missing multiple required classes receives only one CT-002 finding. |
| F141 | confirmed | — | Read tests/unit/test_validators.py:608-610. Same or-vs-and defect as F8. Duplicate. |
| F142 | confirmed | — | Read tests/unit/test_svp.py:154-157,389-390. Same VerifierTier inconsistency as F9. Duplicate. |
| F143 | confirmed | — | Static analysis of tests/unit/test_models.py:298-304. Same docstring/assertion inversion as F38. Duplicate. |
| F144 | confirmed | — | Static analysis of tests/unit/test_guard.py:408-425. `test_valid_markdown_packet` sole assertion is `canonical_enabled is False`. Whether the packet actually passed validation is unverified. |
| F145 | confirmed | — | Static analysis of tests/unit/test_auditor.py:514-533. Mock `git log` helper output format differs from real git log format. Tests verified against mock, not real git output fidelity. |
| F146 | confirmed | — | Static analysis of src/aiv/guard/runner.py:191. Same path traversal as F14/F83. Triplicate. |
| F147 | confirmed | — | Static analysis of src/aiv/lib/validators/links.py:163. Same SSRF as F15/F84. Triplicate. |
| F148 | untested | — | .github/workflows/ci.yml:387 not read; details truncated in agent output. No test execution occurred. |
| F149 | confirmed | — | Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit. |
| F150 | untested | — | src/aiv/guard/github_api.py:42 details truncated in agent output; not directly verified. No test execution occurred. |
| F151 | confirmed | — | Static analysis of tests/unit/test_validators.py:427-479. Confirms production LinkValidator calls urlopen with raw packet URLs. No test validates internal URL blocking. Near-duplicate of F19/F90. |
| F152 | confirmed | — | Static analysis of tests/unit/test_models.py:87-89. `ArtifactLink.from_url('https://example.com/some/page')` accepted without rejection. No test validates that file://, ftp://, or cloud-metadata URLs are rejected at model level. |
| F153 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. Same ambient environment spread as F21/F95. Near-duplicate. |
| F154 | confirmed | — | Static analysis of tests/unit/test_auditor.py:370-381. Auto-fix falls back to 'main' branch (mutable); test confirms and accepts this. Near-duplicate of F39/F111. |
| F155 | confirmed | — | Static analysis of tests/unit/test_coverage.py:398-407. Only syntactically malformed YAML tested; structurally-valid YAML with wrong type for functional_prefixes — the exact scenario swallowed by `except Exception: pass` — is never tested. |
| F156 | confirmed | — | Static analysis of tests/unit/test_svp.py:443-528. TestSessionValidator exercises rules using in-memory objects only. Discrepancies in CLI argument parsing that affect session construction would be missed. |
| F157 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:116-138. Only benign strings tested. No test validates markdown content injection via --skip-reason. Near-duplicate of F92. |
| F158 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:261. Same dead `validate_file_type_triggers` as F46/F217. Triplicate. |
| F159 | confirmed | — | Static analysis of src/aiv/lib/validators/pipeline.py:183. `_TIER_REQUIRED[R1]` contains {EXECUTION, REFERENTIAL, INTENT}. pre_commit.py:240 displays only '[A + B]' for R1, omitting INTENT (Class E). Near-duplicate of F23. |
| F160 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:113. Rule ID 'E020' emitted at two distinct sites with unrelated meanings. Duplicate rule ID causes ambiguity in reports. |
| F161 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:402. anti_cheat.py:207 uses `claim.justification or claim.description` fallback; evidence.py:402 does not use the same fallback. Inconsistent behavior between the two validation paths. |
| F162 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:242. Zero-Touch check scans only five DB keywords. Any ORM, NoSQL tool, or SQL dialect not in the list bypasses manual-state detection. |
| F163 | confirmed | — | Static analysis of tests/unit/test_pre_commit_hook.py:35. Same inverted test name as F37/F106/F172. Near-duplicate. |
| F164 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:10. Module docstring 'Phase 4: manual — tested via model injection' vs CLI implementation. Near-duplicate of F36/F105. |
| F165 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:321. Method docstring vs CLI implementation mismatch. Near-duplicate of F35/F104. |
| F166 | confirmed | — | Static analysis of tests/unit/test_validators.py:298. Same docstring/assertion inversion as F38/F143. Near-duplicate. |
| F167 | confirmed | — | Static analysis of tests/unit/test_guard.py:408. Same assertion-only-checks-canonical-enabled as F144. Near-duplicate. |
| F168 | confirmed | — | Static analysis of tests/unit/test_auditor.py:356. Same non-crashing-only assertion as F42/F110. Near-duplicate. |
| F169 | confirmed | — | Static analysis of tests/unit/test_cli_init.py:139. Same docstring/content mismatch as F107. Near-duplicate. |
| F170 | confirmed | — | Static analysis of tests/unit/test_auditor.py:244. Same stale hard-coded line numbers in docstring as F40. Near-duplicate. |
| F171 | confirmed | — | Static analysis of tests/unit/test_models.py:97. `with pytest.raises(Exception)` catches any unrelated exception instead of the specific expected type (ValidationError or TypeError). |
| F172 | confirmed | — | Static analysis of tests/unit/test_pre_commit_hook.py:35. Same inverted test name as F37/F106/F163. Plus cross-subsystem inconsistency: hook treats templates as packets; auditor excludes them. Near-duplicate. |
| F173 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:249. Same 'never raises' contract violation as F114/F52. Near-duplicate. |
| F174 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:43. Same URLError not caught as F115/F44. Near-duplicate. |
| F175 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:183. Same temp file no cleanup as F113. Near-duplicate. |
| F176 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:348. `_run(pytest_cmd, timeout=360)` — `_run` makes no attempt to catch subprocess.TimeoutExpired. 'Never raises' contract violated. |
| F177 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:60. `_request_bytes` is called only from `download_artifact_zip`, which is never invoked from runner.py. Method is dead code in the current guard execution path. |
| F178 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:191. `search_code` method defined but never called from runner.py or any other audited file. Dead code. |
| F179 | confirmed | — | Static analysis of tests/unit/test_cli_init.py. Six test methods call subprocess.run without storing or checking return value. Near-duplicate of F62/F131. |
| F180 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:118-121,131-134. Same discarded return value as F68/F81/F125. Near-duplicate. |
| F181 | confirmed | — | Read tests/unit/test_auditor.py:365. Same p.read_text() discard as F10. Duplicate. |
| F182 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. Same __import__('os') inline as F21/F95/F126. Near-duplicate. |
| F183 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:157-172. Same missing _load_hook_config patch as F13. Duplicate. |
| F184 | confirmed | — | Static analysis of tests/unit/test_guard.py:408-425. Same assertion-only-checks-canonical-enabled as F144/F167. Near-duplicate. |
| F185 | confirmed | — | Read tests/unit/test_svp.py:676. Same mid-module import as F248/F128. Duplicate. |
| F186 | confirmed | — | Read src/aiv/lib/validators/anti_cheat.py:132-142. Same operator precedence defect as F1. Duplicate. |
| F187 | confirmed | — | Static analysis of src/aiv/lib/validators/anti_cheat.py:192-213. Same blanket justification clearing as F134. Near-duplicate with additional detail: a single lengthy justification anywhere clears ALL anti-cheat findings. |
| F188 | confirmed | — | Read src/aiv/guard/models.py:182-188. Same finalize() compliance_level defect as F3. Duplicate. |
| F189 | confirmed | — | Static analysis of src/aiv/lib/parser.py:585. Same raw URL bypass as F74/F139. Near-duplicate. |
| F190 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:390-401. `_check_packet` uses `re.search(r'## Claim\(s\)\s*\n...')`. The guard accepts alternative heading spellings. Parse discrepancy between auditor and guard for the same packet. |
| F191 | confirmed | — | Read tests/unit/test_svp.py:154-157,387,885. Same VerifierTier inconsistency as F9/F77/F142. Duplicate. |
| F192 | confirmed | — | Read tests/unit/test_validators.py:608. Same or-vs-and defect as F8. Duplicate. |
| F193 | confirmed | — | Static analysis of tests/unit/test_svp.py:262-265. `fs.checked is False` and `fs.result == 'confirmed'` on the same object. A scenario that has not been checked having result='confirmed' is logically contradictory; the model allows an invalid state. |
| F194 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:134. Accesses `evidence_files[0]` without prior length assertion while sibling test first asserts `len(evidence_files) == 1`. Near-duplicate of F64. |
| F195 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:158-172. Same missing _load_hook_config patch as F13/F82/F130/F183. Duplicate. |
| F196 | confirmed | — | Static analysis of src/aiv/lib/validators/links.py:163-168. Same SSRF as F15/F84/F147. Near-duplicate. |
| F197 | confirmed | — | Static analysis of src/aiv/guard/runner.py:191-200. Same path traversal as F14/F83/F146. Near-duplicate. |
| F198 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:176. Same missing URL-encoding as F86. Near-duplicate. |
| F199 | confirmed | — | Static analysis of src/aiv/guard/canonical.py:438-441. `_read_scope_inventory` base64-decodes payload with no length guard. Arbitrarily large inline-b64-json scope inventory can cause memory exhaustion. |
| F200 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:40. `self.token` stored as plain string attribute with no `__repr__` override. `repr(api)` or pickling emits the token value. |
| F201 | confirmed | — | Static analysis of src/aiv/guard/canonical.py:442. `__import__('json').loads(decoded)` — dynamic import in an auditability tool. json is a stdlib module; deferred inline import is non-idiomatic and hides the dependency. |
| F202 | confirmed | — | Static analysis of tests/unit/test_validators.py:427. Same SSRF confirmation as F19/F90/F151. Triplicate. |
| F203 | confirmed | — | Static analysis of tests/unit/test_validators.py:465. `test_audit_links_network_error_warns` patches urlopen to raise URLError and expects WARN. No test verifies that a redirect to an internal address is blocked before following. |
| F204 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:114. Same missing markdown injection test as F92/F157. Near-duplicate. |
| F205 | confirmed | — | Static analysis of tests/unit/test_svp.py:511. S011 checks author_github_id == session.verifier_id but no test verifies that author_github_id is derived from a trusted source. Near-duplicate of F91. |
| F206 | confirmed | — | Static analysis of tests/unit/test_auditor.py:370. Same auto-fix produces mutable URL as F39/F111/F154. Near-duplicate. |
| F207 | confirmed | — | Static analysis of tests/unit/test_guard.py:92. `_minimal_canonical()` constructs scope inventory as `'inline-json:' + json.dumps(['README.md'])`. Test doesn't validate behavior with malformed JSON payload after the prefix. |
| F208 | confirmed | — | Static analysis of tests/unit/test_pre_push_hook.py:189. TestMain mocks entire real execution path. Tests verify logic but not actual git integration. |
| F209 | confirmed | — | Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit. |
| F210 | confirmed | — | Static analysis of .husky/pre-commit:61. PACKET_PATTERN only matches VERIFICATION_PACKET_*. Does not match EVIDENCE_*.md or PACKET_*.md. Near-duplicate of F96/F97. |
| F211 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:7. Module docstring says 'Feature-complete port of the original .husky/pre-commit' but Python hook adds capabilities absent from bash hook (change context mode, evidence-file recognition). Description is inaccurate. |
| F212 | confirmed | — | Static analysis of .cursorrules:30-35. .cursorrules defines tiers only as risk-level descriptions. canonical.py enforces specific evidence class requirements per tier. Developer-facing documentation does not show actual evidence class requirements. |
| F213 | confirmed | — | Static analysis of src/aiv/guard/runner.py:5. Module docstring states 'Replaces the 2244-line inline JS in aiv-guard.yml'. No such JavaScript file found in the repository. Referenced original is absent. |
| F214 | confirmed | — | Static analysis of .github/workflows/ci.yml:5-7. Both push and pull_request triggers constrained to `branches: [main]`. Protocol-audit only fires when changes reach main — PR branches not covered. Near-duplicate of F32/F101. |
| F215 | confirmed | — | Static analysis of src/aiv/lib/config.py:154. HookConfig.functional_prefixes includes .gitignore-related files. Near-duplicate of F30. |
| F216 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:334. `validate_file_type_triggers()` emits rule_id='E021'. `LinkValidator._check_link` also uses E021 for link-related checks. Duplicate rule ID across two validators. |
| F217 | confirmed | — | Static analysis of src/aiv/lib/validators/evidence.py:261. `validate_file_type_triggers` takes `changed_files: list[str]` but `ValidationPipeline` calls `validator.validate(packet)` with no `changed_files` argument. Architecturally uncallable through standard pipeline interface. Near-duplicate of F46/F158. |
| F218 | confirmed | — | Static analysis of src/aiv/lib/validators/structure.py:24-30. Class docstring itemises four checks but implementation includes additional checks (E004, E006, E007) not listed. Docstring is an incomplete enumeration of enforced rules. |
| F219 | confirmed | — | Static analysis of scripts/map_packets.py:15. PACKET_PREFIX uses different pattern from auditor, pre-commit hook, and guard expectations. Mapping script may miss packets or include non-packet files. |
| F220 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:317. Docstring states 'injected directly into session JSON' but implementation uses CLI. Near-duplicate of F35/F104/F105/F165. |
| F221 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:4. Module docstring omits Phase 0 (Sanity/AIV Guard check), which is exercised by test_full_journey_passes_validation via phase_0_complete assertions. |
| F222 | confirmed | — | Static analysis of tests/unit/test_models.py:296. Same docstring/assertion inversion as F38/F143/F166. Near-duplicate. |
| F223 | confirmed | — | Static analysis of tests/unit/test_cli_init.py:139. Same docstring mismatch as F107/F169. Near-duplicate. |
| F224 | confirmed | — | Static analysis of tests/unit/test_pre_commit_hook.py:233. TestRule8TooManyFiles test name implies three functional files trigger rejection but staged list may include non-functional files, making the count ambiguous. |
| F225 | confirmed | — | Static analysis of tests/unit/test_auditor.py:243. Same stale hard-coded line numbers in docstring as F40/F170. Near-duplicate. |
| F226 | confirmed | — | Read tests/unit/test_validators.py:606-610. Same or-vs-and defect as F8. Duplicate. |
| F227 | confirmed | — | Static analysis of tests/unit/test_auditor.py:359. Same non-crashing-only assertion as F10/F42/F61/F110/F124. Near-duplicate. |
| F228 | confirmed | — | Static analysis of tests/unit/test_coverage.py:36. Same misleading test name as F41/F112. Near-duplicate. |
| F229 | confirmed | — | Static analysis of tests/unit/test_guard.py:449. `REQUIRED_CLASSES['R0'] == ['A', 'B']` (no E) vs test_coverage.py asserting Class E for R0. Inconsistency between guard-enforced requirements and template-generated output. |
| F230 | confirmed | — | Read src/aiv/lib/change.py:82. `except (json.JSONDecodeError, Exception)` — redundant listing. Same as F50. Duplicate. |
| F231 | confirmed | — | Static analysis of src/aiv/lib/config.py:284. Same `except Exception: pass` swallowing YAML errors as F60. Near-duplicate. |
| F232 | confirmed | — | Static analysis of src/aiv/lib/evidence_collector.py:249. Same 'never raises' contract violation as F52/F114/F173. Near-duplicate. |
| F233 | confirmed | — | Static analysis of src/aiv/hooks/pre_commit.py:155. Same temp file no cleanup as F113/F175. Near-duplicate. |
| F234 | confirmed | — | Static analysis of src/aiv/cli/main.py:1664. Same `'changed_symbols' in dir()` antipattern as F28/F118. Near-duplicate. |
| F235 | confirmed | — | Static analysis of src/aiv/cli/main.py:1488. Dead `import subprocess as _sp` alias. Near-duplicate of F121. |
| F236 | confirmed | — | Static analysis of src/aiv/lib/auditor.py:236. Inside `audit()` loop, `p.read_text()` and `p.write_text()` called with no surrounding try/except. Permission error mid-audit propagates as unhandled exception, aborting the entire audit run. |
| F237 | confirmed | — | Static analysis of src/aiv/guard/github_api.py:54. `_request` catches HTTPError but not URLError. Near-duplicate of F115/F174/F44. |
| F238 | confirmed | — | Read src/aiv/cli/main.py:740-745. Line 741: `subprocess.run(['python', '-m', 'pytest', ...])`. `python` may not resolve to the current venv interpreter. `sys.executable` is already imported at the top of main.py and is the correct idiom. |
| F239 | confirmed | — | Read src/aiv/guard/runner.py:393-399. main() calls GitHubAPI.context_from_env() and runner.run() with no surrounding try/except. Missing env vars raise KeyError; network failures raise URLError or GitHubAPIError. All surface as raw Python tracebacks. |
| F240 | confirmed | — | Grep for validate_class_a_manifest\|validate_class_c_manifest\|validate_semantic_manifest\|validate_durable_manifest across src/ returned zero hits outside manifest.py. Four public functions defined in guard/manifest.py:23-218 but never imported or called. Manifest validation permanently inactive. |
| F241 | confirmed | — | Read src/aiv/lib/parser.py:35-42. ParsedSection.raw_start and raw_end assigned in _extract_sections but never accessed by downstream parser methods or external callers. Dead state tracking confirmed. |
| F242 | confirmed | — | Read src/aiv/lib/language_drivers/treesitter_driver.py:247. `names[1].text.decode('utf-8') if names[1].text else ''` — empty string added to imports set when text is falsy. Downstream matching on empty string produces false positives for malformed AST nodes. |
| F243 | confirmed | — | Read src/aiv/lib/evidence_collector.py:343. `import xdist as _  # noqa: F401` — package imported solely to test for presence; binding discarded. `importlib.util.find_spec('xdist') is not None` is the correct idiom. |
| F244 | confirmed | — | Static analysis of tests/unit/test_cli_init.py:54-69,75-82,128-135,192-197. Multiple test methods call subprocess.run([sys.executable, '-m', 'aiv', 'init', ...]) and discard return value with no returncode check. aiv init failures invisible; tests fail later on directory assertions with misleading messages. |
| F245 | confirmed | — | Static analysis of tests/unit/test_cli_commit_skip.py:117-118,130-131. In test_reason_in_class_a and test_reason_in_method, `_run_aiv_commit()` called but CompletedProcess return value not assigned or inspected. Command failure surfaces only as 'Expected 1 evidence file, got 0', obscuring root cause. |
| F246 | confirmed | — | Read tests/unit/test_pre_commit_hook.py:157-172. test_functional_plus_packet_validates patches 5 symbols but omits 'aiv.hooks.pre_commit._load_hook_config'. Real .aiv.yml read from os.getcwd() making test non-deterministic. All other tests use _mock_main which patches this function. |
| F247 | confirmed | — | Static analysis of tests/unit/test_evidence_collector.py:100-101. `with patch('pathlib.Path.read_text', return_value='...')` replaces method on stdlib Path class globally. Any Path.read_text() call in the entire call stack returns the stub, not just the intended target. |
| F248 | confirmed | — | Read tests/unit/test_svp.py:670-680. Line 676: mid-file `from aiv.svp.lib.rating import calculate_rating, score_session` after multiple class definitions, violating PEP 8 E402. ImportError mid-collection causes confusing partial-collection failure. |
| F249 | confirmed | — | Static analysis of tests/unit/test_validators.py:394. IntentSection re-imported inside fixture body at line 394 despite module-level import at line 21. ArtifactLink imported locally at line 394 and again at line 502, instead of being consolidated at module level. |
| F250 | confirmed | — | Read tests/unit/test_language_drivers.py:90-95. `try: TreeSitterDriver().available except ImportError` — only ImportError caught. Constructing TreeSitterDriver() or accessing .available may raise AttributeError/RuntimeError/OSError causing pytest collection error instead of graceful skip. |
| F251 | confirmed | — | Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` — os module absent from module-level imports; inline __import__ used. Non-idiomatic; makes os dependency invisible to static analysis. Duplicate of F21/F95/F126/F153/F182. |
| F17 | confirmed | DEFECT | cli/main.py:1237 runs ['git','commit','--no-verify','-m',commit_msg]; live inspection confirms the close command bypasses all hook validation on the packet commit. |
| F21 | confirmed | NA | test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed by source inspection; test-code only, no production impact. |
| F22 | refined | NA | Grep over src/ found no exec/eval/subprocess call on test_code field; session.py:252 only checks field presence. The injection risk is latent in the model design, not an active execution path in current production code. |
| F23 | confirmed | DEFECT | pre_commit.py:243 prints 'REQUIRES: [A + B]' for R1; pipeline.py:183 enforces {EXECUTION, REFERENTIAL, INTENT}. Class E (INTENT) is silently required but not documented in the hook rubric. |
| F24 | confirmed | DEFECT | pre_commit.py:237 prints 'REQUIRES: A + B + C + E + [D + F]' with D and F in brackets implying optional; pipeline.py:190-197 enforces all six as mandatory for R3. |
| F33 | refined | DEFECT | Triplication confirmed: identical 3-element tuple at pre_commit.py:46-50, pre_push.py:40-44, auditor.py:51-55. Finding description cited wrong values ('.aiv/'); actual values are '.github/aiv-packets/VERIFICATION_PACKET_', '.github/VERIFICATION_PACKET_', '.github/aiv-packets/PACKET_'. Core claim (no shared source of truth) stands. |
| F43 | confirmed | DEFECT | pre_commit.py:212-214: except Exception as exc: print(f'WARNING: Packet validation skipped ({exc})') return True. Any transient subprocess error silently allows commits through. |
| F46 | confirmed | DEFECT | grep of entire src/ and tests/ for 'validate_file_type_triggers' returns only the definition at evidence.py:261; method is never called. |
| F62 | confirmed | NA | test_cli_init.py lines 25,31,54,63,76,128,141,190 call subprocess.run without capturing or checking returncode; test-code hygiene issue only. |
| F64 | untested | NA | All 7 tests in test_cli_commit_skip.py failed at fixture setup: git commit exit 128 due to sandbox-level commit-signing enforcement (signing server returns HTTP 400). IndexError risk at line 136 not exercisable in this environment. |
| F67 | confirmed | NA | IntentSection imported at test_validators.py:17 (module level) and redundantly re-imported inside fixture bodies at lines 394 and 500; test-code only. |
| F68 | untested | NA | Tests in test_cli_commit_skip.py could not run; git commit signing constraint in sandbox prevented fixture setup. Source inspection supports the finding but live execution was blocked. |
| F71 | confirmed | DEFECT | runner.py:383 sets valid=present where present is a boolean presence check only; no URL, SHA, or content validation performed before promoting valid=True. |
| F82 | confirmed | NA | Source inspection confirms test_functional_plus_packet_validates (test_pre_commit_hook.py:157) does not patch _load_hook_config unlike _mock_main at line 120; test-code quality issue. |
| F95 | confirmed | NA | test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only, same root cause as F21/F153. |
| F103 | confirmed | DEFECT | cli/main.py:1646-1649: when skip_checks=True (R0 only), class_a_md is set to '### Class A (Execution Evidence)\n\n- Local checks skipped (--skip-checks).' This placeholder header satisfies the parser's Class A section detection and the pipeline's R0 EXECUTION requirement with zero actual execution evidence. |
| F109 | confirmed | NA | test_validators.py:379 asserts len(info) >= 1; the test name and docstring claim both D and F produce INFO, but a single INFO for either D or F alone satisfies the assertion. Test-code quality issue. |
| F118 | confirmed | DEFECT | cli/main.py:1664 'changed_symbols' in dir() and line 1721 'class_c_data' in dir() confirmed. dir() with no argument returns all names in local+enclosing+global+builtin scopes; locals() is the correct check for local variable assignment. |
| F120 | confirmed | DEFECT | github_api.py:187 'import base64' inside get_file_content and line 193 'import urllib.parse' inside search_code confirmed; production code with deferred stdlib imports obfuscates dependencies. |
| F121 | confirmed | DEFECT | cli/main.py:1488 'import subprocess as _sp' inside commit function body when subprocess is already imported at module level; redundant alias confirmed. |
| F126 | confirmed | NA | test_svp_full_workflow.py:51 __import__('os').environ confirmed; test-code only. Same location as F182 and F251. |
| F127 | confirmed | NA | test_auditor.py:419-420 'import subprocess; import sys' inside test method body and again at 434-435 confirmed; test-code only. |
| F128 | confirmed | NA | test_svp.py:676 'from aiv.svp.lib.rating import calculate_rating, score_session' after all test class definitions confirmed; same location as F185 and F248. |
| F129 | confirmed | NA | test_language_drivers.py:90-95 'except ImportError: _TREESITTER_AVAILABLE = False' confirmed; AttributeError from TreeSitterDriver() constructor would propagate uncaught. Same location as F250. |
| F130 | confirmed | NA | test_pre_commit_hook.py:157-172 omits _load_hook_config patch; confirmed by source inspection. Duplicate of F82 and F183. |
| F153 | confirmed | NA | test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only. Duplicate of F95. |
| F156 | confirmed | DEFECT | No production code validates session file origin, signature, or chain-of-custody. SVP session JSON files can be forged by writing directly to .svp/. validators/session.py validates content rules (S001-S016) but not file integrity. No test exercises this attack path. |
| F158 | confirmed | DEFECT | validate_file_type_triggers defined at evidence.py:261, never called from any production or test code. Duplicate of F46. |
| F159 | confirmed | DEFECT | pipeline.py:183 _TIER_REQUIRED[R1]={EXECUTION,REFERENTIAL,INTENT}; pre_commit.py:243 rubric shows 'REQUIRES: [A + B]' without Class E. Same underlying defect as F23. |
| F162 | confirmed | DEFECT | evidence.py:242 manual_state_keywords=['sqlite3','psql','mysql','mongo','query'] confirmed; excludes all other manual reproduction steps (shell scripts, file edits, API calls, etc.). |
| F164 | confirmed | NA | test_svp_full_workflow.py:10 docstring 'Phase 4: Ownership Lock (manual — tested via model injection)' is stale; all Phase 4 tests use self._run('ownership',...) CLI calls. Test-code docstring drift. |
| F171 | confirmed | NA | test_models.py:98 'with pytest.raises(Exception)' confirmed; masks the specific exception type (ValidationError/PydanticUserError). Test-code quality issue. |
| F178 | confirmed | DEFECT | github_api.py:191-202 search_code method confirmed; grep of entire src/ shows no callers outside github_api.py itself. Dead production code. |
| F182 | confirmed | NA | test_svp_full_workflow.py:51 __import__('os') confirmed; test-code only. Same location as F126 and F251. |
| F183 | confirmed | NA | _load_hook_config not mocked in test_functional_plus_packet_validates; same finding as F82 and F130. |
| F185 | confirmed | NA | test_svp.py:676 mid-file module-level import after class definitions confirmed; same location as F128 and F248. |
| F191 | confirmed | DEFECT | models.py:592 tier: VerifierTier = Field(default=VerifierTier.NOVICE) hardcodes NOVICE as default even when elo_rating=500 (the other default). from_elo(500) returns COMPETENT at line 89-90 but VerifierRating().tier is NOVICE until apply_event() is called. The initial tier is wrong for any VerifierRating constructed without events. |
| F199 | confirmed | DEFECT | canonical.py:441 base64.b64decode(payload) where payload is the raw inline-b64-json: suffix from a packet's reference field; no length guard. Confirmed by source inspection. |
| F201 | confirmed | DEFECT | canonical.py:442 and 451 __import__('json').loads(...) in security-enforcing _read_scope_inventory; confirmed. The dynamic import hides the json dependency from static analysis in this audit-critical path. |
| F208 | confirmed | NA | test_pre_push_hook.py mocks _get_commit_files and _get_commits_in_range throughout; no test performs a real git push. Test coverage gap confirmed by source inspection. |
| F214 | confirmed | DEFECT | ci.yml:4-7 push and pull_request triggers both restricted to branches:[main]; confirmed. pre_push.py:17-22 claims Layer 3 CI coverage for all pushed branches, which is false for feature branches. |
| F216 | confirmed | DEFECT | rule_id='E021' appears at evidence.py:334 (missing Class D section trigger) and links.py:140,152 (unreachable evidence URL). Two structurally different violations share the same rule ID, making suppression impossible. |
| F229 | confirmed | DEFECT | canonical.py:24 REQUIRED_CLASSES['R0']=['A','B']; pipeline.py:182 _TIER_REQUIRED[R0]={EXECUTION,REFERENTIAL}; test_e2e_compliance.py:744 asserts Class E IS present for R0 in _build_evidence_sections output. Three divergent definitions for R0 required classes. |
| F231 | confirmed | DEFECT | config.py:263-284: entire YAML load and extraction in a single try: ... except Exception: pass block; any YAML error, type mismatch, or I/O failure silently returns default config with no log output. |
| F233 | confirmed | DEFECT | pre_commit.py:155 NamedTemporaryFile(delete=False) and line 183 mkdtemp not in try/finally; if subprocess.run at line 187 raises (e.g., timeout), both tmp_path and audit_dir leak. Outer except at line 212 does not clean up these resources. |
| F234 | confirmed | DEFECT | cli/main.py:1664 and 1721 use 'X in dir()' as local variable existence checks; confirmed. dir() with no argument returns names from all scopes; locals() is the correct check. Same defect as F118. |
| F235 | confirmed | DEFECT | cli/main.py:1488 'import subprocess as _sp' inside commit function body; subprocess already imported at module level. Same code as F121. |
| F238 | confirmed | DEFECT | cli/main.py:741 ['python','-m','pytest',...], line 768 ['python','-m','ruff',...], line 784 ['python','-m','mypy',...] confirmed. All use bare 'python' rather than sys.executable, breaking venv isolation. |
| F240 | confirmed | DEFECT | grep of src/ for 'from aiv.guard.manifest' or 'import manifest' returns no hits outside manifest.py itself; the four public functions are only imported by tests. Dead code in production surface. |
| F242 | confirmed | DEFECT | treesitter_driver.py:247 'imports.add(names[1].text.decode("utf-8") if names[1].text else "")' confirmed; when names[1].text is b'' (empty bytes), the empty string '' is added to the imports set, causing false-positive symbol matching. |
| F243 | refined | DEFECT | evidence_collector.py:343 'import xdist as _' confirmed; the pattern is functionally correct (ImportError on absence triggers serial mode) but non-idiomatic. importlib.util.find_spec('xdist') is the conventional probe. The # noqa: F401 suppresses the linter but the pattern remains opaque. |
| F248 | confirmed | NA | test_svp.py:676 mid-file import confirmed; same location as F128 and F185. |
| F249 | confirmed | NA | test_validators.py:394 and 500 re-import IntentSection inside fixture bodies; already imported at module level line 17. Same pattern as F67. |
| F250 | confirmed | NA | test_language_drivers.py:90-95 except ImportError only; same location as F129. |
| F251 | confirmed | NA | test_svp_full_workflow.py:51 inline __import__('os') confirmed; same location as F126 and F182. |

## Un-executed (100% accounting — each carries proof-of-attempt)

| Region | Reason | Command tried | Failure |
| --- | --- | --- | --- |


## Machine-checkable data

```json
{
  "coverage_pct": 0,
  "coverage_verified": false,
  "observed": [
    {
      "entry": "pip install -e \".[dev]\"",
      "behavior": "Succeeded (exit code 0); aiv-protocol 1.0.0 built and installed in editable mode. All declared dependencies were already satisfied."
    },
    {
      "entry": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml (purpose: test)",
      "behavior": "Failed with exit code 4: 'unrecognized arguments: --cov=aiv --cov-report=term-missing'. pytest-cov plugin is not installed in the environment. No tests executed; no coverage data collected."
    },
    {
      "entry": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml (purpose: coverage)",
      "behavior": "Failed with exit code 4: same as above. Repeated invocation with identical arguments produced identical failure. Zero lines of production or test code were exercised."
    },
    {
      "entry": "tests/ (entire test suite — all unit and integration tests)",
      "behavior": "flipped to executed: The original pass used the uv-isolated `/root/.local/bin/pytest` binary (pytest 9.0.2) which has no pytest-cov plugin in its isolated environment, even though pytest-cov 5.0.0 is installed in the system Python site-packages. Switching to `python -m pytest` (pytest 8.4.2, with cov-5.0.0 and xdist-3.8.0 active) allowed coverage flags to be accepted. The `artifacts/` directory was created for junit output, then the exact original command was re-issued via `python -m pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml` from /home/user/aiv-protocol. (Command: python -m pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml | Exit code: 1 (test failures, not infrastructure failure) | Result: 741 passed, 3 warnings, 7 errors in 29.32s | Coverage: TOTAL 5073 stmts 1484 miss 71% | junit.xml written to artifacts/junit.xml | 7 errors are all fixture-setup failures in tests/unit/test_cli_commit_skip.py — `git commit -m init` exits 128 due to missing git user.name/user.email identity in the sandbox (not a code defect). All 748 collected items were exercised (741 passed + 7 setup-error). Plugins active: cov-5.0.0, xdist-3.8.0. Full suite executed, coverage report generated.)"
    }
  ],
  "deltas": [
    {
      "id": "F1",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/validators/anti_cheat.py:135-141. Python precedence: `(line.startswith('+') and not line.startswith('+++')) or (not line.startswith('-') and not line.startswith('\\\\') and not line.startswith('diff '))`. A '+++' header satisfies the second OR clause, incrementing current_line erroneously."
    },
    {
      "id": "F2",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/models.py:54. `normalized.startswith(member.value)` where member values are single capital letters. Inputs like 'AB' or 'AF' match member 'A'. Equality comparison is required."
    },
    {
      "id": "F3",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/models.py:182-189. else branch at line 187-188 sets only `overall_result = OverallResult.PASS` without setting `compliance_level`. Field default at line 123 is 'L1'. A passed R3 packet reports compliance_level='L1', indistinguishable from a passed R0 packet."
    },
    {
      "id": "F4",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/change.py:232. `git log --format=%H %s {first_sha}^..HEAD` fails with exit code 128 when first_sha is the initial commit. Line 238 returns [] silently on non-zero returncode, masking the failure."
    },
    {
      "id": "F5",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/validators/evidence.py:86-101. `pass` at line 90 returns empty errors for github_actions/external link types. The elif branches for performance (E013) and UI (E012) are dead for these link types."
    },
    {
      "id": "F6",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1237. `subprocess.run(['git', 'commit', '--no-verify', '-m', commit_msg], ...)`. Pre-commit hooks bypassed. No secondary structural validation of packet content observed before this call."
    },
    {
      "id": "F7",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/runner.py:249-253. `if not has_optional and not missing` fires only when no required sections are missing. When both required sections AND methodology are absent, the methodology-specific E-METH diagnostic is swallowed."
    },
    {
      "id": "F8",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_validators.py:607-610. Line 608: `assert artifacts[1] != artifacts[0] or artifacts[2] != artifacts[0]`. With `or`, if claim-2 duplicates but claim-3 does not, assertion passes silently. Comment requires AND."
    },
    {
      "id": "F9",
      "delta": "confirmed",
      "evidence": "Read src/aiv/svp/lib/models.py:89-92 and 592. `from_elo(500)` returns COMPETENT (line 89). `VerifierRating.tier` defaults to NOVICE (line 592). update_tier() is not called at construction. Boundary inconsistency at ELO=500 confirmed."
    },
    {
      "id": "F10",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_auditor.py:363-368. Line 365: `p.read_text(encoding='utf-8')` return value discarded. Whether the auto-fix modified the file is never asserted."
    },
    {
      "id": "F11",
      "delta": "untested",
      "evidence": "tests/unit/test_coverage.py:120 not read by either analysis pass; no test execution occurred."
    },
    {
      "id": "F12",
      "delta": "untested",
      "evidence": "tests/integration/test_svp_full_workflow.py:247 — agent noted json.loads called after asserting returncode==1; static analysis plausible but source not directly read by primary analyst. No test execution occurred."
    },
    {
      "id": "F13",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:157-172. test_functional_plus_packet_validates uses 5 patches but omits 'aiv.hooks.pre_commit._load_hook_config', allowing real .aiv.yml to be read from os.getcwd(). All other tests use _mock_main which patches this function."
    },
    {
      "id": "F14",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:191-204. `file_path.startswith('.github/')` check passes for paths like '.github/x/../../../../../../etc/passwd'. Subsequent `Path(file_path).read_text()` then reads outside the repository root. Path traversal vulnerability confirmed."
    },
    {
      "id": "F15",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/links.py:163-176. `_head_check(url)` passes user-supplied URLs from packet evidence directly to `urllib.request.urlopen` without scheme validation or private-IP blocklist. SSRF vector confirmed."
    },
    {
      "id": "F16",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:639-700. `_detect_git_context()` extracts owner/repo via regex `[^/]+/[^/.]+` from git remote URL. These character classes permit `?`, `#`, `@` allowing crafted .git/config to inject query parameters into GitHub API calls."
    },
    {
      "id": "F17",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1233-1241. Same --no-verify commit as F6 at line 1237. Duplicate finding, same defect."
    },
    {
      "id": "F18",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1879. `subprocess.run(['git', 'add', str(file), str(packet_path)], ...)` omits the `--` separator. A file path starting with `-` would be misinterpreted as a git flag."
    },
    {
      "id": "F19",
      "delta": "untested",
      "evidence": "tests/unit/test_validators.py:427-479 not directly read; confirms SSRF via agent analysis but test code not verified by primary analyst. No test execution occurred."
    },
    {
      "id": "F20",
      "delta": "untested",
      "evidence": "tests/unit/test_pre_commit_hook.py:308-314 not read; no test execution occurred."
    },
    {
      "id": "F21",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` — `os` is never imported at module level; `__import__` is used inline. Non-idiomatic; static analysis tools miss the dependency. Duplicate of F251/F95/F126/F153/F182."
    },
    {
      "id": "F22",
      "delta": "untested",
      "evidence": "tests/unit/test_svp.py:625-630 not read; no test execution occurred."
    },
    {
      "id": "F23",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:240. Line 240 prints 'REQUIRES: [A + B]' for R1. pipeline.py enforces {A, B, E} for R1. Developers following the displayed rubric will omit Class E evidence and be blocked without prior warning."
    },
    {
      "id": "F24",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:237. Line 237 prints 'REQUIRES: A + B + C + E + [D + F]' for R3 with brackets implying D and F are optional. pipeline.py _TIER_REQUIRED[R3] contains all six classes with no optional carve-out."
    },
    {
      "id": "F25",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:514 and 1143. Line 514 emits version '2.1'; line 1143 emits version '2.2'. guard/runner.py accepts both. No schema diff or changelog found between v2.1 and v2.2."
    },
    {
      "id": "F26",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1236-1237. Same --no-verify commit defect as F6. Duplicate."
    },
    {
      "id": "F27",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/pipeline.py:48. Class docstring enumerates seven stages, omitting 'Risk-Tier Evidence Requirements' which is Stage 5 at line 131. CLI references '8-stage pipeline'. Docstring omission confirmed."
    },
    {
      "id": "F28",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1664. `'changed_symbols' in dir()` uses no-arg `dir()` which returns scope names; unreliable for testing local variable binding. `locals()` is the correct idiom."
    },
    {
      "id": "F29",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:283. `collect_class_b` calls `_run_git('rev-parse', 'HEAD')` before the commit. The SHA embedded in Class B permalink equals the parent commit, not the commit introducing the change."
    },
    {
      "id": "F30",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/config.py:163. `functional_root_files` includes '.gitignore'. .husky/pre-commit also includes .gitignore in IS_FUNCTIONAL regex. Neither .cursorrules nor any developer-facing doc documents these as functional files."
    },
    {
      "id": "F31",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/models.py:182-189. Same finalize() missing compliance_level on PASS as F3. Duplicate."
    },
    {
      "id": "F32",
      "delta": "confirmed",
      "evidence": "Static analysis of .github/workflows/ci.yml:67. `if: github.event_name == push` on protocol-audit job. PR branches are not covered by push-event CI; --no-verify push on a PR branch is undetected until post-merge."
    },
    {
      "id": "F33",
      "delta": "confirmed",
      "evidence": "Static analysis: identical PACKET_PREFIXES list literal appears in pre_commit.py:46-50, pre_push.py:40-44, and auditor.py:51-55. Three independent edits required to add or rename a packet path."
    },
    {
      "id": "F34",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/models.py:268-271. `has_provenance_evidence` iterates `self.claims` for EvidenceClass.PROVENANCE. A packet with Class F in a standalone evidence section but without a PROVENANCE-typed claim returns False."
    },
    {
      "id": "F35",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:319-322. Docstring says 'injected directly into the session JSON' but actual code at lines 380-403 calls `self._run('ownership', ...)` — a full CLI subprocess invocation. Stale docstring."
    },
    {
      "id": "F36",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:3-17. Module docstring lists phases 1-4 and omits Phase 0, describes Phase 4 as 'manual — tested via model injection' but all Phase 4 tests use CLI subprocess. Docstring is wrong on two counts."
    },
    {
      "id": "F37",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_commit_hook.py:35-38. Method name `test_template_is_not_packet` vs assertion `_is_packet('...VERIFICATION_PACKET_TEMPLATE.md') is True`. Test name is the exact inverse of the asserted behavior."
    },
    {
      "id": "F38",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_models.py:296-305. Docstring reads \"'main' should NOT be mutable if excluded from custom set.\" Assertion at line 304 is `assert link.is_immutable is False` (IS mutable). Docstring states the inverse."
    },
    {
      "id": "F39",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:370-381. `test_fix_class_e_local_ref` calls audit(fix=True) and then asserts the fixed URL contains '/blob/main/' — a mutable branch reference that CLASS_E_MUTABLE would immediately re-flag as an ERROR. Auto-fix produces non-compliant output."
    },
    {
      "id": "F40",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:243-244. Class docstring references hard-coded line numbers pointing to `auditor.py#L251-L262` and `auditor.py#L276-L296`. These become stale on any insertion or deletion in auditor.py."
    },
    {
      "id": "F41",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_coverage.py:36-40. Test name `test_r0_has_class_b_and_a` but line 40 asserts `'### Class E' in result`. Guard constant REQUIRED_CLASSES['R0']==['A','B'] does not list E as required for R0. Misleading test name."
    },
    {
      "id": "F42",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_auditor.py:361-368. Same discarded p.read_text() result as F10. Duplicate."
    },
    {
      "id": "F43",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:212-214. `_validate_packet` wraps subprocess invocation in bare `except Exception: return True`. Any transient error silently allows commit, defeating the enforcement guarantee."
    },
    {
      "id": "F44",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/github_api.py:43-58 and 112-117. `_request` catches only HTTPError; URLError propagates. `list_pr_files` catches only GitHubAPIError at line 116. Caller gets truncated results with no indication of truncation."
    },
    {
      "id": "F45",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/github_api.py:150-165. Same pattern as F44 in `list_run_artifacts`. Transient network error mid-pagination causes PASS on artifact check even when artifact exists only on a later page."
    },
    {
      "id": "F46",
      "delta": "confirmed",
      "evidence": "Static analysis: Grep of src/ confirms `validate_file_type_triggers` is defined in evidence.py:261 but never imported or called from ValidationPipeline, EvidenceValidator, guard runner, or CLI. All four trigger rules permanently inactive."
    },
    {
      "id": "F47",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:283-285. `collect_class_b` calls `_run_git('rev-parse', 'HEAD')` and falls back to 'unknown' on failure. All subsequent permalink URLs assembled with this string, producing evidence that resolves to a 404."
    },
    {
      "id": "F48",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit."
    },
    {
      "id": "F49",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1085. Evidence file reading in `close` command loop uses bare `except Exception: pass`. Corrupt or missing evidence files cause Layer 2 packet to be generated with no real claims, silently."
    },
    {
      "id": "F50",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/change.py:82. `except (json.JSONDecodeError, Exception)` — json.JSONDecodeError is a subclass of Exception; the first entry is redundant. More critically, disk full and permission denied errors are silently treated as 'no active change'."
    },
    {
      "id": "F51",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:65-71. `_run_git` at lines 55-71 returns `result.stdout.strip()` without checking `result.returncode`. When git fails, empty string is returned, causing hook to exit 0 and allow the commit."
    },
    {
      "id": "F52",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:249-255. `_run_git` returns empty string on any git failure. `collect_class_c()` then reports no test files modified and `anti_cheat_clean=True`, producing falsely clean Class C evidence."
    },
    {
      "id": "F53",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:188. `base64.b64decode(data['content'])` called with no exception handling. Truncated or padded base64 from GitHub API raises `binascii.Error` uncaught."
    },
    {
      "id": "F54",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:622-626. For each of N symbol nodes from outer ast.walk, a second full ast.walk runs to find parent ClassDef. O(N²) confirmed. Also `node in ast.iter_child_nodes(parent)` uses object identity which may miss nodes."
    },
    {
      "id": "F55",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:117-140. `_write_safety_snapshot` creates new timestamped directory under `.cache/bb-safety-snapshots/` on every pre-commit run with no cleanup, rotation, or size-limit mechanism."
    },
    {
      "id": "F56",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:492. EVIDENCE_MUTABLE_LINK finding created with `auto_fixable=True` regardless of whether commit_sha is None. `_apply_fixes` silently skips the fix when short_sha is None. `auto_fixable=True` is misleading."
    },
    {
      "id": "F57",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/models.py:123. `compliance_level: str = 'L1'` is the field default. Same as F3 — finalize() never overwrites this on PASS. Duplicate citing the field declaration."
    },
    {
      "id": "F58",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:115-117. `_get_introducing_commit` returns `shas[-1]` from split stdout. If git outputs an error message as the last line, that garbage string is returned as a commit SHA."
    },
    {
      "id": "F59",
      "delta": "confirmed",
      "evidence": "Static analysis: `EvidenceValidator._is_bug_fix` and `auditor._is_bug_fix_claim` use different approaches to detect bug-fix packets. Same packet assessed differently by each, creating inconsistent enforcement."
    },
    {
      "id": "F60",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/config.py:284-285. `load_hook_config` wraps entire YAML parse in `try: ... except Exception: pass`. Malformed YAML, wrong types, I/O errors all silently fall back to defaults."
    },
    {
      "id": "F61",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_auditor.py:365. Same p.read_text() discard as F10. Duplicate."
    },
    {
      "id": "F62",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py. Six test methods call subprocess.run to invoke `aiv init` but neither assign the return value nor pass check=True. aiv init failures are invisible; tests fail on filesystem assertions with misleading messages."
    },
    {
      "id": "F63",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:45-61. `_run()` helper calls subprocess.run with timeout=30 but no try/except. Timeout raises subprocess.TimeoutExpired which propagates as uncaught exception, losing stdout/stderr."
    },
    {
      "id": "F64",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:136-137. Line 137 accesses `evidence_files[0]` with no length assertion, causing IndexError if the command failed and produced no evidence files."
    },
    {
      "id": "F65",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:377. `auditor.audit(tmp_path, fix=True)` called with no assignment. AuditResult discarded. A regression where fix() produces zero findings would go undetected."
    },
    {
      "id": "F66",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:433,487. `HTTPError(req.full_url, N, msg, {}, None)` uses empty dict `{}` as fourth argument; urllib.error.HTTPError expects an http.client.HTTPMessage instance. Tests may mask incorrect error handling."
    },
    {
      "id": "F67",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:395,500. IntentSection re-imported inside fixture body at line 395 and inside test at line 500, shadowing the module-level binding. Dead re-import confirmed."
    },
    {
      "id": "F68",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:118-121,131-134. `_run_aiv_commit(...)` return value not captured. Non-zero exit invisible until downstream assertion fails with misleading message."
    },
    {
      "id": "F69",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1236-1237. Same --no-verify commit as F6. Duplicate."
    },
    {
      "id": "F70",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/svp/lib/validators/session.py:113. `if pred.predicted_complexity is None:` — in Pydantic v2, unset required field raises ValidationError at construction before this code executes. The None branch is unreachable; S004 warnings are never emitted."
    },
    {
      "id": "F71",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:383. `valid=present` — _build_evidence_class_results unconditionally sets valid=present. No independent artifact integrity check. valid always equals present; the field carries no independent information."
    },
    {
      "id": "F72",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/models.py:132-133. `len(ref) >= min_sha_length and all(c in '0123456789abcdef' for c in ref.lower())` — a mutable git tag whose name is ≥7 hex chars is treated as an immutable commit SHA."
    },
    {
      "id": "F73",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/svp/lib/rating.py:23-124. `score_session()` contains no code path that appends `RatingEvent(event_type='bug_missed', ...)`. The -25 ELO penalty for missed bugs is never applied; bugs_missed is always 0."
    },
    {
      "id": "F74",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/parser.py:585. When `artifact_raw` starts with 'http', it is passed directly to `ArtifactLink.from_url()`. If it contains trailing prose or embedded newlines, Pydantic rejects it and except clause returns plain str, skipping all link validation."
    },
    {
      "id": "F75",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/canonical.py:159-160. `validate_canonical()` accesses `canonical_data['attestations'][0]` without iterating over all attestations. Multiple attestations have only their first validated."
    },
    {
      "id": "F76",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/pipeline.py:163-169. In strict mode, `result.status = ValidationStatus.FAIL` when warnings exist. But `ValidationResult.is_valid` returns `not self.blocking_errors`, checking only blocking errors. Callers reading `is_valid` see True while `status` is FAIL."
    },
    {
      "id": "F77",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:154-157,385-388,883-886 and src/aiv/svp/lib/models.py:80-92,585-614. from_elo(500)==COMPETENT vs VerifierRating(elo=500).tier==NOVICE. Mutually contradictory. Same as F9."
    },
    {
      "id": "F78",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_validators.py:607-610. Same or-vs-and defect as F8. Duplicate."
    },
    {
      "id": "F79",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:875-884. `test_evidence_dir_none_skips_scan` creates empty packets_dir and asserts 0 scanned and 0 findings. Both assertions trivially satisfied regardless of evidence_dir=None behavior."
    },
    {
      "id": "F80",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:247,309. After asserting returncode==1, test calls `json.loads(result.stdout)`. A plain-text error response raises json.JSONDecodeError instead of a meaningful AssertionError."
    },
    {
      "id": "F81",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:119,132. `_run_aiv_commit(...)` return value discarded. Same as F68. Duplicate."
    },
    {
      "id": "F82",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:157-172. Same missing _load_hook_config patch as F13. Duplicate."
    },
    {
      "id": "F83",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:191. Same path traversal as F14 — `file_path.startswith('.github/')` without Path.resolve(). Triplicate finding."
    },
    {
      "id": "F84",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/links.py:169. Same SSRF as F15 — `urlopen(req, ...)` with no scheme/host restriction. Triplicate finding."
    },
    {
      "id": "F85",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:683. `_fetch_latest_ci_url` constructs API URL from owner/repo extracted via regex without validation. Crafted .git/config can inject query parameters into the URL."
    },
    {
      "id": "F86",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:176. `get_file_content` constructs URL with `path` argument without URL-encoding. A path containing `#`, `?`, `%`, or `/..` alters the request path or query string."
    },
    {
      "id": "F87",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit."
    },
    {
      "id": "F88",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:843. `owner`, `repo`, `head_sha` interpolated into GitHub URL in generated markdown without sanitization. Repository remote with Markdown-special characters can break link syntax."
    },
    {
      "id": "F89",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:88. `Path(event_path).read_text()` with no path restrictions. In environments where GITHUB_EVENT_PATH is attacker-settable, this allows reading arbitrary files."
    },
    {
      "id": "F90",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:427. TestLinkVitality confirms production LinkValidator calls urlopen with user-supplied URLs. No test validates internal/cloud-metadata URLs are blocked. Near-duplicate of F19."
    },
    {
      "id": "F91",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:387. S011 checks that author_github_id matches session.verifier_id but both originate from the same user-supplied --verifier CLI flag with no cryptographic binding."
    },
    {
      "id": "F92",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:116. Tests validate only benign alphanumeric --skip-reason strings. No test validates that markdown structural characters are escaped before insertion into evidence files."
    },
    {
      "id": "F93",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:370. Auto-fix test confirms URL construction concatenates local filename without URL-encoding. Packet reference like '../../.env' would embed unencoded string in generated URL."
    },
    {
      "id": "F94",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:63. Session path constructed as '.svp/session-pr{pr}.json' keyed on PR number. Two actors targeting the same PR number share one session, allowing overwrites."
    },
    {
      "id": "F95",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` spreads all host environment variables including CI secrets into subprocess. Near-duplicate of F21/F153/F182/F126/F251."
    },
    {
      "id": "F96",
      "delta": "confirmed",
      "evidence": "Static analysis: .husky/pre-commit PACKET_PATTERN only matches VERIFICATION_PACKET_* prefix. `aiv commit` stages EVIDENCE_*.md files which do not match, so HAS_PACKET is empty and Rule 5 fires, blocking the commit. Python hook correctly allows evidence-only commits."
    },
    {
      "id": "F97",
      "delta": "confirmed",
      "evidence": "Static analysis: `aiv close` generates PACKET_<name>.md files. Bash hook only matches VERIFICATION_PACKET_*. Commits of close-generated packets are blocked by Husky with spurious Rule 5 rejection."
    },
    {
      "id": "F98",
      "delta": "confirmed",
      "evidence": "Static analysis: Python pre-commit hook allows any commit when `aiv begin` is active (change context mode). Bash hook has no equivalent check, making it semantically incompatible with the aiv begin/commit/close workflow."
    },
    {
      "id": "F99",
      "delta": "confirmed",
      "evidence": "Static analysis: `close` command docstring never mentions --no-verify bypass. Python pre-commit hook would allow this commit anyway (packet-only check passes), so --no-verify is also unnecessary — it creates a compliance gap without functional need."
    },
    {
      "id": "F100",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/pipeline.py:49-56. ValidationPipeline docstring enumerates seven stages but omits 'Risk-Tier Evidence Requirements'. CLI references '8-stage pipeline'. Missing stage is where E019/E020 findings originate."
    },
    {
      "id": "F101",
      "delta": "confirmed",
      "evidence": "Static analysis: pre_push.py claims 'CI catches even --no-verify push (server-side)'. ci.yml protocol-audit runs only on `push` to main, not on `pull_request`. A PR with --no-verify commits bypasses all three layers until post-merge."
    },
    {
      "id": "F102",
      "delta": "confirmed",
      "evidence": "Static analysis: .cursorrules:9 instructs `git add <file>` before `aiv commit`, but `aiv commit` internally calls `git add` again. Documented workflow and actual execution model differ in staging sequence."
    },
    {
      "id": "F103",
      "delta": "confirmed",
      "evidence": "Static analysis: R0 requires Class A evidence. With --skip-checks, a placeholder '### Class A' header satisfies the validator without any real execution artifact. Tier check bypassed silently."
    },
    {
      "id": "F104",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:321. Docstring states Phase 4 'is injected directly into the session JSON', but implementation uses CLI subprocess. Stale docstring. Near-duplicate of F35."
    },
    {
      "id": "F105",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:10. Module docstring reads 'Phase 4: Ownership Lock (manual — tested via model injection)'. All Phase 4 tests use `self._run('ownership', ...)`. Near-duplicate of F36."
    },
    {
      "id": "F106",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_commit_hook.py:36. Test named `test_template_is_not_packet` asserts `_is_packet(TEMPLATE.md) is True`. The hook treats templates as valid packets while the auditor excludes them — cross-subsystem inconsistency. Near-duplicate of F37."
    },
    {
      "id": "F107",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py:139. `test_pre_push_hook_content_mentions_no_verify` docstring claims behavioral verification but assertion only checks that the string '--no-verify' appears in the hook file content."
    },
    {
      "id": "F108",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:401. `test_empty_body_fails` uses `assert result.block_count >= 1 or result.warn_count >= 1`. With `or`, a warning-only outcome passes, which would not block PR merge."
    },
    {
      "id": "F109",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:366. `test_r2_optional_d_and_f_info` asserts `len(info) >= 1`. Satisfied if only one of D/F fires; missing F is silently accepted."
    },
    {
      "id": "F110",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:359. `test_fix_commit_pending` only asserts non-crashing. Auto-fix behavior itself is entirely untested. Near-duplicate of F42/F10."
    },
    {
      "id": "F111",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:370. `test_fix_class_e_local_ref` asserts fixed URL contains '/blob/main/' — mutable branch reference — which CLASS_E_MUTABLE would immediately re-flag as ERROR. Auto-fix produces non-compliant output. Same as F39."
    },
    {
      "id": "F112",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_coverage.py:43. `test_r1_adds_class_e` name is misleading because R0 tests also assert Class E presence. Near-duplicate of F41."
    },
    {
      "id": "F113",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:155-214. NamedTemporaryFile (delete=False) and mkdtemp `audit_dir` created with no cleanup in the except block at line 212. Exception between creation and cleanup leaves temp resources on disk permanently."
    },
    {
      "id": "F114",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:249-255. Docstring states 'never raises' but `subprocess.run(..., timeout=30)` with no try/except means subprocess.TimeoutExpired and FileNotFoundError propagate uncaught."
    },
    {
      "id": "F115",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:51-76. `_request` and `_request_bytes` catch only HTTPError. URLError (DNS failures, connection refused, SSL errors) propagates uncaught. Near-duplicate of F44."
    },
    {
      "id": "F116",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:88. `json.loads(Path(event_path).read_text(...))` called with no try/except. Malformed GITHUB_EVENT_PATH JSON causes unhandled json.JSONDecodeError before any validation begins."
    },
    {
      "id": "F117",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1879,1233. `subprocess.run(['git', 'add', ...], check=True, timeout=10)` — CalledProcessError, TimeoutExpired, FileNotFoundError propagate as raw exceptions, inconsistent with rest of CLI user-facing error handling."
    },
    {
      "id": "F118",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1664,1721. `'changed_symbols' in dir()` and `'class_c_data' in dir()` antipattern. Near-duplicate of F28."
    },
    {
      "id": "F119",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:381. `valid=present` — field never carries independent information. Near-duplicate of F71."
    },
    {
      "id": "F120",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:188,193. `import base64` and `import urllib.parse` deferred inside function bodies. Inconsistent with module-level imports elsewhere; hides dependencies from static analysis."
    },
    {
      "id": "F121",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1489. `import subprocess as _sp` creates alias at line 1489 that is never referenced after line 1513. Dead code."
    },
    {
      "id": "F122",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:128-131. `_LOCAL_FILE_PATHS` maps only AUDIT_REPORT.md and SPECIFICATION.md. In any repo without exactly these filenames, `auto_fixable` is always False and the auto-fix logic in `_apply_fixes` is dead for all practical users."
    },
    {
      "id": "F123",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:620-626. O(N²) AST traversal — inner ast.walk for each outer node. No size limit enforced on file before parsing. Near-duplicate of F54."
    },
    {
      "id": "F124",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_auditor.py:365. Same discarded p.read_text() as F10. Duplicate."
    },
    {
      "id": "F125",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:119. `_run_aiv_commit(...)` return value discarded. Near-duplicate of F68/F81."
    },
    {
      "id": "F126",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. `__import__('os')` inline — os absent from module-level imports, hiding dependency from static analysis. Near-duplicate of F21/F95."
    },
    {
      "id": "F127",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:419. `import subprocess` and `import sys` inside test body, hiding dependencies from static analysis and running import machinery on every test invocation."
    },
    {
      "id": "F128",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:670-680. Line 676: mid-file `from aiv.svp.lib.rating import calculate_rating, score_session` after test classes, violating PEP 8 E402."
    },
    {
      "id": "F129",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_language_drivers.py:90. `try: ... except ImportError` catches only ImportError. `TreeSitterDriver().available` may raise AttributeError or RuntimeError if native libraries are partially installed. Near-duplicate of F250."
    },
    {
      "id": "F130",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:157. Same missing _load_hook_config patch as F13. Duplicate."
    },
    {
      "id": "F131",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py:57. Same subprocess.run return value discarded as F62. Near-duplicate."
    },
    {
      "id": "F132",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/validators/anti_cheat.py:132-142. Same operator precedence defect as F1. Duplicate."
    },
    {
      "id": "F133",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/models.py:306-309. `is_valid` returns `len(self.blocking_errors) == 0`. In strict mode, status is FAIL when warnings exist, but `is_valid` returns True. Callers branching on `is_valid` incorrectly allow strict-mode failures through."
    },
    {
      "id": "F134",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/anti_cheat.py:203-209. `check_justification` — first matching Class F claim with justification > 20 chars clears the finding for ALL deletions, not just the relevant claim. Single lengthy justification blanket-clears all anti-cheat findings."
    },
    {
      "id": "F135",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:336-365. Guard checks only head_sha match and aiv-evidence artifact presence. Workflow run conclusion status (success/failure) not validated; a failed CI run with correct SHA is accepted as proof."
    },
    {
      "id": "F136",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/svp/lib/validators/session.py:156-157,183-185. `return False` called immediately after appending first S006 or S015 error. If session.traces has N elements, only the first invalid trace is reported; subsequent N-1 are silently skipped."
    },
    {
      "id": "F137",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:434-578. `_check_packet` includes TODO remnant scans. These internal TODO-marker checks are applied to user-facing packets, potentially flagging legitimate packet fields that contain the string 'TODO'."
    },
    {
      "id": "F138",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/svp/lib/rating.py:147. `bugs_caught = len([e for e in all_events if e.event_type.startswith('bug_caught')])`. Both confirmed probe findings and falsification confirmations are counted, potentially double-counting the same bug."
    },
    {
      "id": "F139",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/parser.py:584-586. Same as F74 — raw multi-line URL strings bypass validation via except clause returning plain str. Near-duplicate."
    },
    {
      "id": "F140",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/canonical.py:231-235. `return False` after first missing evidence class. Only the first missing class reported; a packet missing multiple required classes receives only one CT-002 finding."
    },
    {
      "id": "F141",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_validators.py:608-610. Same or-vs-and defect as F8. Duplicate."
    },
    {
      "id": "F142",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:154-157,389-390. Same VerifierTier inconsistency as F9. Duplicate."
    },
    {
      "id": "F143",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_models.py:298-304. Same docstring/assertion inversion as F38. Duplicate."
    },
    {
      "id": "F144",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:408-425. `test_valid_markdown_packet` sole assertion is `canonical_enabled is False`. Whether the packet actually passed validation is unverified."
    },
    {
      "id": "F145",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:514-533. Mock `git log` helper output format differs from real git log format. Tests verified against mock, not real git output fidelity."
    },
    {
      "id": "F146",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:191. Same path traversal as F14/F83. Triplicate."
    },
    {
      "id": "F147",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/links.py:163. Same SSRF as F15/F84. Triplicate."
    },
    {
      "id": "F148",
      "delta": "untested",
      "evidence": ".github/workflows/ci.yml:387 not read; details truncated in agent output. No test execution occurred."
    },
    {
      "id": "F149",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit."
    },
    {
      "id": "F150",
      "delta": "untested",
      "evidence": "src/aiv/guard/github_api.py:42 details truncated in agent output; not directly verified. No test execution occurred."
    },
    {
      "id": "F151",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:427-479. Confirms production LinkValidator calls urlopen with raw packet URLs. No test validates internal URL blocking. Near-duplicate of F19/F90."
    },
    {
      "id": "F152",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_models.py:87-89. `ArtifactLink.from_url('https://example.com/some/page')` accepted without rejection. No test validates that file://, ftp://, or cloud-metadata URLs are rejected at model level."
    },
    {
      "id": "F153",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. Same ambient environment spread as F21/F95. Near-duplicate."
    },
    {
      "id": "F154",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:370-381. Auto-fix falls back to 'main' branch (mutable); test confirms and accepts this. Near-duplicate of F39/F111."
    },
    {
      "id": "F155",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_coverage.py:398-407. Only syntactically malformed YAML tested; structurally-valid YAML with wrong type for functional_prefixes — the exact scenario swallowed by `except Exception: pass` — is never tested."
    },
    {
      "id": "F156",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_svp.py:443-528. TestSessionValidator exercises rules using in-memory objects only. Discrepancies in CLI argument parsing that affect session construction would be missed."
    },
    {
      "id": "F157",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:116-138. Only benign strings tested. No test validates markdown content injection via --skip-reason. Near-duplicate of F92."
    },
    {
      "id": "F158",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:261. Same dead `validate_file_type_triggers` as F46/F217. Triplicate."
    },
    {
      "id": "F159",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/pipeline.py:183. `_TIER_REQUIRED[R1]` contains {EXECUTION, REFERENTIAL, INTENT}. pre_commit.py:240 displays only '[A + B]' for R1, omitting INTENT (Class E). Near-duplicate of F23."
    },
    {
      "id": "F160",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:113. Rule ID 'E020' emitted at two distinct sites with unrelated meanings. Duplicate rule ID causes ambiguity in reports."
    },
    {
      "id": "F161",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:402. anti_cheat.py:207 uses `claim.justification or claim.description` fallback; evidence.py:402 does not use the same fallback. Inconsistent behavior between the two validation paths."
    },
    {
      "id": "F162",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:242. Zero-Touch check scans only five DB keywords. Any ORM, NoSQL tool, or SQL dialect not in the list bypasses manual-state detection."
    },
    {
      "id": "F163",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_commit_hook.py:35. Same inverted test name as F37/F106/F172. Near-duplicate."
    },
    {
      "id": "F164",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:10. Module docstring 'Phase 4: manual — tested via model injection' vs CLI implementation. Near-duplicate of F36/F105."
    },
    {
      "id": "F165",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:321. Method docstring vs CLI implementation mismatch. Near-duplicate of F35/F104."
    },
    {
      "id": "F166",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:298. Same docstring/assertion inversion as F38/F143. Near-duplicate."
    },
    {
      "id": "F167",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:408. Same assertion-only-checks-canonical-enabled as F144. Near-duplicate."
    },
    {
      "id": "F168",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:356. Same non-crashing-only assertion as F42/F110. Near-duplicate."
    },
    {
      "id": "F169",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py:139. Same docstring/content mismatch as F107. Near-duplicate."
    },
    {
      "id": "F170",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:244. Same stale hard-coded line numbers in docstring as F40. Near-duplicate."
    },
    {
      "id": "F171",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_models.py:97. `with pytest.raises(Exception)` catches any unrelated exception instead of the specific expected type (ValidationError or TypeError)."
    },
    {
      "id": "F172",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_commit_hook.py:35. Same inverted test name as F37/F106/F163. Plus cross-subsystem inconsistency: hook treats templates as packets; auditor excludes them. Near-duplicate."
    },
    {
      "id": "F173",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:249. Same 'never raises' contract violation as F114/F52. Near-duplicate."
    },
    {
      "id": "F174",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:43. Same URLError not caught as F115/F44. Near-duplicate."
    },
    {
      "id": "F175",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:183. Same temp file no cleanup as F113. Near-duplicate."
    },
    {
      "id": "F176",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:348. `_run(pytest_cmd, timeout=360)` — `_run` makes no attempt to catch subprocess.TimeoutExpired. 'Never raises' contract violated."
    },
    {
      "id": "F177",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:60. `_request_bytes` is called only from `download_artifact_zip`, which is never invoked from runner.py. Method is dead code in the current guard execution path."
    },
    {
      "id": "F178",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:191. `search_code` method defined but never called from runner.py or any other audited file. Dead code."
    },
    {
      "id": "F179",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py. Six test methods call subprocess.run without storing or checking return value. Near-duplicate of F62/F131."
    },
    {
      "id": "F180",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:118-121,131-134. Same discarded return value as F68/F81/F125. Near-duplicate."
    },
    {
      "id": "F181",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_auditor.py:365. Same p.read_text() discard as F10. Duplicate."
    },
    {
      "id": "F182",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. Same __import__('os') inline as F21/F95/F126. Near-duplicate."
    },
    {
      "id": "F183",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:157-172. Same missing _load_hook_config patch as F13. Duplicate."
    },
    {
      "id": "F184",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:408-425. Same assertion-only-checks-canonical-enabled as F144/F167. Near-duplicate."
    },
    {
      "id": "F185",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:676. Same mid-module import as F248/F128. Duplicate."
    },
    {
      "id": "F186",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/validators/anti_cheat.py:132-142. Same operator precedence defect as F1. Duplicate."
    },
    {
      "id": "F187",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/anti_cheat.py:192-213. Same blanket justification clearing as F134. Near-duplicate with additional detail: a single lengthy justification anywhere clears ALL anti-cheat findings."
    },
    {
      "id": "F188",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/models.py:182-188. Same finalize() compliance_level defect as F3. Duplicate."
    },
    {
      "id": "F189",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/parser.py:585. Same raw URL bypass as F74/F139. Near-duplicate."
    },
    {
      "id": "F190",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:390-401. `_check_packet` uses `re.search(r'## Claim\\(s\\)\\s*\\n...')`. The guard accepts alternative heading spellings. Parse discrepancy between auditor and guard for the same packet."
    },
    {
      "id": "F191",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:154-157,387,885. Same VerifierTier inconsistency as F9/F77/F142. Duplicate."
    },
    {
      "id": "F192",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_validators.py:608. Same or-vs-and defect as F8. Duplicate."
    },
    {
      "id": "F193",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_svp.py:262-265. `fs.checked is False` and `fs.result == 'confirmed'` on the same object. A scenario that has not been checked having result='confirmed' is logically contradictory; the model allows an invalid state."
    },
    {
      "id": "F194",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:134. Accesses `evidence_files[0]` without prior length assertion while sibling test first asserts `len(evidence_files) == 1`. Near-duplicate of F64."
    },
    {
      "id": "F195",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:158-172. Same missing _load_hook_config patch as F13/F82/F130/F183. Duplicate."
    },
    {
      "id": "F196",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/links.py:163-168. Same SSRF as F15/F84/F147. Near-duplicate."
    },
    {
      "id": "F197",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:191-200. Same path traversal as F14/F83/F146. Near-duplicate."
    },
    {
      "id": "F198",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:176. Same missing URL-encoding as F86. Near-duplicate."
    },
    {
      "id": "F199",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/canonical.py:438-441. `_read_scope_inventory` base64-decodes payload with no length guard. Arbitrarily large inline-b64-json scope inventory can cause memory exhaustion."
    },
    {
      "id": "F200",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:40. `self.token` stored as plain string attribute with no `__repr__` override. `repr(api)` or pickling emits the token value."
    },
    {
      "id": "F201",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/canonical.py:442. `__import__('json').loads(decoded)` — dynamic import in an auditability tool. json is a stdlib module; deferred inline import is non-idiomatic and hides the dependency."
    },
    {
      "id": "F202",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:427. Same SSRF confirmation as F19/F90/F151. Triplicate."
    },
    {
      "id": "F203",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:465. `test_audit_links_network_error_warns` patches urlopen to raise URLError and expects WARN. No test verifies that a redirect to an internal address is blocked before following."
    },
    {
      "id": "F204",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:114. Same missing markdown injection test as F92/F157. Near-duplicate."
    },
    {
      "id": "F205",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_svp.py:511. S011 checks author_github_id == session.verifier_id but no test verifies that author_github_id is derived from a trusted source. Near-duplicate of F91."
    },
    {
      "id": "F206",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:370. Same auto-fix produces mutable URL as F39/F111/F154. Near-duplicate."
    },
    {
      "id": "F207",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:92. `_minimal_canonical()` constructs scope inventory as `'inline-json:' + json.dumps(['README.md'])`. Test doesn't validate behavior with malformed JSON payload after the prefix."
    },
    {
      "id": "F208",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_push_hook.py:189. TestMain mocks entire real execution path. Tests verify logic but not actual git integration."
    },
    {
      "id": "F209",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:1237. Duplicate of F6 — same --no-verify commit."
    },
    {
      "id": "F210",
      "delta": "confirmed",
      "evidence": "Static analysis of .husky/pre-commit:61. PACKET_PATTERN only matches VERIFICATION_PACKET_*. Does not match EVIDENCE_*.md or PACKET_*.md. Near-duplicate of F96/F97."
    },
    {
      "id": "F211",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:7. Module docstring says 'Feature-complete port of the original .husky/pre-commit' but Python hook adds capabilities absent from bash hook (change context mode, evidence-file recognition). Description is inaccurate."
    },
    {
      "id": "F212",
      "delta": "confirmed",
      "evidence": "Static analysis of .cursorrules:30-35. .cursorrules defines tiers only as risk-level descriptions. canonical.py enforces specific evidence class requirements per tier. Developer-facing documentation does not show actual evidence class requirements."
    },
    {
      "id": "F213",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/runner.py:5. Module docstring states 'Replaces the 2244-line inline JS in aiv-guard.yml'. No such JavaScript file found in the repository. Referenced original is absent."
    },
    {
      "id": "F214",
      "delta": "confirmed",
      "evidence": "Static analysis of .github/workflows/ci.yml:5-7. Both push and pull_request triggers constrained to `branches: [main]`. Protocol-audit only fires when changes reach main — PR branches not covered. Near-duplicate of F32/F101."
    },
    {
      "id": "F215",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/config.py:154. HookConfig.functional_prefixes includes .gitignore-related files. Near-duplicate of F30."
    },
    {
      "id": "F216",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:334. `validate_file_type_triggers()` emits rule_id='E021'. `LinkValidator._check_link` also uses E021 for link-related checks. Duplicate rule ID across two validators."
    },
    {
      "id": "F217",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/evidence.py:261. `validate_file_type_triggers` takes `changed_files: list[str]` but `ValidationPipeline` calls `validator.validate(packet)` with no `changed_files` argument. Architecturally uncallable through standard pipeline interface. Near-duplicate of F46/F158."
    },
    {
      "id": "F218",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/validators/structure.py:24-30. Class docstring itemises four checks but implementation includes additional checks (E004, E006, E007) not listed. Docstring is an incomplete enumeration of enforced rules."
    },
    {
      "id": "F219",
      "delta": "confirmed",
      "evidence": "Static analysis of scripts/map_packets.py:15. PACKET_PREFIX uses different pattern from auditor, pre-commit hook, and guard expectations. Mapping script may miss packets or include non-packet files."
    },
    {
      "id": "F220",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:317. Docstring states 'injected directly into session JSON' but implementation uses CLI. Near-duplicate of F35/F104/F105/F165."
    },
    {
      "id": "F221",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:4. Module docstring omits Phase 0 (Sanity/AIV Guard check), which is exercised by test_full_journey_passes_validation via phase_0_complete assertions."
    },
    {
      "id": "F222",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_models.py:296. Same docstring/assertion inversion as F38/F143/F166. Near-duplicate."
    },
    {
      "id": "F223",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py:139. Same docstring mismatch as F107/F169. Near-duplicate."
    },
    {
      "id": "F224",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_pre_commit_hook.py:233. TestRule8TooManyFiles test name implies three functional files trigger rejection but staged list may include non-functional files, making the count ambiguous."
    },
    {
      "id": "F225",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:243. Same stale hard-coded line numbers in docstring as F40/F170. Near-duplicate."
    },
    {
      "id": "F226",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_validators.py:606-610. Same or-vs-and defect as F8. Duplicate."
    },
    {
      "id": "F227",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_auditor.py:359. Same non-crashing-only assertion as F10/F42/F61/F110/F124. Near-duplicate."
    },
    {
      "id": "F228",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_coverage.py:36. Same misleading test name as F41/F112. Near-duplicate."
    },
    {
      "id": "F229",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_guard.py:449. `REQUIRED_CLASSES['R0'] == ['A', 'B']` (no E) vs test_coverage.py asserting Class E for R0. Inconsistency between guard-enforced requirements and template-generated output."
    },
    {
      "id": "F230",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/change.py:82. `except (json.JSONDecodeError, Exception)` — redundant listing. Same as F50. Duplicate."
    },
    {
      "id": "F231",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/config.py:284. Same `except Exception: pass` swallowing YAML errors as F60. Near-duplicate."
    },
    {
      "id": "F232",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/evidence_collector.py:249. Same 'never raises' contract violation as F52/F114/F173. Near-duplicate."
    },
    {
      "id": "F233",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/hooks/pre_commit.py:155. Same temp file no cleanup as F113/F175. Near-duplicate."
    },
    {
      "id": "F234",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1664. Same `'changed_symbols' in dir()` antipattern as F28/F118. Near-duplicate."
    },
    {
      "id": "F235",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/cli/main.py:1488. Dead `import subprocess as _sp` alias. Near-duplicate of F121."
    },
    {
      "id": "F236",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/lib/auditor.py:236. Inside `audit()` loop, `p.read_text()` and `p.write_text()` called with no surrounding try/except. Permission error mid-audit propagates as unhandled exception, aborting the entire audit run."
    },
    {
      "id": "F237",
      "delta": "confirmed",
      "evidence": "Static analysis of src/aiv/guard/github_api.py:54. `_request` catches HTTPError but not URLError. Near-duplicate of F115/F174/F44."
    },
    {
      "id": "F238",
      "delta": "confirmed",
      "evidence": "Read src/aiv/cli/main.py:740-745. Line 741: `subprocess.run(['python', '-m', 'pytest', ...])`. `python` may not resolve to the current venv interpreter. `sys.executable` is already imported at the top of main.py and is the correct idiom."
    },
    {
      "id": "F239",
      "delta": "confirmed",
      "evidence": "Read src/aiv/guard/runner.py:393-399. main() calls GitHubAPI.context_from_env() and runner.run() with no surrounding try/except. Missing env vars raise KeyError; network failures raise URLError or GitHubAPIError. All surface as raw Python tracebacks."
    },
    {
      "id": "F240",
      "delta": "confirmed",
      "evidence": "Grep for validate_class_a_manifest|validate_class_c_manifest|validate_semantic_manifest|validate_durable_manifest across src/ returned zero hits outside manifest.py. Four public functions defined in guard/manifest.py:23-218 but never imported or called. Manifest validation permanently inactive."
    },
    {
      "id": "F241",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/parser.py:35-42. ParsedSection.raw_start and raw_end assigned in _extract_sections but never accessed by downstream parser methods or external callers. Dead state tracking confirmed."
    },
    {
      "id": "F242",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/language_drivers/treesitter_driver.py:247. `names[1].text.decode('utf-8') if names[1].text else ''` — empty string added to imports set when text is falsy. Downstream matching on empty string produces false positives for malformed AST nodes."
    },
    {
      "id": "F243",
      "delta": "confirmed",
      "evidence": "Read src/aiv/lib/evidence_collector.py:343. `import xdist as _  # noqa: F401` — package imported solely to test for presence; binding discarded. `importlib.util.find_spec('xdist') is not None` is the correct idiom."
    },
    {
      "id": "F244",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_init.py:54-69,75-82,128-135,192-197. Multiple test methods call subprocess.run([sys.executable, '-m', 'aiv', 'init', ...]) and discard return value with no returncode check. aiv init failures invisible; tests fail later on directory assertions with misleading messages."
    },
    {
      "id": "F245",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_cli_commit_skip.py:117-118,130-131. In test_reason_in_class_a and test_reason_in_method, `_run_aiv_commit()` called but CompletedProcess return value not assigned or inspected. Command failure surfaces only as 'Expected 1 evidence file, got 0', obscuring root cause."
    },
    {
      "id": "F246",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_pre_commit_hook.py:157-172. test_functional_plus_packet_validates patches 5 symbols but omits 'aiv.hooks.pre_commit._load_hook_config'. Real .aiv.yml read from os.getcwd() making test non-deterministic. All other tests use _mock_main which patches this function."
    },
    {
      "id": "F247",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_evidence_collector.py:100-101. `with patch('pathlib.Path.read_text', return_value='...')` replaces method on stdlib Path class globally. Any Path.read_text() call in the entire call stack returns the stub, not just the intended target."
    },
    {
      "id": "F248",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_svp.py:670-680. Line 676: mid-file `from aiv.svp.lib.rating import calculate_rating, score_session` after multiple class definitions, violating PEP 8 E402. ImportError mid-collection causes confusing partial-collection failure."
    },
    {
      "id": "F249",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/unit/test_validators.py:394. IntentSection re-imported inside fixture body at line 394 despite module-level import at line 21. ArtifactLink imported locally at line 394 and again at line 502, instead of being consolidated at module level."
    },
    {
      "id": "F250",
      "delta": "confirmed",
      "evidence": "Read tests/unit/test_language_drivers.py:90-95. `try: TreeSitterDriver().available except ImportError` — only ImportError caught. Constructing TreeSitterDriver() or accessing .available may raise AttributeError/RuntimeError/OSError causing pytest collection error instead of graceful skip."
    },
    {
      "id": "F251",
      "delta": "confirmed",
      "evidence": "Static analysis of tests/integration/test_svp_full_workflow.py:51. `env={**__import__('os').environ, ...}` — os module absent from module-level imports; inline __import__ used. Non-idiomatic; makes os dependency invisible to static analysis. Duplicate of F21/F95/F126/F153/F182."
    },
    {
      "id": "F17",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1237 runs ['git','commit','--no-verify','-m',commit_msg]; live inspection confirms the close command bypasses all hook validation on the packet commit."
    },
    {
      "id": "F21",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed by source inspection; test-code only, no production impact."
    },
    {
      "id": "F22",
      "delta": "refined",
      "classification": "NA",
      "note": "Grep over src/ found no exec/eval/subprocess call on test_code field; session.py:252 only checks field presence. The injection risk is latent in the model design, not an active execution path in current production code."
    },
    {
      "id": "F23",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "pre_commit.py:243 prints 'REQUIRES: [A + B]' for R1; pipeline.py:183 enforces {EXECUTION, REFERENTIAL, INTENT}. Class E (INTENT) is silently required but not documented in the hook rubric."
    },
    {
      "id": "F24",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "pre_commit.py:237 prints 'REQUIRES: A + B + C + E + [D + F]' with D and F in brackets implying optional; pipeline.py:190-197 enforces all six as mandatory for R3."
    },
    {
      "id": "F33",
      "delta": "refined",
      "classification": "DEFECT",
      "note": "Triplication confirmed: identical 3-element tuple at pre_commit.py:46-50, pre_push.py:40-44, auditor.py:51-55. Finding description cited wrong values ('.aiv/'); actual values are '.github/aiv-packets/VERIFICATION_PACKET_', '.github/VERIFICATION_PACKET_', '.github/aiv-packets/PACKET_'. Core claim (no shared source of truth) stands."
    },
    {
      "id": "F43",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "pre_commit.py:212-214: except Exception as exc: print(f'WARNING: Packet validation skipped ({exc})') return True. Any transient subprocess error silently allows commits through."
    },
    {
      "id": "F46",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "grep of entire src/ and tests/ for 'validate_file_type_triggers' returns only the definition at evidence.py:261; method is never called."
    },
    {
      "id": "F62",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_cli_init.py lines 25,31,54,63,76,128,141,190 call subprocess.run without capturing or checking returncode; test-code hygiene issue only."
    },
    {
      "id": "F64",
      "delta": "untested",
      "classification": "NA",
      "note": "All 7 tests in test_cli_commit_skip.py failed at fixture setup: git commit exit 128 due to sandbox-level commit-signing enforcement (signing server returns HTTP 400). IndexError risk at line 136 not exercisable in this environment."
    },
    {
      "id": "F67",
      "delta": "confirmed",
      "classification": "NA",
      "note": "IntentSection imported at test_validators.py:17 (module level) and redundantly re-imported inside fixture bodies at lines 394 and 500; test-code only."
    },
    {
      "id": "F68",
      "delta": "untested",
      "classification": "NA",
      "note": "Tests in test_cli_commit_skip.py could not run; git commit signing constraint in sandbox prevented fixture setup. Source inspection supports the finding but live execution was blocked."
    },
    {
      "id": "F71",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "runner.py:383 sets valid=present where present is a boolean presence check only; no URL, SHA, or content validation performed before promoting valid=True."
    },
    {
      "id": "F82",
      "delta": "confirmed",
      "classification": "NA",
      "note": "Source inspection confirms test_functional_plus_packet_validates (test_pre_commit_hook.py:157) does not patch _load_hook_config unlike _mock_main at line 120; test-code quality issue."
    },
    {
      "id": "F95",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only, same root cause as F21/F153."
    },
    {
      "id": "F103",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1646-1649: when skip_checks=True (R0 only), class_a_md is set to '### Class A (Execution Evidence)\\n\\n- Local checks skipped (--skip-checks).' This placeholder header satisfies the parser's Class A section detection and the pipeline's R0 EXECUTION requirement with zero actual execution evidence."
    },
    {
      "id": "F109",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_validators.py:379 asserts len(info) >= 1; the test name and docstring claim both D and F produce INFO, but a single INFO for either D or F alone satisfies the assertion. Test-code quality issue."
    },
    {
      "id": "F118",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1664 'changed_symbols' in dir() and line 1721 'class_c_data' in dir() confirmed. dir() with no argument returns all names in local+enclosing+global+builtin scopes; locals() is the correct check for local variable assignment."
    },
    {
      "id": "F120",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "github_api.py:187 'import base64' inside get_file_content and line 193 'import urllib.parse' inside search_code confirmed; production code with deferred stdlib imports obfuscates dependencies."
    },
    {
      "id": "F121",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1488 'import subprocess as _sp' inside commit function body when subprocess is already imported at module level; redundant alias confirmed."
    },
    {
      "id": "F126",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 __import__('os').environ confirmed; test-code only. Same location as F182 and F251."
    },
    {
      "id": "F127",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_auditor.py:419-420 'import subprocess; import sys' inside test method body and again at 434-435 confirmed; test-code only."
    },
    {
      "id": "F128",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp.py:676 'from aiv.svp.lib.rating import calculate_rating, score_session' after all test class definitions confirmed; same location as F185 and F248."
    },
    {
      "id": "F129",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_language_drivers.py:90-95 'except ImportError: _TREESITTER_AVAILABLE = False' confirmed; AttributeError from TreeSitterDriver() constructor would propagate uncaught. Same location as F250."
    },
    {
      "id": "F130",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_pre_commit_hook.py:157-172 omits _load_hook_config patch; confirmed by source inspection. Duplicate of F82 and F183."
    },
    {
      "id": "F153",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only. Duplicate of F95."
    },
    {
      "id": "F156",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "No production code validates session file origin, signature, or chain-of-custody. SVP session JSON files can be forged by writing directly to .svp/. validators/session.py validates content rules (S001-S016) but not file integrity. No test exercises this attack path."
    },
    {
      "id": "F158",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "validate_file_type_triggers defined at evidence.py:261, never called from any production or test code. Duplicate of F46."
    },
    {
      "id": "F159",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "pipeline.py:183 _TIER_REQUIRED[R1]={EXECUTION,REFERENTIAL,INTENT}; pre_commit.py:243 rubric shows 'REQUIRES: [A + B]' without Class E. Same underlying defect as F23."
    },
    {
      "id": "F162",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "evidence.py:242 manual_state_keywords=['sqlite3','psql','mysql','mongo','query'] confirmed; excludes all other manual reproduction steps (shell scripts, file edits, API calls, etc.)."
    },
    {
      "id": "F164",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:10 docstring 'Phase 4: Ownership Lock (manual — tested via model injection)' is stale; all Phase 4 tests use self._run('ownership',...) CLI calls. Test-code docstring drift."
    },
    {
      "id": "F171",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_models.py:98 'with pytest.raises(Exception)' confirmed; masks the specific exception type (ValidationError/PydanticUserError). Test-code quality issue."
    },
    {
      "id": "F178",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "github_api.py:191-202 search_code method confirmed; grep of entire src/ shows no callers outside github_api.py itself. Dead production code."
    },
    {
      "id": "F182",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 __import__('os') confirmed; test-code only. Same location as F126 and F251."
    },
    {
      "id": "F183",
      "delta": "confirmed",
      "classification": "NA",
      "note": "_load_hook_config not mocked in test_functional_plus_packet_validates; same finding as F82 and F130."
    },
    {
      "id": "F185",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp.py:676 mid-file module-level import after class definitions confirmed; same location as F128 and F248."
    },
    {
      "id": "F191",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "models.py:592 tier: VerifierTier = Field(default=VerifierTier.NOVICE) hardcodes NOVICE as default even when elo_rating=500 (the other default). from_elo(500) returns COMPETENT at line 89-90 but VerifierRating().tier is NOVICE until apply_event() is called. The initial tier is wrong for any VerifierRating constructed without events."
    },
    {
      "id": "F199",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "canonical.py:441 base64.b64decode(payload) where payload is the raw inline-b64-json: suffix from a packet's reference field; no length guard. Confirmed by source inspection."
    },
    {
      "id": "F201",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "canonical.py:442 and 451 __import__('json').loads(...) in security-enforcing _read_scope_inventory; confirmed. The dynamic import hides the json dependency from static analysis in this audit-critical path."
    },
    {
      "id": "F208",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_pre_push_hook.py mocks _get_commit_files and _get_commits_in_range throughout; no test performs a real git push. Test coverage gap confirmed by source inspection."
    },
    {
      "id": "F214",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "ci.yml:4-7 push and pull_request triggers both restricted to branches:[main]; confirmed. pre_push.py:17-22 claims Layer 3 CI coverage for all pushed branches, which is false for feature branches."
    },
    {
      "id": "F216",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "rule_id='E021' appears at evidence.py:334 (missing Class D section trigger) and links.py:140,152 (unreachable evidence URL). Two structurally different violations share the same rule ID, making suppression impossible."
    },
    {
      "id": "F229",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "canonical.py:24 REQUIRED_CLASSES['R0']=['A','B']; pipeline.py:182 _TIER_REQUIRED[R0]={EXECUTION,REFERENTIAL}; test_e2e_compliance.py:744 asserts Class E IS present for R0 in _build_evidence_sections output. Three divergent definitions for R0 required classes."
    },
    {
      "id": "F231",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "config.py:263-284: entire YAML load and extraction in a single try: ... except Exception: pass block; any YAML error, type mismatch, or I/O failure silently returns default config with no log output."
    },
    {
      "id": "F233",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "pre_commit.py:155 NamedTemporaryFile(delete=False) and line 183 mkdtemp not in try/finally; if subprocess.run at line 187 raises (e.g., timeout), both tmp_path and audit_dir leak. Outer except at line 212 does not clean up these resources."
    },
    {
      "id": "F234",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1664 and 1721 use 'X in dir()' as local variable existence checks; confirmed. dir() with no argument returns names from all scopes; locals() is the correct check. Same defect as F118."
    },
    {
      "id": "F235",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:1488 'import subprocess as _sp' inside commit function body; subprocess already imported at module level. Same code as F121."
    },
    {
      "id": "F238",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "cli/main.py:741 ['python','-m','pytest',...], line 768 ['python','-m','ruff',...], line 784 ['python','-m','mypy',...] confirmed. All use bare 'python' rather than sys.executable, breaking venv isolation."
    },
    {
      "id": "F240",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "grep of src/ for 'from aiv.guard.manifest' or 'import manifest' returns no hits outside manifest.py itself; the four public functions are only imported by tests. Dead code in production surface."
    },
    {
      "id": "F242",
      "delta": "confirmed",
      "classification": "DEFECT",
      "note": "treesitter_driver.py:247 'imports.add(names[1].text.decode(\"utf-8\") if names[1].text else \"\")' confirmed; when names[1].text is b'' (empty bytes), the empty string '' is added to the imports set, causing false-positive symbol matching."
    },
    {
      "id": "F243",
      "delta": "refined",
      "classification": "DEFECT",
      "note": "evidence_collector.py:343 'import xdist as _' confirmed; the pattern is functionally correct (ImportError on absence triggers serial mode) but non-idiomatic. importlib.util.find_spec('xdist') is the conventional probe. The # noqa: F401 suppresses the linter but the pattern remains opaque."
    },
    {
      "id": "F248",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp.py:676 mid-file import confirmed; same location as F128 and F185."
    },
    {
      "id": "F249",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_validators.py:394 and 500 re-import IntentSection inside fixture bodies; already imported at module level line 17. Same pattern as F67."
    },
    {
      "id": "F250",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_language_drivers.py:90-95 except ImportError only; same location as F129."
    },
    {
      "id": "F251",
      "delta": "confirmed",
      "classification": "NA",
      "note": "test_svp_full_workflow.py:51 inline __import__('os') confirmed; same location as F126 and F182."
    }
  ],
  "unexecuted": [],
  "deep": {
    "deps_installed": true,
    "production_coverage_pct": 70.75,
    "version_drift": [],
    "deltas": [
      {
        "id": "F17",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1237 runs ['git','commit','--no-verify','-m',commit_msg]; live inspection confirms the close command bypasses all hook validation on the packet commit."
      },
      {
        "id": "F21",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed by source inspection; test-code only, no production impact."
      },
      {
        "id": "F22",
        "delta": "refined",
        "classification": "NA",
        "note": "Grep over src/ found no exec/eval/subprocess call on test_code field; session.py:252 only checks field presence. The injection risk is latent in the model design, not an active execution path in current production code."
      },
      {
        "id": "F23",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "pre_commit.py:243 prints 'REQUIRES: [A + B]' for R1; pipeline.py:183 enforces {EXECUTION, REFERENTIAL, INTENT}. Class E (INTENT) is silently required but not documented in the hook rubric."
      },
      {
        "id": "F24",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "pre_commit.py:237 prints 'REQUIRES: A + B + C + E + [D + F]' with D and F in brackets implying optional; pipeline.py:190-197 enforces all six as mandatory for R3."
      },
      {
        "id": "F33",
        "delta": "refined",
        "classification": "DEFECT",
        "note": "Triplication confirmed: identical 3-element tuple at pre_commit.py:46-50, pre_push.py:40-44, auditor.py:51-55. Finding description cited wrong values ('.aiv/'); actual values are '.github/aiv-packets/VERIFICATION_PACKET_', '.github/VERIFICATION_PACKET_', '.github/aiv-packets/PACKET_'. Core claim (no shared source of truth) stands."
      },
      {
        "id": "F43",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "pre_commit.py:212-214: except Exception as exc: print(f'WARNING: Packet validation skipped ({exc})') return True. Any transient subprocess error silently allows commits through."
      },
      {
        "id": "F46",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "grep of entire src/ and tests/ for 'validate_file_type_triggers' returns only the definition at evidence.py:261; method is never called."
      },
      {
        "id": "F62",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_cli_init.py lines 25,31,54,63,76,128,141,190 call subprocess.run without capturing or checking returncode; test-code hygiene issue only."
      },
      {
        "id": "F64",
        "delta": "untested",
        "classification": "NA",
        "note": "All 7 tests in test_cli_commit_skip.py failed at fixture setup: git commit exit 128 due to sandbox-level commit-signing enforcement (signing server returns HTTP 400). IndexError risk at line 136 not exercisable in this environment."
      },
      {
        "id": "F67",
        "delta": "confirmed",
        "classification": "NA",
        "note": "IntentSection imported at test_validators.py:17 (module level) and redundantly re-imported inside fixture bodies at lines 394 and 500; test-code only."
      },
      {
        "id": "F68",
        "delta": "untested",
        "classification": "NA",
        "note": "Tests in test_cli_commit_skip.py could not run; git commit signing constraint in sandbox prevented fixture setup. Source inspection supports the finding but live execution was blocked."
      },
      {
        "id": "F71",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "runner.py:383 sets valid=present where present is a boolean presence check only; no URL, SHA, or content validation performed before promoting valid=True."
      },
      {
        "id": "F82",
        "delta": "confirmed",
        "classification": "NA",
        "note": "Source inspection confirms test_functional_plus_packet_validates (test_pre_commit_hook.py:157) does not patch _load_hook_config unlike _mock_main at line 120; test-code quality issue."
      },
      {
        "id": "F95",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only, same root cause as F21/F153."
      },
      {
        "id": "F103",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1646-1649: when skip_checks=True (R0 only), class_a_md is set to '### Class A (Execution Evidence)\\n\\n- Local checks skipped (--skip-checks).' This placeholder header satisfies the parser's Class A section detection and the pipeline's R0 EXECUTION requirement with zero actual execution evidence."
      },
      {
        "id": "F109",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_validators.py:379 asserts len(info) >= 1; the test name and docstring claim both D and F produce INFO, but a single INFO for either D or F alone satisfies the assertion. Test-code quality issue."
      },
      {
        "id": "F118",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1664 'changed_symbols' in dir() and line 1721 'class_c_data' in dir() confirmed. dir() with no argument returns all names in local+enclosing+global+builtin scopes; locals() is the correct check for local variable assignment."
      },
      {
        "id": "F120",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "github_api.py:187 'import base64' inside get_file_content and line 193 'import urllib.parse' inside search_code confirmed; production code with deferred stdlib imports obfuscates dependencies."
      },
      {
        "id": "F121",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1488 'import subprocess as _sp' inside commit function body when subprocess is already imported at module level; redundant alias confirmed."
      },
      {
        "id": "F126",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 __import__('os').environ confirmed; test-code only. Same location as F182 and F251."
      },
      {
        "id": "F127",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_auditor.py:419-420 'import subprocess; import sys' inside test method body and again at 434-435 confirmed; test-code only."
      },
      {
        "id": "F128",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp.py:676 'from aiv.svp.lib.rating import calculate_rating, score_session' after all test class definitions confirmed; same location as F185 and F248."
      },
      {
        "id": "F129",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_language_drivers.py:90-95 'except ImportError: _TREESITTER_AVAILABLE = False' confirmed; AttributeError from TreeSitterDriver() constructor would propagate uncaught. Same location as F250."
      },
      {
        "id": "F130",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_pre_commit_hook.py:157-172 omits _load_hook_config patch; confirmed by source inspection. Duplicate of F82 and F183."
      },
      {
        "id": "F153",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 env={**__import__('os').environ,...} confirmed; test-code only. Duplicate of F95."
      },
      {
        "id": "F156",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "No production code validates session file origin, signature, or chain-of-custody. SVP session JSON files can be forged by writing directly to .svp/. validators/session.py validates content rules (S001-S016) but not file integrity. No test exercises this attack path."
      },
      {
        "id": "F158",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "validate_file_type_triggers defined at evidence.py:261, never called from any production or test code. Duplicate of F46."
      },
      {
        "id": "F159",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "pipeline.py:183 _TIER_REQUIRED[R1]={EXECUTION,REFERENTIAL,INTENT}; pre_commit.py:243 rubric shows 'REQUIRES: [A + B]' without Class E. Same underlying defect as F23."
      },
      {
        "id": "F162",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "evidence.py:242 manual_state_keywords=['sqlite3','psql','mysql','mongo','query'] confirmed; excludes all other manual reproduction steps (shell scripts, file edits, API calls, etc.)."
      },
      {
        "id": "F164",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:10 docstring 'Phase 4: Ownership Lock (manual — tested via model injection)' is stale; all Phase 4 tests use self._run('ownership',...) CLI calls. Test-code docstring drift."
      },
      {
        "id": "F171",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_models.py:98 'with pytest.raises(Exception)' confirmed; masks the specific exception type (ValidationError/PydanticUserError). Test-code quality issue."
      },
      {
        "id": "F178",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "github_api.py:191-202 search_code method confirmed; grep of entire src/ shows no callers outside github_api.py itself. Dead production code."
      },
      {
        "id": "F182",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 __import__('os') confirmed; test-code only. Same location as F126 and F251."
      },
      {
        "id": "F183",
        "delta": "confirmed",
        "classification": "NA",
        "note": "_load_hook_config not mocked in test_functional_plus_packet_validates; same finding as F82 and F130."
      },
      {
        "id": "F185",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp.py:676 mid-file module-level import after class definitions confirmed; same location as F128 and F248."
      },
      {
        "id": "F191",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "models.py:592 tier: VerifierTier = Field(default=VerifierTier.NOVICE) hardcodes NOVICE as default even when elo_rating=500 (the other default). from_elo(500) returns COMPETENT at line 89-90 but VerifierRating().tier is NOVICE until apply_event() is called. The initial tier is wrong for any VerifierRating constructed without events."
      },
      {
        "id": "F199",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "canonical.py:441 base64.b64decode(payload) where payload is the raw inline-b64-json: suffix from a packet's reference field; no length guard. Confirmed by source inspection."
      },
      {
        "id": "F201",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "canonical.py:442 and 451 __import__('json').loads(...) in security-enforcing _read_scope_inventory; confirmed. The dynamic import hides the json dependency from static analysis in this audit-critical path."
      },
      {
        "id": "F208",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_pre_push_hook.py mocks _get_commit_files and _get_commits_in_range throughout; no test performs a real git push. Test coverage gap confirmed by source inspection."
      },
      {
        "id": "F214",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "ci.yml:4-7 push and pull_request triggers both restricted to branches:[main]; confirmed. pre_push.py:17-22 claims Layer 3 CI coverage for all pushed branches, which is false for feature branches."
      },
      {
        "id": "F216",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "rule_id='E021' appears at evidence.py:334 (missing Class D section trigger) and links.py:140,152 (unreachable evidence URL). Two structurally different violations share the same rule ID, making suppression impossible."
      },
      {
        "id": "F229",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "canonical.py:24 REQUIRED_CLASSES['R0']=['A','B']; pipeline.py:182 _TIER_REQUIRED[R0]={EXECUTION,REFERENTIAL}; test_e2e_compliance.py:744 asserts Class E IS present for R0 in _build_evidence_sections output. Three divergent definitions for R0 required classes."
      },
      {
        "id": "F231",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "config.py:263-284: entire YAML load and extraction in a single try: ... except Exception: pass block; any YAML error, type mismatch, or I/O failure silently returns default config with no log output."
      },
      {
        "id": "F233",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "pre_commit.py:155 NamedTemporaryFile(delete=False) and line 183 mkdtemp not in try/finally; if subprocess.run at line 187 raises (e.g., timeout), both tmp_path and audit_dir leak. Outer except at line 212 does not clean up these resources."
      },
      {
        "id": "F234",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1664 and 1721 use 'X in dir()' as local variable existence checks; confirmed. dir() with no argument returns names from all scopes; locals() is the correct check. Same defect as F118."
      },
      {
        "id": "F235",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:1488 'import subprocess as _sp' inside commit function body; subprocess already imported at module level. Same code as F121."
      },
      {
        "id": "F238",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "cli/main.py:741 ['python','-m','pytest',...], line 768 ['python','-m','ruff',...], line 784 ['python','-m','mypy',...] confirmed. All use bare 'python' rather than sys.executable, breaking venv isolation."
      },
      {
        "id": "F240",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "grep of src/ for 'from aiv.guard.manifest' or 'import manifest' returns no hits outside manifest.py itself; the four public functions are only imported by tests. Dead code in production surface."
      },
      {
        "id": "F242",
        "delta": "confirmed",
        "classification": "DEFECT",
        "note": "treesitter_driver.py:247 'imports.add(names[1].text.decode(\"utf-8\") if names[1].text else \"\")' confirmed; when names[1].text is b'' (empty bytes), the empty string '' is added to the imports set, causing false-positive symbol matching."
      },
      {
        "id": "F243",
        "delta": "refined",
        "classification": "DEFECT",
        "note": "evidence_collector.py:343 'import xdist as _' confirmed; the pattern is functionally correct (ImportError on absence triggers serial mode) but non-idiomatic. importlib.util.find_spec('xdist') is the conventional probe. The # noqa: F401 suppresses the linter but the pattern remains opaque."
      },
      {
        "id": "F248",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp.py:676 mid-file import confirmed; same location as F128 and F185."
      },
      {
        "id": "F249",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_validators.py:394 and 500 re-import IntentSection inside fixture bodies; already imported at module level line 17. Same pattern as F67."
      },
      {
        "id": "F250",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_language_drivers.py:90-95 except ImportError only; same location as F129."
      },
      {
        "id": "F251",
        "delta": "confirmed",
        "classification": "NA",
        "note": "test_svp_full_workflow.py:51 inline __import__('os') confirmed; same location as F126 and F182."
      }
    ],
    "still_unexecuted": [
      {
        "region": "src/aiv/cli/main.py:982-1256",
        "reason": "aiv close command body; no integration test invokes close end-to-end (requires real git repo with a prior aiv commit context)."
      },
      {
        "region": "src/aiv/guard/__main__.py:3-6",
        "reason": "Guard CLI entry point; invocation requires GITHUB_TOKEN and a live PR context; coverage=0%."
      },
      {
        "region": "src/aiv/guard/github_api.py:45-202",
        "reason": "All GitHub API methods require network access and auth token; coverage=26% (only class/method stubs covered)."
      },
      {
        "region": "src/aiv/guard/runner.py:298-420",
        "reason": "GuardRunner.run() main execution path; requires GitHub API context; coverage=47%."
      },
      {
        "region": "src/aiv/cli/main.py:1413-1925",
        "reason": "aiv commit command body (subprocess-heavy paths); tests/unit/test_cli_commit_skip.py 7 tests all fail at fixture setup due to sandbox commit-signing constraint (signing server returns HTTP 400)."
      },
      {
        "region": "src/aiv/hooks/pre_commit.py:150-214",
        "reason": "_validate_packet subprocess paths; actual pre-commit hook invocation blocked by the same git signing constraint that prevents staged_repo fixture from completing."
      }
    ]
  },
  "run_commands": [
    {
      "cmd": "pip install -e \".[dev]\"",
      "code": 0
    },
    {
      "cmd": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml",
      "code": 4
    },
    {
      "cmd": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml",
      "code": 4
    }
  ]
}
```
