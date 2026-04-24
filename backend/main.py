from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import logging
from typing import Optional
from datetime import datetime

from backend.graph.orchestrator import app_graph
from backend.models.state import ReviewState
from backend.db.postgres_client import get_db, ContractMetadata, AgentLog
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Contract Intelligence System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-text")
async def analyze_contract_text(
    raw_text: str = Form(...),
    user_role: str = Form("Employer"),
    counterparty_role: str = Form("Employee"),
    contract_type: str = Form("Employment"),
    jurisdiction: str = Form("India"),
    db: Session = Depends(get_db)
):
    contract_id = str(uuid.uuid4())
    
    # Initial state
    initial_state = {
        "contract_id": contract_id,
        "raw_text": raw_text,
        "user_role": user_role,
        "counterparty_role": counterparty_role,
        "contract_type": contract_type,
        "jurisdiction": jurisdiction,
        "clauses": [],
        "risks": [],
        "assumptions": [],
        "uncertainties": [],
        "remediation_suggestions": [],
        "overall_confidence": 1.0,
        "graph_built": False
    }
    
    # 1. Run Graph
    logger.info(f"Starting orchestration for contract {contract_id}")
    final_state = app_graph.invoke(initial_state)
    logger.info(f"Finished orchestration for contract {contract_id}")
    
    # 2. Persist to Relational DB (PostgreSQL) for Metadata
    db_metadata = ContractMetadata(
        id=contract_id,
        filename="Manual Text Input",
        extracted_roles={"user": request.user_role, "counterparty": request.counterparty_role},
        status="completed"
    )
    db.add(db_metadata)
    
    # Log the final state JSON briefly
    db_log = AgentLog(
        contract_id=contract_id,
        agent_name="orchestrator",
        log_data={"total_risks_found": len(final_state.get("risks", [])), "graph_built": final_state.get("graph_built")}
    )
    db.add(db_log)
    db.commit()

    return {
        "contract_id": contract_id,
        "status": "completed",
        "risks": final_state.get("risks"),
        "remediations": final_state.get("remediation_suggestions"),
        "assumptions": final_state.get("assumptions"),
        "uncertainties": final_state.get("uncertainties")
    }

@app.get("/")
def read_root():
    return {"message": "Agent Contract Intelligence System Backend is Running."}
