import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from backend.db.vector_store import vector_store

logger = logging.getLogger(__name__)

def scholar_node(state: ReviewState) -> ReviewState:
    """
    Statutory Research Agent (SCHOLAR)
    Role: Legal Researcher (Retrieval-based)
    Retrieves relevant statutory provisions from the pre-ingested legal corpus.
    """
    logger.info("Executing SCHOLAR Agent")
    clauses = state.get("clauses", [])
    jurisdiction = state.get("jurisdiction", "Unknown")
    
    if not clauses:
        return state
        
    # Example: fetch statute for a clause text logic
    # We use vector_store.search_law
    
    search_query = f"jurisdiction: {jurisdiction}. {clauses[0].get('heading', '')}"
    try:
        results = vector_store.search_law(search_query)
        logger.info(f"Scholar retrieved {len(results.get('documents', []))} references.")
        # Store back in state - in real system append to specific clause metadata
    except Exception as e:
        logger.warning(f"Scholar retrieval failed or ChromaDB not initialized: {e}")

    return state
