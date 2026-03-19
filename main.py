import streamlit as st
import requests
import hashlib
import os

# --- Configuration ---
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Define the 3 Modes
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

users_db = {"admin": hashlib.sha256("password".encode()).hexdigest()}

# --- Page Setup ---
st.set_page_config(page_title="Rapid LDR Chat", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mode' not in st.session_state:
    st.session_state.mode = "Profile Writer"

# --- Login Logic ---
if not st.session_state.logged_in:
    st.title("🤖 Rapid LDR Chat")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username in users_db and users_db[username] == hashlib.sha256(password.encode()).hexdigest():
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password")

# --- Main App Logic ---
else:
    # Header with Title and Logout
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.title("🤖 Rapid LDR Chat")
    with col_logout:
        st.write("") # Spacing
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    # --- MODE SELECTOR (AT THE TOP) ---
    # This creates a clean toolbar right under the title
    st.markdown("###") 
    cols = st.columns(3)
    
    for idx, (mode_name, details) in enumerate(MODES.items()):
        with cols[idx]:
            # Check if this is the current mode
            is_active = st.session_state.mode == mode_name
            if st.button(
                f"{details['icon']} {mode_name}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                # If clicked, switch mode and clear chat
                st.session_state.mode = mode_name
                st.session_state.messages = []
                st.rerun()

    st.divider() # Visual separation line

    # Display current mode status
    st.caption(f"Current Mode: **{st.session_state.mode}**")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Chat Input Logic ---
    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    current_system_prompt = MODES[st.session_state.mode]["prompt"]

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
