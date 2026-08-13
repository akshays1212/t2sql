

import streamlit as st
from dotenv import load_dotenv

from llm_config import get_llm
from sql_generator import write_sql_query
from database import run_query

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Text2SQL Chatbot",
    page_icon="🗄️",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🗄️ Text2SQL Chatbot")
st.caption("Ask questions about your database in plain English.")

st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_llm():
    """Load LLM model with caching."""
    return get_llm()


def answer_user_query_with_sql(query, llm):
    """Answer user query and return both SQL and response."""
    sql_chain = write_sql_query(llm)
    
    try:
        sql_query = sql_chain.invoke({"question": query})
        
        if sql_query.strip().upper() == "NO_VALID_QUERY":
            sql_response = "No valid query could be generated for this question."
        else:
            sql_response = run_query(sql_query)
        
        return {
            "query": sql_query,
            "answer": sql_response
        }
    
    except Exception as e:
        return {
            "query": "",
            "answer": f"Error: {str(e)}"
        }


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm" not in st.session_state:
    with st.spinner("⏳ Loading model..."):
        st.session_state.llm = load_llm()
    st.success("✓ Model loaded successfully!")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(msg["answer"])
            with st.expander("🔍 Generated SQL Query"):
                st.code(msg["query"], language="sql")
        else:
            st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask something about your database..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("🔄 Generating SQL and processing query..."):
            try:
                llm = st.session_state.llm
                
                result = answer_user_query_with_sql(user_input, llm)
                generated_sql = result["query"]
                answer = result["answer"]
                
                st.markdown(answer)
                with st.expander("🔍 Generated SQL Query"):
                    st.code(generated_sql, language="sql")
                
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "answer": answer,
                        "query": generated_sql,
                    }
                )
            except Exception as e:
                err = f"❌ Error: {str(e)}"
                st.error(err)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "answer": err,
                        "query": "",
                    }
                )

# Sidebar
with st.sidebar:
    st.markdown("### 📋 About")
    st.markdown("""
    This chatbot converts natural language questions into SQL queries.
    
    **How it works:**
    1. You ask a question in English
    2. The LLM generates an appropriate SQL query
    3. The query is executed against the Chinook database
    4. Results are displayed in natural format
    
    **Database:** Chinook (Music Store Database)
    """)
    
    st.markdown("### 🎯 Example Queries")
    examples = [
        "List all tracks by Audioslave",
        "Show the 3 longest tracks by duration",
        "Which playlists contain the track 'Balls to the Wall'?",
        "List all albums by Taylor Swift",
    ]
    for example in examples:
        st.caption(f"• {example}")
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
