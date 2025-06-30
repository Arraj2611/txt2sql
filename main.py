from fastapi import FastAPI, HTTPException
from schemas import QueryRequest, QueryResponse
from agent import run_agent
import uvicorn

app = FastAPI(
    title="Natural Language to SQL/API Agent",
    description="An AI agent that converts natural language to SQL queries.",
    version="1.0.0"
)

@app.post("/query", response_model=QueryResponse)
def process_query(request: QueryRequest):
    """
    Accepts a natural language query and returns the result from the agent.
    """
    try:
        result = run_agent(request.query)
        return QueryResponse(result=result)
    except Exception as e:
        # For production, you'd want more specific error handling
        # and logging.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="Root", description="Root endpoint to check if the API is running.")
def read_root():
    return {"message": "API is running. Post your query to /query."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 