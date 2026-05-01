import logging
import uuid
import sys
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.models.state import ReviewState, Clause
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ClauseExtracted(BaseModel):
    heading: str = Field(description="The heading or title of the clause")
    raw_text: str = Field(description="The exact raw text of the clause")

class ContractExtraction(BaseModel):
    """Extraction of all clauses from the contract"""
    clauses: List[ClauseExtracted] = Field(description="List of all extracted clauses")

def clause_extraction_node(state: ReviewState) -> ReviewState:
    """
    Clause Extraction Agent (READER)
    Identifies and segments clauses from raw contract text using an LLM.
    """
    logger.info("Executing READER Agent")
    raw_text = state.get("raw_text", "")
    
    if not os.getenv("GOOGLE_API_KEY") or not raw_text:
        logger.warning("Missing API Key or raw text, falling back to basic split.")
        raw_clauses = [c.strip() for c in raw_text.split("\n\n") if c.strip()]
        clauses = []
        for i, text in enumerate(raw_clauses):
            clauses.append({
                "clause_id": str(uuid.uuid4()),
                "heading": f"Clause {i+1}",
                "start_offset": 0,
                "end_offset": len(text),
                "raw_text": text
            })
        return {"clauses": clauses}

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(ContractExtraction)
    
    prompt = PromptTemplate.from_template(
        "You are a Junior Associate Legal Agent. Extract all distinct clauses from the following contract text.\n\n"
        "Contract Text:\n{raw_text}\n"
    )
    
    try:
        # Limit text size to prevent massive token usage in prototype
        result = structured_llm.invoke(prompt.format(raw_text=raw_text[:30000]))
        
        clauses = []
        current_offset = 0
        for extracted in result.clauses:
            start_idx = raw_text.find(extracted.raw_text, current_offset)
            if start_idx == -1:
                start_idx = current_offset # Fallback
            end_idx = start_idx + len(extracted.raw_text)
            current_offset = end_idx
            
            clause: Clause = {
                "clause_id": str(uuid.uuid4()),
                "heading": extracted.heading,
                "start_offset": start_idx,
                "end_offset": end_idx,
                "raw_text": extracted.raw_text
            }
            clauses.append(clause)
            
        return {"clauses": clauses}
    except Exception as e:
        logger.error(f"READER extraction failed: {e}")
        return state
