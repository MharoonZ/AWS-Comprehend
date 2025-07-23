"""
Text Extractor Module

Extracts patient data from clinician input text.
"""

import re
import logging
from typing import Dict, Any, List, Optional

def extract_patient_data(text: str) -> Dict[str, Any]:
    """Extract patient data from clinician input text."""
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
        "notes": []
    }
    
    # Extract age
    age_match = re.search(r'(\d+)\s*(?:yo|year[s]?\s+old|-year-old)', text, re.IGNORECASE)
    if age_match:
        patient_data["age"] = int(age_match.group(1))
    else:
        age_match = re.search(r'(\d+)\s*(?:year|yr)', text, re.IGNORECASE)
        if age_match:
            patient_data["age"] = int(age_match.group(1))
    
    # Extract sex
    if re.search(r'\b(?:male|man)\b', text, re.IGNORECASE):
        patient_data["sex"] = "male"
    elif re.search(r'\b(?:female|woman)\b', text, re.IGNORECASE):
        patient_data["sex"] = "female"
    
    # Extract HF stage
    stage_match = re.search(r'stage\s+([A-D])', text, re.IGNORECASE)
    if stage_match:
        patient_data["hf_stage"] = stage_match.group(1).upper()
    
    # Extract HF type
    if re.search(r'\bHFrEF\b', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFrEF"
    elif re.search(r'\bHFpEF\b', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFpEF"
    elif re.search(r'\bHFmrEF\b', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFmrEF"
    elif re.search(r'heart failure with reduced ejection fraction', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFrEF"
    elif re.search(r'heart failure with preserved ejection fraction', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFpEF"
    elif re.search(r'reduced ejection fraction', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFrEF"
    elif re.search(r'preserved ejection fraction', text, re.IGNORECASE):
        patient_data["hf_type"] = "HFpEF"
    
    # Extract LVEF and determine HF type if not specified
    lvef_match = re.search(r'LVEF\s*(?:of|:|is|=)?\s*(\d+)(?:\s*%)?', text, re.IGNORECASE)
    if lvef_match:
        lvef = int(lvef_match.group(1))
        patient_data["lvef"] = lvef
        
        if not patient_data["hf_type"]:
            if lvef <= 40:
                patient_data["hf_type"] = "HFrEF"
            elif lvef >= 50:
                patient_data["hf_type"] = "HFpEF"
            else:
                patient_data["hf_type"] = "HFmrEF"
    
    # Extract NYHA class
    nyha_match = re.search(r'NYHA\s+(?:class)?\s*([I]{1,4}|[1-4])', text, re.IGNORECASE)
    if nyha_match:
        nyha = nyha_match.group(1)
        if nyha in ['I', '1']:
            patient_data["nyha_class"] = 1
        elif nyha in ['II', '2']:
            patient_data["nyha_class"] = 2
        elif nyha in ['III', '3']:
            patient_data["nyha_class"] = 3
        elif nyha in ['IV', '4']:
            patient_data["nyha_class"] = 4
    
    # Extract medications
    clean_text = text.replace("Currently on", "").replace("and", ",")
    medication_pattern = r'([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(?:mg|mcg)(?:\s+(?:daily|BID|TID|QID|once daily|twice daily))?'
    medication_matches = re.finditer(medication_pattern, clean_text, re.IGNORECASE)
    
    for match in medication_matches:
        med_name = match.group(1).strip()
        med_dose = match.group(2)
        
        # Skip lab values
        if med_name.lower() in ['k', 'k+', 'potassium', 'na', 'na+', 'sodium', 'cr', 'creatinine']:
            continue
            
        med_name = med_name.strip().strip(',')
        patient_data["medications"].append({
            "name": med_name,
            "dose": float(med_dose),
            "frequency": match.group(0).split(med_dose)[1].strip() if len(match.group(0).split(med_dose)) > 1 else None
        })
    
    # Extract lab values
    k_match = re.search(r'K\+?\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*(?:mEq\/L|meq\/l)?', text, re.IGNORECASE)
    if k_match:
        patient_data["lab_values"]["potassium"] = float(k_match.group(1))
    
    egfr_match = re.search(r'(?:eGFR|GFR)\s*(?:of|:)?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    if egfr_match:
        patient_data["lab_values"]["egfr"] = float(egfr_match.group(1))
    
    # Extract comorbidities
    if re.search(r'no\s+history\s+of\s+angioedema', text, re.IGNORECASE):
        patient_data["angioedema_history"] = False
    elif re.search(r'history\s+of\s+angioedema', text, re.IGNORECASE):
        patient_data["angioedema_history"] = True
        patient_data["comorbidities"].append("History of angioedema")
    
    if re.search(r'\b(?:diabetes|T2DM|type\s*2\s*diabetes)\b', text, re.IGNORECASE):
        patient_data["comorbidities"].append("Diabetes")
    
    if re.search(r'\b(?:atrial\s*fibrillation|AFib|AF)\b', text, re.IGNORECASE):
        patient_data["comorbidities"].append("Atrial Fibrillation")
    
    return patient_data
