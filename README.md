# Nexus AI: Agentic Contract Intelligence

An advanced, multi-agent AI system for intelligent contract analysis, powered by LangGraph, Google Gemini, and a hybrid database architecture (PostgreSQL, Neo4j, and ChromaDB).

Nexus AI breaks down complex legal documents, identifies semantic cross-references between clauses, highlights risks, and suggests remediations using a team of specialized AI agents.

---

## 🌟 Features

- **Agentic Workflow**: Utilizes LangGraph to orchestrate a pipeline of specialized agents (Context Intake, Reader, Architect, Navigator, Interpreter, Scholar, Partner, Auditor & Scribe).
- **Knowledge Graph Representation**: Maps clauses and their cross-references using Neo4j to understand the interconnected structure of a contract.
- **Risk Dashboard**: Identifies risks based on commercial and legal dimensions and provides actionable remediation suggestions.
- **Modern UI**: A responsive, interactive React frontend featuring contract graph visualizations with ReactFlow.
- **Multi-Format Support**: Upload and analyze `.pdf` documents or use manual text input.

---

## 🏗 Architecture

The system uses a stateful LangGraph-based agentic pipeline. Each agent is a specialized node in the graph with a well-defined role:

| Agent | Role | Responsibility |
|---|---|---|
| **Context Intake** | Intake Officer | Gathers user role, counterparty, contract type, and jurisdiction |
| **Reader** | Clause Extractor | Parses raw document text into discrete, structured clauses |
| **Architect** | Graph Builder | Creates `Clause` nodes in the Neo4j knowledge graph |
| **Navigator** | Cross-Reference Resolver | Identifies and maps `REFERENCES` edges between clauses |
| **Interpreter** | Clause Summarizer | Generates plain-language summaries of each clause |
| **Scholar** | Context Retriever | Retrieves relevant context from ChromaDB vector store |
| **Partner** | Risk Evaluator | Identifies legal and commercial risks per clause |
| **Auditor / Scribe** | Explainability Officer & Drafter | Provides remediations, assumptions, uncertainties & confidence score |

![System Architecture Diagram](temp_architecture_diagram.jpeg)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TypeScript, ReactFlow |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI / Agents** | LangGraph, LangChain, Google Gemini (`gemini-2.5-flash-lite`) |
| **Graph DB** | Neo4j (clause relationship mapping) |
| **Relational DB** | PostgreSQL (contract metadata & agent logs) |
| **Vector DB** | ChromaDB (semantic search & context retrieval) |
| **Infrastructure** | Docker & Docker Compose |

---

## 📁 Project Structure

```
ContractAnalysis-AgenticAI/
├── backend/
│   ├── agents/                 # Individual agent node implementations
│   │   ├── context_intake.py   # Intake agent
│   │   ├── reader.py           # Clause extraction agent
│   │   ├── architect.py        # Graph builder agent
│   │   ├── navigator.py        # Cross-reference resolver agent
│   │   ├── interpreter.py      # Clause summarizer agent
│   │   ├── scholar.py          # Context retrieval agent
│   │   ├── partner.py          # Risk evaluation agent
│   │   └── auditor_scribe.py   # Audit & remediation agent
│   ├── db/
│   │   ├── neo4j_client.py     # Neo4j connection & helpers
│   │   └── postgres_client.py  # SQLAlchemy models & session
│   ├── graph/
│   │   └── orchestrator.py     # LangGraph state machine definition
│   ├── models/
│   │   └── state.py            # Shared ReviewState TypedDict
│   ├── scripts/                # Utility and test scripts
│   └── main.py                 # FastAPI application entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadForm.tsx  # Contract upload & text input form
│   │   │   ├── RiskDashboard.tsx # Risk display panel
│   │   │   └── ContractGraph.tsx # ReactFlow knowledge graph view
│   │   ├── App.tsx             # Root application component
│   │   ├── api.ts              # API request helpers
│   │   └── index.css           # Global styles & design tokens
│   ├── index.html
│   └── package.json
├── architecture_diagram.jpg    # System architecture overview
├── docker-compose.yml          # Database services configuration
├── requirements.txt            # Python dependencies
├── sample.env                  # Environment variable template
└── README.md
```

---

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ContractAnalysis-AgenticAI
```

### 2. Configure Environment Variables

Copy the template and fill in your credentials:

```bash
cp sample.env .env
```

Then edit `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
POSTGRES_URL=postgresql://postgres:password@localhost:5433/contract_intelligence
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### 3. Start Database Services

Spin up Neo4j, PostgreSQL, and ChromaDB with Docker Compose:

```bash
docker-compose up -d
```

Services exposed:
- Neo4j Browser UI → `http://localhost:7474`
- Neo4j Bolt → `bolt://localhost:7687`
- PostgreSQL → `localhost:5433`
- ChromaDB → `http://localhost:8000`

### 4. Setup & Run the Backend

```bash
# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Unix / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server from the ROOT project directory
python -m uvicorn backend.main:app --reload --port 8001
```

> **Note:** The backend runs on port `8001` to avoid conflicts with ChromaDB on `8000`.

The FastAPI interactive docs will be available at `http://localhost:8001/docs`.

### 5. Setup & Run the Frontend

Open a new terminal and run:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### 6. Usage

1. Open `http://localhost:5173` in your browser.
2. Upload a `.pdf` contract file **or** paste raw contract text into the text area.
3. Fill in the analysis context: **User Role**, **Counterparty Role**, **Contract Type**, and **Jurisdiction**.
4. Click **"Start Analysis"**.
5. The multi-agent pipeline will process the document and return:
   - An **interactive knowledge graph** visualizing clauses and their cross-references.
   - A **Risk Dashboard** listing identified risks, their severity, and actionable remediation suggestions.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check – confirms backend is running |
| `POST` | `/analyze-text` | Analyze a contract from raw pasted text |
| `POST` | `/analyze-file` | Analyze a contract from an uploaded PDF/document |

Full interactive API documentation: `http://localhost:8001/docs`

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.
