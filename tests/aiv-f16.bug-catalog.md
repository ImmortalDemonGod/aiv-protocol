# Bug catalog — aiv-f16

| # | Location | Defect | Evidence (harness-executed) | Caught by |
|---|----------|--------|------------------------------|-----------|
| 1 | src/aiv/cli/main.py:639-700 | `_detect_git_context()` at line 640 extracts `owner` and `repo` from the git remote URL via `re.search(r'[:/]([^/]+)/([^/.]+?)(?:\.git)?$', url)`. The character class `[^/]+` for owner (and `[^/.]+` for repo) permits `?`, `#`, `@`, and other URL-structural characters. These values are interpolated verbatim into GitHub API URLs at lines 683 and 714 (`f"https://api.github.com/repos/{owner}/{repo}/actions/runs?..."`) without percent-encoding. A crafted git remote URL can inject query parameters or fragment identifiers that alter the effective API endpoint. | Unit test with a remote URL containing query/fragment characters raises a controlled error; generated markdown link is well-formed for a normal remote. | `tests/test_aiv_f16.py` |

- **Expected (per the finding goal):** Unit test with a remote URL containing query/fragment characters raises a controlled error; generated markdown link is well-formed for a normal remote.
- Every row above is recorded ground truth (finding fields + harness-executed command outputs); no value is estimated.
