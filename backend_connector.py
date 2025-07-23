# backend_connector.py
import json
import logging
from typing import Dict, Any, List
from guideline_processor import load_guidelines
from rule_based_recommendations import generate_rule_based_recommendation

# Try to import enhanced text extractor with AWS Comprehend Medical support
try:
    from enhanced_text_extractor import extract_patient_data_enhanced
    from aws_config import check_aws_comprehend_availability
    AWS_AVAILABLE = True
except ImportError:
    from text_extractor import extract_patient_data
    AWS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load guidelines once when the module is imported
guidelines = load_guidelines()

def get_guidelines() -> Dict[str, Any]:
    """Return the loaded guidelines"""
    return guidelines

def process_user_input(user_input: str, conversation_history: List[Dict[str, str]] = None, use_aws_comprehend: bool = False) -> Dict[str, Any]:
    """
    Process user input and return recommendations.

    Args:
        user_input: The user's question or patient information
        conversation_history: List of previous messages in the conversation
        use_aws_comprehend: Whether to use AWS Comprehend Medical for text extraction

    Returns:
        Dictionary containing recommendations and other processed data
    """
    try:
        # Check AWS availability if requested
        if use_aws_comprehend and AWS_AVAILABLE:
            is_available, status_msg = check_aws_comprehend_availability()
            if not is_available:
                logger.warning(f"AWS Comprehend Medical not available: {status_msg}")
                use_aws_comprehend = False
        
        # Extract patient data from input
        if AWS_AVAILABLE and use_aws_comprehend:
            patient_data = extract_patient_data_enhanced(user_input, use_aws_comprehend=True)
        elif AWS_AVAILABLE:
            patient_data = extract_patient_data_enhanced(user_input, use_aws_comprehend=False)
        else:
            patient_data = extract_patient_data(user_input)

        # Generate recommendation using rule-based system
        recommendation = generate_rule_based_recommendation(user_input, patient_data, guidelines)

        return {
            "success": True,
            "recommendations": recommendation,
            "patient_data": patient_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recommendations": f"Error processing request: {str(e)}"
        }