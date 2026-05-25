# LumenFlow

AI-powered customer support workflow system with local LLMs, RAG, human-in-the-loop review, evaluation harness, and observability built for production-style support operations.

---

## Overview

LumenFlow is a production-focused GenAI support workflow built for handling inbound customer support tickets at scale.

The system ingests customer emails, retrieves relevant context, classifies and routes tickets, drafts grounded responses using local LLMs, and surfaces everything through a human review dashboard.

This project was built as part of the GenAI Workflow Engineer assignment.

---

## Core Features

- Local LLM powered workflow (Ollama)
- Retrieval-Augmented Generation (RAG)
- Multi-stage ticket classification
- Human-in-the-loop review system
- Grounded response generation with citations
- Evaluation harness for offline testing
- Observability and tracing
- Prompt versioning
- Role-based dashboard access
- Guardrails against prompt injection and hallucinations

---

## Architecture

```text
Inbound Email
    ↓
Preprocessing
    ↓
Guardrails / Injection Detection
    ↓
Classification
    ↓
Context Retrieval
    ↓
Decision Engine
    ↓
Draft Generation
    ↓
Citation Grounding
    ↓
Human Review Dashboard
```

---

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- pgvector
- SQLAlchemy
- Ollama
- SentenceTransformers

### Frontend
- Next.js
- TailwindCSS
- shadcn/ui

### Infrastructure
- Docker
- Docker Compose

---

## Project Structure

```text
backend/
frontend/
prompts/
evals/
synthetic_data/
scripts/
docker/
```

---

## Current Status

Work in Progress

Planned implementation phases:

- [ ] Backend foundation
- [ ] Database schema
- [ ] Authentication system
- [ ] Ticket ingestion pipeline
- [ ] RAG pipeline
- [ ] LLM workflow orchestration
- [ ] Dashboard UI
- [ ] Evaluation harness
- [ ] Observability & tracing
- [ ] Dockerization
- [ ] Documentation & reflection

---

## Key Design Goals

- Prefer deterministic workflows over autonomous agents
- Keep humans in control of final actions
- Use the smallest effective local models
- Prioritize grounded and traceable outputs
- Make failures observable and debuggable
- Optimize for reliability over flashy demos

---

## Evaluation Focus

The evaluation harness will measure:

- Classification accuracy
- Retrieval quality
- Routing correctness
- Draft groundedness
- Human override rate
- Failure modes
- Prompt injection robustness

---

## Local Development

### Clone the repository

```bash
git clone <repo-url>
cd lumenflow
```

### Start services

```bash
docker compose up -d
```

### Fresh local setup

Use this when starting from a fresh local database:

```bash
docker compose down -v
docker compose up -d
source venv/bin/activate
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

### Normal local run

Use this when the database already exists and no new migration has been added:

```bash
source venv/bin/activate
cd backend
uvicorn app.main:app --reload
```

### Local run after schema changes

Use this when a new Alembic migration has been added:

```bash
source venv/bin/activate
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Planned Models

| Task | Model |
|---|---|
| Embeddings | BGE Small |
| Classification | Llama 3.2 3B |
| Drafting | Mistral 7B |
| Retrieval | pgvector |

---

## Future Improvements

- Regression testing for prompt changes
- Human feedback learning loop
- Better reranking
- Multi-turn conversation memory
- Cost monitoring dashboard
- Fine-tuned classifiers

---

## Disclaimer

This project uses fully synthetic customer support data for demonstration and evaluation purposes only.

---

## License

MIT
