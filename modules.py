#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

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
    """Write a good docstring here."""
    pass


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
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
