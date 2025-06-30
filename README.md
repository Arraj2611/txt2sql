# Natural Language to SQL/API Agent

This project implements an AI agent that converts natural language queries into SQL commands. It uses a FastAPI backend, a PostgreSQL database, and a LangGraph-based agent for processing the natural language queries.

## Project Structure

```text
.
├── .env.example
├── .gitignore
├── agent.py
├── config.py
├── database.py
├── main.py
├── README.md
├── requirements.txt
├── sample_data.sql
└── schemas.py
```

- **`main.py`**: The main FastAPI application file. It exposes the API endpoints for handling natural language queries.
- **`agent.py`**: Contains the core logic of the AI agent, including the LangGraph setup.
- **`database.py`**: Manages the database connection and provides functions for executing queries and fetching the schema.
- **`schemas.py`**: Defines the Pydantic models for API request and response validation.
- **`config.py`**: Holds the configuration settings for the application, loading values from a `.env` file.
- **`requirements.txt`**: Lists the Python dependencies for the project.
- **`sample_data.sql`**: SQL script to create and populate the database with sample data.
- **`.env.example`**: An example file for the required environment variables.
- **`.gitignore`**: Specifies which files and directories to ignore in version control.
- **`README.md`**: This file, providing an overview and setup instructions.

## Setup and Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create and configure the environment file:**
    - Create a file named `.env` in the project root.
    - Copy the contents from `.env.example` or use the following template:

    ```bash
    # PostgreSQL Database URL
    # Format: postgresql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"

    # Groq API Key
    GROQ_API_KEY="your-groq-api-key-here"
    ```

    - Replace the placeholder values with your actual database URL and Groq API key.

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
