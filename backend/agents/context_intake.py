import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState

logger = logging.getLogger(__name__)

def context_intake_node(state: ReviewState) -> ReviewState:
    """
    User Context Intake Module (Pre-Processing)
    Deterministic configuration stage.
    Normally this would extract context from a frontend request.
    For now, if missing, we inject default parameters or parse from metadata.
    """
    logger.info("Executing Context Intake Module")
    
    return {
        "user_role": state.get("user_role") or "Employer",
        "counterparty_role": state.get("counterparty_role") or "Employee",
        "contract_type": state.get("contract_type") or "Employment",
        "jurisdiction": state.get("jurisdiction") or "India"
    }
