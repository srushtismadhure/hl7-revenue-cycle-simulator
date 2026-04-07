"""Streamlit dashboard for the HL7 revenue cycle simulator."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "parsed_output.csv"


def load_data() -> pd.DataFrame:
    """Load the prepared CSV output for the dashboard."""

    return pd.read_csv(DATA_PATH).fillna("")


st.set_page_config(page_title="HL7 Revenue Cycle Simulator", layout="wide")
st.title("HL7 Revenue Cycle Simulator")
st.caption(
    "Synthetic ADT messages are parsed into a revenue-cycle review table to highlight"
    " missing registration, provider, and encounter details."
)

if not DATA_PATH.exists():
    st.error("`data/parsed_output.csv` was not found. Run `python src/main.py` first.")
    st.stop()

df = load_data()

message_type_options = sorted(df["message_type"].dropna().unique().tolist())
billing_status_options = sorted(df["billing_status"].dropna().unique().tolist())

selected_message_types = st.sidebar.multiselect(
    "Filter by message type",
    options=message_type_options,
    default=message_type_options,
)
selected_billing_statuses = st.sidebar.multiselect(
    "Filter by billing status",
    options=billing_status_options,
    default=billing_status_options,
)

filtered_df = df[
    df["message_type"].isin(selected_message_types)
    & df["billing_status"].isin(selected_billing_statuses)
].copy()

total_records = len(filtered_df)
ready_count = int(filtered_df["billing_status"].eq("Ready for Billing Review").sum())
ready_pct = (ready_count / total_records * 100) if total_records else 0.0

severity_counts = filtered_df["issue_severity"].value_counts()

metric_columns = st.columns(4)
metric_columns[0].metric("Total Records", f"{total_records}")
metric_columns[1].metric("Ready for Billing Review", f"{ready_pct:.1f}%")
metric_columns[2].metric("Critical Records", f"{severity_counts.get('Critical', 0)}")
metric_columns[3].metric("At-Risk Records", f"{severity_counts.get('At Risk', 0)}")

st.markdown("### Record Mix")
mix_columns = st.columns(3)
mix_columns[0].metric("Complete Records", f"{severity_counts.get('Complete', 0)}")
mix_columns[1].metric("Admissions", f"{int(filtered_df['message_type'].eq('ADT^A01').sum())}")
mix_columns[2].metric("Discharges", f"{int(filtered_df['message_type'].eq('ADT^A03').sum())}")

chart_data = (
    filtered_df["rule_triggered"]
    .value_counts()
    .rename_axis("rule_triggered")
    .reset_index(name="count")
)

st.markdown("### Rule Category Volume")
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(chart_data["rule_triggered"], chart_data["count"], color="#3B82F6")
ax.set_ylabel("Records")
ax.set_xlabel("Rule Category")
ax.set_title("Revenue Cycle Rule Distribution")
ax.tick_params(axis="x", rotation=30)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)

st.markdown("### Flagged Records")
flagged_df = filtered_df[filtered_df["issue_severity"] != "Complete"].copy()

if flagged_df.empty:
    st.info("No flagged records match the selected filters.")
else:
    display_columns = [
        "message_type",
        "message_control_id",
        "patient_id",
        "patient_last_name",
        "patient_first_name",
        "visit_id",
        "attending_provider",
        "billing_status",
        "issue_severity",
        "trigger_details",
        "event_timestamp",
    ]
    st.dataframe(
        flagged_df[display_columns].sort_values(by="event_timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
