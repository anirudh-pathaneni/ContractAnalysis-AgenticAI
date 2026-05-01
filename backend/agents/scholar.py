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
        
    all_citations = []
    
    for clause in clauses:
        search_query = f"Jurisdiction: {jurisdiction}. Topic: {clause.get('heading', '')}. Text: {clause.get('raw_text', '')}"
        try:
            results = vector_store.search_law(search_query)
            if results and results.get('documents') and len(results['documents']) > 0:
                for idx, doc_set in enumerate(results['documents']):
                    for i, doc in enumerate(doc_set):
                        meta = results['metadatas'][idx][i] if results.get('metadatas') else {}
                        all_citations.append({
                            "clause_id": clause["clause_id"],
                            "statute": meta.get("statute", "Unknown Statute"),
                            "text": doc
                        })
        except Exception as e:
            logger.warning(f"Scholar retrieval failed: {e}")
            break

    current_citations = state.get("statutory_citations")
    if current_citations is None:
        current_citations = []
    state["statutory_citations"] = current_citations + all_citations
    return state
