# hl7-revenue-cycle-simulator

A small, polished Python portfolio project that simulates how synthetic HL7 ADT messages flow into downstream revenue cycle review logic. The project generates a mock ADT feed, parses key patient access and encounter fields, applies billing-focused validation rules, exports a structured CSV, and surfaces flagged records in a simple Streamlit dashboard.

This project is written as a resume-ready sample for Product Analyst / Business Analyst roles focused on MEDITECH Expanse, HL7 interfaces, patient access, admissions, billing, and collections.

## Why HL7 ADT matters

ADT messages are one of the earliest operational signals in a healthcare revenue cycle workflow. Admission, discharge, and transfer activity influences:

- patient identity matching
- encounter creation and visit tracking
- provider attribution
- downstream coding and billing readiness
- claim integrity and follow-up work queues

If registration or encounter details are incomplete when ADT data lands downstream, billing teams often end up working exception queues instead of clean claims. This prototype simulates that handoff in a lightweight, inspectable way.

## Business problem simulated

The project models a common healthcare IT scenario:

1. A hospital ADT feed sends admission and discharge messages from a source system such as MEDITECH.
2. A downstream revenue cycle workflow receives those events and expects core registration and encounter fields to be complete.
3. Missing patient IDs, missing providers, duplicate visit events, or incomplete discharge state create billing risk.
4. Analysts need a quick way to identify which records are billing-ready and which ones require follow-up.

## Architecture

`HL7 message -> parser -> structured pandas table -> billing rules -> CSV output + Streamlit dashboard`

- `src/generate_messages.py` creates deterministic synthetic HL7 v2-style ADT messages.
- `src/parser.py` reads the text feed and extracts business-relevant fields from `MSH`, `PID`, and `PV1`.
- `src/rules.py` applies revenue-cycle validation rules and assigns billing statuses.
- `src/main.py` runs the pipeline and exports `data/parsed_output.csv`.
- `dashboard/app.py` visualizes billing readiness, rule categories, and flagged records.

## Project structure

```text
hl7-revenue-cycle-simulator/
├── data/
│   ├── sample_hl7_messages.txt
│   └── parsed_output.csv
├── dashboard/
│   └── app.py
├── src/
│   ├── generate_messages.py
│   ├── main.py
│   ├── parser.py
│   └── rules.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

From the project root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
streamlit run dashboard/app.py
```

## What the pipeline does

The synthetic feed includes:

- `ADT^A01` admissions and `ADT^A03` discharges
- missing patient IDs
- missing attending providers
- incomplete encounter details on admissions
- discharges missing disposition / end-state details
- duplicate visit IDs on the same event type

The rules assign outcomes such as:

- `Critical - Missing Patient ID`
- `At Risk - Missing Provider`
- `At Risk - Duplicate Visit`
- `Incomplete Encounter`
- `Ready for Billing Review`

## Sample output

Running `python src/main.py` will:

- regenerate `data/sample_hl7_messages.txt`
- parse the synthetic HL7 feed into a structured table
- export `data/parsed_output.csv`
- print summary counts for billing readiness and issue severity

The Streamlit dashboard then shows:

- total records
- percent ready for billing review
- counts of critical, at-risk, and complete records
- a rule category bar chart
- a table of flagged records with message, patient, visit, and billing review details

## Notes on realism

- All records are fully synthetic and safe for local portfolio use.
- The parser is intentionally lightweight and not a full HL7 engine.
- The business rules are written to reflect common patient access and revenue-cycle quality checks without overengineering the prototype.

## Resume bullets

**Analyst / Product Analyst version**

- Built a Python and Streamlit prototype that simulated HL7 ADT admissions and discharges flowing into revenue cycle review logic, translating patient access data quality issues into billing-ready vs. exception workflow outcomes.

**Healthcare IT / Interoperability version**

- Developed a synthetic HL7 v2 ADT interface simulator that parsed `MSH`, `PID`, and `PV1` segments, identified registration and encounter defects, and visualized downstream billing risk in a lightweight analytics dashboard.

