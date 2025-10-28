# Autonomous Platform Architecture

This document outlines the default layout for the autonomous application. The
structure is intentionally modular so that new capabilities can be added with
minimal friction.

## High-Level Components

- **Backend API (`backend/`)** — Exposes core automation capabilities over HTTP
  using FastAPI. The API now includes the `TrendingService` which aggregates
  viral content from multiple free providers, keeps a rolling cache, and exposes
  `/trending` plus `/trending/sources` endpoints.
- **Automation Routines (`automation/`)** — Hosts long-running jobs and
  background monitors that enable self-healing behaviour. The
  `TrendingServiceMonitor` can trigger cache refreshes when a provider becomes
  unhealthy.
- **Interface Layer (`frontend/` or other clients)** — Web, mobile, or CLI
  clients that consume the API. The repository provides hooks for plugging in a
  web frontend or any other interface.
- **Infrastructure (`infra/`)** — Containerisation, IaC, and deployment scripts
  for cloud or edge environments. The default `docker-compose.yaml` covers local
  development.
- **Documentation (`docs/`)** — Architectural decisions, onboarding guides, and
  API references live here.

## Suggested Workflow

1. Extend the FastAPI routers with new feature endpoints under
   `backend/app/routers/`. New adapters can register with the `TrendingService`
   by implementing the `TrendingSource` interface.
2. Add automation routines that call internal services or external APIs under
   `automation/`. Pair them with monitors like `TrendingServiceMonitor` for
   autonomous recovery.
3. Wire background jobs to the API using a scheduler (e.g. Celery, APScheduler)
   once requirements are known.
4. Describe new capabilities in `docs/` and keep the top-level `README.md`
   updated.

## Next Steps

- Define persistent storage (PostgreSQL, MongoDB, or other) inside `infra/` and
  expose repositories/services within the backend.
- Implement authentication in the API to support multi-tenant access.
- Add monitoring/observability tooling (OpenTelemetry, Prometheus) for deep
  insights into self-healing performance.
- Persist snapshots of trending data for analytics and recommendation engines.
