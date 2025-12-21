from langchain.agents import create_agent
from ..state import AgentState
from ..tools.search_tools import search_news, web_search
from ..utils import get_llm

def news_analyst_node(state: AgentState):
    """
    Finance News Analyst node that utilizes a ReAct agent to search, 
    filter, and synthesize market news based on investment styles.
    
    This agent balances between broad ticker coverage and specific web 
    searches to address the user's query, providing sentiment analysis, 
    catalyst identification, and structured news summaries.
    
    Args:
        state (AgentState): The current graph state.
        
    Returns:
        dict: A dictionary containing the 'news_analysis' report string.
    """
    # Initialize the LLM with zero temperature for objective synthesis
    llm = get_llm(temperature=0)
    tools = [search_news, web_search]
    
    # Retrieve investment style to apply specific searching and analysis guidelines
    style = state.get("investment_style", "Balanced")

    style_guidelines = {
        "Conservative": """
        **STYLE GUIDELINE: CONSERVATIVE (保守型)**
        - **Search Focus**: Prioritize searching for **downside risk news** (下行風險新聞) like macro economic risks, regulatory threats, potential litigation, and supply chain disruptions.
        - **Analysis Focus**: Deeply analyze the rationale behind the Bear arguments and prioritize risk news in the summary.
        """,
        "Aggressive": """
        **STYLE GUIDELINE: AGGRESSIVE (積極型)**
        - **Search Focus**: Prioritize searching for **growth catalyst news** (成長催化劑新聞) like new product launches, expansion plans, technological breakthroughs, and upward guidance revisions.
        - **Analysis Focus**: Deeply analyze the feasibility of the Bull arguments and prioritize growth catalysts in the summary.
        """,
        "Balanced": """
        **STYLE GUIDELINE: BALANCED (穩健型)**
        - **Search Focus**: Balance the search for both bullish and bearish news.
        - **Analysis Focus**: Look for structural changes ignored by the market.
        """
    }
    current_guideline = style_guidelines.get(style, style_guidelines["Balanced"])
    
    # Construct the system prompt defining the persona and reporting constraints
    system_prompt = f"""You are a Senior News Analyst at a top-tier investment bank.
    Your goal is to synthesize market news into actionable insights, **specifically addressing the user's question**. (您的目標是將市場新聞合成可操作的見解，特別針對用戶的問題。)
    
    **Current Investment Strategy: {style}**
    {current_guideline}

    **Recency Rule**: Prioritize news from the **last 7 days** unless the user query explicitly specifies an older time frame.

    1. **Tool Selection**:
       - Use `search_news` for broad company coverage.
       - Use `web_search` for **specific questions**, **market sentiment**, or **competitor analysis**.
       - **STRATEGY**: If the user asks a specific question, you MUST use `web_search` with a targeted query.
    
    2. **Context-Aware Analysis**: Address the user's specific concern using filtered news.
    3. **Debate Analysis**: Present Bull vs Bear arguments adjusted for the {style} style.
    4. **Catalyst Identification**: Identify events likely to trigger price movement.
    5. **Sentiment Analysis**: Assess the market sentiment score (1-10).
    
    Output a structured analysis in **Traditional Chinese (繁體中文)**:
    - **Market Debate (市場辯論)**: Bull vs Bear arguments.
    - **Key Catalysts (關鍵催化劑)**: Upcoming/recent major events.
    - **Sentiment Score (情緒評分)**: 1-10 with reasoning.
    - **Headline Summary (頭條摘要)**: Concise bullet points. **NO URLs HERE.**
    - **News links (新聞連結)**: Strictly Markdown `[Title](URL)`.
    
    **CRITICAL RULE FOR TOOL USE:**
    1. **NO INTERNAL MONOLOGUE**: Output the JSON tool call IMMEDIATELY.
    2. **SILENCE**: Do not explain your search process.
    """
    
    # Initialize the ReAct agent with search capabilities
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    # Extract operational parameters from the state
    tickers = state["tickers"]
    query = state["query"]
    instructions = state.get("news_analyst_instructions", "")
    
    # Construct the message containing specific tickers and lead analyst instructions
    user_message = f"""Find and analyze news for the following tickers: {tickers}. 

        User's Specific Question: {query}

        **Specific Instructions from Lead**:
        {instructions}
        """
    
    # Execute the news analysis workflow
    result = agent.invoke({"messages": [("human", user_message)]})
    
    # Retrieve the content from the final message in the interaction sequence
    last_message = result["messages"][-1]
    return {"news_analysis": last_message.content}