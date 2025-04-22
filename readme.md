# Transaction Reconciliation Tool

## Overview
Automatically match transactions between a bank CSV and a ledger CSV using fuzzy logic and confidence scoring. Outputs matched pairs, unmatched bank entries, and unmatched ledger entries, plus an Excel report.

## Folder Structure 

transaction_reconciliation/
├── reconciliation.py
├── app.py
├── run_all.py
├── requirements.txt
├── README.md
├── input_data/
│   ├── bank_transactions.csv
│   └── ledger_transactions.csv
└── output/_____

## Matching Logic
- **Amount**: ±₹1
- **Date**: ±3 days
- **Description**: ≥60% similarity (RapidFuzz)
- **Confidence**: Weighted by amount (40%), date (30%), description (30%)

## Setup

Download this repository as a zip or clone it in your local drive, and using whichever IDE you want, run this in the terminal to view the UI which shows the project, and also downloads the output files for you.


python run_all.py


