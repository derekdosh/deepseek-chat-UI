import streamlit as st
import requests
import hashlib

# YOUR DEEPSEEK API KEY - Added directly
DEEPSEEK_API_KEY = "sk-4547a326aa734ebdafb53bdd48a10b51"

# Simple user auth
users_db = {"admin": hashlib.sha256("password".encode()).hexdigest()}

st.title("🤖 My DeepSeek Bot")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Login form
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
else:
    # Logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask something..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call DeepSeek API directly with your key
                    response = requests.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant."},
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
