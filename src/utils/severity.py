"""Severity comparison and computation helpers."""

from typing import List
from src.agents.models.evaluation import Severity


def max_severity(severities: List[Severity]) -> Severity:
    """
    Return the maximum severity from a list of severities.
    
    Args:
        severities: List of Severity enum values
        
    Returns:
        Severity: The highest severity level
    """
    if not severities:
        return Severity.PASS
    
    return max(severities)


def severity_from_string(severity_str: str) -> Severity:
    """
    Convert a string to Severity enum, with fallback to PASS.
    
    Args:
        severity_str: String representation of severity
        
    Returns:
        Severity: Corresponding Severity enum value
    """
    try:
        return Severity[severity_str.upper()]
    except (KeyError, AttributeError):
        return Severity.PASS


def compute_overall_severity(principle_severities: List[str], 
                            pii_severities: List[str],
                            jailbreak_severity: str = "PASS") -> Severity:
    """
    Compute overall severity from multiple evaluation layers.
    
    Args:
        principle_severities: List of severity strings from principle evaluation
        pii_severities: List of severity strings from PII detection
        jailbreak_severity: Severity string from jailbreak detection
        
    Returns:
        Severity: Overall maximum severity
    """
    all_severities = []
    
    # Convert principle severities
    for sev_str in principle_severities:
        all_severities.append(severity_from_string(sev_str))
    
    # Convert PII severities
    for sev_str in pii_severities:
        all_severities.append(severity_from_string(sev_str))
    
    # Convert jailbreak severity
    all_severities.append(severity_from_string(jailbreak_severity))
    
    return max_severity(all_severities)
