#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import streamlit as st
import streamlit.components.v1 as components
import importlib.util
from data_fetcher import process_bet_transaction, get_user_profile
import os

# Hide Streamlit's default page navigation menu so only the custom sidebar is shown.
st.set_option("client.showSidebarNavigation", False)

_COMPONENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "custom_components", "individual_bet_summary_component"))

# Declare the new bidirectional component
_bet_summary_component = components.declare_component(
    "individual_bet_summary_component",
    path=_COMPONENT_ROOT
)

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    
    # This import is now local to the function that uses it
    from internals import create_component
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Render a simple post with optional image.

    This is a minimal implementation used in the home feed and in unit tests.
    The parameters mirror the data returned by :func:`get_user_posts`.
    """
    st.subheader(f"{username} – {timestamp}")
    st.write(content)
    if post_image:
        st.image(post_image)


def _render_comment_card(comment, nested=False):
    """Render a single comment card with optional nested indentation."""
    indent_style = "margin-left: 1.5rem;" if nested else ""
    avatar = comment.get('avatar', '💬')
    st.markdown(
        f"""
        <div style="{indent_style} border:1px solid rgba(148,163,184,0.18); background: rgba(15,23,42,0.92); border-radius: 18px; padding: 18px; margin-bottom: 0.85rem;">
            <div style="display:flex; align-items:center; gap: 0.85rem; flex-wrap:wrap;">
                <div style="width:38px; height:38px; border-radius:50%; background:#2563eb; color:white; display:flex; align-items:center; justify-content:center; font-size:1rem;">{avatar}</div>
                <div style="line-height:1.2; min-width:0;">
                    <div style="font-weight:700; color:#f8fafc;">{comment['author']}</div>
                    <div style="color:#94a3b8; font-size:0.85rem;">{comment['timestamp']}</div>
                </div>
                <div style="margin-left:auto; color:#60a5fa; font-size:0.88rem;">Reply</div>
            </div>
            <div style="margin-top:0.9rem; color:#e2e8f0; font-size:0.95rem; line-height:1.65;">{comment['content']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_comment_thread(comments, title='Comment thread'):
    """Render a forum-style comment thread."""
    st.markdown(f"### {title}")
    if not comments:
        st.info('No comments yet. Start the conversation!')
        return

    for comment in comments:
        _render_comment_card(comment)
        for reply in comment.get('replies', []):
            _render_comment_card(reply, nested=True)


def compute_trade_metrics(trades_list):
    """Return aggregate statistics for a list of trades."""
    total_trades = len(trades_list)
    total_volume = sum(t.get('quantity', 0) for t in trades_list)
    total_value = sum(t.get('quantity', 0) * t.get('price', 0) for t in trades_list)
    return {
        'total_trades': total_trades,
        'total_volume': total_volume,
        'total_value': total_value,
    }


def display_trade_summary(trades_list):
    """Render a summary view and table for a user's trades.

    Metrics are calculated via :func:`compute_trade_metrics`. The raw trade
    data is then displayed with ``st.table``.
    """
    if not trades_list:
        st.write("No trades available.")
        return
    metrics = compute_trade_metrics(trades_list)
    st.header("Trade Summary")
    st.metric("Total trades", metrics['total_trades'])
    st.metric("Total volume", metrics['total_volume'])
    st.metric("Total value", f"${metrics['total_value']:.2f}")
    st.table(trades_list)


def display_individual_bet_summary(
    bet_id: str,
    bet_name: str,
    bet_image_link: str | None,
    yes_value: float,
    no_value: float,
    yes_percent: float,
    no_percent: float,
    rules: str,
):
    """Displays an individual bet summary card and handles bet submission.

    This component renders the bet details and provides UI for placing a bet.
    On submission, it calls the database to record the new active bet and
    displays a success or failure notification.

    Parameters:
        bet_id (str): ID of the bet.
        bet_name (str): Display name of the bet.
        bet_image_link (str | None): URL to the bet image.
        yes_value (float): Dollar value for a Yes share.
        no_value (float): Dollar value for a No share.
        yes_percent (float): Implied probability % for Yes.
        no_percent (float): Implied probability % for No.
        rules (str): Description / rules text for the bet.
    """
    if not st.session_state.get('logged_in') or not st.session_state.get('username'):
        st.warning("Please log in to place bets.")
        return

    component_value = _bet_summary_component(
        bet_id=bet_id,
        bet_name=bet_name,
        bet_image_link=bet_image_link,
        yes_value=f"{yes_value:.2f}",
        no_value=f"{no_value:.2f}",
        yes_percent=f"{yes_percent:.0f}",
        no_percent=f"{no_percent:.0f}",
        rules=rules,
        key=f"bet_summary_{bet_id}"
    )

    # This block now receives real data from the component's frontend
    if isinstance(component_value, dict) and component_value.get('action') == 'submit_transaction':
        user_id = st.session_state.get('username', 'user1')
        user_took_yes = (component_value['choice'] == 'Yes')
        wager_amount = component_value['amount']
        mode = component_value.get('mode', 'Buy')

        success, message = process_bet_transaction(
            user_id=user_id,
            bet_id=bet_id,
            user_took_yes=user_took_yes,
            wager_amount=wager_amount,
            mode=mode,
            bet_name=bet_name
        )

        if success:
            st.toast(message, icon="✅")
        else:
            st.toast(message, icon="❌")

def filter_bets_by_category(bets_list, selected_category):
    """Return bets matching selected category, or all bets if "All" or None."""
    if selected_category is None or selected_category == "All":
        return bets_list
    return [bet for bet in bets_list if bet.get("category") == selected_category]


def display_recent_workouts(workouts_list):
    """Placeholder for recent-workouts widget; currently unused.

    The function is defined so that imports in other files don't break while the
    feature is not implemented.  It will only render text if the list is
    non-empty.
    """
    if workouts_list:
        st.write("Recent workouts placeholder")


def display_genai_advice(timestamp, content, image):
    """
    Calls the AI Advice page logic to display content within the dashboard.
    """
    page_path = os.path.join("pages", "3_AI_Advice.py")
    
    if os.path.exists(page_path):
        # Dynamically load the module because the filename starts with a number
        spec = importlib.util.spec_from_file_location("ai_advice_page", page_path)
        ai_advice_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_advice_module)
        
        # Call the main function from 3_AI_Advice.py 
        if hasattr(ai_advice_module, "main"):
            ai_advice_module.main()
        else:
            st.error("Could not find a main() function in 3_AI_Advice.py")
    else:
        st.error(f"File not found: {page_path}")


