from typing import Literal
from pydantic import BaseModel, Field


RequirementStatus = Literal["MATCHED", "UNCLEAR", "MISSING"]


class Requirement(BaseModel):
    id: str
    name: str
    description: str
    importance: Literal["REQUIRED", "PREFERRED"]


class JobAnalysis(BaseModel):
    role: str
    company_context: str = ""
    summary: str
    requirements: list[Requirement]


class CandidateProfile(BaseModel):
    name: str
    email: str = ""
    summary: str = ""
    skills: list[str] = []
    experience: list[str] = []
    projects: list[str] = []
    education: list[str] = []


class RequirementEvidence(BaseModel):
    requirement_id: str
    requirement_name: str
    status: RequirementStatus
    evidence: str
    source: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


class CandidateAnalysis(BaseModel):
    profile: CandidateProfile
    evidence: list[RequirementEvidence]


class MatchResult(BaseModel):
    candidate_name: str
    evidence: list[RequirementEvidence]


class InterviewQuestion(BaseModel):
    requirement_id: str
    question: str
    objective: str


class AnswerEvaluation(BaseModel):
    requirement_id: str
    status: Literal["VALIDATED", "PARTIAL", "INSUFFICIENT"]
    evidence_found: str
    reasoning: str
    next_action: Literal["CONTINUE", "FOLLOW_UP", "STOP"]
    follow_up_question: str = ""


class InterviewTurn(BaseModel):
    question: str
    answer: str
    evaluation: AnswerEvaluation


class FinalReport(BaseModel):
    candidate_name: str
    role: str
    summary: str
    strengths: list[str]
    unresolved_items: list[str]
    interview_findings: list[str]
    evidence_notes: list[str]