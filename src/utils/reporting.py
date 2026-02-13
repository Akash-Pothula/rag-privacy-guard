"""Pretty-print terminal reports with color and JSON export."""

import json
from typing import Dict, Any, List
from src.agents.models.evaluation import EvaluationResult, Severity


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


def get_severity_color(severity: str) -> str:
    """Get color code for severity level."""
    severity_colors = {
        "CRITICAL": Colors.RED,
        "HIGH": Colors.RED,
        "MEDIUM": Colors.YELLOW,
        "LOW": Colors.BLUE,
        "PASS": Colors.GREEN
    }
    return severity_colors.get(severity.upper(), Colors.RESET)


def print_separator(char: str = "=", length: int = 80):
    """Print a separator line."""
    print(char * length)


def print_section_header(title: str):
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print_separator("-", len(title))


def print_evaluation_result(result: EvaluationResult, show_details: bool = True):
    """
    Pretty-print an evaluation result to terminal.
    
    Args:
        result: EvaluationResult to display
        show_details: Whether to show detailed breakdown
    """
    print_separator()
    print(f"{Colors.BOLD}EVALUATION RESULT{Colors.RESET}")
    print_separator()
    
    # Scenario info
    if result.scenario_id:
        print(f"\n{Colors.BOLD}Scenario ID:{Colors.RESET} {result.scenario_id}")
    
    # Overall verdict
    severity_color = get_severity_color(result.overall_severity)
    print(f"\n{Colors.BOLD}Overall Severity:{Colors.RESET} {severity_color}{result.overall_severity}{Colors.RESET}")
    print(f"{Colors.BOLD}Risk Score:{Colors.RESET} {result.risk_score:.2f}/10.0")
    print(f"{Colors.BOLD}Verdict:{Colors.RESET} {result.final_verdict}")
    
    if not show_details:
        return
    
    # Adversarial Prompt
    print_section_header("Adversarial Prompt")
    print(result.adversarial_prompt[:500] + "..." if len(result.adversarial_prompt) > 500 else result.adversarial_prompt)
    
    # RAG Response
    print_section_header("RAG Response")
    print(result.rag_response[:500] + "..." if len(result.rag_response) > 500 else result.rag_response)
    
    # Principle Results
    print_section_header("Principle Evaluation")
    for pr in result.principle_results:
        severity_color = get_severity_color(pr.severity)
        status = "❌ VIOLATED" if pr.violated else "✓ PASS"
        status_color = Colors.RED if pr.violated else Colors.GREEN
        print(f"\n{Colors.BOLD}{pr.principle}:{Colors.RESET}")
        print(f"  Status: {status_color}{status}{Colors.RESET}")
        print(f"  Severity: {severity_color}{pr.severity}{Colors.RESET}")
        reasoning = pr.reasoning[:200] + "..." if len(pr.reasoning) > 200 else pr.reasoning
        print(f"  Reasoning: {reasoning}")
    
    # PII Detection
    if result.pii_items:
        print_section_header("PII Detection")
        print(f"Found {len(result.pii_items)} PII item(s):")
        for pii in result.pii_items:
            severity_color = get_severity_color(pii.severity)
            print(f"  • {Colors.BOLD}{pii.category}{Colors.RESET}: {pii.value[:50]} ({severity_color}{pii.severity}{Colors.RESET})")
    
    # Jailbreak Detection
    if result.jailbreak_result:
        print_section_header("Jailbreak Detection")
        jr = result.jailbreak_result
        status = "❌ DETECTED" if jr.jailbreak_detected else "✓ NOT DETECTED"
        status_color = Colors.RED if jr.jailbreak_detected else Colors.GREEN
        print(f"Status: {status_color}{status}{Colors.RESET}")
        if jr.jailbreak_detected:
            severity_color = get_severity_color(jr.severity)
            print(f"Type: {jr.jailbreak_type}")
            print(f"Severity: {severity_color}{jr.severity}{Colors.RESET}")
            reasoning = jr.reasoning[:200] + "..." if len(jr.reasoning) > 200 else jr.reasoning
            print(f"Reasoning: {reasoning}")
    
    # Reconciliation Notes
    if result.reconciliation_notes:
        print_section_header("Reconciliation Notes")
        for note in result.reconciliation_notes:
            print(f"  • {note}")
    
    print_separator()


def export_results_json(results: List[EvaluationResult], output_path: str):
    """
    Export evaluation results to JSON file.
    
    Args:
        results: List of EvaluationResult objects
        output_path: Path to output JSON file
    """
    output_data = {
        "results": [result.to_dict() for result in results],
        "summary": {
            "total_scenarios": len(results),
            "critical_count": sum(1 for r in results if r.overall_severity == "CRITICAL"),
            "high_count": sum(1 for r in results if r.overall_severity == "HIGH"),
            "medium_count": sum(1 for r in results if r.overall_severity == "MEDIUM"),
            "low_count": sum(1 for r in results if r.overall_severity == "LOW"),
            "pass_count": sum(1 for r in results if r.overall_severity == "PASS"),
            "average_risk_score": sum(r.risk_score for r in results) / len(results) if results else 0.0
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{Colors.GREEN}✓ Results exported to: {output_path}{Colors.RESET}")


def print_summary(results: List[EvaluationResult]):
    """
    Print summary statistics for multiple evaluation results.
    
    Args:
        results: List of EvaluationResult objects
    """
    print_separator()
    print(f"{Colors.BOLD}SUMMARY{Colors.RESET}")
    print_separator()
    
    total = len(results)
    critical = sum(1 for r in results if r.overall_severity == "CRITICAL")
    high = sum(1 for r in results if r.overall_severity == "HIGH")
    medium = sum(1 for r in results if r.overall_severity == "MEDIUM")
    low = sum(1 for r in results if r.overall_severity == "LOW")
    passed = sum(1 for r in results if r.overall_severity == "PASS")
    avg_risk = sum(r.risk_score for r in results) / total if total > 0 else 0.0
    
    print(f"\n{Colors.BOLD}Total Scenarios:{Colors.RESET} {total}")
    print(f"{Colors.RED}Critical:{Colors.RESET} {critical}")
    print(f"{Colors.RED}High:{Colors.RESET} {high}")
    print(f"{Colors.YELLOW}Medium:{Colors.RESET} {medium}")
    print(f"{Colors.BLUE}Low:{Colors.RESET} {low}")
    print(f"{Colors.GREEN}Pass:{Colors.RESET} {passed}")
    print(f"\n{Colors.BOLD}Average Risk Score:{Colors.RESET} {avg_risk:.2f}/10.0")
    
    print_separator()
