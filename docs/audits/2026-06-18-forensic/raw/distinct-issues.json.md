# distinct-issues.json (verbatim)

> Raw audit artifact, wrapped in Markdown for fast-track-eligible tracking. Content below is byte-for-byte the original `distinct-issues.json`. To extract: delete this header and the surrounding fence lines.

```json
[
  {
    "sig": ".husky/pre-commit :: husky-drift",
    "severity": "critical",
    "class": "doc/code drift",
    "title": "Bash hook incompatible with aiv commit: EVIDENCE_*.md not recognized as packet",
    "location": ".husky/pre-commit:61 vs src/aiv/cli/main.py:1879 vs src/aiv/hooks/pre_commit.py:342",
    "ids": [
      "F96",
      "F98",
      "F97"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: fail-open",
    "severity": "critical",
    "class": "error-handling",
    "title": "pre-commit exception handler returns True — enforcement bypassed",
    "location": "src/aiv/hooks/pre_commit.py:212-214",
    "ids": [
      "F43"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: close-no-verify",
    "severity": "high",
    "class": "correctness",
    "title": "aiv close commits verification packet with --no-verify, bypassing hook validation",
    "location": "src/aiv/cli/main.py:1236-1237",
    "ids": [
      "F69",
      "F209",
      "F17",
      "F48",
      "F87",
      "F99",
      "F26",
      "F149",
      "F6"
    ],
    "n": 9,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: test-doc-drift",
    "severity": "high",
    "class": "doc_code_drift",
    "title": "Phase 4 docstring claims JSON injection but code runs CLI command",
    "location": "tests/integration/test_svp_full_workflow.py:321",
    "ids": [
      "F104",
      "F220",
      "F35",
      "F36",
      "F105",
      "F164",
      "F165",
      "F221"
    ],
    "n": 8,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: github-api-errors",
    "severity": "high",
    "class": "error-handling",
    "title": "list_pr_files silently returns partial file list on pagination error",
    "location": "src/aiv/guard/github_api.py:116-117",
    "ids": [
      "F44",
      "F115",
      "F174",
      "F237",
      "F45",
      "F177",
      "F178"
    ],
    "n": 7,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_validators.py :: ssrf",
    "severity": "high",
    "class": "SSRF",
    "title": "SSRF via LinkValidator outbound fetch of user-controlled packet URLs",
    "location": "tests/unit/test_validators.py:427-479",
    "ids": [
      "F19",
      "F202",
      "F90",
      "F151",
      "F203",
      "F66"
    ],
    "n": 6,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: path-traversal",
    "severity": "high",
    "class": "path-traversal",
    "title": "Path traversal in Packet Source resolution",
    "location": "src/aiv/guard/runner.py:191-204",
    "ids": [
      "F14",
      "F83",
      "F146",
      "F197"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/links.py :: ssrf",
    "severity": "high",
    "class": "ssrf",
    "title": "SSRF via link vitality checker — unrestricted URL fetch",
    "location": "src/aiv/lib/validators/links.py:163-176",
    "ids": [
      "F15",
      "F196",
      "F84",
      "F147"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: dead-code",
    "severity": "high",
    "class": "dead-code",
    "title": "EvidenceValidator.validate_file_type_triggers is dead code — never called",
    "location": "src/aiv/lib/validators/evidence.py:261",
    "ids": [
      "F46",
      "F59",
      "F158",
      "F217"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: error-handling",
    "severity": "high",
    "class": "error-handling",
    "title": "close command silently fabricates empty claims when evidence files are unreadable",
    "location": "src/aiv/cli/main.py:1085",
    "ids": [
      "F49",
      "F117",
      "F118",
      "F238"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: run-git-contract",
    "severity": "high",
    "class": "error-handling",
    "title": "_run_git in evidence_collector.py silently omits try/except despite 'never raises' docstring",
    "location": "src/aiv/lib/evidence_collector.py:249-255",
    "ids": [
      "F114",
      "F173",
      "F232",
      "F52"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_validators.py :: correctness/logic",
    "severity": "high",
    "class": "correctness/logic",
    "title": "Logic error: `or` instead of `and` in unlinked-evidence-consumption assertion",
    "location": "tests/unit/test_validators.py:608",
    "ids": [
      "F8",
      "F78",
      "F141"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_models.py :: test-doc-drift",
    "severity": "high",
    "class": "doc/code drift",
    "title": "Test name and docstring say 'main should NOT be mutable' but assertion asserts IS mutable",
    "location": "tests/unit/test_models.py:296",
    "ids": [
      "F222",
      "F38",
      "F143"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_validators.py :: test-doc-drift",
    "severity": "high",
    "class": "doc/code drift",
    "title": "OR-logic in assertion contradicts comment that 'Claims 2 AND 3' must differ from claim 1",
    "location": "tests/unit/test_validators.py:606",
    "ids": [
      "F226",
      "F109",
      "F166"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: tier-drift",
    "severity": "high",
    "class": "doc-code-drift",
    "title": "R1 rubric omits mandatory Class E in two hook files",
    "location": "src/aiv/hooks/pre_commit.py:240",
    "ids": [
      "F23",
      "F24"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: error-handling",
    "severity": "high",
    "class": "error-handling",
    "title": "collect_class_b emits non-functional GitHub permalinks when git rev-parse fails",
    "location": "src/aiv/lib/evidence_collector.py:283-285",
    "ids": [
      "F47",
      "F54"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: authz",
    "severity": "high",
    "class": "authz",
    "title": "SVP verifier identity is self-asserted via CLI argument with no authentication",
    "location": "tests/integration/test_svp_full_workflow.py:387",
    "ids": [
      "F91",
      "F94"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: resource-leak",
    "severity": "high",
    "class": "resource-leak",
    "title": "Temp files leaked in exception paths inside _validate_packet",
    "location": "src/aiv/hooks/pre_commit.py:155-214",
    "ids": [
      "F113",
      "F175"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/anti_cheat.py :: antichat-blanket",
    "severity": "high",
    "class": "logic-bug/security-bypass",
    "title": "check_justification: any Class F claim with >20 chars justifies ALL anti-cheat findings",
    "location": "src/aiv/lib/validators/anti_cheat.py:203-209",
    "ids": [
      "F134",
      "F187"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: test-doc-drift",
    "severity": "high",
    "class": "doc_code_drift",
    "title": "Test name 'test_template_is_not_packet' directly contradicts its own assertion",
    "location": "tests/unit/test_pre_commit_hook.py:36",
    "ids": [
      "F106"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: missing-check/logic-gap",
    "severity": "high",
    "class": "missing-check/logic-gap",
    "title": "_inspect_class_a_run does not verify CI run succeeded (no conclusion check)",
    "location": "src/aiv/guard/runner.py:336-365",
    "ids": [
      "F135"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/pipeline.py :: tier-drift",
    "severity": "high",
    "class": "doc-code-drift",
    "title": "R1 evidence requirement: hook rubric documents {A,B} but pipeline enforces {A,B,E}",
    "location": "src/aiv/lib/validators/pipeline.py:183",
    "ids": [
      "F159"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".husky/pre-commit :: path-traversal",
    "severity": "high",
    "class": "doc/code drift",
    "title": ".husky/pre-commit PACKET_PATTERN does not match Layer 1 EVIDENCE_*.md files or PACKET_*.md prefix, diverging from Python hook",
    "location": ".husky/pre-commit:61",
    "ids": [
      "F210"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: dead-code",
    "severity": "medium",
    "class": "dead-code",
    "title": "Dead read: p.read_text() return value discarded in test_fix_commit_pending",
    "location": "tests/unit/test_auditor.py:365",
    "ids": [
      "F61",
      "F124",
      "F10",
      "F65",
      "F127",
      "F181"
    ],
    "n": 6,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_commit_skip.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "Unguarded evidence_files[0] in test_reason_in_methodology risks IndexError",
    "location": "tests/unit/test_cli_commit_skip.py:136-137",
    "ids": [
      "F64",
      "F125",
      "F68",
      "F180"
    ],
    "n": 4,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: secrets",
    "severity": "medium",
    "class": "secrets",
    "title": "Integration test propagates full process environment to subprocess under test",
    "location": "tests/integration/test_svp_full_workflow.py:51",
    "ids": [
      "F153",
      "F21",
      "F95"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/pipeline.py :: test-doc-drift",
    "severity": "medium",
    "class": "doc-code-drift",
    "title": "ValidationPipeline docstring lists 7 stages; 8 are implemented",
    "location": "src/aiv/lib/validators/pipeline.py:48",
    "ids": [
      "F27",
      "F76",
      "F100"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/auditor.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "Unguarded read_text and write_text in auditor.audit() loop crash entire run on single-file error",
    "location": "src/aiv/lib/auditor.py:236",
    "ids": [
      "F236",
      "F56",
      "F58"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_svp.py :: tier-drift",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "VerifierRating initial tier contradicts from_elo boundary",
    "location": "tests/unit/test_svp.py:155,389-390",
    "ids": [
      "F142",
      "F191",
      "F77"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_commit_skip.py :: injection",
    "severity": "medium",
    "class": "injection",
    "title": "User-controlled --skip-reason text inserted verbatim into structured markdown evidence files",
    "location": "tests/unit/test_cli_commit_skip.py:116",
    "ids": [
      "F92",
      "F204",
      "F157"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_svp.py :: test-doc-drift",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "Contradictory assertions: `from_elo(500)` returns COMPETENT but initial VerifierRating at ELO 500 asserts NOVICE",
    "location": "tests/unit/test_svp.py:154-155",
    "ids": [
      "F9",
      "F193"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: correctness/logic",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "json.loads(result.stdout) called unconditionally after returncode==1 in integration tests — non-JSON CLI output yields JSONDecodeError masking the real failure",
    "location": "tests/integration/test_svp_full_workflow.py:247,309",
    "ids": [
      "F80",
      "F12"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: path-traversal",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "pre_commit.py module docstring claims to be a 'feature-complete port' of the bash hook but adds Rules 10, EVIDENCE_PREFIX handling, and active-change-context bypass not present in the bash hook",
    "location": "src/aiv/hooks/pre_commit.py:7",
    "ids": [
      "F211",
      "F33"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: doc/code drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "test_fix_commit_pending discards read_text result and verifies no fix behavior",
    "location": "tests/unit/test_auditor.py:361-368",
    "ids": [
      "F42",
      "F227"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "get_file_content has unhandled binascii.Error on malformed base64",
    "location": "src/aiv/guard/github_api.py:188",
    "ids": [
      "F53",
      "F116"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: resource-handling",
    "severity": "medium",
    "class": "resource-handling",
    "title": "Temp file and temp dir in _validate_packet not guarded with try/finally; outer except silently allows commits on failure",
    "location": "src/aiv/hooks/pre_commit.py:155",
    "ids": [
      "F233",
      "F55"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: tier-drift",
    "severity": "medium",
    "class": "correctness",
    "title": "_build_evidence_class_results() sets valid=present without independent quality validation",
    "location": "src/aiv/guard/runner.py:383",
    "ids": [
      "F71",
      "F119"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: correctness/logic",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "test_evidence_dir_none_skips_scan passes vacuously — empty packets_dir makes the assertion trivially true",
    "location": "tests/unit/test_auditor.py:875-884",
    "ids": [
      "F79",
      "F145"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: injection",
    "severity": "medium",
    "class": "injection",
    "title": "URL injection via unencoded path parameter in get_file_content",
    "location": "src/aiv/guard/github_api.py:176",
    "ids": [
      "F86",
      "F198"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_init.py :: test-doc-drift",
    "severity": "medium",
    "class": "doc_code_drift",
    "title": "test_cli_init docstring claims hook 'catches' bypass but assertion only checks string presence",
    "location": "tests/unit/test_cli_init.py:139",
    "ids": [
      "F107",
      "F223"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: injection",
    "severity": "medium",
    "class": "injection",
    "title": "Injection: auto-fix mode generates mutable /blob/main/ URLs, defeating the auditor's own immutability enforcement",
    "location": "tests/unit/test_auditor.py:370",
    "ids": [
      "F206",
      "F154"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_svp.py :: authz",
    "severity": "medium",
    "class": "authz",
    "title": "No test for SVP session forgery via direct JSON file creation",
    "location": "tests/unit/test_svp.py:443-528",
    "ids": [
      "F156",
      "F205"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/canonical.py :: injection",
    "severity": "medium",
    "class": "injection",
    "title": "Unbounded base64 decode in _read_scope_inventory",
    "location": "src/aiv/guard/canonical.py:438-441",
    "ids": [
      "F199",
      "F201"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/anti_cheat.py :: correctness",
    "severity": "medium",
    "class": "correctness",
    "title": "Anti-cheat line counter increments on +++ file header lines",
    "location": "src/aiv/lib/validators/anti_cheat.py:135-141",
    "ids": [
      "F1"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/models.py :: correctness",
    "severity": "medium",
    "class": "correctness",
    "title": "GuardResult.finalize() never updates compliance_level for passing results",
    "location": "src/aiv/guard/models.py:182-189",
    "ids": [
      "F3"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: correctness",
    "severity": "medium",
    "class": "correctness",
    "title": "_validate_execution() early pass for github_actions/external links suppresses performance and UI sub-checks",
    "location": "src/aiv/lib/validators/evidence.py:86-91",
    "ids": [
      "F5"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: close-no-verify",
    "severity": "medium",
    "class": "authz",
    "title": "Authorization bypass: pre-commit hook reads live .aiv.yml at commit time enabling policy self-disablement",
    "location": "tests/unit/test_pre_commit_hook.py:308-314",
    "ids": [
      "F20"
    ],
    "n": 1,
    "runtime": false
  },
  {
    "sig": "src/aiv/cli/main.py :: doc-code-drift",
    "severity": "medium",
    "class": "doc-code-drift",
    "title": "generate emits v2.1 packet header; close emits v2.2 — undocumented schema split",
    "location": "src/aiv/cli/main.py:514",
    "ids": [
      "F25"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: stale-data",
    "severity": "medium",
    "class": "stale-data",
    "title": "Class B evidence links embed pre-commit HEAD SHA; links are stale after actual commit",
    "location": "src/aiv/lib/evidence_collector.py:283",
    "ids": [
      "F29"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".github/workflows/ci.yml :: intent-drift",
    "severity": "medium",
    "class": "intent-drift",
    "title": "protocol-audit CI job guarded by push-event filter; does not run on PRs",
    "location": ".github/workflows/ci.yml:67",
    "ids": [
      "F32"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/change.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "load_change silently returns None on any parse or I/O error",
    "location": "src/aiv/lib/change.py:82",
    "ids": [
      "F50"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_commit.py :: run-git-contract",
    "severity": "medium",
    "class": "error-handling",
    "title": "_run_git in pre_commit.py never checks returncode — silent git failures",
    "location": "src/aiv/hooks/pre_commit.py:65-71",
    "ids": [
      "F51"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: run-git-contract",
    "severity": "medium",
    "class": "error-handling",
    "title": "subprocess.TimeoutExpired unhandled in integration test helper _run()",
    "location": "tests/integration/test_svp_full_workflow.py:45-61",
    "ids": [
      "F63"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/svp/lib/validators/session.py :: dead-code",
    "severity": "medium",
    "class": "correctness",
    "title": "S004 complexity-estimate warning is dead code — predicted_complexity is non-optional",
    "location": "src/aiv/svp/lib/validators/session.py:113",
    "ids": [
      "F70"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/models.py :: correctness",
    "severity": "medium",
    "class": "correctness",
    "title": "ArtifactLink.from_url() SHA-pinning detection false-positive on short hex-format strings",
    "location": "src/aiv/lib/models.py:132-133",
    "ids": [
      "F72"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: ssrf",
    "severity": "medium",
    "class": "ssrf",
    "title": "SSRF / URL injection via git-remote-derived owner/repo in GitHub API calls",
    "location": "src/aiv/cli/main.py:683",
    "ids": [
      "F85"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: path-traversal",
    "severity": "medium",
    "class": "path-traversal",
    "title": "Auto-fix mode embeds local file path directly into GitHub URL without URL-encoding",
    "location": "tests/unit/test_auditor.py:370",
    "ids": [
      "F93"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/hooks/pre_push.py :: doc/code drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "Pre-push hook claims CI layer-3 catches no-verify commits on PRs but protocol-audit only runs on push",
    "location": "src/aiv/hooks/pre_push.py:15-16 vs .github/workflows/ci.yml:67",
    "ids": [
      "F101"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: doc_code_drift",
    "severity": "medium",
    "class": "doc_code_drift",
    "title": "test_guard empty-body test comment says 'fail' but assertion accepts non-blocking warn",
    "location": "tests/unit/test_guard.py:401",
    "ids": [
      "F108"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: doc_code_drift",
    "severity": "medium",
    "class": "doc_code_drift",
    "title": "test_fix_commit_pending claims to test auto-fix but only verifies no crash",
    "location": "tests/unit/test_auditor.py:359",
    "ids": [
      "F110"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: intent_mismatch",
    "severity": "medium",
    "class": "intent_mismatch",
    "title": "Auto-fix test for CLASS_E_NO_URL asserts URL conversion but not SHA-pinning; may legitimize mutable /blob/main/ links",
    "location": "tests/unit/test_auditor.py:370",
    "ids": [
      "F111"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/models.py :: logic-inconsistency",
    "severity": "medium",
    "class": "logic-inconsistency",
    "title": "ValidationResult.is_valid inconsistent with status in strict mode",
    "location": "src/aiv/lib/models.py:306-309",
    "ids": [
      "F133"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/svp/lib/validators/session.py :: logic-bug/incomplete-validation",
    "severity": "medium",
    "class": "logic-bug/incomplete-validation",
    "title": "_validate_trace early returns drop validation errors for subsequent traces",
    "location": "src/aiv/svp/lib/validators/session.py:156-157,183-185",
    "ids": [
      "F136"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/auditor.py :: logic-gap/missing-check",
    "severity": "medium",
    "class": "logic-gap/missing-check",
    "title": "_check_evidence omits TODO remnants, classified_by, blast_radius, and claims-TODO checks present in _check_packet",
    "location": "src/aiv/lib/auditor.py:434-578",
    "ids": [
      "F137"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".github/workflows/ci.yml :: injection",
    "severity": "medium",
    "class": "injection",
    "title": "GitHub Actions expression injection via github.actor in shell run step",
    "location": ".github/workflows/ci.yml:387",
    "ids": [
      "F148"
    ],
    "n": 1,
    "runtime": false
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: doc-code-drift/rule-id-collision",
    "severity": "medium",
    "class": "doc-code-drift/rule-id-collision",
    "title": "Rule IDs E020 and E021 each map to two unrelated finding types across validators",
    "location": "src/aiv/lib/validators/evidence.py:113",
    "ids": [
      "F160"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: antichat-blanket",
    "severity": "medium",
    "class": "doc-code-drift/logic-inconsistency",
    "title": "Class F adequacy checked by two validators with contradictory criteria for the same requirement",
    "location": "src/aiv/lib/validators/evidence.py:402",
    "ids": [
      "F161"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: claim-not-verified",
    "severity": "medium",
    "class": "claim-not-verified",
    "title": "test_valid_markdown_packet asserts only canonical_enabled flag, not packet validity",
    "location": "tests/unit/test_guard.py:408",
    "ids": [
      "F167"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: claim-not-verified",
    "severity": "medium",
    "class": "claim-not-verified",
    "title": "TestAutoFix class claims to test auto-remediation but only checks for no crash",
    "location": "tests/unit/test_auditor.py:356",
    "ids": [
      "F168"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_init.py :: close-no-verify",
    "severity": "medium",
    "class": "claim-not-verified",
    "title": "Claim 'hook catches --no-verify bypasses' tested only by string presence in hook file",
    "location": "tests/unit/test_cli_init.py:139",
    "ids": [
      "F169"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: cross-component-inconsistency",
    "severity": "medium",
    "class": "cross-component-inconsistency",
    "title": "Pre-commit hook and auditor disagree on whether TEMPLATE packets count as valid evidence",
    "location": "tests/unit/test_pre_commit_hook.py:35",
    "ids": [
      "F172"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: fail-open",
    "severity": "medium",
    "class": "error-handling-gap",
    "title": "collect_class_a subprocess calls not wrapped in exception handlers",
    "location": "src/aiv/lib/evidence_collector.py:348",
    "ids": [
      "F176"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "test_valid_markdown_packet asserts only canonical_enabled — guard result and block_count unverified",
    "location": "tests/unit/test_guard.py:408-425",
    "ids": [
      "F184"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/models.py :: correctness/logic",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "finalize() leaves compliance_level as 'L1' when guard runs in markdown-only mode",
    "location": "src/aiv/guard/models.py:182-188",
    "ids": [
      "F188"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/parser.py :: correctness/logic",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "URL extraction skipped when artifact_raw starts with 'http' but contains trailing content",
    "location": "src/aiv/lib/parser.py:585",
    "ids": [
      "F189"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/auditor.py :: correctness/logic",
    "severity": "medium",
    "class": "correctness/logic",
    "title": "Auditor CLAIM_TODO and FIX_NO_CLASS_F checks silently skipped for ## Claims heading variant",
    "location": "src/aiv/lib/auditor.py:390-401",
    "ids": [
      "F190"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_validators.py :: logic",
    "severity": "medium",
    "class": "logic",
    "title": "or vs and in artifact-deduplication assertion allows half-correct behavior to pass",
    "location": "tests/unit/test_validators.py:608",
    "ids": [
      "F192"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: secrets",
    "severity": "medium",
    "class": "secrets",
    "title": "GITHUB_TOKEN exposed in plain instance attribute with no repr masking",
    "location": "src/aiv/guard/github_api.py:40",
    "ids": [
      "F200"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".cursorrules :: tier-drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": ".cursorrules risk-tier definitions document R0-R3 but omit the per-tier evidence-class requirements enforced by canonical.py and pipeline.py",
    "location": ".cursorrules:30-35",
    "ids": [
      "F212"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: test-doc-drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "runner.py docstring references a non-existent 2244-line inline JS guard",
    "location": "src/aiv/guard/runner.py:5",
    "ids": [
      "F213"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".github/workflows/ci.yml :: doc/code drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "ci.yml workflow is restricted to main-branch events only; pre_push.py Layer 3 claim that CI protocol-audit covers all pushed branches is false for feature branches",
    "location": ".github/workflows/ci.yml:5-7",
    "ids": [
      "F214"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/config.py :: path-traversal",
    "severity": "medium",
    "class": "doc/code drift",
    "title": ".husky/ path listed in HookConfig.functional_prefixes creates circular enforcement for changes to the bash hook itself",
    "location": "src/aiv/lib/config.py:154",
    "ids": [
      "F215"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: doc/code drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "Rule ID E021 is assigned to two unrelated violation types across evidence.py and links.py",
    "location": "src/aiv/lib/validators/evidence.py:334",
    "ids": [
      "F216"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: tier-drift",
    "severity": "medium",
    "class": "doc/code drift",
    "title": "R0 required evidence classes differ between guard definition and evidence-builder output",
    "location": "tests/unit/test_guard.py:449",
    "ids": [
      "F229"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: error-handling",
    "severity": "medium",
    "class": "error-handling",
    "title": "guard/runner.py main() has no exception handling around env parsing or API calls — raw tracebacks in CI",
    "location": "src/aiv/guard/runner.py:393",
    "ids": [
      "F239"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_init.py :: resource/error-handling",
    "severity": "medium",
    "class": "resource/error-handling",
    "title": "Discarded subprocess result before filesystem assertion in test_cli_init.py",
    "location": "tests/unit/test_cli_init.py:54-69,75-82,128-135,192-197",
    "ids": [
      "F244"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_commit_skip.py :: resource/error-handling",
    "severity": "medium",
    "class": "resource/error-handling",
    "title": "Discarded _run_aiv_commit return value before asserting on generated evidence files",
    "location": "tests/unit/test_cli_commit_skip.py:117-118,130-131",
    "ids": [
      "F245"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: resource/error-handling",
    "severity": "medium",
    "class": "resource/error-handling",
    "title": "test_functional_plus_packet_validates does not patch _load_hook_config, creating environment dependency",
    "location": "tests/unit/test_pre_commit_hook.py:157-172",
    "ids": [
      "F246"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_evidence_collector.py :: resource/error-handling",
    "severity": "medium",
    "class": "resource/error-handling",
    "title": "Overly broad patch of stdlib pathlib.Path.read_text in test_collect_new_file_fallback",
    "location": "tests/unit/test_evidence_collector.py:100-101",
    "ids": [
      "F247"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: injection",
    "severity": "low",
    "class": "injection",
    "title": "URL injection via unvalidated git-remote owner/repo into GitHub API URLs",
    "location": "src/aiv/cli/main.py:639-700",
    "ids": [
      "F16",
      "F18",
      "F88"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: test-doc-drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": "TestEvidenceTodoSeverity docstring pins implementation line numbers that will drift",
    "location": "tests/unit/test_auditor.py:243-244",
    "ids": [
      "F40",
      "F170",
      "F225"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_coverage.py :: tier-drift",
    "severity": "low",
    "class": "intent mismatch",
    "title": "test_r0_has_class_b_and_a asserts Class E presence for R0, but R0 does not require E per REQUIRED_CLASSES",
    "location": "tests/unit/test_coverage.py:36-40",
    "ids": [
      "F41",
      "F112",
      "F228"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_init.py :: error-handling",
    "severity": "low",
    "class": "error-handling",
    "title": "Six subprocess.run calls in test_cli_init.py discard results without check=True",
    "location": "tests/unit/test_cli_init.py:54-59,63-68,76-81,128-133,141-146,190-195",
    "ids": [
      "F62",
      "F131",
      "F179"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/integration/test_svp_full_workflow.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "Inline __import__(\"os\") hides os dependency from static analysis",
    "location": "tests/integration/test_svp_full_workflow.py:51",
    "ids": [
      "F126",
      "F182",
      "F251"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_svp.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "Rating-engine import placed mid-file after all test classes",
    "location": "tests/unit/test_svp.py:676",
    "ids": [
      "F128",
      "F185",
      "F248"
    ],
    "n": 3,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: correctness/logic",
    "severity": "low",
    "class": "correctness/logic",
    "title": "test_functional_plus_packet_validates omits _load_hook_config patch present in _mock_main, making it sensitive to the actual .aiv.yml on disk",
    "location": "tests/unit/test_pre_commit_hook.py:157-172",
    "ids": [
      "F82",
      "F13"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: logic-error",
    "severity": "low",
    "class": "logic-error",
    "title": "Variable existence checked via dir() instead of locals() — unreliable scope test",
    "location": "src/aiv/cli/main.py:1664",
    "ids": [
      "F234",
      "F28"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: doc/code drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": "Test method named 'test_template_is_not_packet' but asserts template IS a packet",
    "location": "tests/unit/test_pre_commit_hook.py:35-38",
    "ids": [
      "F37",
      "F224"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/config.py :: error-handling",
    "severity": "low",
    "class": "error-handling",
    "title": "load_hook_config silently falls back to defaults on any YAML error",
    "location": "src/aiv/lib/config.py:284-285",
    "ids": [
      "F60",
      "F231"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_validators.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "Redundant IntentSection re-import inside fixture in test_validators.py",
    "location": "tests/unit/test_validators.py:394",
    "ids": [
      "F249",
      "F67"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/cli/main.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "Redundant import subprocess as _sp shadows already-imported subprocess",
    "location": "src/aiv/cli/main.py:1489",
    "ids": [
      "F121",
      "F235"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: error-handling",
    "severity": "low",
    "class": "error-handling",
    "title": "test_functional_plus_packet_validates omits _load_hook_config patch, unlike _mock_main",
    "location": "tests/unit/test_pre_commit_hook.py:157",
    "ids": [
      "F130",
      "F183"
    ],
    "n": 2,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/change.py :: correctness",
    "severity": "low",
    "class": "correctness",
    "title": "detect_untracked_commits() silently returns [] when first tracked commit has no parent",
    "location": "src/aiv/lib/change.py:233",
    "ids": [
      "F4"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/runner.py :: correctness",
    "severity": "low",
    "class": "correctness",
    "title": "Verification Methodology missing-section error suppressed when other required sections also absent",
    "location": "src/aiv/guard/runner.py:249-253",
    "ids": [
      "F7"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_coverage.py :: test-doc-drift",
    "severity": "low",
    "class": "correctness/logic",
    "title": "Test named 'test_multi_hunk_line_numbers' never asserts on line numbers",
    "location": "tests/unit/test_coverage.py:120",
    "ids": [
      "F11"
    ],
    "n": 1,
    "runtime": false
  },
  {
    "sig": "src/aiv/lib/config.py :: doc-code-drift",
    "severity": "low",
    "class": "doc-code-drift",
    "title": ".gitignore listed as functional file requiring a packet; undocumented in developer guidance",
    "location": "src/aiv/lib/config.py:163",
    "ids": [
      "F30"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/models.py :: doc-code-drift",
    "severity": "low",
    "class": "doc-code-drift",
    "title": "GuardResult.compliance_level never set to COMPLIANT on pass; stays at Pydantic default L1",
    "location": "src/aiv/guard/models.py:182",
    "ids": [
      "F31"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_auditor.py :: tier-drift",
    "severity": "low",
    "class": "intent mismatch",
    "title": "Auto-fix test approves a 'fixed' Class E link that uses /blob/main/ — itself a CLASS_E_MUTABLE violation",
    "location": "tests/unit/test_auditor.py:370-381",
    "ids": [
      "F39"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/models.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "GuardResult.compliance_level is never computed — hardcoded to 'L1'",
    "location": "src/aiv/guard/models.py:123",
    "ids": [
      "F57"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/svp/lib/rating.py :: correctness",
    "severity": "low",
    "class": "correctness",
    "title": "score_session() never emits bug_missed RatingEvents; bugs_missed and ELO penalty are permanently zero",
    "location": "src/aiv/svp/lib/rating.py:23-124",
    "ids": [
      "F73"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/parser.py :: correctness",
    "severity": "low",
    "class": "correctness",
    "title": "Multi-line or prose-trailing http artifact string passed whole to ArtifactLink, silently bypassing immutability checks",
    "location": "src/aiv/lib/parser.py:585",
    "ids": [
      "F74"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/canonical.py :: correctness",
    "severity": "low",
    "class": "correctness",
    "title": "validate_canonical() only validates attestations[0]; all subsequent attestations are unchecked",
    "location": "src/aiv/guard/canonical.py:159-160",
    "ids": [
      "F75"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_commit_skip.py :: correctness/logic",
    "severity": "low",
    "class": "correctness/logic",
    "title": "Return value of _run_aiv_commit discarded in skip-checks evidence tests — command failures produce misleading assertion errors",
    "location": "tests/unit/test_cli_commit_skip.py:119,132",
    "ids": [
      "F81"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": ".cursorrules :: doc/code drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": ".cursorrules workflow includes redundant git add step that aiv commit handles internally",
    "location": ".cursorrules:9 vs src/aiv/cli/main.py:1879",
    "ids": [
      "F102"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/pipeline.py :: doc/code drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": "R0 with --skip-checks produces a Class A placeholder header that satisfies the pipeline Class A requirement",
    "location": "src/aiv/lib/validators/pipeline.py:182 vs src/aiv/cli/main.py:1465-1649",
    "ids": [
      "F103"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "Standard library modules imported inside functions rather than at module level",
    "location": "src/aiv/guard/github_api.py:188,193",
    "ids": [
      "F120"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/auditor.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "_LOCAL_FILE_PATHS maps only two project-specific filenames — unusable in user repos",
    "location": "src/aiv/lib/auditor.py:128-131",
    "ids": [
      "F122"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: resource-handling",
    "severity": "low",
    "class": "resource-handling",
    "title": "O(n²) nested ast.walk in resolve_changed_symbols — no bound on large files",
    "location": "src/aiv/lib/evidence_collector.py:620-626",
    "ids": [
      "F123"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_language_drivers.py :: error-handling",
    "severity": "low",
    "class": "error-handling",
    "title": "Module-level try/except catches only ImportError; non-ImportError from TreeSitterDriver() propagates uncaught",
    "location": "tests/unit/test_language_drivers.py:90",
    "ids": [
      "F129"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/anti_cheat.py :: logic-bug/operator-precedence",
    "severity": "low",
    "class": "logic-bug/operator-precedence",
    "title": "Operator-precedence bug causes +++ file-header lines to advance line counter",
    "location": "src/aiv/lib/validators/anti_cheat.py:132-142",
    "ids": [
      "F132"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/svp/lib/rating.py :: logic-bug/metric-error",
    "severity": "low",
    "class": "logic-bug/metric-error",
    "title": "bugs_caught metric conflates confirmed-bug probe events with falsification-scenario events",
    "location": "src/aiv/svp/lib/rating.py:147",
    "ids": [
      "F138"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/parser.py :: logic-bug/url-extraction",
    "severity": "low",
    "class": "logic-bug/url-extraction",
    "title": "artifact_raw.startswith('http') check bypasses URL extraction for multi-line or padded artifact text",
    "location": "src/aiv/lib/parser.py:584-586",
    "ids": [
      "F139"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/canonical.py :: tier-drift",
    "severity": "low",
    "class": "logic-bug/incomplete-error-reporting",
    "title": "validate_canonical returns on first missing required evidence class, suppressing subsequent missing-class errors",
    "location": "src/aiv/guard/canonical.py:231-235",
    "ids": [
      "F140"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: correctness/logic",
    "severity": "low",
    "class": "correctness/logic",
    "title": "test_valid_markdown_packet asserts only a mode flag, not the validation outcome",
    "location": "tests/unit/test_guard.py:408-425",
    "ids": [
      "F144"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: ssrf",
    "severity": "low",
    "class": "ssrf",
    "title": "owner/repo from git remote interpolated into GitHub API URL path",
    "location": "src/aiv/guard/github_api.py:42",
    "ids": [
      "F150"
    ],
    "n": 1,
    "runtime": false
  },
  {
    "sig": "tests/unit/test_models.py :: ssrf",
    "severity": "low",
    "class": "SSRF",
    "title": "ArtifactLink.from_url accepts arbitrary URL schemes with no block test",
    "location": "tests/unit/test_models.py:87-89",
    "ids": [
      "F152"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_coverage.py :: injection",
    "severity": "low",
    "class": "injection",
    "title": "Config loading test omits YAML unsafe-deserialization attack surface",
    "location": "tests/unit/test_coverage.py:398-407",
    "ids": [
      "F155"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/evidence.py :: doc-code-drift/missing-check",
    "severity": "low",
    "class": "doc-code-drift/missing-check",
    "title": "_validate_differential Zero-Touch check covers only 5 DB CLI keywords, misses all other manual reproduction steps",
    "location": "src/aiv/lib/validators/evidence.py:242",
    "ids": [
      "F162"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: naming-inversion",
    "severity": "low",
    "class": "naming-inversion",
    "title": "Test method name inverts its own assertion",
    "location": "tests/unit/test_pre_commit_hook.py:35",
    "ids": [
      "F163"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_models.py :: over-broad-assertion",
    "severity": "low",
    "class": "over-broad-assertion",
    "title": "test_frozen_model uses bare pytest.raises(Exception), masking the expected immutability exception",
    "location": "tests/unit/test_models.py:97",
    "ids": [
      "F171"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/anti_cheat.py :: correctness/logic",
    "severity": "low",
    "class": "correctness/logic",
    "title": "Line counter advances for +++ header lines due to missing negation in OR branch",
    "location": "src/aiv/lib/validators/anti_cheat.py:132-142",
    "ids": [
      "F186"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_cli_commit_skip.py :: logic",
    "severity": "low",
    "class": "logic",
    "title": "Missing length guard before indexing evidence_files[0] in test_reason_in_methodology",
    "location": "tests/unit/test_cli_commit_skip.py:134",
    "ids": [
      "F194"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_commit_hook.py :: logic",
    "severity": "low",
    "class": "logic",
    "title": "test_functional_plus_packet_validates omits _load_hook_config mock, making test environment-sensitive",
    "location": "tests/unit/test_pre_commit_hook.py:158-172",
    "ids": [
      "F195"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_guard.py :: injection",
    "severity": "low",
    "class": "injection",
    "title": "Injection: inline-json scope inventory reference accepts unvalidated JSON payload",
    "location": "tests/unit/test_guard.py:92",
    "ids": [
      "F207"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_pre_push_hook.py :: authz",
    "severity": "low",
    "class": "authz",
    "title": "Authz: pre-push hook verified by content check only; no test confirms actual git-push execution triggers the hook",
    "location": "tests/unit/test_pre_push_hook.py:189",
    "ids": [
      "F208"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/validators/structure.py :: test-doc-drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": "StructureValidator class docstring claims to check E001, E003, E006, E007 but validate() checks none of them",
    "location": "src/aiv/lib/validators/structure.py:24-30",
    "ids": [
      "F218"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "scripts/map_packets.py :: husky-drift",
    "severity": "low",
    "class": "doc/code drift",
    "title": "scripts/map_packets.py indexes only Layer 2 VERIFICATION_PACKET_*.md files; Layer 1 EVIDENCE_*.md files in .github/aiv-evidence/ are invisible to it",
    "location": "scripts/map_packets.py:15",
    "ids": [
      "F219"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/change.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "json.JSONDecodeError before Exception in except tuple is dead code",
    "location": "src/aiv/lib/change.py:82",
    "ids": [
      "F230"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/manifest.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "guard/manifest.py entire module is unreachable dead code — no callers in audited surface",
    "location": "src/aiv/guard/manifest.py:1",
    "ids": [
      "F240"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/parser.py :: dead-code",
    "severity": "low",
    "class": "dead-code",
    "title": "ParsedSection.raw_start and raw_end are written but never read — dead state fields",
    "location": "src/aiv/lib/parser.py:38",
    "ids": [
      "F241"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/language_drivers/treesitter_driver.py :: logic-error",
    "severity": "low",
    "class": "logic-error",
    "title": "Empty bytes from tree-sitter node adds empty string to imported-symbols set — false-positive symbol matching",
    "location": "src/aiv/lib/language_drivers/treesitter_driver.py:249",
    "ids": [
      "F242"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_language_drivers.py :: resource/error-handling",
    "severity": "low",
    "class": "resource/error-handling",
    "title": "try/except at module level catches only ImportError, leaving AttributeError unhandled during driver capability probe",
    "location": "tests/unit/test_language_drivers.py:90-95",
    "ids": [
      "F250"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/models.py :: path-traversal",
    "severity": "info",
    "class": "correctness",
    "title": "EvidenceClass.from_string() startswith allows multi-character prefix false positives",
    "location": "src/aiv/lib/models.py:54",
    "ids": [
      "F2"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "tests/unit/test_svp.py :: injection",
    "severity": "info",
    "class": "injection",
    "title": "Code injection risk: FalsificationScenario.test_code stores executable Python without documented sandboxing (UNVERIFIED)",
    "location": "tests/unit/test_svp.py:625-630",
    "ids": [
      "F22"
    ],
    "n": 1,
    "runtime": false
  },
  {
    "sig": "src/aiv/lib/models.py :: tier-drift",
    "severity": "info",
    "class": "logic-error",
    "title": "has_provenance_evidence checks claims only; ignores evidence_classes_present field",
    "location": "src/aiv/lib/models.py:268",
    "ids": [
      "F34"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/guard/github_api.py :: path-traversal",
    "severity": "info",
    "class": "path_traversal",
    "title": "Arbitrary file read via GITHUB_EVENT_PATH environment variable",
    "location": "src/aiv/guard/github_api.py:88",
    "ids": [
      "F89"
    ],
    "n": 1,
    "runtime": true
  },
  {
    "sig": "src/aiv/lib/evidence_collector.py :: dead-code",
    "severity": "info",
    "class": "dead-code",
    "title": "'import xdist as _' immediately discards the imported symbol — should use importlib.util.find_spec",
    "location": "src/aiv/lib/evidence_collector.py:343",
    "ids": [
      "F243"
    ],
    "n": 1,
    "runtime": true
  }
]
```
