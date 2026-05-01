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

class Remediation(BaseModel):
    issue: str = Field(description="The core risk or issue")
    suggestion: str = Field(description="Actionable suggestion to remediate the risk")
    justification: str = Field(description="Legal or commercial justification for the change")

class AuditorScribeOutput(BaseModel):
    assumptions: List[str] = Field(description="Assumptions made during analysis")
    uncertainties: List[str] = Field(description="Ambiguities or uncertainties in the contract")
    overall_confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    remediations: List[Remediation] = Field(description="List of remediations for identified risks")

def auditor_scribe_node(state: ReviewState) -> ReviewState:
    """
    Assumption & Uncertainty Auditor (AUDITOR)
    Role: Explainability Officer
    + 
    Remediation Suggestion Agent (SCRIBE)
    Role: Drafter
    """
    logger.info("Executing AUDITOR_SCRIBE Agent")
    risks = state.get("risks", [])
    
    if not os.getenv("GOOGLE_API_KEY"):
        state["assumptions"] = ["Jurisdiction derived from input context."]
        state["uncertainties"] = []
        state["overall_confidence"] = 0.85
        state["remediation_suggestions"] = []
        return state
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(AuditorScribeOutput)
    
    risk_summary = "\n".join([f"Dimension: {r['risk_dimension']}, Level: {r['risk_level']}, Reason: {r['reason']}" for r in risks])
    
    prompt = PromptTemplate.from_template(
        "You are an Auditor and Legal Drafter.\n"
        "Based on the following identified risks in the contract:\n"
        "{risk_summary}\n\n"
        "Provide:\n"
        "1. Any assumptions you are making.\n"
        "2. Uncertainties or ambiguities that require human review.\n"
        "3. An overall confidence score (0.0 to 1.0) of the risk analysis.\n"
        "4. Actionable remediation strategies for each critical or high risk.\n"
    )
    
    try:
        result = structured_llm.invoke(prompt.format(risk_summary=risk_summary if risk_summary else "No major risks identified."))
        
        state["assumptions"] = result.assumptions
        state["uncertainties"] = result.uncertainties
        state["overall_confidence"] = result.overall_confidence
        state["remediation_suggestions"] = [r.model_dump() for r in result.remediations]
        
    except Exception as e:
        logger.error(f"AUDITOR_SCRIBE failed: {e}")
        state["assumptions"] = ["Error during LLM analysis"]
        state["uncertainties"] = ["Failed to process uncertainties"]
        state["overall_confidence"] = 0.5
        state["remediation_suggestions"] = []
        
    return state
