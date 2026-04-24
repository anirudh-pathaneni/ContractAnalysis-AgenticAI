import logging
import sys
from pathlib import Path

# Add the root project dir to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langgraph.graph import StateGraph, END
from backend.models.state import ReviewState
from backend.agents.context_intake import context_intake_node
from backend.agents.reader import clause_extraction_node
from backend.agents.architect import architect_node
from backend.agents.navigator import navigator_node
from backend.agents.interpreter import interpreter_node
from backend.agents.scholar import scholar_node
from backend.agents.partner import partner_node
from backend.agents.auditor_scribe import auditor_scribe_node

logger = logging.getLogger(__name__)

def build_graph():
    """
    Review State Controller (ORCHESTRATOR)
    Builds the cyclic state machine for the contract review process.
    """
    workflow = StateGraph(ReviewState)
    
    # 1. Add nodes
    workflow.add_node("context_intake", context_intake_node)
    workflow.add_node("reader", clause_extraction_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("navigator", navigator_node)
    workflow.add_node("interpreter", interpreter_node)
    workflow.add_node("scholar", scholar_node)
    workflow.add_node("partner", partner_node)
    workflow.add_node("auditor_scribe", auditor_scribe_node)
    
    # Define an intermediate cyclic routing logic
    def check_confidence(state: ReviewState) -> str:
        # Example cyclical rule: If SCHOLAR/AUDITOR confidence < threshold -> re-query or end
        confidence = state.get("overall_confidence", 1.0)
        if confidence < 0.7:
            logger.warning("Confidence too low. We could loop back. (Ending for prototype).")
            return "end" # In a complex graph, this could route back to "scholar" or "interpreter"
        return "end"

    # 2. Add linear Edges (per architecture diagram flow)
    workflow.set_entry_point("context_intake")
    workflow.add_edge("context_intake", "reader")
    workflow.add_edge("reader", "architect")
    workflow.add_edge("architect", "navigator")
    workflow.add_edge("navigator", "interpreter")
    workflow.add_edge("interpreter", "scholar")
    workflow.add_edge("scholar", "partner")
    workflow.add_edge("partner", "auditor_scribe")
    
    # 3. Add Conditional Edge for the Orchestrator loop at the end
    workflow.add_conditional_edges(
        "auditor_scribe",
        check_confidence,
        {
            "end": END,
            "requery": "scholar" # Example of cycling back
        }
    )
    
    return workflow.compile()

app_graph = build_graph()
