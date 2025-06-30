from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

from database import get_db_schema, execute_sql_query, get_db_session
from config import GROQ_API_KEY

# Ensure the API key is set
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

# 1. Define the agent's state
class AgentState(TypedDict):
    question: str
    db_schema: str
    sql_query: str
    result: str
    final_response: str

# 2. Define the nodes of the graph
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
        ("system", f"You are an expert SQL writer. Based on the following schema, write a SQL query to answer the user's question. Only output the SQL query and nothing else.\n\nSchema:\n{schema}"),
        ("user", "{question}")
    ])
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192" # Or another model you prefer
    )
    
    chain = prompt | llm | StrOutputParser()
    
    sql_query = chain.invoke({"question": question})
    return {"sql_query": sql_query}

def execute_sql_node(state: AgentState):
    """Node to execute the generated SQL query."""
    session = next(get_db_session())
    sql_query = state["sql_query"]
    result = execute_sql_query(session, sql_query)
    return {"result": result}

def generate_response_node(state: AgentState):
    """Node to generate a natural language response from the SQL result."""
    question = state["question"]
    sql_result = state["result"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that provides answers based on database query results. The user asked a question, and a SQL query was executed. Now, you need to formulate a clear, natural language response based on the query's result."),
        ("user", "Original question: {question}\nSQL query result:\n{sql_result}\n\nYour natural language response:")
    ])

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192"
    )

    chain = prompt | llm | StrOutputParser()

    final_response = chain.invoke({
        "question": question,
        "sql_result": sql_result
    })
    return {"final_response": final_response}

# 3. Build the graph
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