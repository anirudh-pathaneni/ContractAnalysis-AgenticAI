import logging
import sys
import re
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from backend.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

def navigator_node(state: ReviewState) -> ReviewState:
    """
    Cross-Reference Resolution Agent (NAVIGATOR)
    Role: Senior Associate (Stateful)
    Resolves internal references like "subject to Section X" using basic heuristics or an LLM.
    Updates the knowledge graph with REFERENCES edges.
    """
    logger.info("Executing NAVIGATOR Agent")
    clauses = state.get("clauses", [])
    contract_id = state.get("contract_id")
    
    if not clauses or not contract_id:
        return state

    # A simple heuristic-based resolver (in production, use LLM for semantic reference extraction)
    for clause in clauses:
        text = clause.get("raw_text", "")
        # Look for "Clause X" or "Section X"
        matches = re.finditer(r"(Clause|Section)\s+(\d+)", text, re.IGNORECASE)
        for match in matches:
            ref_idx = match.group(2)
            # Try to find the referenced clause based on heading parsing (assuming headings like "Clause 2")
            target_clause = next((c for c in clauses if f"Clause {ref_idx}" in c.get("heading", "")), None)
            
            if target_clause:
                logger.info(f"Resolved reference from {clause['clause_id']} to {target_clause['clause_id']}")
                neo4j_client.add_cross_reference(clause["clause_id"], target_clause["clause_id"])
                
    return state
