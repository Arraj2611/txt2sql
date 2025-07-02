import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="MCP Database Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("MCP Database Assistant 🤖")
st.caption("Your Master Control Program for interacting with the database.")

# API Endpoint
API_URL = "http://127.0.0.1:8000/query"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you with the database today?"}]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything about the database..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            # Send request to the MCP server
            response = requests.post(API_URL, json={"query": prompt})
            response.raise_for_status()
            
            # Get the result from the JSON response
            full_response = response.json().get("result", "Sorry, I encountered an error.")
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            error_message = f"Error connecting to the MCP Server: {e}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
        except json.JSONDecodeError:
            error_message = "Error: Invalid response from the server."
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message}) 