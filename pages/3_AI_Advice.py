
""" AI Advice page:  """
import streamlit as st
import os
from modules import display_genai_advice, render_sidebar


def main():
    
    # ---- Page config ----
    st.set_page_config(layout="wide", page_title="AI Advisor — AirBets")
    render_sidebar()

    # ---- Inline styles ----
    st.markdown("""
    <style>
    /* stat cards */

    .stat-card {
        background: #262730;
        border: 1px solid #31333f;
        border-top: 3px solid #28a745;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 0.5rem;
    }
    .stat-card-yellow {
        background: #262730;
        border: 1px solid #31333f;
        border-top: 3px solid #ffc107;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 0.5rem;
    }
    .stat-card-red {
        background: #262730;
        border: 1px solid #31333f;
        border-top: 3px solid #dc3545;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.68rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #8b8fa8;
        margin-bottom: 6px;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .stat-sub { font-size: 0.72rem; color: #8b8fa8; margin-top: 4px; }

    /* advice blocks */

    .advice-block {
        background: rgba(255,75,75,0.08);
        border-left: 3px solid #28a745;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .advice-block.analysis {
        background: rgba(255,209,106,0.07);
        border-left-color: #808080
    ;
    }
    .advice-block.tip {
        background: rgba(255,209,106,0.07);
        border-left-color: #ffd16a;
    }
    .advice-tag {
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #28a745;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .advice-tag-analysis{
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #808080;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .advice-block.tip .advice-tag { color: #ffd16a; }
    .advice-text { font-size: 0.85rem; line-height: 1.7; color: #fafafa; }


    /* chat bubbles */
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 0.85rem;
        line-height: 1.7;
    }
    .chat-bubble.user {
        background: rgba(255,75,75,0.1);
        border-left: 3px solid #ff4b4b;
    }
    .chat-bubble.ai {
        background: #262730;
        border: 1px solid #31333f;
    }
    .bubble-sender {
        font-size: 0.62rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
        color: #8b8fa8;
    }
    .bubble-sender.you { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

    # ---- Page heading ---
    st.markdown("## AI Advisor")
    st.caption("Personalized insights based on your trade history.")
    st.markdown("---")

    # ---- Stat Cards ----
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Total P&L</div>
            <div class="stat-value">+$342</div>
            <div class="stat-sub">18 total trades</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="stat-card-yellow">
            <div class="stat-label">Win Rate</div>
            <div class="stat-value">61%</div>
            <div class="stat-sub">11 wins · 7 losses</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="stat-card-red">
            <div class="stat-label">Open Positions</div>
            <div class="stat-value">3</div>
            <div class="stat-sub">Currently active</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ---- Two-column layout: advice + trade history ----
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### AI Analysis")

        st.markdown("""
        <div class="advice-block">
            <div class="advice-tag">Trend Insight</div>
            <div class="advice-text">
                Your win rate on <strong>political markets is 78%</strong> — well above your overall average.
                Consider allocating more of your bankroll to this category.
            </div>
        </div>

        <div class="advice-block ">
            <div class="advice-tag">Risk Flag</div>
            <div class="advice-text">
                You've placed <strong>3 bets on Tech earnings</strong> this week with an average stake of $40.
                Your historical loss rate in this category is 65% — consider reducing exposure.
            </div>
        </div>


        <div class="advice-block">
            <div class="advice-tag">Pattern Detected</div>
            <div class="advice-text">
                Friday bets account for <strong>40% of your losses</strong> but only 18% of total trades.
                You may want to avoid placing bets on Fridays.
            </div>
        </div>
           <div class="advice-block tip">
            <div class="advice-tag">Strategy Tip</div>
            <div class="advice-text">
                Your best trades close within <strong>48 hours</strong> of opening.
                Trades held longer than 5 days have a 70% loss rate — try tightening your exit window.
            </div>
        </div>

        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("### Recent Trades")

        # Placeholder trade rows 
        trades = [
            {"market": "BTC > $70k",     "stake": "$25", "pnl": "+$38", "result": "Win"},
            {"market": "Election 2025",  "stake": "$50", "pnl": "+$72", "result": "Win"},
            {"market": "NVDA Earnings",  "stake": "$30", "pnl": "-$30", "result": "Loss"},
            {"market": "Fed Rate Cut",   "stake": "$20", "pnl": "+$14", "result": "Win"},
            {"market": "AAPL Q2 Beat",   "stake": "$35", "pnl": "-$35", "result": "Loss"},
            {"market": "ETH Merge",      "stake": "$40", "pnl": "—",    "result": "Open"},
        ]
        result_colors = {
        "Win": "#28a745",   # Green
        "Loss": "#dc3545",  # Red
        "Open": "#ffc107"   # Yellow/Gold
    }

        for trade in trades:
            color = result_colors.get(trade['result'], "#ffffff") # Default to white if not found
        
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #444;">
                <span>{trade['market']}</span>
                <span style="color: {color}; font-weight: bold;">{trade['result']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

    # ---- Quick question buttons ----
    st.caption("Select a quick question or type your own below.")

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.button("Best category?",   use_container_width=True)
    with q2:
        st.button("Biggest risk?",    use_container_width=True)
    with q3:
        st.button("Top tip?",          use_container_width=True)
    with q4:
        st.button("Best day to bet?",  use_container_width=True)

    st.write("")

    # ---- Placeholder chat history ----
    st.markdown("""
    <div class="chat-bubble user">
        <div class="bubble-sender you">You</div>
        What is my riskiest habit?
    </div>
    <div class="chat-bubble ai">
        <div class="bubble-sender">AI Advisor</div>
        Your riskiest habit is over-trading Tech earnings markets. You've entered 8 positions
        in this category over the past month with a 65% loss rate — the highest of any category.
        Reducing your stake size here or skipping these markets entirely would have a meaningful
        impact on your overall P&L.
    </div>
    """, unsafe_allow_html=True)

    # ---- Chat input ----
    st.chat_input("Ask anything about your trades...", disabled=True)

if __name__ == "__main__":
    main()