"""AI Analyst Dashboard Page."""

import sys
import os
import uuid
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from dashboard.components.layout import configure_page, render_header
from dashboard.components.charts import render_chart
from dashboard.components.tables import render_styled_dataframe
from dashboard.components.states import render_error_state
from ai.assistant import get_agent

configure_page("AI Copilot", "🤖")
render_header("Retail Intelligence Copilot", "Natural Language Data Analyst")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR FOR CONVERSATION CONTROLS ---
with st.sidebar:
    st.markdown("### 🛠️ Copilot Settings")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 💡 Example Prompts")
    examples = [
        "What are my top 5 selling products?",
        "Show me revenue by region over the last 30 days.",
        "Which customer segment has the highest CLV?",
        "What is the average order value by category?"
    ]
    for ex in examples:
        if st.button(ex, help="Click to run this query"):
            st.session_state.prompt_injection = ex

# Handle prompt injection from sidebar
prompt = st.chat_input("E.g., What are my top 5 selling products?")
if "prompt_injection" in st.session_state:
    prompt = st.session_state.prompt_injection
    del st.session_state.prompt_injection

# --- CHAT HISTORY ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        
        if "sql" in msg and msg["sql"]:
            with st.expander("📝 View Generated SQL"):
                st.code(msg["sql"], language="sql")
                if "execution_time" in msg:
                    st.caption(f"⏱️ Execution Time: {msg['execution_time']}s")
                    
        if "df" in msg and msg["df"] is not None:
            st.markdown("##### Data Results")
            render_styled_dataframe(msg["df"])
            
        if "chart" in msg and msg["chart"] is not None:
            st.markdown("##### Visual Insights")
            render_chart(msg["chart"], height=450)

# --- NEW CHAT INPUT ---
if prompt:
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Analyzing schema and generating SQL..."):
            agent = get_agent()
            response = agent.process_query(prompt)

            if response.get("error"):
                render_error_state("Copilot Error", Exception(response['error']))
                if response.get("sql"):
                    with st.expander("📝 Generated SQL that failed"):
                        st.code(response["sql"], language="sql")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"Sorry, I encountered an error: {response['error']}",
                    }
                )
            else:
                st.markdown(response["explanation"])
                
                with st.expander("📝 View Generated SQL"):
                    st.code(response["sql"], language="sql")
                    st.caption(f"⏱️ Execution Time: {response['execution_time']}s")
                
                if response.get("df") is not None:
                    st.markdown("##### Data Results")
                    render_styled_dataframe(response["df"])
                    
                if response.get("chart"):
                    st.markdown("##### Visual Insights")
                    render_chart(response["chart"], height=450)

                # Save to history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response["explanation"],
                        "sql": response["sql"],
                        "df": response["df"],
                        "chart": response["chart"],
                        "execution_time": response["execution_time"],
                    }
                )

