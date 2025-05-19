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
    if "roommate1_color" not in st.session_state:
        st.session_state.roommate1_color = "#FF5733"  # Default orange-red
    if "roommate2_color" not in st.session_state:
        st.session_state.roommate2_color = "#3366FF"  # Default blue
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
            # For user messages, create a custom avatar container
            message_container = st.container()
            # Display the message content
            with message_container.chat_message(message["role"]):
                st.markdown(message["content"])
            # Insert the HTML avatar (this is a bit of a hack since Streamlit doesn't directly support HTML in avatars)
            message_container.markdown(f"""
            <style>
            [data-testid="stChatMessageAvatar"] {{display: none;}}  /* Hide the default avatar */
            .custom-avatar {{position: absolute; top: 0; left: 0; width: 2rem; height: 2rem; margin: 0.5rem; z-index: 1;}}  /* Position our custom avatar */
            </style>
            <div class="custom-avatar">{message["avatar"]}</div>
            """, unsafe_allow_html=True)
    
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
            st.subheader("First Roommate")
            col1, col2 = st.columns([3, 1])
            with col1:
                roommate1 = st.text_input("Name", value=st.session_state.roommate1_name)
            with col2:
                roommate1_color = st.color_picker("Icon Color", value=st.session_state.roommate1_color)
                
            # Second roommate settings
            st.subheader("Second Roommate")
            col1, col2 = st.columns([3, 1])
            with col1:
                roommate2 = st.text_input("Name", value=st.session_state.roommate2_name)
            with col2:
                roommate2_color = st.color_picker("Icon Color", value=st.session_state.roommate2_color)
            
            # Preview of how the icons will look
            st.markdown("### Preview")
            preview_cols = st.columns(2)
            with preview_cols[0]:
                st.markdown(f"<div style='width:50px;height:50px;border-radius:50%;background-color:{roommate1_color};display:flex;align-items:center;justify-content:center;margin:0 auto;color:white;font-weight:bold;'>{roommate1[0] if roommate1 else '?'}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center'>{roommate1}</p>", unsafe_allow_html=True)
            with preview_cols[1]:
                st.markdown(f"<div style='width:50px;height:50px;border-radius:50%;background-color:{roommate2_color};display:flex;align-items:center;justify-content:center;margin:0 auto;color:white;font-weight:bold;'>{roommate2[0] if roommate2 else '?'}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center'>{roommate2}</p>", unsafe_allow_html=True)
            
            submit_button = st.form_submit_button(label="Save Profiles", use_container_width=True)
            
            if submit_button:
                if roommate1 and roommate2:
                    st.session_state.roommate1_name = roommate1
                    st.session_state.roommate2_name = roommate2
                    st.session_state.roommate1_color = roommate1_color
                    st.session_state.roommate2_color = roommate2_color
                    st.session_state.current_speaker = roommate1
                    st.session_state.custom_names_set = True
                    st.experimental_rerun()
                else:
                    st.error("Please enter names for both roommates.")
    
    # Modern speaker toggle
    st.markdown("### 🎙️ Who's Speaking Now?")
    
    # Create a modern toggle with emojis and styling
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.write("")
    
    with col2:
        toggle_cols = st.columns([5, 1, 5])
        
        # First roommate button with color icon
        roommate1_active = st.session_state.current_speaker == st.session_state.roommate1_name
        roommate1_style = "primary" if roommate1_active else "secondary"
        
        # Second roommate button with color icon
        roommate2_active = st.session_state.current_speaker == st.session_state.roommate2_name
        roommate2_style = "primary" if roommate2_active else "secondary"
        
        # Create colored circle icons with first letter of name
        roommate1_icon = f"<div style='display:inline-flex;width:25px;height:25px;border-radius:50%;background-color:{st.session_state.roommate1_color};align-items:center;justify-content:center;color:white;font-weight:bold;margin-right:5px;'>{st.session_state.roommate1_name[0]}</div>"
        roommate2_icon = f"<div style='display:inline-flex;width:25px;height:25px;border-radius:50%;background-color:{st.session_state.roommate2_color};align-items:center;justify-content:center;color:white;font-weight:bold;margin-right:5px;'>{st.session_state.roommate2_name[0]}</div>"
        
        with toggle_cols[0]:
            # Using a container to wrap the button and allow HTML in it
            roommate1_container = st.container()
            roommate1_btn = roommate1_container.button(st.session_state.roommate1_name, type=roommate1_style, use_container_width=True, key="roommate1_button")
            # Display the colored icon above the button
            roommate1_container.markdown(f"<div style='text-align:center;margin-bottom:-35px;position:relative;z-index:1;'>{roommate1_icon}</div>", unsafe_allow_html=True)
            if roommate1_btn and not roommate1_active:
                st.session_state.current_speaker = st.session_state.roommate1_name
                st.experimental_rerun()
        
        with toggle_cols[1]:
            st.write("")
            
        with toggle_cols[2]:
            # Using a container to wrap the button and allow HTML in it
            roommate2_container = st.container()
            roommate2_btn = roommate2_container.button(st.session_state.roommate2_name, type=roommate2_style, use_container_width=True, key="roommate2_button")
            # Display the colored icon above the button
            roommate2_container.markdown(f"<div style='text-align:center;margin-bottom:-35px;position:relative;z-index:1;'>{roommate2_icon}</div>", unsafe_allow_html=True)
            if roommate2_btn and not roommate2_active:
                st.session_state.current_speaker = st.session_state.roommate2_name
                st.experimental_rerun()
    
    with col3:
        st.write("")
    
    # Get user text input with personalized placeholder
    if prompt := st.chat_input(f"Type your message as {st.session_state.current_speaker}..."):
        # Add user message to chat history
        speaker = st.session_state.current_speaker
        
        # Create a colored circle avatar with the first letter of the roommate's name
        if speaker == st.session_state.roommate1_name:
            avatar_color = st.session_state.roommate1_color
        else:
            avatar_color = st.session_state.roommate2_color
            
        # Create HTML for the colored circle avatar
        avatar = f"<div style='width:100%;height:100%;border-radius:50%;background-color:{avatar_color};display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;'>{speaker[0]}</div>"
        
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
