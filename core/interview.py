from core.llm import ask_structured
from core.prompts import (
    QUESTION_PROMPT,
    EVALUATION_PROMPT,
)
from core.schemas import (
    InterviewQuestion,
    AnswerEvaluation,
    RequirementEvidence,
)


def generate_question(
    requirement,
    previous_context=""
):

    prompt = f"""
Requirement:

ID: {requirement.requirement_id}
Name: {requirement.requirement_name}

Current status:
{requirement.status}

Existing evidence:
{requirement.evidence}

Reasoning:
{requirement.reasoning}

Previous context:
{previous_context}

Generate the next targeted interview question.
"""

    return ask_structured(
        QUESTION_PROMPT,
        prompt,
        InterviewQuestion
    )


def evaluate_answer(
    requirement,
    question: str,
    answer: str,
    previous_turns=""
):

    prompt = f"""
REQUIREMENT:

ID:
{requirement.requirement_id}

Name:
{requirement.requirement_name}

Current status:
{requirement.status}

Existing resume evidence:
{requirement.evidence}

INTERVIEW QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

PREVIOUS INTERVIEW CONTEXT:
{previous_turns}

Evaluate the answer.
"""

    return ask_structured(
        EVALUATION_PROMPT,
        prompt,
        AnswerEvaluation
    )


def apply_evaluation(
    evidence: RequirementEvidence,
    evaluation: AnswerEvaluation
):

    if evaluation.status == "VALIDATED":

        return evidence.model_copy(
            update={
                "status": "MATCHED",
                "evidence": (
                    evidence.evidence
                    + "\n\nInterview evidence: "
                    + evaluation.evidence_found
                ),
                "reasoning": evaluation.reasoning,
                "confidence": max(
                    evidence.confidence,
                    0.9
                ),
            }
        )

    if evaluation.status == "PARTIAL":

        return evidence.model_copy(
            update={
                "status": "UNCLEAR",
                "evidence": (
                    evidence.evidence
                    + "\n\nPartial interview evidence: "
                    + evaluation.evidence_found
                ),
                "reasoning": evaluation.reasoning,
                "confidence": max(
                    evidence.confidence,
                    0.6
                ),
            }
        )

    return evidence.model_copy(
        update={
            "status": "UNCLEAR",
            "reasoning": evaluation.reasoning,
        }
    )