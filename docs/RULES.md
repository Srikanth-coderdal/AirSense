# Project Rules & Guidelines

## 1. Technology Stack
- **Backend:** Python FastAPI
- **Frontend:** React
- **Database:** PostgreSQL with TimescaleDB & PostGIS extensions

## 2. Naming Conventions
- **Python / SQL:** `snake_case` for variables, functions, module names, table names, and column names.
- **JavaScript / TypeScript:** `camelCase` for variables, functions, and properties; `PascalCase` for React components.

## 3. Directory Structure
- `/backend`: FastAPI application, endpoints, models, business logic.
- `/frontend`: React frontend application.
- `/ingestion`: Data ingestion pipelines and background workers.
- `/db`: Database schemas, migrations, seed scripts, and configuration.
- `/docs`: Project documentation, architectural diagrams, and guidelines.

## 4. Security & Environment
- Never hardcode secrets, API keys, credentials, or sensitive configuration values.
- Exclusively use `.env` files and environment variables for secret management and configuration.

## 5. Agent Workflow & Safety
- Always ask for my explicit confirmation before running destructive
  commands (rm, drop, prune, truncate, git reset --hard, etc.).
- Work on one phase at a time. Do not build features outside the
  current task.
- Show an implementation plan and wait for approval before writing code.
## 6. Environment & Tooling
- Python 3.11+, Node 20+, JavaScript (not TypeScript).
- All services run through Docker Compose.
- Use the timescale/timescaledb-ha image for the database.
- Always provide a .env.example and keep .env in .gitignore.

## 7. Code Style
- Use simple, descriptive variable names.
- Keep functions short, with a one-line comment explaining each.

## 8. Honesty & Verification
- Never use fake or mock data unless I ask. If a real API call fails,
  say so instead of silently substituting data.
- Never claim something works unless you ran it. Show the raw
  command output as proof.
- List every file you created or changed at the end of each task.
