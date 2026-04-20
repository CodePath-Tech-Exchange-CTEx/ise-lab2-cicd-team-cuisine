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


def _initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_auth_modal' not in st.session_state:
        st.session_state.show_auth_modal = False
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'Log in'


def login():
    """Legacy login helper for backward-compatible tests."""
    _initialize_session_state()

    auth_mode = st.radio(
        'Auth mode',
        ['Log in', 'Sign up'],
        horizontal=True,
        key='login_auth_mode',
    )

    if auth_mode == 'Sign up':
        username = st.text_input('Username', key='signup_username')
        full_name = st.text_input('Full name', key='signup_full_name')
        date_of_birth = st.text_input('Date of birth (YYYY-MM-DD)', key='signup_dob')
        if st.button('Create account', key='create_account'):
            if not username:
                st.error('Username is required to create an account.')
            else:
                existing_user_id = get_user_id_by_username(username)
                if existing_user_id:
                    st.warning('That username already exists; logging you in instead.')
                    st.session_state.username = existing_user_id
                    st.session_state.logged_in = True
                    st.session_state.show_auth_modal = False
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
                        st.session_state.show_auth_modal = False
                        st.success('Account created successfully.')
                    except ValueError as err:
                        st.error(str(err))
    else:
        username = st.text_input('Username', key='login_username')
        password = st.text_input('Password', type='password', key='login_password')
        if st.button('Log in', key='log_in'):
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
            st.session_state.show_auth_modal = False
            st.success('Welcome back')

    return False


def render_auth_modal():
    _initialize_session_state()
    st.markdown("# Account")
    auth_mode = st.radio(
        'Auth mode',
        ['Log in', 'Sign up'],
        horizontal=True,
        key='modal_auth_mode',
    )

    if auth_mode == 'Sign up':
        username = st.text_input('Username', key='modal_signup_username')
        full_name = st.text_input('Full name', key='modal_signup_full_name')
        date_of_birth = st.text_input('Date of birth (YYYY-MM-DD)', key='modal_signup_dob')
        if st.button('Create account', key='modal_create_account'):
            if not username:
                st.error('Username is required to create an account.')
            else:
                existing_user_id = get_user_id_by_username(username)
                if existing_user_id:
                    st.warning('That username already exists; logging you in instead.')
                    st.session_state.username = existing_user_id
                    st.session_state.logged_in = True
                    st.session_state.show_auth_modal = False
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
                        st.session_state.show_auth_modal = False
                        st.success('Account created successfully.')
                    except ValueError as err:
                        st.error(str(err))
    else:
        username = st.text_input('Username', key='modal_login_username')
        password = st.text_input('Password', type='password', key='modal_login_password')
        if st.button('Log in', key='modal_log_in'):
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
            st.session_state.show_auth_modal = False
            st.success('Welcome back')


LOGO_PATH = "static/images/airbets-logo.svg"

st.set_page_config(layout="wide", page_title="Home", page_icon=LOGO_PATH)

COLS_PER_ROW = 4

# Navbar: one row, logo + name left, Profile right
def _logo_data_uri():
    try:
        with open(LOGO_PATH, "rb") as f:
            return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def render_post_creator(user_id):
    if 'user_posts' not in st.session_state:
        st.session_state.user_posts = get_user_posts(user_id)

    with st.expander("Create a post", expanded=True):
        content = st.text_area("What's on your mind?", key="new_post_content", height=100)
        if st.button("Post", key="submit_new_post"):
            if not content or not content.strip():
                st.error("Post content cannot be empty.")
            else:
                st.session_state.user_posts.insert(0, {
                    'user_id': user_id,
                    'post_id': f'post{len(st.session_state.user_posts) + 1}',
                    'timestamp': '2024-01-01 00:00:00',
                    'content': content.strip(),
                    'image': None,
                })
                st.success("Post created successfully.")
                st.session_state.new_post_content = ""

    st.markdown("### Recent posts")
    if st.session_state.user_posts:
        for post in st.session_state.user_posts:
            display_post(
                post['user_id'],
                get_user_profile(user_id).get('profile_image', ''),
                post['timestamp'],
                post['content'],
                post.get('image'),
            )
    else:
        st.info("No posts yet.")


