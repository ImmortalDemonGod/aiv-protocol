# Bug catalog — aiv-f177

| # | Location | Defect | Evidence (harness-executed) | Caught by |
|---|----------|--------|------------------------------|-----------|
| 1 | src/aiv/guard/github_api.py:60 | _request_bytes at line 60 is called exclusively from download_artifact_zip at line 169. download_artifact_zip is never invoked from runner.py: _inspect_class_a_run at lines 296-365 calls list_run_artifacts to find the aiv-evidence artifact, then immediately marks the rules as PASS at lines 364-365 without downloading or inspecting artifact contents. Both methods are unreachable from the guard's execution path. | Grep confirms no remaining callers of removed methods; repr(GitHubAPI(...)) contains no token characters; lint passes with module-level imports. | `tests/test_aiv_f177.py` |

- **Expected (per the finding goal):** Grep confirms no remaining callers of removed methods; repr(GitHubAPI(...)) contains no token characters; lint passes with module-level imports.
- Every row above is recorded ground truth (finding fields + harness-executed command outputs); no value is estimated.
