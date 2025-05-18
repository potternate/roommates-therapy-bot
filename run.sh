#!/bin/bash

# Check for system dependencies on macOS
if [[ "$(uname)" == "Darwin" ]]; then
    if ! brew list portaudio &>/dev/null; then
        echo "Installing portaudio with Homebrew..."
        brew install portaudio
    fi
fi

# Make sure Ollama is running
if ! pgrep -x "ollama" > /dev/null
then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5  # Give Ollama time to start
fi

# Check if the model is available
if ! ollama list | grep -q "llama3"
then
    echo "Downloading llama3 model..."
    ollama pull llama3
fi

# Install dependencies if needed
if [ ! -d "venv" ]
then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies with pip
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
    
    # Check if we need to update dependencies
    if [[ requirements.txt -nt venv/last_update || ! -f venv/last_update ]]; then
        echo "Updating dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        touch venv/last_update
    fi
fi

# Check for HuggingFace token
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Warning: HF_TOKEN environment variable not set."
    echo "    Advanced speaker diarization will not be available."
    echo "    Get a token at https://huggingface.co and set it with:"
    echo "    export HF_TOKEN=your_token"
    echo ""
fi

# Run the application
echo "Starting AI Couples Therapy Bot - Voice Edition..."
echo "Open your browser to the URL shown below (typically http://localhost:8501)"
streamlit run src/app.py
