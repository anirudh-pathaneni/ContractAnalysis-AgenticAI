import sys
from pathlib import Path

# Add backend to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.db.vector_store import vector_store

def ingest_laws():
    print("Ingesting statutory laws into ChromaDB...")
    
    # Mock data for Indian Contract Act & Labor Laws
    laws = [
        {
            "id": "ica_sec_27",
            "text": "Every agreement by which anyone is restrained from exercising a lawful profession, trade or business of any kind, is to that extent void. Exception: Saving of agreement not to carry on business of which goodwill is sold.",
            "metadata": {"statute": "Indian Contract Act, 1872", "section": "27", "topic": "Non-compete"}
        },
        {
            "id": "ica_sec_73",
            "text": "Compensation for loss or damage caused by breach of contract. When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach, or which the parties knew, when they made the contract, to be likely to result from the breach of it.",
            "metadata": {"statute": "Indian Contract Act, 1872", "section": "73", "topic": "Damages"}
        },
        {
            "id": "payment_of_gratuity_sec_4",
            "text": "Gratuity shall be payable to an employee on the termination of his employment after he has rendered continuous service for not less than five years, on his superannuation, or on his retirement or resignation.",
            "metadata": {"statute": "Payment of Gratuity Act, 1972", "section": "4", "topic": "Gratuity"}
        }
    ]
    
    ids = [law["id"] for law in laws]
    texts = [law["text"] for law in laws]
    metadatas = [law["metadata"] for law in laws]
    
    vector_store.add_documents(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Successfully ingested {len(laws)} legal provisions into the vector store.")

if __name__ == "__main__":
    ingest_laws()
