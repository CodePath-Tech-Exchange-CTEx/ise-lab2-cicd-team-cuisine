#############################################################################
# app.py — Dashboard: navbar, category filter (display only), grid of bet cards.
#############################################################################

import base64
import streamlit as st

from data import get_available_bets

from modules import (
    display_individual_bet_summary
    display_my_custom_component,
    display_post,
    display_genai_advice,
    display_individual_bet_summary,
    display_recent_workouts,
    display_trade_summary,
)
from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
    get_user_trades,
)

userId = 'user1'  # fallback when no username has been entered


def login():
    """Simple mock login using session state."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title('Welcome to SDS!')
        st.subheader('Please log in')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Log in'):
            st.session_state.logged_in = True
            st.session_state.username = username or userId
        return False
    return True

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
    # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

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
# This is the starting point for your app.  The flow checks login state
# first and then renders either the home feed or the profile/trade page.
if __name__ == '__main__':
    if login():
        page = st.sidebar.radio(
            'Navigation', ['Home', 'Profile / Trade Summary']
        )
        if page == 'Home':
            display_app_page()
        elif page == 'Profile / Trade Summary':
            st.title('Profile & Trade Summary')
            uid = st.session_state.get('username', userId)
            trades = get_user_trades(uid)
            display_trade_summary(trades)
