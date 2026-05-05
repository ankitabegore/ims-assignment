
 # Incident Management System (IMS)

This is an internal incident management platform built for Zeotap. It ingests massive amounts of signals from failing infrastructure components, debounces them into actionable work items, and manages their lifecycle through a state machine requiring Root Cause Analysis (RCA) before closure.

## Features & Architecture Highlights

- **High Concurrency Ingestion**: Rate-limited (1000/sec) FastAPI endpoint pushing directly to an in-memory `asyncio.Queue` acting as a backpressure buffer. System absorbs spikes gracefully without crashing or dropping signals.
- **Debounce Engine**: A tumbling window algorithm (10s) groups raw signals by `component_id` so the database is not overwhelmed by cascading alerts.
- **Strict Separation of Concerns (4 Databases)**:
  - **MongoDB**: Append-only audit log for every single raw signal payload.
  - **PostgreSQL**: Transactional storage for structured `WorkItem` entities and `RCA` records.
  - **Redis**: Real-time pub/sub engine powering the Server-Sent Events (SSE) live feed.
  - **TimescaleDB**: High-performance timeseries storage for calculating MTTR and incident metrics.
- **Strict LLD Patterns**:
  - **State Pattern**: Work items follow a strict FSM (`OPEN` → `INVESTIGATING` → `RESOLVED` → `CLOSED`). Transitioning to `CLOSED` strictly enforces the presence of an RCA payload.
  - **Strategy Pattern**: Alerts are routed via P0-P3 strategies (e.g., paging on-call vs. logging).
- **Resilience**: Database operations are wrapped with exponential backoff retries using `tenacity`.
- **Live React Dashboard**: The frontend consumes an SSE stream (`/stream`) to instantly display new incidents and status updates without polling.
- **Bonus Feature**: Mock LLM RCA Suggester endpoint uses simple heuristics to generate a synthetic Anthropic-like RCA suggestion for quick resolution.

## Quickstart

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d postgres mongo redis
   ```
2. **Start Backend** (From `backend/` directory):
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
3. **Start Frontend** (From `frontend/` directory):
   ```bash
   npm install
   npm run dev
   ```

## Testing Load and Backpressure

Run the included load generator script to blast the ingestion API and observe the debounce engine and backpressure queue handling the cascading failure:
```bash
python scripts/mock_signals.py
```
Watch the live React dashboard to see the incidents group and update dynamically.

## Testing Core Logic
```bash
cd backend
pytest tests/
```
