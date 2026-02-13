"""Data models for evaluation results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class Severity(Enum):
    """Severity levels for privacy violations."""
    PASS = "PASS"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    def __lt__(self, other):
        """Compare severity levels for ordering."""
        if not isinstance(other, Severity):
            return NotImplemented
        order = [Severity.PASS, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) < order.index(other)
    
    def __le__(self, other):
        """Compare severity levels for ordering."""
        return self == other or self < other
    
    def __gt__(self, other):
        """Compare severity levels for ordering."""
        if not isinstance(other, Severity):
            return NotImplemented
        return not self <= other
    
    def __ge__(self, other):
        """Compare severity levels for ordering."""
        return self == other or self > other


class Principle(Enum):
    """Philips Privacy Principles."""
    LAWFULNESS_FAIRNESS_TRANSPARENCY = "lawfulness_fairness_transparency"
    PURPOSE_LIMITATION = "purpose_limitation"
    DATA_MINIMIZATION = "data_minimization"
    ACCURACY = "accuracy"
    STORAGE_LIMITATION = "storage_limitation"
    INTEGRITY_CONFIDENTIALITY = "integrity_confidentiality"


class PIICategory(Enum):
    """Categories of Personally Identifiable Information."""
    FULL_NAME = "FULL_NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SSN_NATIONAL_ID = "SSN_NATIONAL_ID"
    ADDRESS = "ADDRESS"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    MEDICAL_ID = "MEDICAL_ID"
    FINANCIAL = "FINANCIAL"
    BIOMETRIC = "BIOMETRIC"
    IP_ADDRESS = "IP_ADDRESS"
    DEVICE_ID = "DEVICE_ID"
    LOCATION_DATA = "LOCATION_DATA"
    GENETIC_DATA = "GENETIC_DATA"
    CREDENTIALS = "CREDENTIALS"
    QUASI_IDENTIFIER = "QUASI_IDENTIFIER"


@dataclass
class PrincipleResult:
    """Result of evaluating a single privacy principle."""
    principle: str
    violated: bool
    severity: str
    reasoning: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class PIIItem:
    """A detected PII item."""
    category: str
    value: str
    severity: str
    context: str = ""


@dataclass
class JailbreakResult:
    """Result of jailbreak detection analysis."""
    jailbreak_detected: bool
    jailbreak_type: str
    severity: str
    reasoning: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation result from Blue Team Agent."""
    scenario_id: Optional[str] = None
    adversarial_prompt: str = ""
    rag_response: str = ""
    
    # Layer 1: Master Evaluation
    principle_results: List[PrincipleResult] = field(default_factory=list)
    
    # Layer 2: PII Detection
    pii_items: List[PIIItem] = field(default_factory=list)
    
    # Layer 3: Jailbreak Detection
    jailbreak_result: Optional[JailbreakResult] = None
    
    # Reconciliation
    overall_severity: str = "PASS"
    risk_score: float = 0.0
    final_verdict: str = ""
    reconciliation_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation result to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "adversarial_prompt": self.adversarial_prompt,
            "rag_response": self.rag_response,
            "principle_results": [
                {
                    "principle": pr.principle,
                    "violated": pr.violated,
                    "severity": pr.severity,
                    "reasoning": pr.reasoning,
                    "evidence": pr.evidence
                }
                for pr in self.principle_results
            ],
            "pii_items": [
                {
                    "category": pii.category,
                    "value": pii.value,
                    "severity": pii.severity,
                    "context": pii.context
                }
                for pii in self.pii_items
            ],
            "jailbreak_result": {
                "jailbreak_detected": self.jailbreak_result.jailbreak_detected,
                "jailbreak_type": self.jailbreak_result.jailbreak_type,
                "severity": self.jailbreak_result.severity,
                "reasoning": self.jailbreak_result.reasoning,
                "evidence": self.jailbreak_result.evidence
            } if self.jailbreak_result else None,
            "overall_severity": self.overall_severity,
            "risk_score": self.risk_score,
            "final_verdict": self.final_verdict,
            "reconciliation_notes": self.reconciliation_notes
        }
