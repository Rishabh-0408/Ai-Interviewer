# AI Interviewer

An evidence-driven AI interview simulator that researches the candidate's target role and organization, analyzes relevant interview patterns and core concepts, and conducts realistic adaptive interviews.

## Modes

- **Focused Practice** — Practice specific question categories (Technical, Behavioral, Case Study, etc.) through a realistic, adaptive interview.
- **Real Interview Simulation** — Experience a full interview where the AI dynamically determines the interview structure based on the target role and company.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy 2.x |
| Database | PostgreSQL 16, pgvector |
| Auth | Firebase Authentication |
| Voice | Pipecat (MVP) |
| Migrations | Alembic |
| Infrastructure | Docker, Docker Compose |

## Project Structure

```
ai-interviewer/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── docker/            # Docker configs
├── docs/              # Documentation
├── docker-compose.yml
└── .env.example
```

## Local Development

### Prerequisites

- Python 3.14+
- Node.js 24+
- Docker & Docker Compose (for PostgreSQL)
- Firebase project (for authentication)

### Setup

1. **Clone & configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials and database URL
   ```

2. **Start PostgreSQL**
   ```bash
   docker compose up -d db
   ```

3. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   pip install -e ".[dev]"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

4. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture

The system uses a **modular monolith** backend architecture. Core modules:

- `api/` — HTTP routes (thin layer)
- `interview/` — Interview engine, planner, state machine
- `ai/` — Question generation, evaluation, report generation
- `research/` — Organization & role research
- `rag/` — Document ingestion, embedding, retrieval
- `voice/` — Voice interface (Pipecat)

## License

Private — All rights reserved.
