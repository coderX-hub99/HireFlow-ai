from core.schemas import (
    CandidateAnalysis,
    RequirementEvidence,
    JobAnalysis,
)


def build_match_result(
    candidate: CandidateAnalysis,
    job: JobAnalysis
):
    """
    Normalize candidate evidence against the complete
    requirement list.
    """

    existing = {
        item.requirement_id: item
        for item in candidate.evidence
    }

    normalized = []

    for requirement in job.requirements:

        if requirement.id in existing:
            evidence = existing[requirement.id]

            normalized.append(
                evidence.model_copy(
                    update={
                        "requirement_name": requirement.name
                    }
                )
            )

        else:
            normalized.append(
                RequirementEvidence(
                    requirement_id=requirement.id,
                    requirement_name=requirement.name,
                    status="MISSING",
                    evidence="No evidence found.",
                    source="Resume",
                    reasoning="The resume did not provide meaningful evidence.",
                    confidence=0.0,
                )
            )

    return normalized


def unresolved_requirements(evidence):
    return [
        item
        for item in evidence
        if item.status in ["UNCLEAR", "MISSING"]
    ]


def evidence_counts(evidence):

    matched = sum(
        x.status == "MATCHED"
        for x in evidence
    )

    unclear = sum(
        x.status == "UNCLEAR"
        for x in evidence
    )

    missing = sum(
        x.status == "MISSING"
        for x in evidence
    )

    return matched, unclear, missing