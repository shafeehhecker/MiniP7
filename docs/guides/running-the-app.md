# How to run the app

> Category: **How-to guide**. Launches the full backend + browser UI.

The backend vertical (schema → engine → persistence → services → API) plus a
zero-build browser UI run together with one command. No Node, no build step.

## 1. Install backend dependencies

```bash
pip install -r requirements.txt
```

## 2. Launch

```bash
./run.sh           # macOS / Linux
run.bat            # Windows
```

Then open **http://127.0.0.1:8000** — press "Load sample", then "Schedule".
You will see the KPI cards, the schedule table (critical path in red), and a
Gantt chart, all served from the live CPM engine.

## 3. Explore the API

- Interactive API docs (Swagger UI): **http://127.0.0.1:8000/docs**
- The OpenAPI contract (used to generate the typed client in Phase 4):
  **http://127.0.0.1:8000/openapi.json**

## 4. Run the tests

```bash
PYTHONPATH=packages/schema/src:packages/engine/src:packages/persistence/src:packages/services/src \
  python -m pytest packages/engine/tests packages/services/tests
```
