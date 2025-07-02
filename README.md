# Natural Language to SQL - MCP Agent

This project implements an AI agent that converts natural language queries into SQL commands. It uses a client-server architecture with a FastAPI backend acting as a "Master Control Program" (MCP) and a Streamlit-based chatbot UI as the client.

## Project Structure

```text
.
├── mcp_server/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── chatbot_ui/
│   └── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

- **`mcp_server/`**: Contains the FastAPI backend application (the "MCP Server").
  - `main.py`: The main FastAPI application file.
  - `agent.py`: Contains the core logic of the LangGraph-based AI agent.
  - `database.py`: Manages the database connection.
  - `schemas.py`: Defines the Pydantic models for API validation.
  - `config.py`: Manages configuration settings from the `.env` file.
- **`chatbot_ui/`**: Contains the Streamlit frontend application.
  - `app.py`: The code for the chatbot user interface.
- **`requirements.txt`**: Lists the Python dependencies for the project.
- **`.env.example`**: An example file for the required environment variables.

## Setup and Installation

1. **Clone the repository and navigate to the project directory.**

2. **Create and configure the environment file:**
    - Create a file named `.env` in the project root.
    - Copy the contents from `.env.example` or use the following template, replacing the placeholder values with your actual credentials:

    ```bash
    # PostgreSQL Database URL
    DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"

    # Groq API Key
    GROQ_API_KEY="your-groq-api-key-here"
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the PostgreSQL database:**
    - Make sure you have a PostgreSQL server running.
    - Create a new, empty database with the name you specified in your `.env` file.

## How to Run

You will need to run two separate processes in two different terminals.

### 1. Run the MCP Server (Backend)

In your first terminal, run the following command from the project's root directory to start the FastAPI server:

```bash
uvicorn mcp_server.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

### 2. Run the Chatbot UI (Frontend)

In your second terminal, run the following command from the project's root directory to start the Streamlit UI:

```bash
streamlit run chatbot_ui/app.py
```

The chatbot interface will open in your browser, usually at `http://localhost:8501`.

You can now interact with your database by typing natural language queries into the chat window.

## Initializing Your Database

Since the project no longer includes a sample data script, your database will initially be empty.

The MCP agent is capable of creating tables and inserting data for you. To get started, you can ask the agent to create the initial schema. For example, you can use a prompt like this in the chat interface:

"Create an `employees` table with columns for id, name, and hire_date. Also create a `departments` table with id and name. Then, create a `salaries` table with employee_id, amount, and date. Finally, insert a few sample records into each table so I can query them."
