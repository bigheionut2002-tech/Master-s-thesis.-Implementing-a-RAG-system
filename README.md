# Information Retrieval Systems based on Vector Databases — Implementing a RAG System

Master's thesis project — Babeș-Bolyai University, Cluj-Napoca
**Student:** Bighe Ionuț Denis
**Coordinator:** Prof. Dr. Maria-Camelia Chișălița-Crețu
**Specialization:** Databases (Master)
**Academic year:** 2025-2026

---

## Overview

This repository contains three related deliverables on the same topic:

1. **Master's thesis** (`masters_theses/Bighe_Ionut_Denis_RAG_Thesis/`) — LaTeX source, English, ~25 pages.
2. **Research reports** (`research_reports/`) — three reports in Romanian (.docx) for the "Proiect de cercetare în baze de date" course.
3. **RAG application** (`rag_application/`) — a working Retrieval-Augmented Generation system that lets users upload PDF documents and ask natural-language questions about their content. Built with FastAPI, PostgreSQL, ChromaDB, Google Gemini, and React.

---

## Repository layout

```
.
├── masters_theses/
│   ├── Bachelor Thesis Template UBB/        # Original UBB template (untouched)
│   └── Bighe_Ionut_Denis_RAG_Thesis/        # Adapted master's thesis
├── rag_application/
│   ├── backend/                             # FastAPI + PostgreSQL + ChromaDB
│   ├── frontend/                            # React + Vite + Tailwind + shadcn/ui
│   └── docker-compose.yml
├── research_reports/                        # .docx reports in Romanian
└── README.md
```

---

## Quick start (development)

### Prerequisites
- Python 3.12+
- Node.js 20+ with `pnpm` (via `corepack enable`)
- Docker Desktop (for PostgreSQL and the full stack)

### Running the full stack with Docker

```bash
cd rag_application
cp .env.example .env      # fill in GEMINI_API_KEY, POSTGRES_PASSWORD, JWT_SECRET_KEY
docker compose up --build
```

- Backend API: http://localhost:8000
- Frontend:    http://localhost:5173
- PostgreSQL:  localhost:5432

### Running backend locally (without Docker)

```bash
cd rag_application/backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Running frontend locally

```bash
cd rag_application/frontend
pnpm install
pnpm dev
```

---

## Demo accounts

Three demo accounts are seeded on first startup:

| Email                  | Password   | Use case                      |
|------------------------|------------|-------------------------------|
| `avocatura@demo.com`   | `demo1234` | Law firm (legal documents)    |
| `restaurant@demo.com`  | `demo1234` | Restaurant (menus, nutrition) |
| `admin@demo.com`       | `demo1234` | General testing               |

Each user has an isolated ChromaDB collection — documents are never visible across accounts.

---

## Architecture

**Ingestion pipeline:** PDF → PyMuPDF text extraction → chunking (~500 tokens) → Gemini Embeddings → vectors + metadata stored in ChromaDB per user.

**Query pipeline:** user question → embed query → ChromaDB similarity search (top-5) → context + question → Gemini LLM → answer with source citations (filename + page).

---

## License

Academic work for UBB Cluj-Napoca, 2025-2026.
