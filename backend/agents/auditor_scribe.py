import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState

logger = logging.getLogger(__name__)

def auditor_scribe_node(state: ReviewState) -> ReviewState:
    """
    Assumption & Uncertainty Auditor (AUDITOR)
    Role: Explainability Officer
    + 
    Remediation Suggestion Agent (SCRIBE)
    Role: Drafter
    """
    logger.info("Executing AUDITOR_SCRIBE Agent")
    
    # AUDITOR Logic
    state["assumptions"] = ["Jurisdiction derived from input context."]
    state["uncertainties"] = []
    state["overall_confidence"] = 0.85
    
    # SCRIBE Logic
    risks = state.get("risks", [])
    remediations = []
    
    for risk in risks:
        if risk["risk_dimension"] == "Legal Validity" and "Non-compete" in risk["reason"]:
            remediations.append({
                "issue": "Non-compete clause",
                "suggestion": "Consider removing non-compete obligation or limiting to trade secrets.",
                "justification": "Mitigates total void risk under Indian Contract Act."
            })
            
    state["remediation_suggestions"] = remediations
    
    return state
