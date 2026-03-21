# Mini-P7 — CPM Scheduler

A desktop Critical Path Method (CPM) scheduler built with **Python + PySide6**.  

---

## Features

### Phase 1 — Core CPM Engine
- **CPM Engine** — Forward pass, backward pass, Total Float, Free Float, critical path identification
- **Activity Table** — P6-style grid with ID, Name, Duration, Predecessors, ES, EF, LS, LF, Float columns
- **Gantt Chart** — Auto-rendered from CPM results; critical path highlighted in red, float bars in grey
- **SQLite persistence** — Activities saved automatically between sessions via SQLAlchemy
- **Add / Edit / Delete** activities via a validated modal dialog
- **Load Sample Project** — 5-activity demo network with a real critical path

### Phase 2 — Scheduling Intelligence
- **WBS Tree Panel** — Collapsible Work Breakdown Structure tree; add/edit/delete nodes; click any node to filter the activity table and Gantt to that branch
- **Date-Based Scheduling** — Project start date picker; CPM day-offsets converted to real calendar dates respecting work days and holidays; toggle between offset and calendar views on the Gantt
- **Multiple Calendars** — Create named work calendars with custom work-day patterns (Mon–Fri, 6-day, etc.), hours-per-day, and individual holiday exceptions; assign calendars per-activity or use the project default
- **Resource Management** — Define Labour / Material / Equipment resources with type, unit, max units, and cost-per-unit; assign resources with usage fractions to individual activities
- **Resource Loading Histogram** — Daily usage chart rendered per resource from assignment data; visible in the Resources tab
- **Activity Dialog — 3 tabs** — *Basic Info* (id, name, duration, predecessors, resource label, notes), *Scheduling* (WBS node + calendar override), *Resources* (assign resources with units)
- **Task Properties Panel** — Right-side collapsible detail panel; auto-updates when you click any row in the activity table
- **Export to Excel (.xlsx)** — Formatted schedule table with conditional formatting, auto-filter, frozen panes, Free Float column, Start/Finish Date columns, colour-coded Gantt grid sheet, and Resource Loading sheet
- **Export to PDF** — Landscape A4 report with styled table, critical path summary, and a vector Gantt chart drawing embedded directly in the document
- **P6 XML Import** — Import Primavera P6 XML files; parses activities, all four relationship types (FS/SS/FF/SF) with lag values
- **P6 XML Export** — Full export: activities with CPM dates, relationships with type + lag, WBS nodes, calendars with holidays, resources, and resource assignments
- **Enhanced CPM Engine** — Full support for FS / SS / FF / SF relationship types with positive and negative lag; Free Float correctly computed per relationship type
- **Enhanced Gantt** — Zoom in/out (toolbar buttons + Ctrl+scroll), dependency arrows with arrowheads (red on critical path), milestone diamonds for zero-duration activities, date-mode with month headers + weekend shading + Today marker line, Arrows toggle
- **Enhanced Activity Table** — Free Float (FF) column, Start Date / Finish Date columns, sortable column headers, right-click context menu, keyboard shortcuts (Del = delete, Enter = edit)

---

## Install

```bash
pip install -r requirements.txt
```

**`requirements.txt`**
```
PySide6>=6.5
SQLAlchemy>=2.0
openpyxl>=3.1
reportlab>=4.0
lxml>=4.9
```

> Requires **Python 3.11+**

---

## Run

```bash
python main.py
```

---

## How to Use

### Basic workflow
1. Click **Load Sample Project** to load the built-in 5-activity demo
2. Click **▶ Schedule** (or press **F5**) to run the CPM engine
3. The table fills with ES / EF / LS / LF / TF / FF values
4. The Gantt chart renders — **red bars = critical path**, grey bars = float
5. Use **+ Add** to create your own activities; double-click any row to edit

### Date-based scheduling
1. Set the **Project Start** date in the title bar
2. Run **▶ Schedule**
3. Toggle **Dates** in the Gantt toolbar to switch the timeline to calendar dates
4. Start Date and Finish Date columns populate automatically in the activity table

### WBS
1. Open the **WBS** tab in the left panel
2. Right-click to add root or child nodes; assign codes like `1.0`, `1.1`, `1.2`
3. Click a WBS node to filter the table and Gantt to only that branch
4. Click **⊘ Show All Activities** to clear the filter
5. Open any activity's **Edit** dialog → **Scheduling** tab to assign it to a WBS node

### Calendars
1. Open **Tools → Calendar Manager**
2. Create a calendar, check the work days, set hours/day
3. Click a date in the calendar widget and press **Add Holiday** to mark exceptions
4. Mark a calendar as **Default** — all activities use it unless overridden
5. Override per-activity via the **Scheduling** tab in the activity dialog

