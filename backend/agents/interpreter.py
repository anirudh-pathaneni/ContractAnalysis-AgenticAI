import logging
import sys
import os
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.state import ReviewState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

def interpreter_node(state: ReviewState) -> ReviewState:
    """
    Definition & Scope Resolution Agent (INTERPRETER)
    Computes effective meaning of a clause and resolves carve-outs.
    """
    logger.info("Executing INTERPRETER Agent")
    clauses = state.get("clauses", [])
    
    if not clauses or not os.getenv("GOOGLE_API_KEY"):
        logger.warning("No clauses to interpret or missing GOOGLE_API_KEY.")
        return state
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    
    prompt = PromptTemplate.from_template(
        "You are a Legal Analyst interpreting contract clauses.\n"
        "Contract Context: Jurisdiction: {jurisdiction}, Type: {contract_type}\n"
        "Clause:\n{clause_text}\n\n"
        "Provide a plain-english effective meaning, resolving any subject-to carve-outs."
    )
    
    # In a full flow, you'd process specific prioritized clauses or batch them
    # We will simulate interpreting the first major clause as an example
    if len(clauses) > 0:
        target = clauses[0]
        chain = prompt | llm
        try:
            res = chain.invoke({
                "jurisdiction": state.get("jurisdiction", "Unknown"),
                "contract_type": state.get("contract_type", "Unknown"),
                "clause_text": target["raw_text"]
            })
            logger.info("INTERPRETER successfully processed a clause.")
        except Exception as e:
            logger.error(f"LLM Interpretation failed: {e}")
            
    return state
