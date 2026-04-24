import logging
import uuid
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState, Clause

logger = logging.getLogger(__name__)

def clause_extraction_node(state: ReviewState) -> ReviewState:
    """
    Clause Extraction Agent (READER)
    Identifies and segments clauses from raw contract text.
    In a real scenario, this would use unstructured.io or LLM parsing.
    For prototype purposes, we simulate splitting by double newlines or headers.
    """
    logger.info("Executing READER Agent")
    raw_text = state.get("raw_text", "")
    
    # Mock segmentation: split by double newlines and treat them as clauses
    # In production, use `unstructured.partition.text.partition_text`
    raw_clauses = [c.strip() for c in raw_text.split("\n\n") if c.strip()]
    
    clauses = []
    current_offset = 0
    
    for i, text in enumerate(raw_clauses):
        # Find actual offset
        start_idx = raw_text.find(text, current_offset)
        if start_idx == -1:
            start_idx = current_offset # Fallback
            
        end_idx = start_idx + len(text)
        current_offset = end_idx
        
        # Determine a mock heading (e.g., first few words)
        heading = text.split(".")[0][:50] if "." in text else f"Clause {i+1}"
        
        clause: Clause = {
            "clause_id": str(uuid.uuid4()),
            "heading": heading,
            "start_offset": start_idx,
            "end_offset": end_idx,
            "raw_text": text
        }
        clauses.append(clause)

    return {"clauses": clauses}
