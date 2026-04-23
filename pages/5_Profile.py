import streamlit as st

from data_fetcher import (
    get_friends_activity,
    get_user_friends,
    get_user_profile,
    get_user_trades,
)
from modules import display_friends_activity_card, display_trade_summary, render_sidebar

st.set_page_config(layout="wide", page_title="Profile & Trade Summary - AirBets")

render_sidebar()

if not st.session_state.get('logged_in'):
    st.warning("Please log in to view your profile and place bets.")
    if st.button("← Back to Dashboard"):
        st.switch_page("home.py")
    st.stop()

user_id = st.session_state.get('username', 'user1')
try:
    profile = get_user_profile(user_id)
except ValueError:
    st.error("Profile not found.")
    if st.button("← Back to Dashboard"):
            st.switch_page("home.py")

left, right = st.columns([2, 3])
with left:
    st.image(profile.get('profile_image', ''), width=180)
    st.subheader(profile.get('full_name', profile.get('username', 'Unknown')))
    st.caption(f"@{profile.get('username', '')}")
    st.write(f"Born: {profile.get('date_of_birth', 'Unknown')}")
    st.metric("Paper balance", f"${profile.get('balance', 10000.0):,.2f}")
    st.markdown("---")
    st.markdown("### Friends list")
    friend_profiles = get_user_friends(user_id)
    if friend_profiles:
        for friend in friend_profiles:
            st.markdown(
                f"**{friend['full_name']}** — @{friend['username']}"
            )
    else:
        st.info("You have no friends added yet.")

with right:
    st.markdown("### Past bets")
    trades = get_user_trades(user_id)
    if trades:
        display_trade_summary(trades)
    else:
        st.info("No past bets found yet.")

st.markdown("---")
st.markdown("### Friends' current bets")
friend_activity = get_friends_activity(user_id)
if friend_activity:
    for bet in friend_activity:
        display_friends_activity_card(bet)
else:
    st.info("No friend bets available right now.")

if st.button("← Back to Dashboard"):
    st.switch_page("home.py")
