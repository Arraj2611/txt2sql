from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
import logging

from .database import get_db_schema, execute_sql_query, get_db_session
from .config import GROQ_API_KEY

# Set up basic logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the API key is set
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

## Agent State
class AgentState(TypedDict):
    question: str
    db_schema: str
    sql_query: str
    result: str
    final_response: str
    needs_execution: bool

## Agent Nodes
def get_schema_node(state: AgentState):
    """Node to get the database schema."""
    session = next(get_db_session())
    schema = get_db_schema(session)
    return {"db_schema": schema}

def generate_sql_node(state: AgentState):
    """Node to generate SQL query based on the question and schema."""
    question = state["question"]
    schema = state["db_schema"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert PostgreSQL Database Administrator. Your goal is to translate any user request into the appropriate SQL commands to accomplish the task.

Database Schema:
{schema}

Your capabilities include, but are not limited to:
- Answering questions about the data (generating SELECT queries).
- Creating, altering, and dropping tables (CREATE, ALTER, DROP).
- Inserting, updating, and deleting data (INSERT, UPDATE, DELETE).
- Managing indexes, views, and other database objects.
- Correcting user-provided SQL that may have syntax errors.
- Fulfilling complex multi-step requests.

Instructions:
1.  Carefully analyze the user's request.
2.  If the request is a question about data, generate the appropriate SELECT query.
3.  If the request involves modifying the database schema or data, generate the necessary DDL/DML SQL statements.
4.  If the user provides SQL with errors (e.g., wrapped in markdown), correct it and provide the valid SQL.
5.  Output ONLY the valid, executable SQL required to fulfill the request. Do not add any conversational text or explanations.
"""),
        ("user", "{question}")
    ])
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192"
    )
    
    chain = prompt | llm | StrOutputParser()
    sql_query = chain.invoke({"question": question})
    logger.info(f"--- GENERATED SQL ---\n{sql_query}\n--------------------")
    # Determine if this needs execution (contains DDL/DML keywords)
    needs_execution = any(keyword in sql_query.upper() for keyword in ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER'])
    
    return {"sql_query": sql_query, "needs_execution": needs_execution}

def execute_sql_node(state: AgentState):
    """Node to execute the generated SQL query."""
    logger.info(f"--- EXECUTING SQL ---\n{state['sql_query']}\n-------------------")
    session = next(get_db_session())
    sql_query = state["sql_query"]
    result = execute_sql_query(session, sql_query)
    logger.info(f"--- RAW DB RESULT ---\n{result}\n-------------------")
    return {"result": result}

def generate_response_node(state: AgentState):
    """Node to generate a natural language response from the SQL result."""
    question = state["question"]
    sql_result = state["result"]
    sql_query = state["sql_query"]
    needs_execution = state.get("needs_execution", False)

    logger.info("--- GENERATING FINAL RESPONSE ---")

    if needs_execution:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI database assistant. You have just executed a database operation. Your task is to provide a clear, professional confirmation to the user.

Instructions:
1.  State clearly what action was performed.
2.  Confirm whether the operation was successful or if there was an error.
3.  If data was changed or added, you can show a sample or summary of the changes if appropriate.
4.  Maintain a helpful, authoritative, and professional tone.
"""),
            ("user", "Original request: {question}\n\nExecuted SQL:\n```sql\n{sql_query}\n```\n\nExecution Result: {sql_result}\n\nYour confirmation response:")
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI database assistant. You have just executed a query to retrieve data. Your task is to present the findings to the user in a clear, easy-to-understand format.

Instructions:
1.  Answer the user's original question directly.
2.  If the result is tabular, present it in a clean markdown table.
3.  If the result is a single value, state it clearly.
4.  Maintain a helpful, authoritative, and professional tone.
"""),
            ("user", "Original question: {question}\n\nSQL query result:\n{sql_result}\n\nYour natural language response:")
        ])

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192"
    )

    chain = prompt | llm | StrOutputParser()

    final_response = chain.invoke({
        "question": question,
        "sql_result": sql_result,
        "sql_query": sql_query
    })
    return {"final_response": final_response}

## Agent Workflow
workflow = StateGraph(AgentState)

workflow.add_node("get_schema", get_schema_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("generate_response", generate_response_node)

workflow.set_entry_point("get_schema")
workflow.add_edge("get_schema", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph into a runnable app
agent_app = workflow.compile()

def run_agent(question: str):
    """Function to run the agent with a user question."""
    inputs = {"question": question}
    final_state = agent_app.invoke(inputs)
    return final_state['final_response'] 