"""
Guideline Processor Module

This module handles the processing and structuring of the heart failure guidelines.
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

def preprocess_guidelines(guideline_file: str = "Heart Failure-CPG-heidenreich-et-al-2022-Chapter-7.docx") -> None:
    """
    Preprocess the guidelines document and save structured data to a JSON file.
    
    This function would ideally use a docx parser to extract content from the Word document,
    but for this implementation, we'll create a structured representation manually.
    
    Args:
        guideline_file: Path to the guidelines document file
    """
    # In a production environment, this would parse the actual document
    # For now, we'll create a structured representation based on the provided content
    
    # Define the main sections for Stage C HF from Chapter 7
    guidelines = {
        "metadata": {
            "title": "2022 AHA/ACC/HFSA Heart Failure Guidelines",
            "chapter": "Chapter 7: Stage C HF",
            "version": "1.0"
        },
        "sections": [
            {
                "id": "7.1",
                "title": "Nonpharmacological Interventions",
                "subsections": [
                    {
                        "id": "7.1.1",
                        "title": "Self-Care Support in HF",
                        "recommendations": [
                            {
                                "id": "7.1.1-1",
                                "cor": "1",
                                "loe": "A",
                                "text": "Patients with HF should receive care from multidisciplinary teams to facilitate the implementation of GDMT, address potential barriers to self-care, reduce the risk of subsequent rehospitalization for HF, and improve survival."
                            },
                            {
                                "id": "7.1.1-2",
                                "cor": "1",
                                "loe": "B-R",
                                "text": "Patients with HF should receive specific education and support to facilitate HF self-care in a multidisciplinary manner."
                            },
                            {
                                "id": "7.1.1-3",
                                "cor": "2a",
                                "loe": "B-NR",
                                "text": "In patients with HF, vaccinating against respiratory illnesses is reasonable to reduce mortality."
                            },
                            {
                                "id": "7.1.1-4",
                                "cor": "2a",
                                "loe": "B-NR",
                                "text": "In adults with HF, screening for depression, social isolation, frailty, and low health literacy as risk factors for poor self-care is reasonable to improve management."
                            }
                        ]
                    },
                    {
                        "id": "7.1.2",
                        "title": "Dietary Sodium Restriction",
                        "recommendations": [
                            {
                                "id": "7.1.2-1",
                                "cor": "2a",
                                "loe": "C-LD",
                                "text": "For patients with stage C HF, avoiding excessive sodium intake is reasonable to reduce congestive symptoms."
                            }
                        ]
                    }
                ]
            },
            {
                "id": "7.2",
                "title": "Diuretics and Decongestion Strategies in Patients With HF",
                "recommendations": [
                    {
                        "id": "7.2-1",
                        "cor": "1",
                        "loe": "B-NR",
                        "text": "In patients with HF who have fluid retention, diuretics are recommended to relieve congestion, improve symptoms, and prevent worsening."
                    },
                    {
                        "id": "7.2-2",
                        "cor": "1",
                        "loe": "B-NR",
                        "text": "For patients with HF and congestive symptoms, addition of a thiazide (eg, metolazone) to treatment with a loop diuretic should be reserved for patients who do not respond to moderate or high-dose loop diuretics to minimize electrolyte abnormalities."
                    }
                ]
            },
            {
                "id": "7.3",
                "title": "Pharmacological Treatment for HFrEF",
                "subsections": [
                    {
                        "id": "7.3.1",
                        "title": "Renin-Angiotensin System Inhibition With ACEi or ARB or ARNI",
                        "recommendations": [
                            {
                                "id": "7.3.1-1",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with HFrEF, use of an ACEi is recommended to reduce morbidity and mortality."
                            },
                            {
                                "id": "7.3.1-2",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with HFrEF and NYHA class II to III symptoms, the use of an ARNI in place of an ACEi is recommended to reduce morbidity and mortality."
                            },
                            {
                                "id": "7.3.1-3",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with HFrEF who are unable to tolerate an ACEi or ARNI, use of an ARB is recommended to reduce morbidity and mortality."
                            },
                            {
                                "id": "7.3.1-4",
                                "cor": "1",
                                "loe": "B-R",
                                "text": "In patients with chronic symptomatic HFrEF NYHA class II or III who tolerate an ACEi or ARB, replacement by an ARNI is recommended to further reduce morbidity and mortality."
                            },
                            {
                                "id": "7.3.1-5",
                                "cor": "1",
                                "loe": "B-R",
                                "text": "For patients with HFrEF and NYHA class II to III symptoms who are intolerant to an ACEi because of cough or angioedema, and who are intolerant to ARNI because of angioedema, the use of a combination of a hydralazine and an oral nitrate is recommended to improve symptoms and reduce morbidity and mortality."
                            }
                        ],
                        "criteria": {
                            "ACEi_Eligible": "No contraindications (intolerance, hypotension, hyperkalemia, renal dysfunction, angioedema)",
                            "ARNi_Eligible": "NYHA II-III, LVEF ≤40%, No history of angioedema, Systolic BP ≥100 mmHg, Tolerance to ACEi/ARB, eGFR ≥30 mL/min/1.73m²",
                            "ARB_Eligible": "Intolerance to ACEi/ARNI"
                        },
                        "contraindications": {
                            "ACEi": ["History of angioedema", "Pregnancy", "Bilateral renal artery stenosis"],
                            "ARNi": ["Active angioedema", "Concomitant ACEi use (must wait 36 hours after last ACEi dose)", "eGFR <30 mL/min/1.73m²", "Severe hepatic impairment"]
                        }
                    },
                    {
                        "id": "7.3.2",
                        "title": "Beta Blockers",
                        "recommendations": [
                            {
                                "id": "7.3.2-1",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with HFrEF, use of 1 of the 3 beta blockers proven to reduce mortality (eg, bisoprolol, carvedilol, metoprolol succinate) is recommended to reduce mortality and hospitalizations."
                            }
                        ],
                        "criteria": {
                            "Beta_Blocker_Eligible": "Stable HFrEF patients without hypotension, bradycardia, or advanced heart block"
                        },
                        "medications": {
                            "Carvedilol": {"target_dose": "25-50 mg BID"},
                            "Metoprolol succinate": {"target_dose": "200 mg daily"},
                            "Bisoprolol": {"target_dose": "10 mg daily"}
                        }
                    },
                    {
                        "id": "7.3.3",
                        "title": "Mineralocorticoid Receptor Antagonists",
                        "recommendations": [
                            {
                                "id": "7.3.3-1",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with HFrEF and NYHA class II to IV symptoms, an MRA is recommended to reduce morbidity and mortality, if eGFR is >30 mL/min/1.73 m2 and serum potassium is <5.0 mEq/L. Careful monitoring of potassium, renal function, and diuretic dosing should be performed at initiation and closely followed thereafter to minimize risk of hyperkalemia and renal insufficiency."
                            }
                        ],
                        "criteria": {
                            "MRA_Eligible": "NYHA II-IV, LVEF ≤35%, eGFR >30 mL/min/1.73m², K+ <5.0 mEq/L"
                        },
                        "medications": {
                            "Spironolactone": {"target_dose": "25-50 mg daily"},
                            "Eplerenone": {"target_dose": "50 mg daily"}
                        }
                    },
                    {
                        "id": "7.3.4",
                        "title": "SGLT2i",
                        "recommendations": [
                            {
                                "id": "7.3.4-1",
                                "cor": "1",
                                "loe": "A",
                                "text": "For patients with symptomatic chronic HFrEF, an SGLT2i is recommended to reduce hospitalization for HF and cardiovascular mortality, irrespective of the presence of type 2 diabetes."
                            }
                        ],
                        "criteria": {
                            "SGLT2i_Eligible": "Symptomatic HFrEF, LVEF ≤40%, eGFR ≥20 mL/min/1.73m²"
                        },
                        "medications": {
                            "Dapagliflozin": {"target_dose": "10 mg daily", "min_eGFR": 25},
                            "Empagliflozin": {"target_dose": "10 mg daily", "min_eGFR": 20}
                        }
                    }
                ]
            },
            {
                "id": "7.3.8",
                "title": "Guideline-Directed Medical Therapy and Initiation and Titration",
                "content": "GDMT should be titrated to target doses or maximally tolerated doses. Table 14 contains target doses for key medications.",
                "tables": {
                    "table14": {
                        "title": "Doses of GDMT for HFrEF",
                        "medications": {
                            "ACEi": {
                                "Captopril": {"starting_dose": "6.25 mg TID", "target_dose": "50 mg TID"},
                                "Enalapril": {"starting_dose": "2.5 mg BID", "target_dose": "10-20 mg BID"},
                                "Lisinopril": {"starting_dose": "2.5-5 mg daily", "target_dose": "20-40 mg daily"},
                                "Ramipril": {"starting_dose": "1.25-2.5 mg daily", "target_dose": "10 mg daily"}
                            },
                            "ARNi": {
                                "Sacubitril/Valsartan": {"starting_dose": "49/51 mg BID", "target_dose": "97/103 mg BID"}
                            },
                            "ARB": {
                                "Candesartan": {"starting_dose": "4-8 mg daily", "target_dose": "32 mg daily"},
                                "Losartan": {"starting_dose": "25-50 mg daily", "target_dose": "150 mg daily"},
                                "Valsartan": {"starting_dose": "40 mg BID", "target_dose": "160 mg BID"}
                            },
                            "Beta Blockers": {
                                "Bisoprolol": {"starting_dose": "1.25 mg daily", "target_dose": "10 mg daily"},
                                "Carvedilol": {"starting_dose": "3.125 mg BID", "target_dose": "25-50 mg BID"},
                                "Metoprolol succinate": {"starting_dose": "12.5-25 mg daily", "target_dose": "200 mg daily"}
                            },
                            "MRA": {
                                "Spironolactone": {"starting_dose": "12.5-25 mg daily", "target_dose": "25-50 mg daily"},
                                "Eplerenone": {"starting_dose": "25 mg daily", "target_dose": "50 mg daily"}
                            },
                            "SGLT2i": {
                                "Dapagliflozin": {"starting_dose": "10 mg daily", "target_dose": "10 mg daily"},
                                "Empagliflozin": {"starting_dose": "10 mg daily", "target_dose": "10 mg daily"}
                            }
                        }
                    }
                }
            }
        ],
        "special_topics": [
            {
                "id": "HFrEF",
                "title": "Heart Failure with Reduced Ejection Fraction",
                "definition": "LVEF ≤40%",
                "key_treatments": ["ACEi/ARNi", "Beta-Blocker", "MRA", "SGLT2i"]
            },
            {
                "id": "HFpEF",
                "title": "Heart Failure with Preserved Ejection Fraction",
                "definition": "LVEF ≥50%",
                "key_treatments": ["SGLT2i", "MRA", "Diuretics"]
            },
            {
                "id": "HFmrEF",
                "title": "Heart Failure with Mildly Reduced Ejection Fraction",
                "definition": "LVEF 41-49%",
                "key_treatments": ["ACEi/ARNi", "Beta-Blocker", "MRA", "SGLT2i"]
            }
        ]
    }
    
    # Save the structured guidelines to a JSON file
    with open("guidelines.json", "w") as f:
        json.dump(guidelines, f, indent=2)
    
    logging.info("Guidelines processed and saved to guidelines.json")

def load_guidelines(json_file: str = "guidelines.json") -> Dict[str, Any]:
    """
    Load the preprocessed guidelines from the JSON file.
    
    Args:
        json_file: Path to the JSON file containing the preprocessed guidelines
        
    Returns:
        Dictionary containing the structured guidelines
    """
    try:
        with open(json_file, "r") as f:
            guidelines = json.load(f)
        return guidelines
    except FileNotFoundError:
        logging.warning(f"Guidelines file {json_file} not found. Creating it now.")
        preprocess_guidelines()
        with open(json_file, "r") as f:
            guidelines = json.load(f)
        return guidelines
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {json_file}. The file may be corrupted.")
        raise

def find_relevant_sections(patient_data: Dict[str, Any], guidelines: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find relevant guideline sections based on patient data.
    
    Args:
        patient_data: Dictionary containing extracted patient data
        guidelines: Dictionary containing the structured guidelines
        
    Returns:
        List of relevant guideline sections
    """
    relevant_sections = []
    
    # Example logic to find relevant sections
    if "hf_type" in patient_data:
        hf_type = patient_data["hf_type"].lower()
        
        # Find sections relevant to HFrEF
        if "hfref" in hf_type:
            for section in guidelines["sections"]:
                if section["id"] == "7.3":  # Pharmacological Treatment for HFrEF
                    relevant_sections.append(section)
                    
                    # Check if patient is on ACEi and eligible for ARNi
                    if "medications" in patient_data:
                        meds = [med.lower() for med in patient_data["medications"]]
                        acei_meds = ["lisinopril", "enalapril", "captopril", "ramipril"]
                        
                        if any(acei in meds for acei in acei_meds) and not patient_data.get("angioedema_history", False):
                            for subsection in section.get("subsections", []):
                                if subsection["id"] == "7.3.1":  # ACEi/ARB/ARNI section
                                    relevant_sections.append(subsection)
                    
        # Add SGLT2i recommendations for all HF types
        for section in guidelines["sections"]:
            if section["id"] == "7.3":
                for subsection in section.get("subsections", []):
                    if subsection["id"] == "7.3.4":  # SGLT2i section
                        relevant_sections.append(subsection)
    
    # Add other logic as needed for other HF types and conditions
    
    return relevant_sections
