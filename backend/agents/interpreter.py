import logging
import sys
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ClauseInterpretation(BaseModel):
    clause_id: str = Field(description="The ID of the clause being interpreted")
    effective_meaning: str = Field(description="The plain-english effective meaning of the clause")

class BatchInterpretationResult(BaseModel):
    """Batch interpretation of multiple clauses"""
    interpretations: List[ClauseInterpretation] = Field(description="List of interpretations for the provided clauses")

def interpreter_node(state: ReviewState) -> ReviewState:
    """
    Definition & Scope Resolution Agent (INTERPRETER)
    Computes effective meaning of clauses in a single batch to avoid rate limits.
    """
    logger.info("Executing INTERPRETER Agent")
    clauses = state.get("clauses", [])
    
    if not clauses or not os.getenv("GOOGLE_API_KEY"):
        logger.warning("No clauses to interpret or missing GOOGLE_API_KEY.")
        return state
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(BatchInterpretationResult)
    
    prompt = PromptTemplate.from_template(
        "You are a Legal Analyst interpreting contract clauses.\n"
        "Contract Context: Jurisdiction: {jurisdiction}, Type: {contract_type}\n"
        "Clauses to interpret:\n{clauses_text}\n\n"
        "Provide a plain-english effective meaning, resolving any subject-to carve-outs, for EACH clause."
    )
    
    # Prepare a condensed string of all clauses to interpret
    clauses_text = ""
    for c in clauses:
        clauses_text += f"ID: {c.get('clause_id')}\nText: {c.get('raw_text')}\n---\n"
        
    try:
        result = structured_llm.invoke(prompt.format(
            jurisdiction=state.get("jurisdiction", "Unknown"),
            contract_type=state.get("contract_type", "Unknown"),
            clauses_text=clauses_text
        ))
        
        # Map back to original clauses by ID
        interpretation_map = {i.clause_id: i.effective_meaning for i in result.interpretations}
        for clause in clauses:
            clause["effective_meaning"] = interpretation_map.get(clause.get("clause_id"), "Interpretation unavailable.")
            
    except Exception as e:
        logger.error(f"Batch LLM Interpretation failed: {e}")
            
    return state
