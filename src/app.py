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

def switch_speaker():
    if st.session_state.current_speaker == "Roommate 1":
        st.session_state.current_speaker = "Roommate 2"
    else:
        st.session_state.current_speaker = "Roommate 1"

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
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])
    
    # Add AI therapist's introduction if this is the start of the conversation
    if not st.session_state.messages:
        therapist_intro = "Hello, I'm your AI therapist specializing in roommate relationships. I'm here to help you navigate common living arrangement challenges and improve your home environment. Who would like to start by sharing what roommate issue brings you here today?"
        st.session_state.messages.append({"role": "assistant", "avatar": "🧠", "content": therapist_intro})
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(therapist_intro)
    
    # Speaker selection
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(f"Switch to {('Roommate 2' if st.session_state.current_speaker == 'Roommate 1' else 'Roommate 1')}"):
            switch_speaker()
    with col2:
        st.info(f"Currently speaking: {st.session_state.current_speaker}")
    
    # Get user text input
    if prompt := st.chat_input(f"Type your message here..."):
        # Add user message to chat history
        speaker = st.session_state.current_speaker
        avatar = "👤" if speaker == "Roommate 1" else "👥"
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
