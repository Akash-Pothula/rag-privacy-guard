"""Robust JSON extraction from LLM output."""

import json
import re
from typing import Any, Dict, Optional


def extract_json(text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract JSON from LLM output, handling various formats.
    
    Handles:
    - Clean JSON
    - JSON in markdown code fences
    - JSON with extra text before/after
    - Completely invalid input (returns fallback)
    
    Args:
        text: Raw LLM output text
        fallback: Default value to return if parsing fails
        
    Returns:
        Dict[str, Any]: Parsed JSON object or fallback
    """
    if fallback is None:
        fallback = {}
    
    if not text or not isinstance(text, str):
        return fallback
    
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code fences
    json_fence_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_fence_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON object in text (look for { ... })
    brace_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\})*)*\})*)*\}'
    matches = re.findall(brace_pattern, text, re.DOTALL)
    
    # Try matches from longest to shortest
    for match in sorted(matches, key=len, reverse=True):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON array in text (look for [ ... ])
    bracket_pattern = r'\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\])*)*\])*)*\]'
    matches = re.findall(bracket_pattern, text, re.DOTALL)
    
    for match in sorted(matches, key=len, reverse=True):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # All parsing attempts failed
    return fallback


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with a default.
    
    Args:
        data: Dictionary to extract from
        key: Key to look up
        default: Default value if key not found
        
    Returns:
        Value from dict or default
    """
    return data.get(key, default)
