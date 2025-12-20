from langchain.agents import create_agent
from ..state import AgentState
from ..tools.technical_tools import get_technical_data
from ..utils import get_llm

def pattern_analyst_node(state: AgentState):
    """
    Technical Pattern Analyst node that identifies chart patterns and price action signals.
    
    This agent uses historical price data to detect classical technical patterns 
    (e.g., Head and Shoulders, Double Top/Bottom, Triangles) and provides 
    breakout/breakdown levels to inform trading decisions.
    
    Args:
        state (AgentState): The current graph state.
        
    Returns:
        dict: A dictionary containing the 'pattern_analysis' report string.
    """
    # Initialize the LLM with zero temperature for precise pattern recognition logic
    llm = get_llm(temperature=0)
    tools = [get_technical_data]
    
    # Define the specialized system prompt for the pattern analyst
    system_prompt = """You are a Technical Analyst specializing in Chart Patterns. (您是一位專注於圖表型態的技術分析師。)
    Your goal is to identify any potential price patterns based on the technical data and price action provided, and offer related trading implications.
    
    1. Use the `get_technical_data` tool to retrieve historical stock price data.
    2. **Pattern Identification (型態識別)**: Identify if any significant patterns (e.g., Head and Shoulders Bottom/Top, Double Bottom, Double Top, Triangle Consolidation, Box Consolidation) exist within the last 6 months.
    3. **Pattern Interpretation (型態解讀)**: If a pattern is identified, explain its bullish/bearish implication and the key breakout/breakdown levels.
    
    Output a structured analysis report in **Traditional Chinese (繁體中文)**.
    
    **CRITICAL OUTPUT FORMAT**:
    - **Identified Pattern (識別型態)**: State the pattern found. If no clear pattern is found, explicitly state that the price is in a no-obvious-pattern or consolidation phase.
    - **Pattern Implication (型態意義)**: Explain the trend direction typically suggested by this pattern.
    - **Breakout Levels (爆發點位)**: Note the key price levels that trigger buy/sell signals for the pattern.
    
    **IMPORTANT**: 
    Start directly with the analysis.
    """
    
    # Create the ReAct agent with the specified technical tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    # Extract operational parameters from the state
    tickers = state["tickers"]
    query = state["query"]
    instructions = state.get("pattern_analyst_instructions", "")
    
    # Construct the task-specific message for pattern detection
    user_message = f"""分析以下股票的型態狀況: {tickers}. 

        用戶的特定問題: {query}

        **來自主管的具體指示**:
        {instructions}
        """
        
    # Invoke the agent to perform the analysis
    result = agent.invoke({"messages": [("human", user_message)]})
    
    # Retrieve the content of the final output message
    last_message = result["messages"][-1]
    
    # Return the identified pattern analysis to the shared state
    return {"pattern_analysis": last_message.content}