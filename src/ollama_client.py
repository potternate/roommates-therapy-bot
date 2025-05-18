import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def prepare_therapy_context(messages, current_speaker):
    """
    Prepare the context for the therapy session, including conversation history
    and information about the current speaker.
    """
    # Start with system prompt that instructs the model how to behave
    system_prompt = """You are a skilled and empathetic roommate mediator with years of experience helping people navigate shared living situations.
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

    # Convert the message history into a format suitable for the model
    conversation_history = []
    for msg in messages:
        if msg["role"] == "user":
            conversation_history.append(msg["content"])
        elif msg["role"] == "assistant":
            conversation_history.append(f"Therapist: {msg['content']}")
    
    # Add information about who is currently speaking
    context = f"{system_prompt}\n\nConversation history:\n"
    context += "\n".join(conversation_history)
    context += f"\n\nCurrent speaker: {current_speaker}\n\nYour response as the therapist:"
    
    return context

def get_response(prompt):
    """
    Send a request to the Ollama API and get a response.
    """
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 1024
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {str(e)}"
    except (KeyError, json.JSONDecodeError):
        return "Error: Received invalid response from Ollama"
