import os
import pandas as pd
from rapidfuzz.fuzz import partial_ratio

# Matching thresholds
AMOUNT_TOLERANCE = 1.0       # ₹1
DATE_TOLERANCE_DAYS = 3      # ±3 days
DESC_SIM_THRESHOLD = 60      # 60% similarity

def preprocess(df):
    """Clean up date, amount, description columns."""
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = (df['Amount']
                    .astype(str)
                    .str.replace(',', '')
                    .str.replace('₹', '')
                    .astype(float))
    df['Description'] = df['Description'].astype(str).str.lower().str.strip()
    return df

def fuzzy_score(a, b):
    """Return similarity score (0–100) between two strings."""
    return partial_ratio(a, b)

def should_match(b, l):
    """Check basic thresholds before computing confidence."""
    if abs(b['Amount'] - l['Amount']) > AMOUNT_TOLERANCE:
        return False
    if abs((b['Date'] - l['Date']).days) > DATE_TOLERANCE_DAYS:
        return False
    if fuzzy_score(b['Description'], l['Description']) < DESC_SIM_THRESHOLD:
        return False
    return True

def compute_confidence(b, l):
    """Weighted confidence: amount 40%, date 30%, description 30%."""
    amt_score = max(0, 1 - abs(b['Amount'] - l['Amount']) / AMOUNT_TOLERANCE)
    date_score = max(0, 1 - abs((b['Date'] - l['Date']).days) / DATE_TOLERANCE_DAYS)
    desc_score = fuzzy_score(b['Description'], l['Description']) / 100
    return round((amt_score * 0.4 + date_score * 0.3 + desc_score * 0.3) * 100, 2)

def reconcile(bank_df, ledger_df):
    """Return DataFrames: matched, unmatched_bank, unmatched_ledger."""
    bank_df = preprocess(bank_df.copy())
    ledger_df = preprocess(ledger_df.copy())

    matched = []
    unmatched_bank = []
    used = set()

    for i, b in bank_df.iterrows():
        best_conf = 0
        best_j = None
        for j, l in ledger_df.iterrows():
            if j in used:
                continue
            if should_match(b, l):
                conf = compute_confidence(b, l)
                if conf > best_conf:
                    best_conf, best_j = conf, j
        if best_j is not None:
            l = ledger_df.loc[best_j]
            matched.append({
                'Bank Date': b['Date'], 'Bank Amount': b['Amount'], 'Bank Desc': b['Description'],
                'Ledger Date': l['Date'], 'Ledger Amount': l['Amount'], 'Ledger Desc': l['Description'],
                'Confidence': best_conf
            })
            used.add(best_j)
        else:
            unmatched_bank.append({
                'Date': b['Date'], 'Amount': b['Amount'], 'Description': b['Description'],
                'Reason': 'No suitable match', 'Confidence': 0
            })

    # any ledger rows not used
    unmatched_ledger = []
    for j, l in ledger_df.iterrows():
        if j not in used:
            unmatched_ledger.append({
                'Date': l['Date'], 'Amount': l['Amount'], 'Description': l['Description'],
                'Reason': 'No matching bank entry', 'Confidence': 0
            })

    return pd.DataFrame(matched), pd.DataFrame(unmatched_bank), pd.DataFrame(unmatched_ledger)

def export_outputs(matched, unmatched_bank, unmatched_ledger, out_dir='output'):
    """Save CSVs and an Excel report."""
    os.makedirs(out_dir, exist_ok=True)
    matched.to_csv(f"{out_dir}/matched.csv", index=False)
    unmatched_bank.to_csv(f"{out_dir}/unmatched_bank.csv", index=False)
    unmatched_ledger.to_csv(f"{out_dir}/unmatched_ledger.csv", index=False)

    # Excel
    with pd.ExcelWriter(f"{out_dir}/reconciliation_report.xlsx") as writer:
        matched.to_excel(writer, sheet_name='Matched', index=False)
        unmatched_bank.to_excel(writer, sheet_name='Unmatched_Bank', index=False)
        unmatched_ledger.to_excel(writer, sheet_name='Unmatched_Ledger', index=False)
        # summary
        total = len(matched) + len(unmatched_bank)
        summary = pd.DataFrame({
            'Metric': ['Total Bank', 'Matched', 'Unmatched Bank', 'Unmatched Ledger', '% Matched', 'Avg Conf'],
            'Value': [total, len(matched), len(unmatched_bank), len(unmatched_ledger),
                      f"{len(matched)/total*100:.2f}%", matched['Confidence'].mean() if not matched.empty else 0]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)

if __name__ == '__main__':
    bank = pd.read_csv('input_data/bank_transactions.csv')
    ledger = pd.read_csv('input_data/ledger_transactions.csv')
    m, ub, ul = reconcile(bank, ledger)
    export_outputs(m, ub, ul)