### Resources
1. Open the **Resources** tab in the left panel
2. Click **+ Add Resource** to define a Labour / Material / Equipment resource
3. Edit any activity → **Resources** tab → pick a resource and enter units → **+ Assign**
4. After scheduling, the **Resource Loading** histogram shows daily usage per resource

### Export
| Menu item | Output |
|---|---|
| File → Export to Excel | `.xlsx` with schedule table, Gantt grid, and resource loading sheet |
| File → Export to PDF | Landscape A4 with formatted table and embedded Gantt drawing |
| File → Export to P6 XML | Full Primavera-compatible XML (activities, relationships, WBS, calendars, resources) |
| File → Import P6 XML | Import a P6 XML file; replaces the current project |

### Keyboard shortcuts
| Key | Action |
|---|---|
| F5 | Run CPM Schedule |
| Ctrl+A | Add Activity |
| Ctrl+I | Import P6 XML |
| Ctrl+E | Export to Excel |
| Ctrl+P | Export to PDF |
| Ctrl+N | New Project |
| Del | Delete selected activity |
| Enter | Edit selected activity |
| Ctrl+Scroll | Zoom Gantt horizontally |

---

## Project Structure

```
mini_p6/
├── main.py                  ← Entry point, app bootstrap, splash screen
├── activity.py              ← Activity dataclass with CPM fields
├── scheduler.py             ← CPM engine: forward/backward pass, FS/SS/FF/SF + lag
├── calendar_engine.py       ← Work-calendar date arithmetic
├── models.py                ← SQLAlchemy ORM: Activity, WBSNode, Calendar,
│                                CalendarException, Resource, ResourceAssignment
├── db.py                    ← CRUD for all models; default calendar bootstrap
├── main_window.py           ← Main application window + all menu/toolbar wiring
├── activity_table.py        ← Activity grid widget (sortable, context menu)
├── activity_dialog.py       ← Add/Edit dialog (3-tab: Basic / Scheduling / Resources)
├── gantt_view.py            ← Gantt chart (zoom, arrows, milestones, date mode)
├── wbs_panel.py             ← WBS tree panel with drag-and-drop and filter signal
├── calendar_dialog.py       ← Calendar manager dialog (work days, holidays)
├── resource_panel.py        ← Resource list + daily loading histogram
├── task_properties.py       ← Collapsible detail panel for selected activity
├── exporter.py              ← Excel and PDF export
├── p6_xml.py                ← Primavera P6 XML import and export
├── status_panel.py          ← Bottom status bar
└── simple_activity_table.py ← Lightweight table (used internally)
```

---

## Sample Data

| ID | Name       | Dur | Predecessor | ES | EF | LS | LF | TF | FF | Critical |
|----|------------|-----|-------------|----|----|----|----|----|----|----------|
| A  | Start      | 2   | —           | 0  | 2  | 0  | 2  | 0  | 0  | ★        |
| B  | Foundation | 4   | A           | 2  | 6  | 2  | 6  | 0  | 0  | ★        |
| C  | Structure  | 6   | B           | 6  | 12 | 6  | 12 | 0  | 0  | ★        |
| D  | Electrical | 3   | B           | 6  | 9  | 9  | 12 | 3  | 3  | —        |
| E  | Finish     | 2   | C, D        | 12 | 14 | 12 | 14 | 0  | 0  | ★        |

**Critical path:** A → B → C → E  
**Project duration:** 14 days  
**Activity D:** 3 days of total float and free float — can slip without affecting E

---

## CPM Relationship Types

The Phase 2 scheduler supports all four P6 relationship types, each with an optional lag (positive = delay, negative = lead):

| Type | Meaning | Constraint |
|---|---|---|
| **FS** | Finish-to-Start *(default)* | `succ.ES ≥ pred.EF + lag` |
| **SS** | Start-to-Start | `succ.ES ≥ pred.ES + lag` |
| **FF** | Finish-to-Finish | `succ.EF ≥ pred.EF + lag` |
| **SF** | Start-to-Finish *(rare)* | `succ.EF ≥ pred.ES + lag` |

```python
from scheduler import CPMScheduler, Relationship
from activity import Activity

activities = {
    "Excavate":  Activity("Excavate",  "Excavate",  5, []),
    "Backfill":  Activity("Backfill",  "Backfill",  3, []),
}
relationships = [
    Relationship("Excavate", "Backfill", rel_type="SS", lag=2),
]
CPMScheduler(activities, relationships).schedule()
```

---