def render_topbar():
    _logo = _logo_data_uri()
    _initialize_session_state()

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(
            '<div style="display:flex; align-items:center; gap:12px; margin-bottom:1rem;">'
            f'<img src="{_logo}" alt="AirBets logo" style="height:52px; width:52px; object-fit:contain;" onerror="this.style.display=\'none\'"/>'
            '<div style="display:flex; flex-direction:column; gap:0.1rem;">'
            '<span style="font-size:1.8rem; font-weight:700; margin:0;">AirBets</span>'
            '<span style="color:#9ca3af; font-size:0.95rem; margin:0;">Smart trading, insightful bets.</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        if st.session_state.logged_in:
            st.markdown(
                '<div style="padding:1rem; border:1px solid rgba(255,255,255,0.1); border-radius:16px; background:rgba(255,255,255,0.03); text-align:right;">'
                '<div style="font-size:0.95rem; color:#9ca3af; margin-bottom:0.35rem;">Signed in as</div>'
                f'<div style="font-size:1rem; font-weight:700;">{st.session_state.username}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button('👤 Account', key='account_button'):
                st.session_state.show_auth_modal = True
            if st.button('Log out', key='logout_button'):
                st.session_state.logged_in = False
                st.session_state.username = ''
        else:
            st.markdown(
                '<div style="padding:1rem; border:1px solid rgba(255,255,255,0.1); border-radius:16px; background:rgba(255,255,255,0.03); text-align:right;">'
                '<div style="font-size:1rem; font-weight:700; margin-bottom:0.25rem;">Welcome back</div>'
                '<div style="font-size:0.9rem; color:#9ca3af; margin-bottom:0.5rem;">Use your credentials or create a new account.</div>'
                '<div style="font-size:0.95rem; color:#9ca3af; margin-bottom:0.35rem;">Account</div>'
                '<div style="font-size:1rem; font-weight:700;">Log in / Sign up</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button('👤 Account', key='account_button'):
                st.session_state.show_auth_modal = True

    if st.session_state.show_auth_modal:
        with st.container():
            st.markdown('---')
            render_auth_modal()


def render_home():
    if st.session_state.get('show_individual'):
        if st.button('← Back to all bets', key='back_all'):
            st.session_state.show_individual = False
            st.rerun()
        st.markdown('---')
        bet_id = st.session_state.get('selected_bet_id')
        if not bet_id:
            available_bets = get_available_bets()
            bet_id = available_bets[0]['bet_id'] if available_bets else None
        bet = get_bet_data(bet_id) if bet_id else None
        if bet:
            display_individual_bet_summary(
                bet_id=bet_id,
                **bet
            )
        else:
            st.error('Could not find a valid bet to show in the individual bet view.')
        return

    st.markdown('---')
    user_id = st.session_state.get('username', userId)
    render_post_creator(user_id)

    st.markdown('---')
    st.subheader('Available bets')
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

    category_options = ['All'] + get_bet_categories()
    selected_category = st.selectbox(
        'Category',
        options=category_options,
        index=0,
        key='category_filter',
    )

    bets = get_available_bets()
    bets = filter_bets_by_category(bets, selected_category)

    if not bets:
        st.info('No bets yet.')
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
                        if st.button('View details', key=f"view_{bet['bet_id']}", use_container_width=True):
                            st.session_state.selected_bet_id = bet['bet_id']
                            st.session_state.show_individual = True
                            st.rerun()


def main():
    _initialize_session_state()
    render_topbar()

    if st.session_state.get('next_page') == 'profile':
        st.session_state.next_page = None
        st.switch_page('pages/5_Profile.py')

    render_home()


if st.runtime.exists() or __name__ == '__main__':
    main()
