# AI Roommates Therapy Bot

An AI-powered therapy assistant designed to help roommates resolve conflicts and improve their living situation. This application provides a neutral mediator to facilitate constructive conversations about common roommate issues like chore distribution, noise levels, personal space, and shared expenses.

## Features

- Interactive conversation with an AI mediator specialized in roommate issues
- Maintains conversation context and history between roommates
- Provides therapeutic insights and practical solutions for common roommate conflicts
- Easy speaker switching to facilitate balanced conversations
- Modern web interface built with Streamlit
- Powered by Ollama's llama3 model for natural language understanding

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- The `llama3` model downloaded in Ollama

## Installation

1. Clone this repository

   ```bash
   git clone https://github.com/yourusername/roommates-therapy-bot.git
   cd roommates-therapy-bot
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure Ollama is running with the llama3 model:

   ```bash
   # In a separate terminal window
   ollama run llama3
   ```

## Usage

1. Start the application using the provided run script:

```bash
./run.sh
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Using the application:
   - The AI therapist will introduce itself and ask who wants to start
   - Use the "Switch to Roommate X" button to change who is speaking
   - Type your message in the text input field and press Enter
   - The AI will provide insights and suggestions for resolving roommate conflicts
   - Continue the conversation, switching between roommates as needed

## How It Works

This application uses several technologies to create an effective roommate therapy experience:

### AI Therapy Process

1. **Conversation Tracking**: The system maintains a history of the conversation between roommates, including who said what.

2. **Context Building**: The conversation history, along with information about the current speaker, is formatted into a context prompt for the AI.

3. **LLM Processing**: Ollama's llama3 model processes the context with specific instructions to act as a roommate mediator.

4. **Response Generation**: The AI generates therapeutic responses tailored to roommate issues, providing insights and practical solutions.

### Technical Components

1. **Streamlit Interface**: Provides a clean, interactive web interface for the conversation.

2. **Ollama Integration**: Connects to a locally running Ollama instance to access the llama3 language model.

3. **Speaker Management**: Tracks which roommate is currently speaking and maintains context throughout the conversation.

4. **Response Streaming**: Displays the AI's responses in a natural, word-by-word manner to create a more conversational feel.

## Customization

You can customize various aspects of the application:

- **Therapist Personality**: Modify the system prompt in `ollama_client.py` to change the mediator's personality or approach
- **UI Appearance**: Customize the Streamlit interface in `app.py`
- **LLM Parameters**: Adjust temperature, top_p, and other parameters in the `get_response` function in `ollama_client.py`
- **Different Model**: Change the `MODEL_NAME` variable in `ollama_client.py` to use a different Ollama model

## Contributing

Contributions are welcome! Here's how you can contribute to this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
