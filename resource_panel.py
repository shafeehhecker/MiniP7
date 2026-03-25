"""
Resource Panel — Phase 2
=========================
A collapsible panel that displays per-resource workload as a
simple bar chart drawn on a QGraphicsScene.

Shows Early-Start loading (default) and highlights over-allocation
if a resource appears in more than one concurrent activity.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPen, QPainter
from PySide6.QtWidgets import (
    QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem,
    QGraphicsView, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget,
)

from activity import Activity


# Layout constants
BAR_H    = 26     # height per resource row
DAY_W    = 20     # pixels per day
LABEL_W  = 120    # left label column
HEADER_H = 32

# Colors
CLR_BG       = "#f8f8f8"
CLR_HDR      = "#e8e8e8"
CLR_NORMAL   = "#3a7ca5"
CLR_CRIT     = "#c04040"
CLR_OVERLOAD = "#e08020"
CLR_GRID     = "#d0d0d0"
CLR_TEXT     = "#202020"
CLR_HDR_TXT  = "#505050"


class ResourcePanel(QWidget):
    """Horizontal bar chart showing per-resource daily loading."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._activities: Dict[str, Activity] = {}
        self._setup_ui()

    # ------------------------------------------------------------------ #
    # Setup                                                               #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {CLR_BG};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(f"""
            QFrame {{ background-color: {CLR_HDR}; border-bottom: 1px solid #c0c0c0; }}
            QLabel {{ color: #404040; font-size: 10px; font-weight: bold; letter-spacing: 1px; }}
        """)
        tb_row = QHBoxLayout(toolbar)
        tb_row.setContentsMargins(12, 0, 12, 0)
        lbl = QLabel("RESOURCE LOADING  (Early-Start basis)")
        tb_row.addWidget(lbl)
        tb_row.addStretch()
        legend_over = QLabel("■ Over-allocated")
        legend_over.setStyleSheet(f"color: {CLR_OVERLOAD}; font-size: 11px;")
        tb_row.addWidget(legend_over)
        legend_norm = QLabel("■ Normal")
        legend_norm.setStyleSheet(f"color: {CLR_NORMAL}; font-size: 11px; margin-left: 10px;")
        tb_row.addWidget(legend_norm)
        layout.addWidget(toolbar)

        # Scene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet(f"""
            QGraphicsView {{ background-color: {CLR_BG}; border: none; }}
        """)
        layout.addWidget(self.view)

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def render_resources(self, activities: Dict[str, Activity]):
        """Rebuild the resource chart from the activities dict."""
        self._activities = activities
        self.scene.clear()

        if not activities:
            self._draw_empty()
            return

        # Group activities by resource
        resource_map: Dict[str, List[Activity]] = defaultdict(list)
        for act in activities.values():
            key = act.resource or "(Unassigned)"
            resource_map[key].append(act)

        if not resource_map:
            self._draw_empty()
            return

        project_end = max((a.EF for a in activities.values() if a.EF > 0), default=20)
        total_days  = max(project_end + 2, 20)

        scene_w = LABEL_W + total_days * DAY_W + 20
        scene_h = HEADER_H + len(resource_map) * BAR_H + 10
        self.scene.setSceneRect(0, 0, scene_w, scene_h)

        self._draw_header(total_days)
        self._draw_resource_rows(resource_map, total_days)

    # ------------------------------------------------------------------ #
    # Drawing                                                             #
    # ------------------------------------------------------------------ #

    def _draw_empty(self):
        self.scene.setSceneRect(0, 0, 600, 120)
        msg = QGraphicsTextItem("No resource data.\nAdd Resource names to activities and run Schedule.")
        msg.setDefaultTextColor(QColor("#808080"))
        msg.setFont(QFont("Arial", 11))
        msg.setPos(60, 30)
        self.scene.addItem(msg)

    def _draw_header(self, total_days: int):
        hdr_w = LABEL_W + total_days * DAY_W + 20
        bg = QGraphicsRectItem(0, 0, hdr_w, HEADER_H)
        bg.setBrush(QBrush(QColor(CLR_HDR)))
        bg.setPen(QPen(Qt.NoPen))
        self.scene.addItem(bg)

        font = QFont("Consolas", 8)
        pen_grid = QPen(QColor(CLR_GRID), 1, Qt.DotLine)
        for d in range(0, total_days + 1, 5):
            x = LABEL_W + d * DAY_W
            tick = self.scene.addLine(x, HEADER_H - 8, x, HEADER_H,
                                      QPen(QColor("#b0b0b0"), 1))
            lbl = QGraphicsTextItem(f"D{d}")
            lbl.setDefaultTextColor(QColor(CLR_HDR_TXT))
            lbl.setFont(font)
            lbl.setPos(x - 8, 6)
            self.scene.addItem(lbl)

        self.scene.addLine(0, HEADER_H, hdr_w, HEADER_H,
                           QPen(QColor("#b0b0b0"), 2))

    def _draw_resource_rows(
        self,
        resource_map: Dict[str, List[Activity]],
        total_days: int,
    ):
        # Build daily loading: resource → {day: count}
        daily_load: Dict[str, Dict[int, int]] = {}
        for res, acts in resource_map.items():
            daily_load[res] = defaultdict(int)
            for act in acts:
                for d in range(act.ES, act.EF):
                    daily_load[res][d] += 1

        font_lbl = QFont("Arial", 9)
        pen_border = QPen(QColor("#a0a0a0"), 1)

        for row_idx, (res_name, acts) in enumerate(resource_map.items()):
            y = HEADER_H + row_idx * BAR_H

            # Row background
            row_bg = QGraphicsRectItem(0, y, LABEL_W + total_days * DAY_W, BAR_H)
            row_bg.setBrush(QBrush(QColor("#ffffff" if row_idx % 2 == 0 else "#f4f4f4")))
            row_bg.setPen(QPen(Qt.NoPen))
            self.scene.addItem(row_bg)

            # Resource name label
            lbl = QGraphicsTextItem(res_name[:18])
            lbl.setDefaultTextColor(QColor(CLR_TEXT))
            lbl.setFont(font_lbl)
            lbl.setPos(4, y + 4)
            self.scene.addItem(lbl)

            # Activity bars
            for act in acts:
                bx = LABEL_W + act.ES * DAY_W
                bw = max(act.duration * DAY_W - 2, 2)
                bar_y = y + 4
                bar_h = BAR_H - 8

                load_at_es = daily_load[res_name].get(act.ES, 1)
                if load_at_es > 1:
                    clr = QColor(CLR_OVERLOAD)
                elif act.is_critical:
                    clr = QColor(CLR_CRIT)
                else:
                    clr = QColor(CLR_NORMAL)

                bar = QGraphicsRectItem(bx, bar_y, bw, bar_h)
                bar.setBrush(QBrush(clr))
                bar.setPen(pen_border)
                bar.setZValue(2)
                self.scene.addItem(bar)

                # Activity ID label on bar
                if bw > 20:
                    bar_lbl = QGraphicsTextItem(act.id)
                    bar_lbl.setDefaultTextColor(QColor("#ffffff"))
                    bar_lbl.setFont(QFont("Arial", 7))
                    bar_lbl.setPos(bx + 2, bar_y + 2)
                    bar_lbl.setZValue(3)
                    self.scene.addItem(bar_lbl)

            # Row divider
            self.scene.addLine(
                0, y + BAR_H, LABEL_W + total_days * DAY_W, y + BAR_H,
                QPen(QColor(CLR_GRID), 1)
            )

        # Vertical grid every 5 days
        pen_v = QPen(QColor(CLR_GRID), 1, Qt.DotLine)
        total_h = HEADER_H + len(resource_map) * BAR_H
        for d in range(0, total_days + 1, 5):
            x = LABEL_W + d * DAY_W
            self.scene.addLine(x, HEADER_H, x, total_h, pen_v)
