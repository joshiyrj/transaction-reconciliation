import io
import pandas as pd
import streamlit as st
from reconciliation import reconcile, preprocess

st.set_page_config(page_title="Reconciliation Tool", layout="wide")
st.title("Transaction Reconciliation Dashboard")

bank_file = st.file_uploader("Bank CSV", type="csv")
ledger_file = st.file_uploader("Ledger CSV", type="csv")

if bank_file and ledger_file:
    bank_df = preprocess(pd.read_csv(bank_file))
    ledger_df = preprocess(pd.read_csv(ledger_file))
    matched_df, ub_df, ul_df = reconcile(bank_df, ledger_df)

    st.subheader("Matched Transactions")
    st.dataframe(matched_df, use_container_width=True)

    st.subheader("Unmatched Bank Entries")
    st.dataframe(ub_df, use_container_width=True)

    st.subheader("Unmatched Ledger Entries")
    st.dataframe(ul_df, use_container_width=True)

    # build in-memory Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        matched_df.to_excel(writer, sheet_name="Matched", index=False)
        ub_df.to_excel(writer, sheet_name="Unmatched Bank", index=False)
        ul_df.to_excel(writer, sheet_name="Unmatched Ledger", index=False)
        for ws in writer.sheets.values():
            ws.set_column("A:Z", 20)
    buf.seek(0)

    st.download_button("Download Excel Report",
                       data=buf.getvalue(),
                       file_name="reconciliation_report.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")