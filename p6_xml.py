"""
P6 XML Import / Export — Phase 2
==================================
Provides lightweight read/write of Primavera P6 XML format.

The P6 XML schema is large; this module handles the Activity sub-set
that is needed to round-trip a CPM network:
  • WBS / Project header
  • Activity id, name, duration, predecessors (FS only)
  • Scheduling results (ES, EF, LS, LF, TF, FF)
  • Resource assignments (single resource per activity)

Usage
-----
    from p6_xml import import_p6_xml, export_p6_xml

    activities = import_p6_xml("project.xml")
    export_p6_xml(activities, "output.xml", project_name="My Project")
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Dict, Optional
from activity import Activity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}" if ns else local


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_p6_xml(filepath: str) -> Dict[str, Activity]:
    """
    Parse a Primavera P6 XML file and return {id: Activity}.

    Supports both namespaced (P6 R8+) and plain XML.
    Only Finish-to-Start (FS) relationships are imported.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Detect namespace
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag[1:root.tag.index("}")]

    def find_all(parent, local):
        return parent.findall(_tag(ns, local))

    def find_text(parent, local, default=""):
        el = parent.find(_tag(ns, local))
        return el.text.strip() if el is not None and el.text else default

    activities: Dict[str, Activity] = {}

    # Collect activities
    for act_el in find_all(root, "Activity"):
        act_id   = find_text(act_el, "Id") or find_text(act_el, "ActivityId")
        act_name = find_text(act_el, "Name") or find_text(act_el, "ActivityName")
        dur_str  = find_text(act_el, "PlannedDuration") or find_text(act_el, "Duration", "0")

        # Strip units suffix if present (e.g. "5.0d" → 5)
        dur_clean = "".join(c for c in dur_str if c.isdigit() or c == ".")
        try:
            duration = int(float(dur_clean))
        except ValueError:
            duration = 0

        resource = find_text(act_el, "ResourceId") or None

        if not act_id:
            continue

        activities[act_id] = Activity(
            id=act_id,
            name=act_name or act_id,
            duration=duration,
            predecessors=(),      # filled in next pass
            resource=resource,
        )

    # Collect relationships
    predecessors_map: Dict[str, list] = {aid: [] for aid in activities}

    for rel_el in find_all(root, "Relationship"):
        pred_id = find_text(rel_el, "PredecessorActivityId")
        succ_id = find_text(rel_el, "SuccessorActivityId")
        rel_type = find_text(rel_el, "Type", "FS")

        if rel_type != "FS":
            continue  # only Finish-to-Start supported
        if succ_id in predecessors_map and pred_id in activities:
            predecessors_map[succ_id].append(pred_id)

    # Apply predecessors
    for aid, preds in predecessors_map.items():
        if aid in activities:
            # Rebuild Activity with predecessors (slots=True prevents direct mutation of tuple easily)
            old = activities[aid]
            activities[aid] = Activity(
                id=old.id,
                name=old.name,
                duration=old.duration,
                predecessors=tuple(preds),
                resource=old.resource,
                description=old.description,
            )

    return activities


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_p6_xml(
    activities: Dict[str, Activity],
    filepath: str,
    project_name: str = "Mini-P7 Export",
    start_date: Optional[date] = None,
) -> None:
    """
    Write activities to a Primavera P6-compatible XML file.

    The output follows the XER / XML interchange format for P6 R8+.

    Parameters
    ----------
    activities   : {id: Activity}
    filepath     : destination .xml path
    project_name : written as <ProjectName>
    start_date   : if supplied, PlannedStartDate is computed per activity
    """
    root = ET.Element("APIBusinessObjects")
    root.set("xmlns", "http://xmlns.oracle.com/Primavera/P6/WS/Activity/V1")

    # ---- Project header ----
    proj = ET.SubElement(root, "Project")
    ET.SubElement(proj, "Id").text          = "PROJ-001"
    ET.SubElement(proj, "Name").text        = project_name
    ET.SubElement(proj, "ExportDate").text  = date.today().isoformat()
    if start_date:
        ET.SubElement(proj, "PlannedStartDate").text = start_date.isoformat()

    # ---- Activities ----
    for act in activities.values():
        el = ET.SubElement(root, "Activity")
        ET.SubElement(el, "Id").text              = act.id
        ET.SubElement(el, "ActivityId").text      = act.id
        ET.SubElement(el, "Name").text            = act.name
        ET.SubElement(el, "PlannedDuration").text = str(act.duration)
        ET.SubElement(el, "Type").text            = "Task Dependent"
        ET.SubElement(el, "Status").text          = "Not Started"
        ET.SubElement(el, "IsCritical").text      = str(act.is_critical).lower()
        ET.SubElement(el, "TotalFloat").text      = str(act.total_float)
        ET.SubElement(el, "FreeFloat").text       = str(act.free_float)
        ET.SubElement(el, "EarlyStart").text      = str(act.ES)
        ET.SubElement(el, "EarlyFinish").text     = str(act.EF)
        ET.SubElement(el, "LateStart").text       = str(act.LS)
        ET.SubElement(el, "LateFinish").text      = str(act.LF)
        if act.resource:
            ET.SubElement(el, "ResourceId").text  = act.resource
        if act.description:
            ET.SubElement(el, "Description").text = act.description

        if start_date:
            sd = start_date + timedelta(days=act.ES)
            fd = start_date + timedelta(days=act.EF)
            ET.SubElement(el, "PlannedStartDate").text  = sd.isoformat()
            ET.SubElement(el, "PlannedFinishDate").text = fd.isoformat()

    # ---- Relationships ----
    for act in activities.values():
        for pred_id in act.predecessors:
            rel = ET.SubElement(root, "Relationship")
            ET.SubElement(rel, "PredecessorActivityId").text = pred_id
            ET.SubElement(rel, "SuccessorActivityId").text   = act.id
            ET.SubElement(rel, "Type").text                  = "FS"
            ET.SubElement(rel, "Lag").text                   = "0"

    # Pretty-print (Python 3.9+)
    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
