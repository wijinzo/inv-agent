from langchain.agents import create_agent
from ..state import AgentState
from ..utils import get_llm

def risk_manager_node(state: AgentState):
    """
    Risk Manager node that assesses potential downside risks and "Bear Case" scenarios.
    
    This agent acts as a "Devil's Advocate," synthesizing quantitative data, 
    qualitative news sentiment, and technical outlooks to identify macro, sector, 
    and company-specific risks based on the user's investment style.
    
    Args:
        state (AgentState): The current graph state.
        
    Returns:
        dict: A dictionary containing the 'risk_assessment' report string.
    """
    # Initialize the LLM with zero temperature for unbiased risk assessment
    llm = get_llm(temperature=0)

    # 1. Retrieve the investment style from the state (default to Balanced)
    style = state.get("investment_style", "Balanced")
    
    # 2. Define persona-specific instructions tailored to different risk appetites
    style_instructions = {
        "Conservative": """
        **CURRENT MODE: CONSERVATIVE (保守型)**
        - **Primary Goal**: Capital Preservation (本金安全).
        - **Mindset**: Be extremely skeptical. Assume the worst-case scenario is likely.
        - **Criteria**: Heavily penalize high valuations (high P/E), unproven technology, or high debt.
        - **Advice**: If there is any significant doubt, recommend avoiding the stock. "Better safe than sorry."
        """,
        
        "Aggressive": """
        **CURRENT MODE: AGGRESSIVE (積極型)**
        - **Primary Goal**: High Growth Potential (高成長潛力).
        - **Mindset**: Tolerate volatility. Focus only on "Thesis Breakers" (risks that permanently destroy value).
        - **Criteria**: Don't worry about standard high valuations if growth supports it. Focus on competitive threats or regulatory bans.
        - **Advice**: Highlight risks that would kill the growth story, but ignore short-term market noise.
        """,
        
        "Balanced": """
        **CURRENT MODE: BALANCED (穩健型)**
        - **Primary Goal**: Risk-Adjusted Returns (風險調整後回報).
        - **Mindset**: Rational "Devil's Advocate". Weigh upside vs. downside.
        - **Criteria**: look for structural risks that the market is ignoring.
        """
    }

    # Apply the corresponding style instructions
    specific_instruction = style_instructions.get(style, style_instructions["Balanced"])

    # 3. Construct the master system prompt for the Chief Risk Officer persona
    system_prompt = f"""You are a Chief Risk Officer. Your goal is to identify downside risks, but you must strictly adhere to the user's chosen Investment Style: **{style}**. (您的目標是識別下行風險，但必須嚴格遵守用戶選擇的投資風格。)

    {specific_instruction}

    Your Task:
    Based on the **Risk Profile** defined above, analyze the input data and act as a "Devil's Advocate" *within that specific context*, **specifically regarding the user's question**.
    
    Input:
    - User Query: The specific question or hypothesis the user has.
    - Data Analysis (Valuation, Financials)
    - News Analysis (Catalysts, Sentiment)
    - **Technical Strategy (Technical Outlook)**: The combined view of chart trends, patterns, and indicators.
    
    Output in **Traditional Chinese (繁體中文)**:
    1. **Stress Test User's Hypothesis (壓力測試用戶假設)**: Explore "What if X is NOT a bottleneck?" or "What if X gets worse?".
    2. **Bear Case Scenario (看空情境)**: Describe a specific scenario where the stock could drop 20%+. Highlight *Technical Breakdowns* (e.g., breaking major moving average or support) as a primary risk.
    3. **Risk Categorization (風險分類)**: Macro, Sector, Company.
    4. **Risk Score (風險評分)**: Assign a score (1-10) with justification.
    
    Be conservative. If the stock is "priced for perfection," highlight that as a major risk.
    
    **IMPORTANT**: Start directly with the analysis. Do NOT use introductory phrases.
    """
    
    # Initialize the ReAct agent (currently no external tools needed for synthesis)
    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=system_prompt
    )
    
    # Extract existing analysis reports from the state
    user_query = state.get("query", "No specific query provided.")
    data_analysis = state.get("data_analysis", "No data analysis provided.")
    news_analysis = state.get("news_analysis", "No news analysis provided.")
    technical_strategy = state.get("technical_strategy", "No technical strategy provided.")
    
    # Format the user message to provide context for the risk assessment
    user_message = f"""User Query:
{user_query}

Data Analysis:
{data_analysis}

News Analysis:
{news_analysis}

Technical Strategy:
{technical_strategy}

Please provide your risk assessment."""
    
    # Execute the agent workflow to generate the risk assessment
    result = agent.invoke({"messages": [("human", user_message)]})
    
    # Return the content of the final report message to the graph
    last_message = result["messages"][-1]
    return {"risk_assessment": last_message.content}