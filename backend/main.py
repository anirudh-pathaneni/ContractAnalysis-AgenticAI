import os
import shutil
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import logging
from typing import Optional
from datetime import datetime
from unstructured.partition.auto import partition

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

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

def process_contract(
    raw_text: str,
    user_role: str,
    counterparty_role: str,
    contract_type: str,
    jurisdiction: str,
    filename: str,
    db: Session
):
    contract_id = str(uuid.uuid4())
    
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
    
    logger.info(f"Starting orchestration for contract {contract_id}")
    final_state = app_graph.invoke(initial_state)
    logger.info(f"Finished orchestration for contract {contract_id}")
    
    db_metadata = ContractMetadata(
        id=contract_id,
        filename=filename,
        extracted_roles={"user": user_role, "counterparty": counterparty_role},
        status="completed"
    )
    db.add(db_metadata)
    
    risks_list = final_state.get("risks")
    if risks_list is None:
        risks_list = []
    
    db_log = AgentLog(
        contract_id=contract_id,
        agent_name="orchestrator",
        log_data={"total_risks_found": len(risks_list), "graph_built": final_state.get("graph_built")}
    )
    db.add(db_log)
    db.commit()

    return {
        "contract_id": contract_id,
        "status": "completed",
        "clauses": final_state.get("clauses", []),
        "risks": final_state.get("risks", []),
        "remediations": final_state.get("remediation_suggestions", []),
        "assumptions": final_state.get("assumptions", []),
        "uncertainties": final_state.get("uncertainties", [])
    }

@app.post("/analyze-text")
async def analyze_contract_text(
    raw_text: str = Form(...),
    user_role: str = Form("Employer"),
    counterparty_role: str = Form("Employee"),
    contract_type: str = Form("Employment"),
    jurisdiction: str = Form("India"),
    db: Session = Depends(get_db)
):
    return process_contract(
        raw_text=raw_text,
        user_role=user_role,
        counterparty_role=counterparty_role,
        contract_type=contract_type,
        jurisdiction=jurisdiction,
        filename="Manual Text Input",
        db=db
    )

@app.post("/analyze-file")
async def analyze_contract_file(
    file: UploadFile = File(...),
    user_role: str = Form("Employer"),
    counterparty_role: str = Form("Employee"),
    contract_type: str = Form("Employment"),
    jurisdiction: str = Form("India"),
    db: Session = Depends(get_db)
):
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_path = f"temp_contract_{uuid.uuid4()}{file_extension}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if file_extension.lower() == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(temp_file_path)
            raw_text = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            elements = partition(filename=temp_file_path)
            raw_text = "\n\n".join([str(el) for el in elements])
        
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        raise HTTPException(status_code=500, detail="Error parsing document. Ensure the file is a valid PDF or Document.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return process_contract(
        raw_text=raw_text,
        user_role=user_role,
        counterparty_role=counterparty_role,
        contract_type=contract_type,
        jurisdiction=jurisdiction,
        filename=file.filename,
        db=db
    )

@app.get("/")
def read_root():
    return {"message": "Agent Contract Intelligence System Backend is Running."}
