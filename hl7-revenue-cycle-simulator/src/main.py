"""Entrypoint for the HL7 revenue cycle simulator pipeline."""

from __future__ import annotations

from pathlib import Path

from generate_messages import write_sample_messages
from parser import parse_hl7_messages
from rules import apply_revenue_cycle_rules


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_PATH = DATA_DIR / "sample_hl7_messages.txt"
OUTPUT_PATH = DATA_DIR / "parsed_output.csv"


def run_pipeline() -> Path:
    """Generate synthetic HL7 data, parse it, apply rules, and export CSV output."""

    message_path = write_sample_messages(INPUT_PATH)
    parsed_df = parse_hl7_messages(message_path)
    reviewed_df = apply_revenue_cycle_rules(parsed_df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    reviewed_df.to_csv(OUTPUT_PATH, index=False)

    total_records = len(reviewed_df)
    ready_count = int(reviewed_df["billing_status"].eq("Ready for Billing Review").sum())
    ready_pct = (ready_count / total_records * 100) if total_records else 0.0

    print(f"Synthetic HL7 feed written to: {message_path}")
    print(f"Structured billing review file written to: {OUTPUT_PATH}")
    print(f"Total records: {total_records}")
    print(f"Ready for billing review: {ready_count} ({ready_pct:.1f}%)")
    print("\nIssue severity counts:")
    for severity, count in reviewed_df["issue_severity"].value_counts().items():
        print(f"  - {severity}: {count}")

    print("\nBilling status counts:")
    for status, count in reviewed_df["billing_status"].value_counts().items():
        print(f"  - {status}: {count}")

    return OUTPUT_PATH


if __name__ == "__main__":
    run_pipeline()

