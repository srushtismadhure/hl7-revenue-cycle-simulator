"""Simple parser for synthetic HL7 ADT messages."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def _get_field(fields: list[str], index: int) -> str:
    """Safely return a field value from a split HL7 segment."""

    return fields[index].strip() if index < len(fields) else ""


def _format_date(value: str) -> str:
    """Convert HL7 YYYYMMDD dates into a recruiter-friendly format."""

    if not value:
        return ""

    try:
        return datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return value


def _format_timestamp(value: str) -> str:
    """Convert HL7 timestamps into a readable local timestamp string."""

    if not value:
        return ""

    try:
        return datetime.strptime(value, "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def _format_person_name(value: str) -> tuple[str, str]:
    """Split an HL7 person name into last and first name parts."""

    if not value:
        return "", ""

    parts = value.split("^")
    last_name = parts[0].title() if parts else ""
    first_name = parts[1].title() if len(parts) > 1 else ""
    return last_name, first_name


def _format_provider_name(value: str) -> str:
    """Convert an HL7 provider name from LAST^FIRST into First Last."""

    last_name, first_name = _format_person_name(value)
    return " ".join(part for part in [first_name, last_name] if part)


def _parse_message(message_text: str) -> dict[str, str]:
    """Parse the handful of HL7 fields needed for this prototype."""

    segments = {}
    for raw_segment in message_text.splitlines():
        segment = raw_segment.strip()
        if not segment:
            continue

        fields = segment.split("|")
        segments[fields[0]] = fields

    msh = segments.get("MSH", [])
    pid = segments.get("PID", [])
    pv1 = segments.get("PV1", [])

    patient_last_name, patient_first_name = _format_person_name(_get_field(pid, 5))

    provider_field = _get_field(pv1, 7) or _get_field(pv1, 6)

    return {
        "message_type": _get_field(msh, 8),
        "message_control_id": _get_field(msh, 9),
        "patient_id": _get_field(pid, 3),
        "patient_last_name": patient_last_name,
        "patient_first_name": patient_first_name,
        "dob": _format_date(_get_field(pid, 7)),
        "sex": _get_field(pid, 8),
        "patient_class": _get_field(pv1, 2),
        "location": _get_field(pv1, 3),
        "attending_provider": _format_provider_name(provider_field),
        "visit_id": _get_field(pv1, 19),
        "event_timestamp": _format_timestamp(_get_field(msh, 6)),
        "discharge_disposition": _get_field(pv1, 36),
    }


def parse_hl7_messages(file_path: str | Path) -> pd.DataFrame:
    """Read a text file of HL7 messages and return a structured DataFrame."""

    source_path = Path(file_path)
    if not source_path.exists():
        raise FileNotFoundError(f"HL7 source file not found: {source_path}")

    raw_text = source_path.read_text(encoding="utf-8").strip()
    if not raw_text:
        return pd.DataFrame(
            columns=[
                "message_type",
                "message_control_id",
                "patient_id",
                "patient_last_name",
                "patient_first_name",
                "dob",
                "sex",
                "patient_class",
                "location",
                "attending_provider",
                "visit_id",
                "event_timestamp",
                "discharge_disposition",
            ]
        )

    message_blocks = [block for block in re.split(r"\n\s*\n", raw_text) if block.strip()]
    parsed_rows = [_parse_message(block) for block in message_blocks]
    return pd.DataFrame(parsed_rows)

