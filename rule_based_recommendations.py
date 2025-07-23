"""
Rule-based Recommendation Engine

Generates heart failure management recommendations based on extracted patient data
and 2022 AHA/ACC/HFSA guidelines without requiring external AI services.
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class GuidelineRecommendationEngine:
    """Generate evidence-based recommendations using rule-based logic."""
    
    def __init__(self, guidelines: Dict[str, Any]):
        """
        Initialize the recommendation engine with guidelines.
        
        Args:
            guidelines: Loaded heart failure guidelines
        """
        self.guidelines = guidelines
    
    def generate_recommendation(self, patient_data: Dict[str, Any], user_input: str = "") -> str:
        """
        Generate comprehensive heart failure management recommendations.
        
        Args:
            patient_data: Extracted patient information
            user_input: Original user input for context
            
        Returns:
            Formatted recommendation string
        """
        try:
            # Extract key patient characteristics
            age = patient_data.get('age')
            sex = patient_data.get('sex', '')
            lvef = patient_data.get('lvef')
            hf_type = patient_data.get('hf_type', '')
            nyha_class = patient_data.get('nyha_class')
            medications = patient_data.get('medications', [])
            lab_values = patient_data.get('lab_values', {})
            comorbidities = patient_data.get('comorbidities', [])
            
            # Generate recommendations based on patient profile
            recommendations = []
            
            # Header
            recommendations.append("## 🏥 Heart Failure Management Recommendations")
            recommendations.append("*Based on 2022 AHA/ACC/HFSA Heart Failure Guidelines*")
            recommendations.append("")
            
            # Patient summary
            summary = self._generate_patient_summary(patient_data)
            if summary:
                recommendations.append("### 📋 Patient Summary")
                recommendations.append(summary)
                recommendations.append("")
            
            # Current medications analysis
            med_analysis = self._analyze_current_medications(medications, hf_type, lvef)
            if med_analysis:
                recommendations.append("### 💊 Current Medications Analysis")
                recommendations.append(med_analysis)
                recommendations.append("")
            
            # New recommendations
            new_recs = self._generate_medication_recommendations(patient_data)
            if new_recs:
                recommendations.append("### ✅ Medication Recommendations")
                recommendations.append(new_recs)
                recommendations.append("")
            
            # Monitoring recommendations
            monitoring = self._generate_monitoring_recommendations(patient_data)
            if monitoring:
                recommendations.append("### 🔍 Monitoring & Follow-up")
                recommendations.append(monitoring)
                recommendations.append("")
            
            # Lifestyle and additional considerations
            lifestyle = self._generate_lifestyle_recommendations(patient_data)
            if lifestyle:
                recommendations.append("### 🏃 Lifestyle & Additional Considerations")
                recommendations.append(lifestyle)
                recommendations.append("")
            
            # Warning if insufficient data
            if not lvef and not medications and not hf_type:
                recommendations.append("### ⚠️ Note")
                recommendations.append("For more specific recommendations, please provide:")
                recommendations.append("- LVEF (ejection fraction)")
                recommendations.append("- Current medications with doses")
                recommendations.append("- NYHA functional class or symptoms")
                recommendations.append("- Recent laboratory values (K+, creatinine)")
            
            return "\n".join(recommendations)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"
    
    def _generate_patient_summary(self, patient_data: Dict[str, Any]) -> str:
        """Generate patient summary."""
        summary_parts = []
        
        # Demographics
        age = patient_data.get('age')
        sex = patient_data.get('sex', '')
        if age or sex:
            demo = f"{age}-year-old {sex}" if age and sex else f"{age} years old" if age else sex
            summary_parts.append(f"**Demographics:** {demo}")
        
        # Heart failure details
        hf_type = patient_data.get('hf_type', '')
        lvef = patient_data.get('lvef')
        nyha_class = patient_data.get('nyha_class')
        
        hf_details = []
        if hf_type:
            hf_details.append(f"Type: {hf_type}")
        if lvef:
            hf_details.append(f"LVEF: {lvef}%")
        if nyha_class:
            hf_details.append(f"NYHA Class: {nyha_class}")
        
        if hf_details:
            summary_parts.append(f"**Heart Failure:** {', '.join(hf_details)}")
        
        return "\n".join(summary_parts)
    
    def _analyze_current_medications(self, medications: List[Dict], hf_type: str, lvef: Optional[int]) -> str:
        """Analyze current medications."""
        if not medications:
            return "No current medications reported."
        
        analysis = []
        
        # Categorize medications
        ace_arb = []
        beta_blockers = []
        mra = []
        diuretics = []
        sglt2 = []
        other = []
        
        for med in medications:
            name = med.get('name', '').lower()
            
            # ACE inhibitors and ARBs
            if any(drug in name for drug in ['lisinopril', 'enalapril', 'captopril', 'ramipril', 'losartan', 'valsartan', 'candesartan']):
                ace_arb.append(med)
            # Beta blockers
            elif any(drug in name for drug in ['metoprolol', 'carvedilol', 'bisoprolol', 'nebivolol']):
                beta_blockers.append(med)
            # MRA
            elif any(drug in name for drug in ['spironolactone', 'eplerenone']):
                mra.append(med)
            # Diuretics
            elif any(drug in name for drug in ['furosemide', 'torsemide', 'bumetanide', 'hydrochlorothiazide']):
                diuretics.append(med)
            # SGLT2 inhibitors
            elif any(drug in name for drug in ['dapagliflozin', 'empagliflozin', 'canagliflozin']):
                sglt2.append(med)
            else:
                other.append(med)
        
        # Analyze each category for HFrEF
        if hf_type == 'HFrEF' or (lvef and lvef < 40):
            
            if ace_arb:
                analysis.append(f"✅ **ACE inhibitor/ARB:** {self._format_medications(ace_arb)} - Appropriate for HFrEF")
            else:
                analysis.append("❌ **ACE inhibitor/ARB:** Not prescribed - **Strongly recommended** for HFrEF")
            
            if beta_blockers:
                analysis.append(f"✅ **Beta-blocker:** {self._format_medications(beta_blockers)} - Appropriate for HFrEF")
            else:
                analysis.append("❌ **Beta-blocker:** Not prescribed - **Strongly recommended** for HFrEF")
            
            if mra:
                analysis.append(f"✅ **MRA:** {self._format_medications(mra)} - Good addition for HFrEF")
            else:
                analysis.append("⚠️ **MRA:** Consider adding if LVEF ≤35% and symptoms persist")
            
            if sglt2:
                analysis.append(f"✅ **SGLT2 inhibitor:** {self._format_medications(sglt2)} - Excellent for additional benefit")
            else:
                analysis.append("⚠️ **SGLT2 inhibitor:** Consider for additional cardiovascular benefit")
            
            if diuretics:
                analysis.append(f"✅ **Diuretics:** {self._format_medications(diuretics)} - For volume management")
        
        else:
            # For HFpEF or unspecified
            for med in medications:
                confidence = med.get('confidence', 'N/A')
                conf_text = f" (confidence: {confidence:.2f})" if isinstance(confidence, (int, float)) else ""
                analysis.append(f"• {med.get('name', 'Unknown')} {med.get('dose', '')} {med.get('frequency', '')}{conf_text}")
        
        return "\n".join(analysis)
    
    def _format_medications(self, medications: List[Dict]) -> str:
        """Format medication list."""
        formatted = []
        for med in medications:
            name = med.get('name', 'Unknown')
            dose = med.get('dose', '')
            frequency = med.get('frequency', '')
            formatted.append(f"{name} {dose} {frequency}".strip())
        return ", ".join(formatted)
    
    def _generate_medication_recommendations(self, patient_data: Dict[str, Any]) -> str:
        """Generate new medication recommendations."""
        recommendations = []
        
        hf_type = patient_data.get('hf_type', '')
        lvef = patient_data.get('lvef')
        medications = patient_data.get('medications', [])
        nyha_class = patient_data.get('nyha_class')
        
        # Get current medication types
        current_meds = [med.get('name', '').lower() for med in medications]
        
        # For HFrEF
        if hf_type == 'HFrEF' or (lvef and lvef < 40):
            
            # ACE inhibitor/ARB
            if not any(drug in ' '.join(current_meds) for drug in ['lisinopril', 'enalapril', 'losartan', 'valsartan']):
                recommendations.append("1. **ACE inhibitor** - Start lisinopril 5mg daily, titrate to maximum tolerated dose (up to 40mg daily)")
            
            # Beta-blocker
            if not any(drug in ' '.join(current_meds) for drug in ['metoprolol', 'carvedilol', 'bisoprolol']):
                recommendations.append("2. **Beta-blocker** - Start metoprolol succinate 25mg daily or carvedilol 3.125mg BID, titrate as tolerated")
            
            # MRA
            if not any(drug in ' '.join(current_meds) for drug in ['spironolactone', 'eplerenone']):
                if lvef and lvef <= 35:
                    recommendations.append("3. **MRA therapy** - Consider spironolactone 25mg daily (monitor K+ and creatinine)")
            
            # SGLT2 inhibitor
            if not any(drug in ' '.join(current_meds) for drug in ['dapagliflozin', 'empagliflozin']):
                recommendations.append("4. **SGLT2 inhibitor** - Consider dapagliflozin 10mg daily for additional cardiovascular benefit")
            
            # Diuretics if symptoms
            if nyha_class and nyha_class >= 2:
                if not any(drug in ' '.join(current_meds) for drug in ['furosemide', 'torsemide']):
                    recommendations.append("5. **Loop diuretic** - Consider if signs of volume overload present")
        
        elif hf_type == 'HFpEF' or (lvef and lvef >= 50):
            recommendations.append("**HFpEF Management:**")
            recommendations.append("• Control blood pressure (target <130/80 mmHg)")
            recommendations.append("• Manage diabetes if present")
            recommendations.append("• Consider SGLT2 inhibitor for additional benefit")
            recommendations.append("• Diuretics for volume management if needed")
        
        else:
            # General recommendations when type unclear
            recommendations.append("**General Heart Failure Management:**")
            recommendations.append("• LVEF assessment needed to guide therapy")
            recommendations.append("• Consider ACE inhibitor or ARB")
            recommendations.append("• Beta-blocker therapy if appropriate")
            recommendations.append("• Volume assessment and diuretic therapy if needed")
        
        return "\n".join(recommendations) if recommendations else "Continue current therapy with regular monitoring."
    
    def _generate_monitoring_recommendations(self, patient_data: Dict[str, Any]) -> str:
        """Generate monitoring recommendations."""
        monitoring = []
        
        medications = patient_data.get('medications', [])
        hf_type = patient_data.get('hf_type', '')
        
        # Standard monitoring
        monitoring.append("**Laboratory Monitoring:**")
        monitoring.append("• Complete metabolic panel (K+, Na+, creatinine, eGFR) in 1-2 weeks after medication changes")
        monitoring.append("• BNP or NT-proBNP if diagnosis unclear or monitoring therapy")
        
        # Medication-specific monitoring
        med_names = ' '.join([med.get('name', '').lower() for med in medications])
        
        if any(drug in med_names for drug in ['spironolactone', 'eplerenone']):
            monitoring.append("• **MRA monitoring:** K+ and creatinine within 1 week, then monthly for 3 months")
        
        if any(drug in med_names for drug in ['lisinopril', 'enalapril', 'losartan', 'valsartan']):
            monitoring.append("• **ACE inhibitor/ARB:** Monitor blood pressure and renal function")
        
        # Clinical monitoring
        monitoring.append("")
        monitoring.append("**Clinical Monitoring:**")
        monitoring.append("• Daily weight monitoring (report weight gain >2-3 lbs in 1 day or >5 lbs in 1 week)")
        monitoring.append("• Symptoms assessment (dyspnea, fatigue, exercise tolerance)")
        monitoring.append("• Blood pressure and heart rate")
        monitoring.append("• Follow-up in 1-2 weeks after medication initiation/changes")
        
        return "\n".join(monitoring)
    
    def _generate_lifestyle_recommendations(self, patient_data: Dict[str, Any]) -> str:
        """Generate lifestyle recommendations."""
        lifestyle = []
        
        lifestyle.append("**Dietary Modifications:**")
        lifestyle.append("• Sodium restriction: <3g daily (2g if advanced HF)")
        lifestyle.append("• Fluid restriction: 2L daily if hyponatremic or advanced HF")
        lifestyle.append("• Weight management if overweight")
        
        lifestyle.append("")
        lifestyle.append("**Activity & Exercise:**")
        lifestyle.append("• Regular aerobic exercise as tolerated (cardiac rehabilitation if available)")
        lifestyle.append("• Avoid excessive exertion during acute decompensation")
        
        lifestyle.append("")
        lifestyle.append("**Additional Considerations:**")
        lifestyle.append("• Medication adherence counseling")
        lifestyle.append("• Vaccination (influenza, pneumococcal, COVID-19)")
        lifestyle.append("• Avoid NSAIDs and certain antiarrhythmic drugs")
        
        # Device therapy consideration
        lvef = patient_data.get('lvef')
        if lvef and lvef <= 35:
            lifestyle.append("• **Device therapy evaluation:** Consider ICD/CRT evaluation if LVEF ≤35% on optimal medical therapy")
        
        return "\n".join(lifestyle)

def generate_rule_based_recommendation(user_input: str, patient_data: Dict[str, Any], guidelines: Dict[str, Any]) -> str:
    """
    Generate recommendations using rule-based engine.
    
    Args:
        user_input: Original user input
        patient_data: Extracted patient data
        guidelines: Loaded guidelines
        
    Returns:
        Formatted recommendation string
    """
    engine = GuidelineRecommendationEngine(guidelines)
    return engine.generate_recommendation(patient_data, user_input)
