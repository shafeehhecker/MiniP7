"""
Project Settings Dialog — Phase 2
===================================
Lets the user set:
  • Project name
  • Project start date (calendar picker)
  • Working-day calendar (Mon–Fri vs 7-day week)
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

_QSS = """
QDialog {
    background-color: #f8f8f8;
    color: #202020;
}
QLabel { color: #404040; font-size: 12px; }
QLabel#title { color: #1e5c8a; font-size: 16px; font-weight: bold; }
QLineEdit, QDateEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 12px;
    min-height: 26px;
}
QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid #3a7ca5;
    background-color: #f0f8ff;
}
QPushButton {
    background-color: #ffffff;
    color: #404040;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 12px;
    min-width: 80px;
}
QPushButton[accent="true"] {
    background-color: #3a7ca5;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #2a5a80;
}
QPushButton[accent="true"]:hover { background-color: #2a6a90; }
QFrame[frameShape="4"] { color: #d0d0d0; max-height: 1px; }
"""


class ProjectSettingsDialog(QDialog):
    """Modal dialog for project-level settings."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        project_name: str = "My Project",
        start_date: Optional[date] = None,
        calendar_type: str = "Mon-Fri",
    ) -> None:
        super().__init__(parent)
        self._build_ui(project_name, start_date, calendar_type)
        self._connect()

    # ---- UI ----

    def _build_ui(self, project_name, start_date, calendar_type):
        self.setWindowTitle("Project Settings")
        self.setMinimumWidth(380)
        self.setModal(True)
        self.setStyleSheet(_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel("Project Settings")
        title.setObjectName("title")
        root.addWidget(title)
        root.addWidget(self._divider())

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Project name
        self._name_edit = QLineEdit()
        self._name_edit.setText(project_name)
        self._name_edit.setMaxLength(120)
        form.addRow("Project Name", self._name_edit)

        # Start date
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("dd MMM yyyy")
        q_date = QDate(*((start_date or date.today()).timetuple()[:3]))
        self._date_edit.setDate(q_date)
        form.addRow("Start Date", self._date_edit)

        # Calendar type
        self._cal_combo = QComboBox()
        self._cal_combo.addItems(["Mon–Fri (5 days/week)", "7-day week"])
        if calendar_type != "Mon-Fri":
            self._cal_combo.setCurrentIndex(1)
        form.addRow("Calendar", self._cal_combo)

        root.addLayout(form)
        root.addSpacing(6)
        root.addWidget(self._divider())

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        ok = QPushButton("Save")
        ok.setProperty("accent", True)
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        btn_row.addWidget(ok)
        root.addLayout(btn_row)

    def _connect(self):
        pass

    # ---- Public API ----

    @property
    def project_name(self) -> str:
        return self._name_edit.text().strip() or "My Project"

    @property
    def start_date(self) -> date:
        q = self._date_edit.date()
        return date(q.year(), q.month(), q.day())

    @property
    def calendar_type(self) -> str:
        return "Mon-Fri" if self._cal_combo.currentIndex() == 0 else "7-day"

    # ---- Helpers ----

    @staticmethod
    def _divider() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFrameShadow(QFrame.Plain)
        return f
