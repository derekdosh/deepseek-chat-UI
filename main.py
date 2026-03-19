import streamlit as st
import requests
import hashlib
import os

# --- Configuration ---
# Get API key from Render environment variables
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Define the 3 Modes and their specific AI Personalities
MODES = {
    "Profile Writer": {
        "icon": "✍️",
        "prompt": "You are an expert dating profile writer. Your goal is to create witty, engaging, and authentic dating profiles. Ask the user about their interests, quirks, and what they are looking for, then craft the perfect bio."
    },
    "Rapid Messaging": {
        "icon": "💬",
        "prompt": "You are a rapid-response dating coach. Provide short, punchy, and effective replies for dating apps. Focus on keeping the conversation flowing naturally. Do not give long explanations, just give the text options."
    },
    "Reignite": {
        "icon": "🔥",
        "prompt": "You are a specialist in rekindling old connections. Help users craft low-pressure, intriguing messages to reconnect with past matches or old flames. Focus on nostalgia and curiosity."
    }
}

# Simple user auth
users_db = {"admin": hashlib.sha256("password".encode()).hexdigest()}

# --- Page Setup ---
st.set_page_config(page_title="Rapid LDR Chat", layout="wide")
st.title("🤖 Rapid LDR Chat")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mode' not in st.session_state:
    st.session_state.mode = "Profile Writer" # Default mode

# --- Login Logic ---
if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username in users_db and users_db[username] == hashlib.sha256(password.encode()).hexdigest():
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

# --- Main App Logic ---
else:
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
        
        # Display current status
        st.info(f"Current Mode: **{st.session_state.mode}**")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- FOOTER: Mode Selector ---
    # We create a separator and then 3 columns for the buttons
    st.markdown("---")
    
    # Create 3 equal columns
    col1, col2, col3 = st.columns(3)
    
    # Helper function to handle button clicks
    def set_mode(mode_name):
        st.session_state.mode = mode_name
        # Optional: Clear chat history when switching modes for a fresh start
        # st.session_state.messages = [] 

    with col1:
        # Check if this is the active mode to style it differently (disabled button look)
        is_active = st.session_state.mode == "Profile Writer"
        st.button(
            f"{MODES['Profile Writer']['icon']} Profile Writer", 
            use_container_width=True, 
            on_click=set_mode, 
            args=("Profile Writer",),
            disabled=is_active, # Visually indicates active state
            type="primary" if is_active else "secondary"
        )

    with col2:
        is_active = st.session_state.mode == "Rapid Messaging"
        st.button(
            f"{MODES['Rapid Messaging']['icon']} Rapid Messaging", 
            use_container_width=True, 
            on_click=set_mode, 
            args=("Rapid Messaging",),
            disabled=is_active,
            type="primary" if is_active else "secondary"
        )

    with col3:
        is_active = st.session_state.mode == "Reignite"
        st.button(
            f"{MODES['Reignite']['icon']} Reignite", 
            use_container_width=True, 
            on_click=set_mode, 
            args=("Reignite",),
            disabled=is_active,
            type="primary" if is_active else "secondary"
        )

    # --- Chat Input Logic ---
    if prompt := st.chat_input("Ask something..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Select the system prompt based on the current mode
                    current_system_prompt = MODES[st.session_state.mode]["prompt"]

                    # Call DeepSeek API
                    response = requests.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": current_system_prompt},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            "temperature": 0.7,
                            "max_tokens": 4096
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        bot_response = result["choices"][0]["message"]["content"]
                        st.markdown(bot_response)
                        st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
