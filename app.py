import sys
from pathlib import Path

# Ensure project root is in sys.path BEFORE any src imports
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from src.execution_engine import execute_with_self_correction

# Page Configuration
st.set_page_config(
    page_title="SQLMind AI - Text-to-SQL Assistant",
    page_icon="🤖",
    layout="wide"
)

# Sidebar Information
with st.sidebar:
    st.header("⚙️ System Architecture")
    st.markdown("""
    - **LLM Engine:** Groq Cloud / Local LLM
    - **Vector Store:** ChromaDB (`all-MiniLM-L6-v2`)
    - **Database:** PostgreSQL (Neon Cloud)
    - **Features:** Automated Schema Reflection & Self-Correction Loop
    """)
    st.markdown("---")
    st.markdown("### 💡 Sample Prompts")
    st.markdown("- List all customers living in Coimbatore.")
    st.markdown("- Show all orders with their status.")
    st.markdown("- What products are in the electronics category?")

# Main Interface Header
st.title("🤖 SQLMind AI")
st.caption("Your local, privacy-first, self-correcting Text-to-SQL database agent.")

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Prior Messages from Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message and message["sql"]:
            st.code(message["sql"], language="sql")
        if "df" in message and not message["df"].empty:
            st.dataframe(message["df"], use_container_width=True)

# User Chat Input Box
if user_query := st.chat_input("Ask a question about your e-commerce database..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    if user_query.strip().lower() in ["hi", "hello", "hey"]:
        response_text = "Hello! I'm SQLMind AI. Ask me a question about your e-commerce database (e.g., 'List all customers living in Coimbatore')."
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "sql": None,
            "df": pd.DataFrame()
        })
    else:
        full_prompt = user_query
        if len(st.session_state.messages) > 1:
            prev_user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
            if len(prev_user_msgs) > 1:
                full_prompt = f"Previous context: {prev_user_msgs[-2]}. Current question: {user_query}"

        with st.chat_message("assistant"):
            with st.spinner("Reflecting schema, generating SQL, and running self-correction loop..."):
                try:
                    final_sql, results_df = execute_with_self_correction(full_prompt)
                    
                    response_text = "Here is the executable SQL query and the results fetched from your database:"
                    st.markdown(response_text)
                    st.code(final_sql, language="sql")
                    
                    if not results_df.empty:
                        st.dataframe(results_df, use_container_width=True)
                    else:
                        st.info("The query executed successfully, but returned 0 rows.")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sql": final_sql,
                        "df": results_df
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error executing pipeline: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sql": None,
                        "df": pd.DataFrame()
                    })