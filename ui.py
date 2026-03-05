import streamlit as st
import requests
import time

# --- CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="Project Veritas",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (The "Beautiful" Part) ---
st.markdown("""
<style>
    /* 1. Main Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* 2. Chat Bubbles */
    .stChatMessage {
        background-color: #1E2329;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid #2B313E;
    }
    
    /* 3. Sidebar Style */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #2B313E;
    }
    
    /* 4. Glowing Title */
    h1 {
        color: #FFFFFF;
        text-shadow: 0 0 10px #4A90E2;
    }
    
    /* 5. Citations Box */
    .stExpander {
        border: 1px solid #4A90E2;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- API CONNECTIONS ---
JAVA_API_URL = "http://localhost:8080/api/chat"
PYTHON_UPLOAD_URL = "http://localhost:8000/ingest" 

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.title("📂 Knowledge Core")
    st.markdown("---")
    
    # CHANGE 1: Enable Multiple Files
    uploaded_files = st.file_uploader("Upload Evidence (PDFs)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🚀 Ingest All Data", type="primary"):
            with st.spinner("⚡ Neural Engine Processing..."):
                success_count = 0
                
                # CHANGE 2: Loop through all files
                for uploaded_file in uploaded_files:
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    try:
                        response = requests.post(PYTHON_UPLOAD_URL, files=files)
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            st.error(f"Failed to load {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
                
                if success_count == len(uploaded_files):
                    st.toast(f"✅ Successfully ingested {success_count} documents!", icon="🧠")
                    time.sleep(1)
    
    st.markdown("---")
    st.caption("🟢 System Status: **ONLINE**")
    st.caption("🔗 Model: **Llama-3 (Local)**")

# --- MAIN CHAT INTERFACE ---
st.title("🧠 Project Veritas")
st.markdown("#### *Autonomous Retrieval-Augmented Generation System*")

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Query the Neural Network..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Get AI Response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Thinking..."):
            try:
                payload = {"question": prompt}
                response = requests.post(JAVA_API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer_text = data.get("answer", "No answer found.")
                    citations = data.get("citations", {})

                    # <--- MOTION 3: Typewriter Effect
                    for char in answer_text:
                        full_response += char
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.005) # Speed of typing
                    
                    message_placeholder.markdown(full_response)
                    
                    # Show Citations
                    if citations:
                        with st.expander("📚 Verified Sources"):
                            for source, page in citations.items():
                                st.markdown(f"**{source}** (Page {page})")
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error(f"Java Backend Error: {response.status_code}")
            except Exception as e:
                st.error(f"Critical System Failure: {e}")