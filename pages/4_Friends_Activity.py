import streamlit as st
from data_fetcher import get_friends_activity
from modules import display_friends_activity_card

# Set page config for the individual page
st.set_page_config(layout="wide", page_title="Friends Activity - AirBets")

st.title("Friends")
st.write("See what your crew is betting on")
st.markdown("---")

userId = st.session_state.get('username', 'user1')
activity = get_friends_activity(userId)

if not activity:
    st.info("None of your friends are currently betting.")
else:
    # Sort control: toggle between Most (Descending) and Least (Ascending)
    sort_most = st.toggle("Sort by most friends betting", value=True)
    
    # Sorting logic based on friend count
    activity.sort(key=lambda x: len(x['friends']), reverse=sort_most)
    
    # Render cards vertically as per mockup design
    for bet in activity:
        display_friends_activity_card(bet)

if st.button("← Back to Dashboard"):
    st.switch_page("app.py")