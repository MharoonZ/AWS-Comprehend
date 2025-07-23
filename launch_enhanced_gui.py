#!/usr/bin/env python3
"""
Launch Enhanced GUI with AWS Comprehend Medical-style Interface

This script launches the enhanced GUI that displays medical coding information
similar to AWS Comprehend Medical's interface.
"""

import subprocess
import sys
import os

def main():
    """Launch the enhanced GUI."""
    
    print("🚀 Launching Enhanced Heart Failure Clinical Decision Support System")
    print("=" * 70)
    print()
    print("Features:")
    print("✅ AWS Comprehend Medical-style entity extraction display")
    print("✅ RXNorm medication codes with confidence scores")
    print("✅ ICD-10-CM diagnostic codes with confidence scores") 
    print("✅ SNOMED CT clinical concepts with confidence scores")
    print("✅ Enhanced UI with tabs and medical coding visualization")
    print("✅ Sample patient cases for testing")
    print()
    print("=" * 70)
    
    try:
        # Launch the enhanced GUI
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "enhanced_gui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching GUI: {e}")
        print()
        print("💡 Try running manually:")
        print("   streamlit run enhanced_gui.py")
        
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it:")
        print("   pip install streamlit")
        
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")

if __name__ == "__main__":
    main()
