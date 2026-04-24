import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from backend.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

def architect_node(state: ReviewState) -> ReviewState:
    """
    Contract Graph Builder Agent (ARCHITECT)
    Deterministic knowledge engineer converting extracted clauses into a structural graph.
    """
    logger.info("Executing ARCHITECT Agent")
    contract_id = state.get("contract_id")
    contract_type = state.get("contract_type")
    jurisdiction = state.get("jurisdiction")
    clauses = state.get("clauses", [])
    
    if not contract_id:
        logger.error("No contract ID found in state.")
        return {"graph_built": False}
        
    try:
        # Create base Contract graph node
        neo4j_client.add_contract(contract_id, contract_type, jurisdiction)
        
        # Add Clause nodes and edges
        for clause in clauses:
            neo4j_client.add_clause(
                contract_id=contract_id,
                clause_id=clause["clause_id"],
                heading=clause["heading"],
                start_offset=clause["start_offset"],
                end_offset=clause["end_offset"],
                raw_text=clause["raw_text"]
            )
            
        return {"graph_built": True}
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        return {"graph_built": False}
