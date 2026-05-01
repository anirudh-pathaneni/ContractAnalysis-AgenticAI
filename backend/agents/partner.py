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

class Risk(BaseModel):
    clause_id: str = Field(description="The ID of the clause this risk applies to")
    risk_dimension: str = Field(description="e.g., Legal Validity, Enforceability, Commercial Imbalance, Compliance")
    risk_level: str = Field(description="Low, Medium, High, or Critical")
    reason: str = Field(description="Clear explanation of the risk factor.")

class RiskAssessment(BaseModel):
    """Assessment of all risks across all clauses in the contract"""
    risks: List[Risk] = Field(description="List of all identified risks across all clauses")

def partner_node(state: ReviewState) -> ReviewState:
    """
    Risk Assessment Agent (PARTNER)
    Role: Senior Partner (Rule-guided reasoning)
    Assigns risks across dimensions in a single batch call.
    """
    logger.info("Executing PARTNER Agent")
    clauses = state.get("clauses", [])
    jurisdiction = state.get("jurisdiction", "")
    user_role = state.get("user_role", "")
    
    if "risks" not in state or not state["risks"]:
        state["risks"] = []

    if not os.getenv("GOOGLE_API_KEY") or not clauses:
        logger.warning("Missing API Key or clauses. Skipping AI Risk Assessment.")
        return state

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(RiskAssessment)
    
    # Build a condensed summary of all clauses with their statutes
    statutory_citations = state.get("statutory_citations", [])
    clauses_text = ""
    for clause in clauses:
        clause_statutes = [c["text"] for c in statutory_citations if c.get("clause_id") == clause["clause_id"]]
        statute_text = "\n".join(clause_statutes) if clause_statutes else "No specific statute provided."
        clauses_text += (
            f"Clause ID: {clause['clause_id']}\n"
            f"Heading: {clause['heading']}\n"
            f"Text: {clause['raw_text']}\n"
            f"Relevant Statutes: {statute_text}\n---\n"
        )
    
    prompt = PromptTemplate.from_template(
        "You are a Senior Legal Partner analyzing a contract.\n"
        "Analyze ALL of the following clauses for risks from the perspective of the {user_role} under {jurisdiction} law.\n"
        "For each risk found, include the clause_id it belongs to.\n\n"
        "Clauses:\n{clauses_text}\n\n"
        "Return ALL identified risks across ALL clauses."
    )
    
    try:
        result = structured_llm.invoke(prompt.format(
            user_role=user_role,
            jurisdiction=jurisdiction,
            clauses_text=clauses_text
        ))
        
        # Validate clause IDs and append
        valid_ids = {c["clause_id"] for c in clauses}
        for r in result.risks:
            if r.clause_id in valid_ids:
                state["risks"].append({
                    "clause_id": r.clause_id,
                    "risk_dimension": r.risk_dimension,
                    "risk_level": r.risk_level,
                    "reason": r.reason
                })
            else:
                logger.warning(f"PARTNER returned risk for unknown clause_id: {r.clause_id}")
                
    except Exception as e:
        logger.error(f"Batch PARTNER risk analysis failed: {e}")
            
    return state
