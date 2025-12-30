# GitHub Repo Assistant

An Agentic RAG application that allows you to chat with any GitHub repository's documentation.

## Features
- **Index GitHub Repos**: Automatically downloads and indexes markdown files from a public GitHub repository.
- **Agentic RAG**: Uses MinSearch for retrieval and OpenAI's GPT-4o-mini for answering questions.
- **Interactive UI**: Built with Streamlit for a smooth user experience.

## Setup

1. **Install Dependencies**:
   Ensure you have Python 3.12+ installed.
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

2. **Environment Variables**:
   Set your OpenAI API Key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   Alternatively, you can enter the API Key directly in the application sidebar.

3. **Run the App**:
   ```bash
   streamlit run main.py
   ```

## Usage
1. Open the app in your browser (usually `http://localhost:8501`).
2. Enter the **Repo Owner** and **Repo Name** (e.g., `evidentlyai` / `docs`).
3. Click **Index Repository**.
4. Start chatting!

## Architecture
- `main.py`: Streamlit frontend application.
- `ingest.py`: Handles downloading and indexing of repository content.
- `search_agent.py`: Configures the AI agent.
- `search_tools.py`: Connects MinSearch with the agent.
