"""
aiv/svp/lib/validators/session.py

SVP session validator — orchestrates validation of all phases (S001-S016).
"""

from __future__ import annotations

from ..models import (
    SessionType,
    SVPPhase,
    SVPSession,
    SVPValidationError,
    SVPValidationResult,
    ValidationSeverity,
)


def validate_session(session: SVPSession) -> SVPValidationResult:
    """
    Validate a complete SVP session against rules S001-S016.

    Returns a SVPValidationResult with all errors and warnings.
    """
    errors: list[SVPValidationError] = []
    warnings: list[SVPValidationError] = []

    # Phase 0: Sanity Gate
    p0 = _validate_sanity(session, errors)

    # Phase 1: Prediction
    p1 = _validate_prediction(session, errors, warnings)

    # Phase 2: Trace
    p2 = _validate_trace(session, errors, warnings)

    # Phase 3: Probe
    p3 = _validate_probe(session, errors, warnings)

    # Phase 4: Ownership
    p4 = _validate_ownership(session, errors, warnings)

    status = session.status

    return SVPValidationResult(
        pr_number=session.pr_number,
        repository=session.repository,
        verifier_id=session.verifier_id,
        status=status,
        phase_0_complete=p0,
        phase_1_complete=p1,
        phase_2_complete=p2,
        phase_3_complete=p3,
        phase_4_complete=p4,
        errors=errors,
        warnings=warnings,
    )


def _validate_sanity(
    session: SVPSession,
    errors: list[SVPValidationError],
) -> bool:
    """S001: AIV-Guard must pass before SVP begins."""
    if not session.aiv_guard_passed:
        errors.append(
            SVPValidationError(
                rule_id="S001",
                phase=SVPPhase.SANITY,
                severity=ValidationSeverity.BLOCK,
                message="AIV-Guard must pass before SVP begins.",
                suggestion="Ensure the AIV verification packet passes all checks.",
            )
        )
        return False
    return True


def _validate_prediction(
    session: SVPSession,
    errors: list[SVPValidationError],
    warnings: list[SVPValidationError],
) -> bool:
    """S002-S004: Prediction validation."""
    pred = session.prediction

    if pred is None:
        errors.append(
            SVPValidationError(
                rule_id="S002",
                phase=SVPPhase.PREDICTION,
                severity=ValidationSeverity.BLOCK,
                message="Prediction must be recorded.",
                suggestion="Run 'svp predict' before viewing the implementation diff.",
            )
        )
        return False

    # S003: Timing check
    if not pred.is_valid_timing:
        errors.append(
            SVPValidationError(
                rule_id="S003",
                phase=SVPPhase.PREDICTION,
                severity=ValidationSeverity.BLOCK,
                message="Prediction timestamp must precede diff view.",
                suggestion="Record prediction BEFORE viewing the implementation.",
            )
        )
        return False

    # S004: Complexity estimate (WARN)
    if pred.predicted_complexity is None:
        warnings.append(
            SVPValidationError(
                rule_id="S004",
                phase=SVPPhase.PREDICTION,
                severity=ValidationSeverity.WARN,
                message="Prediction should contain complexity estimate.",
            )
        )

    return True


def _validate_trace(
    session: SVPSession,
    errors: list[SVPValidationError],
    warnings: list[SVPValidationError],
) -> bool:
    """S005-S007, S015: Trace validation."""
    if len(session.traces) == 0:
        errors.append(
            SVPValidationError(
                rule_id="S005",
                phase=SVPPhase.TRACE,
                severity=ValidationSeverity.BLOCK,
                message="At least one trace record required per PR.",
                suggestion="Run 'svp trace' to record mental execution trace.",
            )
        )
        return False

    is_ai = session.session_type == SessionType.AI_ADVERSARIAL_TRIAGE

    for trace in session.traces:
        # S006: Edge case test
        if not trace.edge_case_tested or len(trace.edge_case_tested) < 10:
            errors.append(
                SVPValidationError(
                    rule_id="S006",
                    phase=SVPPhase.TRACE,
                    severity=ValidationSeverity.BLOCK,
                    message=f"Trace for {trace.function_path} must include edge case test.",
                )
            )
            return False

        # S007: Trace notes minimum length (WARN)
        if len(trace.trace_notes) < 100:
            warnings.append(
                SVPValidationError(
                    rule_id="S007",
                    phase=SVPPhase.TRACE,
                    severity=ValidationSeverity.WARN,
                    message=f"Trace notes for {trace.function_path} should be ≥100 characters.",
                )
            )

        # S015: AI sessions must include verified_output (execution evidence)
        if is_ai and not trace.verified_output:
            errors.append(
                SVPValidationError(
                    rule_id="S015",
                    phase=SVPPhase.TRACE,
                    severity=ValidationSeverity.BLOCK,
                    message=(
                        f"AI session trace for {trace.function_path} must include "
                        f"verified_output from actual execution. Mental simulation "
                        f"is not sufficient for AI verifiers."
                    ),
                    suggestion="Run the edge case and capture stdout/return value in verified_output.",
                )
            )
            return False

    return True


