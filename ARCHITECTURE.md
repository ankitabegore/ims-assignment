# IMS Architecture

## Components Overview
1. **Ingestion API**: FastAPI endpoint using `slowapi` for rate limiting to drop malicious or runaway alert loops early.
2. **Backpressure Queue**: Uses `asyncio.Queue` (size 10,000) to ensure the API never blocks waiting for the database, preventing cascading timeouts to upstream systems.
3. **Debouncer Engine**: Tumbling 10s window groups signals by `component_id`. This massively reduces I/O pressure on the database during an outage.
4. **State Machine**: Enforces the workflow logic for incident management. A strict guard prevents closure of an incident without a filled RCA.
5. **Multi-DB Storage Layer**:
    - MongoDB: Scales horizontally for high-throughput raw signal writes.
    - PostgreSQL: Handles ACID transactions for structured state updates and RCA integrity.
    - Redis: Offloads pub/sub operations for real-time LiveFeed updates, preventing database polling.
    - TimescaleDB: Optimizes storage and query speed for time-series metrics.
6. **React Frontend**: Connects via Server-Sent Events (SSE) to update state efficiently without long-polling overhead.

## Data Flow
`Client -> POST /signals -> Rate Limiter -> In-Memory Queue -> Background Worker Loop -> Debouncer (10s Wait) -> Persistence (4 DBs) -> Redis Pub/Sub -> SSE -> React UI`
