# 🏥 Heart Failure Guidelines Recommendation System

A rule-based clinical decision support system that provides evidence-based heart failure management recommendations based on the 2022 AHA/ACC/HFSA Heart Failure Guidelines.

## ✨ Features

- **Rule-based recommendations** - No external AI dependencies required
- **Multiple input methods** - Web interface, command line, or Python API
- **Natural language processing** - Extracts patient data from clinical text
- **AWS Comprehend Medical integration** - Optional enhanced medical text extraction
- **Comprehensive guidelines** - Based on 2022 AHA/ACC/HFSA Heart Failure Guidelines
- **Easy deployment** - Minimal setup, works locally

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)
```bash
# Copy template and add AWS credentials (optional for enhanced extraction)
cp .env.template .env
# Edit .env with your AWS credentials (optional)
```

### 3. Run the System

**Web Interface (Recommended):**
```bash
streamlit run gui.py
```
Opens at http://localhost:8501

**Command Line:**
```bash
python main.py
```

## 📝 Example Usage

### Input Examples:
```
"65-year-old male with heart failure, LVEF 35%"
"Heart failure patient on carvedilol and lisinopril"  
"HFrEF, age 72, female, EF 25%, NYHA Class III"
```

### Sample Output:
```
## 🏥 Heart Failure Management Recommendations
*Based on 2022 AHA/ACC/HFSA Heart Failure Guidelines*

### 📋 Patient Summary
**Demographics:** 65-year-old male
**Heart Failure:** Type: HFrEF, LVEF: 35%

### 💊 Current Medications Analysis
No current medications reported.

### ✅ Medication Recommendations
1. **ACE inhibitor** - Start lisinopril 5mg daily, titrate to maximum tolerated dose
2. **Beta-blocker** - Start metoprolol succinate 25mg daily or carvedilol 3.125mg BID
3. **MRA therapy** - Consider spironolactone 25mg daily (monitor K+ and creatinine)
4. **SGLT2 inhibitor** - Consider dapagliflozin 10mg daily for additional benefit

### 🔍 Monitoring & Follow-up
**Laboratory Monitoring:**
• Complete metabolic panel in 1-2 weeks after medication changes
• BNP or NT-proBNP if diagnosis unclear

**Clinical Monitoring:**
• Daily weight monitoring
• Blood pressure and heart rate
• Follow-up in 1-2 weeks after medication changes
```

## 🏗️ Architecture

- **Text Extraction**: Enhanced regex patterns + optional AWS Comprehend Medical
- **Recommendation Engine**: Rule-based clinical logic following 2022 guidelines
- **Multiple Interfaces**: Streamlit web app, command line, Python API
- **Fallback System**: Works with or without AWS integration

## 📁 Core Files

- `gui.py` - Streamlit web interface
- `main.py` - Command line interface  
- `backend_connector.py` - Main processing logic
- `rule_based_recommendations.py` - Clinical recommendation engine
- `enhanced_text_extractor.py` - Medical text extraction
- `aws_comprehend_medical.py` - AWS integration (optional)
- `guidelines.json` - Clinical guidelines database

## 🔧 System Requirements

- Python 3.8+
- Internet connection (optional, for AWS features)
- Windows/Mac/Linux

## 💡 Usage Scenarios

1. **Clinical Decision Support** - Input patient data, get guideline recommendations
2. **Medical Education** - Learn evidence-based heart failure management
3. **EHR Integration** - API integration with existing systems
4. **Research** - Standardized recommendation generation

## 🎯 Input Flexibility

The system accepts various input formats:
- Natural language clinical notes
- Structured medical data
- Mixed formats with abbreviations
- Discharge summaries and progress notes

## 📊 What the System Provides

- **Patient Summary** - Demographics and heart failure details
- **Medication Analysis** - Current therapy assessment
- **Evidence-based Recommendations** - Specific medication suggestions with dosing
- **Monitoring Guidelines** - Laboratory and clinical follow-up requirements
- **Lifestyle Recommendations** - Diet, exercise, and additional considerations

## 🚀 API Usage

```python
from backend_connector import process_user_input

# Process clinical text
result = process_user_input("72-year-old female with HFrEF, LVEF 25%")
print(result['recommendations'])
```

## ⚠️ Important Notes

- **Clinical Judgment Required** - Recommendations are guidance only
- **Individual Patient Factors** - Consider patient-specific circumstances
- **Current Guidelines** - Based on 2022 AHA/ACC/HFSA guidelines
- **No Data Storage** - All processing done in memory for privacy

## 🎓 Educational Use

Perfect for:
- Medical students learning heart failure management
- Residents practicing guideline application
- Healthcare providers needing quick reference
- Clinical decision support tool development

---

**Disclaimer**: This system provides clinical guidance based on established guidelines but does not replace professional medical judgment. Always consider individual patient factors and current clinical context.
