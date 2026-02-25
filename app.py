#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_individual_bet_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

    # Test display_individual_bet_summary
    display_individual_bet_summary(
        bet_name="Will Bitcoin hit $100k?",
        bet_image_link="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/240px-Bitcoin.svg.png",
        yes_value=0.72,
        no_value=0.28,
        yes_percent=72,
        no_percent=28,
        rules="Resolves YES if Bitcoin closes above $100,000 USD on any major exchange before Dec 31 2026.",
    )


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
