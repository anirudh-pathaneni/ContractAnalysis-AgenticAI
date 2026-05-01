import logging
import sys
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from backend.db.neo4j_client import neo4j_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class Reference(BaseModel):
    source_clause_id: str = Field(description="The ID of the clause making the reference")
    target_clause_id: str = Field(description="The ID of the clause being referenced")

class ReferencesExtraction(BaseModel):
    """Extraction of all references between clauses in the contract"""
    references: List[Reference] = Field(description="List of all cross-references between clauses")

def navigator_node(state: ReviewState) -> ReviewState:
    """
    Cross-Reference Resolution Agent (NAVIGATOR)
    Role: Senior Associate (Stateful)
    Resolves internal references like "subject to Section X" using an LLM in a single batch.
    Updates the knowledge graph with REFERENCES edges.
    """
    logger.info("Executing NAVIGATOR Agent")
    clauses = state.get("clauses", [])
    contract_id = state.get("contract_id")
    
    if not clauses or not contract_id or not os.getenv("GOOGLE_API_KEY"):
        logger.warning("Missing API Key or clauses. Skipping semantic cross-reference resolution.")
        return state

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(ReferencesExtraction)
    
    # Prepare a condensed string of all clauses
    clauses_text = ""
    for c in clauses:
        clauses_text += f"ID: {c.get('clause_id')} | Heading: {c.get('heading')}\nText: {c.get('raw_text')}\n---\n"
    
    prompt = PromptTemplate.from_template(
        "You are a Cross-Reference Resolution Agent.\n"
        "Here is the list of all clauses in a contract:\n{clauses_text}\n\n"
        "Analyze ALL the clauses and identify if ANY clause references another clause.\n"
        "Return a comprehensive list of all identified references with their source and target clause IDs."
    )
    
    try:
        result = structured_llm.invoke(prompt.format(
            clauses_text=clauses_text
        ))
        
        for ref in result.references:
            # Basic validation to ensure both IDs exist before adding to neo4j
            source_exists = any(c["clause_id"] == ref.source_clause_id for c in clauses)
            target_exists = any(c["clause_id"] == ref.target_clause_id for c in clauses)
            
            if source_exists and target_exists:
                neo4j_client.add_cross_reference(ref.source_clause_id, ref.target_clause_id)
                logger.info(f"Resolved reference from {ref.source_clause_id} to {ref.target_clause_id}")
            else:
                logger.warning(f"Ignored invalid reference: {ref.source_clause_id} -> {ref.target_clause_id}")
                
    except Exception as e:
        logger.error(f"Batch NAVIGATOR failed: {e}")
            
    return state
