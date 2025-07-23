"""
Enhanced AWS Comprehend Medical Integration

Provides comprehensive medical entity extraction using multiple AWS APIs:
- detect_entities_v2: Basic entity detection
- infer_icd10_cm: ICD-10-CM diagnostic codes
- infer_rx_norm: RXNorm medication codes  
- infer_snomed_ct: SNOMED CT clinical concepts
"""

import boto3
import logging
from typing import Dict, Any, List, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class EnhancedAWSComprehendMedical:
    """Enhanced AWS Comprehend Medical client for comprehensive medical coding."""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the enhanced AWS Comprehend Medical client."""
        try:
            self.client = boto3.client('comprehendmedical', region_name=region_name)
            self.region = region_name
            logger.info(f"Enhanced AWS Comprehend Medical client initialized for region: {region_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize AWS client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AWS Comprehend Medical is available."""
        if not self.client:
            return False
        
        try:
            # Test with a simple call
            self.client.detect_entities_v2(Text="test")
            return True
        except (ClientError, NoCredentialsError):
            return False
        except Exception:
            return True  # Other errors might be temporary
    
    def extract_comprehensive_medical_data(self, text: str) -> Dict[str, Any]:
        """
        Extract comprehensive medical data using multiple AWS APIs.
        
        Args:
            text: Input clinical text
            
        Returns:
            Dictionary containing results from all medical APIs
        """
        if not self.client:
            logger.warning("AWS client not available")
            return self._get_empty_results()
        
        results = {
            'basic_entities': {},
            'icd10_cm': {},
            'rx_norm': {},
            'snomed_ct': {},
            'success': False,
            'errors': []
        }
        
        try:
            # 1. Basic entity detection
            logger.info("Calling detect_entities_v2...")
            basic_response = self.client.detect_entities_v2(Text=text)
            results['basic_entities'] = self._process_basic_entities(basic_response)
            
            # 2. ICD-10-CM inference
            logger.info("Calling infer_icd10_cm...")
            try:
                icd_response = self.client.infer_icd10_cm(Text=text)
                results['icd10_cm'] = self._process_icd10_cm(icd_response)
            except Exception as e:
                logger.warning(f"ICD-10-CM inference failed: {e}")
                results['errors'].append(f"ICD-10-CM: {str(e)}")
            
            # 3. RXNorm inference
            logger.info("Calling infer_rx_norm...")
            try:
                rx_response = self.client.infer_rx_norm(Text=text)
                results['rx_norm'] = self._process_rx_norm(rx_response)
            except Exception as e:
                logger.warning(f"RXNorm inference failed: {e}")
                results['errors'].append(f"RXNorm: {str(e)}")
            
            # 4. SNOMED CT inference
            logger.info("Calling infer_snomed_ct...")
            try:
                snomed_response = self.client.infer_snomed_ct(Text=text)
                results['snomed_ct'] = self._process_snomed_ct(snomed_response)
            except Exception as e:
                logger.warning(f"SNOMED CT inference failed: {e}")
                results['errors'].append(f"SNOMED CT: {str(e)}")
            
            results['success'] = True
            logger.info("Comprehensive medical extraction completed successfully")
            
        except Exception as e:
            logger.error(f"Error in comprehensive medical extraction: {e}")
            results['errors'].append(f"General error: {str(e)}")
        
        return results
    
    def _process_basic_entities(self, response: Dict) -> Dict[str, Any]:
        """Process basic entity detection response."""
        processed = {
            'medications': [],
            'medical_conditions': [],
            'anatomy': [],
            'test_procedures': [],
            'protected_health_info': []
        }
        
        entities = response.get('Entities', [])
        
        for entity in entities:
            entity_info = {
                'text': entity.get('Text', ''),
                'category': entity.get('Category', ''),
                'type': entity.get('Type', ''),
                'confidence': entity.get('Score', 0.0),
                'begin_offset': entity.get('BeginOffset', 0),
                'end_offset': entity.get('EndOffset', 0),
                'attributes': entity.get('Attributes', [])
            }
            
            category = entity.get('Category', '').lower()
            if category == 'medication':
                processed['medications'].append(entity_info)
            elif category == 'medical_condition':
                processed['medical_conditions'].append(entity_info)
            elif category == 'anatomy':
                processed['anatomy'].append(entity_info)
            elif category in ['test_treatment_procedure', 'procedure']:
                processed['test_procedures'].append(entity_info)
            elif category == 'protected_health_information':
                processed['protected_health_info'].append(entity_info)
        
        return processed
    
    def _process_icd10_cm(self, response: Dict) -> Dict[str, Any]:
        """Process ICD-10-CM inference response."""
        processed = {
            'entities': [],
            'total_concepts': 0
        }
        
        entities = response.get('Entities', [])
        
        for entity in entities:
            entity_info = {
                'text': entity.get('Text', ''),
                'category': entity.get('Category', ''),
                'type': entity.get('Type', ''),
                'confidence': entity.get('Score', 0.0),
                'begin_offset': entity.get('BeginOffset', 0),
                'end_offset': entity.get('EndOffset', 0),
                'icd10_cm_concepts': []
            }
            
            # Process ICD-10-CM concepts
            concepts = entity.get('ICD10CMConcepts', [])
            for concept in concepts:
                concept_info = {
                    'description': concept.get('Description', ''),
                    'code': concept.get('Code', ''),
                    'score': concept.get('Score', 0.0)
                }
                entity_info['icd10_cm_concepts'].append(concept_info)
            
            processed['entities'].append(entity_info)
            processed['total_concepts'] += len(concepts)
        
        return processed
    
    def _process_rx_norm(self, response: Dict) -> Dict[str, Any]:
        """Process RXNorm inference response."""
        processed = {
            'entities': [],
            'total_concepts': 0
        }
        
        entities = response.get('Entities', [])
        
        for entity in entities:
            entity_info = {
                'text': entity.get('Text', ''),
                'category': entity.get('Category', ''),
                'type': entity.get('Type', ''),
                'confidence': entity.get('Score', 0.0),
                'begin_offset': entity.get('BeginOffset', 0),
                'end_offset': entity.get('EndOffset', 0),
                'rx_norm_concepts': []
            }
            
            # Process RXNorm concepts
            concepts = entity.get('RxNormConcepts', [])
            for concept in concepts:
                concept_info = {
                    'description': concept.get('Description', ''),
                    'code': concept.get('Code', ''),
                    'score': concept.get('Score', 0.0)
                }
                entity_info['rx_norm_concepts'].append(concept_info)
            
            processed['entities'].append(entity_info)
            processed['total_concepts'] += len(concepts)
        
        return processed
    
    def _process_snomed_ct(self, response: Dict) -> Dict[str, Any]:
        """Process SNOMED CT inference response."""
        processed = {
            'entities': [],
            'total_concepts': 0
        }
        
        entities = response.get('Entities', [])
        
        for entity in entities:
            entity_info = {
                'text': entity.get('Text', ''),
                'category': entity.get('Category', ''),
                'type': entity.get('Type', ''),
                'confidence': entity.get('Score', 0.0),
                'begin_offset': entity.get('BeginOffset', 0),
                'end_offset': entity.get('EndOffset', 0),
                'snomed_concepts': []
            }
            
            # Process SNOMED CT concepts
            concepts = entity.get('SNOMEDCTConcepts', [])
            for concept in concepts:
                concept_info = {
                    'description': concept.get('Description', ''),
                    'code': concept.get('Code', ''),
                    'score': concept.get('Score', 0.0)
                }
                entity_info['snomed_concepts'].append(concept_info)
            
            processed['entities'].append(entity_info)
            processed['total_concepts'] += len(concepts)
        
        return processed
    
    def _get_empty_results(self) -> Dict[str, Any]:
        """Return empty results structure."""
        return {
            'basic_entities': {
                'medications': [],
                'medical_conditions': [],
                'anatomy': [],
                'test_procedures': [],
                'protected_health_info': []
            },
            'icd10_cm': {'entities': [], 'total_concepts': 0},
            'rx_norm': {'entities': [], 'total_concepts': 0},
            'snomed_ct': {'entities': [], 'total_concepts': 0},
            'success': False,
            'errors': ['AWS client not available']
        }
    
    def get_medication_entities_with_codes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medications with RXNorm codes and confidence scores.
        
        Args:
            text: Input clinical text
            
        Returns:
            List of medication entities with RXNorm codes
        """
        results = self.extract_comprehensive_medical_data(text)
        
        medications = []
        
        # Combine basic entities with RXNorm codes
        basic_meds = results.get('basic_entities', {}).get('medications', [])
        rx_entities = results.get('rx_norm', {}).get('entities', [])
        
        # Create a comprehensive medication list
        for med in basic_meds:
            med_info = {
                'text': med['text'],
                'confidence': med['confidence'],
                'category': med['category'],
                'rx_norm_codes': []
            }
            
            # Find matching RXNorm codes
            for rx_entity in rx_entities:
                if rx_entity['text'].lower() in med['text'].lower():
                    med_info['rx_norm_codes'] = rx_entity['rx_norm_concepts']
                    break
            
            medications.append(med_info)
        
        return medications
    
    def get_condition_entities_with_codes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medical conditions with ICD-10-CM codes and confidence scores.
        
        Args:
            text: Input clinical text
            
        Returns:
            List of condition entities with ICD-10-CM codes
        """
        results = self.extract_comprehensive_medical_data(text)
        
        conditions = []
        
        # Combine basic entities with ICD-10-CM codes
        basic_conditions = results.get('basic_entities', {}).get('medical_conditions', [])
        icd_entities = results.get('icd10_cm', {}).get('entities', [])
        
        # Create a comprehensive conditions list
        for condition in basic_conditions:
            condition_info = {
                'text': condition['text'],
                'confidence': condition['confidence'],
                'category': condition['category'],
                'icd10_cm_codes': []
            }
            
            # Find matching ICD-10-CM codes
            for icd_entity in icd_entities:
                if icd_entity['text'].lower() in condition['text'].lower():
                    condition_info['icd10_cm_codes'] = icd_entity['icd10_cm_concepts']
                    break
            
            conditions.append(condition_info)
        
        return conditions

# Global instance
enhanced_aws_medical = EnhancedAWSComprehendMedical()
