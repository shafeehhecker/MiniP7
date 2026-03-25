"""
Main Window for Mini-P7 CPM Scheduler – Phase 2.

Layout:
  ┌─────────────────────────────────────────────────────┐
  │  Menu bar (File / Edit / Export / Help)             │
  ├─────────────────────────────────────────────────────┤
  │  Title bar                                          │
  ├─────────────────────────────────────────────────────┤
  │  Toolbar                                            │
  ├──────────────────────┬──────────────────────────────┤
  │   Activity Table     │  Tab: Gantt | Resource       │
  │   (left 42%)         │  (right 58%)                 │
  ├──────────────────────┴──────────────────────────────┤
  │  Status Panel                                       │
  └─────────────────────────────────────────────────────┘

Phase 2 additions
-----------------
  * File → Project Settings  (name + start date)
  * File → Import P6 XML
  * Export → Excel / PDF / P6 XML
  * Resource Loading tab alongside Gantt
  * Free Float column in activity table
  * All Phase 1 bugs fixed
"""

from __future__ import annotations

import os
from datetime import date
from typing import Dict, Optional

from activity import Activity
from activity_dialog import ActivityDialog
from activity_table import ActivityTable
from db import delete_activity, init_db, load_all_activities, save_activity, save_all_activities
from gantt_view import GanttView
from project_settings_dialog import ProjectSettingsDialog
from resource_panel import ResourcePanel
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QSplitter,
    QTabWidget, QVBoxLayout, QWidget,
)
from scheduler import CPMScheduler, SchedulerError
from status_panel import StatusPanel

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
SAMPLE_ACTIVITIES = [
    Activity("A", "Start",      2, ()),
    Activity("B", "Foundation", 4, ("A",)),
    Activity("C", "Structure",  6, ("B",)),
    Activity("D", "Electrical", 3, ("B",), resource="Electrical Team"),
    Activity("E", "Finish",     2, ("C", "D")),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._activities: Dict[str, Activity] = {}
        self._project_name: str = "My Project"
        self._start_date: Optional[date] = None
        self._calendar_type: str = "Mon-Fri"

        init_db()
        self._settings = QSettings("OpenPlan", "Mini-P7")
        self.restoreGeometry(self._settings.value("geometry", b""))

        self._setup_window()
        self._setup_ui()
        self._load_from_db()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self):
        self.setWindowTitle("Mini-P7  |  CPM Scheduler  |  Phase 2")
        self.setMinimumSize(1100, 680)
        self.resize(1440, 820)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._create_menu_bar()
        root.addWidget(self._build_titlebar())
        root.addWidget(self._build_toolbar())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #c0c0c0; width: 2px; }"
        )

        self.activity_table = ActivityTable()
        self.activity_table.add_requested.connect(self._on_add_activity)
        self.activity_table.edit_requested.connect(self._on_edit_activity)
        self.activity_table.delete_requested.connect(self._on_delete_activity)

        # Right side: tabbed view
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #f8f8f8; }
            QTabBar::tab {
                background-color: #e8e8e8; color: #505050;
                padding: 6px 18px; border: 1px solid #c0c0c0;
                border-bottom: none; font-size: 11px; font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #f8f8f8; color: #1e5c8a;
                border-bottom: 2px solid #3a7ca5;
            }
            QTabBar::tab:hover { background-color: #d8e8f0; }
        """)

        self.gantt_view = GanttView()
        self.resource_panel = ResourcePanel()
        self._tabs.addTab(self.gantt_view,     "Gantt Chart")
        self._tabs.addTab(self.resource_panel, "Resource Loading")

        splitter.addWidget(self.activity_table)
        splitter.addWidget(self._tabs)
        splitter.setSizes([500, 940])
        root.addWidget(splitter)

        self.status_panel = StatusPanel()
        root.addWidget(self.status_panel)

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------

    def _create_menu_bar(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")

        act = QAction("&New Project", self)
        act.setShortcut(QKeySequence.New)
        act.triggered.connect(self._clear_all)
        file_menu.addAction(act)

        act = QAction("&Project Settings…", self)
        act.setShortcut(QKeySequence("Ctrl+,"))
        act.triggered.connect(self._show_project_settings)
        file_menu.addAction(act)

        file_menu.addSeparator()

        act = QAction("&Load Sample Project", self)
        act.triggered.connect(self._load_sample)
        file_menu.addAction(act)

        act = QAction("&Import P6 XML…", self)
        act.setShortcut(QKeySequence("Ctrl+I"))
        act.triggered.connect(self._import_p6_xml)
        file_menu.addAction(act)

        file_menu.addSeparator()

        act = QAction("E&xit", self)
        act.setShortcut(QKeySequence.Quit)
        act.triggered.connect(self.close)
        file_menu.addAction(act)

        # Edit
        edit_menu = mb.addMenu("&Edit")

        act = QAction("&Add Activity", self)
        act.setShortcut(QKeySequence("Ctrl+A"))
        act.triggered.connect(self._on_add_activity)
        edit_menu.addAction(act)

        act = QAction("&Schedule  (CPM)", self)
        act.setShortcut(QKeySequence("F5"))
        act.triggered.connect(self._run_schedule)
        edit_menu.addAction(act)

        # Export
        export_menu = mb.addMenu("&Export")

        act = QAction("Export to &Excel (.xlsx)…", self)
        act.setShortcut(QKeySequence("Ctrl+E"))
        act.triggered.connect(self._export_excel)
        export_menu.addAction(act)

        act = QAction("Export to &PDF…", self)
        act.setShortcut(QKeySequence("Ctrl+P"))
        act.triggered.connect(self._export_pdf)
        export_menu.addAction(act)

        export_menu.addSeparator()

        act = QAction("Export P6 &XML…", self)
        act.triggered.connect(self._export_p6_xml)
        export_menu.addAction(act)

        # Help
        help_menu = mb.addMenu("&Help")
        act = QAction("&About", self)
        act.triggered.connect(self._show_about)
        help_menu.addAction(act)

    # ------------------------------------------------------------------
    # Title bar & Toolbar
    # ------------------------------------------------------------------

    def _build_titlebar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(
            "QFrame { background-color: #e0e0e0; border-bottom: 2px solid #a0a0a0; }"
        )
        bar.setFixedHeight(46)
        row = QHBoxLayout(bar)
        row.setContentsMargins(16, 0, 16, 0)

        logo = QLabel("◈")
        logo.setStyleSheet("color: #2a7ab0; font-size: 20px;")
        row.addWidget(logo)

        title = QLabel("Mini-P7")
        title.setStyleSheet(
            "color: #202020; font-size: 18px; font-weight: bold;"
            " letter-spacing: 1px; margin-left: 6px;"
        )
        row.addWidget(title)

        sub = QLabel("CPM Scheduler  ·  Phase 2")
        sub.setStyleSheet(
            "color: #505050; font-size: 12px; margin-left: 4px; margin-top: 4px;"
        )
        row.addWidget(sub)

        row.addStretch()

        self._project_label = QLabel("Project: My Project")
        self._project_label.setStyleSheet(
            "color: #1e5c8a; font-size: 11px; font-weight: bold;"
        )
        row.addWidget(self._project_label)

        row.addWidget(QLabel("  ·  "))

        self._date_label = QLabel("No start date set")
        self._date_label.setStyleSheet("color: #606060; font-size: 11px;")
        row.addWidget(self._date_label)

        row.addWidget(QLabel("  ·  "))

        hint = QLabel("Double-click row to edit  ·  F5 to schedule")
        hint.setStyleSheet("color: #606060; font-size: 11px;")
        row.addWidget(hint)

        return bar

    def _build_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame { background-color: #f0f0f0; border-bottom: 1px solid #b0b0b0; }
            QPushButton {
                background-color: #ffffff; color: #202020;
                border: 1px solid #b0b0b0; border-radius: 4px;
                padding: 6px 14px; font-size: 12px; min-width: 70px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton#scheduleBtn {
                background-color: #2a7ab0; color: #ffffff;
                border: 1px solid #1e5a8a; font-weight: bold;
                font-size: 13px; padding: 6px 22px;
            }
            QPushButton#scheduleBtn:hover { background-color: #1e6aa0; }
            QPushButton#clearBtn:hover {
                background-color: #f0d0d0; color: #a00000; border-color: #c06060;
            }
            QPushButton#exportBtn {
                background-color: #f0f8f0; color: #2a7a2a; border: 1px solid #80b080;
            }
            QPushButton#exportBtn:hover { background-color: #d8f0d8; }
            QPushButton#settingsBtn {
                background-color: #f8f4e8; color: #7a6020; border: 1px solid #c0a840;
            }
            QPushButton#settingsBtn:hover { background-color: #f0e8c0; }
        """)
        bar.setFixedHeight(48)
        row = QHBoxLayout(bar)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(8)

        def btn(label, slot, obj_name=None, tip=None):
            b = QPushButton(label)
            if obj_name:
                b.setObjectName(obj_name)
            if tip:
                b.setToolTip(tip)
            b.clicked.connect(slot)
            row.addWidget(b)
            return b

        btn("Load Sample",        self._load_sample,          tip="Load built-in sample project")
        btn("Clear All",          self._clear_all,  "clearBtn", tip="Delete all activities")
        btn("Import P6 XML",      self._import_p6_xml,        tip="Import from Primavera P6 XML")
        btn("Project Settings",   self._show_project_settings, "settingsBtn",
            tip="Set project name and start date (Ctrl+,)")

        row.addStretch()

        btn("Excel",  self._export_excel,   "exportBtn", tip="Export to Excel (Ctrl+E)")
        btn("PDF",    self._export_pdf,     "exportBtn", tip="Export to PDF (Ctrl+P)")
        btn("P6 XML", self._export_p6_xml,  "exportBtn", tip="Export to Primavera P6 XML")

        row.addSpacing(12)

        schedule_btn = QPushButton(" ▶  Schedule")
        schedule_btn.setObjectName("scheduleBtn")
        schedule_btn.setToolTip("Run CPM forward/backward pass (F5)")
        schedule_btn.clicked.connect(self._run_schedule)
        row.addWidget(schedule_btn)

        return bar

    # ------------------------------------------------------------------
    # Data loading / saving
    # ------------------------------------------------------------------

    def _load_from_db(self):
        self._activities = load_all_activities()
        self._refresh_ui()
        if self._activities:
            self.status_panel.set_message(
                f"Loaded {len(self._activities)} activit(ies) from database."
            )

    def _refresh_ui(self):
        self.activity_table.populate(self._activities)
        self.gantt_view.render_gantt(self._activities)
        self.resource_panel.render_resources(self._activities)
        self._project_label.setText(f"Project: {self._project_name}")
        self._date_label.setText(
            self._start_date.strftime("Start: %d %b %Y")
            if self._start_date else "No start date set"
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _show_project_settings(self):
        dlg = ProjectSettingsDialog(
            parent=self,
            project_name=self._project_name,
            start_date=self._start_date,
            calendar_type=self._calendar_type,
        )
        if dlg.exec():
            self._project_name  = dlg.project_name
            self._start_date    = dlg.start_date
            self._calendar_type = dlg.calendar_type
            self._refresh_ui()
            self.status_panel.set_message(
                f"Project settings saved.  "
                f"Start: {self._start_date.strftime('%d %b %Y')}"
            )

    def _load_sample(self):
        reply = QMessageBox.question(
            self, "Load Sample",
            "This will replace the current project with sample data.\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        for act_id in list(self._activities.keys()):
            delete_activity(act_id)
        self._activities.clear()

        for act in SAMPLE_ACTIVITIES:
            a = Activity(act.id, act.name, act.duration, act.predecessors,
                         resource=act.resource)
            self._activities[a.id] = a
            save_activity(a)

        self._refresh_ui()
        self.status_panel.set_message(
            "Sample project loaded. Click ▶ Schedule to compute CPM."
        )

    def _clear_all(self):
        if not self._activities:
            return
        reply = QMessageBox.question(
            self, "Clear All", "Delete all activities? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        for act_id in list(self._activities.keys()):
            delete_activity(act_id)
        self._activities.clear()
        self._refresh_ui()
        self.status_panel.set_message("All activities cleared.")

    def _run_schedule(self):
        if not self._activities:
            self.status_panel.set_message("No activities to schedule.", error=True)
            return
        try:
            scheduler = CPMScheduler(self._activities)
            scheduler.schedule()
            save_all_activities(self._activities)
            critical = scheduler.get_critical_path()
            self._refresh_ui()
            self.status_panel.update_stats(self._activities, critical)
        except SchedulerError as e:
            self.status_panel.set_message(str(e), error=True)
            QMessageBox.critical(self, "Scheduling Error", str(e))

    # ---- Export ----

    def _export_excel(self):
        if not self._activities:
            QMessageBox.information(self, "Export", "No activities to export.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel", f"{self._project_name}.xlsx",
            "Excel Workbook (*.xlsx)"
        )
        if not filepath:
            return
        try:
            from export_manager import export_to_excel
            export_to_excel(self._activities, filepath,
                            project_name=self._project_name,
                            start_date=self._start_date)
            self.status_panel.set_message(
                f"Exported to Excel: {os.path.basename(filepath)}"
            )
            QMessageBox.information(self, "Export Complete",
                                    f"Schedule exported to:\n{filepath}")
        except ImportError as e:
            QMessageBox.critical(self, "Missing Dependency",
                                 f"{e}\n\nRun:  pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _export_pdf(self):
        if not self._activities:
            QMessageBox.information(self, "Export", "No activities to export.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to PDF", f"{self._project_name}.pdf",
            "PDF Document (*.pdf)"
        )
        if not filepath:
            return
        try:
            from export_manager import export_to_pdf
            export_to_pdf(self._activities, filepath,
                          project_name=self._project_name,
                          start_date=self._start_date)
            self.status_panel.set_message(
                f"Exported to PDF: {os.path.basename(filepath)}"
            )
            QMessageBox.information(self, "Export Complete",
                                    f"Schedule exported to:\n{filepath}")
        except ImportError as e:
            QMessageBox.critical(self, "Missing Dependency",
                                 f"{e}\n\nRun:  pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _export_p6_xml(self):
        if not self._activities:
            QMessageBox.information(self, "Export", "No activities to export.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export P6 XML", f"{self._project_name}.xml",
            "P6 XML File (*.xml)"
        )
        if not filepath:
            return
        try:
            from p6_xml import export_p6_xml
            export_p6_xml(self._activities, filepath,
                          project_name=self._project_name,
                          start_date=self._start_date)
            self.status_panel.set_message(
                f"Exported P6 XML: {os.path.basename(filepath)}"
            )
            QMessageBox.information(self, "Export Complete",
                                    f"P6 XML exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _import_p6_xml(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import P6 XML", "", "P6 XML Files (*.xml);;All Files (*)"
        )
        if not filepath:
            return
        reply = QMessageBox.question(
            self, "Import P6 XML",
            "This will replace all current activities.\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            from p6_xml import import_p6_xml
            imported = import_p6_xml(filepath)
            if not imported:
                QMessageBox.warning(self, "Import",
                                    "No activities found in the XML file.")
                return
            for act_id in list(self._activities.keys()):
                delete_activity(act_id)
            self._activities.clear()
            for act in imported.values():
                self._activities[act.id] = act
                save_activity(act)
            self._refresh_ui()
            self.status_panel.set_message(
                f"Imported {len(imported)} activit(ies) from "
                f"{os.path.basename(filepath)}. Click ▶ Schedule to compute CPM."
            )
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))

    # ---- CRUD ----

    def _on_add_activity(self):
        dlg = ActivityDialog(parent=self, existing_ids=list(self._activities.keys()))
        if dlg.exec():
            act = dlg.get_activity()
            self._activities[act.id] = act
            save_activity(act)
            self._refresh_ui()
            self.status_panel.set_message(
                f"Activity '{act.id}' added. Click ▶ Schedule to update CPM."
            )

    def _on_edit_activity(self, act_id: str):
        if act_id not in self._activities:
            return
        dlg = ActivityDialog(
            parent=self,
            activity=self._activities[act_id],
            existing_ids=list(self._activities.keys()),
        )
        if dlg.exec():
            updated = dlg.get_activity()
            self._activities[act_id] = updated
            save_activity(updated)
            self._refresh_ui()
            self.status_panel.set_message(
                f"Activity '{act_id}' updated. Click ▶ Schedule to update CPM."
            )

    def _on_delete_activity(self, act_id: str):
        reply = QMessageBox.question(
            self, "Delete Activity", f"Delete activity '{act_id}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        del self._activities[act_id]
        delete_activity(act_id)
        self._refresh_ui()
        self.status_panel.set_message(
            f"Activity '{act_id}' deleted. Click ▶ Schedule to update CPM."
        )

    def _show_about(self):
        QMessageBox.about(
            self, "About Mini-P7",
            "<b>Mini-P7</b> v2.0.0 — CPM Scheduler<br><br>"
            "<b>Phase 2 features added:</b><br>"
            "&nbsp;&nbsp;• Project Settings (name + start date)<br>"
            "&nbsp;&nbsp;• Export to Excel (.xlsx)<br>"
            "&nbsp;&nbsp;• Export to PDF (reportlab)<br>"
            "&nbsp;&nbsp;• Import / Export Primavera P6 XML<br>"
            "&nbsp;&nbsp;• Resource Loading chart<br>"
            "&nbsp;&nbsp;• Free Float (FF) column<br>"
            "&nbsp;&nbsp;• Resource column in activity table<br><br>"
            "<b>Phase 1 bugs fixed:</b><br>"
            "&nbsp;&nbsp;• Raw SQL / wrong table name in db.py<br>"
            "&nbsp;&nbsp;• Missing resource, description, free_float fields<br>"
            "&nbsp;&nbsp;• Free float never computed in scheduler<br>"
            "&nbsp;&nbsp;• Predecessors isinstance(tuple) check<br><br>"
            "Built with PySide6.",
        )

    def closeEvent(self, event):
        self._settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
