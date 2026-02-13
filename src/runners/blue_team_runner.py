"""CLI entry point for Blue Team Agent."""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

from src.config import Config
from src.agents.blue_team_agent import BlueTeamAgent
from src.agents.models.evaluation import EvaluationResult
from src.utils.reporting import (
    print_evaluation_result, export_results_json, print_summary
)


def load_scenarios(file_path: str) -> List[Dict[str, Any]]:
    """
    Load test scenarios from JSON file.
    
    Args:
        file_path: Path to JSON file containing scenarios
        
    Returns:
        List of scenario dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Handle both array of scenarios and object with scenarios key
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'scenarios' in data:
                return data['scenarios']
            else:
                print(f"Error: Invalid scenario file format")
                return []
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return []


def run_evaluation(scenarios: List[Dict[str, Any]], 
                   output_path: str = None) -> List[EvaluationResult]:
    """
    Run Blue Team evaluation on scenarios.
    
    Args:
        scenarios: List of scenario dictionaries
        output_path: Optional path to save JSON results
        
    Returns:
        List of EvaluationResult objects
    """
    # Validate configuration
    if not Config.validate():
        print("\n⚠ Configuration Error: Missing required environment variables")
        print("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
        print("You can copy .env.example to .env and fill in your values")
        sys.exit(1)
    
    agent = BlueTeamAgent()
    results = []
    
    print(f"\n🔍 Running Blue Team evaluation on {len(scenarios)} scenario(s)...\n")
    
    for i, scenario in enumerate(scenarios, 1):
        scenario_id = scenario.get('scenario_id', f'scenario_{i}')
        description = scenario.get('description', 'No description')
        adversarial_prompt = scenario.get('adversarial_prompt', '')
        rag_response = scenario.get('rag_response', '')
        
        print(f"[{i}/{len(scenarios)}] Evaluating: {scenario_id} - {description}")
        
        if not adversarial_prompt or not rag_response:
            print(f"  ⚠ Skipping: Missing prompt or response")
            continue
        
        try:
            result = agent.evaluate(
                adversarial_prompt=adversarial_prompt,
                rag_response=rag_response,
                scenario_id=scenario_id
            )
            results.append(result)
            
            # Print brief status
            severity_icon = "✓" if result.overall_severity == "PASS" else "❌"
            print(f"  {severity_icon} {result.overall_severity} (Risk: {result.risk_score:.2f}/10.0)")
            
        except Exception as e:
            print(f"  ❌ Error during evaluation: {e}")
            continue
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Blue Team Agent - RAG Privacy Guard Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo scenarios
  python -m src.runners.blue_team_runner
  
  # Run custom scenarios from file
  python -m src.runners.blue_team_runner --file attacks.json
  
  # Save results to JSON
  python -m src.runners.blue_team_runner --output results.json
  
  # Run custom scenarios and save results
  python -m src.runners.blue_team_runner --file attacks.json --output results.json
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to JSON file containing test scenarios'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save JSON output results'
    )
    
    parser.add_argument(
        '--no-details',
        action='store_true',
        help='Hide detailed evaluation breakdown'
    )
    
    args = parser.parse_args()
    
    # Determine scenario file
    if args.file:
        scenario_file = args.file
    else:
        # Use demo scenarios
        repo_root = Path(__file__).parent.parent.parent
        scenario_file = repo_root / 'data' / 'demo_scenarios.json'
    
    # Load scenarios
    scenarios = load_scenarios(str(scenario_file))
    
    if not scenarios:
        print("No scenarios to evaluate. Exiting.")
        sys.exit(1)
    
    # Run evaluation
    results = run_evaluation(scenarios, args.output)
    
    if not results:
        print("\n❌ No results generated. Check for errors above.")
        sys.exit(1)
    
    # Print detailed results
    if not args.no_details:
        print("\n" + "="*80)
        print("DETAILED RESULTS")
        print("="*80)
        for result in results:
            print_evaluation_result(result, show_details=True)
    
    # Print summary
    print_summary(results)
    
    # Export to JSON if requested
    if args.output:
        export_results_json(results, args.output)
    
    print("\n✓ Evaluation complete!")


if __name__ == "__main__":
    main()
