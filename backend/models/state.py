from typing import TypedDict, List, Dict, Any, Optional

class Clause(TypedDict):
    clause_id: str
    heading: str
    start_offset: int
    end_offset: int
    raw_text: str

class ReviewState(TypedDict):
    contract_id: str
    raw_text: str
    
    # Context Intake
    user_role: Optional[str]
    counterparty_role: Optional[str]
    contract_type: Optional[str]
    jurisdiction: Optional[str]
    
    # Reader
    clauses: List[Clause]
    
    # Architect
    graph_built: bool
    
    # Navigator, Interpreter, Scholar, Partner outputs
    risks: List[Dict[str, Any]]
    assumptions: List[str]
    uncertainties: List[str]
    overall_confidence: float
    remediation_suggestions: List[Dict[str, Any]]
