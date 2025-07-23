"""
Enhanced Text Extractor with AWS Comprehend Medical Integration

This module extends the existing text extraction capabilities by optionally
integrating with AWS Comprehend Medical for more accurate medical entity recognition.
"""

import re
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_patient_data_enhanced(text: str, use_aws_comprehend: bool = False) -> Dict[str, Any]:
    """
    Enhanced patient data extraction with optional AWS Comprehend Medical integration.
    
    Args:
        text: Clinical text to process
        use_aws_comprehend: Whether to use AWS Comprehend Medical (requires setup)
        
    Returns:
        Enhanced patient data structure
    """
    if use_aws_comprehend:
        try:
            from aws_comprehend_medical import extract_with_comprehend
            return extract_with_comprehend(text)
        except ImportError:
            logger.warning("AWS Comprehend Medical not available. Install boto3 and configure AWS credentials.")
        except Exception as e:
            logger.warning(f"AWS Comprehend Medical failed: {e}. Falling back to regex extraction.")
    
    # Fallback to existing regex-based extraction
    return extract_patient_data_regex(text)

def extract_patient_data_regex(text: str) -> Dict[str, Any]:
    """
    Original regex-based patient data extraction (enhanced version).
    This is your existing logic with some improvements.
    """
    patient_data = {
        "age": None,
        "sex": None,
        "hf_stage": None,
        "hf_type": None,
        "lvef": None,
        "nyha_class": None,
        "medications": [],
        "lab_values": {},
        "comorbidities": [],
        "notes": [],
        "extraction_method": "regex"
    }
    
    # Enhanced age extraction - more specific patterns to avoid false matches
    age_patterns = [
        r'(\d+)\s*(?:year[s]?\s+old|yo|y\.?o\.?)\b',
        r'(\d+)\s*(?:year|yr)s?\s+old\b',
        r'\bage\s*:?\s*(\d+)\b',
        r'(\d+)\s*years?\s+of\s+age\b',
        r'^\s*(\d+)\s*(?:year[s]?\s+old|yo)',  # At start of line
        r'(\d{2})\s*-\s*year[s]?\s*-\s*old'   # Format like "72-year-old"
    ]
    
    for pattern in age_patterns:
        age_match = re.search(pattern, text, re.IGNORECASE)
        if age_match:
            age = int(age_match.group(1))
            # Sanity check: age should be reasonable (18-120)
            if 18 <= age <= 120:
                patient_data["age"] = age
                break
    
    # Enhanced sex/gender extraction
    gender_patterns = [
        (r'\b(?:male|man|gentleman|mr\.?)\b', "male"),
        (r'\b(?:female|woman|lady|ms\.?|mrs\.?)\b', "female")
    ]
    
    for pattern, gender in gender_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            patient_data["sex"] = gender
            break
    
    # Enhanced HF stage extraction
    stage_patterns = [
        r'(?:heart\s+failure\s+)?stage\s+([A-D])',
        r'HF\s+stage\s+([A-D])',
        r'ACC/AHA\s+stage\s+([A-D])'
    ]
    
    for pattern in stage_patterns:
        stage_match = re.search(pattern, text, re.IGNORECASE)
        if stage_match:
            patient_data["hf_stage"] = stage_match.group(1).upper()
            break
    
    # Enhanced HF type extraction
    hf_type_patterns = [
        (r'\bHFrEF\b|heart\s+failure\s+with\s+reduced\s+ejection\s+fraction', "HFrEF"),
        (r'\bHFpEF\b|heart\s+failure\s+with\s+preserved\s+ejection\s+fraction', "HFpEF"),
        (r'\bHFmrEF\b|heart\s+failure\s+with\s+mid-range\s+ejection\s+fraction', "HFmrEF"),
        (r'\bHFimpEF\b|heart\s+failure\s+with\s+improved\s+ejection\s+fraction', "HFimpEF")
    ]
    
    for pattern, hf_type in hf_type_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            patient_data["hf_type"] = hf_type
            break
    
    # Enhanced LVEF extraction
    lvef_patterns = [
        r'LVEF\s*(?:of|:|=|is)?\s*(\d+)(?:\s*%)?',
        r'ejection\s+fraction\s*(?:of|:|=|is)?\s*(\d+)(?:\s*%)?',
        r'EF\s*(?:of|:|=|is)?\s*(\d+)(?:\s*%)?'
    ]
    
    for pattern in lvef_patterns:
        lvef_match = re.search(pattern, text, re.IGNORECASE)
        if lvef_match:
            lvef = int(lvef_match.group(1))
            patient_data["lvef"] = lvef
            
            # Auto-determine HF type if not specified
            if not patient_data["hf_type"]:
                if lvef <= 40:
                    patient_data["hf_type"] = "HFrEF"
                elif lvef >= 50:
                    patient_data["hf_type"] = "HFpEF"
                else:
                    patient_data["hf_type"] = "HFmrEF"
            break
    
    # Enhanced NYHA class extraction
    nyha_patterns = [
        r'NYHA\s+(?:class|functional\s+class)?\s*([I]{1,4}|[1-4])',
        r'functional\s+class\s*([I]{1,4}|[1-4])',
        r'FC\s*([I]{1,4}|[1-4])'
    ]
    
    for pattern in nyha_patterns:
        nyha_match = re.search(pattern, text, re.IGNORECASE)
        if nyha_match:
            nyha = nyha_match.group(1)
            nyha_mapping = {'I': 1, '1': 1, 'II': 2, '2': 2, 'III': 3, '3': 3, 'IV': 4, '4': 4}
            patient_data["nyha_class"] = nyha_mapping.get(nyha)
            break
    
    # Enhanced medication extraction
    patient_data["medications"] = extract_medications_enhanced(text)
    
    # Enhanced lab values extraction
    patient_data["lab_values"] = extract_lab_values_enhanced(text)
    
    # Enhanced comorbidities extraction
    patient_data["comorbidities"] = extract_comorbidities_enhanced(text)
    
    return patient_data

