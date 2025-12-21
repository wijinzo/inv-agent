from langchain.agents import create_agent
from ..state import AgentState
from ..tools.technical_tools import get_technical_data
from ..utils import get_llm

def trend_analyst_node(state: AgentState):
    """
    Technical Trend Analyst node focusing on price direction and moving averages.
    
    This agent retrieves historical price data and technical indicators to evaluate 
    the relationship between short-term and medium-term moving averages (SMA_20 vs SMA_50) 
    and identifies key support and resistance levels.
    
    Args:
        state (AgentState): The current graph state.
        
    Returns:
        dict: A dictionary updating the state with the 'trend_analysis' report.
    """
    # Initialize the LLM with zero temperature for consistent trend signal interpretation
    llm = get_llm(temperature=0)
    tools = [get_technical_data]
    
    # Define the system prompt for the trend analysis expert persona
    system_prompt = """You are a Senior Technical Analyst specializing in Trends and Moving Averages (MA). (您是一位專注於趨勢和移動平均線的資深技術分析師。)
    Your goal is to provide a clear trend assessment and key price level analysis based on the technical data provided.
    
    1. Use the `get_technical_data` tool to retrieve technical indicator data.
    2. **MA Analysis (均線分析)**: Determine the current trend (Bullish, Bearish, or Consolidation) based on the relationship between the short-term (SMA_20) and medium-term (SMA_50) Moving Averages (e.g., SMA_20 above SMA_50 is Bullish).
    3. **Trend Assessment (趨勢判斷)**: Determine if the stock price is holding above key MAs or if it has broken below key support levels.
    
    Output a structured analysis report in **Traditional Chinese (繁體中文)**.
    
    **CRITICAL OUTPUT FORMAT**:
    - **Trend Overview (趨勢概況)**: Summarize the current trend.
    - **MA Signal (均線信號)**: Detail the relationship between SMA_20 and SMA_50 and its implied signal.
    - **Key Levels (關鍵價位)**: Provide 90-day Resistance and Support levels and explain their significance.
    
    **IMPORTANT**: 
    Start directly with the analysis.
    """
    
    # Create the ReAct agent with the technical analysis toolset
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    # Extract operational parameters from the state
    tickers = state["tickers"]
    query = state["query"]
    instructions = state.get("trend_analyst_instructions", "")
    
    # Construct the task message for the trend analyst
    user_message = f"""分析以下股票的趨勢狀況: {tickers}. 

        用戶的特定問題: {query}

        **來自主管的具體指示**:
        {instructions}
        """
        
    # Execute the agent to perform technical trend evaluation
    result = agent.invoke({"messages": [("human", user_message)]})
    
    # Return the generated trend report to the shared state
    last_message = result["messages"][-1]
    return {"trend_analysis": last_message.content}