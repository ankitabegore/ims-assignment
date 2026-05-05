# PROMPTS & Planning Notes

This project was built iteratively. Below are the key planning thoughts and system architecture decisions made during development:

1. **Phase 1 (Foundation)**: We needed 4 distinct databases. TimescaleDB was chosen as the `postgres` image since it functions seamlessly as standard PostgreSQL while supporting hyper-tables natively.
2. **Phase 2 (Ingestion & Backpressure)**: The most critical part of this phase was to *never block the API response*. By immediately pushing to an `asyncio.Queue` of size 10,000, we created a massive buffer that can absorb API spikes without failing requests or holding connections.
3. **Phase 3 (Debounce & State)**: 
   - *Debouncing*: We used a 10s tumbling window grouped by `component_id`. This effectively turns 100 duplicate signals into 1 database write, drastically reducing I/O. 
   - *State Machine*: Built using the State Pattern, explicitly preventing transitioning to CLOSED if an RCA is missing, raising a custom `RCAMissingError`.
4. **Phase 4 (API & Frontend)**: To eliminate constant database polling from the dashboard, we used Redis Pub/Sub combined with Server-Sent Events (SSE). When a new incident is logged or updated, Redis pushes the event to all connected clients instantly.
5. **Phase 5 (Polish)**: Added the AI suggester as a mock endpoint, built Pytest validation scripts, and created a `mock_signals.py` script to simulate an RDBMS cascade failure.
