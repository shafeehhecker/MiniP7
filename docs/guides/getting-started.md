# Getting started

> Category: **Tutorial**. Learning-oriented. By the end you will have run the
> scheduling engine and seen a critical path computed.

This walks you through the one piece that already works end-to-end: the `engine`
and `schema` packages.

## 1. Clone and enter the repo

```bash
git clone <repo-url> minip7
cd minip7
```

## 2. Run the engine on the sample network

The engine is pure Python and depends only on `schema`. From the repo root:

```bash
python -c "
import sys; sys.path.insert(0, 'packages/schema/src'); sys.path.insert(0, 'packages/engine/src')
from schema import Activity
from engine import CPMScheduler
acts = {a.id: a for a in [
    Activity('A','Start',2,()),
    Activity('B','Foundation',4,('A',)),
    Activity('C','Structure',6,('B',)),
    Activity('D','Electrical',3,('B',)),
    Activity('E','Finish',2,('C','D')),
]}
s = CPMScheduler(acts); s.schedule()
print('duration:', s.project_duration())
print('critical path:', s.get_critical_path())
"
```

You should see a duration of 14 and the critical path `['A', 'B', 'C', 'E']`. To
understand *why*, read [how CPM works](../domain/cpm.md).

## 3. Run the engine's tests

```bash
pytest packages/engine/tests
```

## Where to go next

- Understand the architecture: [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
- Learn the domain language: [glossary](../domain/glossary.md)
- See the plan: [ROADMAP.md](../ROADMAP.md)
