# Mini-P7 — CPM Scheduler  ·  Phase 2

A desktop Critical Path Method (CPM) scheduler built with Python + PySide6.

---

## What's new in Phase 2

| Area | Feature |
|---|---|
| **Project Settings** | Set project name and start date; displayed in the title bar |
| **Export → Excel** | Formatted `.xlsx` with CPM columns, critical-path highlighting, summary sheet, optional date columns |
| **Export → PDF** | Landscape A4 report via `reportlab`; critical rows highlighted in red |
| **Import P6 XML** | Read Primavera P6 XML activity/relationship files (FS relationships only) |
| **Export P6 XML** | Write a P6-compatible XML for round-tripping to Primavera |
| **Resource Loading tab** | Horizontal Gantt bars per resource; over-allocation highlighted in orange |
| **Free Float column (FF)** | Correctly computed by the scheduler and shown in the table |
| **Resource column** | Resource field visible in the activity table |

---

## Install

```bash
pip install -r requirements.txt
```

> Requires Python 3.11+

Phase 2 adds two new dependencies (already in `requirements.txt`):
```
openpyxl>=3.1.0    # Excel export
reportlab>=4.0.0   # PDF export
```

---

## Run

```bash
python main.py
```

---

## How to Use

### Basic workflow
1. Click **Load Sample Project** to load the demo dataset
2. Click **▶ Schedule** to run the CPM engine
3. The table fills with ES / EF / LS / LF / TF / FF values
4. The **Gantt Chart** tab renders — red bars = critical path
5. Switch to **Resource Loading** to see per-resource workload

### Project Settings
- Menu **File → Project Settings** (`Ctrl+,`)
- Set a project name and start date
- Once a start date is set, Excel/PDF exports include real date columns

### Keyboard shortcuts

| Action | Shortcut |
|---|---|
| New Project | `Ctrl+N` |
| Project Settings | `Ctrl+,` |
| Import P6 XML | `Ctrl+I` |
| Add Activity | `Ctrl+A` |
| Schedule (CPM) | `F5` |
| Export to Excel | `Ctrl+E` |
| Export to PDF | `Ctrl+P` |

---

## Project Structure

```
mini_p7/
├── main.py                     ← Entry point
├── activity.py                 ← Activity dataclass (CPM fields)
├── scheduler.py                ← CPM engine (forward/backward pass + free float)
├── models.py                   ← SQLAlchemy ORM model
├── db.py                       ← CRUD operations (all bugs fixed)
├── main_window.py              ← Main application window (Phase 2)
├── activity_table.py           ← Activity grid (+ Resource + FF columns)
├── gantt_view.py               ← Gantt chart (QGraphicsView)
├── activity_dialog.py          ← Add/Edit activity dialog
├── status_panel.py             ← Bottom status bar
├── resource_panel.py           ← [NEW] Resource loading chart
├── project_settings_dialog.py  ← [NEW] Project name + start date dialog
├── export_manager.py           ← [NEW] Excel + PDF export
├── p6_xml.py                   ← [NEW] P6 XML import/export
└── requirements.txt
```

---

## Sample Data

| ID | Name       | Dur | Predecessor | Resource |
|----|------------|-----|-------------|----------|
| A  | Start      | 2   | —           | —        |
| B  | Foundation | 4   | A           | —        |
| C  | Structure  | 6   | B           | —        |
| D  | Electrical | 3   | B           | Electrical Team |
| E  | Finish     | 2   | C, D        | —        |

**Critical path:** A → B → C → E  (14 days)  
**D** has TF = 5, FF = 5

---

## CPM Terminology

| Term | Formula | Meaning |
|---|---|---|
| ES | max(pred EF) | Earliest the activity can start |
| EF | ES + Duration | Earliest it can finish |
| LS | LF − Duration | Latest it can start without delay |
| LF | min(succ LS) | Latest it must finish |
| TF | LS − ES | Total Float — slack before delaying project |
| FF | min(succ ES) − EF | Free Float — slack before delaying any successor |
| Critical | TF == 0 | On the critical path |

---

## Phase 3 Ideas

- WBS tree panel (hierarchical activity grouping)
- Working-day calendar (skip weekends / holidays)
- Resource levelling / smoothing
- Baseline vs. actual comparison
- SS, FF, SF relationship types with lag
- P6 XER format import
