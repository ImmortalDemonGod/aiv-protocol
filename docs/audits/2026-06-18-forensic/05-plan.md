# 05 — Execution Plan

_Generated 2026-06-18 01:51:36 · branch `claude/eloquent-goodall-sqfrhf` · forensic-audit-pipeline (consolidated)_

**79 change items** — convergence: NOT-CONVERGED: ["P77","P79"].

| ID | Change | Links | Location | Verification | Depends |
| --- | --- | --- | --- | --- | --- |
| P1 | Establish a single canonical tier->evidence-class requirement map (pipeline._TIER_REQUIRED is authoritative) and derive ALL human-facing rubrics from it instead of hand-maintaining them. Reconcile the R1={A,B,E} / R2 adds C / R3 adds D,F mapping across every surface, and resolve the R0 Class-E disagreement (builder always emits Class E for R0 but guard REQUIRED_CLASSES['R0']==['A','B']). | F23,F24,F159,F212,F228,F229,F41,F112 | src/aiv/lib/validators/pipeline.py:183 (canonical); consumers src/aiv/hooks/pre_commit.py:237-243, .husky/pre-commit:93-99, .cursorrules:18-21, src/aiv/cli/main.py:308-310, src/aiv/guard/canonical.py:25 | New test asserts each printed rubric string equals pipeline._TIER_REQUIRED for R0-R3; an R1 packet with only A+B is blocked with the SAME message the installed rubric instructed; test_validators tier tests and test_guard REQUIRED_CLASSES test both pass without contradiction. |  |
| P2 | Extract PACKET_PREFIXES / EVIDENCE_PREFIX into one shared module and import it everywhere; teach scripts/map_packets.py to also scan Layer-1 .github/aiv-evidence/EVIDENCE_*.md so Layer-1 coverage is visible in the evidence index. | F33,F219 | new src/aiv/lib/packet_paths.py; consumers src/aiv/hooks/pre_commit.py:46, src/aiv/hooks/pre_push.py:40, src/aiv/lib/auditor.py:51, scripts/map_packets.py:15 | Unit test imports the constant from all four modules and asserts identity; map_packets test with only an EVIDENCE_ file shows the covered file as mapped, not unmapped. |  |
| P3 | Bring the bash .husky/pre-commit hook to parity with the Python hook (or replace its body with a call to `python -m aiv.hooks.pre_commit`): recognize the PACKET_ prefix and Layer-1 EVIDENCE_ files, and implement the active-change-context bypass. Update the pre_commit.py module docstring rule inventory (Rules 1-10) so it is not stale. | F96,F97,F98,F210,F211 | .husky/pre-commit:61; src/aiv/hooks/pre_commit.py:7,46-52,342,381-404,424 | Integration test stages the exact `aiv commit` output (one EVIDENCE_*.md + one source file) and runs both hooks; both exit 0. A >2-file commit inside an active `aiv begin` context is allowed by both. Docstring rule list matches implemented rules. | P2 |
| P4 | Canonicalize the PR-body-supplied packet path before reading: call Path(file_path).resolve() and assert it stays within the repository root, in addition to the `.github/` prefix check. | F14,F83,F146,F197 | src/aiv/guard/runner.py:191-204 | Unit test: a body value like `.github/../../../../etc/passwd` is rejected (no read) while a legitimate `.github/aiv-packets/...` path still resolves and reads. |  |
| P5 | Add an SSRF guard to the link validator: enforce a scheme allowlist {http,https}, reject file://ftp://gopher://, and block loopback/link-local/RFC-1918 hosts (resolve and check before request); do not follow redirects to internal hosts. | F15,F84,F147,F196 | src/aiv/lib/validators/links.py:163-176 | Unit tests assert urlopen is NOT reached for file:///etc/shadow, http://169.254.169.254/latest/meta-data/, and http://127.0.0.1/; a normal https URL still issues the HEAD check. |  |
| P6 | Validate owner/repo parsed from the git remote against `^[A-Za-z0-9._-]+$` and percent-encode them before interpolating into GitHub API URLs and generated markdown links; reject crafted remotes containing ?,#,@. | F16,F85,F88 | src/aiv/cli/main.py:639-700,683,843 | Unit test with a remote URL containing query/fragment characters raises a controlled error; generated markdown link is well-formed for a normal remote. |  |
| P7 | URL-encode `path` and `ref` (and validate owner/repo segments) in GitHubAPI.get_file_content using urllib.parse.quote, matching the encoding already applied in search_code; guard against `owner/../` style GITHUB_REPOSITORY values. | F86,F198,F150 | src/aiv/guard/github_api.py:176,42 | Unit test: a path `README.md?ref=main&per_page=100` is encoded so the effective request path/query is unchanged; malformed GITHUB_REPOSITORY rejected. |  |
| P8 | Catch the parent urllib.error.URLError (DNS/refused/SSL) in _request and _request_bytes and re-raise as GitHubAPIError; wrap runner.main() so missing env vars (KeyError) and API failures produce a structured message + exit code rather than a raw traceback. | F115,F174,F237,F239 | src/aiv/guard/github_api.py:43-76; src/aiv/guard/runner.py:393 | Unit test: a simulated URLError surfaces as GitHubAPIError; running main() with GITHUB_TOKEN unset prints a diagnostic and exits non-zero, no traceback. |  |
| P9 | Stop silently truncating on pagination errors: signal/raise when list_pr_files or list_run_artifacts breaks mid-pagination so scope/artifact checks are not run against an incomplete list; catch binascii.Error on base64.b64decode in get_file_content; catch JSONDecodeError on the GITHUB_EVENT_PATH read. | F44,F45,F53,F116 | src/aiv/guard/github_api.py:116-117,159-160,188,88 | Unit tests: a page-2 API error marks results as truncated (not a silent PASS); invalid base64 and malformed event JSON yield handled errors, not crashes. | P8 |
| P10 | Remove or wire the unreachable download_artifact_zip and search_code methods; hoist the lazy `import base64`/`import urllib.parse` to module level; add a __repr__/__str__ that redacts the token; replace canonical.py's __import__('json') with a top-level import. | F177,F178,F120,F200,F201 | src/aiv/guard/github_api.py:60,191,188,193,40; src/aiv/guard/canonical.py:442 | Grep confirms no remaining callers of removed methods; repr(GitHubAPI(...)) contains no token characters; lint passes with module-level imports. |  |
| P11 | Document and constrain the GITHUB_EVENT_PATH trust boundary: treat the variable as runner-controlled only, and note in the spec that local/CI environments where it is attacker-settable can read arbitrary files. | F89 | src/aiv/guard/github_api.py:88; SPECIFICATION.md | Code comment + SPEC paragraph present; no behavioral regression in guard tests. |  |
| P12 | Enforce a maximum payload length on the inline-b64-json scope-inventory ref before base64.b64decode, and add adversarial test coverage for oversized/crafted inline-json and inline-b64-json payloads. | F199,F207 | src/aiv/guard/canonical.py:438-441; tests/unit/test_guard.py:92 | Unit test: a multi-megabyte base64 payload is rejected with a CT error before decode; a crafted deeply-nested inline-json payload is bounded/rejected. |  |
| P13 | Pass github.actor into the CI step via an `env:` variable and reference $ACTOR in the bash heredoc instead of interpolating ${{ github.actor }} directly into shell. | F148 | .github/workflows/ci.yml:387 | Workflow lint passes; the actor value is consumed only through an env var; no direct expression interpolation into shell. |  |
| P14 | Match Class-F justifications to the SPECIFIC anti-cheat finding (file/violation type) instead of letting any one >20-char Class-F claim clear every finding; require a justification that references the affected test file or violation. | F134,F187 | src/aiv/lib/validators/anti_cheat.py:192-213 | Unit test: deleting assertions in test_a.py and skipping a test in test_b.py with a single generic Class-F claim still produces findings for both files. |  |
| P15 | Parenthesize the diff line-counter condition so `+++` headers do not increment current_line; correct operator precedence between the `+` and context clauses. | F1,F132,F186,F11 | src/aiv/lib/validators/anti_cheat.py:132-142 | Unit test (strengthen test_multi_hunk_line_numbers) asserts deleted-line line_number is exactly correct across multiple hunks containing `+++` headers. |  |
| P16 | Make packet validation fail CLOSED: on any infrastructure error in _validate_packet, return False (block) or raise, instead of `except Exception: ... return True`. Surface the error to the developer. | F43,F233 | src/aiv/hooks/pre_commit.py:212-214 | Unit test: a forced exception inside _validate_packet causes main() to block the commit (non-zero exit), not pass. |  |
| P17 | Wrap the NamedTemporaryFile and mkdtemp audit_dir lifecycle in try/finally so both are cleaned up even when subprocess raises TimeoutExpired/FileNotFoundError. | F113,F175 | src/aiv/hooks/pre_commit.py:155-214 | Unit test: an exception during packet validation leaves no orphaned temp file or audit_dir on disk. | P16 |
| P18 | Before marking A-002/A-005 PASS, require run_data conclusion=='success' AND status=='completed'; a failed/cancelled/in-progress run that uploaded an aiv-evidence artifact must NOT yield passing Class-A evidence. | F135 | src/aiv/guard/runner.py:336-365 | Unit test: a workflow run with conclusion=='failure' (artifact present) does not produce A-002/A-005 PASS. |  |
| P19 | Honor the documented 'never raises' contract of evidence_collector._run_git/_run by catching FileNotFoundError and TimeoutExpired and returning empty string; detect the resulting degraded state (empty diff, 'unknown' SHA) and signal it so collect_class_b/collect_class_c/collect_class_a do not emit falsely-clean or 404-permalink evidence; guard collect_class_a against missing pytest/ruff/mypy. | F47,F114,F173,F232,F52,F176 | src/aiv/lib/evidence_collector.py:249-255,283-285,348,457 | Unit tests with git/pytest absent produce a structured degraded result (no traceback); a git failure during collect_class_c does NOT report anti_cheat_clean=True. |  |
| P20 | Fix the Class-B permalink SHA: it currently equals the parent commit because rev-parse HEAD runs before the commit. Either compute the post-commit SHA in the close path or clearly mark the permalink SHA as provisional and patch it post-commit. | F29 | src/aiv/lib/evidence_collector.py:283 | Test asserts the generated Class-B permalink references the commit that introduces the files, not its parent. | P19 |
| P21 | Replace the O(N^2) per-node `ast.walk(tree)` parent-class lookup with a single precomputed child->parent map (correctly handling classes nested in functions); replace `import xdist as _` with importlib.util.find_spec('xdist'). | F54,F123,F243 | src/aiv/lib/evidence_collector.py:620-626,343 | Test: a method of a class nested inside a function gets the correct ClassName.method symbol; no second tree walk per node; xdist presence detected without importing it. |  |
| P22 | In change.load_change, distinguish corrupt-file errors from 'no active change' (narrow the except; drop the redundant `(json.JSONDecodeError, Exception)` ordering) so corruption is surfaced; in get_untracked_commits handle the initial/root commit (use `--root` or detect the no-parent case) instead of swallowing CalledProcessError as zero commits. | F50,F230,F4 | src/aiv/lib/change.py:82,233 | Tests: a corrupt change file raises/logs (not silent None); an initial-commit repo returns the real untracked-commit list, not []. |  |
| P23 | In pre_commit._run_git, check result.returncode and treat git failure (git missing / not a repo) as an error (fail closed or diagnostic) rather than returning '' which _staged_files reads as 'nothing staged' and exits 0. | F51 | src/aiv/hooks/pre_commit.py:65-71 | Unit test: a git invocation failure causes the hook to NOT exit 0 silently. | P16 |
| P24 | Add rotation/size-cap/cleanup for the .cache/bb-safety-snapshots/ directory created on every pre-commit run so snapshots do not accumulate unbounded. | F55 | src/aiv/hooks/pre_commit.py:117-140 | Unit test: after N runs only the most recent K snapshots remain (or total size is bounded). |  |
| P25 | Replace the silent `except Exception: pass` in load_hook_config with a logged warning so a corrupt/mis-typed .aiv.yml is visible; document functional_root_files (.gitignore) and the .husky/ self-modification circularity; add a test that the loader uses yaml.safe_load (object-injection payload rejected). | F60,F231,F215,F30,F155 | src/aiv/lib/config.py:284-285,154,163 | Test: a malformed .aiv.yml emits a warning and falls back; a `!!python/object/apply` payload does NOT execute (safe_load); docs mention .gitignore and .husky circularity. |  |
| P26 | Remove `--no-verify` from the close/commit packet-commit calls so the packet commit passes through the pre-commit hook (Rule 6 already allows packet-only commits, making the flag unnecessary). Update the close docstring to stop claiming non-bypassable while bypassing. | F6,F17,F26,F48,F69,F87,F99,F209,F149 | src/aiv/cli/main.py:1233-1241,1236-1237,969-979 | Integration test: `aiv close` commits the packet WITHOUT --no-verify and the pre-commit hook runs and passes; grep confirms no --no-verify in the close path. | P16,P3 |
| P27 | Replace the bare `except Exception: pass` in the close evidence-extraction loop with a narrowed except that logs the failing file and does NOT silently substitute the untestable generic boilerplate claim for real evidence-derived claims. | F49 | src/aiv/cli/main.py:1085 | Test: a corrupt/missing evidence file surfaces a diagnostic and the packet is not generated with only boilerplate claims. |  |
| P28 | Add the `--` separator before path arguments in the git-add invocations, and wrap CalledProcessError/TimeoutExpired/FileNotFoundError as console.print + raise typer.Exit(1) to match the rest of the CLI. | F18,F117 | src/aiv/cli/main.py:1879,1233 | Test: a filename beginning with `-` is treated as a path, not a flag; a git failure yields a friendly Typer error not a raw traceback. |  |
| P29 | Replace the `"name" in dir()` scope probes with `"name" in locals()` for changed_symbols and class_c_data so empty line_ranges does not produce environment-dependent behavior or a NameError. | F28,F118,F234 | src/aiv/cli/main.py:1664,1721 | Test: the empty-line_ranges path runs without NameError and falls back deterministically. |  |
| P30 | Remove the redundant `import subprocess as _sp` alias (use the already-imported subprocess) and replace the bare `python` pytest invocation with sys.executable to respect the active virtualenv. | F121,F235,F238 | src/aiv/cli/main.py:1488-1489,743 | Lint shows no unused alias; pytest is launched via sys.executable in a venv test. |  |
| P31 | Unify the verification-packet schema version emitted by generate (v2.1) and close (v2.2) to a single value, or add a CHANGELOG/SPEC entry documenting the v2.1->v2.2 difference. | F25 | src/aiv/cli/main.py:514,1143 | Both commands emit the same version string OR a changelog/spec diff for v2.1->v2.2 exists. |  |
| P32 | Run the protocol-audit CI job on pull_request events (not only push to main) so a --no-verify push on a PR branch is caught before merge; align the pre_push.py Layer-3 docstring with the actual trigger coverage. | F32,F101,F214 | .github/workflows/ci.yml:5-7,67; src/aiv/hooks/pre_push.py:15-22 | Workflow triggers protocol-audit on a PR; docstring no longer overstates coverage. |  |
| P33 | Wire EvidenceValidator.validate_file_type_triggers into the pipeline: add a changed_files field to ValidationContext, parse changed paths from the diff, and invoke the method so SQL/migration/dependency/API/Dockerfile changes actually demand Class D (E021/E022). | F46,F158,F217 | src/aiv/lib/validators/evidence.py:261; src/aiv/lib/validators/pipeline.py:34-43,126-128 | Test: a packet whose diff touches a Dockerfile/.sql/pyproject.toml without Class D is blocked by the file-type trigger; grep shows a real call site. |  |
| P34 | Restructure the evidence early-`pass` so github_actions/external link types still reach the E012 (UI state-transition) and E013 (performance benchmark) checks for Class-A claims. | F5 | src/aiv/lib/validators/evidence.py:86-91 | Test: a Class-A UI/performance claim linked to a CI run triggers E012/E013 instead of passing unchallenged. |  |
| P35 | Collapse the two divergent bug-fix/Class-F-adequacy implementations into one shared helper and one justification-vs-description fallback rule so anti_cheat and evidence validators enforce the same standard; broaden the Zero-Touch Class-D manual-execution keyword set beyond the five DB strings. | F59,F161,F162 | src/aiv/lib/validators/evidence.py:415,402,242; src/aiv/lib/validators/anti_cheat.py:207 | Test: the same Class-F claim is assessed identically by both validators; a Class-D reproduction using kubectl/docker exec/ssh is flagged by Zero-Touch. |  |
| P36 | Eliminate the rule-id collisions: E020 means two unrelated things (evidence.py:113 vs pipeline.py:248) and E021 collides (evidence.py:334 vs links.py:140,152). Assign distinct ids or namespace rule ids by validator so downstream suppression/aggregation is unambiguous. | F160,F216 | src/aiv/lib/validators/evidence.py:113,334; src/aiv/lib/validators/pipeline.py:248; src/aiv/lib/validators/links.py:140,152 | Test: each rule_id in emitted findings maps to exactly one message/meaning across all validators. |  |
| P37 | Fix has_provenance_evidence to also consult evidence_classes_present (standalone Class-F evidence section) rather than only PROVENANCE-typed claim objects, so E010 gating is not falsely skipped. | F34 | src/aiv/lib/models.py:268 | Test: a packet with Class F only in a standalone evidence section returns True from has_provenance_evidence. |  |
| P38 | Make ValidationResult.is_valid consistent with status: in strict mode a warning-only packet has status FAIL but is_valid True. Have is_valid reflect status (or factor in strict warnings) so library/CI consumers branching on is_valid cannot pass a strict-failing packet. | F76,F133 | src/aiv/lib/models.py:306-309; src/aiv/lib/validators/pipeline.py:163-169 | Test: strict_mode packet with only WARN findings has is_valid==False (matching status FAIL). |  |
| P39 | Correct the ValidationPipeline class docstring to enumerate all stages including 'Risk-Tier Evidence Requirements' (Stage 5) so it matches the 8-stage reality referenced in the CLI quickstart. | F27,F100 | src/aiv/lib/validators/pipeline.py:48-56,131; src/aiv/cli/main.py:324 | Docstring stage list matches the implemented stages and the quickstart text. |  |
| P40 | Stop the R0 `--skip-checks` Class-A placeholder header from silently satisfying the tier requirement: emit an explicit skip marker (INFO/E019 distinct flag) so a placeholder is not counted as real execution evidence. | F103 | src/aiv/cli/main.py:1465-1649; src/aiv/lib/validators/pipeline.py:182,229 | Test: R0+--skip-checks produces a distinct 'execution evidence skipped' marker rather than a clean Class-A PASS. |  |
| P41 | In GuardResult.finalize set a meaningful compliance_level on PASS (e.g. 'COMPLIANT' or a tier-aware value) and compute graduated levels when WARN-only findings exist; ensure a markdown-only run is not reported as full L1 canonical compliance. | F3,F31,F57,F188 | src/aiv/guard/models.py:182-189,123; src/aiv/guard/runner.py:144-150 | Test: a passed R3 packet and a passed R0 packet report distinguishable compliance_level; a clean pass yields 'COMPLIANT', not the default 'L1'. |  |
| P42 | Compute EvidenceClassResult.valid from actual artifact integrity (URL reachability/SHA pinning), not `valid=present`; or remove the dead field if no independent validation is intended. | F71,F119 | src/aiv/guard/runner.py:381-383 | Test: a present Class-A entry with a broken URL/wrong SHA gets valid=False (or the field is removed and consumers updated). |  |
| P43 | Emit the E-METH methodology diagnostic independently of whether other required sections are already flagged missing, so the methodology gap is always surfaced. | F7 | src/aiv/guard/runner.py:249-253 | Test: a packet missing both required sections AND methodology still reports the targeted E-METH message. |  |
| P44 | In parser._enrich_claims_with_evidence always run _extract_url to isolate the URL before ArtifactLink.from_url (handle multi-line/embedded-prose artifact strings) so http-prefixed multi-line blocks still produce a validated ArtifactLink that gets immutability-checked. | F74,F139,F189 | src/aiv/lib/parser.py:584-586,603 | Test: a multi-line evidence block beginning with https://... yields an ArtifactLink (immutability checked), not a raw-string fallback. |  |
| P45 | Remove the unused ParsedSection.raw_start/raw_end byte-offset fields (or consume them) to eliminate dead state. | F241 | src/aiv/lib/parser.py:38 | Lint/grep shows no readers; tests pass after removal. |  |
| P46 | Only set auto_fixable=True when a commit SHA is actually resolvable; validate _get_introducing_commit output is a real SHA (not trailing garbage) before using it to build URLs/decide auto_fixable; document that _LOCAL_FILE_PATHS only fixes repos containing AUDIT_REPORT.md/SPECIFICATION.md. | F56,F58,F122 | src/aiv/lib/auditor.py:492,115-117,128-131 | Test: an evidence finding with unknown SHA reports auto_fixable=False; a garbage git line is rejected, not used as a SHA. |  |
| P47 | Apply the Layer-2 TODO/classified_by/blast_radius/numbered-claim TODO checks to Layer-1 evidence files in _check_evidence; and make the claims-section regex accept the `## Claims` heading alternative (currently only `## Claim(s)`), so CLAIM_TODO and FIX_NO_CLASS_F checks are not skipped. | F137,F190 | src/aiv/lib/auditor.py:434-578,390-401 | Tests: an evidence file with classified_by:'TODO' is flagged; a packet using `## Claims` with TODO placeholders and no Class F on a bug fix is flagged. |  |
| P48 | Wrap the per-packet read_text/write_text in auditor.audit in try/except so a single unreadable/undeletable file does not abort the whole run; emit partial results. | F236 | src/aiv/lib/auditor.py:236-247 | Test: one unreadable packet among several yields findings for the others plus a per-file error, not a total crash. |  |
| P49 | Fix the Class-E auto-fix so it SHA-pins (never emits a mutable /blob/main/ URL that the auditor's own CLASS_E_MUTABLE rule would re-flag) and URL-encodes/sanitizes the local filename (reject ../, %, #). Refresh the stale hard-coded auditor.py line-number references in test docstrings. | F39,F40,F93,F111,F154,F206,F170,F225 | src/aiv/lib/auditor.py (auto-fix path); tests/unit/test_auditor.py:370-381,243-244 | Test: auto-fix output passes a follow-up audit (no CLASS_E_MUTABLE); a filename containing ../ is encoded/rejected; docstring line refs are symbolic, not pinned. |  |
| P50 | Resolve the ELO tier boundary contradiction: either have VerifierRating.__init__ derive tier via from_elo (so elo=500 -> COMPETENT) or set the COMPETENT threshold to >500 (so from_elo(500)->NOVICE). Pick one and make the constructor and from_elo agree, then align the three conflicting tests. | F9,F77,F142,F191 | src/aiv/svp/lib/rating.py; VerifierTier.from_elo and VerifierRating.__init__ (svp models) | Test: from_elo(500) and a freshly-constructed VerifierRating(elo=500).tier return the same tier; no contradictory assertions remain. |  |
| P51 | Make score_session emit RatingEvent(event_type='bug_missed', -25) when a falsification scenario is missed/unfalsified, and count bugs_caught only from confirmed probe findings (not from falsified-scenario events), so bugs_missed is recorded and bugs_caught is not inflated. | F73,F138 | src/aiv/svp/lib/rating.py:23-124,147 | Tests: a missed bug applies the -25 penalty and increments bugs_missed; a verifier with 0 confirmed bugs but 5 falsified scenarios does NOT report bugs_caught=5. |  |
| P52 | In session validation, make predicted_complexity Optional (or remove the unreachable None branch) so S004 is reachable as intended; and remove the early `return False` in _validate_trace so all S006/S015 violations across all traces are collected. | F70,F136 | src/aiv/svp/lib/validators/session.py:113,156-157,183-185 | Test: a session with 3 traces each violating S006 reports 3 errors (not 1); S004 path is reachable. |  |
| P53 | Iterate ALL attestations (not just [0]) in validate_canonical, and collect all missing required classes before returning instead of returning on the first missing class. | F75,F140 | src/aiv/guard/canonical.py:159-160,231-235 | Tests: a second invalid/unsigned attestation is flagged; an R3 packet missing C,D,F reports all three, not just the first. |  |
| P54 | Align the StructureValidator class docstring with the checks actually implemented (E002, E005, E008), noting parser-time enforcement for E001/E003/E006/E007 rather than listing them as performed here. | F218 | src/aiv/lib/validators/structure.py:24-30 | Docstring enumerates only the checks the validate() method performs (with parser-delegation notes). |  |
| P55 | Replace `normalized.startswith(member.value)` with equality so 'AB'/'AF'/'A1' do not match evidence class 'A'. | F2 | src/aiv/lib/models.py:54 | Test: an input 'AB' does not resolve to EvidenceClass A; valid single-letter inputs still resolve. |  |
| P56 | Tighten the SHA-pinned classification in ArtifactLink.from_url so an all-hex mutable tag (>=7 hex chars) is not mistaken for an immutable commit SHA: require canonical length (7/40) plus context, or document the limitation explicitly. | F72 | src/aiv/lib/models.py:132-133 | Test: a 7-char all-hex tag ref is not classified as immutable/SHA-pinned (still warns). |  |
| P57 | Skip empty decoded import names in _extract_named_imports so an empty bytes node does not add '' to the imports set and cause false-positive coverage matches downstream. | F242 | src/aiv/lib/language_drivers/treesitter_driver.py:249 | Test: a malformed/anonymous import node does not add '' to imported_symbols; find_covering_tests does not spuriously match. |  |
| P58 | Change the cross-claim leakage assertion operator from OR to AND so the test fails when EITHER claim 2 OR claim 3 incorrectly reuses claim 1's unlinked artifact. | F8,F78,F141,F192,F226 | tests/unit/test_validators.py:606-610 | With artifacts=['src/handler.py','src/handler.py','See Evidence'] the assertion now FAILS (catches the partial bug). |  |
| P59 | Guard the json.loads(result.stdout) calls in the SVP failure tests: assert stdout looks like JSON (or wrap in try/except with a descriptive re-raise) so a non-JSON error path produces a meaningful AssertionError, not a JSONDecodeError. | F12,F80 | tests/integration/test_svp_full_workflow.py:247,309 | A non-JSON stdout on the failure path yields a clear assertion message identifying the real CLI error. |  |
| P60 | Strengthen the TestAutoFix tests to actually assert remediation: capture and assert on post-fix file content (SHA replaced / pending resolved) and on result.packets_scanned/findings, instead of discarding read_text and audit() results; and make test_evidence_dir_none_skips_scan populate a real evidence file and assert it is NOT scanned. | F10,F42,F61,F65,F79,F110,F124,F168,F181,F227 | tests/unit/test_auditor.py:359-381,875-884 | Tests fail if the auto-fix writes nothing/corrupts the file or if evidence_dir=None still scans a present evidence file. | P47,P49 |
| P61 | Capture and assert result.returncode==0 (or pass check=True) on the `aiv init` subprocess invocations so an init failure surfaces directly instead of as a misleading filesystem-assertion error. | F62,F131,F179,F244 | tests/unit/test_cli_init.py:54-69,75-83,127-148,190-197 | An induced non-zero `aiv init` exit makes the test report the subprocess failure (with stderr), not a 'directory missing' assertion. |  |
| P62 | Capture the _run_aiv_commit CompletedProcess and assert returncode==0 and len(evidence_files)==1 before indexing in the skip-reason tests, matching the sibling test that already guards index access. | F64,F68,F81,F125,F180,F194,F245 | tests/unit/test_cli_commit_skip.py:114-138 | An induced commit failure produces an explicit returncode assertion failure (and no IndexError). |  |
| P63 | Sanitize/escape the --skip-reason text before writing it into the markdown evidence file (so newlines, '## headings', '---', table pipes, fences cannot forge evidence sections), and add adversarial tests with markdown-injection payloads. | F92,F157,F204 | src/aiv/cli/main.py:1646-1649 (evidence writer); tests/unit/test_cli_commit_skip.py:114-138 | Test: a skip-reason containing '\n## Class A (Execution Evidence)\n- pytest: 999 passed' does not create a parseable forged Class-A section in the evidence file. |  |
| P64 | Stop spreading the full host environment into aiv subprocesses in tests: start from a minimal env dict (only PYTHONPATH/PYTHONUTF8/PATH) and add a top-level `import os` instead of the inline __import__('os') form, so CI secrets are not propagated and the dependency is statically visible. | F21,F95,F126,F153,F182,F251 | tests/integration/test_svp_full_workflow.py:43-61,51; tests/unit/test_cli_commit_skip.py:78-84; tests/unit/test_cli_init.py:44-51 | Subprocess env contains no inherited secret variables; module imports os at top; tests still pass. |  |
| P65 | Wrap the subprocess.run(timeout=30) call in the _run helper with try/except subprocess.TimeoutExpired so a hung aiv subcommand fails as a clear test failure (with captured cmd) rather than an uncaught exception that corrupts the class run. | F63 | tests/integration/test_svp_full_workflow.py:45-61 | An induced hang yields a descriptive test failure, not a raw TimeoutExpired traceback. |  |
| P66 | Patch _load_hook_config in test_functional_plus_packet_validates (and any sibling using raw patch blocks) so the test is not sensitive to a real .aiv.yml in the working directory; route it through the _mock_main helper that already patches all six callables. | F13,F82,F130,F183,F195,F246 | tests/unit/test_pre_commit_hook.py:157-172 | The test produces the same result regardless of a custom .aiv.yml present in cwd. |  |
| P67 | Rename test_template_is_not_packet to reflect the asserted behavior (templates ARE structurally packets) and reconcile the cross-component inconsistency: the hook accepts TEMPLATE files as packets while the auditor excludes them. Decide one policy and align both so a bare template cannot satisfy the gate while leaving no audit trail. | F37,F106,F163,F172 | tests/unit/test_pre_commit_hook.py:35-38; src/aiv/hooks/pre_commit.py:46-52,80; src/aiv/lib/auditor.py:216 (TEMPLATE exclusion via glob filter) | Test name matches assertion; a TEMPLATE-only commit is handled consistently by both hook and auditor (a test asserts the chosen policy). | P2 |
| P68 | Fix the inverted docstring in test_default_branch_not_mutable_with_custom_set so it matches the assertion (is_immutable is False == 'main' remains mutable); the inline comment is already correct. | F38,F143,F166,F222 | tests/unit/test_models.py:296-305; tests/unit/test_validators.py:298 | Docstring and assertion agree; no reviewer would invert the assertion based on the docstring. |  |
| P69 | Strengthen claim-not-verified / weak-assertion tests so they verify behavior, not just string presence: pre-push tests must assert actual interception behavior (or be renamed to documentation checks), test_valid_markdown_packet must assert block_count/warn_count/overall_result, and the R2-optional-D-and-F test must assert BOTH D and F produce INFO. | F107,F108,F109,F144,F167,F169,F184,F223 | tests/unit/test_cli_init.py:139; tests/unit/test_guard.py:401,408-425; tests/unit/test_validators.py:366 | Each test fails if the underlying behavior regresses (e.g. guard blocks all markdown packets, or only D emits INFO). |  |
| P70 | Misc test-correctness cleanups: make the git-log mock reproduce the real `--format=%H --name-only` blank-line-after-SHA layout; replace over-broad pytest.raises(Exception) with the specific frozen-model exception; correct the TestRule8 name/count (two functional files, not three); narrow the global Path.read_text patch to the specific module usage. | F145,F171,F224,F247 | tests/unit/test_auditor.py:514-533; tests/unit/test_models.py:97; tests/unit/test_pre_commit_hook.py:233; tests/unit/test_evidence_collector.py:100-101 | Mock format matches real git output; frozen-model test catches only the expected exception; rule-8 name reflects the actual trigger count; the read_text patch no longer suppresses unrelated I/O. |  |
| P71 | Fix the unsafe default pairing on FalsificationScenario (checked=False with result='confirmed'): default an unchecked scenario to result=None/'pending', and update the test to assert the safe default and to guard .result reads on .checked. | F193 | tests/unit/test_svp.py:262-265; svp FalsificationScenario model | Test: a newly constructed unchecked scenario has result None/'pending', not 'confirmed'; consumers gate on checked. |  |
| P72 | Close the verifier-identity authz gap: bind author_github_id/verifier_id to a trusted source (git commit signature or verified GitHub token) rather than a self-chosen --verifier string, and add adversarial tests that (a) reject a hand-forged .svp/session-pr{N}.json passed to `svp validate`, (b) reject impersonation/empty identifiers, (c) confirm test_code is never exec/eval'd, and (d) exercise the real installed pre-push hook end-to-end. | F22,F91,F94,F156,F205,F208 | src/aiv/svp/lib/validators/session.py:291-298 (S011 author_github_id==verifier_id); .svp/session-pr{N}.json handling; tests/unit/test_svp.py:511; tests/integration/test_svp_full_workflow.py:63; tests/unit/test_pre_push_hook.py:189 | Tests: identical self-chosen --verifier strings no longer trivially satisfy S011 without a trusted binding; a forged session file is rejected; a real git push exercises the pre-push hook. |  |
| P73 | Test hygiene: move the late module-level `from aiv.svp.lib.rating import ...` to the top import block; hoist in-test local imports (subprocess/sys, ArtifactLink/IntentSection) to module level removing the dead duplicate IntentSection re-imports; broaden the treesitter availability guard to catch non-ImportError exceptions so a partial native install yields a skip, not a collection error. | F67,F127,F128,F129,F185,F248,F249,F250 | tests/unit/test_svp.py:676; tests/unit/test_auditor.py:419; tests/unit/test_validators.py:394,500; tests/unit/test_language_drivers.py:90-95 | Imports live at module top; no duplicate IntentSection import; a corrupted tree-sitter native lib produces a skip, not a module-collection failure (covers F129/F250 pattern). |  |
| P74 | Add SSRF negative-test coverage proving internal/cloud-metadata URLs and non-http(s) schemes are blocked before urlopen, including a redirect-to-internal case, and fix the HTTPError mocks to pass an http.client.HTTPMessage (not a bare dict) for hdrs so the mock matches production error handling. | F19,F66,F90,F151,F152,F202,F203 | tests/unit/test_validators.py:427-543,433,487; tests/unit/test_models.py:87-89 | New tests assert LinkValidator(audit_links=True) refuses 169.254.169.254/127.0.0.1/file:// and a public->internal redirect; HTTPError mocks use HTTPMessage. | P5 |
| P75 | Correct the stale SVP integration-test docstrings: Phase 4 is exercised via the `self._run('ownership', ...)` CLI path (not JSON/model injection), and the suite covers Phases 0-4 (five phases incl Phase 0 Sanity), not 1-4. Update module and method docstrings accordingly. | F35,F36,F104,F105,F164,F165,F220,F221 | tests/integration/test_svp_full_workflow.py:3-17,317-322 | Docstrings describe the CLI-driven Phase 4 and enumerate Phases 0-4 consistent with the five phase_N_complete assertions. |  |
| P76 | Detect verification-config tampering: when .aiv.yml is itself staged/modified in a commit that also weakens functional_prefixes (or empties them) alongside functional code without a packet, the pre-commit hook must not read the weakened config to exempt those files — require a packet or refuse the weakening. | F20 | src/aiv/hooks/pre_commit.py (config load at commit time); src/aiv/lib/config.py | Test: a commit that stages an .aiv.yml emptying functional_prefixes plus a functional file with no packet is blocked, not exited 0. | P16,P25 |
| P77 | Resolve manifest.py dead code: either invoke validate_class_a/c/semantic/durable_manifest from the guard pipeline (so per-class evidence is actually validated against manifest content) or remove the module and document the decision. | F240 | src/aiv/guard/manifest.py:23,89,146,177 (validate_class_a/c/semantic/durable_manifest — zero references in src/aiv/guard/runner.py); src/aiv/guard/runner.py | If wired: a test shows Class-A/C manifest content is validated during a guard run; if removed: grep confirms no references and a note records the removal. | P18 |
| P78 | Doc cleanup: align .cursorrules step 2 with the fact that `aiv commit` auto-stages the source file and generated evidence (the manual `git add` changes which diff is available), and remove the ghost 'Replaces the 2244-line inline JS' reference in runner.py whose target does not exist in the repo. | F102,F213 | .cursorrules:9; src/aiv/guard/runner.py:5 | The documented commit workflow matches actual staging behavior; the runner docstring no longer references a nonexistent JS precursor. |  |
| P79 | Quine goal-gap closure (the only non-grounded goal: 'demonstrate the protocol on itself with full pre-commit enforcement'). After the enforcement fixes land (P26 removes the close --no-verify self-exemption, P3 brings the bash hook to parity, P16 makes validation fail-closed, P32 extends CI to PRs), produce primary-source evidence that this repo is maintained under AIV without bypass: run a clean cross-commit audit, confirm the installed pre-commit hook is active, and document the velocity claim in SPEC/README. | goal:quine | repo-wide: .github/aiv-packets/, audit/04-goal.md, SPECIFICATION.md, README.md, .husky/pre-commit, src/aiv/cli/main.py:1233-1241 (close path) | `aiv audit --commits N` runs clean; grep confirms no remaining --no-verify in the close/commit path; pre-commit hook is installed and exercised on a real commit; the goal status is upgradeable from needs-human-confirm to grounded with a cited audit log. | P26,P3,P16,P32 |


## Machine-checkable data

```json
{
  "items": [
    {
      "id": "P1",
      "change": "Establish a single canonical tier->evidence-class requirement map (pipeline._TIER_REQUIRED is authoritative) and derive ALL human-facing rubrics from it instead of hand-maintaining them. Reconcile the R1={A,B,E} / R2 adds C / R3 adds D,F mapping across every surface, and resolve the R0 Class-E disagreement (builder always emits Class E for R0 but guard REQUIRED_CLASSES['R0']==['A','B']).",
      "links_to": "F23,F24,F159,F212,F228,F229,F41,F112",
      "location": "src/aiv/lib/validators/pipeline.py:183 (canonical); consumers src/aiv/hooks/pre_commit.py:237-243, .husky/pre-commit:93-99, .cursorrules:18-21, src/aiv/cli/main.py:308-310, src/aiv/guard/canonical.py:25",
      "verification": "New test asserts each printed rubric string equals pipeline._TIER_REQUIRED for R0-R3; an R1 packet with only A+B is blocked with the SAME message the installed rubric instructed; test_validators tier tests and test_guard REQUIRED_CLASSES test both pass without contradiction.",
      "depends_on": ""
    },
    {
      "id": "P2",
      "change": "Extract PACKET_PREFIXES / EVIDENCE_PREFIX into one shared module and import it everywhere; teach scripts/map_packets.py to also scan Layer-1 .github/aiv-evidence/EVIDENCE_*.md so Layer-1 coverage is visible in the evidence index.",
      "links_to": "F33,F219",
      "location": "new src/aiv/lib/packet_paths.py; consumers src/aiv/hooks/pre_commit.py:46, src/aiv/hooks/pre_push.py:40, src/aiv/lib/auditor.py:51, scripts/map_packets.py:15",
      "verification": "Unit test imports the constant from all four modules and asserts identity; map_packets test with only an EVIDENCE_ file shows the covered file as mapped, not unmapped.",
      "depends_on": ""
    },
    {
      "id": "P3",
      "change": "Bring the bash .husky/pre-commit hook to parity with the Python hook (or replace its body with a call to `python -m aiv.hooks.pre_commit`): recognize the PACKET_ prefix and Layer-1 EVIDENCE_ files, and implement the active-change-context bypass. Update the pre_commit.py module docstring rule inventory (Rules 1-10) so it is not stale.",
      "links_to": "F96,F97,F98,F210,F211",
      "location": ".husky/pre-commit:61; src/aiv/hooks/pre_commit.py:7,46-52,342,381-404,424",
      "verification": "Integration test stages the exact `aiv commit` output (one EVIDENCE_*.md + one source file) and runs both hooks; both exit 0. A >2-file commit inside an active `aiv begin` context is allowed by both. Docstring rule list matches implemented rules.",
      "depends_on": "P2"
    },
    {
      "id": "P4",
      "change": "Canonicalize the PR-body-supplied packet path before reading: call Path(file_path).resolve() and assert it stays within the repository root, in addition to the `.github/` prefix check.",
      "links_to": "F14,F83,F146,F197",
      "location": "src/aiv/guard/runner.py:191-204",
      "verification": "Unit test: a body value like `.github/../../../../etc/passwd` is rejected (no read) while a legitimate `.github/aiv-packets/...` path still resolves and reads.",
      "depends_on": ""
    },
    {
      "id": "P5",
      "change": "Add an SSRF guard to the link validator: enforce a scheme allowlist {http,https}, reject file://ftp://gopher://, and block loopback/link-local/RFC-1918 hosts (resolve and check before request); do not follow redirects to internal hosts.",
      "links_to": "F15,F84,F147,F196",
      "location": "src/aiv/lib/validators/links.py:163-176",
      "verification": "Unit tests assert urlopen is NOT reached for file:///etc/shadow, http://169.254.169.254/latest/meta-data/, and http://127.0.0.1/; a normal https URL still issues the HEAD check.",
      "depends_on": ""
    },
    {
      "id": "P6",
      "change": "Validate owner/repo parsed from the git remote against `^[A-Za-z0-9._-]+$` and percent-encode them before interpolating into GitHub API URLs and generated markdown links; reject crafted remotes containing ?,#,@.",
      "links_to": "F16,F85,F88",
      "location": "src/aiv/cli/main.py:639-700,683,843",
      "verification": "Unit test with a remote URL containing query/fragment characters raises a controlled error; generated markdown link is well-formed for a normal remote.",
      "depends_on": ""
    },
    {
      "id": "P7",
      "change": "URL-encode `path` and `ref` (and validate owner/repo segments) in GitHubAPI.get_file_content using urllib.parse.quote, matching the encoding already applied in search_code; guard against `owner/../` style GITHUB_REPOSITORY values.",
      "links_to": "F86,F198,F150",
      "location": "src/aiv/guard/github_api.py:176,42",
      "verification": "Unit test: a path `README.md?ref=main&per_page=100` is encoded so the effective request path/query is unchanged; malformed GITHUB_REPOSITORY rejected.",
      "depends_on": ""
    },
    {
      "id": "P8",
      "change": "Catch the parent urllib.error.URLError (DNS/refused/SSL) in _request and _request_bytes and re-raise as GitHubAPIError; wrap runner.main() so missing env vars (KeyError) and API failures produce a structured message + exit code rather than a raw traceback.",
      "links_to": "F115,F174,F237,F239",
      "location": "src/aiv/guard/github_api.py:43-76; src/aiv/guard/runner.py:393",
      "verification": "Unit test: a simulated URLError surfaces as GitHubAPIError; running main() with GITHUB_TOKEN unset prints a diagnostic and exits non-zero, no traceback.",
      "depends_on": ""
    },
    {
      "id": "P9",
      "change": "Stop silently truncating on pagination errors: signal/raise when list_pr_files or list_run_artifacts breaks mid-pagination so scope/artifact checks are not run against an incomplete list; catch binascii.Error on base64.b64decode in get_file_content; catch JSONDecodeError on the GITHUB_EVENT_PATH read.",
      "links_to": "F44,F45,F53,F116",
      "location": "src/aiv/guard/github_api.py:116-117,159-160,188,88",
      "verification": "Unit tests: a page-2 API error marks results as truncated (not a silent PASS); invalid base64 and malformed event JSON yield handled errors, not crashes.",
      "depends_on": "P8"
    },
    {
      "id": "P10",
      "change": "Remove or wire the unreachable download_artifact_zip and search_code methods; hoist the lazy `import base64`/`import urllib.parse` to module level; add a __repr__/__str__ that redacts the token; replace canonical.py's __import__('json') with a top-level import.",
      "links_to": "F177,F178,F120,F200,F201",
      "location": "src/aiv/guard/github_api.py:60,191,188,193,40; src/aiv/guard/canonical.py:442",
      "verification": "Grep confirms no remaining callers of removed methods; repr(GitHubAPI(...)) contains no token characters; lint passes with module-level imports.",
      "depends_on": ""
    },
    {
      "id": "P11",
      "change": "Document and constrain the GITHUB_EVENT_PATH trust boundary: treat the variable as runner-controlled only, and note in the spec that local/CI environments where it is attacker-settable can read arbitrary files.",
      "links_to": "F89",
      "location": "src/aiv/guard/github_api.py:88; SPECIFICATION.md",
      "verification": "Code comment + SPEC paragraph present; no behavioral regression in guard tests.",
      "depends_on": ""
    },
    {
      "id": "P12",
      "change": "Enforce a maximum payload length on the inline-b64-json scope-inventory ref before base64.b64decode, and add adversarial test coverage for oversized/crafted inline-json and inline-b64-json payloads.",
      "links_to": "F199,F207",
      "location": "src/aiv/guard/canonical.py:438-441; tests/unit/test_guard.py:92",
      "verification": "Unit test: a multi-megabyte base64 payload is rejected with a CT error before decode; a crafted deeply-nested inline-json payload is bounded/rejected.",
      "depends_on": ""
    },
    {
      "id": "P13",
      "change": "Pass github.actor into the CI step via an `env:` variable and reference $ACTOR in the bash heredoc instead of interpolating ${{ github.actor }} directly into shell.",
      "links_to": "F148",
      "location": ".github/workflows/ci.yml:387",
      "verification": "Workflow lint passes; the actor value is consumed only through an env var; no direct expression interpolation into shell.",
      "depends_on": ""
    },
    {
      "id": "P14",
      "change": "Match Class-F justifications to the SPECIFIC anti-cheat finding (file/violation type) instead of letting any one >20-char Class-F claim clear every finding; require a justification that references the affected test file or violation.",
      "links_to": "F134,F187",
      "location": "src/aiv/lib/validators/anti_cheat.py:192-213",
      "verification": "Unit test: deleting assertions in test_a.py and skipping a test in test_b.py with a single generic Class-F claim still produces findings for both files.",
      "depends_on": ""
    },
    {
      "id": "P15",
      "change": "Parenthesize the diff line-counter condition so `+++` headers do not increment current_line; correct operator precedence between the `+` and context clauses.",
      "links_to": "F1,F132,F186,F11",
      "location": "src/aiv/lib/validators/anti_cheat.py:132-142",
      "verification": "Unit test (strengthen test_multi_hunk_line_numbers) asserts deleted-line line_number is exactly correct across multiple hunks containing `+++` headers.",
      "depends_on": ""
    },
    {
      "id": "P16",
      "change": "Make packet validation fail CLOSED: on any infrastructure error in _validate_packet, return False (block) or raise, instead of `except Exception: ... return True`. Surface the error to the developer.",
      "links_to": "F43,F233",
      "location": "src/aiv/hooks/pre_commit.py:212-214",
      "verification": "Unit test: a forced exception inside _validate_packet causes main() to block the commit (non-zero exit), not pass.",
      "depends_on": ""
    },
    {
      "id": "P17",
      "change": "Wrap the NamedTemporaryFile and mkdtemp audit_dir lifecycle in try/finally so both are cleaned up even when subprocess raises TimeoutExpired/FileNotFoundError.",
      "links_to": "F113,F175",
      "location": "src/aiv/hooks/pre_commit.py:155-214",
      "verification": "Unit test: an exception during packet validation leaves no orphaned temp file or audit_dir on disk.",
      "depends_on": "P16"
    },
    {
      "id": "P18",
      "change": "Before marking A-002/A-005 PASS, require run_data conclusion=='success' AND status=='completed'; a failed/cancelled/in-progress run that uploaded an aiv-evidence artifact must NOT yield passing Class-A evidence.",
      "links_to": "F135",
      "location": "src/aiv/guard/runner.py:336-365",
      "verification": "Unit test: a workflow run with conclusion=='failure' (artifact present) does not produce A-002/A-005 PASS.",
      "depends_on": ""
    },
    {
      "id": "P19",
      "change": "Honor the documented 'never raises' contract of evidence_collector._run_git/_run by catching FileNotFoundError and TimeoutExpired and returning empty string; detect the resulting degraded state (empty diff, 'unknown' SHA) and signal it so collect_class_b/collect_class_c/collect_class_a do not emit falsely-clean or 404-permalink evidence; guard collect_class_a against missing pytest/ruff/mypy.",
      "links_to": "F47,F114,F173,F232,F52,F176",
      "location": "src/aiv/lib/evidence_collector.py:249-255,283-285,348,457",
      "verification": "Unit tests with git/pytest absent produce a structured degraded result (no traceback); a git failure during collect_class_c does NOT report anti_cheat_clean=True.",
      "depends_on": ""
    },
    {
      "id": "P20",
      "change": "Fix the Class-B permalink SHA: it currently equals the parent commit because rev-parse HEAD runs before the commit. Either compute the post-commit SHA in the close path or clearly mark the permalink SHA as provisional and patch it post-commit.",
      "links_to": "F29",
      "location": "src/aiv/lib/evidence_collector.py:283",
      "verification": "Test asserts the generated Class-B permalink references the commit that introduces the files, not its parent.",
      "depends_on": "P19"
    },
    {
      "id": "P21",
      "change": "Replace the O(N^2) per-node `ast.walk(tree)` parent-class lookup with a single precomputed child->parent map (correctly handling classes nested in functions); replace `import xdist as _` with importlib.util.find_spec('xdist').",
      "links_to": "F54,F123,F243",
      "location": "src/aiv/lib/evidence_collector.py:620-626,343",
      "verification": "Test: a method of a class nested inside a function gets the correct ClassName.method symbol; no second tree walk per node; xdist presence detected without importing it.",
      "depends_on": ""
    },
    {
      "id": "P22",
      "change": "In change.load_change, distinguish corrupt-file errors from 'no active change' (narrow the except; drop the redundant `(json.JSONDecodeError, Exception)` ordering) so corruption is surfaced; in get_untracked_commits handle the initial/root commit (use `--root` or detect the no-parent case) instead of swallowing CalledProcessError as zero commits.",
      "links_to": "F50,F230,F4",
      "location": "src/aiv/lib/change.py:82,233",
      "verification": "Tests: a corrupt change file raises/logs (not silent None); an initial-commit repo returns the real untracked-commit list, not [].",
      "depends_on": ""
    },
    {
      "id": "P23",
      "change": "In pre_commit._run_git, check result.returncode and treat git failure (git missing / not a repo) as an error (fail closed or diagnostic) rather than returning '' which _staged_files reads as 'nothing staged' and exits 0.",
      "links_to": "F51",
      "location": "src/aiv/hooks/pre_commit.py:65-71",
      "verification": "Unit test: a git invocation failure causes the hook to NOT exit 0 silently.",
      "depends_on": "P16"
    },
    {
      "id": "P24",
      "change": "Add rotation/size-cap/cleanup for the .cache/bb-safety-snapshots/ directory created on every pre-commit run so snapshots do not accumulate unbounded.",
      "links_to": "F55",
      "location": "src/aiv/hooks/pre_commit.py:117-140",
      "verification": "Unit test: after N runs only the most recent K snapshots remain (or total size is bounded).",
      "depends_on": ""
    },
    {
      "id": "P25",
      "change": "Replace the silent `except Exception: pass` in load_hook_config with a logged warning so a corrupt/mis-typed .aiv.yml is visible; document functional_root_files (.gitignore) and the .husky/ self-modification circularity; add a test that the loader uses yaml.safe_load (object-injection payload rejected).",
      "links_to": "F60,F231,F215,F30,F155",
      "location": "src/aiv/lib/config.py:284-285,154,163",
      "verification": "Test: a malformed .aiv.yml emits a warning and falls back; a `!!python/object/apply` payload does NOT execute (safe_load); docs mention .gitignore and .husky circularity.",
      "depends_on": ""
    },
    {
      "id": "P26",
      "change": "Remove `--no-verify` from the close/commit packet-commit calls so the packet commit passes through the pre-commit hook (Rule 6 already allows packet-only commits, making the flag unnecessary). Update the close docstring to stop claiming non-bypassable while bypassing.",
      "links_to": "F6,F17,F26,F48,F69,F87,F99,F209,F149",
      "location": "src/aiv/cli/main.py:1233-1241,1236-1237,969-979",
      "verification": "Integration test: `aiv close` commits the packet WITHOUT --no-verify and the pre-commit hook runs and passes; grep confirms no --no-verify in the close path.",
      "depends_on": "P16,P3"
    },
    {
      "id": "P27",
      "change": "Replace the bare `except Exception: pass` in the close evidence-extraction loop with a narrowed except that logs the failing file and does NOT silently substitute the untestable generic boilerplate claim for real evidence-derived claims.",
      "links_to": "F49",
      "location": "src/aiv/cli/main.py:1085",
      "verification": "Test: a corrupt/missing evidence file surfaces a diagnostic and the packet is not generated with only boilerplate claims.",
      "depends_on": ""
    },
    {
      "id": "P28",
      "change": "Add the `--` separator before path arguments in the git-add invocations, and wrap CalledProcessError/TimeoutExpired/FileNotFoundError as console.print + raise typer.Exit(1) to match the rest of the CLI.",
      "links_to": "F18,F117",
      "location": "src/aiv/cli/main.py:1879,1233",
      "verification": "Test: a filename beginning with `-` is treated as a path, not a flag; a git failure yields a friendly Typer error not a raw traceback.",
      "depends_on": ""
    },
    {
      "id": "P29",
      "change": "Replace the `\"name\" in dir()` scope probes with `\"name\" in locals()` for changed_symbols and class_c_data so empty line_ranges does not produce environment-dependent behavior or a NameError.",
      "links_to": "F28,F118,F234",
      "location": "src/aiv/cli/main.py:1664,1721",
      "verification": "Test: the empty-line_ranges path runs without NameError and falls back deterministically.",
      "depends_on": ""
    },
    {
      "id": "P30",
      "change": "Remove the redundant `import subprocess as _sp` alias (use the already-imported subprocess) and replace the bare `python` pytest invocation with sys.executable to respect the active virtualenv.",
      "links_to": "F121,F235,F238",
      "location": "src/aiv/cli/main.py:1488-1489,743",
      "verification": "Lint shows no unused alias; pytest is launched via sys.executable in a venv test.",
      "depends_on": ""
    },
    {
      "id": "P31",
      "change": "Unify the verification-packet schema version emitted by generate (v2.1) and close (v2.2) to a single value, or add a CHANGELOG/SPEC entry documenting the v2.1->v2.2 difference.",
      "links_to": "F25",
      "location": "src/aiv/cli/main.py:514,1143",
      "verification": "Both commands emit the same version string OR a changelog/spec diff for v2.1->v2.2 exists.",
      "depends_on": ""
    },
    {
      "id": "P32",
      "change": "Run the protocol-audit CI job on pull_request events (not only push to main) so a --no-verify push on a PR branch is caught before merge; align the pre_push.py Layer-3 docstring with the actual trigger coverage.",
      "links_to": "F32,F101,F214",
      "location": ".github/workflows/ci.yml:5-7,67; src/aiv/hooks/pre_push.py:15-22",
      "verification": "Workflow triggers protocol-audit on a PR; docstring no longer overstates coverage.",
      "depends_on": ""
    },
    {
      "id": "P33",
      "change": "Wire EvidenceValidator.validate_file_type_triggers into the pipeline: add a changed_files field to ValidationContext, parse changed paths from the diff, and invoke the method so SQL/migration/dependency/API/Dockerfile changes actually demand Class D (E021/E022).",
      "links_to": "F46,F158,F217",
      "location": "src/aiv/lib/validators/evidence.py:261; src/aiv/lib/validators/pipeline.py:34-43,126-128",
      "verification": "Test: a packet whose diff touches a Dockerfile/.sql/pyproject.toml without Class D is blocked by the file-type trigger; grep shows a real call site.",
      "depends_on": ""
    },
    {
      "id": "P34",
      "change": "Restructure the evidence early-`pass` so github_actions/external link types still reach the E012 (UI state-transition) and E013 (performance benchmark) checks for Class-A claims.",
      "links_to": "F5",
      "location": "src/aiv/lib/validators/evidence.py:86-91",
      "verification": "Test: a Class-A UI/performance claim linked to a CI run triggers E012/E013 instead of passing unchallenged.",
      "depends_on": ""
    },
    {
      "id": "P35",
      "change": "Collapse the two divergent bug-fix/Class-F-adequacy implementations into one shared helper and one justification-vs-description fallback rule so anti_cheat and evidence validators enforce the same standard; broaden the Zero-Touch Class-D manual-execution keyword set beyond the five DB strings.",
      "links_to": "F59,F161,F162",
      "location": "src/aiv/lib/validators/evidence.py:415,402,242; src/aiv/lib/validators/anti_cheat.py:207",
      "verification": "Test: the same Class-F claim is assessed identically by both validators; a Class-D reproduction using kubectl/docker exec/ssh is flagged by Zero-Touch.",
      "depends_on": ""
    },
    {
      "id": "P36",
      "change": "Eliminate the rule-id collisions: E020 means two unrelated things (evidence.py:113 vs pipeline.py:248) and E021 collides (evidence.py:334 vs links.py:140,152). Assign distinct ids or namespace rule ids by validator so downstream suppression/aggregation is unambiguous.",
      "links_to": "F160,F216",
      "location": "src/aiv/lib/validators/evidence.py:113,334; src/aiv/lib/validators/pipeline.py:248; src/aiv/lib/validators/links.py:140,152",
      "verification": "Test: each rule_id in emitted findings maps to exactly one message/meaning across all validators.",
      "depends_on": ""
    },
    {
      "id": "P37",
      "change": "Fix has_provenance_evidence to also consult evidence_classes_present (standalone Class-F evidence section) rather than only PROVENANCE-typed claim objects, so E010 gating is not falsely skipped.",
      "links_to": "F34",
      "location": "src/aiv/lib/models.py:268",
      "verification": "Test: a packet with Class F only in a standalone evidence section returns True from has_provenance_evidence.",
      "depends_on": ""
    },
    {
      "id": "P38",
      "change": "Make ValidationResult.is_valid consistent with status: in strict mode a warning-only packet has status FAIL but is_valid True. Have is_valid reflect status (or factor in strict warnings) so library/CI consumers branching on is_valid cannot pass a strict-failing packet.",
      "links_to": "F76,F133",
      "location": "src/aiv/lib/models.py:306-309; src/aiv/lib/validators/pipeline.py:163-169",
      "verification": "Test: strict_mode packet with only WARN findings has is_valid==False (matching status FAIL).",
      "depends_on": ""
    },
    {
      "id": "P39",
      "change": "Correct the ValidationPipeline class docstring to enumerate all stages including 'Risk-Tier Evidence Requirements' (Stage 5) so it matches the 8-stage reality referenced in the CLI quickstart.",
      "links_to": "F27,F100",
      "location": "src/aiv/lib/validators/pipeline.py:48-56,131; src/aiv/cli/main.py:324",
      "verification": "Docstring stage list matches the implemented stages and the quickstart text.",
      "depends_on": ""
    },
    {
      "id": "P40",
      "change": "Stop the R0 `--skip-checks` Class-A placeholder header from silently satisfying the tier requirement: emit an explicit skip marker (INFO/E019 distinct flag) so a placeholder is not counted as real execution evidence.",
      "links_to": "F103",
      "location": "src/aiv/cli/main.py:1465-1649; src/aiv/lib/validators/pipeline.py:182,229",
      "verification": "Test: R0+--skip-checks produces a distinct 'execution evidence skipped' marker rather than a clean Class-A PASS.",
      "depends_on": ""
    },
    {
      "id": "P41",
      "change": "In GuardResult.finalize set a meaningful compliance_level on PASS (e.g. 'COMPLIANT' or a tier-aware value) and compute graduated levels when WARN-only findings exist; ensure a markdown-only run is not reported as full L1 canonical compliance.",
      "links_to": "F3,F31,F57,F188",
      "location": "src/aiv/guard/models.py:182-189,123; src/aiv/guard/runner.py:144-150",
      "verification": "Test: a passed R3 packet and a passed R0 packet report distinguishable compliance_level; a clean pass yields 'COMPLIANT', not the default 'L1'.",
      "depends_on": ""
    },
    {
      "id": "P42",
      "change": "Compute EvidenceClassResult.valid from actual artifact integrity (URL reachability/SHA pinning), not `valid=present`; or remove the dead field if no independent validation is intended.",
      "links_to": "F71,F119",
      "location": "src/aiv/guard/runner.py:381-383",
      "verification": "Test: a present Class-A entry with a broken URL/wrong SHA gets valid=False (or the field is removed and consumers updated).",
      "depends_on": ""
    },
    {
      "id": "P43",
      "change": "Emit the E-METH methodology diagnostic independently of whether other required sections are already flagged missing, so the methodology gap is always surfaced.",
      "links_to": "F7",
      "location": "src/aiv/guard/runner.py:249-253",
      "verification": "Test: a packet missing both required sections AND methodology still reports the targeted E-METH message.",
      "depends_on": ""
    },
    {
      "id": "P44",
      "change": "In parser._enrich_claims_with_evidence always run _extract_url to isolate the URL before ArtifactLink.from_url (handle multi-line/embedded-prose artifact strings) so http-prefixed multi-line blocks still produce a validated ArtifactLink that gets immutability-checked.",
      "links_to": "F74,F139,F189",
      "location": "src/aiv/lib/parser.py:584-586,603",
      "verification": "Test: a multi-line evidence block beginning with https://... yields an ArtifactLink (immutability checked), not a raw-string fallback.",
      "depends_on": ""
    },
    {
      "id": "P45",
      "change": "Remove the unused ParsedSection.raw_start/raw_end byte-offset fields (or consume them) to eliminate dead state.",
      "links_to": "F241",
      "location": "src/aiv/lib/parser.py:38",
      "verification": "Lint/grep shows no readers; tests pass after removal.",
      "depends_on": ""
    },
    {
      "id": "P46",
      "change": "Only set auto_fixable=True when a commit SHA is actually resolvable; validate _get_introducing_commit output is a real SHA (not trailing garbage) before using it to build URLs/decide auto_fixable; document that _LOCAL_FILE_PATHS only fixes repos containing AUDIT_REPORT.md/SPECIFICATION.md.",
      "links_to": "F56,F58,F122",
      "location": "src/aiv/lib/auditor.py:492,115-117,128-131",
      "verification": "Test: an evidence finding with unknown SHA reports auto_fixable=False; a garbage git line is rejected, not used as a SHA.",
      "depends_on": ""
    },
    {
      "id": "P47",
      "change": "Apply the Layer-2 TODO/classified_by/blast_radius/numbered-claim TODO checks to Layer-1 evidence files in _check_evidence; and make the claims-section regex accept the `## Claims` heading alternative (currently only `## Claim(s)`), so CLAIM_TODO and FIX_NO_CLASS_F checks are not skipped.",
      "links_to": "F137,F190",
      "location": "src/aiv/lib/auditor.py:434-578,390-401",
      "verification": "Tests: an evidence file with classified_by:'TODO' is flagged; a packet using `## Claims` with TODO placeholders and no Class F on a bug fix is flagged.",
      "depends_on": ""
    },
    {
      "id": "P48",
      "change": "Wrap the per-packet read_text/write_text in auditor.audit in try/except so a single unreadable/undeletable file does not abort the whole run; emit partial results.",
      "links_to": "F236",
      "location": "src/aiv/lib/auditor.py:236-247",
      "verification": "Test: one unreadable packet among several yields findings for the others plus a per-file error, not a total crash.",
      "depends_on": ""
    },
    {
      "id": "P49",
      "change": "Fix the Class-E auto-fix so it SHA-pins (never emits a mutable /blob/main/ URL that the auditor's own CLASS_E_MUTABLE rule would re-flag) and URL-encodes/sanitizes the local filename (reject ../, %, #). Refresh the stale hard-coded auditor.py line-number references in test docstrings.",
      "links_to": "F39,F40,F93,F111,F154,F206,F170,F225",
      "location": "src/aiv/lib/auditor.py (auto-fix path); tests/unit/test_auditor.py:370-381,243-244",
      "verification": "Test: auto-fix output passes a follow-up audit (no CLASS_E_MUTABLE); a filename containing ../ is encoded/rejected; docstring line refs are symbolic, not pinned.",
      "depends_on": ""
    },
    {
      "id": "P50",
      "change": "Resolve the ELO tier boundary contradiction: either have VerifierRating.__init__ derive tier via from_elo (so elo=500 -> COMPETENT) or set the COMPETENT threshold to >500 (so from_elo(500)->NOVICE). Pick one and make the constructor and from_elo agree, then align the three conflicting tests.",
      "links_to": "F9,F77,F142,F191",
      "location": "src/aiv/svp/lib/rating.py; VerifierTier.from_elo and VerifierRating.__init__ (svp models)",
      "verification": "Test: from_elo(500) and a freshly-constructed VerifierRating(elo=500).tier return the same tier; no contradictory assertions remain.",
      "depends_on": ""
    },
    {
      "id": "P51",
      "change": "Make score_session emit RatingEvent(event_type='bug_missed', -25) when a falsification scenario is missed/unfalsified, and count bugs_caught only from confirmed probe findings (not from falsified-scenario events), so bugs_missed is recorded and bugs_caught is not inflated.",
      "links_to": "F73,F138",
      "location": "src/aiv/svp/lib/rating.py:23-124,147",
      "verification": "Tests: a missed bug applies the -25 penalty and increments bugs_missed; a verifier with 0 confirmed bugs but 5 falsified scenarios does NOT report bugs_caught=5.",
      "depends_on": ""
    },
    {
      "id": "P52",
      "change": "In session validation, make predicted_complexity Optional (or remove the unreachable None branch) so S004 is reachable as intended; and remove the early `return False` in _validate_trace so all S006/S015 violations across all traces are collected.",
      "links_to": "F70,F136",
      "location": "src/aiv/svp/lib/validators/session.py:113,156-157,183-185",
      "verification": "Test: a session with 3 traces each violating S006 reports 3 errors (not 1); S004 path is reachable.",
      "depends_on": ""
    },
    {
      "id": "P53",
      "change": "Iterate ALL attestations (not just [0]) in validate_canonical, and collect all missing required classes before returning instead of returning on the first missing class.",
      "links_to": "F75,F140",
      "location": "src/aiv/guard/canonical.py:159-160,231-235",
      "verification": "Tests: a second invalid/unsigned attestation is flagged; an R3 packet missing C,D,F reports all three, not just the first.",
      "depends_on": ""
    },
    {
      "id": "P54",
      "change": "Align the StructureValidator class docstring with the checks actually implemented (E002, E005, E008), noting parser-time enforcement for E001/E003/E006/E007 rather than listing them as performed here.",
      "links_to": "F218",
      "location": "src/aiv/lib/validators/structure.py:24-30",
      "verification": "Docstring enumerates only the checks the validate() method performs (with parser-delegation notes).",
      "depends_on": ""
    },
    {
      "id": "P55",
      "change": "Replace `normalized.startswith(member.value)` with equality so 'AB'/'AF'/'A1' do not match evidence class 'A'.",
      "links_to": "F2",
      "location": "src/aiv/lib/models.py:54",
      "verification": "Test: an input 'AB' does not resolve to EvidenceClass A; valid single-letter inputs still resolve.",
      "depends_on": ""
    },
    {
      "id": "P56",
      "change": "Tighten the SHA-pinned classification in ArtifactLink.from_url so an all-hex mutable tag (>=7 hex chars) is not mistaken for an immutable commit SHA: require canonical length (7/40) plus context, or document the limitation explicitly.",
      "links_to": "F72",
      "location": "src/aiv/lib/models.py:132-133",
      "verification": "Test: a 7-char all-hex tag ref is not classified as immutable/SHA-pinned (still warns).",
      "depends_on": ""
    },
    {
      "id": "P57",
      "change": "Skip empty decoded import names in _extract_named_imports so an empty bytes node does not add '' to the imports set and cause false-positive coverage matches downstream.",
      "links_to": "F242",
      "location": "src/aiv/lib/language_drivers/treesitter_driver.py:249",
      "verification": "Test: a malformed/anonymous import node does not add '' to imported_symbols; find_covering_tests does not spuriously match.",
      "depends_on": ""
    },
    {
      "id": "P58",
      "change": "Change the cross-claim leakage assertion operator from OR to AND so the test fails when EITHER claim 2 OR claim 3 incorrectly reuses claim 1's unlinked artifact.",
      "links_to": "F8,F78,F141,F192,F226",
      "location": "tests/unit/test_validators.py:606-610",
      "verification": "With artifacts=['src/handler.py','src/handler.py','See Evidence'] the assertion now FAILS (catches the partial bug).",
      "depends_on": ""
    },
    {
      "id": "P59",
      "change": "Guard the json.loads(result.stdout) calls in the SVP failure tests: assert stdout looks like JSON (or wrap in try/except with a descriptive re-raise) so a non-JSON error path produces a meaningful AssertionError, not a JSONDecodeError.",
      "links_to": "F12,F80",
      "location": "tests/integration/test_svp_full_workflow.py:247,309",
      "verification": "A non-JSON stdout on the failure path yields a clear assertion message identifying the real CLI error.",
      "depends_on": ""
    },
    {
      "id": "P60",
      "change": "Strengthen the TestAutoFix tests to actually assert remediation: capture and assert on post-fix file content (SHA replaced / pending resolved) and on result.packets_scanned/findings, instead of discarding read_text and audit() results; and make test_evidence_dir_none_skips_scan populate a real evidence file and assert it is NOT scanned.",
      "links_to": "F10,F42,F61,F65,F79,F110,F124,F168,F181,F227",
      "location": "tests/unit/test_auditor.py:359-381,875-884",
      "verification": "Tests fail if the auto-fix writes nothing/corrupts the file or if evidence_dir=None still scans a present evidence file.",
      "depends_on": "P47,P49"
    },
    {
      "id": "P61",
      "change": "Capture and assert result.returncode==0 (or pass check=True) on the `aiv init` subprocess invocations so an init failure surfaces directly instead of as a misleading filesystem-assertion error.",
      "links_to": "F62,F131,F179,F244",
      "location": "tests/unit/test_cli_init.py:54-69,75-83,127-148,190-197",
      "verification": "An induced non-zero `aiv init` exit makes the test report the subprocess failure (with stderr), not a 'directory missing' assertion.",
      "depends_on": ""
    },
    {
      "id": "P62",
      "change": "Capture the _run_aiv_commit CompletedProcess and assert returncode==0 and len(evidence_files)==1 before indexing in the skip-reason tests, matching the sibling test that already guards index access.",
      "links_to": "F64,F68,F81,F125,F180,F194,F245",
      "location": "tests/unit/test_cli_commit_skip.py:114-138",
      "verification": "An induced commit failure produces an explicit returncode assertion failure (and no IndexError).",
      "depends_on": ""
    },
    {
      "id": "P63",
      "change": "Sanitize/escape the --skip-reason text before writing it into the markdown evidence file (so newlines, '## headings', '---', table pipes, fences cannot forge evidence sections), and add adversarial tests with markdown-injection payloads.",
      "links_to": "F92,F157,F204",
      "location": "src/aiv/cli/main.py:1646-1649 (evidence writer); tests/unit/test_cli_commit_skip.py:114-138",
      "verification": "Test: a skip-reason containing '\\n## Class A (Execution Evidence)\\n- pytest: 999 passed' does not create a parseable forged Class-A section in the evidence file.",
      "depends_on": ""
    },
    {
      "id": "P64",
      "change": "Stop spreading the full host environment into aiv subprocesses in tests: start from a minimal env dict (only PYTHONPATH/PYTHONUTF8/PATH) and add a top-level `import os` instead of the inline __import__('os') form, so CI secrets are not propagated and the dependency is statically visible.",
      "links_to": "F21,F95,F126,F153,F182,F251",
      "location": "tests/integration/test_svp_full_workflow.py:43-61,51; tests/unit/test_cli_commit_skip.py:78-84; tests/unit/test_cli_init.py:44-51",
      "verification": "Subprocess env contains no inherited secret variables; module imports os at top; tests still pass.",
      "depends_on": ""
    },
    {
      "id": "P65",
      "change": "Wrap the subprocess.run(timeout=30) call in the _run helper with try/except subprocess.TimeoutExpired so a hung aiv subcommand fails as a clear test failure (with captured cmd) rather than an uncaught exception that corrupts the class run.",
      "links_to": "F63",
      "location": "tests/integration/test_svp_full_workflow.py:45-61",
      "verification": "An induced hang yields a descriptive test failure, not a raw TimeoutExpired traceback.",
      "depends_on": ""
    },
    {
      "id": "P66",
      "change": "Patch _load_hook_config in test_functional_plus_packet_validates (and any sibling using raw patch blocks) so the test is not sensitive to a real .aiv.yml in the working directory; route it through the _mock_main helper that already patches all six callables.",
      "links_to": "F13,F82,F130,F183,F195,F246",
      "location": "tests/unit/test_pre_commit_hook.py:157-172",
      "verification": "The test produces the same result regardless of a custom .aiv.yml present in cwd.",
      "depends_on": ""
    },
    {
      "id": "P67",
      "change": "Rename test_template_is_not_packet to reflect the asserted behavior (templates ARE structurally packets) and reconcile the cross-component inconsistency: the hook accepts TEMPLATE files as packets while the auditor excludes them. Decide one policy and align both so a bare template cannot satisfy the gate while leaving no audit trail.",
      "links_to": "F37,F106,F163,F172",
      "location": "tests/unit/test_pre_commit_hook.py:35-38; src/aiv/hooks/pre_commit.py:46-52,80; src/aiv/lib/auditor.py:216 (TEMPLATE exclusion via glob filter)",
      "verification": "Test name matches assertion; a TEMPLATE-only commit is handled consistently by both hook and auditor (a test asserts the chosen policy).",
      "depends_on": "P2"
    },
    {
      "id": "P68",
      "change": "Fix the inverted docstring in test_default_branch_not_mutable_with_custom_set so it matches the assertion (is_immutable is False == 'main' remains mutable); the inline comment is already correct.",
      "links_to": "F38,F143,F166,F222",
      "location": "tests/unit/test_models.py:296-305; tests/unit/test_validators.py:298",
      "verification": "Docstring and assertion agree; no reviewer would invert the assertion based on the docstring.",
      "depends_on": ""
    },
    {
      "id": "P69",
      "change": "Strengthen claim-not-verified / weak-assertion tests so they verify behavior, not just string presence: pre-push tests must assert actual interception behavior (or be renamed to documentation checks), test_valid_markdown_packet must assert block_count/warn_count/overall_result, and the R2-optional-D-and-F test must assert BOTH D and F produce INFO.",
      "links_to": "F107,F108,F109,F144,F167,F169,F184,F223",
      "location": "tests/unit/test_cli_init.py:139; tests/unit/test_guard.py:401,408-425; tests/unit/test_validators.py:366",
      "verification": "Each test fails if the underlying behavior regresses (e.g. guard blocks all markdown packets, or only D emits INFO).",
      "depends_on": ""
    },
    {
      "id": "P70",
      "change": "Misc test-correctness cleanups: make the git-log mock reproduce the real `--format=%H --name-only` blank-line-after-SHA layout; replace over-broad pytest.raises(Exception) with the specific frozen-model exception; correct the TestRule8 name/count (two functional files, not three); narrow the global Path.read_text patch to the specific module usage.",
      "links_to": "F145,F171,F224,F247",
      "location": "tests/unit/test_auditor.py:514-533; tests/unit/test_models.py:97; tests/unit/test_pre_commit_hook.py:233; tests/unit/test_evidence_collector.py:100-101",
      "verification": "Mock format matches real git output; frozen-model test catches only the expected exception; rule-8 name reflects the actual trigger count; the read_text patch no longer suppresses unrelated I/O.",
      "depends_on": ""
    },
    {
      "id": "P71",
      "change": "Fix the unsafe default pairing on FalsificationScenario (checked=False with result='confirmed'): default an unchecked scenario to result=None/'pending', and update the test to assert the safe default and to guard .result reads on .checked.",
      "links_to": "F193",
      "location": "tests/unit/test_svp.py:262-265; svp FalsificationScenario model",
      "verification": "Test: a newly constructed unchecked scenario has result None/'pending', not 'confirmed'; consumers gate on checked.",
      "depends_on": ""
    },
    {
      "id": "P72",
      "change": "Close the verifier-identity authz gap: bind author_github_id/verifier_id to a trusted source (git commit signature or verified GitHub token) rather than a self-chosen --verifier string, and add adversarial tests that (a) reject a hand-forged .svp/session-pr{N}.json passed to `svp validate`, (b) reject impersonation/empty identifiers, (c) confirm test_code is never exec/eval'd, and (d) exercise the real installed pre-push hook end-to-end.",
      "links_to": "F22,F91,F94,F156,F205,F208",
      "location": "src/aiv/svp/lib/validators/session.py:291-298 (S011 author_github_id==verifier_id); .svp/session-pr{N}.json handling; tests/unit/test_svp.py:511; tests/integration/test_svp_full_workflow.py:63; tests/unit/test_pre_push_hook.py:189",
      "verification": "Tests: identical self-chosen --verifier strings no longer trivially satisfy S011 without a trusted binding; a forged session file is rejected; a real git push exercises the pre-push hook.",
      "depends_on": ""
    },
    {
      "id": "P73",
      "change": "Test hygiene: move the late module-level `from aiv.svp.lib.rating import ...` to the top import block; hoist in-test local imports (subprocess/sys, ArtifactLink/IntentSection) to module level removing the dead duplicate IntentSection re-imports; broaden the treesitter availability guard to catch non-ImportError exceptions so a partial native install yields a skip, not a collection error.",
      "links_to": "F67,F127,F128,F129,F185,F248,F249,F250",
      "location": "tests/unit/test_svp.py:676; tests/unit/test_auditor.py:419; tests/unit/test_validators.py:394,500; tests/unit/test_language_drivers.py:90-95",
      "verification": "Imports live at module top; no duplicate IntentSection import; a corrupted tree-sitter native lib produces a skip, not a module-collection failure (covers F129/F250 pattern).",
      "depends_on": ""
    },
    {
      "id": "P74",
      "change": "Add SSRF negative-test coverage proving internal/cloud-metadata URLs and non-http(s) schemes are blocked before urlopen, including a redirect-to-internal case, and fix the HTTPError mocks to pass an http.client.HTTPMessage (not a bare dict) for hdrs so the mock matches production error handling.",
      "links_to": "F19,F66,F90,F151,F152,F202,F203",
      "location": "tests/unit/test_validators.py:427-543,433,487; tests/unit/test_models.py:87-89",
      "verification": "New tests assert LinkValidator(audit_links=True) refuses 169.254.169.254/127.0.0.1/file:// and a public->internal redirect; HTTPError mocks use HTTPMessage.",
      "depends_on": "P5"
    },
    {
      "id": "P75",
      "change": "Correct the stale SVP integration-test docstrings: Phase 4 is exercised via the `self._run('ownership', ...)` CLI path (not JSON/model injection), and the suite covers Phases 0-4 (five phases incl Phase 0 Sanity), not 1-4. Update module and method docstrings accordingly.",
      "links_to": "F35,F36,F104,F105,F164,F165,F220,F221",
      "location": "tests/integration/test_svp_full_workflow.py:3-17,317-322",
      "verification": "Docstrings describe the CLI-driven Phase 4 and enumerate Phases 0-4 consistent with the five phase_N_complete assertions.",
      "depends_on": ""
    },
    {
      "id": "P76",
      "change": "Detect verification-config tampering: when .aiv.yml is itself staged/modified in a commit that also weakens functional_prefixes (or empties them) alongside functional code without a packet, the pre-commit hook must not read the weakened config to exempt those files — require a packet or refuse the weakening.",
      "links_to": "F20",
      "location": "src/aiv/hooks/pre_commit.py (config load at commit time); src/aiv/lib/config.py",
      "verification": "Test: a commit that stages an .aiv.yml emptying functional_prefixes plus a functional file with no packet is blocked, not exited 0.",
      "depends_on": "P16,P25"
    },
    {
      "id": "P77",
      "change": "Resolve manifest.py dead code: either invoke validate_class_a/c/semantic/durable_manifest from the guard pipeline (so per-class evidence is actually validated against manifest content) or remove the module and document the decision.",
      "links_to": "F240",
      "location": "src/aiv/guard/manifest.py:23,89,146,177 (validate_class_a/c/semantic/durable_manifest — zero references in src/aiv/guard/runner.py); src/aiv/guard/runner.py",
      "verification": "If wired: a test shows Class-A/C manifest content is validated during a guard run; if removed: grep confirms no references and a note records the removal.",
      "depends_on": "P18"
    },
    {
      "id": "P78",
      "change": "Doc cleanup: align .cursorrules step 2 with the fact that `aiv commit` auto-stages the source file and generated evidence (the manual `git add` changes which diff is available), and remove the ghost 'Replaces the 2244-line inline JS' reference in runner.py whose target does not exist in the repo.",
      "links_to": "F102,F213",
      "location": ".cursorrules:9; src/aiv/guard/runner.py:5",
      "verification": "The documented commit workflow matches actual staging behavior; the runner docstring no longer references a nonexistent JS precursor.",
      "depends_on": ""
    },
    {
      "id": "P79",
      "change": "Quine goal-gap closure (the only non-grounded goal: 'demonstrate the protocol on itself with full pre-commit enforcement'). After the enforcement fixes land (P26 removes the close --no-verify self-exemption, P3 brings the bash hook to parity, P16 makes validation fail-closed, P32 extends CI to PRs), produce primary-source evidence that this repo is maintained under AIV without bypass: run a clean cross-commit audit, confirm the installed pre-commit hook is active, and document the velocity claim in SPEC/README.",
      "links_to": "goal:quine",
      "location": "repo-wide: .github/aiv-packets/, audit/04-goal.md, SPECIFICATION.md, README.md, .husky/pre-commit, src/aiv/cli/main.py:1233-1241 (close path)",
      "verification": "`aiv audit --commits N` runs clean; grep confirms no remaining --no-verify in the close/commit path; pre-commit hook is installed and exercised on a real commit; the goal status is upgradeable from needs-human-confirm to grounded with a cited audit log.",
      "depends_on": "P26,P3,P16,P32"
    }
  ],
  "_ambiguous": [
    "P77",
    "P79"
  ]
}
```
