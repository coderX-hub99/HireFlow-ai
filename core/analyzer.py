from core.llm import ask_structured
from core.prompts import (
    JOB_PROMPT,
    CANDIDATE_PROMPT,
)
from core.schemas import (
    JobAnalysis,
    CandidateAnalysis,
)
from core.parser import clip_text


def analyze_job_description(job_text: str) -> JobAnalysis:

    prompt = f"""
JOB DESCRIPTION:

{clip_text(job_text)}

Analyze this job description.
"""

    return ask_structured(
        JOB_PROMPT,
        prompt,
        JobAnalysis
    )


def analyze_candidate(
    resume_text: str,
    job: JobAnalysis
) -> CandidateAnalysis:

    requirements = "\n".join(
        [
            f"{r.id}: {r.name} — {r.description}"
            for r in job.requirements
        ]
    )

    prompt = f"""
JOB ROLE:
{job.role}

JOB REQUIREMENTS:
{requirements}

CANDIDATE RESUME:

{clip_text(resume_text)}

Analyze this candidate against the requirements.
"""

    return ask_structured(
        CANDIDATE_PROMPT,
        prompt,
        CandidateAnalysis
    )