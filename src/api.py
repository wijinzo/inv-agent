from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.graph import create_graph
import json 
import os 

import pandas

# Load environment variables from the .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(title="Investment Agent API")

class ResearchRequest(BaseModel):
    """
    Data model for the investment research request.
    
    Attributes:
        query (str): The specific research question or list of stock tickers.
        style (str): The target investment strategy (e.g., Balanced, Growth, Value).
    """
    query: str
    style: str = "Balanced"  # Default investment style is set to Balanced

@app.post("/research")
async def research(request: ResearchRequest):
    """
    Endpoint to trigger the multi-agent research workflow.
    
    This route initializes the agent graph, passes the user query into the state,
    executes the analysis, and exports a snapshot of the results to a JSON file
    for development and debugging purposes.
    """
    try:
        # Initialize the LangGraph workflow
        graph = create_graph()
        
        # Initialize the state object with all required fields for the agentic architecture
        initial_state = {
            "query": request.query,
            "investment_style": request.style,  # Pass the style parameter into the State
            "tickers": [],
            "data_analyst_instructions": None,
            "news_analyst_instructions": None,
            "trend_analyst_instructions": None,
            "pattern_analyst_instructions": None,
            "indicator_analyst_instructions": None,
            "data_analysis": None,
            "news_analysis": None,
            "trend_analysis": None,
            "pattern_analysis": None,
            "indicator_analysis": None,
            "technical_strategy": None,
            "risk_assessment": None,
            "final_report": None
        }
        
        # Invoke the graph to start the multi-agent execution
        result = graph.invoke(initial_state)
        
        # Export the resulting state to a JSON file for frontend development/testing
        output_filename = "real_data_snapshot.json"
        
        # Use default=str to handle non-serializable objects like datetime
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4, default=str)
            
        print(f"✅ Research data exported to: {os.path.abspath(output_filename)}")
        
        return result
        
    except Exception as e:
        # Print the full stack trace for backend debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """
    Standard health check endpoint to verify service availability.
    """
    return {"status": "ok"}