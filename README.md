
## Overview

This project simulates how healthcare systems process HL7 ADT (Admission, Discharge, Transfer) messages by converting raw, pipe-delimited data into structured datasets and identifying data quality issues that can impact downstream workflows.

The goal is to demonstrate how unstructured hospital data can be transformed and validated to support reliable system operations and decision-making.

---

##  Problem

Healthcare systems exchange data using HL7 messages, which are often:

* unstructured and difficult to interpret
* inconsistent across sources
* prone to missing or incomplete fields

These issues can lead to:

* incomplete patient records
* workflow inefficiencies
* downstream data quality challenges

---

## Solution

This project builds a lightweight pipeline to:

1. Parse HL7 ADT messages (MSH, PID, PV1 segments)
2. Extract key patient and encounter fields
3. Convert raw messages into structured tabular data
4. Apply validation logic to identify incomplete or inconsistent records

---

##  Workflow

HL7 Message → Parser → Structured Data → Validation Rules → Output Dataset

---

##  Key Features

* **HL7 Message Parsing**
  Extracts patient and encounter data from raw ADT messages

* **Structured Data Transformation**
  Converts unstructured text into clean, analysis-ready format

* **Data Validation Logic**
  Flags records with:

  * missing patient identifiers
  * missing provider information
  * incomplete encounter data

* **Synthetic Data Simulation**
  Uses generated HL7 messages to mimic real-world scenarios

---

## Tech Stack

* Python
* pandas
* Streamlit (optional dashboard)

---

## 📂 Project Structure

```
hl7-data-parsing-pipeline/
│
├── data/
│   └── sample_hl7_messages.txt
│
├── src/
│   ├── parser.py
│   ├── rules.py
│   └── main.py
│
├── output/
│   └── parsed_data.csv
│
├── dashboard/ (optional)
│   └── app.py
│
├── requirements.txt
└── README.md
```

---

## How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the pipeline

```
python src/main.py
```

### 3. (Optional) Run dashboard

```
streamlit run dashboard/app.py
```

---

##  Sample Output

The pipeline generates a structured dataset with fields such as:

| patient_id | name     | encounter_type | provider  | validation_flag  |
| ---------- | -------- | -------------- | --------- | ---------------- |
| 12345      | John Doe | Inpatient      | Dr. Smith | Complete         |
| 67890      | Jane Doe | ER             | Missing   | Missing Provider |

---

##  Key Takeaways

* Demonstrates how raw HL7 data can be structured for analysis
* Highlights the importance of data validation in healthcare workflows
* Shows how missing or inconsistent data can be surfaced early
* Reflects real-world challenges in healthcare data processing

---

##  Future Improvements

* Expand support for additional HL7 message types
* Add more advanced validation rules
* Integrate with a database for persistent storage
* Enhance dashboard for deeper analytics

---

## 👤 Author

Srushti Madhure



