# GitHub Repo Assistant

A powerful Agentic RAG application that allows you to chat with any GitHub repository's documentation.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.12%2B-blue)

## 1. Overview

**GitHub Repo Assistant** solves the problem of navigating complex codebases. Instead of manually searching through endless markdown files, you can simply ask questions. It scrapes a repository, builds a local index, and uses an AI agent to provide context-aware answers with citations.

**Why it's useful:**
- ⚡️ **Instant Answers**: Stop `ctrl+f` searching.
- 🧠 **Context Aware**: Understands the structure of the documentation.
- 🔗 **Citable**: Always links back to the source file.

*(Placeholder for Screenshot/GIF)*

## 2. Installation

### Requirements
- **Python**: 3.12 or higher
- **Operating System**: macOS / Linux / Windows
- **API Key**: OpenAI API Key

### Step-by-Step Guide
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd github_repo_assistant
   ```

2. **Install Dependencies**:
   We recommend using `uv` for fast dependency management, but `pip` works too.

   **Using uv (Recommended):**
   ```bash
   uv sync
   ```

   **Using pip:**
   ```bash
   pip install -r requirements.txt
   ```

## 3. Usage

### Running Locally
To start the application, run the Streamlit server:

```bash
# Using uv
uv run streamlit run main.py

# Using standard python
streamlit run main.py
```

### How to Use
1. Open your browser to `http://localhost:8501`.
2. In the Sidebar, enter the **Repo Owner** (e.g., `evidentlyai`) and **Repo Name** (e.g., `docs`).
3. (Optional) Enter your OpenAI API Key if not set in your environment.
4. Click **Index Repository**.
5. Ask questions like "How do I install the package?" or "Explain the core architecture."

### 📊 Evaluation Dashboard
This project comes with a built-in evaluation tool to assess the quality of answers.

1. **Run the Evaluation Pipeline**:
   This processes logs in `evaluation_data/` using an LLM Judge (gpt-5-nano).
   ```bash
   uv run python evaluation.py
   ```

2. **View Results**:
   Launch the dedicated dashboard to visualize pass rates and inspect logs.
   ```bash
   uv run streamlit run evaluation_app.py
   ```

## 4. Features

- **Agentic RAG**: Powered by `pydantic-ai` for robust agent loops.
- **Local Indexing**: Uses `MinSearch` for fast, in-memory text search.
- **History Memory**: Remembers context from previous turn in the conversation.
- **Rich UI**: Gemini-inspired interface with dark/light mode support.
- **Source Citations**: Every answer includes links to the GitHub files used.
- **Evaluation Dashboard**: Built-in LLM Judge to benchmark answer quality against logged interactions.

## 5. Contributing

Contributions are welcome! Please follow these steps:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

**Coding Standards**:
- We use `pytest` for testing.
- Please ensure all new features are covered by tests.

## 6. Tests

We use `pytest` for unit and integration testing.

**Run all tests:**
```bash
uv run python -m pytest tests
```

**Run specific test file:**
```bash
uv run python -m pytest tests/test_ingest.py
```

## 7. Deployment

This application is built with Streamlit and is ready for deployment on:
- **Streamlit Cloud**: Simply connect your GitHub repo and set the `OPENAI_API_KEY` secret.
- **Docker**: Can be containerized (Dockerfile coming soon).

## 8. FAQ / Troubleshooting

**Q: I get an OpenAI Authentication Error.**
A: Ensure your `OPENAI_API_KEY` is set correctly in the sidebar or your environment variables (`export OPENAI_API_KEY=sk-...`).

**Q: The indexing takes a long time.**
A: Large repositories with many text files may take a minute to download and chunk. Check the terminal for progress logs.

## 9. Credits

- **Streamlit**: For the frontend framework.
- **Pydantic AI**: For the agentic framework.
- **MinSearch**: For the lightweight search engine.

## 11. Project Structure

A professional, modular architecture designed for scalability and maintainability.

```
github_repo_assistant/
├── main.py              # 🚀 Entry point for the RAG Chatbot
├── evaluation.py        # ⚖️ Evaluation pipeline (LLM Judge)
├── evaluation_app.py    # 📊 Dashboard for visualizing evaluation results
├── ingest.py            # 📥 Data ingestion and indexing logic
├── search_agent.py      # 🤖 Agent definition and logic
├── search_tools.py      # 🔍 Search engine integration tools
├── config.py            # ⚙️ Centralized configuration and prompts
├── logs.py              # 📝 Logging utilities
├── requirements.txt     # 📦 Dependency definitions
└── tests/               # 🧪 Unit and integration tests
```
