# Zeotap Infrastructure / SRE Intern Assignment
**Project Name:** Incident Management System (IMS)
**Candidate Name:** [Your Full Name Here]
**GitHub Repository:** [Insert Link to your GitHub Repo here]

---

## 1. Project Overview

This project is a high-concurrency, full-stack incident management platform built to ingest massive amounts of signals from failing infrastructure components. It debounces noisy alerts into actionable work items, and manages their lifecycle through a strict state machine requiring Root Cause Analysis (RCA) before closure. 

The application is built with a **FastAPI** backend and a **React** frontend, employing a highly decoupled architecture that ensures resilience under heavy load.

---

## 2. Architecture & Design Patterns

### High Concurrency & Backpressure
The system is designed to handle cascading failures without crashing. The ingestion API pushes incoming signals directly into an in-memory `asyncio.Queue`. This acts as a backpressure buffer, allowing the API to immediately return a `202 Accepted` response while workers process the queue asynchronously.

### Debounce Engine
To prevent the database from being overwhelmed during an infrastructure outage, the system uses a tumbling window algorithm (10s) that groups raw signals by `component_id`. Multiple signals for the same component within the time window are aggregated into a single Work Item.

### Strict Separation of Concerns (4 Databases)
The application employs polyglot persistence to optimize for different data access patterns:
- **MongoDB:** Serves as an append-only audit log, reliably storing every single raw signal payload for compliance and historical replay.
- **PostgreSQL:** Provides transactional ACID storage for structured `WorkItem` entities, state transitions, and `RCA` records.
- **Redis:** Acts as a real-time Pub/Sub message broker, powering the Server-Sent Events (SSE) live feed to the frontend.
- **TimescaleDB:** High-performance timeseries storage optimized for calculating MTTR (Mean Time To Resolution) and querying historical incident metrics.

### Strict LLD Patterns
- **State Pattern:** Work items follow a strict Finite State Machine (FSM): `OPEN` → `INVESTIGATING` → `RESOLVED` → `CLOSED`. Transitioning to the `CLOSED` state is strictly prohibited unless a valid RCA payload is attached.
- **Strategy Pattern:** Alerts are routed via P0-P3 strategies (e.g., P0 triggers immediate critical logging/paging, while P3 is merely logged).

---

## 3. Non-Functional Requirements & Bonus Achievements

- **Resilience & Fault Tolerance:** Database operations are wrapped with exponential backoff retries using the `tenacity` library. Transient database connection issues will not crash the application or drop signals in the queue.
- **Security & Rate Limiting:** The API is protected by `slowapi` rate limiters (e.g., 1000 requests/sec limit on ingestion) to prevent DDoS attacks and API abuse. Cross-Origin Resource Sharing (CORS) is configured to restrict unauthorized domain access.
- **Bonus Feature - GenAI RCA Suggester:** A mock LLM RCA Suggester endpoint uses heuristics to generate a synthetic Anthropic-like RCA suggestion, accelerating the incident resolution workflow for engineers.
- **Live React Dashboard:** The frontend consumes an SSE stream (`/stream`) to instantly display new incidents and status updates. This eliminates the need for aggressive client-side polling, drastically reducing backend load.

---

## 4. Setup, Packaging, & Execution

The project is fully packaged and orchestrated. 

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 18+

### Running the Application

1. **Start Infrastructure Services:**
   ```bash
   docker-compose up -d postgres mongo redis
   ```
2. **Start the Backend API:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
3. **Start the Frontend Dashboard:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Testing & Validation

The application includes automated tests and load generation scripts to validate the architecture.

- **Load Testing (Backpressure & Debounce):**
  A bundled script blasts the ingestion API to simulate a cascading failure. You can observe the debounce engine grouping alerts and the queue absorbing the spike.
  ```bash
  python scripts/mock_signals.py
  ```
- **Automated Tests:**
  Core state machine logic and endpoints are tested via `pytest`.
  ```bash
  cd backend
  pytest tests/
  ```

---
*Please refer to the GitHub repository for the full source code, commit history, and detailed README.*
