# RED test for the finding — the fix-pipeline harness pre-resolved and VERIFIED the import below (#146).
# Your ONLY job: replace the sentinel line in the test body with a REAL assertion that FAILS against the
# CURRENT (buggy) value of GitHubAPI (assert the CORRECT expected value). Do NOT change the import line.
# Use the FACT output(s) above for the CORRECT expected value — do NOT invent a number.
from src.aiv.guard.github_api import GitHubAPI  # verified working import — do not edit


def test_githubapi_pins_the_finding_defect():
    # GitHubAPI is imported above and ready to assert on.
    # Replace the next line with e.g.:  assert abs(GitHubAPI - <CORRECT_VALUE_from_the_FACT_above>) < <TOL>
    raise NotImplementedError("SCAFFOLD_SENTINEL_fill_the_red_assertion")