def extract_medications_enhanced(text: str) -> List[Dict[str, Any]]:
    """Enhanced medication extraction with better parsing."""
    medications = []
    
    # Common heart failure medications
    hf_medications = [
        'lisinopril', 'enalapril', 'captopril', 'ramipril', 'fosinopril',  # ACE inhibitors
        'losartan', 'valsartan', 'candesartan', 'telmisartan', 'olmesartan',  # ARBs
        'metoprolol', 'carvedilol', 'bisoprolol', 'nebivolol',  # Beta blockers
        'spironolactone', 'eplerenone',  # MRAs
        'sacubitril/valsartan', 'entresto',  # ARNI
        'furosemide', 'torsemide', 'bumetanide',  # Diuretics
        'digoxin', 'ivabradine', 'hydralazine', 'isosorbide'
    ]
    
    # Enhanced medication pattern
    med_pattern = r'([A-Za-z]+(?:[\/\-][A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(?:mg|mcg|units?)\s*(?:(daily|bid|tid|qid|once\s+daily|twice\s+daily|three\s+times\s+daily|four\s+times\s+daily))?'
    
    matches = re.finditer(med_pattern, text, re.IGNORECASE)
    
    for match in matches:
        med_name = match.group(1).lower().strip()
        med_dose = float(match.group(2))
        frequency = match.group(3) if match.group(3) else "daily"
        
        # Skip if it's likely a lab value
        lab_indicators = ['k', 'k+', 'potassium', 'na', 'na+', 'sodium', 'cr', 'creatinine', 'bun']
        if med_name in lab_indicators:
            continue
        
        medication = {
            "name": med_name,
            "dose": med_dose,
            "frequency": frequency.lower() if frequency else "daily",
            "is_hf_medication": med_name in hf_medications
        }
        
        medications.append(medication)
    
    return medications

def extract_lab_values_enhanced(text: str) -> Dict[str, Any]:
    """Enhanced lab values extraction."""
    lab_values = {}
    
    # Common lab patterns
    lab_patterns = {
        'potassium': r'(?:K\+?|potassium)\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'sodium': r'(?:Na\+?|sodium)\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'creatinine': r'(?:Cr|creatinine)\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'egfr': r'eGFR\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'bun': r'BUN\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'bnp': r'BNP\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'nt_probnp': r'(?:NT-proBNP|NT\s*pro\s*BNP)\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)',
        'hemoglobin': r'(?:Hgb|hemoglobin)\s*(?:of|:|=|is)?\s*(\d+(?:\.\d+)?)'
    }
    
    for lab_name, pattern in lab_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            lab_values[lab_name] = {
                'value': float(match.group(1)),
                'unit': _get_lab_unit(lab_name)
            }
    
    return lab_values

def extract_comorbidities_enhanced(text: str) -> List[Dict[str, Any]]:
    """Enhanced comorbidities extraction."""
    comorbidities = []
    
    # Common comorbidities in heart failure patients
    comorbidity_patterns = {
        'diabetes': r'\b(?:diabetes|DM|T2DM|type\s+2\s+diabetes)\b',
        'hypertension': r'\b(?:hypertension|HTN|high\s+blood\s+pressure)\b',
        'chronic_kidney_disease': r'\b(?:CKD|chronic\s+kidney\s+disease|renal\s+insufficiency)\b',
        'atrial_fibrillation': r'\b(?:atrial\s+fibrillation|AF|A-fib)\b',
        'coronary_artery_disease': r'\b(?:CAD|coronary\s+artery\s+disease|CHD)\b',
        'copd': r'\b(?:COPD|chronic\s+obstructive\s+pulmonary\s+disease)\b',
        'sleep_apnea': r'\b(?:sleep\s+apnea|OSA|obstructive\s+sleep\s+apnea)\b',
        'depression': r'\b(?:depression|depressive\s+disorder)\b'
    }
    
    for condition, pattern in comorbidity_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            comorbidities.append({
                'condition': condition.replace('_', ' ').title(),
                'confidence': 0.9,  # High confidence for pattern-matched conditions
                'extraction_method': 'regex'
            })
    
    return comorbidities

def _get_lab_unit(lab_name: str) -> str:
    """Get the standard unit for a lab value."""
    units = {
        'potassium': 'mEq/L',
        'sodium': 'mEq/L',
        'creatinine': 'mg/dL',
        'egfr': 'mL/min/1.73m²',
        'bun': 'mg/dL',
        'bnp': 'pg/mL',
        'nt_probnp': 'pg/mL',
        'hemoglobin': 'g/dL'
    }
    return units.get(lab_name, '')

# Backward compatibility
def extract_patient_data(text: str) -> Dict[str, Any]:
    """
    Backward compatible function that maintains the original API.
    Enhanced with better regex patterns but same return structure.
    """
    return extract_patient_data_regex(text)
