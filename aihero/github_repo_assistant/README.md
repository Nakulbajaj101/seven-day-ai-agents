# GitHub Repo Assistant 🤖

An advanced Agentic RAG application that allows you to chat with any public GitHub repository's documentation as if it were a knowledgeable pair programmer.

## 🌟 Features

- **Instant Indexing**: Automatically downloads, parses, and indexes markdown/text files from a public GitHub repository.
- **Agentic RAG**: Powered by `pydantic-ai` and `MinSearch` for accurate retrieval and context-aware answers.
- **Modern UI**: A clean, Gemini-inspired Streamlit interface with a light theme and enhanced readability.
- **History Aware**: Maintains context across your conversation session.
- **Source Citations**: Provides links back to the original source files in GitHub.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Recommended for package management)
- OpenAI API Key

### Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository_url>
    cd github_repo_assistant
    ```

2.  **Install Dependencies**:

    Using `uv` (Fast & Recommended):
    ```bash
    uv sync
    ```

    Using standard `pip`:
    ```bash
    pip install -r requirements.txt
    ```

### ▶️ Running the Application

1.  **Set up Credentials** (Optional but recommended):
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```
    *Note: You can also enter the key in the specific sidebar input field if you prefer not to use environment variables.*

2.  **Launch the App**:
    ```bash
    uv run streamlit run main.py
    ```
    *Or with standard python:*
    ```bash
    streamlit run main.py
    ```

3.  **Access**:
    Open your browser to `http://localhost:8501`.

## 🧪 Running Tests

This project uses `pytest` for testing. The test suite covers ingestion logic and agent history persistence.

To run the full test suite:

```bash
uv run python -m pytest tests
```

## 📂 Project Structure

- `main.py`: The entry point for the Streamlit web application.
- `ingest.py`: Core logic for scraping GitHub and building the search index.
- `search_agent.py`: Definition of the AI agent, its system prompts, and tools.
- `search_tools.py`: Interface between the Agent and the MinSearch index.
- `logs.py`: Utilities for logging user interactions.
- `tests/`: Contains unit and integration tests.
