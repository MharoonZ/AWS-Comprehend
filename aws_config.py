"""
Configuration for AWS Comprehend Medical Integration

This module handles configuration and setup for AWS Comprehend Medical services.
"""

import os
import logging
from typing import Dict, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use environment variables only

logger = logging.getLogger(__name__)

class AWSConfig:
    """Configuration for AWS services."""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.session_token = os.getenv('AWS_SESSION_TOKEN')  # For temporary credentials
        
    def is_configured(self) -> bool:
        """Check if AWS credentials are configured."""
        # Check if credentials are available via environment variables or AWS CLI/SDK
        return bool(self.access_key_id and self.secret_access_key) or self._check_aws_cli_config()
    
    def _check_aws_cli_config(self) -> bool:
        """Check if AWS CLI is configured."""
        try:
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
        except:
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get AWS configuration dictionary."""
        config = {'region_name': self.region}
        
        if self.access_key_id and self.secret_access_key:
            config.update({
                'aws_access_key_id': self.access_key_id,
                'aws_secret_access_key': self.secret_access_key
            })
            
        if self.session_token:
            config['aws_session_token'] = self.session_token
            
        return config

def check_aws_comprehend_availability() -> tuple[bool, str]:
    """
    Check if AWS Comprehend Medical is available and properly configured.
    
    Returns:
        Tuple of (is_available, status_message)
    """
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        config = AWSConfig()
        
        if not config.is_configured():
            return False, "AWS credentials not configured. Please set up AWS credentials."
        
        # Test connection
        client = boto3.client('comprehendmedical', **config.get_config())
        
        # Simple test call to verify service access
        test_text = "Patient is a 65-year-old male with diabetes."
        try:
            response = client.detect_entities_v2(Text=test_text)
            return True, "AWS Comprehend Medical is available and configured correctly."
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                return False, "Access denied to AWS Comprehend Medical. Check IAM permissions."
            elif error_code == 'ServiceUnavailableException':
                return False, "AWS Comprehend Medical service is temporarily unavailable."
            else:
                return False, f"AWS Comprehend Medical error: {error_code}"
                
    except ImportError:
        return False, "boto3 not installed. Run: pip install boto3"
    except NoCredentialsError:
        return False, "AWS credentials not found. Please configure AWS credentials."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def get_required_iam_permissions() -> Dict[str, Any]:
    """
    Get the required IAM permissions for AWS Comprehend Medical.
    
    Returns:
        Dictionary containing IAM policy information
    """
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "comprehendmedical:DetectEntitiesV2",
                    "comprehendmedical:DetectPHI",
                    "comprehendmedical:InferICD10CM",
                    "comprehendmedical:InferRxNorm",
                    "comprehendmedical:InferSNOMEDCT"
                ],
                "Resource": "*"
            }
        ]
    }

def setup_aws_credentials_help() -> str:
    """
    Provide help text for setting up AWS credentials.
    
    Returns:
        Help text string
    """
    return """
    AWS Credentials Setup:
    
    Option 1: Environment Variables
    Set the following environment variables:
    - AWS_ACCESS_KEY_ID=your_access_key
    - AWS_SECRET_ACCESS_KEY=your_secret_key
    - AWS_REGION=us-east-1 (or your preferred region)
    
    Option 2: AWS CLI Configuration
    Run: aws configure
    
    Option 3: Create .env file in your project directory:
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    AWS_REGION=us-east-1
    
    Option 4: Use AWS IAM Roles (for EC2 instances)
    
    Required IAM Permissions:
    Your AWS user/role needs permissions for:
    - comprehendmedical:DetectEntitiesV2
    - comprehendmedical:DetectPHI
    - comprehendmedical:InferICD10CM
    - comprehendmedical:InferRxNorm
    - comprehendmedical:InferSNOMEDCT
    """