def format_friends_activity_text(friends):
    """Return a readable summary sentence for friends betting."""
    if not friends:
        return "No friends betting yet"
    if len(friends) == 1:
        return f"{friends[0]} is betting"
    if len(friends) == 2:
        return f"{friends[0]} and {friends[1]} are betting"
    if len(friends) == 3:
        return f"{friends[0]}, {friends[1]}, and {friends[2]} are betting"
    return f"{friends[0]}, {friends[1]}, and {len(friends) - 2} others are betting"


def display_friends_activity_card(bet):
    """Renders a card for friends' activity as seen in mockups."""
    with st.container(border=True):
        st.caption(bet.get('category', 'Category').upper())
        st.markdown(f"### {bet['bet_name']}")
        
        # Percentages and Prices
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<span style='color:#00ff88; font-weight:bold;'>Yes {bet['yes_percent']:.0f}%</span>", unsafe_allow_html=True)
            st.caption(f"${bet['yes_value']:.2f}")
        with c2:
            st.markdown(f"<span style='color:#ff4b4b; font-weight:bold;'>No {bet['no_percent']:.0f}%</span>", unsafe_allow_html=True)
            st.caption(f"${bet['no_value']:.2f}")
            
        st.divider()
        
        # Friends text
        friends = bet.get('friends', []) or []
        friend_count = len(friends)
        friend_count_text = (
            f"{friend_count} friend{'s' if friend_count != 1 else ''} betting"
            if friend_count > 0
            else "No friends betting yet"
        )
        st.caption(friend_count_text)
        st.caption(format_friends_activity_text(friends))
        
        # Navigation to individual bet view in home.py
        if st.button("View Details", key=f"view_{bet['bet_id']}", use_container_width=True):
            st.session_state.selected_bet_id = bet['bet_id']
            st.session_state.show_individual = True
            st.switch_page("home.py")


def render_sidebar():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = 'user1'

    with st.sidebar:
        try:
            st.image("static/images/airbets-logo.svg", width=48)
        except Exception:
            pass

        st.markdown(
            '<div style="display:flex; align-items:center; gap:8px; margin-bottom:0.75rem;">'
            '<span style="font-size:1.25rem; font-weight:700;">AirBets</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        balance = 10000.0
        if st.session_state.logged_in:
            try:
                profile = get_user_profile(st.session_state.username)
                balance = float(profile.get('balance', balance))
            except Exception:
                balance = 10000.0

        st.metric('Wallet balance', f'${balance:,.2f}')
        st.markdown('---')

        if st.button('🏠 Community', key='sidebar_community', use_container_width=True):
            st.switch_page('home.py')
        if st.button('📈 Marketplace', key='sidebar_marketplace', use_container_width=True):
            st.switch_page('pages/1_Available_bets.py')
        if st.button('🤖 AI Insights', key='sidebar_ai_insights', use_container_width=True):
            st.switch_page('pages/3_AI_Advice.py')

        st.markdown('---')
        if st.button('👤 My Profile', key='sidebar_my_profile', use_container_width=True):
            st.switch_page('pages/5_Profile.py')
