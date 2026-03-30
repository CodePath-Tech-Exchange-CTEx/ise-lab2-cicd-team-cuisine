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
from data_fetcher import add_active_bet
import os

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

        success = add_active_bet(
            user_id=user_id,
            bet_id=bet_id,
            user_took_yes=user_took_yes,
            wager_amount=wager_amount
        )

        if success:
            st.toast("Transaction successfull!", icon="✅")
        else:
            st.error("Transaction failed. Please try again.")

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