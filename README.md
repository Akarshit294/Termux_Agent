# Termux Agent 🤖

A lightweight, LLM-powered assistant designed for Termux, featuring a modular Clean Architecture for system management and intelligent chat.

## 📂 Project Structure

```text
D:\Misc\Termux_Agent\
├── main.py                # Entry point: Bot initialization & Polling
├── database/              # Data Access Layer (Repositories)
│   ├── connection.py      # Centralized SQLite path management
│   ├── models.py          # Pydantic entities (ChatMessage, Task)
│   ├── task_manager_db.py # Task persistence logic
│   └── telegram_db.py     # Chat history persistence logic
├── database_files/        # Physical SQLite Storage (.db files)
├── handlers/              # Interface Layer (Bot Commands)
│   └── telegram_commands.py # Admin & Task management handlers
├── llm/                   # Infrastructure Layer (LLM Providers)
│   ├── gemini_llm.py      # Google Gemini implementation
│   ├── groq_llm.py        # Groq implementation (with concurrency locks)
│   └── llm_gateway.py     # Priority Queue & Retry logic
├── middlewares/           # Global Request Interceptors
│   └── auth.py            # Chat ID-based Authorization
├── pipeline/              # Orchestration Layer
│   └── telegram_pipeline.py # High-level flow: Service -> LLM -> Service
├── prompts/               # Instruction Layer
│   ├── loader.py          # Prompt file loading utility
│   └── termux_assistant.txt  # Core behavioral instructions
├── services/              # Business Logic Layer
│   ├── chat_service.py    # Context pruning & interaction persistence
│   └── task_manager.py    # Linux process lifecycle management
└── utils/                 # Cross-cutting Concerns
    ├── config.py          # Centralized Settings & Env Validation
    ├── helpers.py         # Shared utility functions
    └── logger.py          # Centralized Rotating Log system
```

## 🛠️ Key Architectural Features

### 🏗️ Clean Architecture
- **Entities (`models.py`)**: Logic interacts with structured Python objects, not raw database rows.
- **Service Layer**: Business rules (like how to prune chat history) are isolated from the bot's interface.
- **Orchestration**: The pipeline coordinates between services and LLMs without knowing the underlying implementation details.

### 🛡️ Security & Stability
- **Global Middleware**: Authorization is handled at the gateway level.
- **Structured Config**: Pydantic validates all environment variables (`.env`) at startup.
- **Priority Gateway**: High-priority chat takes precedence over background tasks in the LLM queue.

## 📦 Dependencies
- **aiogram v3+**: Asynchronous Telegram framework.
- **pydantic-settings**: Environment validation.
- **aiosqlite**: Asynchronous database interactions.
- **aiohttp**: Non-blocking network requests.

## 🚀 Quick Start
1. Configure `.env` with `BOT_TOKEN`, `CHAT_ID`, and `GEMINI_API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python main.py`.
