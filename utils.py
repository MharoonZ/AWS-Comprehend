"""
Utilities Module

This module contains utility functions for the application.
"""

import os
import logging
from typing import Optional

def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def format_recommendation(recommendation: str) -> str:
    """
    Format the recommendation text for better readability.
    
    Args:
        recommendation: The recommendation text
        
    Returns:
        Formatted recommendation text
    """
    lines = recommendation.strip().split("\n")
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Add spacing around headers
        if line.startswith("#"):
            formatted_lines.append("")
            formatted_lines.append(line)
            formatted_lines.append("")
        # Format bullet points
        elif line.startswith("- "):
            formatted_lines.append(line)
        # Format section references
        elif "Section" in line and ":" in line:
            parts = line.split(":", 1)
            formatted_lines.append(f"**{parts[0].strip()}:** {parts[1].strip()}")
        else:
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)
