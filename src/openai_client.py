import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Default to GPT-4o, but can be changed
MODEL_NAME = "gpt-4o"

def prepare_therapy_context(messages, current_speaker):
    """
    Prepare the context for the therapy session, including conversation history
    and information about the current speaker.
    """
    # Start with system message that instructs the model how to behave
    system_message = {
        "role": "system", 
        "content": """You are a skilled and empathetic roommate mediator with years of experience helping people navigate shared living situations.
Your role is to facilitate a constructive conversation between roommates who are seeking help with their living arrangement issues.
- Always maintain a neutral, non-judgmental stance
- Recognize and acknowledge the feelings of both roommates
- Help identify common roommate problems like chore distribution, noise levels, personal space, shared expenses, and guest policies
- Suggest practical solutions for common roommate conflicts
- Ask clarifying questions when needed
- Provide insights based on what you've heard from both roommates
- Remember details about each roommate and reference them appropriately
- Recognize who is currently speaking to you

You should address the current speaker directly while keeping in mind the context of the entire conversation.
"""
    }
    
    # Convert the message history into a format suitable for OpenAI
    formatted_messages = [system_message]
    
    for msg in messages:
        if msg["role"] == "user":
            # Extract the speaker name from the content (format is "**Speaker**: message")
            content = msg["content"]
            formatted_messages.append({"role": "user", "content": content})
        elif msg["role"] == "assistant":
            formatted_messages.append({"role": "assistant", "content": msg["content"]})
    
    # Add information about who is currently speaking
    formatted_messages.append({
        "role": "system",
        "content": f"The current speaker is {current_speaker}. Address your response to them specifically."
    })
    
    return formatted_messages

def get_response(messages):
    """
    Send a request to the OpenAI API and get a response.
    """
    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"
