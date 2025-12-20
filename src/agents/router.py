from typing import List
from langchain.agents import create_agent
from langchain_core.tools import tool
from ..state import AgentState
from ..utils import get_llm

@tool
def submit_routing_instructions(tickers: List[str], data_analyst_instructions: str, news_analyst_instructions: str, trend_analyst_instructions: str, pattern_analyst_instructions: str, indicator_analyst_instructions: str):
    """
    Submit the extracted tickers and specific instructions for the Data Analyst, News Analyst, Trend Analyst, Pattern Analyst, and Indicator Analyst.
    
    Args:
        tickers: List of stock tickers found in the query.
        data_analyst_instructions: Specific instructions for the Data Analyst (financials, valuation).
        news_analyst_instructions: Specific instructions for the News Analyst (news, sentiment, events).
        trend_analyst_instructions: Specific instructions for the Trend Analyst (MA, trend lines, direction).
        pattern_analyst_instructions: Specific instructions for the Pattern Analyst (candlestick and chart patterns).
        indicator_analyst_instructions: Specific instructions for the Indicator Analyst (RSI, MACD, Stochastic).
    """
    return "Instructions submitted."

def router_node(state: AgentState):
    """
    Router agent node that extracts tickers and orchestrates task assignments.
    
    This agent acts as the gateway of the research workflow, parsing the user's 
    intent to identify relevant stock symbols and generating tailored, high-precision 
    instructions for each specialized sub-agent.
    
    Args:
        state (AgentState): The current graph state containing the raw user query.
        
    Returns:
        dict: A dictionary updating the state with tickers and individualized instructions.
    """
    # Initialize the LLM with zero temperature for reliable extraction and routing
    llm = get_llm(temperature=0)
    
    # Define the core coordinating persona and task extraction logic
    system_prompt = """You are a Senior Financial Research Lead.
    Your job is to coordinate the research flow by analyzing the user's query and assigning tasks. (您的工作是透過分析用戶的查詢並分配任務來協調研究流程。)
    
    1. **Analyze User Query**: Understand the core question, hypothesis, or concern.
    2. **Extract Stock Tickers**: Identify all mentioned or implied stock tickers.
    3. **Assign to Data Analyst**: Create specific instructions for the Data Analyst.
       - What specific financial metrics should they look for? (e.g., "Check Gross Margin if the user asks about profitability.")
       - Which valuation multiples are relevant?
    4. **Assign to News Analyst**: Create specific instructions for the News Analyst.
       - What specific keywords or topics should they search for? (e.g., "Search for 'supply chain issues' if the user asks about delays.")
       - Which sentiments or events are most important?
    5. **Assign to Trend Analyst**: Create specific instructions, focusing on Moving Averages, price direction, and timeframes (e.g., "Analyze the relationship between the 20-day and 50-day Moving Averages.").
    6. **Assign to Pattern Analyst**: Create specific instructions, focusing on candlestick or chart patterns (e.g., "Look for a Head and Shoulders Bottom or a Flag pattern.").
    7. **Assign to Indicator Analyst**: Create specific instructions, focusing on momentum (RSI, MACD) and volatility indicators (e.g., "Evaluate momentum using the 14-period RSI.").
       
    **Goal**: Do NOT just pass the general query. Translate the user's intent into precise, actionable technical instructions.
    
    You **MUST** call the `submit_routing_instructions` tool to output your decision.
    """
    
    # Create the ReAct agent with the routing tool
    agent = create_agent(
        model=llm,
        tools=[submit_routing_instructions],
        system_prompt=system_prompt
    )
    
    # Execute routing by passing the raw query to the Research Lead agent
    result = agent.invoke({"messages": [("human", state["query"])]})
    
    # Extract the tool call to parse the assigned instructions
    messages = result["messages"]
    tool_call = None
    
    # Iterate backwards to find the model's tool call decision
    for msg in reversed(messages):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_call = msg.tool_calls[0]
            break
            
    # Process the tool call arguments and update the state
    if tool_call and tool_call["name"] == "submit_routing_instructions":
        args = tool_call["args"]
        return {
            "tickers": args.get("tickers", []),
            "data_analyst_instructions": args.get("data_analyst_instructions", ""),
            "news_analyst_instructions": args.get("news_analyst_instructions", ""),
            "trend_analyst_instructions": args.get("trend_analyst_instructions", ""),
            "pattern_analyst_instructions": args.get("pattern_analyst_instructions", ""),
            "indicator_analyst_instructions": args.get("indicator_analyst_instructions", "")
        }
    
    # Fallback mechanism to ensure the workflow continues even if the agent fails to use the tool
    default_instruction = state["query"]
    return {
        "tickers": [], 
        "data_analyst_instructions": default_instruction, 
        "news_analyst_instructions": default_instruction,
        "trend_analyst_instructions": default_instruction,
        "pattern_analyst_instructions": default_instruction,
        "indicator_analyst_instructions": default_instruction
    }