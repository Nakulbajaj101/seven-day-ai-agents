import asyncio
import os

import streamlit as st

from ingest import index_data
from logs import log_interaction
from search_agent import init_agent

# 1. Page Configuration
st.set_page_config(
    page_title="GitHub Repo Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for Rich Aesthetics (Gemini/ChatGPT-like Light Theme)
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa; /* Light grey */
        border-right: 1px solid #e9ecef;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #1f1f1f;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #0b57d0; /* Gemini Blue */
        color: white;
        border: none;
        border-radius: 24px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .stButton > button:hover {
        background-color: #0842a0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }

    /* Headers */
    h1, h2, h3 {
        color: #1f1f1f !important;
        font-family: 'Google Sans', 'Heading Now', 'Helvetica Neue', sans-serif;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: transparent;
        border: none;
        padding: 15px 0;
    }
    
    /* Inline Code (e.g. `variable`) */
    :not(pre) > code {
        color: #c02d76 !important;
        background-color: #f1f3f4;
        padding: 2px 4px;
        border-radius: 4px;
        font-family: 'Fira Code', 'Consolas', monospace;
    }
    
    /* Code Blocks (Keep syntax highlighting) */
    .stCodeBlock {
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Ensure pre tags (blocks) don't get the inline pink color */
    pre code {
        color: inherit;
        background-color: transparent;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #0b57d0 transparent #0b57d0 transparent;
    }
    
    /* Custom container for aesthetic spacing */
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Session State Management
if "agent" not in st.session_state:
    st.session_state.agent = None
if "index" not in st.session_state:
    st.session_state.index = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "repo_info" not in st.session_state:
    st.session_state.repo_info = {"owner": "", "name": ""}
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# 4. Agent Initialization Helper
def load_and_index_repo(owner: str, name: str):
    """Indexes the repo and initializes the agent."""
    try:
        with st.spinner(f"✨ Indexing {owner}/{name}... Gathering intelligence."):
            # Check if we already have this index loaded to avoid re-indexing
            if (st.session_state.repo_info["owner"] == owner and 
                st.session_state.repo_info["name"] == name and 
                st.session_state.index is not None):
                st.success(f"✅ Repository {owner}/{name} is ready!")
                return st.session_state.agent

            # 1. Indexing
            try:
                index = index_data(repo_owner=owner, repo_name=name)
            except Exception as e:
                st.error(f"❌ Indexing Failed: {type(e).__name__}: {e}")
                return None

            # 2. Agent Initialization
            try:
                agent = init_agent(index=index, repo_owner=owner, repo_name=name)
            except Exception as e:
                st.error(f"❌ Agent Initialization Failed: {type(e).__name__}: {e}")
                return None
            
            # Update Session State
            st.session_state.index = index
            st.session_state.agent = agent
            st.session_state.repo_info = {"owner": owner, "name": name}
            st.session_state.messages = [] # Clear history on new repo
            st.session_state.conversation_history = [] # Clear agent history on new repo
            
            st.success(f"✅ Successfully indexed {owner}/{name}!")
            return agent
    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        return None

# 5. Sidebar Layout
with st.sidebar:
    st.title("Settings")
    st.caption("Configure your AI Pair Programmer")
    
    st.subheader("Repository")
    input_owner = st.text_input("Owner", value="evidentlyai", placeholder="e.g. facebook")
    input_name = st.text_input("Repo Name", value="docs", placeholder="e.g. react")
    
    st.subheader("Authentication")
    api_key = st.text_input("OpenAI API Key", type="password", help="Leave empty if set in env vars")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    st.write("") # Spacer
    if st.button("Initialize Agent", type="primary", use_container_width=True):
        if not input_owner or not input_name:
            st.warning("Please provide both Owner and Repository Name.")
        else:
            load_and_index_repo(input_owner, input_name)

    st.markdown("---")
    st.info("💡 **Tip:** Ask about architecture, functions, or specific logic in the codebase.")

# 6. Main UI Layout
st.title("GitHub Assistant")
st.markdown("#### Your Agentic RAG Companion")

if st.session_state.agent is None:
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px; color: #5f6368; background-color: #f8f9fa; border-radius: 12px; margin-top: 20px;'>
        <h2 style='color: #1f1f1f;'>👋 Ready to assist!</h2>
        <p style='font-size: 1.1em;'>Configure a repository in the sidebar to start chatting.</p>
        <p>I can explain code, find files, and answer architectural questions.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Header for active session
    st.caption(f"Active Repository: **{st.session_state.repo_info['owner']}/{st.session_state.repo_info['name']}**")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about the code..."):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Helper to run async pydantic-ai agent
                async def get_response(user_prompt, history):
                    result = await st.session_state.agent.run(
                        user_prompt,
                        message_history=history
                    )
                    return result

                with st.spinner("Thinking..."):
                    # Robust async handling for Streamlit
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None
                    
                    if loop and loop.is_running():
                        # This should not happen in standard Streamlit script execution, 
                        # but if it does, we can't use run_until_complete.
                        # We would need to use a future or nest_asyncio.
                        # For now, let's assume we can schedule and wait (which is hard in sync).
                        # We will try to rely on the fact that we are likely not in a running loop.
                        # But if we are, we try to wait on the task?
                        # Actually standard streamlit runs in a thread.
                        future = asyncio.run_coroutine_threadsafe(
                            get_response(prompt, st.session_state.conversation_history),
                            loop
                        )
                        result = future.result()
                    else:
                        # No running loop, safe to use asyncio.run
                        result = asyncio.run(get_response(prompt, st.session_state.conversation_history))
                
                response_text = result.output
                
                # Update conversation history with new messages from the agent run
                st.session_state.conversation_history.extend(result.new_messages())
                
                # Display final response
                st.markdown(response_text)
                
                # Log interaction
                try:
                    log_interaction(st.session_state.agent, result.new_messages_json(), source="git_assistant_web")
                except Exception as e:
                    print(f"Logging error: {e}")
                    
                full_response = response_text

            except Exception as e:
                full_response = f"⚠️ An error occurred: {str(e)}"
                st.error(full_response)
                import traceback
                traceback.print_exc()
            
            # Add assistant message to state
            st.session_state.messages.append({"role": "assistant", "content": full_response})
