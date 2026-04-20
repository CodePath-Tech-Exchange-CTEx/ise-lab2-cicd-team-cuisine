#############################################################################
# app.py — Dashboard: navbar, category filter (display only), grid of bet cards.
#############################################################################

import base64
import streamlit as st

from data import get_available_bets
from data.bets import get_bet_categories

from modules import (
    display_post,
    display_genai_advice,
    display_individual_bet_summary,
    display_recent_workouts,
    display_trade_summary,
    filter_bets_by_category,
)
from data_fetcher import (
    create_user,
    get_bet_data,
    get_user_friends,
    get_user_posts,
    get_genai_advice,
    get_user_id_by_username,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
    get_user_trades,
)

userId = 'user1'  # fallback when no username has been entered


def login():
    """Simple mock login and sign-up using session state."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title('Welcome to Airbets!')
        st.subheader('Please log in or sign up')

        auth_mode = st.radio(
            'Auth mode',
            ['Log in', 'Sign up'],
            horizontal=True,
            key='auth_mode',
        )

        if auth_mode == 'Sign up':
            username = st.text_input('Username', key='signup_username')
            full_name = st.text_input('Full name', key='signup_full_name')
            date_of_birth = st.text_input('Date of birth (YYYY-MM-DD)', key='signup_dob')
            if st.button('Create account'):
                if not username:
                    st.error('Username is required to create an account.')
                else:
                    existing_user_id = get_user_id_by_username(username)
                    if existing_user_id:
                        st.warning('That username already exists; logging you in instead.')
                        st.session_state.username = existing_user_id
                        st.session_state.logged_in = True
                    else:
                        try:
                            new_user_id = create_user(
                                username.strip(),
                                full_name=full_name.strip() if full_name else username.strip().title(),
                                date_of_birth=date_of_birth.strip() if date_of_birth else '2000-01-01',
                            )
                            st.session_state.logged_in = True
                            st.session_state.username = new_user_id
                            st.session_state.next_page = 'profile'
                            st.success('Account created successfully.')
                        except ValueError as err:
                            st.error(str(err))
                return False
        else:
            username = st.text_input('Username', key='login_username')
            password = st.text_input('Password', type='password', key='login_password')
            if st.button('Log in'):
                if username:
                    user_id = get_user_id_by_username(username)
                    if user_id is None:
                        user_id = create_user(
                            username.strip(),
                            full_name=username.strip().title(),
                            date_of_birth='2000-01-01',
                        )
                    st.session_state.logged_in = True
                    st.session_state.username = user_id
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = userId
                return False
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
    # Fetch selected bet from session state or fallback to the first available bet
    bet_id = st.session_state.get("selected_bet_id")
    if not bet_id:
        available_bets = get_available_bets()
        bet_id = available_bets[0]["bet_id"] if available_bets else None
    bet = get_bet_data(bet_id) if bet_id else None
    if bet:
        display_individual_bet_summary(
            bet_id=bet_id,
            **bet
        )
    else:
        st.error("Could not find a valid bet to show in the individual bet view.")
    st.stop()

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

# ---- Category filter ----
category_options = ["All"] + get_bet_categories()
selected_category = st.selectbox(
    "Category",
    options=category_options,
    index=0,
    key="category_filter",
    disabled=False,
)

bets = get_available_bets()
bets = filter_bets_by_category(bets, selected_category)

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
        if st.session_state.get('next_page') == 'profile':
            st.session_state.next_page = None
            st.switch_page("pages/5_Profile.py")

        page = st.sidebar.radio(
            'Navigation', ['Home', 'Friends Activity', 'Profile / Trade Summary']
        )
        if page == 'Home':
            pass
        elif page == 'Friends Activity':
            st.switch_page("pages/4_Friends_Activity.py")
        elif page == 'Profile / Trade Summary':
            st.switch_page("pages/5_Profile.py")
