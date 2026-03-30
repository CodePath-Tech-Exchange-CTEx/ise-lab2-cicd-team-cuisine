"""
Individual view: shows the full individual_bet_summary component (Shavaughn's design)
— image, Buy/Sell, Yes/No, rules, amount input, Submit button — at /individual_view.
"""
import streamlit as st

from data_fetcher import get_bet_data, add_active_bet
from modules import display_individual_bet_summary

st.set_page_config(page_title="Bet detail — AirBets", layout="wide")

st.markdown("[← Back to dashboard](/)")
st.markdown("---")

query_params = st.query_params
bet_id = query_params.get("bet_id")

if not bet_id:
    # Fallback to a default bet if accessed directly via sidebar
    bet_id = "bet001"

bet = get_bet_data(bet_id)
if not bet:
    st.error(f"Could not find data for bet with ID '{bet_id}'.")
else:
    display_individual_bet_summary(
        bet_id=bet_id,
        **bet
    )
