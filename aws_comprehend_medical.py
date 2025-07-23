"""
AWS Comprehend Medical Integration Module

Enhances text extraction capabilities using AWS Comprehend Medical API
for more accurate medical entity recognition and relationship extraction.
"""

import boto3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use environment variables only

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehendMedicalProcessor:
    """Process medical text using AWS Comprehend Medical."""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize AWS Comprehend Medical client.
        
        Args:
            region_name: AWS region for Comprehend Medical service
        """
        try:
            self.client = boto3.client('comprehendmedical', region_name=region_name)
            logger.info(f"AWS Comprehend Medical client initialized for region: {region_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS Comprehend Medical client: {e}")
            raise
    
    def extract_medical_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract medical entities from text using AWS Comprehend Medical.
        
        Args:
            text: Medical text to analyze
            
        Returns:
            Dictionary containing extracted medical entities
        """
        try:
            # Detect entities
            response = self.client.detect_entities_v2(Text=text)
            
            # Process entities into structured format
            structured_data = self._process_entities(response['Entities'])
            
            logger.info(f"Successfully extracted {len(response['Entities'])} entities")
            return structured_data
            
        except ClientError as e:
            logger.error(f"AWS Comprehend Medical API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error extracting medical entities: {e}")
            raise
    
    def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect Protected Health Information (PHI) in medical text.
        
        Args:
            text: Medical text to analyze
            
        Returns:
            List of PHI entities found
        """
        try:
            response = self.client.detect_phi(Text=text)
            return response['Entities']
        except ClientError as e:
            logger.error(f"AWS Comprehend Medical PHI detection error: {e}")
            raise
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract relationships between medical entities.
        
        Args:
            text: Medical text to analyze
            
        Returns:
            List of relationship mappings
        """
        try:
            # First get entities
            entities_response = self.client.detect_entities_v2(Text=text)
            
            # Extract relationships
            relationships = []
            for entity in entities_response['Entities']:
                if 'Attributes' in entity:
                    for attribute in entity['Attributes']:
                        relationships.append({
                            'entity': entity,
                            'attribute': attribute,
                            'relationship_type': attribute['Type']
                        })
            
            return relationships
        except ClientError as e:
            logger.error(f"Error extracting relationships: {e}")
            raise
    
    def _process_entities(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        Process raw entities into structured patient data format.
        
        Args:
            entities: Raw entities from Comprehend Medical
            
        Returns:
            Structured patient data compatible with existing system
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
            "medical_entities": {}  # New field for comprehensive entity data
        }
        
        # Group entities by category
        entity_groups = {
            'MEDICATION': [],
            'MEDICAL_CONDITION': [],
            'TEST_TREATMENT_PROCEDURE': [],
            'ANATOMY': [],
            'TIME_EXPRESSION': [],
            'PROTECTED_HEALTH_INFORMATION': []
        }
        
        for entity in entities:
            category = entity['Category']
            if category in entity_groups:
                entity_groups[category].append(entity)
        
        # Process medications
        for med_entity in entity_groups['MEDICATION']:
            medication = {
                'name': med_entity['Text'],
                'confidence': med_entity['Score'],
                'type': med_entity['Type'],
                'attributes': []
            }
            
            # Extract dosage, frequency, route from attributes
            if 'Attributes' in med_entity:
                for attr in med_entity['Attributes']:
                    medication['attributes'].append({
                        'type': attr['Type'],
                        'text': attr['Text'],
                        'confidence': attr['Score']
                    })
                    
                    # Map to existing structure
                    if attr['Type'] == 'DOSAGE':
                        try:
                            # Extract numeric dose
                            import re
                            dose_match = re.search(r'(\d+(?:\.\d+)?)', attr['Text'])
                            if dose_match:
                                medication['dose'] = float(dose_match.group(1))
                        except:
                            pass
                    elif attr['Type'] == 'FREQUENCY':
                        medication['frequency'] = attr['Text']
            
            patient_data['medications'].append(medication)
        
        # Process medical conditions
        for condition in entity_groups['MEDICAL_CONDITION']:
            condition_text = condition['Text'].lower()
            
            # Check for heart failure specific conditions
            if 'heart failure' in condition_text or 'hf' in condition_text:
                if 'hfref' in condition_text or 'reduced ejection' in condition_text:
                    patient_data['hf_type'] = 'HFrEF'
                elif 'hfpef' in condition_text or 'preserved ejection' in condition_text:
                    patient_data['hf_type'] = 'HFpEF'
                elif 'hfmref' in condition_text or 'mid-range' in condition_text:
                    patient_data['hf_type'] = 'HFmrEF'
            
            patient_data['comorbidities'].append({
                'condition': condition['Text'],
                'type': condition['Type'],
                'confidence': condition['Score']
            })
        
        # Process test results for lab values
        for test in entity_groups['TEST_TREATMENT_PROCEDURE']:
            test_text = test['Text'].lower()
            
            # Look for specific lab values
            if 'lvef' in test_text or 'ejection fraction' in test_text:
                # Try to extract LVEF value from attributes
                if 'Attributes' in test:
                    for attr in test['Attributes']:
                        if attr['Type'] == 'TEST_VALUE':
                            try:
                                import re
                                lvef_match = re.search(r'(\d+)', attr['Text'])
                                if lvef_match:
                                    patient_data['lvef'] = int(lvef_match.group(1))
                            except:
                                pass
            
            # Add to lab values
            patient_data['lab_values'][test['Text']] = {
                'type': test['Type'],
                'confidence': test['Score']
            }
        
        # Store all entity data for advanced processing
        patient_data['medical_entities'] = entity_groups
        
        return patient_data
    
    def enhanced_text_extraction(self, text: str) -> Dict[str, Any]:
        """
        Enhanced text extraction combining AWS Comprehend Medical with existing logic.
        
        Args:
            text: Clinical text to process
            
        Returns:
            Enhanced patient data structure
        """
        try:
            # Get AWS Comprehend Medical analysis
            aws_data = self.extract_medical_entities(text)
            
            # Import and run existing text extractor as fallback
            from enhanced_text_extractor import extract_patient_data_regex
            fallback_data = extract_patient_data_regex(text)
            
            # Merge results, prioritizing AWS Comprehend Medical when available
            merged_data = self._merge_extraction_results(aws_data, fallback_data)
            merged_data['extraction_method'] = 'aws_comprehend_medical'
            
            return merged_data
            
        except Exception as e:
            logger.warning(f"AWS Comprehend Medical failed, falling back to regex extraction: {e}")
            # Fallback to existing extraction
            from enhanced_text_extractor import extract_patient_data_regex
            fallback_data = extract_patient_data_regex(text)
            fallback_data['extraction_method'] = 'regex_fallback'
            return fallback_data
    
    def _merge_extraction_results(self, aws_data: Dict, fallback_data: Dict) -> Dict[str, Any]:
        """
        Merge AWS Comprehend Medical results with fallback regex extraction.
        
        Args:
            aws_data: Data from AWS Comprehend Medical
            fallback_data: Data from regex-based extraction
            
        Returns:
            Merged patient data
        """
        merged = fallback_data.copy()
        
        # Prefer AWS data when available and confident
        for key in ['medications', 'comorbidities', 'lab_values']:
            if aws_data.get(key) and len(aws_data[key]) > 0:
                merged[key] = aws_data[key]
        
        # For specific values, use AWS if available, otherwise fallback
        for key in ['age', 'sex', 'hf_stage', 'hf_type', 'lvef', 'nyha_class']:
            if aws_data.get(key) is not None:
                merged[key] = aws_data[key]
        
        # Add AWS-specific data
        if 'medical_entities' in aws_data:
            merged['medical_entities'] = aws_data['medical_entities']
        
        return merged

# Utility functions for easy integration

def create_comprehend_processor(region_name: str = 'us-east-1') -> ComprehendMedicalProcessor:
    """Create and return a ComprehendMedicalProcessor instance."""
    return ComprehendMedicalProcessor(region_name)

def extract_with_comprehend(text: str, processor: ComprehendMedicalProcessor = None) -> Dict[str, Any]:
    """
    Extract patient data using AWS Comprehend Medical.
    
    Args:
        text: Clinical text to process
        processor: Optional existing processor instance
        
    Returns:
        Enhanced patient data
    """
    if processor is None:
        processor = create_comprehend_processor()
    
    return processor.enhanced_text_extraction(text)
