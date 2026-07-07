"""AI Analyst Dashboard Page."""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from ai.assistant import get_agent

st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")
st.title("🤖 AI Data Analyst")
st.markdown("Ask natural language questions about your retail platform. I will generate SQL, query the warehouse, and visualize the results!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            with st.expander("View Generated SQL"):
                st.code(msg["sql"], language="sql")
                if "execution_time" in msg:
                    st.caption(f"Execution Time: {msg['execution_time']}s")
        if "df" in msg and msg["df"] is not None:
            st.dataframe(msg["df"], use_container_width=True)
        if "chart" in msg and msg["chart"] is not None:
            st.plotly_chart(msg["chart"], use_container_width=True, key=f"chart_history_{idx}")

# Input
if prompt := st.chat_input("E.g., What are my top 5 selling products?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema and generating SQL..."):
            agent = get_agent()
            response = agent.process_query(prompt)
            
            if response["error"]:
                st.error(f"Error: {response['error']}")
                if response["sql"]:
                    with st.expander("Generated SQL that failed"):
                        st.code(response["sql"], language="sql")
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {response['error']}"})
            else:
                st.markdown(response["explanation"])
                with st.expander("View Generated SQL"):
                    st.code(response["sql"], language="sql")
                    st.caption(f"Execution Time: {response['execution_time']}s")
                st.dataframe(response["df"], use_container_width=True)
                if response["chart"]:
                    import uuid
                    st.plotly_chart(response["chart"], use_container_width=True, key=f"chart_new_{uuid.uuid4().hex}")
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["explanation"],
                    "sql": response["sql"],
                    "df": response["df"],
                    "chart": response["chart"],
                    "execution_time": response["execution_time"]
                })
