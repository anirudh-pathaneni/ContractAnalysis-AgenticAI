import os
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:password@localhost:5433/contract_intelligence")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ContractMetadata(Base):
    __tablename__ = "contract_metadata"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    extracted_roles = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(String, index=True)
    agent_name = Column(String)
    log_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