def _validate_probe(
    session: SVPSession,
    errors: list[SVPValidationError],
    warnings: list[SVPValidationError],
) -> bool:
    """S008-S009, S014, S016: Probe validation."""
    probe = session.probe

    if probe is None:
        errors.append(
            SVPValidationError(
                rule_id="S008",
                phase=SVPPhase.PROBE,
                severity=ValidationSeverity.BLOCK,
                message="Adversarial checklist must be submitted.",
                suggestion="Run 'svp probe' to complete the adversarial checklist.",
            )
        )
        return False

    if not probe.checklist_complete:
        errors.append(
            SVPValidationError(
                rule_id="S008",
                phase=SVPPhase.PROBE,
                severity=ValidationSeverity.BLOCK,
                message="All adversarial checklist items must be completed.",
            )
        )
        return False

    # S009: Why questions (WARN)
    if len(probe.why_questions) == 0:
        warnings.append(
            SVPValidationError(
                rule_id="S009",
                phase=SVPPhase.PROBE,
                severity=ValidationSeverity.WARN,
                message='At least one "Why?" question should be documented.',
            )
        )

    # S014: Falsification scenarios
    if len(probe.falsification_scenarios) == 0:
        errors.append(
            SVPValidationError(
                rule_id="S014",
                phase=SVPPhase.PROBE,
                severity=ValidationSeverity.BLOCK,
                message="At least one Falsification Scenario is required per primary claim.",
                suggestion=(
                    "Define what evidence would prove a primary claim false. "
                    "Example: 'If test_parse_header shows a missing-version packet "
                    "accepted, claim C-001 is falsified.'"
                ),
            )
        )
        return False

    # S016: AI sessions must have test_code on falsification scenarios
    is_ai = session.session_type == SessionType.AI_ADVERSARIAL_TRIAGE
    if is_ai:
        prose_only = [s for s in probe.falsification_scenarios if not s.test_code]
        if prose_only:
            errors.append(
                SVPValidationError(
                    rule_id="S016",
                    phase=SVPPhase.PROBE,
                    severity=ValidationSeverity.BLOCK,
                    message=(
                        f"{len(prose_only)} falsification scenario(s) have no test_code. "
                        f"AI sessions require executable pytest snippets, not prose descriptions."
                    ),
                    suggestion="Provide a pytest function in test_code that validates the scenario.",
                )
            )
            return False

    return True


def _validate_ownership(
    session: SVPSession,
    errors: list[SVPValidationError],
    warnings: list[SVPValidationError],
) -> bool:
    """S010-S013: Ownership validation."""
    oc = session.ownership_commit

    if oc is None:
        errors.append(
            SVPValidationError(
                rule_id="S010",
                phase=SVPPhase.OWNERSHIP,
                severity=ValidationSeverity.BLOCK,
                message="Ownership commit must exist.",
                suggestion="Push a commit with semantic renames or docstrings.",
            )
        )
        return False

    # S011: Must be by the designated verifier
    if oc.author_github_id != session.verifier_id:
        errors.append(
            SVPValidationError(
                rule_id="S011",
                phase=SVPPhase.OWNERSHIP,
                severity=ValidationSeverity.BLOCK,
                message=(f"Ownership commit must be by verifier ({session.verifier_id}), not {oc.author_github_id}."),
            )
        )
        return False

    # S012: Must contain substantive change
    if not oc.has_substantive_changes:
        errors.append(
            SVPValidationError(
                rule_id="S012",
                phase=SVPPhase.OWNERSHIP,
                severity=ValidationSeverity.BLOCK,
                message="Ownership commit must contain rename OR docstring change.",
            )
        )
        return False

    # S013: Message pattern (WARN)
    if not oc.follows_message_pattern:
        warnings.append(
            SVPValidationError(
                rule_id="S013",
                phase=SVPPhase.OWNERSHIP,
                severity=ValidationSeverity.WARN,
                message='Ownership commit message should start with "ownership:".',
            )
        )

    return True
