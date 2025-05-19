import streamlit as st
import openai_client
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_speaker" not in st.session_state:
        st.session_state.current_speaker = "Roommate 1"
    if "roommate1_name" not in st.session_state:
        st.session_state.roommate1_name = "Roommate 1"
    if "roommate2_name" not in st.session_state:
        st.session_state.roommate2_name = "Roommate 2"
    if "custom_names_set" not in st.session_state:
        st.session_state.custom_names_set = False

def switch_speaker():
    if st.session_state.current_speaker == st.session_state.roommate1_name:
        st.session_state.current_speaker = st.session_state.roommate2_name
    else:
        st.session_state.current_speaker = st.session_state.roommate1_name

def main():
    st.title("AI Roommates Therapy")
    
    initialize_session()
    
    # Display session instructions
    st.markdown("""
    ### Welcome to AI Roommates Therapy
    This is a safe space for roommates to discuss living arrangement issues with the guidance of an AI therapist.
    - Each roommate takes turns speaking with the AI therapist
    - The AI will recognize who is speaking and maintain context
    - Discuss household responsibilities, shared spaces, noise levels, and other common roommate concerns
    - Be honest, respectful, and open to feedback
    """)
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            # For the AI therapist, use the brain emoji
            with st.chat_message(message["role"], avatar="🧠"):
                st.markdown(message["content"])
        else:
            # For user messages, use colored circle emojis
            # Determine which roommate is speaking
            if message["content"].startswith(f"**{st.session_state.roommate1_name}"):
                avatar = "🔴"  # Red circle for roommate 1
            else:
                avatar = "🔵"  # Blue circle for roommate 2
                
            # Display the message with the colored circle emoji
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    
    # Add AI therapist's introduction if this is the start of the conversation
    if not st.session_state.messages:
        therapist_intro = "Hello, I'm your AI therapist specializing in roommate relationships. I'm here to help you navigate common living arrangement challenges and improve your home environment. Who would like to start by sharing what roommate issue brings you here today?"
        st.session_state.messages.append({"role": "assistant", "avatar": "🧠", "content": therapist_intro})
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(therapist_intro)
    
    # Custom name and color input form (only shown at the beginning)
    if not st.session_state.custom_names_set:
        st.markdown("### 🏠 Customize Your Roommate Profiles")
        with st.form(key="roommate_profiles_form"):
            # First roommate settings
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h3 style='text-align:center;'>🔴 First Roommate</h3>", unsafe_allow_html=True)
                roommate1 = st.text_input("Name", value=st.session_state.roommate1_name, key="roommate1_name_input")
                
            # Second roommate settings
            with col2:
                st.markdown("<h3 style='text-align:center;'>🔵 Second Roommate</h3>", unsafe_allow_html=True)
                roommate2 = st.text_input("Name", value=st.session_state.roommate2_name, key="roommate2_name_input")
            
            # Add some spacing
            st.write("")
            st.write("")
            
            submit_button = st.form_submit_button(label="Save Profiles", use_container_width=True)
            
            if submit_button:
                if roommate1 and roommate2:
                    st.session_state.roommate1_name = roommate1
                    st.session_state.roommate2_name = roommate2
                    st.session_state.current_speaker = roommate1
                    st.session_state.custom_names_set = True
                    st.experimental_rerun()
                else:
                    st.error("Please enter names for both roommates.")
    
    # Modern speaker toggle
    st.markdown("### 🎙️ Who's Speaking Now?")
    
    # Custom CSS for better button styling
    st.markdown("""
    <style>
    /* Style for the red speaker button (left) */
    div[data-testid="stButton"] > button[kind="secondary"][data-testid="roommate1_button"] {
        background-color: transparent;
        color: #ff5252;
        border: 2px solid #ff5252;
        border-radius: 12px;
    }
    div[data-testid="stButton"] > button[kind="primary"][data-testid="roommate1_button"] {
        background-color: #ff5252;
        border: none;
        border-radius: 12px;
    }
    
    /* Style for the blue speaker button (right) */
    div[data-testid="stButton"] > button[kind="secondary"][data-testid="roommate2_button"] {
        background-color: transparent;
        color: #3b82f6;
        border: 2px solid #3b82f6;
        border-radius: 12px;
    }
    div[data-testid="stButton"] > button[kind="primary"][data-testid="roommate2_button"] {
        background-color: #3b82f6;
        border: none;
        border-radius: 12px;
    }
    
    /* Hover effects for all buttons */
    div[data-testid="stButton"] > button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a modern toggle with custom styling
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.write("")
    
    with col2:
        # Determine which roommate is active
        roommate1_active = st.session_state.current_speaker == st.session_state.roommate1_name
        roommate2_active = st.session_state.current_speaker == st.session_state.roommate2_name
        
        # We'll keep the emojis for the chat but not for the toggle buttons
        
        # Set button styles based on active state
        roommate1_style = "primary" if roommate1_active else "secondary"
        roommate2_style = "primary" if roommate2_active else "secondary"
        
        # Create the toggle buttons with Streamlit's native buttons
        toggle_cols = st.columns([5, 1, 5])
        
        with toggle_cols[0]:
            if st.button(f"{st.session_state.roommate1_name}", type=roommate1_style, use_container_width=True, key="roommate1_button"):
                if not roommate1_active:
                    st.session_state.current_speaker = st.session_state.roommate1_name
                    st.experimental_rerun()
        
        with toggle_cols[1]:
            st.write("")
            
        with toggle_cols[2]:
            if st.button(f"{st.session_state.roommate2_name}", type=roommate2_style, use_container_width=True, key="roommate2_button"):
                if not roommate2_active:
                    st.session_state.current_speaker = st.session_state.roommate2_name
                    st.experimental_rerun()
    
    with col3:
        st.write("")
    
    # Get user text input with personalized placeholder
    if prompt := st.chat_input(f"Type your message as {st.session_state.current_speaker}..."):
        # Add user message to chat history
        speaker = st.session_state.current_speaker
        
        # Use colored circle emojis based on roommate
        if speaker == st.session_state.roommate1_name:
            # Map custom color to closest standard emoji color
            avatar = "🔴"  # Red circle for roommate 1
        else:
            avatar = "🔵"  # Blue circle for roommate 2
        
        user_message = f"**{speaker}**: {prompt}"
        st.session_state.messages.append({"role": "user", "avatar": avatar, "content": user_message})
        
        # Display user message
        with st.chat_message("user", avatar=avatar):
            st.markdown(user_message)
        
        # Prepare context for the AI model
        formatted_messages = openai_client.prepare_therapy_context(st.session_state.messages, st.session_state.current_speaker)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🧠"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream of response with a spinner
            with st.spinner("Therapist is thinking..."):
                response = openai_client.get_response(formatted_messages)
            
            # Display the response word by word
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "avatar": "🧠", "content": response})

if __name__ == "__main__":
    main()
