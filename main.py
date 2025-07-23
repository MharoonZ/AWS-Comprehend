#!/usr/bin/env python3
"""
Heart Failure Guidelines Recommendation System

Processes clinician input about heart failure patients and provides evidence-based recommendations
from the 2022 AHA/ACC/HFSA Heart Failure Guidelines.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional

from guideline_processor import preprocess_guidelines, load_guidelines
from text_extractor import extract_patient_data
from rule_based_recommendations import generate_rule_based_recommendation
from utils import setup_logging

# Try to import rich for colored output
try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    USE_RICH = True
except ImportError:
    USE_RICH = False
    console = None

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate heart failure management recommendations based on clinical guidelines."
    )
    parser.add_argument(
        "--input", "-i", type=str,
        help="Patient information as text input"
    )
    parser.add_argument(
        "--file", "-f", type=str,
        help="File containing patient information"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--preprocess", "-p", action="store_true",
        help="Preprocess and update the guidelines.json file"
    )
    return parser.parse_args()

def get_input_text(args: argparse.Namespace) -> Optional[str]:
    """Get input text from command-line argument or file."""
    if args.input:
        return args.input.strip()
    elif args.file:
        try:
            with open(args.file, 'r') as file:
                return file.read().strip()
        except Exception as e:
            logging.error(f"Error reading input file: {e}")
            return None
    else:
        # Interactive mode
        if USE_RICH:
            console.print("[bold cyan]Enter patient information (press Enter to submit):[/bold cyan]")
        else:
            print("Enter patient information (press Enter to submit):")
        
        # Get single line input
        input_text = input().strip()
        if not input_text:
            if USE_RICH:
                console.print("[bold red]No input provided. Exiting.[/bold red]")
            else:
                print("No input provided. Exiting.")
            return None
        return input_text

def handle_chat_session(guidelines: Dict[str, Any]) -> None:
    """Handle an interactive chat session with the user."""
    if USE_RICH:
        console.print("[bold cyan]Chat session started. Type 'exit' or 'quit' to end the session.[/bold cyan]")
    else:
        print("Chat session started. Type 'exit' or 'quit' to end the session.")
    
    # Initialize conversation history
    conversation_history = []
    
    while True:
        # Get input text
        if USE_RICH:
            console.print("\n[bold cyan]Enter your question or patient information:[/bold cyan]")
        else:
            print("\nEnter your question or patient information:")
        
        input_text = input().strip()
        
        # Check for exit command
        if input_text.lower() in ['exit', 'quit']:
            if USE_RICH:
                console.print("[bold yellow]Ending chat session. Goodbye![/bold yellow]")
            else:
                print("Ending chat session. Goodbye!")
            break
        
        if not input_text:
            continue
        
        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": input_text})
        
        # Extract patient data
        try:
            patient_data = extract_patient_data(input_text)
        except Exception as e:
            if USE_RICH:
                console.print(f"[bold red]Error extracting patient data: {e}[/bold red]")
            else:
                print(f"Error extracting patient data: {e}")
            continue
        
        # Generate recommendation using rule-based system
        try:
            recommendation = generate_rule_based_recommendation(input_text, patient_data, guidelines)
            # Add assistant's response to conversation history
            conversation_history.append({"role": "assistant", "content": recommendation})
        except Exception as e:
            if USE_RICH:
                console.print(f"[bold red]Error generating recommendation: {e}[/bold red]")
            else:
                print(f"Error generating recommendation: {e}")
            continue
        
        # Print recommendation
        if USE_RICH:
            console.print(Panel("RECOMMENDATION BASED ON 2022 AHA/ACC/HFSA HEART FAILURE GUIDELINES", style="bold green"))
            console.print(Panel(recommendation, style="bold white"))
        else:
            print("\n" + "="*80)
            print("RECOMMENDATION BASED ON 2022 AHA/ACC/HFSA HEART FAILURE GUIDELINES")
            print("="*80 + "\n")
            print(recommendation)
            print("\n" + "="*80)

def main() -> int:
    """Main function to run the application."""
    args = parse_args()

    # Suppress noisy logs unless verbose
    if not args.verbose:
        for noisy_logger in ["httpx", "httpcore"]:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    setup_logging(logging.DEBUG if args.verbose else logging.INFO)

    # Welcome banner
    if USE_RICH:
        console.print(Panel("[bold white]Heart Failure Guidelines Recommendation System[/bold white]", style="bold blue"))
    else:
        print("="*80)
        print("Heart Failure Guidelines Recommendation System")
        print("="*80)

    # Preprocess guidelines if requested
    if args.preprocess:
        logging.info("Preprocessing guidelines...")
        preprocess_guidelines()
        logging.info("Guidelines preprocessing completed.")
        return 0

    # Load guidelines
    try:
        guidelines = load_guidelines()
    except Exception as e:
        if USE_RICH:
            console.print(f"[bold red]Error loading guidelines: {e}[/bold red]")
        else:
            print(f"Error loading guidelines: {e}")
        return 1

    # Handle command line input if provided
    if args.input or args.file:
        input_text = get_input_text(args)
        if not input_text:
            return 1
        
        try:
            patient_data = extract_patient_data(input_text)
            from rule_based_recommendations import generate_rule_based_recommendation
            recommendation = generate_rule_based_recommendation(input_text, patient_data, guidelines)
            
            if USE_RICH:
                console.print(Panel("RECOMMENDATION BASED ON 2022 AHA/ACC/HFSA HEART FAILURE GUIDELINES", style="bold green"))
                console.print(Panel(recommendation, style="bold white"))
            else:
                print("\n" + "="*80)
                print("RECOMMENDATION BASED ON 2022 AHA/ACC/HFSA HEART FAILURE GUIDELINES")
                print("="*80 + "\n")
                print(recommendation)
                print("\n" + "="*80)
        except Exception as e:
            if USE_RICH:
                console.print(f"[bold red]Error: {e}[/bold red]")
            else:
                print(f"Error: {e}")
            return 1
    else:
        # Start interactive chat session
        handle_chat_session(guidelines)

    return 0

if __name__ == "__main__":
    sys.exit(main())
