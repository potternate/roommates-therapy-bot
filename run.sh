#!/bin/bash

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found."
    echo "Creating a template .env file. Please edit it with your OpenAI API key."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo ""
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Warning: OpenAI API key not set in .env file."
    echo "Please edit the .env file and set your OpenAI API key."
    echo ""
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

# Run the application
echo "Starting AI Roommates Therapy Bot..."
echo "Open your browser to the URL shown below (typically http://localhost:8501)"
streamlit run src/app.py
