import pytest
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"

class EvidenceType(str, Enum):
    KNOWN = "known"
    INFERRED = "inferred"

class UnsupportedClaim(Exception):
    pass

class QuestionAnswer(BaseModel):
    question_id: int
    answer: str
    evidence_strength: EvidenceStrength
    evidence_type: EvidenceType

class MockAuditor:
    def __init__(self):
        self.questions_count = 15
        self._answers: Dict[int, QuestionAnswer] = {}
        for i in range(1, 16):
            self._answers[i] = QuestionAnswer(
                question_id=i,
                answer=f"Answer to question {i}",
                evidence_strength=EvidenceStrength.STRONG,
                evidence_type=EvidenceType.KNOWN
            )

    def answer_question(self, question_id: int) -> QuestionAnswer:
        if question_id not in self._answers:
            raise ValueError("Invalid question ID")

        answer = self._answers[question_id]
        if answer.evidence_strength == EvidenceStrength.NONE:
            raise UnsupportedClaim(f"Cannot answer question {question_id} with certainty without adequate evidence.")

        return answer

    def set_mock_answer(self, question_id: int, answer: QuestionAnswer):
        self._answers[question_id] = answer


def test_auditor_answers_15_questions_with_evidence_strength():
    auditor = MockAuditor()
    answered_count = 0
    for i in range(1, 16):
        ans = auditor.answer_question(i)
        assert ans.evidence_strength in [EvidenceStrength.STRONG, EvidenceStrength.MODERATE, EvidenceStrength.WEAK]
        answered_count += 1
    assert answered_count == 15

def test_auditor_refuses_unsupported_certainty_claims():
    auditor = MockAuditor()

    # Mock an unsupported claim
    auditor.set_mock_answer(5, QuestionAnswer(
        question_id=5,
        answer="I don't know",
        evidence_strength=EvidenceStrength.NONE,
        evidence_type=EvidenceType.INFERRED
    ))

    with pytest.raises(UnsupportedClaim):
        auditor.answer_question(5)

def test_auditor_differentiates_known_vs_inferred():
    auditor = MockAuditor()

    # Set up a known answer
    auditor.set_mock_answer(1, QuestionAnswer(
        question_id=1,
        answer="API rate limit is 100 req/s",
        evidence_strength=EvidenceStrength.STRONG,
        evidence_type=EvidenceType.KNOWN
    ))

    # Set up an inferred answer
    auditor.set_mock_answer(2, QuestionAnswer(
        question_id=2,
        answer="Model likely uses context window of 8k based on behavior",
        evidence_strength=EvidenceStrength.WEAK,
        evidence_type=EvidenceType.INFERRED
    ))

    ans1 = auditor.answer_question(1)
    assert ans1.evidence_type == EvidenceType.KNOWN

    ans2 = auditor.answer_question(2)
    assert ans2.evidence_type == EvidenceType.INFERRED
