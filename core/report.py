# core/report.py

from typing import Any, Dict, List


def _get_value(item: Any, key: str, default: Any = None) -> Any:
    """
    Safely get a value from either:
    - a Pydantic model
    - a dictionary
    - a normal Python object
    """

    if item is None:
        return default

    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


def _to_text(value: Any) -> str:
    """
    Convert any value into clean text.

    This prevents errors such as:
    sequence item 0: expected str instance, dict found
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, dict):
        # Prefer common text fields
        for key in [
            "text",
            "reasoning",
            "evidence",
            "description",
            "name",
            "requirement",
            "requirement_name",
            "title",
            "summary",
        ]:
            if key in value and value[key]:
                return _to_text(value[key])

        # Fallback: convert dictionary into readable text
        parts = []

        for key, val in value.items():
            text = _to_text(val)

            if text:
                parts.append(f"{key}: {text}")

        return " | ".join(parts)

    if isinstance(value, (list, tuple, set)):
        parts = []

        for item in value:
            text = _to_text(item)

            if text:
                parts.append(text)

        return ", ".join(parts)

    return str(value).strip()


def _normalize_list(value: Any) -> List[str]:
    """
    Convert any list-like value into a list of strings.

    Example:

    [
        {"requirement": "Python"},
        {"requirement": "PyTorch"}
    ]

    becomes:

    [
        "Python",
        "PyTorch"
    ]
    """

    if value is None:
        return []

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return []

        return [text]

    if isinstance(value, dict):
        text = _to_text(value)

        if text:
            return [text]

        return []

    if isinstance(value, (list, tuple, set)):
        result = []

        for item in value:
            text = _to_text(item)

            if text:
                result.append(text)

        return result

    text = _to_text(value)

    if text:
        return [text]

    return []


def _normalize_evidence(evidence: Any) -> List[Dict[str, Any]]:
    """
    Normalize evidence into a predictable list of dictionaries.

    Supports:

    - Pydantic evidence models
    - dictionaries
    - lists of either
    """

    if evidence is None:
        return []

    if not isinstance(evidence, (list, tuple)):
        evidence = [evidence]

    normalized = []

    for item in evidence:

        requirement_id = _get_value(
            item,
            "requirement_id",
            "",
        )

        requirement_name = _get_value(
            item,
            "requirement_name",
            "",
        )

        status = _get_value(
            item,
            "status",
            "UNCLEAR",
        )

        reasoning = _get_value(
            item,
            "reasoning",
            "",
        )

        evidence_text = _get_value(
            item,
            "evidence",
            "",
        )

        source = _get_value(
            item,
            "source",
            "",
        )

        confidence = _get_value(
            item,
            "confidence",
            0.0,
        )

        # Clean values
        requirement_id = _to_text(requirement_id)

        requirement_name = _to_text(requirement_name)

        status = _to_text(status).upper()

        reasoning = _to_text(reasoning)

        evidence_text = _to_text(evidence_text)

        source = _to_text(source)

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        # Keep confidence between 0 and 1
        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        normalized.append(
            {
                "requirement_id": requirement_id,
                "requirement_name": requirement_name,
                "status": status,
                "reasoning": reasoning,
                "evidence": evidence_text,
                "source": source,
                "confidence": confidence,
            }
        )

    return normalized


def _normalize_interview_findings(
    interview_findings: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize interview findings.

    This prevents dictionary/list type errors when
    interview results come from Pydantic models or Streamlit state.
    """

    if interview_findings is None:
        return []

    if not isinstance(
        interview_findings,
        (list, tuple),
    ):
        interview_findings = [interview_findings]

    normalized = []

    for item in interview_findings:

        requirement_id = _get_value(
            item,
            "requirement_id",
            "",
        )

        requirement_name = _get_value(
            item,
            "requirement_name",
            "",
        )

        question = _get_value(
            item,
            "question",
            "",
        )

        answer = _get_value(
            item,
            "answer",
            "",
        )

        status = _get_value(
            item,
            "status",
            "",
        )

        reasoning = _get_value(
            item,
            "reasoning",
            "",
        )

        evidence_found = _get_value(
            item,
            "evidence_found",
            "",
        )

        next_action = _get_value(
            item,
            "next_action",
            "",
        )

        follow_up_question = _get_value(
            item,
            "follow_up_question",
            "",
        )

        normalized.append(
            {
                "requirement_id": _to_text(
                    requirement_id
                ),
                "requirement_name": _to_text(
                    requirement_name
                ),
                "question": _to_text(
                    question
                ),
                "answer": _to_text(
                    answer
                ),
                "status": _to_text(
                    status
                ).upper(),
                "reasoning": _to_text(
                    reasoning
                ),
                "evidence_found": _to_text(
                    evidence_found
                ),
                "next_action": _to_text(
                    next_action
                ),
                "follow_up_question": _to_text(
                    follow_up_question
                ),
            }
        )

    return normalized


def _build_strengths(
    evidence: List[Dict[str, Any]],
) -> List[str]:
    """
    Extract strengths from MATCHED requirements.
    """

    strengths = []

    for item in evidence:

        status = item.get(
            "status",
            "",
        ).upper()

        if status != "MATCHED":
            continue

        requirement_name = item.get(
            "requirement_name",
            "",
        )

        evidence_text = item.get(
            "evidence",
            "",
        )

        reasoning = item.get(
            "reasoning",
            "",
        )

        if requirement_name:

            if evidence_text:
                strengths.append(
                    f"{requirement_name}: {evidence_text}"
                )

            elif reasoning:
                strengths.append(
                    f"{requirement_name}: {reasoning}"
                )

            else:
                strengths.append(
                    requirement_name
                )

    return strengths


