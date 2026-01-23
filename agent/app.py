"""
Streamlit UI for Mobile Analytics AI Agent.

Usage:
    uv run streamlit run agent/app.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from agent.agent import chat, OPENAI_MODEL

# Page config
st.set_page_config(
    page_title="Ameno Analytics Agent",
    page_icon="📊",
    layout="wide",
)

# Header
st.title("📊 Ameno Technologies - Analytics Agent")
st.caption(f"AI-powered mobile app performance analysis | Model: {OPENAI_MODEL}")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI agent helps analyze mobile app performance data from Snowflake.

    **Capabilities:**
    - Query revenue, cost, and user metrics
    - Calculate ROAS, CPI, eCPM
    - Compare apps and countries
    - Identify profitable/losing segments

    **Data Range:**
    Dec 25, 2025 - Jan 22, 2026
    """)

    st.divider()

    st.header("Quick Questions")
    quick_questions = [
        "What's our total revenue and ROAS?",
        "Which apps are most profitable?",
        "Which apps are losing money?",
        "Top 5 countries by revenue?",
        "Compare Thailand vs Vietnam ROAS",
    ]

    for q in quick_questions:
        if st.button(q, key=f"quick_{q}", use_container_width=True):
            st.session_state.pending_question = q

    st.divider()

    # New conversation button
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"streamlit_{st.session_state.get('thread_count', 0) + 1}"
        st.session_state.thread_count = st.session_state.get('thread_count', 0) + 1
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit_1"
    st.session_state.thread_count = 1

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle pending question from sidebar
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = chat(prompt, st.session_state.thread_id)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask about app performance..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = chat(prompt, st.session_state.thread_id)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.caption("Built for Ameno Technologies | Capstone Project 2026")
