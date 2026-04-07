"""Revenue cycle validation rules for synthetic HL7 encounters."""

from __future__ import annotations

import pandas as pd


def apply_revenue_cycle_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Add billing-focused validation flags and statuses to parsed HL7 rows."""

    reviewed = df.copy()

    for column in reviewed.columns:
        if reviewed[column].dtype == "object":
            reviewed[column] = reviewed[column].fillna("").astype(str).str.strip()

    # A patient ID is the anchor that connects the ADT message to the patient account
    # and downstream billing record. Without it, the encounter cannot be matched safely.
    reviewed["missing_patient_id_flag"] = reviewed["patient_id"].eq("")

    # The attending provider often determines coding ownership, routing, and claim review.
    # Missing provider attribution creates avoidable follow-up work for billing teams.
    reviewed["missing_provider_flag"] = reviewed["attending_provider"].eq("")

    # Duplicate visit IDs on the same event type can indicate a duplicate interface event
    # or registration error that could trigger duplicate work queues or duplicate charges.
    reviewed["duplicate_visit_flag"] = reviewed["visit_id"].ne("") & reviewed.duplicated(
        subset=["visit_id", "message_type"], keep=False
    )

    # Admissions need core encounter details before financial clearance work can proceed.
    # Discharges should carry a disposition/state so the encounter has a clean end state.
    reviewed["incomplete_encounter_flag"] = (
        (
            reviewed["message_type"].eq("ADT^A01")
            & (
                reviewed["patient_class"].eq("")
                | reviewed["location"].eq("")
                | reviewed["visit_id"].eq("")
            )
        )
        | (
            reviewed["message_type"].eq("ADT^A03")
            & reviewed["discharge_disposition"].eq("")
        )
    )

    reviewed["rule_triggered"] = "Ready - No Rule Triggered"
    reviewed["trigger_details"] = "Ready - No Rule Triggered"
    reviewed["billing_status"] = "Ready for Billing Review"
    reviewed["issue_severity"] = "Complete"

    reviewed.loc[reviewed["incomplete_encounter_flag"], "rule_triggered"] = "Incomplete Encounter"
    reviewed.loc[reviewed["duplicate_visit_flag"], "rule_triggered"] = "At Risk - Duplicate Visit"
    reviewed.loc[reviewed["missing_provider_flag"], "rule_triggered"] = "At Risk - Missing Provider"
    reviewed.loc[reviewed["missing_patient_id_flag"], "rule_triggered"] = "Critical - Missing Patient ID"

    reviewed.loc[reviewed["incomplete_encounter_flag"], "billing_status"] = "Review - Incomplete Encounter"
    reviewed.loc[reviewed["duplicate_visit_flag"], "billing_status"] = (
        "Review - Potential Duplicate Encounter"
    )
    reviewed.loc[reviewed["missing_provider_flag"], "billing_status"] = "Hold - Provider Follow-up"
    reviewed.loc[reviewed["missing_patient_id_flag"], "billing_status"] = (
        "Hold - Registration Correction"
    )

    at_risk_mask = (
        reviewed["missing_provider_flag"]
        | reviewed["duplicate_visit_flag"]
        | reviewed["incomplete_encounter_flag"]
    )
    reviewed.loc[at_risk_mask, "issue_severity"] = "At Risk"
    reviewed.loc[reviewed["missing_patient_id_flag"], "issue_severity"] = "Critical"

    def summarize_triggers(row: pd.Series) -> str:
        triggers = []
        if row["missing_patient_id_flag"]:
            triggers.append("Critical - Missing Patient ID")
        if row["missing_provider_flag"]:
            triggers.append("At Risk - Missing Provider")
        if row["duplicate_visit_flag"]:
            triggers.append("At Risk - Duplicate Visit")
        if row["incomplete_encounter_flag"]:
            triggers.append("Incomplete Encounter")
        return "; ".join(triggers) if triggers else "Ready - No Rule Triggered"

    reviewed["trigger_details"] = reviewed.apply(summarize_triggers, axis=1)
    return reviewed

