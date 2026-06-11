import streamlit as st
import requests

API_URL = "http://api:8000/predict"

st.set_page_config(page_title="AML Transaction Monitor", page_icon="🔍")
st.title("🔍 AML Transaction Risk Scorer")
st.markdown("Enter transaction details to get a real-time fraud risk assessment.")

# ── Inputs ────────────────────────────────────────────────────────────────────
txn_type = st.selectbox(
    "Transaction Type",
    options=["CASH_OUT", "TRANSFER", "PAYMENT", "CASH_IN", "DEBIT"]
)

amount = st.number_input("Transaction Amount", min_value=0.0, value=187629.11)

st.markdown("**Origin Account**")
col1, col2, col3 = st.columns(3)
name_orig      = col1.text_input("Account ID (nameOrig)", value="C1231006815")
old_balance_org = col2.number_input("Balance Before (oldbalanceOrg)", min_value=0.0, value=187629.11)
new_balance_org = col3.number_input("Balance After (newbalanceOrig)", min_value=0.0, value=0.0)

st.markdown("**Destination Account**")
col4, col5, col6 = st.columns(3)
name_dest      = col4.text_input("Account ID (nameDest)", value="C553264065")
old_balance_dst = col5.number_input("Balance Before (oldbalanceDest)", min_value=0.0, value=0.0)
new_balance_dst = col6.number_input("Balance After (newbalanceDest)", min_value=0.0, value=187629.11)

# ── Predict ───────────────────────────────────────────────────────────────────
if st.button("Score Transaction"):
    payload = {
        "type":           txn_type,
        "amount":         amount,
        "nameOrig":       name_orig,
        "oldbalanceOrg":  old_balance_org,
        "newbalanceOrig": new_balance_org,
        "nameDest":       name_dest,
        "oldbalanceDest": old_balance_dst,
        "newbalanceDest": new_balance_dst,
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()

            is_fraud  = result["is_fraud"]
            band      = result["risk_band"]
            score     = result["risk_score"]
            threshold = result["threshold_used"]

            # ── Verdict ───────────────────────────────────────────────────────
            if is_fraud:
                st.error("🚨 FRAUD DETECTED — Transaction flagged for review")
            else:
                st.success("✅ LEGITIMATE — Transaction cleared")

            # ── Metrics ───────────────────────────────────────────────────────
            m1, m2, m3 = st.columns(3)
            m1.metric("Risk Score",  f"{score:.4f}")
            m2.metric("Risk Band",   band.upper())
            m3.metric("Threshold",   f"{threshold:.4f}")

            # ── Risk band colour indicator ────────────────────────────────────
            band_colour = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            st.markdown(f"### Risk Level: {band_colour.get(band, '⚪')} {band.upper()}")

            st.progress(
                min(score, 1.0),
                text=f"Fraud probability: {score * 100:.2f}%"
            )

        else:
            st.error(f"API Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the FastAPI container is running.")