"""
Individual view: shows the full individual_bet_summary component (Shavaughn's design)
— image, Buy/Sell, Yes/No, rules, amount input, Submit button — at /individual_view.
"""
import streamlit as st

from data import get_available_bets
from modules import display_individual_bet_summary

st.set_page_config(page_title="Bet detail — AirBets", layout="wide")

st.markdown("[← Back to dashboard](/)")
st.markdown("---")

bets = get_available_bets()
if not bets:
    st.info("No bets available.")
else:
    bet = bets[0]
    display_individual_bet_summary(
        bet_name=bet["bet_name"],
        bet_image_link=bet.get("bet_image_link"),
        yes_value=bet["yes_value"],
        no_value=bet["no_value"],
        yes_percent=bet["yes_percent"],
        no_percent=bet["no_percent"],
        rules=bet["rules"],
    )
