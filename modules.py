#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import streamlit as st
from internals import create_component


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
    bet_name: str,
    bet_image_link: str | None,
    yes_value: float,
    no_value: float,
    yes_percent: float,
    no_percent: float,
    rules: str,
):
    """Displays an individual bet summary card containing a bet title, image (or "No Image Available" fallback), Buy/Sell mode toggle buttons, Yes/No choice toggle buttons, a rules description, and a transaction button. 
    The card defaults to Buy Mode and Yes Mode on load; clicking Buy or Sell updates the active mode border highlight and changes the transaction button's color and label accordingly, while clicking Yes or No similarly toggles the choice highlight. 
    An amount input field validates that the entered dollar value is greater than $0.00, and clicking the transaction button displays a "Transaction Successful" toast popup reflecting the current mode, choice, and amount.

    Parameters:
        bet_name       : Display name of the bet
        bet_image_link : URL to the bet image (or None / empty string)
        yes_value      : Dollar value for a Yes share
        no_value       : Dollar value for a No share
        yes_percent    : Implied probability % for Yes
        no_percent     : Implied probability % for No
        rules          : Description / rules text for the bet
    """
    # Build the image HTML — either an <img> tag or a "No Image Available" fallback
    if bet_image_link:
        image_html = f'<img src="{bet_image_link}" alt="Bet image" />'
    else:
        image_html = "No Image Available"

    data = {
        'BET_NAME':    bet_name,
        'IMAGE_HTML':  image_html,
        'YES_VALUE':   f"{yes_value:.2f}",
        'NO_VALUE':    f"{no_value:.2f}",
        'YES_PERCENT': f"{yes_percent:.0f}",
        'NO_PERCENT':  f"{no_percent:.0f}",
        'RULES':       rules,
    }

    html_file_name = "individual_bet_summary"
    create_component(data, html_file_name, height=700)


def display_recent_workouts(workouts_list):
    """Placeholder for recent-workouts widget; currently unused.

    The function is defined so that imports in other files don't break while the
    feature is not implemented.  It will only render text if the list is
    non-empty.
    """
    if workouts_list:
        st.write("Recent workouts placeholder")


def display_genai_advice(timestamp, content, image):
    """Placeholder for GenAI advice component; currently unused."""
    st.write(f"Advice ({timestamp}): {content}")
