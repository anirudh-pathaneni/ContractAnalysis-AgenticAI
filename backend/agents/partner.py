import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState

logger = logging.getLogger(__name__)

def partner_node(state: ReviewState) -> ReviewState:
    """
    Risk Assessment Agent (PARTNER)
    Role: Senior Partner (Rule-guided reasoning)
    Assigns risks across dimensions: Legal Validity, Enforceability, etc.
    """
    logger.info("Executing PARTNER Agent")
    
    # Initialize risks if not present
    if "risks" not in state or not state["risks"]:
        state["risks"] = []
        
    # Dummy mock reasoning
    # If the jurisdiction is India and type is Employment, flag non-compete broadly.
    jurisdiction = state.get("jurisdiction", "")
    
    for clause in state.get("clauses", []):
        if "non-compete" in clause.get("raw_text", "").lower() and "india" in jurisdiction.lower():
            state["risks"].append({
                "clause_id": clause["clause_id"],
                "risk_dimension": "Legal Validity",
                "risk_level": "Critical",
                "reason": "Non-compete is generally void under Section 27 of Indian Contract Act."
            })
            
    return state
