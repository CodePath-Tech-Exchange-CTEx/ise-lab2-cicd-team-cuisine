"""
Dashboard: navbar (logo + AirBets | Profile, Settings) and grid of compact bet cards.
"""
import streamlit as st

from data import get_available_bets, get_bet_categories
from modules import display_individual_bet_summary

LOGO_PATH = "static/images/airbets-logo.svg"
COLS_PER_ROW = 3

# ---- Navbar: logo + AirBets left, Profile + Settings right ----
nav_left, nav_right = st.columns([3, 1])
with nav_left:
    logo_col, name_col = st.columns([1, 8])
    with logo_col:
        try:
            st.image(LOGO_PATH, width=36)
        except Exception:
            st.write("")
    with name_col:
        st.markdown("# AirBets")
with nav_right:
    st.markdown("<br>", unsafe_allow_html=True)
    profile, settings = st.columns(2)
    with profile:
        st.button("Profile", key="nav_profile")
    with settings:
        st.button("Settings", key="nav_settings")

st.markdown("---")

# ---- Category filter ----
categories = get_bet_categories()
selected = st.selectbox(
    "Filter by category",
    options=["All"] + categories,
    index=0,
    key="dashboard_category",
)

bets = get_available_bets()
filtered = [b for b in bets if selected == "All" or b.get("category") == selected]

# ---- Selected bet detail (when user clicks a card) ----
if "dashboard_selected_bet" in st.session_state and st.session_state.dashboard_selected_bet:
    bet = st.session_state.dashboard_selected_bet
    if st.button("← Back to list", key="back_to_list"):
        st.session_state.dashboard_selected_bet = None
        st.rerun()
    display_individual_bet_summary(
        bet_name=bet["bet_name"],
        bet_image_link=bet.get("bet_image_link"),
        yes_value=bet["yes_value"],
        no_value=bet["no_value"],
        yes_percent=bet["yes_percent"],
        no_percent=bet["no_percent"],
        rules=bet["rules"],
    )
    st.stop()

# ---- Grid of compact bet cards ----
if not filtered:
    st.info("No bets in this category yet.")
else:
    for start in range(0, len(filtered), COLS_PER_ROW):
        row_bets = filtered[start : start + COLS_PER_ROW]
        cols = st.columns(COLS_PER_ROW)
        for col, bet in zip(cols, row_bets):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{bet['category']}**")
                    st.markdown(f"### {bet['bet_name']}")
                    st.caption(f"Yes **{bet['yes_percent']}%** · No **{bet['no_percent']}%**")
                    st.caption(f"${bet['yes_value']:.2f} / ${bet['no_value']:.2f}")
                    if st.button("View", key=f"view_{bet['bet_id']}"):
                        st.session_state.dashboard_selected_bet = bet
                        st.rerun()
