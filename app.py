#############################################################################
# app.py — Dashboard: navbar, category filter (display only), grid of bet cards.
#############################################################################

import base64
import streamlit as st

from data import get_available_bets
from modules import display_individual_bet_summary

st.set_page_config(layout="wide", page_title="AirBets")

LOGO_PATH = "static/images/airbets-logo.svg"
COLS_PER_ROW = 4

# Navbar: one row, logo + name left (same div), Profile/Settings right
def _logo_data_uri():
    try:
        with open(LOGO_PATH, "rb") as f:
            return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return ""

_logo = _logo_data_uri()
st.markdown(
    '<nav style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:1rem;">'
    '<div style="display:flex; align-items:center; gap:12px;">'
    f'<img src="{_logo}" alt="" style="height:56px; width:56px; object-fit:contain;" onerror="this.style.display=\'none\'"/>'
    '<span style="font-size:2rem; font-weight:700;">AirBets</span>'
    '</div>'
    '<div style="color:inherit; opacity:0.9; font-size:1.1rem;">Settings &nbsp; Profile</div>'
    '</nav>',
    unsafe_allow_html=True,
)

st.markdown("---")

# Switch view: "Individual bet view" shows full card (buy/sell, submit) on this same page
if st.button("**Individual bet view** (full card with buy/sell, submit)", key="go_individual"):
    st.session_state.show_individual = True
    st.rerun()

if st.session_state.get("show_individual"):
    if st.button("← Back to all bets", key="back_all"):
        st.session_state.show_individual = False
        st.rerun()
    st.markdown("---")
    bets = get_available_bets()
    if bets:
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
    st.stop()

# Columns fill top-to-bottom; minimal gap between cards
st.markdown(
    """
    <style>
    [data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
    [data-testid="column"] > div { padding-left: 0 !important; padding-right: 0 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { margin: 0 0 0.25rem 0 !important; padding: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Category filter (hardcoded, not functioning — display only) ----
st.selectbox(
    "Category",
    options=["All", "Crypto", "Politics", "Sports", "Other"],
    index=0,
    key="category_filter",
    disabled=False,
)
bets = get_available_bets()

# ---- 4 columns, each filled top-to-bottom with cards ----
if not bets:
    st.info("No bets yet.")
else:
    cols = st.columns(COLS_PER_ROW)
    for c in range(COLS_PER_ROW):
        col_bets = [bets[i] for i in range(c, len(bets), COLS_PER_ROW)]
        with cols[c]:
            for bet in col_bets:
                with st.container(border=True):
                    st.markdown(f"**{bet['category']}**")
                    st.markdown(f"### {bet['bet_name']}")
                    st.caption(f"Yes **{bet['yes_percent']}%** · No **{bet['no_percent']}%**")
                    st.caption(f"${bet['yes_value']:.2f} / ${bet['no_value']:.2f}")