def _build_unresolved_items(
    evidence: List[Dict[str, Any]],
) -> List[str]:
    """
    Extract requirements that are not fully matched.
    """

    unresolved = []

    for item in evidence:

        status = item.get(
            "status",
            "",
        ).upper()

        if status == "MATCHED":
            continue

        requirement_name = item.get(
            "requirement_name",
            "",
        )

        reasoning = item.get(
            "reasoning",
            "",
        )

        if not requirement_name:
            requirement_name = (
                item.get(
                    "requirement_id",
                    "",
                )
            )

        if requirement_name:

            if reasoning:
                unresolved.append(
                    f"{requirement_name}: {reasoning}"
                )

            else:
                unresolved.append(
                    requirement_name
                )

    return unresolved


def _build_summary(
    candidate_name: str,
    role: str,
    evidence: List[Dict[str, Any]],
) -> str:
    """
    Build a simple evidence-based summary.
    """

    total = len(evidence)

    matched = sum(
        1
        for item in evidence
        if item.get("status", "").upper()
        == "MATCHED"
    )

    unclear = sum(
        1
        for item in evidence
        if item.get("status", "").upper()
        == "UNCLEAR"
    )

    missing = sum(
        1
        for item in evidence
        if item.get("status", "").upper()
        == "MISSING"
    )

    if total == 0:
        return (
            f"No structured requirement evidence "
            f"was available for {candidate_name} "
            f"against the {role} role."
        )

    return (
        f"{candidate_name} was analyzed against "
        f"the {role} requirements. "
        f"{matched} of {total} requirements have "
        f"directly matched evidence, "
        f"{unclear} are unclear, and "
        f"{missing} are currently missing."
    )


def generate_report(
    candidate_name: str,
    role: str,
    evidence: Any,
    interview_findings: Any = None,
):
    """
    Generate the final HireFlow report.

    Parameters
    ----------
    candidate_name:
        Candidate's name.

    role:
        Job role.

    evidence:
        Requirement-by-requirement evidence list.

    interview_findings:
        Optional interview evaluation results.

    Returns
    -------
    Dictionary containing the final report.
    """

    # ---------------------------------------------------------
    # STEP 1
    # Normalize evidence
    # ---------------------------------------------------------

    normalized_evidence = _normalize_evidence(
        evidence
    )

    # ---------------------------------------------------------
    # STEP 2
    # Normalize interview findings
    # ---------------------------------------------------------

    normalized_interviews = (
        _normalize_interview_findings(
            interview_findings
        )
    )

    # ---------------------------------------------------------
    # STEP 3
    # Calculate evidence counts
    # ---------------------------------------------------------

    total_requirements = len(
        normalized_evidence
    )

    matched_count = sum(
        1
        for item in normalized_evidence
        if item["status"] == "MATCHED"
    )

    unclear_count = sum(
        1
        for item in normalized_evidence
        if item["status"] == "UNCLEAR"
    )

    missing_count = sum(
        1
        for item in normalized_evidence
        if item["status"] == "MISSING"
    )

    # ---------------------------------------------------------
    # STEP 4
    # Build strengths
    # ---------------------------------------------------------

    strengths = _build_strengths(
        normalized_evidence
    )

    # ---------------------------------------------------------
    # STEP 5
    # Build unresolved requirements
    # ---------------------------------------------------------

    unresolved_items = _build_unresolved_items(
        normalized_evidence
    )

    # ---------------------------------------------------------
    # STEP 6
    # Build summary
    # ---------------------------------------------------------

    summary = _build_summary(
        candidate_name=candidate_name,
        role=role,
        evidence=normalized_evidence,
    )

    # ---------------------------------------------------------
    # STEP 7
    # Add interview information to unresolved items
    # ---------------------------------------------------------

    interview_notes = []

    for finding in normalized_interviews:

        requirement_name = finding.get(
            "requirement_name",
            "",
        )

        status = finding.get(
            "status",
            "",
        )

        reasoning = finding.get(
            "reasoning",
            "",
        )

        evidence_found = finding.get(
            "evidence_found",
            "",
        )

        if requirement_name:

            note = requirement_name

            if status:
                note += f" — Interview status: {status}"

            if evidence_found:
                note += (
                    f". Evidence found: "
                    f"{evidence_found}"
                )

            elif reasoning:
                note += (
                    f". Reasoning: "
                    f"{reasoning}"
                )

            interview_notes.append(
                note
            )

    # ---------------------------------------------------------
    # STEP 8
    # Build final report
    # ---------------------------------------------------------

    report = {
        "candidate_name": _to_text(
            candidate_name
        ),

        "role": _to_text(
            role
        ),

        "summary": summary,

        "strengths": strengths,

        "unresolved_items": unresolved_items,

        "interview_findings": normalized_interviews,

        "interview_notes": interview_notes,

        "evidence_coverage": {
            "total": total_requirements,
            "matched": matched_count,
            "unclear": unclear_count,
            "missing": missing_count,
        },

        "evidence": normalized_evidence,

        "human_review_note": (
            "This report organizes candidate evidence "
            "and interview findings for human review. "
            "It does not make an employment decision."
        ),
    }

    return report