from langchain.agents import create_agent
from ..state import AgentState
from ..tools.finance_tools import get_stock_analysis_data 
from ..utils import get_llm

def data_analyst_node(state: AgentState):
    """
    Agent node specializing in quantitative financial analysis.
    
    This agent uses a ReAct pattern to fetch historical financial data and 
    performs trend analysis on revenue, earnings, margins, and valuation 
    metrics, tailored to the user's specific investment style.
    
    Args:
        state (AgentState): The current state of the graph.
        
    Returns:
        dict: A dictionary containing the 'data_analysis' report string.
    """
    # Initialize the LLM with zero temperature for consistent quantitative results
    llm = get_llm(temperature=0)
    tools = [get_stock_analysis_data]
    
    # Retrieve investment style and determine the corresponding analysis framework
    style = state.get("investment_style", "Balanced")

    style_guidelines = {
        "Conservative": """
        **STYLE GUIDELINE: CONSERVATIVE (保守型)**
        - **Primary Focus**: Financial Health and Stability (財務體質與穩定性).
        - **Analysis Requirement**: Strictly check Debt Ratios and Cash Flow Coverage. Emphasize the **stability of margins** over explosive growth.
        - **Valuation Requirement**: Must rigorously scrutinize if P/E is far above historical averages.
        """,
        "Aggressive": """
        **STYLE GUIDELINE: AGGRESSIVE (積極型)**
        - **Primary Focus**: Growth Potential (成長潛力) and Efficiency.
        - **Analysis Requirement**: Rigorously check Revenue and Earnings **growth trajectories**. Tolerate higher valuations, but require proof that ROE or operating margins are **expanding**.
        - **Valuation Requirement**: Focus on growth-related multiples like PEG or EV/EBITDA.
        """,
        "Balanced": """
        **STYLE GUIDELINE: BALANCED (穩健型)**
        - **Primary Focus**: Growth at a Reasonable Price (GARP). (風險調整後回報).
        - **Analysis Requirement**: Balance the check of financial health and growth trends. Emphasize that valuation must be reasonable.
        """
    }
    current_guideline = style_guidelines.get(style, style_guidelines["Balanced"])
    
    # Define the system prompt for the financial data analyst agent
    system_prompt = f"""You are a Senior Financial Data Analyst at a top-tier investment bank.
    Your goal is to provide a rigorous quantitative analysis of the provided tickers, **specifically addressing the user's question** with a focus on LONG-TERM TRENDS.
    
    **Current Investment Strategy: {style}**
    {current_guideline}
    
    1. **Data Retrieval**: Use the `get_stock_analysis_data` tool to fetch 5-year historical data.
    
    2. **Trend & Growth Analysis (Crucial)**:
        - Do NOT just look at the most recent number. Analyze the trajectory over the past years.
        - **Revenue & Earnings**: Are they growing? Calculate simple growth rates or CAGR if possible based on the provided table.
        - **Margins**: Are Gross/Operating margins **expanding** (getting better) or **contracting** (getting worse) over the years?
        - **Cash Flow**: Is Free Cash Flow positive and growing?
    
    3. **Valuation Context**: 
        - Look at the current valuation metrics (P/E, etc.) in the context of the price performance. 
        - If the price has risen significantly, is the valuation still justified by earnings growth?
    
    4. **Context-Aware Analysis**: Look for data points that specifically support or refute the user's hypothesis.
    
    Output a structured analysis in **Traditional Chinese (繁體中文)**.
    
    **CRITICAL OUTPUT FORMAT**:
    - **Trend Analysis (趨勢分析)**: Discuss the direction of Revenue, Net Income, and Margins over the last few years (e.g., "Revenue has grown consecutively for 4 years").
    - **Financial Health & Efficiency (財務體質與效率)**: Analyze Balance Sheet strength and Margin trends.
    - **Valuation & Performance (估值與表現)**: Current valuation relative to the long-term price performance.
    - **Analyst Verdict (分析師觀點)**: Based on the trends, is the company strictly improving, deteriorating, or mixed?
    - **Key Data Table (關鍵數據表)**: A summary table of the most important metrics (e.g., 5-Year Return, Latest Margin vs 3-Year Ago Margin).
    
    **IMPORTANT**: 
    Start directly with the analysis. Do NOT use introductory phrases.
    Ensure numbers are formatted legibly (e.g., 1.2B, 35%).
    Use data from the "Income Statement Trends" and "Balance Sheet Trends" sections provided by the tool.
    If comparing multiple tickers, a comparison table is highly recommended.
    """

    # Initialize the ReAct agent with specific financial tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    # Extract ticker list and user query from current graph state
    tickers = state["tickers"]
    query = state["query"]
    instructions = state.get("data_analyst_instructions", "")
    
    # Construct the user prompt with specific tickers and lead instructions
    user_message = f"""Analyze the following tickers: {tickers}. 

        User's Specific Question: {query}

        **Specific Instructions from Lead**:
        {instructions}
        """
        
    # Execute the agent workflow
    result = agent.invoke({"messages": [("human", user_message)]})
    
    # Retrieve the final generated analysis content
    last_message = result["messages"][-1]
    return {"data_analysis": last_message.content}