# OKF Knowledge Wiki Implementation Plan

**Goal:** Build a local, self-owned OKF v0.1 knowledge base with a PostgreSQL/pgvector-backed API and a React/Vite visual knowledge browser.

**Architecture:** OKF Markdown under `data/wiki/` remains the source of truth. FastAPI validates and writes OKF concepts, maintains a PostgreSQL catalog/graph projection, and exposes browse/search/ingest APIs. React/Vite consumes the API and renders a Tencent-like workspace with navigation, concept cards, document detail, and an interactive link graph.

**Tech stack:** FastAPI, PostgreSQL + pgvector, Docker Compose, React, Vite, TypeScript, Cytoscape.js, Vitest, pytest.

## Scope
1. Enforce core OKF v0.1 properties: YAML frontmatter, required `type`, `index.md`/`log.md`, Markdown concept links.
2. Persist a database projection and create the pgvector extension; use reliable lexical search in v1. Semantic embeddings remain a separately pluggable stage because no embedding provider is being selected in this build.
3. Provide a polished local UI at `http://localhost:5173`, including graph visualization and a manual ingest panel.
4. Add tests before implementation and validate the live stack.

## Build sequence
1. Create the Compose, API, and web project skeleton.
2. Write failing parser/index tests; implement OKF parsing and writing.
3. Write failing API tests; implement health, documents, graph, and ingest endpoints.
4. Write frontend component tests; implement the workspace UI and graph browser.
5. Build containers, run test suites, bring up the stack, ingest a sample concept, and validate the UI/API.

## Key files
- `docker-compose.yml`
- `server/app/okf.py`, `server/app/main.py`, `server/tests/`
- `web/src/App.tsx`, `web/src/api.ts`, `web/src/App.test.tsx`
- `data/wiki/`

## Validation
- `docker compose run --rm api pytest -q`
- `docker compose run --rm web npm test -- --run`
- `curl http://localhost:8000/api/health`
- Browser inspection of `http://localhost:5173`
